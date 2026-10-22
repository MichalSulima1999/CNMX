# RE — Struktura job block i tabel plemienia (odkryte przez REA)

Uzupełnienie do `re_structures.md`, `re_functions_comprehensive.md`, `re_production_pipeline.md`.

Źródło: REA (Ghidra 12.1.4) — dekompilacje FUN_0042DB20, FUN_0043E8A7, FUN_0044B2FA, FUN_00449F2F, FUN_0044A0D9.

---

## 1. Job block — tabela zawodów plemienia

Adres: `DAT_00511200 + tribe * 0x1AE08 + 0x6928 + job * 0x400`

| Offset | Rozmiar | Nazwa | Opis |
|--------|---------|-------|------|
| +0x000 | 4 | count | liczba goodów na liście job block |
| +0x004 | 4 | ? | nieznane |
| +0x0D8 | 4×N | good_list | lista ID goodów które ten job może produkować |
| +0x330 | 4 | jobDefaultGood | domyślny good do produkcji (wyświetlany w UI) |

**Uwagi:**
- `job*0x400` = 1024 B na zawód
- Lista goodów zaczyna się przy +0xD8, liczba wpisów = count (+0x00)
- jobDefaultGood przy +0x330 jest używany przez FUN_0044B2FA i FUN_0044B226 do ustawiania statusu UI

---

## 2. Tabele plemienia (tribe tables)

Baza: `DAT_00511200 + tribe * 0x1AE08`

### 2.1 Tabela wymagań surowcowych (needforgood) — offset 0x55FC

`tribe_base + 0x55FC + good * 0x14` — używane przez FUN_0042D848

| Offset | Rozmiar | Nazwa | Opis |
|--------|---------|-------|------|
| +0x00 | 4 | target | wymagana ilość surowców |
| +0x04 | 4 | count | liczba typów surowców wejściowych |
| +0x08 | 4×N | input_goods | ID surowców wejściowych |

### 2.2 Tabela wymagań alternatywna — offset 0x519C

`tribe_base + 0x519C + good * 0x14` — używane przez FUN_0042D803

Identyczna struktura jak powyżej. Różne offsety mogą oznaczać różne kategorie wymagań (np. budynek vs jednostka).

### 2.3 Próg produkcji 1 — offset 0x6740

`tribe_base + 0x6740 + (tribe * 0x6B82 + good) * 4` — używane przez FUN_0042D97D

UWAGA: Używa starego imm 0x6B82 (rozmiar rekordu plemienia przed patchowaniem). Po rozszerzeniu ID powinno być 0x8578.

### 2.4 Próg produkcji 2 — offset 0x6820

`tribe_base + 0x6820 + (tribe * 0x6B82 + good) * 4` — używane przez FUN_0042D9A3

Także używa starego imm 0x6B82.

---

## 3. łańcuch decyzyjny produkcji (UI)

Kiedy gracz wybiera good do produkcji w UI (lub gra automatycznie wybiera):

```
FUN_0043E09A (select good to produce)
  ├── FUN_0045C66E (sprawdź coś)
  ├── FUN_0042DB20 (good na job block?)
  ├── FUN_0042C909 (inne sprawdzenie)
  ├── FUN_0043E8A7 (ustaw status UI +0x21C)
  │   ├── FUN_0042DB20 (good na job block?)
  │   ├── iteruje po goodach z job block (+0xD8)
  │   │   ├── FUN_0044B5D9 (pobierz status +0x21C)
  │   │   └── FUN_0044B5E7 (ustaw status 0 jeśli < 0xC i > 0)
  │   └── FUN_0044B5E7(this, good, 0x0B)  // ustaw wybrany good na status 0xB
  │   └── ustaw +0x218 = good, +0x1C = good
  └── jeśli job == 7: dodatkowe obsługa (FUN_0042C6F0, FUN_0042C73B, FUN_0042C783, FUN_0042878E)
  └── jeśli FUN_0042C6F0 (ma budynek):
      ├── FUN_0042C8A8 (building type == 4?)
      ├── FUN_00461C14 (pobierz good z joba)
      ├── FUN_004316F3 (bramka budynku dla gooda)
      └── FUN_0043D037 (jeśli bramka nie przechodzi)
```

### Statusy goodów (+0x21C) w UI:

| Wartość | Znaczenie |
|---------|-----------|
| 0 | good dostępny do produkcji |
| 0x0B (11) | wybrany good / jobDefaultGood |
| 0x0C (12) | brak flagi +0x195 (nie można produkować) |
| 0x0D (13) | good nie na liście job block |
| 0x0E (14) | good można produkować (FUN_0042DA65 true) |

---

## 4. Flag +0x195 — "can produce good"

Ustawiana przez:
1. `FUN_00473461` (unit tick) — gdy timer osiąga próg, dla local_8
2. `FUN_0044A0D9` — dla wszystkich goodów z job block gdy warunki spełnione
3. `FUN_00449F2F` — wywołuje FUN_0044A0D9 na końcu

Sprawdzana przez `FUN_0042DA65` jako pierwszy warunek produkcji.

---

## 5. Aktualizacja struktury jednostki (unit)

Dodatkowe offsety odkryte przez REA:

| Offset | Nazwa | Opis |
|--------|-------|------|
| +0x18 | job | zawód (używane przez FUN_0042C5B3, FUN_0042C676, FUN_0042C6BC, FUN_0042C6CF) |
| +0x194 | flag | ustawiana przez FUN_0044A0D9 na podstawie job_block[0] |
| +0x195 | can_produce[good] | flaga "może produkować good" |
| +0x1C | selected_good | good wybrany w UI |
| +0x158 | production_timer | timer produkcji |
| +0x15C | flag_good[good] | flaga per good (ustawiana przez FUN_00473461 i FUN_0044A0D9) |
| +0x1CD | flag | ustawiana gdy good == 0x38 i job == 0x38 |
| +0x218 | selected_production_good | good wybierany do produkcji |
| +0x21C | job_good_status[good] | status UI: 0, 0xB, 0xC, 0xD, 0xE |
| +0x38C | ui_flag | flaga UI (zerowana przy wyborze gooda) |
| +0xB30 | building_output_good | output good z budynku |
| +0xB34 | building_idx | indeks budynku |
| +0xB3C | ? | ustawiane przez FUN_0043E09A |
| +0xB40 | ? | ustawiane przez FUN_0043E09A |
| +0xB44 | house_list_idx | indeks do listy domów |
| +0xB48 | tribe_idx | indeks plemienia |
| +0xB4C | ? | kopiowane do +0xA80 |
| +0xB51 | ui_flag | wpływa na +0x368 w UI |
| +0xB7C | ? | ustawiane przez FUN_0044A0D9 (0x14, 10, lub 5) |
| +0x1E0 | flag_block[0x38] | bloki flag (zerowane przez FUN_0044A0D9) |
| +0x1DF | flag | ustawiane przez FUN_0044A0D9 |
| +0x1FE, +0x1FF, +0x200 | flagi | ustawiane przez FUN_0044A0D9 |

---

## 6. Kolejne kroki RE

| # | Zadanie | Priorytet |
|---|---------|-----------|
| 1 | Zdekomponować FUN_00494996 (wywoływane z FUN_0049599B) | Wysoki |
| 2 | Zdekomponować FUN_0044B5E7 (setter statusu gooda) | Wysoki |
| 3 | Zdekomponować FUN_0045C66E, FUN_0042C909, FUN_0042C73B, FUN_0042C783, FUN_0042878E (używane w FUN_0043E09A) | Średni |
| 4 | Znaleźć gdzie ładuje się goodtypes.cif do DAT_00511698/6A0/6A4 | Średni |
| 5 | Sprawdzić czy FUN_00495e0c modyfikuje building+0x64 czy tylko DAT_00568CA8 | Wysoki |
| 6 | Dodać kod konwersji drewno→węgiel dla typu 57 | Krytyczny |
