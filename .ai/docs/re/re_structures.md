# RE — Szczegółowe struktury danych CN.PLMOD.exe

Uzupełnienie do `re_engine_comprehensive.md`. Wszystkie adresy to VA (ImageBase 0x400000).

---

## A. Globalne wskaźniki (tablice bazowe)

| Adres VA | Symbol | Element | Stride | Uwagi |
|----------|--------|---------|--------|-------|
| 0x510BC4 | `elem_base` | gracz/element | 0x4A80 | `[base] + gracz*0x4A80` (rozszerzone z 0x1278/0x42) |
| 0x511200 | `tribe_base` | plemię | 0x1AE08 | `[base] + plemię*0x1AE08` |
| 0x5113A0 | `house_types` | typ budynku | 0x624 | Rekord typu domu |
| 0x511420 | `good_types` | typ towaru | 0xD0 | Rekord typu towaru (66→127) |
| 0x510BD0 | `buildings` | instancja budynku | 0x7E0 | Instancje budynków (globalne) |
| 0x510BE0 | `tribe_house` | budynek plemienia | 0x54C | +0x8 = output good ID |
| 0x568C0C | `building_instances` | instancja gracza | 0x8BC | Pętla produkcji budynków |
| 0x568CA8 | `bldg_type_data` | dane typu budynku | 0xD0 | Produkcja/zasoby typu budynku — używane przez FUN_00494f01, FUN_00495e0c, FUN_0047e062 |
| 0x511698 | `sprite_table_1` | sprite'y | — | Używana przez FUN_0042f710 |
| 0x5116A0 | `sprite_table_2` | sprite'y | — | Używana przez FUN_0042f754 |
| 0x5116A4 | `sprite_table_3` | sprite'y | — | Używana przez FUN_0042f776 |

---

## B. Rekord typu budynku (house_type) — 0x624 B

`DAT_005113A0 + type * 0x624`

| Offset | Rozmiar | Nazwa | Opis | Przykład (typ 57 smolarnia) |
|--------|---------|-------|------|------------------------------|
| +0x000 | 4 | category | kategoria budynku | 3 |
| +0x008 | 4 | output_good | good produkowany | 66 (węgiel) |
| +0x01B..+0x020 | 3 B/wpis | stock entries | wpisy zapasów | 0,0,0 |
| +0x060 | 4 | stock_count | liczba wpisów zapasów | 2 |
| +0x064 | 12×66 B | stocks | 12 wpisów × 12 B (good, qty, flag) | 02 00 ... |
| +0x37C | 4×66 | stock_revmap | good → index w stocks, inic -1 | 0xFFFFFFFF |
| +0x484 | 4 | production_count | liczba receptur (max 20=0x14) | 1 |
| +0x488 | 4×20 | production_list | lista goodów output | [66] |
| +0x4D8 | 4×66 | production_revmap | good → index na liście | 0 |
| +0x5E4 | 4 | unknown_5E4 | — | — |
| +0x620 | 4 | zeroed | zerowane per rekord | 0 |

### Kolizja revmap przy good 66
- Stock revmap: `+0x37C + 66*4 = +0x484` → nadpisuje `production_count`. Obejście: `logicproduction 66` przed `logicstock 66 15 0`.
- Production revmap: `+0x4D8 + 66*4 = +0x5E0` → sąsiednie z `+0x5E4`, prawdopodobnie nieszkodliwe.

---

## C. Instancja budynku — 0x7E0 B

`DAT_00510BD0 + idx * 0x7E0` (lub `DAT_00568C0C + idx * 0x8BC` dla instancji gracza)

| Offset | Nazwa | Obserwacja (bldg[71] @ 0x1EBBFF40) | Uwagi |
|--------|-------|-------------------------------------|-------|
| +0x000 | ? | 1 | |
| +0x004 | ? | 0x47 | |
| +0x00C | ? | 0x41A | |
| +0x010 | ? | 0x39 | |
| +0x014 | house_type | 57 | typ budynku z houses.ini |
| +0x018 | ? | 0x3601 | |
| +0x01C | ? | 1 | |
| +0x020 | ? | 0 | |
| +0x024 | ? | 0x3701 | |
| +0x028 | ? | 1 | |
| +0x02C | category? | 3 | |
| +0x030 | type? | 3 | |
| +0x200 | built_flag | `!= 0` jeśli budynek gotowy | sprawdzane w FUN_0046D53A (`pcVar15[2000]`) |
| +0x060 | stock_count | 0 (w zrzucie) | liczba zapasów w budynku |
| +0x064 | stocks | 0 | zapasy towarów |
| +0x644 | owner_entries[20×4] | — | FUN_0043267F szuka wpisu równego owner |

---

## D. Rekord plemienia (tribe) — 0x1AE08 B (rozszerzone)

`DAT_00511200 + tribe * 0x1AE08`

| Offset | Nazwa | Uwagi |
|--------|-------|-------|
| +0x6740 | tribe_threshold[good] | próg plemienia dla gooda: `+ 0x6740 + (tribe*REC + good)*4` |
| +0x6820 | tribe_threshold2[good] | dodawany gdy local_8 != 0 |
| +0x5D200 | player_type_flag | 1→2, 2→5, inaczej 1 (w FUN_004C227C / FUN_0046D53A) |

---

## E. Jednostka (unit)

| Offset | Nazwa | Uwagi |
|--------|-------|-------|
| +0x14 | tribe | plemię |
| +0x18 | job | zawód (56 = smolarz) |
| +0x1C | selected_good | good wybrany w UI |
| +0x158 | production_timer | porównywany z progiem plemienia |
| +0x15C | flag | ustawiana przez patch 0x4A1C0 |
| +0x195 | can_produce[good] | flaga "może produkować good" |
| +0x21C | job_good_status[good] | 0, 0xB, 0xC, 0xD, 0xE |
| +0xA68 | ui_state | 5 / 6 w interakcji z budynkiem |
| +0xACC | interaction_state | 0/2/4 |
| +0xAD0 | interaction_good | good w interakcji |
| +0xAD4 | selected_good_interact | porównywane z building+8 / +0x10 |
| +0xB44 | house_list_idx | `FUN_0041C61E(DAT_00511728, +0xB44)` |
| +0xB48 | tribe_idx | `* 0x54C + DAT_00510BE0` |
| +0xB4C | ? | kopiowane do +0xA80 |
| +0xB51 | ui_flag | wpływa na +0x368 (0x15 vs 1) |
| +0xB34 | building_idx | budynek, do którego przypisana |

---

## F. Rekord typu towaru (good_type) — 0xD0 B

`DAT_00511420 + good * 0xD0`

| Offset | Nazwa | Opis |
|--------|-------|------|
| +0x000 | name | nazwa towaru |
| +0x020 | landscapetype | typ krajobrazu |
| +0x030 | isProducedOnMapFlag | produkowany na mapie |
| +0x031 | isProducedInHouseFlag | produkowany w budynku |
| +0x050 | productionInputGoods | good(y) wejściowe receptury |

---

## G. Dane typu budynku (bldg_type_data) — stride 0xD0

`DAT_00568CA8 + building_type * 0xD0`

Używane przez:
- `FUN_00494f01` — główna operacja budynku
- `FUN_00495e0c` — zarządzanie zapasami/produkcją
- `FUN_0047e062` (param_1 == 0x11) — ustawia flagę przy +0xCC
- 0x47E951, 0x48FBEE, 0x48FC16, 0x48FC28, 0x48FC33, 0x48FC8B, 0x48FD06, 0x48FD47, 0x494F46, 0x4CD406

| Offset | Nazwa | Opis |
|--------|-------|------|
| +0xCC | flaga | ustawiana przez FUN_0047e062 (param_1 == 0x11) — prawdopodobnie "produkcja aktywna" |
| +0x00 | production_count | liczba zapasów/produkcji (używane w FUN_00495e0c jako *bldgTypeData) |
| +0x04..+0xC8 | flagi zapasów | 200 bajtów flag (używane w FUN_00495e0c: iteruje uVar5_3 < 200, sprawdza *(char *)(uVar5_3 + 4 + bldgTypeData)) |

---


---
