# RE - Podsumowanie kluczowych funkcji (2026-10-17)

## Kluczowe adresy VA (ImageBase 0x400000)

| Adres | Nazwa | Rola |
|-------|-------|------|
| 0x473461 | FUN_00473461 | Tick jednostki - obsługuje typy 38 (szkoła), 39 (koszary). **BRAK obsługi typu 57 (smolarnia)** |
| 0x44A0D9 | FUN_0044A0D9 | Ustawia +0x195 dla job goods |
| 0x42DA65 | FUN_0042DA65 | Bramka produkcji - czy może produkować good |
| 0x42DB20 | FUN_0042DB20 | Czy good na liście job block |
| 0x4316F3 | FUN_004316F3 | Bramka budynku dla gooda (revmap) |

## Struktura danych (zdekompilowane)

### house_type (0x624 B, DAT_005113A0 + type*0x624)
- +0x000: category (3 = budynek)
- +0x008: output_good (np. 66 dla węgla)
- +0x060: stock_count
- +0x064: stocks[12] - tablica stocków
- +0x37C: stock_revmap[66] - revmap
- +0x484: production_count
- +0x488: production_list[20]
- +0x4D8: production_revmap[66]

### Instancja budynku (0x7E0 B, DAT_0x510BD0 + idx*0x7E0)
- +0x014: house_type index
- +0x02C: category/type
- +0x200: built_flag
- +0x644: owner_entries[20×4]

### Jednostka (unit) - kluczowe pola
- +0x14: tribe
- +0x18: job (0x19 = potter/25, 56 = smolarz)
- +0x1C: selected_good
- +0x100: building_idx
- +0x158: production_timer
- +0x195: can_produce[good] (flaga)
- +0x21C: job_good_status[good] (0, 0xB, 0xC, 0xD, 0xE)
- +0x390: building_idx
- +0xACC: interaction_state
- +0xAD0: interaction_good

### Tribe house (0x54C B, DAT_0x510BE0 + tribe*0x54C)
- +0x008: output good
- +0x1EC: tribe house type
- +0x338: stock storage

## Problemy do rozwiązania (RE)

1. **FUN_00473461 (unit tick)** - nie obsługuje logictype 57 (smolarnia). Tylko 38 (szkoła) i 39 (koszary). Smolarnia wraca wczesnym return.

2. **Produkcja** - nie jest podpięta pod school/barracks. Musimy dodać handling dla typu 57.

3. **ID towaru 66** - kolizja revmap w house_type (+0x37C + 66*4 = +0x484 = production_count). Trzeba przesunąć revmap lub użyć innego indeksu.

## Plan implementacji DLL

1. **Hook 0x46BD2F (dispatcher)** - dodać case 56 (smolarz) → FUN_0046D53A (potter handler, który jest uniwersalny)
2. **Hook 0x473461 (unit tick)** - dodać obsługę typu 57 dla produkcji
3. **Hook 0x44A0D9** - ustawia +0x195 dla good 57 w job block

Wszystkie dekompilacje są w pliku `.ai/re_rust/all_functions.rs`.