# HANDOFF 2026-10-20 — PRZYWRÓCENIE PRODUKCJI (root cause)

Dokument dla szybkiego restartu sesji. Poprzedni: `HANDOFF-smolarz-wegiel-FAZA2-2026-10-19.md`.
Gra: `G:\Games\CnMod 1.2\CN.PLMOD.exe` (32-bit, ImageBase `0x400000`).

---

## 1. CO ZOSTAŁO DOWIEDZIONE (fakty, nie hipotezy)

### 1.1 Produkcję kończy EVENT ANIMACJI typu 21 — udowodnione

`0x467E60` to dyspozytor eventów animacji atomowej: `eax = [msg+4] - 1`,
`jmp [eax*4 + 0x468280]`, zakres typów 1..36.

Tabela `0x468280` (odczytana z pliku):

| typ | adres | znaczenie |
|----|----|----|
| 21 | `0x467EDD` | **`call 0x46897C` → KONIEC PRODUKCJI** |
| 22 | `0x467EE9` | `441913` |
| 23 | `0x467EF5` | `4418A2` |
| 29 | `0x468171` | dispatch `ab8` 0x59/0x5A (jednostki specjalne) |
| 34 | `0x4681EB` | dźwięk |

`FUN_46897C(unit)` (thiscall, `ecx=unit`) — pełny łańcuch:
1. `esi = pRec + [unit+0x1C] * 0xD0`  (rekord goodtype produkowanego dobra)
2. `edi = pBld + [unit+0xB34] * 0x7E0` (budynek)
3. pętla wejść `i < rec[+0x54]`: `4319D7(bldg, rec[+0x58+4i], 0) >= rec[+0x80+4i]` — inaczej porażka
4. `431DDF(bldg, unit+0x1C)` — jeśli wyjście pełne → porażka
5. zużycie: pętla `i < rec[+0x50]`: `431B3D(bldg, rec[+0xA8+4i], -1)`
6. `[unit+0x1C] == 0x39 || == 0x3A` → `468A99` (ścieżka specjalna), inaczej `468BAE(bldg)`
7. porażka → `[unit+0x36C] = 3`; na końcu `42CF27(unit)`

`468BAE`: `amount = 4421A5(unit)`, `431B53(bldg, unit+0x1C, amount/10, amount%10, 0)`,
`acc=0`, `ad0=0`, `36C=2`.

**Wniosek:** animacja produkcyjna MUSI mieć `event <koniec> 21`. To jedyny wyzwalacz.
(`event 23` nie jest potrzebny — dowód: `viking_miller_produce_flour` go nie ma, a produkcja działa.)

### 1.2 Bramka `45C17B` (thiscall `unit, actionId, -1`)

```
if actionId == 1                              -> 0
if !45C66E(unit)                              -> 0
if byte[pJobs + job*0x88 + 0x24 + actionId] == 0 -> 0     <-- whitelist z "setatomic"
ok: [unit+0xAC0]=idx, [unit+0xAC8]++, [unit+0xAB8]=actionId, [unit+0xABC]=1
```

`idx = pTribe[tribe*0x1AE08 + job*0x170 + actionId*4 + 0x20]`; jeśli `-1` → fallback
`[jobRec+0x20]` (job 56 → 6) i ponowne sprawdzenie.
**Uwaga:** wartość `0` jest POPRAWNA (to indeks akcji 0) — tylko `-1` oznacza „brak".

### 1.3 `atomicForProduction` = pole `+0x4C` rekordu goodtype — udowodnione

`pRec = [0x511420]`, stride `0xD0`. Odczyt na żywo vs `Data\logic\goodtypes.ini` —
zgodność 10/10 (8→51, 11→0, 19→33, 24→29, 26→29, 31→29, 32→33, 37→33, 43→32, 66→38).

### 1.4 ⭐ TEST NA ŻYWO: mąka produkuje się po poprawce

Młyn (ht 13, job 19, dobro 11). Wyjściowo: `atomic=0`, wejścia `[4, 74]`
(dobro **74 nie istnieje** → warunek wejść zawsze fałszywy).

Po ustawieniu w RAM: `rec[11].+0x4C = 46` **oraz** `rec[11].+0x54 = 1` (samo pszenica):

```
[t=40s] wheat=6 flour=0
[t=42s] wheat=4 flour=1     <-- MĄKA POWSTAŁA
```

**To jest dowód end-to-end**, że przy poprawnych danych cały łańcuch działa.

### 1.5 Dlaczego „nic się nie produkuje" — dwa systemowe błędy danych

`goodtypes.ini` był praktycznie **waniliowy** (nazwy, wejścia, atomiki), a `houses.ini`
używa **własnej numeracji moda**. Skutki:

**A) `atomicForProduction` nie należy do zawodu pracownika budynku**
Waniliowe id 25–38 nie występują w `setatomic` żadnego zawodnika →
`allow[job][atomic] == 0` → `45C17B` zwraca 0 → jednostka wchodzi w `36C=1`
i **zawiesza się na zawsze** (patrz 1.6).
Jedyny wyjątek: moneta (dobro 8 → atomik 51 = `viking_coiner_produce_coin`, job 14) — zgadzało się.

**B) `productionInputGoods` wskazywał dobra, których budynek nie magazynuje**
Np. dobro 11 (mąka): `productionInputGoods 4 74` — dobro 74 nie istnieje.
Dobro 19 (piekarnia): wejście `9`, a budynek magazynuje `1, 11, 19` → brak slotu → produkcja niemożliwa.

**C) Śmieciowy blok na końcu `goodtypes.ini`** (`goodtype 66` / `type 12` / `atomicForProduction 1`)
nadpisywał **dobro 12** (atomik 1 = zabroniony) i psuł ul (ht 11, dobro 12).

### 1.6 Deadlock jednostki — zaobserwowany na żywo (smolarz)

`unit = 0x1c1c12e0` (job 56, bldg 5, selgood 66):

```
36c=1  374=2  acc=0  ab8=1  abc=0  ac0=51  ac8=30  ad0=0  ad4=0  a68=5
```

Interpretacja: `36C=1` („pracuje"), ale `ABC=0` (akcja nieaktywna), `AB8=1` (chodzenie).
`0x468171` przy `36C==1` obsługuje tylko `ab8` 0x59/0x5A, resztę pomija →
**jednostka stoi w miejscu na zawsze**. To jest objaw, który użytkownik widzi jako
„nic się nie produkuje".

Po resecie pól stanu cykl ruszył: `36C=1, ab8=3, abc=1, ac8=31` (czyli `45C17B` PRZESZŁO),
ale w następnej sekundzie `36C=3` (porażka) → powrót do deadlocka.
Porażka nastąpiła, bo w RAM nie da się zarejestrować nowej pary (job 56, atomik) —
`ac0` wskazywał złą akcję. **Tego nie da się obejść poprawką danych w locie** — wymaga restartu.

---

## 2. KTÓRE PLIKI SĄ NAPRAWDĘ WCZYTYWANE (ustalone eksperymentalnie)

| plik | status |
|---|---|
| `CN.PLMOD\types\houses.ini` | **LIVE** (ht 57 ma 2 pracowników: `+0x10`=56, `+0x18`=24 → plik z `logicworker 24 1`) |
| `CN.PLMOD\tribetypes12\tribetypes.ini` | **LIVE** (`setatomic`, `allowjob`) |
| `CN.PLMOD\atomicanimations12\atomicanimations.ini` | **LIVE** (length + eventy) |
| `Data\logic\goodtypes.ini` | **LIVE** (jedyne źródło; wartości `+0x4C` zgodne) |
| `CN.PLMOD\budynki12\houses\houses.ini` | grafika budynków (`[GfxHouse]`, „Chata smolarza" L~29797) |
| `Data\logic\houses.ini` | **NIE jest używany** (stary artefakt z markerami `<CULTURES_CIF_END>`) |

Rekord htype (`0x624`): `+0` maintype, `+8` prodGood, `+0xC` liczba stocków,
`+0x10` job0, `+0x14` ile0, `+0x18` job1, `+0x1C` ile1, `+0x60` liczba slotów,
`+0x64+12*i` = `{good, max, flag}`, `+0x37C+good*4` = rewmapa good→slot.

---

## 3. WPROWADZONE POPRAWKI (2026-10-20)

### 3.1 `Data\logic\goodtypes.ini` (kopia: `goodtypes.ini.bak_20261020_*`)

Skrypt: `.ai\tmp\fixgoodtypes.py` (73 zmiany). Reguła:
* `atomicForProduction` = atomik produkcyjny zawodu pracującego w budynku,
* `productionInputGoods` = `logicstock` budynku **minus** produkowane dobra
  (przy kilku budynkach: najkrótsza lista).

Przykłady (sensowne pary): piekarnia `1 11` (woda+mąka), garncarnia `2 5` (muł+drewno),
kowal `6 5 39` (żelazo+drewno+…), kamieniarz `3` (kamień), szwalnia `9` (skóra),
browar `1 12`, zbrojownia `5`, smolarnia `5` (drewno), młyn `4` (pszenica).

Atomiki: 11→46, 13→31, 15→71, 19→47, 20→48, 21→49, 24→56, 25→52, 26→54, 27→55,
28→53, 29→67, 30→58, 31→57, 32→60, 33→62, 34→61, 35→69, 36→70, 37→65, 38→66,
39→59, 40→64, 41→63, 42→68, 43→50, 44→72, 45→73, 46→74, 47→75, 48→76, 49→77,
57→85, 58→86, **66→46**.

Usunięto błędny blok końcowy (`goodtype 66` / `type 12` / `atomicForProduction 1`).

### 3.2 `CN.PLMOD\tribetypes12\tribetypes.ini` (kopia: `.bak_20261020_232451`)

Dodano we **wszystkich 5 plemionach**:
`setatomic 56 46 "viking_miller_produce_flour"` (L189, 1225, 2247, 3275, 4283).
Dla plemienia 5 (Egipt) dodano też cały brakujący zestaw `setatomic 56 2..23`.

**Dlaczego animacja młynarza:** jest to **jedyna animacja zweryfikowana empirycznie**
jako produkująca (`event 190 21`). Żadna animacja `viking_collector_*` nie ma eventu 21,
a nowa nazwa w `atomicanimations.ini` nie miałaby klatek (nazwy seq są w plikach `.bmd`).
Koszt: smolarz odgrywa animację młynarza (job 56 i tak nie ma wpisu w `jobgraphics.ini`).

---

## 4. CO ZROBIĆ PO RESTARCIE (weryfikacja)

1. Zamknąć grę, uruchomić przez `modlauncher` (ini czytane tylko przy starcie).
2. **Młyn**: dostarczyć ≥1 pszenicy → po ~40 s powinna pojawić się mąka.
3. **Smolarnia**: dostarczyć drewno → po cyklu powinien pojawić się węgiel (slot 2, limit 15).
4. Jeśli smolarz znowu stoi (`36C=1`, `ABC=0`, `AB8=1`, `A68=5`) — problem nie leży
   w danych, tylko w doborze animacji; wtedy:
   * próba 2: `setatomic 56 46 "viking_smith_produce_tool_iron"` (dłuższa, „kuźnia"),
   * próba 3: `setatomic 56 46 "viking_potter_produce_crockery"`.
   Zmiana samej nazwy w `tribetypes.ini` — bez ruszania `goodtypes.ini`.
5. Sanity check innych budynków: piekarnia (mąka→chleb), garncarnia (muł+drewno),
   kamieniarz (kamień), browar (woda+12).

---

## 5. NARZĘDZIA / SZYBKIE FAKTY

* Globale: `pBld=[0x510bd0]`, `pRec=[0x511420]`, `pHt=[0x5113a0]`, `pJobs=[0x511180]`,
  `pTribe=[0x511200]`, `pAct=[0x5112fc]`, `[0x510bf0]` = tablica akcji (stride `0x58`).
* Stride: goodtype `0xD0`, htype `0x624`, budynek `0x7E0`, job `0x88`,
  plemię `0x1AE08`, akcja `0x138`, per-job w plemieniu `0x170`.
* Pola jednostki: `+0x18` job, `+0x1C` selgood, `+0x36C` stan, `+0x374` podstan,
  `+0xA68` faza, `+0xAB8` atomik, `+0xABC` flaga, `+0xAC0` indeks akcji,
  `+0xAC8` licznik sukcesów, `+0xACC` acc, `+0xAD0`, `+0xAD4`, `+0xB34` indeks budynku.
* Budynek: `+0x14` htype, `+0x1C` podejście, `+0x24` miejsce pracy,
  `+0x118+slot*4` stan, `+0x430+slot*4` licznik.
* Animacja: `event <klatka> <typ> [param]`; **typ 21 = koniec produkcji**.
* Frida: `Interceptor.attach` NIE odpala callbacków; tylko odczyt/zapis RAM.
  `Memory.readU32` nie istnieje → `ptr(addr).readU32()`. `duration_ms` ≤ 60000.
* MinHook (cnmod_hook) już hakuje: `473461, 46BAD7, 46D53A, 473695, 43267F, 44B910,
  42DA65, 44B58A, 42C977, 4316F3, 431DDF, 431CED, 431F37, 473618, 45C17B, 468BAE, 431B53`
  → Frida nie może tam hakować.
* `cnmod_hook.log` jest bezużyteczny do szybkiej analizy (spam `[owner] NULL!`),
  ale **jest źródłem wskaźników** (np. `unit=1c1c12e0` w linii `[gate 44B58A]`).


---

## FAZA 5 (2026-10-20, sesja pozna) — PRAWDZIWA przyczyna braku produkcji

### 1. `setatomic` NIE daje pozwolenia. Pozwolenie daje `jobtypes.ini`

To byo zródóo caego zamieszania z `allow[56][46]=0`.

* `tribetypes.ini` -> `setatomic <job> <atomic> "<animacja>"` **tylko wize par (job, atomic) z animacj**.
* `Data\logic\jobtypes.ini` -> `[jobtype] type N` + `baseatomics X` + `allowatomic Y`
  **wpywa do tablicy `allow[]`**, któr sprawdza `45C17B`:
  `byte[pJobs + job*0x88 + 0x24 + atomic] != 0`.
* `baseatomics 6` = wspólna baza dla czowieka (id 1-8, 10-15, 17, 20-23, 44, 45, 78, 79, 81, 82, 89, 91).
* Zawartość `allow[]` (odczyt z RAM) bya **dokadnie** równa
  `baseatomics + allowatomic` z `jobtypes.ini`:
  * job 19 (miller): baza + 46  -> `setatomic 19 46` dziaa
  * job 13 (smith):  baza + 60,63,64,68,69,70
  * job 56 (smolarz): baza + 52,53,56  (a w pliku byy tylko `allowatomic 56/52/53`)

### 2. POPRAWKA (wdrożona, data-only)

`Data\logic\jobtypes.ini`, blok `type 56` / `name "smolarz"`:

    baseatomics 6
    allowatomic 46      <-- DODANE
    allowatomic 56
    allowatomic 52
    allowatomic 53

Backup: `jobtypes.ini.bak_<data>`.

### 3. DOWÓD NA ŻYWO (bez restartu)

Zapis do RAM `allow[56][46]=1` na dziaajcej grze:

    PRZED  36c=1 ab8=1  abc=0 ac8=22  drewno=1 wegiel=0
    t=3s   36c=1 ab8=46 abc=1 ac8=23  drewno=1 wegiel=0
    t=18s  ...                        drewno=0 wegiel=1

**Smolarz wykona atomik 46 i wyprodukowa wgiel.** Mechanizm potwierdzony.

### 4. Uwaga: po wyprodukowaniu 1 szt. smolarz czeka na drewno

Stan `36c=1 ab8=46 abc=1 ac8=23` + `drewno=0` to **normalne oczekiwanie na surowiec**,
nie deadlock (mynarz job 19 ma identyczny stan i produkuje non stop).
Prawdziwy deadlock to `36c=1 ab8=<atomik chodzenia> abc=0`.

### 5. Mapowanie pól rekordu goodtype (0xD0) — USTALONE EMPIRYCZNIE

    +0x00  char[] nazwa (4 bajty w rekordzie)
    +0x20  landscapetype
    +0x24  (0xFFFFFFFF / wartość zależna od dobra)
    +0x30  flagi: byte0 isInputGoodFlag, byte1 isProducedInHouseFlag,
                  byte2 isProducedOnMapFlag, byte3 isBioLandscapeFlag
    +0x34  landscapeToHarvest
    +0x38  landscapeToPickup
    +0x3c  landscapeToStore
    +0x40  (typ krajobrazu dla zbioru; wheat=29, wood=24, coal=0)
    +0x44  atomicForCultivating   (wheat=35)
    +0x48  atomicForPlanting      (wheat=34)
    +0x4c  atomicForProduction
    +0x50  liczba zużywanych, +0x54 liczba skadników,
    +0x58+4i skadniki, +0x80+4i wymagane ilości, +0xA8+4i zużywane

### 6. CO JESZCZE JEST ZEPSUTE (pre-existing, potwierdzone diff-em z backupem)

Te defekty **nie powstay** od naszej zmiany `atomicForProduction`.

**(a) Brak jakichkolwiek jednostek job 24 (carrier).**
Skan pamici gry (2122 trafienia sygnatury jednostki) — job 24 wystpuje **0 razy**,
mimo że HQ (`logictype 1`) ma `logicworker 24 3`.
Skutek: **nic nie przewozi towarów midzy budynkami**.
Dowody: myn trzyma 39 mki (i dalej produkuje), piekarnia ma 0 mki;
piekarz stoi w `acc=2 ab8=22 ad0=11` (pickup mki) i nie postpuje.

**(b) Dobro 11 (food/mka) ma będne flagi:**
`isProducedOnMapFlag 1` + `landscapeToHarvest 29`, `landscapeToPickup 30`, `landscapeToStore 30`
(pickup == store!). Dobra produkowane w domu powinny mieć `isProducedOnMapFlag 0`
i brak pól `landscapeTo*` (tak jak węgiel 66).
To tłumaczy „piekarz schyla się nad pustym miejscem”.

**(c) Zduplikowane bloki `type` w `goodtypes.ini`** (ostatni wygrywa!):
* `type 27` x2 -> beer (L280) i wine (L289)  => wine nadpisuje beer
* `type 49` x3 -> cannon (L500), ammunition (L509), gunpowder (L518) => gunpowder wygrywa
* `type 59` x2 -> iron ore (L601), coal (L613) => coal nadpisuje iron ore
* `type 60` x2 -> gold ore (L625), gems ore (L637) => gems ore wygrywa

**(d) `landscapetype` wspódzielone przez wiele dóbr** (może być normalne — grupa brył),
ale wraz z (b) i (c) daje wrażenie „pomieszanych sprite'ów”.

### 7. Co dalej (kolejność)

1. **Restart gry** -> sprawdzić wgiel (must work: `allowatomic 46`).
2. Naprawić (b): `good 11` -> `isProducedOnMapFlag 0`, usunąć `landscapeTo*`.
   To samo dla 9, 10, 23, 28, 29, 30, 52, 55, 58 (wszystkie `isProducedInHouseFlag 1`
   + `isProducedOnMapFlag 1`). **Uwaga:** 23/28/29/30/52 mog być świadomie
   zbierane z mapy (owoce, miód, zioła) — sprawdzić po kolei.
3. Naprawić (c): rozjechać duplikaty `type` na wolne id (68+).
4. Zbadać (a): dlaczego HQ nie tworzy carrier'ów (job 24) — **to blokuje CAŁY transport**.
5. Dopiero potem sprity (`Data\engine2d\inis\goods\goodgraphics.cif`).

---

## FAZA 6 — ZWIESZKA GRY PRZY PRODUKCJI WĘGLA (2026-10-21, ~00:00)

### Objaw
Po dodaniu `allowatomic 46` (jobtype 56) smolarz zaczął produkować węgiel
i gra **zamarzła** (`Responding = False`, CPU 100% jednego rdzenia,
log przestał rosnąć). W logu przed zwiechą ~260 000 wywołań
`[g431F37] htype=57 good=66` w ciasnej pętli.

### Diagnoza (Frida, attach do zawieszonego procesu)
Próbkowanie `Process.enumerateThreads()` -> wątek gry stał w `0x44B530`
(wnętrze `FUN_0044b51c`), rejestry `esi=0x42`, `ecx=0x1db94c78`.

`FUN_0044b51c` to **skaner slotów dobra w obiekcie jednostki**:
```
44b51c: push esi
44b51d: mov  esi, [ecx+0x218]      ; zapamiętaj pozycję startową
44b523: inc  [ecx+0x218]           ; następny
44b529: cmp  [ecx+0x218], 0x42     ; <-- TU BYŁ BŁĄD (limit 66)
44b530: jl   44b539
44b532: and  [ecx+0x218], 0        ; zawijamy do 0
44b539: mov  eax, [ecx+0x218]
44b53f: mov  edx, [ecx+eax*4+0x21c]
44b546: cmp  edx, 0xb
44b54b: test edx, edx
44b54d: jg   44b569                ; 0 < v <= 11 => znalezione
44b54f: cmp  esi, eax
44b551: jne  44b523                ; nie wróciliśmy do startu -> dalej
```
**Jeśli `esi == 0x42` (66)**, to indeks po zawinięciu biegnie 0..65 i NIGDY
nie osiągnie `esi` => pętla nieskończona.

### Skąd `[obj+0x218] == 66`
`+0x1c` = selgood, `+0x218` = kursor skanowania ustawiany na id dobra.
Węgiel ma **id 66**, a tablica stanów dóbr w obiekcie (`+0x21C`, 66 dwordów,
indeksy 0..65) kończy się na 65. Kursor = 66 => zwiecha.

### Dowód z pamięci (jednostka smolarza `0x1db94c78`)
```
+0x18 = 56 (job), +0x1c = 66 (selgood = węgiel)
+0x218 = 66 (kursor), +0x21C + 66*4 = 11
tablica: idx 0 = 0, 1..65 = 12/13, 66 = 11, 67..82 = 0, 83+ = inne dane obiektu
```

### Poprawka
`etapa_gen/patches_ext.h` miał już sekcję COAL/SMOLARZ z czterema
`0x42 -> 0x43` (`0x44B279`, `0x42C93E`, `0x4319E1`, `0x431A92`)
i komentarzem "0x7F would overrun" — **brakowało piątej**:

```c
{ 0x004B52F, 0, 1, { 0x43, ... }, "FUN_0044b51c cmp dword [ecx+0x218],0x42 -> 0x43 ..." }
```
`0x43` = 67 => indeksy 0..66, obejmuje węgiel, nie wychodzi za tablicę.

**Uwaga:** testowałem `0x7F` (127) — gra się odblokowała, ALE skan wchodził
w nieużywane indeksy (67+), znalazł śmieci i ustawił `selgood=83` (korupcja).
Dlatego **tylko 0x43**.

### Weryfikacja na żywo (patch RAM tego samego bajtu)
- gra: `Responding = True`, log rośnie normalnie
- smolarz: `selgood=66`, `+0x218=66`, `ab8` cyklicznie 46/1/22/14, `ac8` rośnie
- smolarnia: zapas węgla **1 -> 5 -> 11**, drewno 0 (czeka na dostawę)
- brak zwiechy przez wiele minut

### Stan plików
- `etapa_gen/patches_ext.h` — dodana 5. łatka (`0x004B52F` = `0x43`)
- `etapc/EtapC.dll` — **zbudowany** (94208 B, 2026-10-21 00:07)
- `EtapC.dll` w rootcie — **wciąż STARY** (93696 B); podmiana wymaga
  zamknięcia gry (plik zablokowany)
- `Data/logic/jobtypes.ini` — `allowatomic 46` w `type 56` (bez zmian, OK)

### WAŻNE
Bez podmiany `EtapC.dll` gra **znowu się zawiesi** przy pierwszym węglu
(smolarz dojdzie do skanera z kursorem 66).

---

## FAZA 7 — SPRITY, RECEPTURY I „MĄKA Z ZIEMI" (2026-10-21, wieczór)

### 0) ZASADNICZE ODKRYCIE: nazwy w `goodtypes.ini` są fikcyjne

Prawdziwe nazwy dóbr (to, co gracz widzi) są w
`Data\text\pol\strings\gameobjects\goods.ini` (`stringn <id> "..."`):

```
1 Woda  2 Glina  3 Kamień  4 Pszenica  5 Drewno  6 Żelazo  7 Złoto  8 Moneta
9 Skóra 10 Wełna 11 Mąka    12 Miód     13 Zioło   14 Grzyb  15 Oliwa  16 Żywność
17 Ciastko 18 Owoc 19 Chleb 20 Ciastko 21 Mięso 22 Ryba 23 Kiełbasa 24 Cegła
25 Dachówka 26 Kamienny blok 27 Marmur 28 Naczynia 29 Meble 30 Buty
31 Drewniane narzędzie 32 Żelazne narzędzie 33 Tunika 34 Skórzana zbroja
35 Kolczuga 36 Zbroja płytowa 37 Krótki łuk 38 Długi łuk 39 Drewniana włócznia
40 Żelazna włócznia 41 Krótki miecz 42 Długi miecz 43 Miód pitny
44-49 mikstury, 50-55 amulety, 56 Zdobycz, 57 Owca, 58 Wół,
59 Wózek ręczny, 60 Zaprzęg, 61 Drakkar, 62 Karvi, 63 Katapulta, 64 Skrzynia,
65 Wszystko, 66 WĘGIEL
```

`name` w `goodtypes.ini` (np. 19 = "leather armor", 11 = "food", 30 = "milk")
**nie ma nic wspólnego z grą** — to stare/nieaktualne etykiety. Nie używać ich
do wnioskowania o znaczeniu dobra. **Zawsze patrzeć na `goods.ini` i na
`logicproduction` w `houses.ini`.**

### 1) `houses.ini` — brak linii `type`

`CN.PLMOD\types\houses.ini`: 57 bloków `[logichousetype]`, **htype = numer
bloku (1-based)**. Nie ma pola `type`. Kluczowe produkcje:

| htype | budynek | produkuje | wejścia (logicstock z flagą 1) |
|---|---|---|---|
| 13 | work mill | 11 (Mąka) | 4 |
| 14 | work bakery 00 | 19 (Chleb) | 1, 11 |
| 15 | work bakery 01 | 19, 20 | 1, 11, 12 |
| 16 | work brewery | 43 | 1, 12 |
| 17 | work animal farm | 4,21,10,9,57,58 | 1, 4 |
| 18/19 | work sewery | 30 / 30,34,33 | 9 / 9,10 |
| 20/21 | work pottery | 24 / 24,25,28 | 2,5 |
| 23-26 | work joinery | 31 / +39,29 / +59,60 / +61,62 | 5, 9 |
| 27/28 | work armory | 37 / 37,38,63 | 5 / 5,6 |
| 29/30 | mason hut | 26 / 26,27 | 3 |
| 31/32 | work smithy | 32,41,40 / +42,35,36 | 6,5,39 |
| 33 | work coin mint | 8 | 5, 7 |
| 34 | work herb hut | 13 | – |
| 35/36 | work druid | 15 / 15,44-49 | 14 / 14,1,13,8 |
| 57 | work charcoal burner | 66 (Węgiel) | 5 |

### 2) BUG „piekarz zbiera mąkę z ziemi" — NAPRAWIONY

Rekord dobra 11 (Mąka) miał w RAM:
`flags=[1,1,1,0]` (inHouse=1, **onMap=1**), `harv=29 pick=30 stor=30`,
`atomicForHarvesting=29`. Engine skoro widzi `onMap=1`, wysyła robotnika
**zbierać mąkę z pola** zamiast czekać na dostawę z młyna.

Klasa błędu dotyczyła dóbr: **10, 11, 12, 23, 28, 29, 30, 58** (dodane
`onMap=1` + `landscapeTo*`), oraz odwrotnie **18, 56** (miały `onMap=0`).

Naprawa (`.ai/tmp/fix_mapflags.py`) — wartości z oryginalnego `goodtypes.cif`:
- 10, 11, 23, 28, 29, 30, 58 → `isProducedOnMapFlag 0`, usunięte
  `landscapeToHarvest/Pickup/Store`, `atomicForHarvesting`, `isBioLandscapeFlag`
- 12 → `isProducedInHouseFlag 1`, `isProducedOnMapFlag 0`, pickup/store 32
- 18, 56 → `isProducedInHouseFlag 0`, `isProducedOnMapFlag 1`
- backup: `goodtypes.ini.bak2_20261021_200235`

### 3) RECEPTURY — przywrócone z oryginału

Poprzednia sesja nadpisała `productionInputGoods` regułą „stock budynku − output",
ale dopasowywała budynki **po nazwach z `goodtypes.ini`** (które są fikcyjne),
więc receptury się pomieszały (np. chleb ← 2 5 = glina+drewno, kiełbasa ← 23
czyli sama siebie, wszystkie zbroje ← 6 5 39).

Naprawa (`.ai/tmp/fix_recipes.py`): dla typów **1..58** przywrócone
`productionInputGoods` z `.ai/decoded/goodtypes.txt` (37 zmian). Typy 59+ bez zmian.
- Przykłady: 19 Chleb ← 11 1, 23 Kiełbasa ← 21, 28 Naczynia ← 2 5 5,
  33 ← 10, 34 ← 9 9, 35 ← 5 6 6, 36 ← 5 5 6 6 6, 40 ← 39 6, 41 ← 5 6,
  57 Owca ← 4 4 1, 58 Wół ← 4 4 1 1
- `atomicForProduction` **nie ruszane**
- backup: `goodtypes.ini.bak3_20261021_200324`

### 4) SPRITY — nowy `goodgraphics.ini`

Silnik czyta `data\engine2d\inis\goods\goodgraphics.ini` (string w exe),
a `.ini` ma priorytet nad `.cif`. Dotychczasowy `goodgraphics.cif` był
**niekompletny i błędny**:

- brak wpisów dla: 8, 18, 22, 23, 33-36, 43-66 (w tym **66 Węgiel**)
- błędne: 19 Chleb → `good_tile`, 20 → `good_tile`, 21 Mięso → `good_honey`,
  30 Buty → `good_tile`

Utworzono **`Data\engine2d\inis\goods\goodgraphics.ini`** — pełna mapa 1..67.
Dostępne nazwy ikon (`humans\randompalette.cif` + `bin\palettes\goods\goods_*.pcx`):
```
good_Water good_clay good_stone good_wheat good_Wood good_iron good_gold
good_leather good_wool good_flour good_honey good_herb good_mushroom good_holyoil
good_food_simple good_bread good_food good_brick good_tile good_pillar
good_ornament good_crockery good_furniture good_shoes good_tools_wooden
good_tools_iron good_armor_wool good_armor_chain good_armor_plate good_bow
good_spear_wooden good_spear_iron good_sword good_longsword
good_potion_food good_potion_stamina good_HandCart good_OxCart
```
Uwaga: `good_bread`, `good_shoes`, `good_food`, `good_sword`, `good_longsword`,
`good_spear_iron`, `good_spear_wooden` **nie były używane w .cif**, ale mają
własne palety `goods_*.pcx` — jeśli któraś ikona zniknie, to znaczy że nazwa
nie istnieje w `ls_goods.bmd` i trzeba wrócić do `good_food_simple`/`good_leather`.
**66 Węgiel → `good_stone`** (brak dedykowanego sprite'a węgla).

### 4b) KRYTYCZNE: `goodgraphics.ini` NIE JEST CZYTANY

Silnik **ignoruje** `Data\engine2d\inis\goods\goodgraphics.ini` — ładuje tylko
`.cif`. Dowód: po restarcie nazwy `good_bread`/`good_shoes`/`good_spear_iron`
nie występowały w pamięci procesu, a `good_potion_food` (z `randompalette.cif`)
tak. Plik `.ini` przemianowany na `goodgraphics.ini.NIEUZYWANY`.
**Edytować wyłącznie `goodgraphics.cif`** przez `cipher`: `cif2txt.exe T`.

Procedura (sprawdzona, round-trip bajt w bajt):
```
cif2txt.exe C goodgraphics.cif orig.txt
# edycja orig.txt, naglowek <000000C9> = liczba linii miedzy BEGIN i END
cif2txt.exe T orig.txt goodgraphics.cif
```
Nagłówek: `<CULTURES_CIF_BEGIN><03FD><%08X>` = liczba linii treści (N*3 dla N wpisów).

### 4c) DOBRA 59–63 TO WYROBY, NIE SUROWCE

`houses.ini`:
| htype | nazwa (houses.cif) | produkuje |
|---|---|---|
| 23/24 | Warszt. ciesielski 1/2 | 31, 39, 29 |
| 25/26 | Warszt. ciesielski 3/4 | + **59, 60** (+61, 62 w htype 26) |
| 27/28 | Warszt. płatnerski 1/2 | 37 / +38, **63** |

W słownikach `Data\text\pol\strings\gameobjects\goods.ini` id 59-63 to
**Wózek ręczny, Zaprzęg, Drakkar, Karvi, Katapulta** — czyli pojazdy/wyroby.
Tymczasem `goodtypes.ini` opisywał je jako „iron ore/gold ore/clay/marble/sulfur"
z `isProducedOnMapFlag 1` i `landscapeToHarvest` = **złoża żelaza(20), złota(23),
kamienia(17), gliny(14)**. Efekt: robotnik zbierał „Wózek ręczny" z góry żelaza,
a ikona była losowa (brak wpisu w `goodgraphics.cif`).

Naprawa (`.ai/tmp/fix_carts.py`): 59–63 → `isProducedOnMapFlag 0`, usunięte
`landscapeTo*`/`atomicForHarvesting`. Ikony: 59 `good_HandCart`, 60–62
`good_OxCart`, 63 `good_HandCart`. Backup: `goodtypes.ini.bak4_20261021_203215`.

### 5) Co jeszcze zostało

1. **Transport** — brak jednostek `job 24` (przewoźników). HQ ma
   `logicworker 24 3`. To blokuje dostawy między budynkami (młyn → piekarnia).
2. **Duplikaty `type` w `goodtypes.ini`**: 27 (beer/wine), 49 (cannon/ammunition/
   gunpowder), 59 (iron ore/coal), 60 (gold ore/gems ore). Wygrywa ostatni blok.
   Skutek: dobra „iron ore", „gold ore", „cannon", „ammunition" **nie istnieją**,
   a 59 i 66 to dwa razy „coal". Do rozdzielenia na wolne id 68+.
3. Dedykowany sprite węgla (wymaga nowego bob+pcx).

---

## FAZA 8 (2026-10-21, wieczór) — IKONY DÓBR: ROOT CAUSE = `landscapetype`

### Objaw
W magazynie dobra miały cudze obrazki: grzyb (14) i oliwa (15) → ikona **drewna**,
a cegła (24), dachówka (25), kamienny blok (26), marmur (27) → ikona **zboża**.

### Błędne tropy (odrzucone — nie tracić na nie czasu)
- **`goodgraphics.cif` / `goodgraphics.ini` NIE sterują ikoną.** Silnik
  (`FUN_0048a162`) czyta wyłącznie `data\engine2d\inis\goods\goodgraphics.ini`
  i mapuje dobro → **RandomPalette** z `Data\engine2d\inis\humans\randompalette.cif`.
  `FUN_0048a857` nakłada wyłącznie **kolory/palety** (16 slotów × 0x40 B).
  Podmiana wpisu w tej tablicy w RAM (test) **nie zmieniła ikon** — potwierdzone.
- `ls_goods.bmd`, nazwy `good_*`, `palettes\goods\*.pcx` — to palety/kolor, nie kształt.

### Root cause
Ikona dobra = **`landscapetype`** w `Data\logic\goodtypes.ini` (grafika terenowa dobra,
ta sama, która leży na ziemi). Nazwy typów: `Data\logic\landscapetypes.cif` (87 typów).
CnMod 1.2 wydano ze „sklejonymi" wartościami — wiele dóbr dzieliło jeden typ:

| dobro | było | efekt | poprawione na |
|---|---|---|---|
| 11 Mąka | 27 = wheat (growing) | zboże | 30 flour |
| 12 Miód | 14 = mud | błoto | 32 honey |
| 13 Zioło | 23 = gold | złoto | 35 herb |
| 14 Grzyb | 7 = wood | **drewno** | 37 mushroom |
| 15 Oliwa | 7 = wood | **drewno** | 38 holy_oil |
| 19 Chleb | 25 = leather | skóra | 42 bread |
| 21 Mięso | 7 = wood | drewno | 44 meat |
| 23 Kiełbasa | 29 = wheat | zboże | 46 sausage |
| 24 Cegła | 29 = wheat | **zboże** | 50 brick |
| 25 Dachówka | 29 = wheat | **zboże** | 51 tile |
| 26 Blok | 29 = wheat | **zboże** | 52 pillar |
| 27 Marmur | 29 = wheat | **zboże** | 53 ornament |
| 30 Buty | 29 = wheat | zboże | 56 shoes |
| 39–42 | 14 / 17 / 20 | — | 63/64/65/66 (spear/spear/sword/sword) |
| 64 Skrzynia | 14 | — | 85 chest_wooden |
| 66 Węgiel | 7 | — | 16 stone_ore |

Pełne mapowanie 1–66: `.ai/tmp/fix_landscapetype.py` (59 zmian),
backup `Data\logic\goodtypes.ini.bak5_20261021_223524`.
Weryfikacja w RAM (PID 5128): `14→37, 15→38, 24→50, 25→51, 26→52, 27→53` — OK.
**Użytkownik potwierdził: „teraz są dobre obrazki w surowcach".**

### Ważne
- Ikony są **renderowane raz przy wczytywaniu gry** — zmiana w RAM **nie odświeża**
  gotowej grafiki, **wymagany restart**. (Dlatego test w pamięci dał fałszywy negatyw.)
- To **nie** wina `cnmod_hook.dll` ani `EtapC.dll`: backup z 19.10
  (`goodtypes.ini.bak_20261020_232318`) miał te same złe wartości.
- Eksperymentalny `goodgraphics.ini` **usunięty**, `goodgraphics.cif` przywrócony
  do oryginału (3066 B, 21.04.2019).

### Nowy błąd znaleziony po drodze: CRASH przy węglu (66)
`FUN_0047e381` case 0xA (`0x47E7CD`–`0x47E7E2`):
```
0x47E7D0  cmp eax, 0x42
0x47E7D3  jl  +4          ; good < 66  -> &DAT_00568740[good]
0x47E7D5  xor eax, eax    ; good >= 66 -> NULL
0x47E7E2  mov ecx, [eax]  ; deref NULL = 0xC0000005
```
Crash `0xC0000005` @ RVA `0x7E7E2` (Event Log: 21:06 i 21:44) = rysowanie ikony
dobra 66 (węgiel). Tablica `DAT_00568740` ma `0x108` B = 66 wpisów, a loader
`FUN_0048a162` też odrzuca `good >= 0x42`.

**Poprawka wpisana do `etapa_gen/patches_ext.h`** (sekcja „IKONY DÓBR"):
1. `0x007E7D1` imm `0x42` → `0x43` (granica w rysowaniu),
2. `0x008A193` imm `0x108` → `0x10C` (tablica 67 wpisów),
3. `0x008A254` imm `0x42` → `0x43` (granica loadera).

**Status: wpisane, `EtapC.dll` jeszcze NIE przebudowany** — wymaga zamkniętej gry.

### Do zrobienia
1. **Przebudować `EtapC.dll`** (`etapc\build.bat`) i wdrożyć — fix crashu węgla.
2. Transport (`job 24`, przewoźnicy) — bez zmian.
3. Duplikaty `type` 27/49/59/60 w `goodtypes.ini` — bez zmian.
