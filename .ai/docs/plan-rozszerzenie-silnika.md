# Plan: pełne rozszerzenie silnika CN.PLMOD (budynki i surowce)

**Data:** 2026-10-09
**Cel:** umożliwić dodawanie **wielu** nowych budynków i surowców w przyszłości (nie tylko
smolarz/huta + węgiel/stal), bez usuwania istniejącej zawartości.
**Status:** Etap 0 ✅ / Etap 1 ✅ / Etap 2 ✅ / Etap 3+ w toku.
**Zakres:** `CN.PLMOD.exe` (`EtapC`), edytory (`EtapD`) jako osobny etap, dane `.ini`, narzędzia.

> **Naprawa crasha zakupki (2026-10-10):** `CN.PLMOD.exe` (pakietowy mod) wydawał się
> crashować przy kliknięciu dowolnego budynku (EIP=0xBD750, AV WRITE @0x38) — **niezależnie
> od EtapC** (czysty 0/303, stock exe). Przyczyna: modder podmienił w 9 funkcjach
> „panel-rect" (`0xA8851`, `0xBC809`, `0xBCA0F`, `0xBCC15`, `0xBD3A8`, `0xBD745`,
> `0xBD833`, `0xBDCC6`, `0xBDDEA`) sekwencje `push 0xH/add eax,-0xH/push 0xW/add eax,-0xW`
> (wymiary paneli z globali `[0x569268]`/`[0x569264]`) na **śmieciowe bajty** (`b4 00 00 00`,
> `d4 fe`, `c2 01`), które po wykonaniu dają `00 00` = `add [eax],al`. Delta exe-vs-orig =
> **81 B w 30 blokach**. Naprawa: **30 patchy „R"** w `patches_ext.h` przywracających bajty
> z `CN.PLMOD.exe.orig` (wszystkie 9 regionów = orig bajt-w-bajt; 333/333 patchy OK;
> gra działa, kliknięcie budynku OK). Panele wróciły do oryginalnych rozmiarów
> (powiększanie pod nowe ID — poprawnym kodem — w dalszych etapach).

> **Werdykt na wejściu:** proste „poszerzenie w miejscu" (stride `0x37 → 0x40`, `0x42 → N`)
> **jest niemożliwe** — tablice luster w strukturze aktora są upakowane co do bajtu
> (42 plemiona × rozmiar tablicy). Rozszerzenie wymaga **przeniesienia tablic** (relokacji)
> i powiększenia elementu struktury. Poniższy plan realizuje to bez przesuwania istniejących
> pól, więc unika setek patchy displacementów w przeplatanych polach.

---

## 1. Ustalenia o silniku (zweryfikowane na binarium)

### 1.1 Struktura aktora (per gracz)
- Baza globalna: `[0x510BC4]` (wskaźnik do tablicy 20 elementów).
- Rozmiar elementu: **`0x4A80`** (stride gracza `imul reg,reg,0x4A80`).
- Liczba graczy: **20** (`cmp ...,0x14`).
- W obrębie elementu, dla **42 plemion**, leżą upakowane tablice flag:

| Pole | Offset bazowy | Stride | Rozmiar regionu | Rozmiar = 42×stride |
|---|---|---|---|---|
| jobs A | `0x18` | `0x38` (56) | `0x18..0x948` | `0x930` |
| jobs B | `0x948` | `0x38` | `0x948..0x1278` | `0x930` |
| **surowce A** | `0x1278` | `0x42` (66) | `0x1278..0x1D4C` | `0xAD4` |
| **surowce A2** | `0x1D4C` | `0x42` (66) | `0x1D4C..0x2820` | `0xAD4` |
| **domy A** | `0x2820` | `0x37` (55) | `0x2820..0x3126` | `0x906` |
| **domy B** | `0x3126` | `0x37` | `0x3126..0x3A2C` | `0x906` |
| **pojazdy** | `0x3A2C` | `7` | `0x3A2C..0x3B52` | `0x126` |
| pola skalarne | `0x3B52` | — | `0x3B52..0x3C78` | — (`0x3B80`, `0x3C00/3C01`) |
| **surowce B** | `0x3C78` | **`0x38` (56!)** | `0x3C78..0x45A8` | `0x930` |
| dalsze pola | `0x45A8`, `0x460C…0x4628`, `0x4944…0x4A37` | — | — | — |

- **Brak luzu:** `0x3126 = 0x2820 + 42×0x37` (domy B tuż za domami A). To obala wcześniejszą
  hipotezę „8 wierszy → dużo luzu" — pętla iteruje **42 plemiona** (`cmp [ebp-0x1c],0x126`,
  krok 7), zawsze ~41–42 razy.
- Element jest wypełniony niemal do końca (`0x4A37` to ostatnie zaobserwowane pole) →
  **przeniesienie tablic do „wolnego ogona" wewnątrz `0x4A80` jest niemożliwe**.
  Trzeba **powiększyć element**.

### 1.2 Rekord plemienia
- Rozmiar: **`0x1AE08`**, tablica **42** rekordów (`0x468D50`).
- Offset pól (upakowane):
  `+0x50A0` jobs (56 B), `+0x50D8` surowce A (66 B), `+0x511A` surowce B (66 B),
  `+0x515C` flagi domów (55 B), `+0x5193` pojazdy (8 B), od `+0x519C` dalsze pola.

### 1.3 Pętla kopiująca (tribe → actor)
- `0x9DDD`–`0xA067`. Iteruje **graczy (20)** × **plemiona (42)**.
- Kopiuje jobs (`+0x50A0`), surowce A (`+0x50D8`), surowce B (`+0x511A`),
  domy (`+0x515C`), pojazdy (`+0x5193`) do luster w strukturze aktora.
- Stride'y realizowane przyrostowo (`add [ebp-0x18],0x37`, `add [ebp-0x10],0x42`,
  `add esi,0x38`, `add [ebp-0x1c],7`), a limity przez `cmp eax,0x37/0x42/0x38/7`.
- **Anomalia:** surowce B są indeksowane przyrostem `esi` = **stride jobs `0x38`**, mimo że
  kopiowane jest 66 surowców (`cmp eax,0x42`). Region `0x3C78..0x45A8` = 42×0x38,
  więc tribes nachodzą na siebie o 10 B. **To trzeba rozstrzygnąć w fazie discovery**
  (być może to bug silnika, ale może „surowce B" mają inną semantykę — np. per-job).

### 1.4 Liczniki odwołań (skala patchy)
| Stała | Znaczenie | Ref |
|---|---|---|
| `0x4A80` | stride elementu aktora | **246** |
| `0x1AE08` | rozmiar rekordu plemienia | 28 |
| `0x37` | licznik/stride domów | 83 (imm+disp) |
| `0x42` | licznik/stride surowców | 166 (imm+disp, w tym śmieci `int/out/'B'`) |
| `0x151BC` | rozmiar tablicy domów (55×0x624) | 6 |
| `0x35A0` | rozmiar tablicy surowców (66×0xD0) | 6 |
| `0x468D50` | koniec tablicy plemion | 2 |

Odwołania baz luster w aktorze (do przepięcia przy relokacji):
`0x1278`=26, `0x2820`=13, `0x3126`=10, `0x3A2C`=1, `0x3C78`=14, `0x1D4C`=21.
Odwołania baz w rekordzie plemienia: `0x50D8`=2, `0x511A`=2, `0x515C`=2, `0x5193`=2.

### 1.5 Ustalenia Etapu 0 (szczegóły: `.ai/docs/etap0-discovery-aktor.md`)
- **`0x1D4C` = surowce A2** — pełna tablica per plemię (42×`0x42`), rozszerzana razem z A/B.
- **Surowce B: stride `0x38` potwierdzony na 100%** (wszystkie 22 stale w pasmie na siatce
  `0x38`, brak ścieżki `0x42`; surowce 56..65 nachodzą na kolejne plemię — bug do fixa).
- **`0x4A80`: 241 realnych użyć** (208× `imul` + 33× `add`); 5 śmieci z desyncu. Wszystkie
  dot. stride'u elementu aktora.
- Pula elementów: `20 × 0x4A80 = 0x5D200`; dodatkowe **52** miejsca (28 cmp + 14 mov + …)
  czyta rozmiar puli — do zaktualizowania.
- Liczby site'ów stride'ów (faza 1): `0x37`=15, `0x42`=45 (43 realne), `0x38`=147
  (głównie jobs — bez zmian; site'y surowców B do wyodrębnienia w generatorze), 7=11.
- **Zapis gry:** binarny chunkowany `hoix<TAG>CI`+len; nie zawiera surowej stałej `0x4A80`.
- Rekomendacja limitów: `NEW_HOUSE_MAX = NEW_GOOD_MAX = 0x7F` (127) → element
  ~`0xB2B6`, pula ~`0xDFC00`.

---

## 2. Strategia (bez przesuwania istniejących pól)

Zasada: **nie przesuwamy niczego, co już ma stały offset** (unika to setek patchy
przeplatanych pól, np. `0x1D4C`, `0x460C`). Zamiast tego:

1. **Rekord plemienia** (42×`0x1AE08`): przenosimy tablice `surowce A/B`, `flagi domów`,
   `pojazdy` na **ogon rekordu** i powiększamy rekord. Pola od `+0x519C` w górę **nie ruszają się**.
2. **Struktura aktora** (20×`0x4A80`): powiększamy element i przenosimy wszystkie tablice
   lustrzane na **nowy ogon**, przepinając wyłącznie ich adresy bazowe. Pola `0x1D4C`,
   `0x45A8`, `0x460C…` itd. **zostają na miejscu** (o ile discovery potwierdzi, że są
   niezależnymi polami, a nie częścią przenoszonych tablic).
3. Wszystkie **stride'y** przenoszonych tablic i **granice pętli** przechodzą na nowe liczniki.
4. **Walidatory/loopy** `0x37`/`0x42`/rozmiarów tablic — patchujemy tylko realne.

### 2.1 Nowe limity i skalowalność
- Flagi to **bajty**, indeksy też → bezpieczny sufit to **127** (porównania używają `jl`/`jge`
  ze znakiem; `0x80` byłoby ujemne). **NIE używać `NEW_*_MAX = 128`**.
- Proponowane cele (z zapasem na przyszłość):
  - `NEW_HOUSE_MAX = 0x64` (100) lub `0x7F` (127) — do decyzji.
  - `NEW_GOOD_MAX  = 0x64` (100) lub `0x7F` (127).
- Wszystkie nowe rozmiary i offsety liczy makro/stała; **żadnych „magic numbers" w patchach**.

### 2.2 Docelowy układ (propozycja)
Nowy bazowy offset „ogonu" aktora = `NEW_ELEM_BASE = 0x4A80` (można wyrównać do `0x4B00`).
Kolejno, w nowym ogonie (przykład, do wyliczenia skryptem):
```
NEW_HOUSE_A   = NEW_ELEM_BASE
NEW_HOUSE_B   = NEW_HOUSE_A + 42*NEW_HOUSE_MAX
NEW_GOODS_A   = NEW_HOUSE_B + 42*NEW_HOUSE_MAX
NEW_GOODS_B   = NEW_GOODS_A + 42*NEW_GOOD_MAX
NEW_VEHICLES  = NEW_GOODS_B + 42*NEW_GOOD_MAX
NEW_ELEM_SIZE = NEW_VEHICLES + 42*8        (wyrównane)
```
Rekord plemienia — analogicznie na ogonie `NEW_REC_BASE = 0x1AE08`.

### 2.3 Model „rezerwy slotów" — dlaczego nie trzeba zapełniać limitów od razu

Rzeczywista zawartość (które budynki/surowce „istnieją" i co robią) żyje w danych:
`houses.ini`, `goodtypes.*`, `tribetypes.ini`, stringi, gfx. Tablice w pamięci aktora
i rekordu to **reprezentacja per-plemię × per-ID**; ich rozmiar po podniesieniu limitu
wynika z `NEW_HOUSE_MAX`/`NEW_GOOD_MAX`, a **nie** z liczby zdefiniowanych obiektów.

Podniesienie limitu tworzy **rezerwę slotów**, którą zapełniamy stopniowo:

| „Miejsce" | Rodzaj | Puste sloty | Kiedy się wypełnia |
|---|---|---|---|
| Tablice lustrzane aktora (stride `0x7F`) | flagi (bajty) | `0x00` = „brak" — normalny stan gry | dodanie `allowhouse`/`allowgood` w danych |
| Rekord plemienia (nowy ogon) | flagi | `0x00` | jw. |
| Tablica domów `0x624` (alokacja) | rekordy | zerowane przy alokacji | wczytanie danych (staty/GfxHouse) |
| Tablica surowców `0xD0` (alokacja) | rekordy | zerowane przy alokacji | wczytanie danych (`goodtypes.*`) |
| Definicje `.ini`/logic | treść | brak wpisu = ID niezdefiniowane | dodanie przez modkit (Etap 7) |

Zasady:
1. **Luki między zdefiniowanymi ID są dozwolone.** Dane ładują się po ID, silnik nie
   wymaga ciągłości zakresu. Przyszłe rozszerzenia dokładają kolejne ID bez przepisywania
   istniejącej zawartości ani patchy.
2. **Pętle kopiujące i walidatory operują na licznikach, nie na treści** — kopiują zera
   i są bezpieczne wobec pustych slotów (pod warunkiem, że iterują do licznika).
3. **Jedyny wymóg: pętle *prezentujące* treść (UI/menu) muszą pomijać puste sloty**,
   a nie zakładać ciągłego zakresu `0..MAX` z grafiką/stringami. To robota Etapu 4.

---

## 3. Zakres patchy

### 3.1 Struktura aktora
- **P1. Stride elementu** `0x4A80 → NEW_ELEM_SIZE`: **246 miejsc**. Wszystkie mają jedną
  z form: `imul r,r,0x4A80` (`69 xx 80 4A 00 00`), `add r,0x4A80` (`81 xx 80 4A 00 00` /
  `05 80 4A 00 00`), `mov r,0x4A80` (`BB 80 4A 00 00`). Generowane maszynowo.
- **P2. Alokacja tablicy aktora** — zlokalizować miejsce zapisu `[0x510BC4]`
  (kandydaci: `0x8087`, `0x8B77`) i zmienić na `20 × NEW_ELEM_SIZE`.
- **P3. Adresy bazowe tablic lustrzanych** — przepiąć z `0x1278/0x2820/0x3126/0x3A2C/0x3C78`
  na nowe offsety (26+13+10+1+14 ref).
- **P4. Stride'y tablic** — `imul ...,0x37` (14 lokalizacji) i `imul ...,0x42`
  (~38 kandydatów do klasyfikacji) oraz `add ...,0x37/0x42` w pętli kopiującej.
- **P5. Granice pętli kopiującej** `0x9E65`, `0x9E82`, `0x9EA1`, oraz init
  `0x9E07` (`=0x37`), `0x9DF6` (`=0x42`), `0xA02E`, `0xA039`.

### 3.2 Rekord plemienia
- **P6a. Rozmiar rekordu** `0x1AE08 → NEW_REC_SIZE` — **28 site'ów** (mov/add/imul, `imm_pos`).
- **P6b. Koniec tablicy rekordu** `0x468D50 → NEW_REC_ARREND` — **2 site'y** (`0xAF51` cmp, `0x13EAB` mov).
- **P7. Relokacja baz** `0x50D8`, `0x511A`, `0x515C`, `0x5193` na ogon rekordu — **8 ref**
  (read copy `0x9E4D/0x9E6C/0x9E89/0x9EA8` + write guard `0x142BB/0x142FD/0x1431E/0x1433F`).
  Bazy rekordu występują **jedynie jako mem-disp32** w tych 8 miejscach (skan imm+mem);
  `jobs` `+0x50A0` (2 refy: `0x9E33` read, `0x142DC` write) **zostaje na miejscu**.
- **P8. Walidatory flag** `0x142F4` (`0x37`), `0x14315`/`0x14336` (`0x42`, imm8 `→ 0x7F`) — **3 site'y**.
- **Wykluczone (SPECIAL → Etap 4/6):** walidatory mapy produkcji `0x14289`/`0x14292`
  (gate `[esi+edi*8+0x1492C]`, tablica 66×8 B **nie relokowana**) — podniesienie wymaga rozszerzenia mapy.
- **Stałe rekordu (Etap 2), układ ogona:**
```
NEW_REC_SUROW_A = 0x1AE08          (0x7F B)
NEW_REC_SUROW_B = NEW_REC_SUROW_A + NEW_GOOD_MAX    (0x1AE87, 0x7F B)
NEW_REC_DOMY    = NEW_REC_SUROW_B + NEW_HOUSE_MAX   (0x1AF06, 0x7F B)
NEW_REC_VEH     = NEW_REC_DOMY    + NEW_HOUSE_MAX   (0x1AF85, 8 B, bez rozszerzania)
NEW_REC_SIZE    = (NEW_REC_VEH + 8 + 15) & ~15      (0x1AF90)
NEW_REC_ARREND  = 42 * NEW_REC_SIZE                 (0x46CDA0)
```
- Pola od `+0x519C` w górę (w tym mapa produkcji `0x1492C`, tablice `0x14B3C`, `0x14C08`)
  **zostają na starych offsetach** — zero patchy displacementów na nich.

### 3.3 Walidatory i rozmiary tablic
- **P9.** `0x151BC` (6 miejsc) → `NEW_HOUSE_MAX × 0x624`.
- **P10.** `0x35A0` (6 miejsc) → `NEW_GOOD_MAX × 0xD0`.
- **P11.** Klasyfikacja **83** wystąpień `0x37` i **166** `0x42`: odsiać śmieci
  (`int 0x42`, `out 0x42`, `mov al,0x42`=ASCII 'B', `push 0x42`=rozmiary buforów,
  offsety `[reg+0x42]`), a wśród realnych `cmp`/`imul` wybrać te dot. domów/surowców
  (analiza data-flow: skąd pochodzi indeks). Patchować tylko potwierdzone.

### 3.4 Pętla kopiująca — zmiana kodu
Ponieważ surowce B mają stride `0x38`, a potrzebują `NEW_GOOD_MAX`, pętla wymaga
**rozseparowania wskaźników** (surowce B nie mogą dłużej reużywać `esi`).
Rozwiązanie: **code cave** (trampolina) w `EtapC.dll` albo przechwycenie funkcji
kopiującej. To najbardziej delikatny punkt — patrz rozdz. 5 (Etap 3).

### 3.5 Iteratory i walidatory — wykaz do zabezpieczenia (Etap 4)

Po podniesieniu limitów każda pętla, która **iteruje po ID** lub **prezentuje treść**,
musi przejść przegląd pod kątem: (a) granicy iteracji (licznik `→ NEW_*_MAX`),
(b) pomijania pustych slotów (`0x00`/zerowany rekord) przy dereferencjach danych.

Katalog dla Etapu 4 (aktualizowany w miarę postępu discovery):

| RVA | Co to robi | Do zrobienia w Etapie 4 |
|---|---|---|
| `0x15368` | ctor/alokator tablicy domów `0x624` (55→127 rekordów) | powiększyć alokację `0x151BC → NEW_HOUSE_MAX×0x624`; puste rekordy = zera |
| `0x158D5`, `0x15923` | walkery tablicy domów `0x624` | granica iteracji `0x37 → 0x7F`; pomijanie pustych rekordów przy odczycie |
| `0x151BC` (6 miejsc) | rozmiar alokacji tablicy domów | `→ NEW_HOUSE_MAX × 0x624` (P9) |
| `0x35A0` (6 miejsc) | rozmiar alokacji tablicy surowców | `→ NEW_GOOD_MAX × 0xD0` (P10) |
| `0x142F4`, `0x14315`, `0x14336` | walidatory flag rekordu (E2) | **WYKONANE w Etapie 2:** granice `→ 0x7F` |
| `0x14289`, `0x14292` | walidatory mapy produkcji `0x1492C` (66×8 B, nie relokowana) | Etap 4/6: rozszerzyć mapę, potem granice `→ 0x7F` |
| `0x14359`, `0x1436F` | walidatory tablic `0x14B3C/0x14C08` | zależne od danych gry — określić semantykę |
| `0x9E89`/`0x9EA1`, `0x9E07`, `0x9DF6`, `0xA02E`, `0xA039` | pętla kopiująca (liczniki/granice) | już objęte E1/C/D; weryfikacja pod kątem pustych replik |
| `0xE557E`, `0xE6DF9`, `0xE79BB` (+ `0x4E907A`) | parsery listy surowców (licznik `0x42`) | po patchu `0x7F` sprawdzić, że puste ID nie powodują odczytów poza tablicą |
| `0xA83B4`, `0xC1EBE`, `0xA3DD5`, `0xAA4AB` | menu budowy / listy UI | iteracje muszą pomijać puste sloty (brak flagi lub zerowy rekord) |
| `0xBD62F` (bound `0xBD6C1`) | lista UI (Y-offset; właściwy bound to `cmp [ebp-4],0x42` @`0xBD6C1`) | dociągnąć bound do `0x7F`, **nie** patchować samego offsetu `0x42` |
| `0xD89AF`, `0xD8AAE` | rysowanie UI (offset pikselowy) | NIE stride — zostawić; tylko zweryfikować przy większych listach |
| `0x36ADD`, `0x4C231`, `0x5F6DE` | dane per-poziom/tablica wartości | dane gry — celowo NIE patchowane (ograniczenia raczej per-poziom) |

Reguły decyzyjne dla każdego wpisu:
- **granica licznika** — zamień imm porównania/przypisania na `NEW_*_MAX`;
- **treść iterowana** — jeśli pętla dereferencjonuje rekord/string/gfx, dodaj warunek
  „rekord niepusty" (oraz dla UI: „flaga `allow*` ustawiona"), inaczej puste sloty
  będą renderować śmieci lub crashować;
- **pętle czysto kopiujące/zeroing** — wystarczy granica, treść ignorują.

---

## 4. Ryzyka i mitygacje

| Ryzyko | Opis | Mitygacja |
|---|---|---|
| R1. `0x4A80` ≠ tylko actor | część z 246 użyć może dotyczyć innych struktur | weryfikacja kontekstowa (data-flow) przed masowym patchem |
| R2. Pola sąsiadujące (`0x1D4C`, `0x45A8`) | mogą być częścią tablic, nie osobnymi polami | discovery: sprawdzić zapisy/odczyty i stride |
| R3. Surowce B stride `0x38` | możliwy bug silnika; nachodzenie tribes | rozstrzygnąć semantykę; ew. trampolina |
| R4. Błędna klasyfikacja `0x37`/`0x42` | nadpisanie niezwiązanej stałej | generator + ręczny przegląd + testy |
| R4b. Puste sloty po podniesieniu limitu | pętla prezentująca treść (UI/menu) dereferencjonuje zerowy/niezdefiniowany rekord → crash lub śmieci w menu | katalog 3.5 + warunek „rekord niepusty/flaga `allow*`" w iteratorach UI; test z lukami ID (rozdz. 6) |
| R5. Zapis gry (`.sav`) | indeksy muszą się mieścić w bajcie | limit ≤127; test zapis/odczyt |
| R6. UI/menu budowy | listy i bufory | osobny przebieg po `0xA83B4`, `0xC1EBE` i in. |
| R7. Edytory | inna struktura niż gra | osobny projekt (Etap 5) |

---

## 5. Etapy realizacji

**Etap 0 — Discovery (bez zmian w kodzie)**
- Pełna mapa struktury aktora: dla każdego offsetu `0x0..0x4A80` ustalić, czy to tablica,
  jej stride, rozmiar i wszystkie miejsca dostępu.
- Rozstrzygnąć R1–R4 (skrypt + przegląd).
- Zatwierdzić `NEW_HOUSE_MAX`, `NEW_GOOD_MAX`, układ ogona.

**Etap 1 — Generator patchy**
- Rozszerzyć `.ai/scripts/gen_tribe_patches.py` (lub nowy `gen_engine_ext.py`):
  - liczy offsety/rozmiary z kodowania (imm8/imm32/disp32),
  - generuje całą tabelę `Patch[]`,
  - waliduje stare bajty w binarium, wypisuje `off/size/bytes` + raport pokrycia.

**Etap 2 — Rekord plemienia (samodzielnie testowalny)**
- P6a/P6b/P7/P8 (patrz 3.2). Test: nowe ID domu/surowca w logice, bez crasha, bez korupcji sąsiednich plemion.
- **WYKONANE (2026-10-09):** relokacja 4 tablic flag na ogon rekordu + 3 walidatory flag `→ 0x7F`;
  generator `gen_engine_ext.py` emituje **41 patchy REC** (28 size + 2 arr_end + 8 disp + 3 limits),
  razem z Etapem 1: **964 patche** w `etapa_gen/patches_ext.h` (raport `.ai/reports/raport_etap12.txt`);
  zintegrowane z `etapc` (EtapC.cpp → `patches_ext.h`, build.bat + `-I"..\etapa_gen"`), `EtapC.dll` zbudowane.
  Walidatory mapy produkcji `0x14289/0x14292` — celowo NIE podniesione (SPECIAL → Etap 4/6).

**Etap 3 — Struktura aktora**
- P1–P5 (+ code cave dla surowców B).
- Build `EtapC.dll`, sprawdzić load i log `patches applied`.

**Etap 4 — Walidatory/menu**
- P9–P11 + menu budowy (`0xA83B4`, `0xC1EBE`, `0xA3DD5`, `0xAA4AB`…).
- Przegląd iteratorów/walidatorów wg **katalogu 3.5**: granice `→ NEW_*_MAX` +
  pomijanie pustych slotów (rekord zerowy / brak flagi `allow*`).
- Test: nowe budynki widoczne i stawialne, produkcja nowych surowców działa,
  puste ID między zdefiniowanymi nie crashuje menu (rezerwa zostaje wykorzystana później).

**Etap 5 — Edytory (`EtapD`)** — osobny projekt; inny rozkład `.text`, brak `0x1AE08`.

**Etap 6 — Dane** (część niezależna od silnika, można robić równolegle)
- `CN.PLMOD/types/houses.ini`: smolarz, huta, nowe receptury kuźni (stal+węgiel).
- `CN.PLMOD/tribetypes12/tribetypes.ini`: `allowhouse`, `allowgood`,
  `toProduceGoodNeedHouse`, `needforgood`, `trainforgood` itd. dla nowych ID.
- `CN.PLMOD/budynki12/houses/houses.ini`: `[GfxHouse]` dla nowych ID.
- `CN.PLMOD/stringstext/gameobjects/houses.ini` + `Data/text/pol/strings/gameobjects/goods.ini`.
- `Data/logic/goodtypes.*`: definicje węgla i stali.

**Etap 7 — Narzędzie (`modkit.py`)**
- Komenda „dodaj łańcuch": budynek + surowce + receptury + tech-tree + gfx + stringi,
  z auto-przydziałem wolnych ID na podstawie nowych limitów.
- Komenda „edytuj recepturę" (mapowanie nazw surowców ↔ ID).

---

## 6. Plan testów

1. **Statyczny:** generator potwierdza 100% patchy (stare bajty zgodne).
2. **Load:** `EtapC.dll` ładuje się, log bez `FAILED`, liczba patchy zgodna.
3. **Izolacja:** nowy dom/surowiec ID = `OLD_MAX+1`; sprawdzić:
   - brak nadpisania sąsiednich plemion (dump pamięci / porównanie flag),
   - widoczność w menu budowy,
   - postawienie i działanie produkcji,
   - zapis i wczytanie gry.
4. **Rezerwa slotów:** nadać kilka ID z **lukami** (np. zdefiniować 56 i 60, zostawić
   57–59 puste); sprawdzić, że puste sloty nie crashują menu/UI (iteratory je pomijają)
   i że można je dodać później bez zmian w patchach (dokładka danych w Etapie 6).
5. **Skalowanie:** dodać kilka ID naraz (np. +10 domów, +10 surowców), powtórzyć.
6. **Regresja:** istniejące 54 domy i 65 surowców działają jak przedtem.
7. **Edytory:** po Etapie 5.

**Procedura testu uruchomieniowego (ważne):** grę trzeba startować z **katalogu z plikami
danych** (`G:\Games\CnMod 1.2`), nie z `etapc`. Kopia `etapc\CN.PLMOD.exe` jest identyczna
z rootową (ten sam MD5), ale bez `Data\`, `CN.PLMOD\`, `Saves\` stoi w CWD=etapc gra kończy
się czysto z `kod = 3` (to **nie** jest crash — mylące przy logowaniu). Poprawna sekwencja:

```
# ubij pozostałości, przebuduj w etapc, potem:
Start-Process etapc\launcher.exe -ArgumentList `
  '"G:\Games\CnMod 1.2\CN.PLMOD.exe"','"G:\Games\CnMod 1.2\etapc\EtapC.dll"'
```

Launcher ustawia CWD dziecka = katalog exe (= root, wszystkie pliki gry); jego log trafia do
`logs\launcher.log`, log DLL do `logs\etapc.log` (względem CWD). Stabilność: proces CN.PLMOD
żyje >20 s z ~300+ MB RAM (dane załadowane) i log kończy się `patches applied: 492/492 ok`.
Wariant test. 2026-10-09: potwierdzony przy CWD=root.

**Stan rozjazdu F (2026-10-09, po testach użytkownika):** wariant `--f-provenance` (F=85,
łącznie 492 patchy) jest **niespójny dla relokacji tablic aktora** — objawy: puste menu
budowania + mieszkańcy „chodzą" zamiast idle. Przyczyna potwierdzona runtime'owo (dump
`logs\dump_etapc.txt`): pętle zapisujące tablice piszą do **nowych** baz (0x4A80/0x8902…),
a liczne odczyty LEA/dword/word (480 site'ów REVIEW, np. klaster `0x2A48/0x2978` w
0x4D900–0x5A000) zostały odfiltrowane i czytają **stare** bazy = zera na świeżo
zaalokowanej puli. Baza `0x4A80`-stride jest ziarnista: nie da się równolegle używać
nowych i starych offsetów.

**Krążenie robocze (przywrócone 2026-10-09):** `patches_ext_baseline.h` = A+B+H tylko
(344 patchy: 246 stride elem + 64 pula + 41 rekord; **bez** F/C/D/E1) — tablice aktora
zostają w oryginalnych offsetach i gra zachowuje oryginalne zachowanie (menu/animacje),
a rekord plemienia jest już rozszerzony do 0x7F. Dokończenie Etapu 1 = pełna klasyfikacja
480 REVIEW (LEA, dword/word, scale, ELOFF, THISCALL-noctx) zamiast filtra `byte-op`, +
code cave surowców B (0x9E79) + korekta +0x18 (helpery 0x9ABC/0x3299A).

---

## 7. Otwarte pytania — rozstrzygnięte w Etapie 0

1. **`0x1D4C` / `0x45A8`** → `0x1D4C` to **surowce A2** (42×`0x42`, rozszerzane);
   `0x45A8` to pola po surowcach B (zostają na miejscu).
2. **Surowce B stride `0x38`** → potwierdzone, bez alternatywnej ścieżki `0x42`;
   nachodzenie tribes = bug, fixujemy przy rozszerzaniu (stride → `NEW_GOOD_MAX`).
3. **246 użyć `0x4A80`** → zweryfikowane: 241 realnych (208 imul + 33 add), 5 śmieci;
   żadne nie dotyczy obcej struktury. Pula `0x5D200` czytana w 52 miejscach.
4. **Limity** → zalecane `NEW_HOUSE_MAX = NEW_GOOD_MAX = 0x7F` (127); element ~`0xB2B6`.
5. **Zapis gry** → chunkowany `hoix<TAG>CI`+len, bez surowego `0x4A80`; serializacja
   aktora do zlokalizowania (rys. Etap 6 / dalsze discovery).

> Pełne wyniki discovery: `.ai/docs/etap0-discovery-aktor.md`.

---

## 8. Podsumowanie

- Cel (wiele nowych budynków i surowców) jest **osiągalny**, ale wymaga **relokacji tablic**
  i **powiększenia elementu aktora**; nie da się tego zrobić „w miejscu".
- Dominujący koszt mechaniczny: **246** użyć stride'u `0x4A80` + ~150–250 patchy baz,
  stride'ów, rozmiarów i walidatorów. Wszystko **generowane skryptem**.
- Bezpieczeństwo opiera się na tym, że **nie przesuwamy istniejących pól** — przepinamy
  tylko adresy bazowe przenoszonych tablic.
- Nowe limity tworzą **rezerwę slotów** (puste = zera/flagi nieustawione), którą można
  zapełniać stopniowo; warunkiem jest, by iteratory UI pomijały puste wpisy (katalog 3.5,
  ryzyko R4b).
- Największe ryzyko to klasyfikacja `0x37`/`0x42` i semantyka surowców B → **Etap 0 Discovery**
  jest obowiązkowy przed kodowaniem.
