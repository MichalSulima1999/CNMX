# RE — Funkcje bâtiments i produkcji budynków (ETAP 7, REA + Ghidra)

Uzupełnienie do `re_engine_comprehensive.md`, `re_production_pipeline.md`, `re_structures.md`, `re_functions.md`.

Źródła: REA (Rizin/Ghidra 12.1.4) — `procedure_pseudo_code`, `xrefs`, `inspect_address_context` na `CN.PLMOD.exe` (SHA-256: 367419b7...).

---

## 1. Architektura produkcji budynków — nowy model

Dotychczasowa hipoteza (tylko `FUN_00473461` unit tick) była **niepełna**. REA wykazało że produkcja/zarządzanie zasobami budynku jest obsługiwane przez **FUN_00494f01** (główna operacja budynku), wywoływaną z renderera mapy `FUN_0049067f`. Nie istnieje osobny "building production tick".

### łańcuch wywołań

```
FUN_0049067f (renderer mapy, VA 0x490D10)
  └── dla każdego obiektu na mapie:
        jeśli typ obiektu == 0x02 (budynek):
          └── FUN_00494f01 (operacja budynku, VA 0x494F01)
                ├── pobiera instancję budynku: param_1 * 0x7E0 + DAT_00510BD0
                ├── pobiera player building instance: house_type_idx * 0x8BC + DAT_00568C0C
                ├── pobiera dane typu budynku: param_1 * 0xD0 + DAT_00568CA8
                ├── sprawdza built_flag (+0x200)
                ├── wywołuje FUN_0049A65E (produkcja/zawartość budynku)
                ├── wywołuje FUN_0049599B (coś z building)
                └── wywołuje FUN_00495E0C (zarządzanie zapasami/produkcją) — WEWNĄTRZ siebie
```

---

## 2. FUN_00494f01 — Główna operacja budynku (VA 0x494F01)

```c
void __cdecl FUN_00494f01(uint building_idx, void *param_2, uint *param_3, uint *param_4, int param_5, void *param_6)
{
  // Instancja budynku (globalne)
  void *bldg = (void *)(building_idx * 0x7E0 + DAT_00510BD0);
  FUN_004316D0((int)bldg);  // inicjalizacja budynku

  // Player building instance (per gracz)
  void *pBldgInst = (byte *)(*(int *)((int)bldg + 0x10) * 0x8BC + DAT_00568C0C);

  // Dane typu budynku (stride 0xD0, jak good_types)
  int *bldgTypeData = (int *)(building_idx * 0xD0 + DAT_00568CA8);

  // Sprawdź czy budynek jest zbudowany (+0x200)
  if (*(char *)((int)bldg + 2000) == '\0') { ... }

  // Wywołaj produkcję/zawartość budynku
  FUN_0049A65E(..., *(int *)((int)bldg + 0xC));

  // Inne operacje na budynku
  FUN_0049599B(building_idx, &local_1a0);

  // FUN_00495E0C jest wywoływane WEWNĄTRZ tej funkcji (adres 0x495738 leży w range 0x494F01-0x495921)
}
```

**Kluczowe struktury:**
- `DAT_00510BD0` — tablica instancji budynków, stride `0x7E0`
- `DAT_00568C0C` — tablica player building instances, stride `0x8BC`
- `DAT_00568CA8` — tablica danych typu budynku, stride `0xD0` (analogiczna do good_types!)

---

## 3. FUN_00495e0c — Zarządzanie zapasami/produkcją budynku (VA 0x495E0c)

Ta funkcja jest wywoływana **wewnątrz FUN_00494f01** (nie jako osobny tick). Odpowiada za zwiększanie/zmniejszanie liczników zapasów w budynku.

```c
void __cdecl FUN_00495e0c(int building_idx)
{
  // Dane typu budynku: building_idx * 0xD0 + DAT_00568CA8
  uint *bldgTypeData = (uint *)(building_idx * 0xD0 + DAT_00568CA8);

  // Instancja budynku: building_idx * 0x7E0 + DAT_00510BD0
  int bldg = building_idx * 0x7E0 + DAT_00510BD0;

  // Player building instance
  int pBldgInst = *(int *)(bldg + 0x10) * 0x8BC + DAT_00568C0C;

  // Wartość z player building instance: +0x1D8 + house_type_idx * 4
  uint uVar5 = *(uint *)(pBldgInst + 0x1D8 + *(int *)(bldg + 0x20) * 4);

  // Wskaźnik do qualcosa w player building instance: (house_type_idx + 0x26) * 0x34 + pBldgInst
  uint *puVar1 = (uint *)((*(int *)(bldg + 0x20) + 0x26) * 0x34 + pBldgInst);

  // Wartość z building +0x7C8
  int iVar3 = *(int *)(bldg + 0x7C8);
  uint uVar2 = *puVar1;

  if (iVar3 < 0) iVar3 = 0;

  // Współczynnik produkcji: ((uVar5 - building_idx) * uVar2) / uVar5
  uint uVar4 = ((uVar5 - building_idx) * uVar2) / uVar5;
  if ((iVar3 < (int)uVar5) && (uVar4 == 0) && (uVar2 != 0))
    uVar4 = 1;

  uint uVar5_2 = *bldgTypeData;  // production count / stock count z danych typu

  if (uVar4 < uVar5_2) {
    // ZUŻYJ surowiec — zmniejsz licznik zapasu
    uint uVar5_3 = 0;
    if (uVar2 != 0) {
      do {
        if ((uVar5_3 < 200) && (*(char *)(uVar5_3 + 4 + (int)bldgTypeData) != '\0')) {
          *(undefined1 *)(uVar5_3 + 4 + (int)bldgTypeData) = 0;  // wyczyść flagę zapasu
          *bldgTypeData = *bldgTypeData - 1;  // zmniejsz count
          return;
        }
        uVar5_3 = uVar5_3 + 1;
      } while (uVar5_3 < uVar2);
    }
  }
  else if (uVar5_2 < uVar4) {
    // TWÓRZ produkt — zwiększ licznik zapasu (losowo)
    uint uVar6 = _rand();
    uint uVar4_2 = *puVar1;
    uint uVar9 = 0, uVar7 = 0;
    if (uVar4_2 != 0) {
      do {
        if ((uVar7 < 200) && (*(char *)(uVar7 + 4 + (int)bldgTypeData) == '\0')) {
          if (uVar6 % (uVar2 - uVar5_2) <= uVar9) {
            *(undefined1 *)(uVar7 + 4 + (int)bldgTypeData) = 1;  // ustaw flagę zapasu
            *bldgTypeData = *bldgTypeData + 1;  // zwiększ count
            return;
          }
          uVar9 = uVar9 + 1;
        }
        uVar7 = uVar7 + 1;
      } while (uVar7 < uVar4_2);
    }
  }
}
```

**Interpretacja:**
- Funkcja nie operuje na `building+0x64` (stocks instancji), lecz na `DAT_00568CA8 + type*0xD0` (dane typu budynku)
- Zużywa/tworzy towary na podstawie współczynnika obliczonego z `uVar5` (wartość z player building instance +0x1D8)
- Używa `_rand()` dla losowego tworzenia produktów
- **To może oznaczać że produkcja węglan nie jest deterministycznie powiązana z dostarczaniem drewna przez smolarza** — może być osobny system zapasów

---

## 4. FUN_0047e062 — Flagi typu budynku (VA 0x47E062)

Ustawia flagi w tabelach danych:
- `param_1 == 0x11`: `*(byte *)(param_3 * 0xD0 + 0xcc + DAT_00568CA8) = value & 1;`
  → flaga w `DAT_00568CA8 + building_type * 0xD0 + 0xCC`
- `param_1 == 0x10`: flaga w `DAT_00568CB0` (inne tablice)
- `param_1 == 0x0E`: flaga w `DAT_0055529C`

`DAT_00568CA8 + type * 0xD0 + 0xCC` może być flagą "produkcja aktywna" lub podobną dla typu budynku.

---

## 5. Sprite'y surowców — skąd biorą się grafiki

### Tablice sprite'ów

| Adres VA | Nazwa | Używane przez | Opis |
|----------|-------|---------------|------|
| 0x511698 | sprite_table_1 | FUN_0042f710 | Sprite'y towarów/budynków (tabela 1) |
| 0x5116A0 | sprite_table_2 | FUN_0042f754 | Sprite'y towarów/budynków (tabela 2) |
| 0x5116A4 | sprite_table_3 | FUN_0042f776 | Sprite'y towarów/budynków (tabela 3) |

### Funkcje dostępu do sprite'ów

```c
// FUN_0042f710 (VA 0x42F710) — sprite table 1
int FUN_0042f710(int idx, uint flag) {
  if (DAT_00511698 == NULL) return 0;
  uint uVar1 = idx * 2;
  if (1 < flag) uVar1 = uVar1 + 1;  // idx*2 + 1 dla flag > 1 (prawdopodobnie klatka animacji)
  return FUN_0042bcae(DAT_00511698, uVar1);  // tab[index]
}

// FUN_0042f754 (VA 0x42F754) — sprite table 2
int FUN_0042f754(int idx, uint flag) {
  if (DAT_005116A0 == NULL) return 0;
  uint uVar1 = idx * 2;
  if (1 < flag) uVar1 = uVar1 + 1;
  return FUN_0042bcae(DAT_005116A0, uVar1);
}

// FUN_0042f776 (VA 0x42F776) — sprite table 3
int FUN_0042f776(int idx, uint flag) {
  if (DAT_005116A4 == NULL) return 0;
  uint uVar1 = idx * 2;
  if (1 < flag) uVar1 = uVar1 + 1;
  return FUN_0042bcae(DAT_005116A4, uVar1);
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
1. `good_id * 2` (lub `good_id * 2 + 1` dla drugiej klatki animacji)
2. Wynik jest indeksem w tablicy `DAT_00511698/6A0/6A4`
3. `FUN_0042BCAE(tab, index)` zwraca wskaźnik na dane sprite'u (prawdopodobnie obraz z pliku .cif)

**Pliki .cif:** `Data\logic\goodtypes.cif`, `Data\logic\housetypes.cif`, `Data\engine2d\inis\vehicles\jobgraphics.cif` zawierają binarne dane graficzne. Engine ładuje je przy starcie do tablic `DAT_00511698/6A0/6A4`. Gdzie dokładnie następuje ładowanie — nie zostało zidentyfikowane w tej sesji (brak stringów "goodtypes.cif" w binarium, prawdopodobnie ścieżki są budowane dynamicznie lub zasoby są w PE).

---

## 6. Root cause — dlaczego smolarz nie produkuje węgla

### Potwierdzony przez REA:

1. **FUN_00473461 (unit tick)** — obsługuje TYLKO typy budynków 38 i 39. Dla typu 57 (smolarnia) robi wczesny `return`. Nie ustawia `+0x195[66]`, nie ma timera produkcji.

2. **FUN_00494f01 (building operation)** — wywoływana z renderera mapy (`FUN_0049067f`) dla każdego budynku na mapie. Obsługuje produkcję przez `FUN_00495e0c`.

3. **FUN_00495e0c (resource management)** — zarządza zapasami w `DAT_00568CA8 + type*0xD0`, NIE w `building+0x64` (stocks instancji). Oblicza współczynnik produkcji na podstawie wartości z player building instance.

### Problem:

Smolarz (job 56) dostarcza drewno do chałupy węglarskiej (typ 57). Drewno trafia do stocks budynku (`building+0x64`). Ale:

- Nie ma kodu który konwertuje `building+0x64` (drewno) na `building+0x64` (węgiel) dla typu 57
- `FUN_00495e0c` operuje na `DAT_00568CA8` (dane typu), nie na stocks instancji
- `FUN_00473461` nie obsługuje typu 57

**Węgiel nie pojawia się w UI, bo:**
1. Nie jest tworzone w kodzie produkcji (brak konwersji drewno→węgiel)
2. Nawet jeśli by zostało utworzone, pętla towarów UI (`0x415E8E`) może crashować dla ID > 66

---

## 7. Dane typu budynku (DAT_00568CA8)

Stride: 0xD0 (jak good_types). Używane przez:
- FUN_00494f01 (building operation)
- FUN_00495e0c (resource management)
- FUN_0047E062 (flagi: +0xCC)
- 0x47E951, 0x48FBEE, 0x48FC16, 0x48FC28, 0x48FC33, 0x48FC8B, 0x48FD06, 0x48FD47, 0x494F46, 0x4CD406

Prawdopodobna struktura (analogiczna do good_types, 0xD0 B):
| Offset | Pole | Opis |
|--------|------|------|
| +0x00 | ? | |
| +0xCC | flaga | ustawiana przez FUN_0047E062 (param_1 == 0x11) |
| ... | ... | |

---

## 8. Następne kroki RE

1. **Zdekomponować FUN_0049A65E** (wywoływane z FUN_00494f01) — prawdopodobnie odpowiedzialne za konwersję surowców w budynku
2. **Zdekomponować FUN_0049599B** (wywoływane z FUN_00494f01) — co robi z building?
3. **Znaleźć gdzie ładuje się goodtypes.cif** do tablic DAT_00511698/6A0/6A4 — szukać wywołań FUN_0042BCAE przy starcie
4. **Sprawdzić czy FUN_00495e0c modyfikuje building+0x64** (stocks instancji) czy tylko DAT_00568CA8
5. **Dodać kod konwersji drewno→węgiel** dla typu 57 (code cave lub zmiana logictype na 38)
6. **Sprawdzić czy UI obsługuje good 66** — pętla 0x415E8E crashuje jeśli bound extended
