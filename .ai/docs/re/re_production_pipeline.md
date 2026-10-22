# RE — Potok produkcji w CN.PLMOD.exe (węgiel w chałupie węglarskiej)

Uzupełnienie do `re_engine_comprehensive.md` i `re_production_flow.md`.

---

## 1. Stan danych (potwierdzony z pamięci)

Plik `CN.PLMOD\types\houses.ini`, typ 57 (work charcoal burner / chałupa węglarska, linia ~932-933):
```
[logichousetype]
debugname "work charcoal burner"
logictype 57          <-- NIE OBSŁUGIWANY przez FUN_00473461 (tylko 38 i 39)
logicmaintype 3
logicworker 56 1      <-- job 56 = smolarz
logicstock 5 1 1      <-- input: drewno (good 5), qty 1, flag 1
logicproduction 66    <-- output: węgiel (good 66) — MUSIĆ BYĆ PRZED logicstock 66 (kolizja revmap)
logicstock 66 15 0    <-- output stock: węgiel, cap 15, flag 0
debugcolor 0 0 100
```

Plik `Data\logic\goodtypes.ini`, good 66 (linia ~586-593):
```
[goodtype]
name "coal"
type 66
landscapetype 66
isInputGoodFlag 0
isProducedInHouseFlag 1
isProducedOnMapFlag 0
productionInputGoods 5     <-- drewno
atomicForProduction 52     <-- mirrors brick (type 24)
```

Plik `CN.PLMOD\tribetypes12\tribetypes.ini` (na plemię, 5 plemion):
```
allowgood 66
allowhouse 57
jobDefaultGood 56 66
jobEnablesGood 56 66
jobEnablesJob 56 56
toProduceGoodNeedHouse 66 57
```

**Potwierdzenia z pamięci:**
- Dom typ 57: `output=66`, `prodlist[0]=66`, `prodcount=1`, `stock_count=2` ✅
- `GOODS_A[plemie][66] = 1` dla plemion 1,2,3,4,7 ✅
- `HOUSES_A[plemie][57] = 1` ✅
- `jobBlock(56)`: `+0xD8=66` (lista goodów), `+0x330=66` (jobDefaultGood) ✅
- `needforgood[66]`, `needforjob[56]` = puste ✅

---

## 2. Przyczyna braku produkcji (ROOT CAUSE)

Silnik nie ma osobnego kodu "building production tick". Produkcja jest napędzana przez **tick jednostki** `FUN_00473461` (VA 0x473461), który obsługuje **TYLKO typy budynków 38 (szkoła) i 39 (koszary)**:

```
0x473482: SUB EDX, 0x26   ; building_type - 38
0x473486: JZ 0x4734B6     ; type == 38 → case 38 (obsługa budynku)
0x473488: DEC EDX         ; building_type - 39
0x473489: JNZ 0x473611    ; type != 39 → RETURN
```

Dla smalarni (typ 57 = 0x39): `0x39 - 0x26 = 0x21`, `DEC` → 0x20 ≠ 0 → `JNZ → return`.

**Efekt:** brak timera produkcji (+0x158), brak ustawiania `+0x195[66]`, brak wywołania `FUN_0044A0D9`, brak możliwości pobrania węgla w UI. Ręczne ustawienie `+0x195[66]=1` nie pomaga, bo nie ma kodu który zużywa drewno i tworzy węgiel.

---

## 3. Hipoteza naprawy — Opcja A (zalecana)

Zmienić `logictype` w `CN.PLMOD\types\houses.ini`:
- Smolarnia (linia ~933): `logictype 57` → `logictype 38`
- Szkoła (linia ~691): `logictype 38` → `logictype 57`

**Uzasadnienie:** Output good (66) pochodzi z `logicproduction 66`, **nie** z logictype. Typ 38 (`logicmaintype 3`, jak smolarnia) jest obsługiwany przez `FUN_00473461` (case 38), który ustawia `+0x195[good]` i uruchamia łańcuch produkcji. Szkoła (typ 38) nie produkuje towarów, więc zmiana jej na 57 (nieobsługiwany) jest obojętna dla produkcji.

**Ryzyko:** inne miejsca w kodzie mogą sprawdzać `logictype == 57` lub `== 38` (UI, budowanie, AI). Znalazłeś miejsca:
- 0x441821 (FUN_00441800): `cmp eax,0x39` — goodi 65,58,57 (zwierzęta?)
- 0x44A4D3 (FUN_0044A0D9): `cmp eax,0x39` — good==57 traktowany specjalnie
- 0x468A64 (FUN_0046897C): `cmp eax,0x39` — nieznane

---

## 4. Hipoteza naprawy — Opcja B (code cave)

Jeśli opcja A nie zadziała, dodać code cave w `FUN_00473461` dla typu 57:
- Ustawić `+0x195[66] = 1`
- Wywołać `FUN_0044A0D9(unit)` + `FUN_0044B2FA(unit)`
- Wymaga dodania nowej sekcji do PE lub rozszerzenia .text (brak miejsca: max 4 zero-bajty z rzędu)

---

## 5. Niezbywalne problemy w potoku produkcji

| # | Problem | Lokalizacja | Status |
|---|---------|-------------|--------|
| 1 | Storage UI nie pokazuje węgla | pętla towarów 0x415E8E crashuje jeśli bound extended | Otwarte |
| 2 | Brak "building production tick" | brak funkcji iterującej po budynkach z logicproduction | Otwarte |
| 3 | Production rev-map collision | good 66 zapisuje do +0x5E0 (sąsiednie z +0x5E4) | Do zweryfikowania |
| 4 | toProduceGoodNeedHouse map | tylko 66 wpisów, nie przeniesiona | Może cicho ignorować good 66 |
| 5 | 0x415E8E — startup vs runtime | nie wiadomo czy wywoływane tylko przy starcie | Do zbadania |
| 6 | Hardcoded good 24 w potter handlerze | do zweryfikowania | Do zbadania |
| 7 | Kopiowanie tribe_house+8 przy budowie | kod kopiujący global_house+8 → tribe_house+8 nie znaleziony | Do znalezienia |

---

## 6. Kandydaci do kolejnej analizy (building tick)

Funkcje z refs do `DAT_00568C0C` (instancje budynków gracza, stride 0x8BC):
- FUN_0047FFC0 (0x47FFC6)
- FUN_0048EA9F (0x48EABD)
- FUN_00494F01 (0x494F31)
- FUN_0049599B (0x4959BD)
- FUN_00495A6D (0x495A95)
- FUN_00495ACA (0x495AFA)
- FUN_00495E0C (0x495E3A)
- FUN_00495EEE (0x495F19)
- FUN_00495F75 (0x495FA0)
- FUN_00495FFC (0x49600F)
- FUN_004C1D1E (0x4C1DD3)
- FUN_004C560B (0x4C5679)

Następny krok: zdekomponować te funkcje i szukać pętli po budynkach z logiką produkcji (`logicproduction`, stocks +0x64, input/output goodów).

---

## 7. Struktura job block i tabel plemienia (odkryte przez REA)

Zobacz `re_jobblock_structure.md` dla pełnej dokumentacji.

### Kluczowe odkrycia:

| Element | Adres | Opis |
|---------|-------|------|
| Job block (per job) | `tribe_base + 0x6928 + job*0x400` | Lista goodów do produkcji + jobDefaultGood |
| Job block count | `+0x00` | Liczba goodów na liście |
| Job block good list | `+0xD8` | ID goodów (4 B każdy) |
| Job default good | `+0x330` | Domyślny good wyświetlany w UI |
| Need table | `tribe_base + 0x55FC + good*0x14` | Wymagania surowcowe (FUN_0042D848) |
| Need table alt | `tribe_base + 0x519C + good*0x14` | Wymagania alternatywne (FUN_0042D803) |
| Threshold 1 | `tribe_base + 0x6740 + (tribe*0x6B82+good)*4` | Próg produkcji 1 (FUN_0042D97D) |
| Threshold 2 | `tribe_base + 0x6820 + (tribe*0x6B82+good)*4` | Próg produkcji 2 (FUN_0042D9A3) |

**UWAGA:** Threshold 1 i 2 używają starego imm `0x6B82` (rozmiar rekordu plemienia przed patchowaniem na 0x8578). To może być bug po rozszerzeniu ID!

### Jak działa wybór gooda do produkcji (UI):

```
FUN_0043E09A (select good)
  → FUN_0043E8A7 (set UI status)
    → FUN_0042DB20 (good on job block?)
    → Iteruje po good_list (+0xD8)
    → FUN_0044B5D9 (get +0x21C status)
    → FUN_0044B5E7 (set status)
  → Ustawia +0x218 = good, +0x1C = good

Statusy +0x21C:
  0x00 = można produkować
  0x0B = wybrany good
  0x0C = brak +0x195 flagi
  0x0D = nie na liście job block
  0x0E = można produkować (FUN_0042DA65 true)
```

### Dlaczego smalarz nie produkuje węgla — pełny obraz:

1. Smalarz (job 56) ma `+0x195[66]=1` (flaga ustawiona przez FUN_0044A0D9 lub ręcznie)
2. Smalarz dostarcza drewno do chałupy → trafia do `building+0x64` (stocks instancji)
3. **ALE** nie ma kodu który konwertuje `building+0x64[wood]` na `building+0x64[coal]` dla typu 57
4. `FUN_00473461` (unit tick) pomija typ 57 → nie ustawia timera, nie wywołuje FUN_0044A0D9
5. `FUN_00495e0c` (building resource mgmt) operuje na `DAT_00568CA8 + type*0xD0`, NIE na `building+0x64`
6. Węgiel nigdy nie zostaje utworzony → nie ma go w UI

### Rozwiązanie:

Dodać kod konwersji w `FUN_00494f01` lub `FUN_00495e0c` dla typu 57:
- Sprawdź czy `building+0x64` ma drewno (good 5)
- Jeśli tak, zmniejsz drewno, zwiększ węgiel
- LUB zmień `logictype` na 38 i niech `FUN_00473461` obsługuje produkcję

