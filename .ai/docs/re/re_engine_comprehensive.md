# RE — Kompleksowa analiza silnika CN.PLMOD.exe (Gra typu Knights & Merchants)

**Cel:** pełne zrozumienie silnika w celu modyfikacji (dodawanie nowych budynków, surowców, zawodów) oraz utrzymania istniejącego modu CN.PLMOD 1.2.

**Źródła analizy:**
- `CN.PLMOD.exe` (root, 1 146 880 B) oraz `CN.PLMOD.exe.orig` (oryginał z 2019)
- Dekompilacje Ghidra 12.1.4: `.ai/re_out/decomp_*.md` (FUN_004c227c, FUN_004e21b7, FUN_0046d53a, FUN_0046e1be, FUN_004a693b, xrefs 0x46897c)
- Dotychczasowa dokumentacja: `.ai/docs/re/re_engine_overview.md`, `re_production_flow.md`, `re_hypothesis_logictype.md`, `re_fix_plan.md`, `re-findings.md`
- Kontekst projektu: `.ai/mod-context.md`, `.ai/docs/jak-dodac-budynek-lub-surowiec.md`
- Pliki danych: `CN.PLMOD\types\houses.ini`, `Data\logic\goodtypes.ini`, `CN.PLMOD\tribetypes12\tribetypes.ini`

---

## 1. Podstawowe fakty o binarium

| Pole | Wartość |
|------|---------|
| Format | PE32 (x86), aplikacja Windows |
| ImageBase | 0x400000 (brak ASLR, RVA = VA − 0x400000) |
| Rozmiar | 1 146 880 B (0x118000) |
| SHA-256 (orig) | 367419b7a797c3db6c64c162f5bb74ad1668252ee32e60dfe8d685e0a4d63f00 |
| Silnik | Typu *Knights & Merchants* (miasto/gospodarka, plemiona, towary, budynki, jednostki, zawody) |
| Język interfejsu | Polski (CP1250, CRLF), pliki .ini / .cif |
| Wczytywanie nowych ID (>54) | Wymaga `etapc\launcher.exe` (runtime overlay Etap C); czyste CN.PLMOD.exe nie wczyta nowych wpisów |

### Sekcja .text i code cave
- `.text`: VA=0x1000, VirtualSize=0xF11CB, RawSize=0xF2000, executable, ImageBase=0x400000
- Code cave GOODS_B: RVA 0xF2300 (w paddingu .text, za VirtualSize)
- Nadpisuje 0x9E76–0x9E80 (11 B): `E9 <rel> + 6×NOP` → skok do cave → powrót `E9` na 0x9E81
- Cave: `mov edx,[ebp-0x10]; add edx,ebx; mov byte [edx+eax+0x742C],1; jmp 0x9E81`

---

## 2. Globalne tablice i struktury danych (VA)

| Adres VA | Nazwa | Stride | Opis |
|----------|-------|--------|------|
| 0x510BC4 | `elem_base` / pula aktora | 0x4A80 (rozszerzona) | Tablica elementów per gracz: `[0x510BC4] + gracz*0x4A80` |
| 0x511200 | `tribe_base` | 0x1AE08 (rozszerzona) | Rekordu plemienia: `[0x511200] + plemię*0x1AE08` |
| 0x5113A0 | `house_types` | 0x624 | Tablica typów budynków (domów) |
| 0x511420 | `good_types` | 0xD0 | Tablica typów towarów (oryginalnie 66, rozszerzona do 127) |
| 0x510BD0 | `buildings` | 0x7E0 | Tablica instancji budynków |
| 0x510BE0 | `tribe_house` | 0x54C | Tablica budynków per plemię; +0x8 = output good ID (kopiowane z global_house+8 przy budowie) |
| 0x568C0C | `building_instances` | 0x8BC | Instancje budynków gracza (pętla produkcji) |
| 0x51171C | singleton (obcy menedżer) | — | Dostęp z klastrów 0x4D938, 0x4DC2B, 0x7E76, 0x484B, 0x1AECD — NIE element aktora |
| 0x569AA0 / 0x569AA4 / 0x569AA8 | kontekst UI / rysowanie | — | Używane w funkcjach UI (FUN_004c227c itp.) |
| 0x569ABC | bufor czcionki/tekstu UI | +0x400 | Używany w FUN_004c227c |
| 0x510BC4 + 0x4A30 | liczniki produkcyjne | — | Używane w FUN_0046d53a: `+ 0x4a30 + (x*0x12a0 + y)*4` |

### Stałe rozmiarów (stare → nowe, po rozszerzeniu ID do 127)
| Tablica | Stary rozmiar | Nowy rozmiar |
|---------|--------------|--------------|
| GOODS_A | 0x1278 / 0x42 | 0x4A80 |
| GOODS_A2 | 0x1D4C / 0x42 | 0x5F56 |
| GOODS_B | 0x3C78 / 0x38 | 0x742C |
| HOUSES_A | 0x2820 / 0x37 | 0x8902 |
| HOUSES_B | 0x3126 / 0x37 | 0x9DD8 |
| STRIDE (ogólny) | 0x42/0x37/0x38 | 0x7F |
| NEW_ELEM_SIZE | — | 0xB2B0 |
| NEW_POOL_SIZE | — | 0xDF5C0 |
| ARR_N | 42 | 42 |
| NEW_REC_SIZE | — | 0x1AF90 |

---

## 3. Struktury rekordów

### 3.1 Rekord typu budynku (house_type) — 0x624 B, baza 0x5113A0 + type*0x624

| Offset | Rozmiar | Pole | Przykład (typ 57, smolarnia) |
|--------|---------|------|------------------------------|
| +0x00 | 4 | category | 3 |
| +0x08 | 4 | output_good | 66 (węgiel) |
| +0x1B..+0x20 | 3 B/wpis | stock entries | 0,0,0 |
| +0x60 | 4 | stock_count | 2 |
| +0x64 | 12×66 B | stocks[0..11] (12 B/wpis) | 02 00 ... |
| +0x37C | 4×66 | stock revmap (good → idx), inicjalizowane -1 | 0xFFFFFFFF |
| +0x484 | 4 | production count (max 0x14=20) | 1 |
| +0x488 | 4×20 | production list (good IDs) | [66] |
| +0x4D8 | 4×66 | production revmap (good → list idx) | 0 |
| +0x5E4 | 4 | unknown | — |
| +0x620 | 4 | zeroed per-record | 0 |

**Kolizje przy good 66:**
- Stock revmap: `+0x37C + 66*4 = +0x484` = production count. Obejście: `logicproduction 66` PRZED `logicstock 66`.
- Production revmap: `+0x4D8 + 66*4 = +0x5E0` (sąsiednie z +0x5E4), prawdopodobnie nieszkodliwe.

### 3.2 Instancja budynku — 0x7E0 B, baza 0x510BD0 + idx*0x7E0 (lub 0x568C0C + idx*0x8BC)

| Offset | Pole | Uwaga |
|--------|------|-------|
| +0x00 | ? | 1 |
| +0x04 | ? | 0x47 |
| +0x0C | ? | 0x41A |
| +0x10 | ? | 0x39 |
| +0x14 | house_type | typ budynku (np. 57) |
| +0x18 | ? | 0x3601 |
| +0x1C | ? | 1 |
| +0x20 | ? | 0 |
| +0x24 | ? | 0x3701 |
| +0x28 | ? | 1 |
| +0x2C | category? | 3 |
| +0x30 | type? | 3 |
| +0x200 | flaga "gotowy/zbudowany" | `pcVar15[2000] != '\0'` w FUN_0046d53a |
| +0x60 | stock_count | stan zapasu budynku |
| +0x64 | stocks | zapasy towarów w budynku |
| +0x644 | 20×4 B | tablica właścicieli (FUN_0043267f szuka wpisu równego owner) |

### 3.3 Rekord plemienia (per plemię, 0x1AE08 B po rozszerzeniu)

| Offset | Pole | Uwaga |
|--------|------|-------|
| +0x6740 | próg plemienia dla gooda | `DAT_00511200 + 0x6740 + (tribe*REC + uVar6)*4` |
| +0x6820 | drugi próg | dodawany gdy local_8 != 0 |
| +0x5D200 | flaga typu gracza | 1 → iVar8=2, 2 → iVar8=5, inaczej 1 (w FUN_004c227c / FUN_0046d53a) |

### 3.4 Jednostka (unit)

| Offset | Pole | Uwaga |
|--------|------|-------|
| +0x14 | tribe | plemię |
| +0x18 | job | zawód (56 = smolarz) |
| +0x1C | selected_good | good wybrany w UI |
| +0x158 | timer produkcji | porównywany z progiem plemienia |
| +0x15C | flaga | ustawiana przez patch 0x4A1C0 (+56 = job) |
| +0x195 | flags[good] | "może produkować good" |
| +0x21C | job_good_status[good] | 0, 0xB, 0xC, 0xD, 0xE |
| +0xA68 | UI state | 5 / 6 (FUN_0046d53a) |
| +0xACC | interaction state | 0/2/4 (FUN_0046d53a) |
| +0xAD0 | ? | ustawiane w interakcji z budynkiem |
| +0xAD4 | selected good w interakcji | porównywane z building+8 / +0x10 |
| +0xB44 | idx do house listy | FUN_0041c61e(DAT_00511728, +0xB44) |
| +0xB48 | tribe idx | `* 0x54C + DAT_00510BE0` |
| +0xB4C | ? | kopiowane do +0xA80 |
| +0xB51 | flaga | wpływa na +0x368 (0x15 vs 1) |
| +0xB34 | building_idx | budynek, do którego przypisana jednostka |

---

## 4. Kluczowe funkcje (Ghidra + REA + analiza statyczna)

### 4.1 FUN_00473461 (VA 0x473461) — TICK JEDNOSTKI / PRODUKCJA [ROOT CAUSE]

Główna funkcja "pracy" jednostki, wywoływana co tick z pętli jednostek (`FUN_004680ea` @0x4681ab).

**Obsługuje TYLKO typy budynków 0x26 (38, szkoła) i 0x27 (39, koszary):**
```
0x473482: SUB EDX, 0x26   ; EDX = building_type - 38
0x473486: JZ 0x4734B6     ; type == 38 → case 38
0x473488: DEC EDX         ; EDX = building_type - 39
0x473489: JNZ 0x473611    ; type != 39 → RETURN (nic nie robi)
```
Dla smalarni (typ 57 = 0x39): `0x39 - 0x26 = 0x21`, `DEC` = 0x20 ≠ 0 → `JNZ → return`.

**Efekt dla smalarni:** brak timera produkcji (+0x158), brak ustawiania `+0x195[66]`, brak wywołania `FUN_0044a0d9`, brak produkcji węgla.

**Przebieg dla typów 38/39 (gdy timer osiąga próg):**
1. Oblicza próg z plemienia (używa starego imm 0x6B82, powinno być 0x8578 — jest patch w RVA 0x734E0)
2. Ustawia `+0x15C + good = 1`, wywołuje `FUN_0045BBAA` (dźwięk)
3. Jeśli `local_8 != 0`: ustawia `+0x195[local_8] = 1`, wywołuje `FUN_0045BB51` (dźwięk)
4. Resetuje timer `+0x158 = 0`
5. Jeśli `job == uVar6`: `FUN_0044A0D9(unit)` + `FUN_0044B2FA(unit)` (ustawia +0x195 i status +0x21C)
6. Inaczej: `FUN_00449F2F(unit, uVar6)` (UI zmiana selected good)
7. `FUN_00449BDA(unit)`
8. Jeśli `FUN_0042DA65(unit, local_8)`: `FUN_0043E8A7(unit, local_8)` (UI wybór gooda do produkcji)

### 4.2 FUN_0044A0D9 (VA 0x44A0D9) — ustawia +0x195 dla goodów joba

Pętla po goodach z job block (+0xD8). Wywoływana TYLKO z FUN_00473461 gdy `job == uVar6`.
- Sprawdza `FUN_0042D9A3` (progi plemienia) LUB `race == 2`
- Dla good == 56 ustawia `+0x1CD = 1`, pomija +0x195
- Dla job == 16 i good == 57: ustawia `+0x195[57] = 1`
- Inaczej: ustawia `+0x195[good] = 1`, plus `GOODS_A2[good] = 1` i `GOODS_B[good] = 1`

### 4.3 FUN_0042DA65 (VA 0x42DA65) — bramka "czy jednostka może produkować good"

`+0x195[good] != 0` AND `FUN_0042DB20(unit, good)` (good na liście job block) AND (`FUN_0042D848` needforgood LUB `FUN_0042D9A3` progi LUB `race == 2`).

### 4.4 FUN_004316F3 (VA 0x4316F3) — bramka budynku dla gooda (revmap)

Używa stock revmap z rekordu domu. Zwraca czy budynek może przyjąć/produkcja gooda.

### 4.5 FUN_00431F37 (VA 0x431F37) — zwraca revmap[good] z rekordu domu

### 4.6 FUN_0043267F (VA 0x43267F) — szuka w building+0x644 wpisu równego owner

Zwraca `(index+100)*0x10 + building` jeśli znajdzie, 0 jeśli nie. Używane w FUN_00473461 (case 38).

### 4.7 FUN_004E21B7 (VA 0x4E21B7) — RENDERER TEKSTU UI [NIE jest dispatcherem jobów!]

Poprzednia dokumentacja błędnie nazywała to "job dispatcherem". To funkcja renderowania tekstu z tagami formatowania:
- Obsługuje `{newline}`, tab (0x09), spację (0x20), enter (0x0A/0x0D)
- `param_7` = tekst źródłowy, `param_5` = kontekst budynku/pola, `FUN_0043967D` pobiera wartość pola
- Wywoływana z FUN_0046D53A i FUN_004C227C do renderowania opisów budynków/towarów

### 4.8 FUN_0046D53A (VA 0x46D53A) — interakcja z budynkiem / panel "rzemieślnik" (potter handler)

Obsługuje kliknięcie w budynek i interakcję (pobieranie towaru, zmiana stanu +0xACC, +0xA68).
- Sprawdza `building+0x200` (czy zbudowane), `building+0x2C == 3` (kategoria)
- Pobiera `tribe_house + 8` (output good ID) — **BUG: dla smalarza +8 nigdy nie ustawiane (pozostaje 0)**
- Stany +0xA68: 5 → wybór gooda, 6 → potwierdzenie pobrania
- Przy stanie 6 i good 66: inkrementuje licznik `DAT_00510BC4 + 0x4A30 + (x*0x12A0 + building+0xC)*4`

### 4.9 FUN_0046E1BE (VA 0x46E1BE) — sprawdzenie czy można interakcjować z budynkiem

Zwraca 1 gdy budynek jest dostępny (w zasięgu, właściciel, flaga +0xB51). Ustawia +0x368 (0x15 lub 1) i +0x36C.

### 4.10 FUN_004A693B (VA 0x4A7297) — renderer panelu informacji budynku (UI)

Renderuje panel z nazwą, kosztem, stanem, zapasami towarów, przychodami. Iteruje po goodach budynku (`+0x60` count, `+0x64` stocks) i rysuje ikony `gfxgood_d_1__s_d__d__d`.

### 4.11 FUN_004C227C (VA 0x4C23D8) — renderer listy budynków/typów UI

Iteruje po budynkach gracza (`DAT_00568C0C`, stride 0x8BC), wyświetla listę z goodami produkcji. Używa `FUN_00432A48` do pobierania goodów z house_type (`+0x484` count, `+0x488` list).

### 4.12 Funkcje parserów plików danych
| Adres | Funkcja | Plik |
|-------|---------|------|
| 0x41531D | FUN_0041531D | houses.ini (typy budynków) |
| 0x413E7B | FUN_00413E7B | tribetypes.ini (plemiona) |
| 0x41592E | FUN_0041592E | goodtypes.ini (towary, alloc 0x35A0 → 0x6730) |
| 0x415403 | FUN_00415403 | logictype handler (walidacja < 0x37 → 0x7F) |
| 0x41575C | FUN_0041575C | logicstock handler (max 66, revmap collision) |
| 0x41581D | FUN_0041581D | logicproduction handler (max 20, revmap collision) |

---

### 4.12 FUN_00494f01 — Główna operacja budynku (VA 0x494F01) [REA]

Wywoływana z renderera mapy `FUN_0049067f` (VA 0x490D10) dla każdego budynku na mapie (typ obiektu 0x02).
To jest **główna funkcja operacji budynku**, nie unit tick.

```c
void FUN_00494f01(uint building_idx, void *param_2, uint *param_3, uint *param_4, int param_5, void *param_6) {
  void *bldg = building_idx * 0x7E0 + DAT_00510BD0;   // instancja budynku
  FUN_004316D0(bldg);                                  // inicjalizacja budynku
  void *pBldgInst = house_type_idx * 0x8BC + DAT_00568C0C;  // player building instance
  int *bldgTypeData = building_idx * 0xD0 + DAT_00568CA8;   // dane typu budynku (stride 0xD0)

  // sprawdza built_flag (+0x200)
  // wywołuje FUN_0049A65E (produkcja/zawartość budynku)
  // wywołuje FUN_0049599B (coś z building)
  // wywołuje FUN_00495E0C WEWNĄTRZ siebie (adres 0x495738 leży w range 0x494F01–0x495921)
}
```

**Kluczowe odkrycie REA:** Nie istnieje osobny "building production tick". Produkcja/zarządzanie zasobami budynku jest zintegrowane z `FUN_00494f01`, wywoływanym z renderera mapy.

### 4.13 FUN_00495e0c — Zarządzanie zapasami/produkcją budynku (VA 0x495E0c) [REA]

Wywoływane **wewnątrz FUN_00494f01**. Zarządza licznikami zapasów w `DAT_00568CA8 + type*0xD0` (dane typu budynku), **NIE** w `building+0x64` (stocks instancji).

```c
void FUN_00495e0c(int building_idx) {
  uint *bldgTypeData = building_idx * 0xD0 + DAT_00568CA8;  // dane typu budynku
  int bldg = building_idx * 0x7E0 + DAT_00510BD0;            // instancja budynku
  int pBldgInst = house_type_idx * 0x8BC + DAT_00568C0C;     // player building instance
  uint uVar5 = *(pBldgInst + 0x1D8 + house_type_idx * 4);    // wartość z player building instance
  uint *puVar1 = (house_type_idx + 0x26) * 0x34 + pBldgInst; // wskaźnik do building instance
  int iVar3 = *(bldg + 0x7C8);                                // wartość z building +0x7C8
  uint uVar2 = *puVar1;

  // Współczynnik produkcji: ((uVar5 - building_idx) * uVar2) / uVar5
  uint uVar4 = ((uVar5 - building_idx) * uVar2) / uVar5;

  uint uVar5_count = *bldgTypeData;  // production/stock count

  if (uVar4 < uVar5_count) {
    // ZUŻYJ surowiec — zmniejsz licznik (iteruje po flagach zapasu +4..+200)
    // czyści flagę, zmniejsza count
  } else if (uVar5_count < uVar4) {
    // TWÓRZ produkt — zwiększ licznik (używa _rand() dla losowości)
    // ustawia flagę, zwiększa count
  }
}
```

**Interpretacja:** Funkcja nie operuje na stocks instancji (`building+0x64`), lecz na danych typu budynku (`DAT_00568CA8`). Zużywa/tworzy towary na podstawie współczynnika obliczonego z wartości z player building instance. Używa `_rand()` dla losowego tworzenia produktów.

### 4.14 FUN_0047e062 — Flagi typu budynku (VA 0x47E062)

Ustawia flagi w tabelach danych typu budynku:
- `param_1 == 0x11`: `*(byte *)(param_3 * 0xD0 + 0xcc + DAT_00568CA8) = value & 1;` — flaga w `DAT_00568CA8 + type * 0xD0 + 0xCC`
- `param_1 == 0x10`: flaga w `DAT_00568CB0`
- `param_1 == 0x0E`: flaga w `DAT_0055529C`

`DAT_00568CA8 + type * 0xD0 + 0xCC` może być flagą "produkcja aktywna" dla typu budynku.

### 4.15 Sprite'y surowców — skąd biorą się grafiki [REA]

#### Tablice sprite'ów (VA)

| Adres VA | Nazwa | Używane przez | Opis |
|----------|-------|---------------|------|
| 0x511698 | `sprite_table_1` | `FUN_0042f710` | Sprite'y towarów/budynków (tabela 1) |
| 0x5116A0 | `sprite_table_2` | `FUN_0042f754` | Sprite'y towarów/budynków (tabela 2) |
| 0x5116A4 | `sprite_table_3` | `FUN_0042f776` | Sprite'y towarów/budynków (tabela 3) |

#### Funkcje dostępu do sprite'ów

```c
// FUN_0042f710 (VA 0x42F710) — sprite table 1
int FUN_0042f710(int idx, uint flag) {
  if (DAT_00511698 == NULL) return 0;
  uint uVar1 = idx * 2;
  if (1 < flag) uVar1 = uVar1 + 1;  // idx*2 + 1 dla drugiej klatki animacji
  return FUN_0042BCAE(DAT_00511698, uVar1);  // tab[index]
}

// FUN_0042f798 (VA 0x42F798) — sprite budynku/towaru
int FUN_0042f798(int building_idx, uint good_idx, uint flag) {
  int bldgInst = FUN_0047FFC0(building_idx);  // building_idx * 0x8BC + 0x3C + DAT_00568C0C
  if ((bldgInst != 0) && (good_idx < *(uint *)(bldgInst + 0x18))) {
    return FUN_0042f776(*(int *)(bldgInst + good_idx * 4), flag);
  }
  return 0;
}
```

**Jak good ID mapuje się na sprite:**
1. `good_id * 2` (lub `good_id * 2 + 1` dla drugiej klatki animacji, gdy flag > 1)
2. Wynik jest indeksem w tablicy `DAT_00511698/6A0/6A4`
3. `FUN_0042BCAE(tab, index)` zwraca wskaźnik na dane sprite'u (obraz z pliku .cif)

**Pliki .cif:** `Data\logic\goodtypes.cif`, `Data\logic\housetypes.cif`, `Data\engine2d\inis\vehicles\jobgraphics.cif` zawierają binarne dane graficzne. Engine ładuje je przy starcie do tablic `DAT_00511698/6A0/6A4`. Miejsce ładowania .cif nie zostało zidentyfikowane w tej sesji (brak stringów "goodtypes.cif" w binarium — ścieżki prawdopodobnie budowane dynamicznie).

### 4.16 Dane typu budynku — `DAT_00568CA8`

Stride: `0xD0` (jak good_types). Używane przez:
- `FUN_00494f01` (building operation)
- `FUN_00495e0c` (resource management)
- `FUN_0047E062` (flaga +0xCC, param_1 == 0x11)
- 0x47E951, 0x48FBEE, 0x48FC16, 0x48FC28, 0x48FC33, 0x48FC8B, 0x48FD06, 0x48FD47, 0x494F46, 0x4CD406

---

## 5. Potok produkcji (produkcja węgla w chałupie węglarskiej)

### Stan obecny (z potwierdzeniami z pamięci)
| Element | Wartość | Status |
|---------|---------|--------|
| Dom typ 57 | output=66, prodlist[0]=66, prodcount=1, stock_count=2 | ✅ |
| `GOODS_A[plemie][66]` | =1 dla plemion 1,2,3,4,7 | ✅ |
| `HOUSES_A[plemie][57]` | =1 | ✅ |
| `jobBlock(56)` | +0xD8=66 (lista goodów), +0x330=66 (jobDefaultGood) | ✅ |
| `needforgood[66]`, `needforjob[56]` | puste (brak wymagań) | ✅ |
| Patch `FUN_0044A0D9` (RVA 0x4A1C0) | naniesiony (`8B 4B 18`) | ✅ |
| `jobEnablesJob 56 56` | dodane w 5 sekcjach plemion | ✅ |
| `+0x195[66]` | utrzymuje się po ręcznym ustawieniu | ✅ |

### Przyczyna braku produkcji (potwierdzona przez REA)

`FUN_00473461` (tick jednostki) **nie obsługuje typu 57** — robi wczesny `return`. Nie ustawia `+0x195[66]`, nie ma timera produkcji.

Dodatkowo, REA wykazało że **nie istnieje osobny "building production tick"**. Produkcja/zarządzanie zasobami budynku jest obsługiwane przez `FUN_00494f01` (główna operacja budynku, VA 0x494F01), wywoływaną z renderera mapy `FUN_0049067f` (VA 0x490D10) dla każdego budynku na mapie. Wewnątrz `FUN_00494f01` wywoływane jest `FUN_00495e0c` (VA 0x495E0c), które zarządza licznikami zapasów w `DAT_00568CA8 + type*0xD0` (dane typu budynku), **NIE** w `building+0x64` (stocks instancji).

**Problem dla smolarza (job 56) w chałupie węglarskiej (typ 57):**
1. Smolarz dostarcza drewno do budynku → drewno trafia do `building+0x64` (stocks instancji)
2. Ale nie ma kodu który konwertuje drewno (`building+0x64`) na węgiel (`building+0x64`) dla typu 57
3. `FUN_00495e0c` operuje na `DAT_00568CA8` (dane typu), nie na stocks instancji
4. `FUN_00473461` nie obsługuje typu 57 → nie ustawia `+0x195[66]`, nie ma timera, nie wywołuje `FUN_0044A0D9`

**Węgiel nie pojawia się w UI, bo:**
1. Nie jest tworzone w kodzie produkcji (brak konwersji drewno→węgiel dla typu 57)
2. Nawet jeśli by zostało utworzone, pętla towarów UI (`0x415E8E`) crashuje jeśli bound extended (0x35A0 → 0x6730)

### Hipoteza naprawy (opcja A, zalecana)
Zmienić `logictype` w `CN.PLMOD\types\houses.ini`:
- Smolarnia (linia ~933): `logictype 57` → `logictype 38`
- Szkoła (linia ~691): `logictype 38` → `logictype 57` (szkoła nie produkuje towarów, więc brak obsługi typu 57 jest obojętny)

Output good (66) pochodzi z `logicproduction 66`, nie z logictype, więc smolarnia nadal produkowałaby węgiel z logiką typu 38.

### Alternatywy
- Opcja B: code cave w `FUN_00473461` dla typu 57 (brak miejsca w .text, max 4 zero-bajty z rzędu — trzeba dodać sekcję do PE lub rozszerzyć .text)
- Opcja C: zmiana `JNZ` (0x473489) na `JZ` — **odrzucane** (psuje koszary typ 39)

---

## 6. System patchów (patches_ext.h)

Format: `{ RVA, offset, size, { new_bytes[8] }, "description" }`. Aplikuje w `base + RVA + offset`.
- **580 patchów**, 0 nakładek
- Etap 1+2 = 535 patchów (f_prov 492 + R 30 + ELOFF 8 + CAVE 5)

### Kluczowe patchy dla good 66 / job 56 / house 57
| RVA | Offset | Size | Nowe bajty | Opis |
|-----|--------|------|------------|------|
| 0x15833 | 0 | 1 | 7F | logicproduction good guard 0x42→0x7F |
| 0x159F1 | 0 | 1 | 7F | goodtypes validator 0x42→0x7F |
| 0x14292 | 2 | 1 | 7F | toProduceGoodNeedHouse good guard 0x42→0x7F |
| 0x56168 | 0 | 4 | 30 67 00 00 | production calc loop 0x35A0→0x6730 |
| 0x35CD7 | 0 | 4 | 30 67 00 00 | active goods loop 0x35A0→0x6730 |
| 0xB02C | 0 | 4 | 30 67 00 00 | name search loop 0x35A0→0x6730 |
| 0x15843 | 0 | 6 | 89 86 08 00 00 00 | logicproduction: write good to global_house+8 |
| 0x5C6FC | 0 | 1 | B0 01 | force depot check pass (actor flag +0xB84 bit 8) |
| 0x6BD36 | 2 | 4 | 85 00 00 00 | job 56 dispatcher → potter handler |

### Pętle iterujące po towarach (bound 0x35A0 = 66 towarów)
| VA | RVA | Kontekst | Status |
|----|-----|----------|--------|
| 0x40B00C | 0xB00C | name search (strcmp) | SAFE do patchowania |
| 0x415E8A | 0x15E8A | goods init/UI | CRASH jeśli bound extended (wywołuje 0x47FEF0) |
| 0x435CD7 | 0x35CD7 | active goods | PATCHED (0x35A0→0x6730) |
| 0x456168 | 0x56168 | production calc | PATCHED (0x35A0→0x6730) |
| 0x45FAFA | 0x5FAFA | build local arrays | UNSAFE (overflow stosu: sub esp,0x2A4, 66+102 sloty) |

---

## 7. Pliki danych i formaty

### goodtypes.ini (Data\logic\goodtypes.ini)
- Nagłówek: `<CULTURES_CIF_BEGIN><03FD><NNNNNNNN>` (N = liczba linii body, hex, 8 cyfr)
- Body: bloki `[goodtype]`, `%01%`→`[`, `%02%` usuwane
- Stopka: `<CULTURES_CIF_END>`
- Kodowanie: CP1250, CRLF
- Good 66 = węgiel: `name "coal"`, `type 66`, `landscapetype 66`, `isProducedInHouseFlag 1`, `productionInputGoods 5` (drewno), `atomicForProduction 52` (mirrors brick type 24)

### houses.ini (CN.PLMOD\types\houses.ini)
- Bloki `[logichousetype]`: `logictype N`, `logicmaintype`, `logicworker`, `logicstock`, `logicproduction`, `debugname`, `debugcolor`
- Typ 38 = szkoła (linia ~691), typ 57 = chałupa węglarska / work charcoal burner (linia ~932-933)

### tribetypes.ini (CN.PLMOD\tribetypes12\tribetypes.ini)
Na plemię (5 plemion):
- `allowgood 66`, `allowhouse 57`
- `jobDefaultGood 56 66`, `jobEnablesGood 56 66`, `jobEnablesJob 56 56`
- `toProduceGoodNeedHouse 66 57`

### 7.5. Funkcje UI i wyboru gooda (REA)

#### FUN_0043E8A7 — UI: wybierz good do produkcji (VA 0x43E8A7)

Wywoływana z FUN_00473461 gdy jednostka może produkować good. Ustawia status +0x21C dla goodów job block i wybiera good do produkcji.

```c
void FUN_0043E8A7(unit *this, int good) {
  if (FUN_0042DB20(this, good)) {
    int job_block = job * 0x400 + 0x6928 + DAT_00511200 + tribe * 0x1AE08;
    if (*(int *)(job_block + 4) != 0) {
      int *good_list = job_block + 0xD8;
      do {
        int g = *good_list;
        int status = FUN_0044B5D9(this, g);
        if (status < 0xC && status > 0)
          FUN_0044B5E7(this, g, 0);  // resetuj status
        good_list++;
      } while (++local_c < *(uint *)(job_block + 4));
    }
    FUN_0044B5E7(this, good, 0x0B);  // ustaw wybrany good na 0xB
    *(int *)(this + 0x38C) = 0;
    *(int *)(this + 0x218) = good;
    *(int *)(this + 0x1C) = good;
  }
}
```

#### FUN_0044B5D9 — Getter statusu gooda +0x21C (VA 0x44B5D9)

```c
uint FUN_0044B5D9(unit *this, int good) {
  return *(uint *)(this + good * 4 + 0x21C);
}
```

#### FUN_0044B5E7 — Setter statusu gooda +0x21C (VA 0x44B5E7)

Ustawia status gooda: 0, 0xB, 0xC, 0xD, 0xE.

#### FUN_0044B2FA — Set production status for job goods (VA 0x44B2FA)

Ustawia +0x21C dla wszystkich goodów z job block:
- 0x0C jeśli brak flagi +0x195
- 0x0D jeśli good nie na liście job block
- 0x0E jeśli FUN_0042DA65 true
- 0x0B dla jobDefaultGood (+0x330) jeśli można produkować

#### FUN_00449F2F — UI: zmień selected good (VA 0x449F2F)

Wywoływana z FUN_00473461 gdy `job != uVar6`. Zmienia job jednostki (+0x18), wywołuje FUN_0044A0D9 i FUN_0044B226 na końcu.

#### FUN_0044B226 — Production menu status (VA 0x44B226)

Ustawia +0x21C dla goodów 1-65:
- 0x0C jeśli `+0x195[good] == 0`
- 0x0D jeśli good nie na job block
- 0x0E jeśli `FUN_0042DA65` true

#### Job Assignment Chain (NOWE ODKRYCIE)

| Adres | Nazwa | Opis |
|-------|-------|------|
| **0x43242C** | **FUN_0043242C** | **Przypisuje job z house_type do unit+0x18** ★ |
| 0x43230A | FUN_0043230A | Worker dispatcher (param_2=2 → FUN_0043242C) |
| 0x431FF5 | FUN_00431FF5 | Building unit logic → woła dispatcher z param_2=2 |
| 0x432003 | FUN_00432003 | Rejestruje workera w building+0x644 |
| 0x4C8F14 | FUN_004C8F14 | Worker logic dispatcher (param_2=5 → FUN_0043242C) |
| 0x4C8919 | FUN_004C8919 | Dispatcher (case 5 → FUN_004C8F14) |
| 0x4B64A6 | FUN_004B64A6 | Pathfinding / unit init → triggeruje łańcuch |

**Struktura workers w house_type (offset +4):**
```
house_type+3  = worker_count
house_type+4  = job_id_0
house_type+8  = count_0
house_type+12 = job_id_1
house_type+16 = count_1
...
```

#### Helper functions (REA)

| Adres | Nazwa | Opis |
|-------|-------|------|
| 0x42C6F0 | Czy jednostka ma budynek? | `*(unit+0xB34) != -1` |
| 0x42C597 | Flaga gracza | `DAT_00510BC4 + player*0x4A80 + 4` |
| 0x42C5B3 | Sprawdź job | job==1/3/5 → 1; job==47 → tribe==3 |
| 0x42C676 | Czy job==15? | `*(unit+0x18) == 0x0F` |
| 0x42C6BC | Czy job 30-41? | `0x1E < job < 0x2A` |
| 0x42C6CF | Czy job 42-47? | `0x29 < job < 0x30` |
| 0x42C8A8 | Czy budynek typu 4 z owner? | `FUN_004316E0(building)==4 && FUN_004322DA(building, owner)` |
| 0x4316E0 | Zwraca house_type z building | `*(building+0x14)` |
| 0x4322DA | Sprawdź owner i flagę | `house_type==4 && FUN_0043267F && bit3` |
| 0x43E09A | Wybierz good do produkcji | Złożona, wywołuje FUN_0043E8A7 |
| 0x4319D7 | Pobierz ilość towaru w budynku | Używa revmap, +0x118 (qty), +0x430 (counter) |
| 0x434142 | Czy budynek ma pracownika? | `*(building+0x7A8+worker*4) != 0` |

---

## 7.6. Batch 4 — dodatkowe funkcje (REA)

### FUN_0043234D — sprawdza czy wpis istnieje w tablicy 20×4B
```c
bool exists = false;
for (int i = 0; i < 20; i++) {
    if (table[i] == value) { exists = true; break; }
}
// jeśli nie istnieje, szuka pustego slotu i dopisuje
```

### FUN_0043256B — sprawdza typ wpisu w tablicy budynku
```c
int type = *(int *)(building + i * 0x40 + offset);
// używane do walidacji typu wpisu (3 = koszary, 2 = dom, 4 = budynek)
```

### FUN_00432516 — sprawdza capacity budynku
```c
int capacity = *(int *)(building + 0x218);  // building+0x218
// porównuje z aktualną liczbą wpisów
```

### FUN_004326EC — pobiera wartość z tablicy budynku
```c
return *(int *)(building + i * 0x40 + offset);
// offset +0x24, +0x26, +0x28, +0x2C
```

### FUN_004319D7 — pobiera ilość towaru w budynku
```c
int qty = *(int *)(building + i * 0x40 + offset);
// offset +0x24, +0x26, +0x28, +0x2C
```

### FUN_0043E09A — wybiera good do produkcji
```c
// sprawdza +0x195[good] != 0, job block, budynek
// jeśli OK: ustawia +0x21C[good] = 0x0E, +0x1C = good
// dodatkowo obsługuje job==7 (budowniczy)
```

### FUN_0042D88D — sprawdza dane jednostki
```c
// używa +0xB34 (building_idx), +0x10 (player?)
// wywołuje FUN_004316F3 (bramka budynku)
```

### FUN_0042C6E3 — pomocnicza funkcja walidacji
```c
// sprawdza +0xB48 * 0x54C + 0x510BE0 (tribe house)
// wywołuje FUN_0044B9AB, FUN_0044B660
```

### FUN_0043230A — sprawdza istnienie wpisu
```c
// iteruje po tablicy 20 wpisów × 4B
// zwraca true jeśli value istnieje, false jeśli nie
// jeśli nie istnieje, szuka pustego slotu i dopisuje
```

---

## 8. Niezbywalne problemy i otwarte wątki RE

1. **Storage UI nie pokazuje węgla** — pętla towarów w 0x415E8E crashuje jeśli bound zostanie rozszerzony. Trzeba znaleźć bezpieczną ścieżkę iteracji.
2. **Brak kodu "building production tick"** — produkcja jest wyłącznie na ticku jednostki (FUN_00473461), który pomija typ 57.
3. **Production rev-map collision** — good 66 zapisuje do +0x5E0, trzeba zweryfikować czy nie ma runtime reads.
4. **toProduceGoodNeedHouse map** — tylko 66 wpisów, nie przeniesiona. Może cicho ignorować good 66.
5. **0x415E8E** — czy wywoływane tylko przy starcie czy też w runtime?
6. **Hardcoded good 24 w potter handlerze** — trzeba zweryfikować.
7. **Kopiowanie tribe_house+8 przy budowie** — gdzie jest kod, który kopiuje global_house+8 do tribe_house+8?

---

## 9. Następne kroki RE

### Krytyczne (naprawa produkcji węgla):

1. **Zdekomponować FUN_00494996** (wywoływane z FUN_0049599B w FUN_00494f01) — może być kluczowe dla produkcji w budynku
2. **Zdekomponować FUN_0044B5E7** (setter statusu gooda +0x21C)
3. **Zdekomponować FUN_0045C66E, FUN_0042C909, FUN_0042C73B, FUN_0042C783, FUN_0042878E** (używane w FUN_0043E09A)
4. **Dodać kod konwersji drewno→węgiel dla typu 57** — albo przez zmianę `logictype` na 38 (opcja A), albo code cave w `FUN_00494f01`/`FUN_00495e0c`
5. **Zweryfikować patch na imm 0x6B82** w FUN_00473461, FUN_0042D9A3, FUN_0042D97D (stary rozmiar rekordu plemienia, powinno być 0x8578)

### Wysoki priorytet:

6. **Znaleźć gdzie ładuje się goodtypes.cif do DAT_00511698/6A0/6A4** (tablice sprite'ów)
7. **Sprawdzić czy FUN_00495e0c modyfikuje building+0x64 czy tylko DAT_00568CA8**
8. **Naprawić Storage UI** — pętla 0x415E8E crashuje dla bound extended
9. **Przetestować zmianę logictype (opcja A) w houses.ini** (smolarnia 57→38, szkoła 38→57)

### Średni priorytet:

10. **Dodać filtr niezdefiniowanych budynków (Etap 4)** — zatrzymać crash przy stawianiu nowych budynków
11. **Zdekomponować kandydatów na "building tick":** FUN_0047FFC0, FUN_0048EA9F, FUN_00494F01, FUN_0049599B, FUN_00495E0C (refs do DAT_00568C0C)
12. **Uzupełnić dane nowych ID smolarz/huta + węgiel/stal (Etap 6)**
13. **Zbadać przyczynę braku animacji idle mieszkańców** (regresja po ELOFF+cave)

### Pliki do modyfikacji:

- `CN.PLMOD\types\houses.ini` — zmiana logictype smalarni 57→38, szkoły 38→57
- `CN.PLMOD\tribetypes12\tribetypes.ini` — już zawiera wszystkie wymagane wpisy dla good 66 / job 56 / house 57
- `Data\logic\goodtypes.ini` — good 66 = węgiel już zdefiniowany
- `patches_ext.h` — patchy walidatorów i boundów już naniesione

