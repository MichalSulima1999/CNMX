# RE — Kompleksowe podsumowanie silnika CN.PLMOD.exe

**Data aktualizacji:** 2026-10-17
**Plik wykonywalny:** CN.PLMOD.exe (SHA-256: 367419b7a797c3db6c64c162f5bb74ad1668252ee32e60dfe8d685e0a4d63f00)
**Typ:** Knights & Merchants (gra typu ekonomiczno-miejska)

---

## 1. Architektura silnika

### Podstawowe dane
- **Format:** PE32 (x86), brak ASLR
- **ImageBase:** 0x400000
- **Rozmiar:** 1 146 880 B (0x118000)
- **Język:** C++ (prawdopodobnie MSVC)

### Globalne tablice i struktury

| Adres VA | Nazwa | Stride | Opis |
|----------|-------|--------|------|
| 0x510BC4 | elem_base | 0x4A80 | Elementy graczy (rozszerzone z 0x1278) |
| 0x511200 | tribe_base | 0x1AE08 | Rekordy plemion |
| 0x5113A0 | house_types | 0x624 | Typy budynków (55 → 127) |
| 0x511420 | good_types | 0xD0 | Typy towarów (66 → 127) |
| 0x510BD0 | buildings | 0x7E0 | Instancje budynków |
| 0x510BE0 | tribe_house | 0x54C | Budynki plemienia (+0x8 = output good) |
| 0x568C0C | building_instances | 0x8BC | Instancje budynków gracza |
| 0x569AA0/4/8 | UI context | — | Kontekst rysowania UI |
| 0x569ABC | font buffer | +0x400 | Bufor czcionki |

---

## 2. Struktury rekordów

### 2.1 Rekord typu budynku (house_type, 0x624 B)
`DAT_005113A0 + type * 0x624`

| Offset | Rozmiar | Nazwa | Przykład (typ 57 - smolarnia) |
|--------|---------|-------|-------------------------------|
| +0x000 | 4 | category | 3 |
| +0x008 | 4 | output_good | 66 (węgiel) |
| +0x01B..+0x020 | 3/wpis | stock entries | 0,0,0 |
| +0x060 | 4 | stock_count | 2 |
| +0x064 | 12×66 | stocks[0..11] | 02 00 ... |
| +0x37C | 4×66 | stock_revmap | 0xFFFFFFFF |
| +0x484 | 4 | production_count | 1 |
| +0x488 | 4×20 | production_list | [66] |
| +0x4D8 | 4×66 | production_revmap | 0 |
| +0x5E4 | 4 | unknown | — |
| +0x620 | 4 | zeroed | 0 |

**Kolizje przy good 66:**
- Stock revmap: `+0x37C + 66*4 = +0x484` (production count)
- Production revmap: `+0x4D8 + 66*4 = +0x5E0` (sąsiednie z +0x5E4)

### 2.2 Rekord typu towaru (good_type, 0xD0 B)
`DAT_00511420 + good * 0xD0`

| Offset | Nazwa | Opis |
|--------|-------|------|
| +0x000 | name | nazwa towaru |
| +0x020 | landscapetype | typ krajobrazu |
| +0x030 | isProducedOnMapFlag | produkowany na mapie |
| +0x031 | isProducedInHouseFlag | produkowany w budynku |
| +0x050 | productionInputGoods | towary wejściowe receptury |

### 2.3 Instancja budynku (building, 0x7E0 B)
`DAT_0x510BD0 + idx * 0x7E0` lub `DAT_00568C0C + idx * 0x8BC`

| Offset | Nazwa | Przykład (bldg[71]) |
|--------|-------|---------------------|
| +0x000 | ? | 1 |
| +0x004 | ? | 0x47 |
| +0x00C | ? | 0x41A |
| +0x010 | ? | 0x39 |
| +0x014 | house_type | 57 |
| +0x018 | ? | 0x3601 |
| +0x01C | ? | 1 |
| +0x020 | ? | 0 |
| +0x024 | ? | 0x3701 |
| +0x028 | ? | 1 |
| +0x02C | category? | 3 |
| +0x030 | type? | 3 |
| +0x060 | stock_count | 0 |
| +0x064 | stocks | 0 |
| +0x200 | built_flag | 0 = niezbudowany |
| +0x644 | owner_entries[20×4] | — |

### 2.4 Rekord plemienia (tribe, 0x1AE08 B)
`DAT_00511200 + tribe * 0x1AE08`

| Offset | Nazwa | Opis |
|--------|-------|------|
| +0x519C + good*0x14 | req_table | Wymagania surowcowe |
| +0x55FC + good*0x14 | need_table | Potrzeby dla gooda |
| +0x6740 + (tribe*0x6B82 + good)*4 | threshold1 | Próg produkcji 1 |
| +0x6820 + (tribe*0x6B82 + good)*4 | threshold2 | Próg produkcji 2 |
| +0x6928 + job*0x400 | job_block | Blok zawodu |
| +0x5D200 | player_type_flag | 1→2, 2→5, inaczej 1 |

### 2.5 Jednostka (unit)

| Offset | Nazwa | Opis |
|--------|-------|------|
| +0x14 | tribe | plemię |
| +0x18 | job | zawód (56 = smolarz) |
| +0x1C | selected_good | good wybrany w UI |
| +0x100 | building_idx | budynek przypisany |
| +0x158 | production_timer | timer produkcji |
| +0x15C | flag | ustawiana przez FUN_00473461 |
| +0x195 | can_produce[good] | flaga "może produkować" |
| +0x21C | job_good_status[good] | status UI: 0, 0xB, 0xC, 0xD, 0xE |
| +0x390 | building_idx | budynek przypisany |
| +0xACC | interaction_state | stan interakcji |
| +0xAD0 | interaction_good | good w interakcji |
| +0xAD4 | selected_good_interact | wybrany good w interakcji |
| +0xA68 | ui_state | stan UI (5/6) |
| +0xA7C | ? | — |
| +0xA80 | ? | kopiowane z tribe+4 |
| +0xB34 | building_idx | budynek przypisany |
| +0xB44 | house_list_idx | indeks do listy domów |
| +0xB48 | tribe_idx | indeks plemienia |
| +0xB4C | ? | — |
| +0xB51 | ui_flag | flaga UI |

---

## 3. Kluczowe funkcje

| Adres | Nazwa | Opis |
|-------|-------|------|
| 0x473461 | FUN_00473461 | Tick jednostki/produkcja (tylko typy 38, 39) |
| 0x44A0D9 | FUN_0044A0D9 | Ustawia +0x195 dla job goods |
| 0x42DA65 | FUN_0042DA65 | Bramka "czy może produkować" |
| 0x42DB20 | FUN_0042DB20 | Czy good na liście job block |
| 0x42D848 | FUN_0042D848 | Needforgood (czy ma surowce) |
| 0x42D9A3 | FUN_0042D9A3 | Próg plemienia dla gooda |
| 0x4316F3 | FUN_004316F3 | Bramka budynku dla gooda (revmap) |
| 0x431F37 | FUN_00431F37 | Zwraca revmap[good] z house record |
| 0x43267F | FUN_0043267F | Szukaj właściciela w building+0x644 |
| 0x494F01 | FUN_00494F01 | Operacja budynku (FUN_00494996) |
| 0x495E0C | FUN_00495E0C | Zarządzanie zasobami/produkcją budynku |
| 0x4E21B7 | FUN_004E21B7 | Renderer tekstu UI (tagi {newline}) |
| 0x46D53A | FUN_0046D53A | Interakcja z budynkiem (potter handler) |
| 0x46E1BE | FUN_0046E1BE | Sprawdź dostępność budynku |
| 0x4A693B | FUN_004A693B | Renderer panelu informacji budynku |
| 0x4C227C | FUN_004C227C | Renderer listy budynków UI |
| 0x449F2F | FUN_00449F2F | UI: zmień selected good |
| 0x44B2FA | FUN_0044B2FA | Ustawia status produkcji +0x21C |
| 0x44B5D9 | FUN_0044B5D9 | Getter statusu +0x21C |
| 0x44B5E7 | FUN_0044B5E7 | Setter statusu +0x21C |

---

## 4. Łańcuch produkcji — główna pętla gry i ticki budynków

### Przepływ wywołań (od głównej pętli do produkcji)

```
FUN_004078C8 (główna pętla gry)
  └─ FUN_0040AD0A (iteracja po budynkach)
       └─ FUN_00433662 (tick budynku)
            └─ FUN_0043127A (iteracja po tablicy jednostek)
                 └─ FUN_0044193D (tick jednostki)
                      └─ FUN_00462C70 (pętla stanu)
                           └─ FUN_0044319A (tick stanu +0x368)
                                └─ FUN_0046BAD7 (dyspozytor na job)
                                     └─ FUN_0046D53A (potter handler, job 0x19)
                                          └─ FUN_0046E52E (logika produkcji)
```

### Funkcje kluczowe

| Adres | Nazwa | Rola w łańcuchu produkcji |
|-------|-------|---------------------------|
| 0x4078C8 | FUN_004078C8 | Główna pętla gry — wywołuje tick budynków |
| 0x40AD0A | FUN_0040AD0A | Iteracja po budynkach (start..end) |
| 0x433662 | FUN_00433662 | Tick budynku — sprawdza ukończenie, animację |
| 0x43127A | FUN_0043127A | Iteracja po tablicy jednostek (stride 0x58) |
| 0x44193D | FUN_0044193D | Tick jednostki — warunek aktywności |
| 0x462C70 | FUN_00462C70 | Pętla stanu — wywołuje tick stanu głównego |
| 0x44319A | FUN_0044319A | Tick stanu głównego — wybiera handler |
| 0x43242C | FUN_0043242C | **Przypisuje job z house_type do unit+0x18** ★ |
| 0x43230A | FUN_0043230A | Worker dispatcher (param_2=2 → FUN_0043242C) |
| 0x431FF5 | FUN_00431FF5 | Building unit logic → woła dispatcher z param_2=2 |
| 0x432003 | FUN_00432003 | Rejestruje workera w building+0x644 |
| 0x4C8F14 | FUN_004C8F14 | Worker logic dispatcher (param_2=5 → FUN_0043242C) |
| 0x4C8919 | FUN_004C8919 | Dispatcher (case 5 → FUN_004C8F14) |
| 0x4B64A6 | FUN_004B64A6 | Pathfinding / unit init → triggeruje łańcuch |
| 0x46BAD7 | FUN_0046BAD7 | Dyspozytor na job (0x19 = potter) |
| 0x46D53A | FUN_0046D53A | Potter handler — zarządza produkcją |
| 0x46E52E | FUN_0046E52E | Logika produkcji — sprawdza surowce |
| 0x46E117 | FUN_0046E117 | Ustawia selected good w tribe house |
| 0x46E02B | FUN_0046E02B | Ustawia stan produkcji |
| 0x44B7B5 | FUN_0044B7B5 | Ustawia tribe house good |

### Job Assignment Chain — Jak jednostka dostaje job (NOWE ODKRYCIE)

**Główna funkcja:** **FUN_0043242C (0x43242C)** — przypisuje job z house_type do unit+0x18

```c
unit+0x18 = house_type_workers[job_idx]  // job_id z house_type+4
```

**Pełny łańcuch:**
```
Unit Creation
    ↓
FUN_004B64A6 → FUN_004C8919 (case 5) → FUN_004C8F14 (param_2=5)
    ↓
FUN_0043242C (PRZYPISANIE JOB!) ← KLUCZOWE
    unit+0x18 = house_type_workers[job_idx]
```

**Kluczowe funkcje:**

| Adres | Nazwa | Rola |
|-------|-------|------|
| 0x43242C | FUN_0043242C | Przypisuje job z house_type do unit+0x18 ★ |
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

---

### Globalne zmienne

| Adres | Nazwa | Opis |
|-------|-------|------|
| 0x510A10 | tick_counter | Globalny licznik ticków gry |
| 0x510A28 | delta_time | Delta time między tickami |
| 0x510BD4 | building_batch | Struktura batch budynków (start/end) |
| 0x511728 | house_lists | Tablica list domów (stride 0x18) |
| 0x510BF0 | unit_table | Tablica jednostek (stride 0x58) |
| 0x510BD8 | units | Tablica unitów (stride 0xC58) |
| 0x510BE0 | tribe_house | Tribe house (stride 0x54C) |

---

## 5. Problemy i otwarte wątki

| # | Problem | Lokalizacja |
|---|---------|-------------|
| 1 | FUN_00473461 nie obsługuje typu 57 (smolarnia) | 0x473482-0x473489 |
| 2 | FUN_00495E0c operuje na DAT_00568CA8 nie na building+0x64 | 0x495E0C |
| 3 | Storage UI crashuje dla bound extended | 0x415E8E |
| 4 | Stary imm 0x6B82 zamiast 0x8578 | FUN_00473461, FUN_0042D9A3, FUN_0042D97D |
| 5 | Kolizja revmap dla good 66 | +0x37C/+0x484, +0x4D8/+0x5E0 |
| 6 | **Brak obsługi smolarni (job 56)** — dyspozytor obsługuje tylko job 0x19 | 0x46BDDC, 0x46BD33 |
| 7 | **Limit jobów = 46** — nie można dodać job 56 bez code cave | 0x46BD33, 0x46BEBE |
| 8 | **Nazwy zawodów w DLL** — nie da się dodać nowej nazwy bez hooka | 0x4F40D0 (DLL) |
| 9 | **Job assignment chain** — znaleziono FUN_0043242C, ale UI nie pokazuje nowej nazwy | 0x43242C, 0x4B64A6 |

---

## 6. Podsumowanie gotowości do code cave

| Element | Status | Uwagi |
|---------|--------|-------|
| Parser INI (houses.ini, goodtypes.ini) | ✅ Gotowe | Obsługuje logicworker, logicstock, logicproduction |
| Job assignment (FUN_0043242C) | ✅ Znalezione | Przypisuje job z house_type+4 |
| Potter handler (FUN_0046D53A) | ✅ Uniwersalny | Obsługuje wszystkie typy przez INI |
| Logika produkcji (FUN_0046E52E) | ✅ Gotowa | Sprawdza surowce, output |
| Dodanie towaru (FUN_0044B910) | ✅ Gotowe | Dodaje do tribe house stock |
| **Job limit (46)** | ⚠️ **Wymaga patcha** | CMP EAX, 0x2E → 0x7F |
| **Job 56 > limit** | ⚠️ **Użyj job 26** | Nie wymaga rozszerzania case table |
| **Nazwa zawodu (UI)** | ❌ **Wymaga hooka DLL** | Nazwy w DLL 0x4F40D0 |
| **Job 56 w case table** | ❌ > 46 | Użyj job 26 (0x1A) |

---

## 7. Plan implementacji smolarni

### Opcja A: Job 26 (REKOMENDOWANA — bez rozszerzania limitu)

```ini
# houses.ini
[logichousetype]
debugname "smolarnia"
logictype 57
logicmaintype 3
logicworker 26 1          # job 26 (0x1A) zamiast 56!
logicstock 5 10 1
logicstock 66 15 0
logicproduction 66
```

**Patchy binarne (3 miejsca):**
1. `0x46BD33`: `83 F8 2E` → `83 F8 7F` (limit 46 → 127) — opcjonalnie
2. `0x46BE76+8`: `E5 BD 46 00` → `26 BE 46 00` (jump_table[2] = 0x46BE26)
3. `0x46BE26`: Nowy case `MOV ECX,ESI; CALL 0x46D53A; JMP 0x46BE26`

### Opcja B: Job 56 (wymaga rozszerzania case table)

Wymaga przeniesienia case table w pamięci — skomplikowane, niezalecane.

---

## 8. Podsumowanie RE — co mamy, czego brakuje

| Element | Status | Szczegóły |
|---------|--------|-----------|
| ✅ Parser INI | Gotowe | houses.ini, goodtypes.ini |
| ✅ Potter handler | Gotowe | Uniwersalny, używa INI |
| ✅ Produkcja | Gotowa | FUN_0046E52E, FUN_0044B910 |
| ✅ Job assignment | **ZNALEZIONE** | FUN_0043242C (0x43242C) |
| ✅ Worker dispatcher | **ZNALEZIONE** | FUN_0043230A, FUN_004C8F14 |
| ✅ Job limit | **ZNALEZIONE** | 0x46BD33, case table 46 |
| ❌ Nazwy zawodów | **W DLL** | 0x4F40D0, wymaga hooka |
| ❌ UI nowej nazwy | **Wymaga code cave** | Hook 0x4F40D0 |
| ❌ Wolne miejsce na code cave | **Do sprawdzenia** | Po 0x46BE1B |

---

## 9. Następne kroki (kolejność)

1. **Sprawdź wolne miejsce** po 0x46BE1B (dla nowego case)
2. **Zaktualizuj patch_charcoal_burner.py** pod job 26
3. **Zbadaj DLL (0x4F40D0)** — tablica nazw zawodów
4. **Zaprojektuj hook UI** — podmiana nazwy dla job 26
5. **Zastosuj patchy INI + binarne**
6. **Test w grze** — czy smolarnia produkuje węgiel?

---

*Ostatnia aktualizacja: 2026-10-18*
*Autor: REA + Ghidra 12.1.4*
