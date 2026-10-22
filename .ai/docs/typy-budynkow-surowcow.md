# Analiza: tabele typów (budynki / surowce) — co da się dodać, a czego nie

**Data:** 2026-10-07
**Zakres:** statyczna analiza `CN.PLMOD.exe` (pefile + capstone) + pliki danych moda/oryginału.
Adresy to VA `CN.PLMOD.exe` (ImageBase `0x400000`).

**Skrypty (`.ai\scripts\`, uruchamiane w katalogu gry):**
- `ht_find.py` — xref-y do stringów ścieżek (`houses.ini`, `goodtypes.ini`, …) + disasembling wokół,
- `disx.py <addr> <end> [align]` — disasembler zakresu (align = cofnięcie do prologu funkcji),
- `ht2.py` — resolve wskaźników stringów + wystąpienia stałych `0x624` / `0x35A0` / `0x151BC`,
- `ht3.py` — census instrukcji z natychmiastami `0x37` (55) i `0x42` (66),
- `disp.py` — wszystkie odwołania do pól tablic typów w rekordzie plemienia,
- `tribedisp.py` — liczba displacementów w zakresie `[0x5193, 0x1AE08)` (= zakres przesunięcia),
- `houses_sections.py` — spis 55 sekcji `houses.ini` (klucze, robotnicy, magazyny),
- `gfxhouses.py` — spis 156 `[GfxHouse]` i mapowanie na typy logiczne,
- `ciflist.py <plik> <klucz> <sekcja>` — spis pozycji z dekodowanego CIF-a.

**Dekody CIF-ów (`.ai\decoded\`)** — `mapper tools\cif2txt.exe C <in.cif> <out.txt>`:
`goodtypes.txt` (65 surowców), `housetypes.txt` (54 oryginalne budynki), `jobtypes.txt` (55),
`armortypes.txt` (4).

---

## 1. Gdzie co leży (pipeline danych)

| Co | Plik ładowany przez grę | Uwagi |
|---|---|---|
| Logika budynków | `cn.plmod\types\houses.ini` (string `0x50055C`, loader `0x41531D`) | 55 sekcji `[logichousetype]`, indeks = wartość klucza `logictype` |
| Oryginał logiki budynków | `Data\logic\housetypes.cif` → **54 sekcje** | ścieżka w exe została spatchowana na `cn.plmod\types\houses.ini` |
| Grafika/obiekty budynków | `cn.plmod\budynki12\houses\houses.ini` (loader `0x48DBA4`) | **156 sekcji `[GfxHouse]`** – osobna tabela, bez limitu 55 |
| Nazwy budynków (PL) | `cn.plmod\stringstext\gameobjects\houses.ini` | `stringn 0..55` |
| Surowce | najpierw `data\logic\goodtypes.ini`, **gdy brak → `goodtypes.cif`** (loader `0x41592E`, opener `0x425A7B` ma domyślny rozszerzenie `.cif`) | obecnie na dysku jest tylko `.cif` → 65 pozycji |
| Teksty surowców (PL) | `Data\text\pol\strings\gameobjects\goods.ini` | `stringn 0..65` |
| Bronie | `cn.plmod\types\weapons.ini` | 19 użytych indeksów |
| Pojazdy | `Data\logic\vehicletypes.ini` (**tekst, obok `.cif`**) – dowód, że tekstowe `.ini` ma pierwszeństwo | 6/6 |
| Plemiona | `cn.plmod\tribetypes12\tribetypes.ini` | 41/42 |
| Konwerter CIF | `mapper tools\cif2txt.exe C\|T` (+ Java `c2mConverter`) | format: `<CULTURES_CIF_BEGIN><03FD>…`, sekcje `%01%`, klucze `%02%` |

**Wniosek 1:** wszystkie tabele typów da się edytować jako zwykły tekst `.ini` — gra najpierw
otwiera wskazaną ścieżkę, a dopiero gdy jej nie ma, podstawia rozszerzenie `.cif`
(`0x425A7B`: `cmp [ebp+0xc],0 / je → mov …, 0x4FF094 ('.cif')`). Wyjątkowo ścieżka
`data\logic\housetypes.ini` została w binarce podmieniona na `cn.plmod\types\houses.ini`.

---

## 2. Twarde limity w exe

### 2.1 Budynki (`HOUSE_TYPE_MAXIMUM = 55`, rekord `0x624` = 1572 B)

| Co | Adres | Kod |
|---|---|---|
| Alokacja całej tabeli | `0x41534E` | `mov esi, 0x151BC` → `malloc` = **55 × 0x624** |
| Pętla konstruktorów | `0x415368` | `mov [ebp-4], 0x37` (=55), `add ebx, 0x624` |
| **Walidacja indeksu z INI** | `0x415421–0x41542F` | `cmp eax, ebx / jbe skip` (odrzuca ≤0), `cmp eax, 0x37 / jae skip` (odrzuca ≥55) → **dopuszczalne 1..54** |
| Indeksowanie rekordu | `0x415435` | `imul esi, esi, 0x624` + `add esi, [0x5113A0]` |
| Iteratory po tabeli | `0x4158D5`, `0x415923` | `cmp …, 0x37 / jb` |
| Lookup „po nazwie" | `0x40AFC0` | `add esi, 0x624 / cmp esi, 0x151BC / jl` |
| Pozostałe pętle po rozmiarze | `0x44A411`, `0x44AC9C`, `0x456326`, `0x45635D` | `cmp …, 0x151BC` |
| **Flaga „plemie może zbudować"** | zapis `0x4142FD`, odczyt `0x409E89` (bound `0x409E82`) | `byte [reg + idx + 0x515C]`, tablica **55 B** w rekordzie plemienia |

### 2.2 Surowce (`GOOD_TYPE_MAXIMUM = 66`, rekord `0xD0` = 208 B)

| Co | Adres | Kod |
|---|---|---|
| Alokacja | `0x41595E` | `mov esi, 0x35A0` = **66 × 0xD0** |
| **Walidacja indeksu** | `0x4159E7–0x4159F2` | `jle skip` (≤0), `cmp eax, 0x42 / jge skip` (≥66) → **dopuszczalne 1..65** |
| Lookup | `0x40B02A` | `add esi, 0xD0 / cmp esi, 0x35A0 / jl` |
| Inne pętle po rozmiarze | `0x416317`, `0x435CD7`, `0x456168`, `0x45FAFA` | `cmp …, 0x35A0` |
| Flagi plemion (tablice 66 B) | zapis `0x414292`(→`+0x50D8`), `0x414315`(→`+0x511A`), odczyt `0x409E4D`, `0x409E6C` | |

### 2.3 Rekord plemienia – jedyne „ciasne" miejsce

Rekord = `0x1AE08` B × 42 = `0x468D50` (allokacja `0x413EAB`). Wewnątrz **ściśle opakowane**
tablice flag (bez wolnych bajtów):

```
+0x50A0: 56 B  +0x50D8: 66 B  +0x511A: 66 B  +0x515C: 55 B (budynek!)  +0x5193: 8 B (pojazdy)
0x50A0+56=0x50D8 ✓  0x50D8+66=0x511A ✓  0x511A+66=0x515C ✓  0x515C+55=0x5193 ✓
```

Powiększenie tablicy budynków o 1 B przesuwa **wszystkie** pola rekordu plemienia powyżej
`0x5193`. Skan całego `.text`: w zakresie `[0x5193, 0x1AE08)` znajduje się jedynie
**41 odwołań do pamięci / 36 różnych displacementów** → przesunięcie o N bajtów to patch
rzędu **~40 instrukcji**, nie tysięcy. To jest kluczowy powód, dla którego „przedłużenie
tablicy" w ogóle wchodzi w grę.

---

## 3. Dowód, że limit jest realny i że dotychczasowy modding = podmiana slotów

1. **`houses.ini` ma 55 sekcji (`logictype 1..55`), ale exe przyjmuje tylko 1..54.**
   Sekcja 55 (`debugname "work murek"`) jest **cicho odrzucana** przez `cmp eax,0x37 / jae`
   przy `0x41542C` → martwy wpis w obecnym modzie.
2. Oryginalny `housetypes.cif` ma **54** sekcje = dokładnie tyle, ile dopuszcza walidator.
3. `[GfxHouse]` (156 sztuk) odwołuje się wyłącznie do typów **1..54** – nigdzie 0 ani 55.
4. Indeks `0` jest zarezerwowany jako „brak" (`goodtype 0`, `logicstock … 0`, komórki mapy).
5. Klasyczny „nowy budynek" w CN.PLMOD to **przejęcie wolnego/star slotu**: oryginalny
   `work pottery 02` (typ 22) jest dziś „Mur h / Mur V" – wszystkie `[GfxHouse]` typu 22
   to mury, żadna garncarnia. Czyli: slotów brak → modderzy przemianowali istniejący.
6. Inwentarz wolnych indeksów (ogółem):

| Tabela | Limit | Zajęte | Wolne |
|---|---|---|---|
| budynki | 55 | 54 (+0=rezerwa „brak") | **0** |
| surowce | 66 | 65 (+0) | **0** |
| bronie | 22 | 19 (brak 13, 14) | **13, 14 – jedyne wolne w grze** |
| pancerze | 5 | 4 (+0) | 0 |
| pojazdy | 7 | 6 (+0) | 0 |
| plemiona | 42 | 41 (+0) | 0 |
| zawody | 56 | 55 (+0) | 0 |

---

## 4. Konsekwencje dla „nowego typu"

**Nowy typ = nie tylko wpis w INI.** Potrzebne jest spójne dopełnienie w 6 miejscach:

1. `types\houses.ini` / `goodtypes.ini` – definicja logiki (indeks!),
2. `stringstext\gameobjects\houses.ini` / `Data\text\pol\strings\gameobjects\goods.ini` – nazwy PL (pojedyncza i mnoga),
3. `budynki12\houses\houses.ini` – `[GfxHouse]` (grafika, obszar, robotnicy, koszt budowy) – **dodawanie wolne, brak limitu**,
4. `tribetypes.ini` – flagi „które plemię może zbudować / używać" (tablice 55/66 B w rekordzie plemienia),
5. GUI: ikony surowców w HUD / przycisk budowania (do zbadania – osobny rozdział pracy),
6. **exe**: 15–20 stałych (alokacje, pętle, walidacje) dla каждойj tabeli + ~40 displacementów przy przesunięciu tablicy w rekordzie plemienia + **osobno te same tabele w edytorach** (`Edytor podstawowy.exe`, `Remik's Editor.exe`).

Niezbędne jeszcze do ustalenia (pytania otwarte):
- format zapisu gry i mapy – czy typ zapisywany jest jako bajt (wtedy pole do 255 wolne),
- skąd bierze się lista przycisków budowania w GUI,
- czy edytory mają identyczne `.text` jak gra (dla dwóch edytorów wiadomo, że są identyczne między sobą).

---

## 5. Werdykt

- **Dziś, bez patcha:** można *podmieniać/okupować* sloty (dowód: mury w slocie 22) i dodawać
  nowe **warianty graficzne** budynków (`[GfxHouse]` bez limitu). Wolne sloty istnieją
  wyłącznie w tabeli broni (13, 14).
- **Z patchem exe:** dodanie nowego typu budynku/surowca jest **realne**, bo koszt jest
  policzalny i mały: ~15–20 stałych na tabelę + ~40 displacementów w rekordzie plemienia +
  tabele w edytorach. Ryzyko: zapisy gry/mapy i GUI (do sprawdzenia przed implementacją).
- Osobnym, szybkim efektem jest już sama **walidarka** – potrafiła wykryć fakt, że obecny
  `logictype 55` nigdy nie działa.
