# HANDOFF 2026-10-22 — Doświadczenie smolarza (job 56) i sekcja „Praca"

## 1. Objaw

W oknie **pracownika-smolarza** brakowało całej sekcji **„Praca"** (u młynarza widać
`Mąka ∞`) oraz sekcji **„Doświadczenie"** (`Mielenie 85`). Dodatkowo smolarz nie
zdobywał doświadczenia za produkcję węgla.

## 2. Root cause (potwierdzony statycznie w exe)

`Data\GameSourceIncludes\logicdefines.inc`:

```
#define JOB_TYPE_MAXIMUM  56      // silnik zna zawody 0..55
```

Smolarz to **job 56** → wypada poza limit dwóch tablic:

### 2.1 Tablica „typy doświadczenia per job" — `[0x510c1c]`

Parser `[humanjobexperiencetype]` @ `0x412855`:

```
0x41287c  mov esi, 0xFD8      ; 4056 = 78 * 0x34  (rekordy doświadczeń, 78 typów)
0x412894  mov esi, 0x9A0      ; 2464 = 56 * 0x2C  (lista typów per JOB)
...
0x412adc  imul eax, eax, 0x2c ; job * 44
0x412aef  mov [eax+ecx*4+4], type
0x412af3  inc dword [eax]
```

**Brak kontroli zakresu `job`** → blok `job 56` pisze pod `56*0x2C = 0x9A0`, czyli
**za końcem malloc** (heap overflow). To dlatego mod nigdy nie dodał wpisu
doświadczenia dla smolarza.

Wpis per job = `count` (4 B) + do 10 typów (40 B) = 0x2C.

### 2.2 Wyszukiwarka `job+good -> typ doświadczenia` — `FUN_00461ba7`

```
0x461bba  cmp eax, 7
0x461bbe  jl  ret            ; job < 7
0x461bc0  cmp eax, 0x1e
0x461bc3  jg  ret            ; job > 30  <-- job 56 NIGDY nie przechodzi
```

Bez typu doświadczenia UI nie ma czego pokazać → brak sekcji „Praca" i
„Doświadczenie", brak XP, a produkcja liczy się z domyślnych wartości.

### 2.3 Rekord doświadczenia jest indeksowany TYPEM, nie jobem

Stride **0x34**, 78 wpisów (typy 0..77), pola:

| offset | pole |
|--------|------|
| +0x20  | job |
| +0x24  | good (1. dobro) |
| +0x28  | good2 (2. dobro) |
| +0x2C  | experiencefactor |
| +0x30  | (ncbr) |

Wniosek: **nie da się „pożyczyć" typu innego zawodu** — rekord typu 3 ma
`good 5` (drewno), więc dla węgla (66) lookup nic nie znajdzie. Potrzebny typ,
którego rekord jest **zerowy**: typy 71..76 (walka bronią) i 77 (trening) nie mają
bloków w tabeli.

## 3. Wdrożone rozwiązanie

### 3.1 Dane — nowy plik `Data\logic\humanjobexperiencetypes.ini`

Ścieżka `data\logic\humanjobexperiencetypes.ini` jest **obsługiwana przez silnik**
(w exe @ `0x0FFC84`), więc .ini nadpisuje/uzupełnia `humanjobexperiencetypes.cif`
— nie trzeba ruszać CIF (oryginał nietknięty, rollback = usunąć .ini).

Zawartość: wszystkie 70 bloków z CIF (konwersja `cif2txt.exe C`) + nowy:

```
[humanjobexperiencetype]
type 71
name "charcoal burner coal"
job 56
good 66
experiencefactor 100
```

Format .ini = tekst CIF bez prefiksów `%01%`/`%02%`, sekcje `[nazwa]`
(tak jak `jobtypes.ini`, `houses.ini`).

### 3.2 Nazwa doświadczenia — `experiences.ini`

`stringn 71` zmienione z `"Walka - Pięść"` na **`"Wypalanie Węgla"`**
(plik cp1250, 78 wpisów). Typ 71 = walka pięściami — najmniej dotkliwy do
przeznaczenia (pięści prawie nie są levelowane; pozostałe 72–76 to włócznia,
miecz, topór, łuk, katapulta).

**Trade-off:** trening pięści nie będzie już pokazywany jako „Walka - Pięść".

### 3.3 Patche EtapC (`etapa_gen/patches_ext.h`, sekcja „DOSWIADCZENIE / SEKCJA PRACA")

| RVA | off | len | bajty | opis |
|-----|-----|-----|-------|------|
| `0x0012895` | 0 | 4 | `CC 09 00 00` | tablica per-job 56 → 57 wpisów (`0x9A0` → `0x9CC`) |
| `0x00061BC2` | 0 | 1 | `0x38` | `FUN_00461ba7`: górna granica joba `0x1E` → `0x38` (job 56) |

> Uwaga: `0x0012895` to RVA **imm** w `mov esi, 0x9A0` @ `0x412894`; ta sama
> wartość trafia do malloc i memset, więc obie operacje są spójne.
> `0x00061BC2` to imm w `cmp eax, 0x1e` @ `0x461BC0`.

Weryfikacja w exe: `0x12894` = `be a0 09 00 00`, `0x61BC0` = `83 f8 1e` ✔

## 4. Co sprawdzić po starcie

1. `logs\etapc.log` — linie `ok` dla `rva 0012895` i `rva 00061BC2`.
2. Okno pracownika-smolarza: czy jest **„Praca"** z `Węgiel ∞`.
3. Sekcja **„Doświadczenie"**: czy pokazuje `Wypalanie Węgla N`.
4. Czy po wyprodukowaniu węgla N rośnie.

Jeśli sekcja „Praca" nadal nie wraca, ale „Doświadczenie" już jest → sekcja
„Praca" ma dodatkowy warunek (osobny trop: pętla `cmp edi,0x42` @ `0x4AC6E9`).

## 5. Rollback

- DLL: `EtapC.dll.bak_exp_<stamp>` w rootcie.
- Dane: usunąć `Data\logic\humanjobexperiencetypes.ini` (oryginalny .cif działa dalej),
  `experiences.ini.bak_20261022_213437`.

## 6. Ważne ustalenia dodatkowe (na przyszłość)

- Silnik ładuje **`.ini`**, nie `.cif`: `data\logic\*.ini`, `data\text\%s\strings\gameobjects\*.ini`
  oraz nadpisania moda `cn.plmod\stringstext\gameobjects\*.ini`.
  `Data\text\pol\strings\gameobjects\jobs.ini` **nie istnieje** → nazwy zawodów idą z `.cif`.
  Gdyby trzeba było dodać/zmienić nazwę zawodu — wystarczy utworzyć ten `.ini`
  (format jak `goods.ini`: `<CULTURES_CIF_BEGIN><03FD><00000073>`, `[control]`,
  `stringidmultiplier 2`, `[text]`, pary `stringn N` / `string`, stopka).
  Nagłówek = liczba stringów + 1 (`jobs`: `0x73` = 115 = 2×56+3 → miejsce na job 56 już jest).
- Kolejność stringów w plikach tekstowych: **UTF-8** w `goods.ini` (renderuje się
  poprawnie: „Mąka"), **cp1250** w `experiences.ini`.
- `JOB_TYPE_MAXIMUM = 56` oznacza, że **każda** tablica indeksowana jobem o stałym
  rozmiarze 56 wymaga sprawdzenia, jeśli dodajemy kolejny zawód (57+).
