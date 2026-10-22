# RE — Przegląd silnika CN.PLMOD.exe (Etap 1)

## Struktury kluczowe (globalne, VA)

| Adres VA | Nazwa | Opis |
|----------|-------|------|
| 0x510bc4 | elem_base | Tablica elementów (per gracz/plemie), stride 0x4A80 |
| 0x511200 | tribe_base | Tablica rekordów plemion, stride 0x215E0 |
| 0x5113a0 | house_types | Tablica typów domów, stride 0x624 |
| 0x511180 | job_types | Tablica typów zawodów, stride 0x88 |
| 0x511420 | good_types | Tablica typów towarów, stride ? |
| 0x510bd0 | buildings | Tablica instancji budynków, stride 0x7e0 |
| 0x510bd8 | ? | Tablica co 0xc58 (używana w FUN_004cb028) |
| 0x510be0 | ? | Tablica co 0x54c (używana w FUN_004cc99c) |

## Struktura rekordu domu (DAT_005113a0 + type*0x624)

| Offset | Nazwa | Wartość dla typ 57 (smolarnia) |
|--------|-------|--------------------------------|
| +0x00 | category | 3 |
| +0x08 | output_good | 66 (węgiel) |
| +0x1b..+0x20 | stock entries (3 bajty/wpis) | 0,0,0 |
| +0x60 | stock_count | 2 |
| +0x64 | stocks[0..11] (12 B/wpis) | 02 00 00 00 01 00 00 00 01 00 00 00 ... |
| +0x37c | stock revmap[good] (4 B/wpis) | 0xFFFFFFFF (dla 0,1) |
| +0x484 | prodcount / revmap[66] | 1 |
| +0x488 | prodlist[0..] | 66 (węgiel) |
| +0x4D8 | prodrevmap[good] | 0 |

## Struktura instancji budynku (0x510bd0 + idx*0x7e0)

| Offset | Nazwa | Obserwacja (bldg[71] @0x1EBBFF40) |
|--------|-------|-----------------------------------|
| +0x00 | ? | 1 |
| +0x04 | ? | 0x47 |
| +0x0c | ? | 0x41a |
| +0x10 | ? | 0x39 |
| +0x14 | house_type | 57 |
| +0x18 | ? | 0x3601 |
| +0x1c | ? | 1 |
| +0x20 | ? | 0 |
| +0x24 | ? | 0x3701 |
| +0x28 | ? | 1 |
| +0x2c | category? | 3 |
| +0x30 | type? | 3 |
| +0x60 | stock_count | 0 (w zrzucie) |
| +0x64 | stocks | 0 |

## Struktura jednostki (unit)

| Offset | Nazwa | Uwaga |
|--------|-------|-------|
| +0x14 | tribe | plemię |
| +0x18 | job | zawód (56 = smolarz) |
| +0x195 | flags[good] | "może produkować good" |
| +0x194 | building_flag? | |
| +0x1c | selected_good | good wybrany w UI |
| +0x15c | ? | flaga ustawiana przez patch 0x4a1c0 (+56 = job) |
| +0x21c | job_good_status[good] | 0, 0xb, 0xe, 0xc, 0xd |
| +0xb34 | building_idx | budynek, do którego przypisany |

## Kluczowe funkcje (znalezione)

| Adres | Nazwa | Co robi | Status |
|-------|-------|---------|--------|
| 0x409dc1 | FUN_00409dc1 | Kopiuje flagi plemienia do elementu (GOODS_A, GOODS_B, HOUSES_A, jobs) | ✅ Zrozumiana |
| 0x413e7b | FUN_00413e7b | Parser tribetypes.ini (zapis do rekordu plemienia) | ✅ Zrozumiana |
| 0x41531d | FUN_0041531d | Parser houses.ini (typy domów) | ✅ Zrozumiana |
| 0x44a0d9 | FUN_0044a0d9 | Ustawia unit+0x195[good] dla pracownika na podstawie job block | ✅ Zrozumiana |
| 0x44b226 | FUN_0044b226 | Menu produkcji pracownika (pętla towarów 1..0x42) | ✅ Zrozumiana |
| 0x44b2fa | FUN_0044b2fa | Ustawia status +0x21c dla goodów joba | ✅ Zrozumiana |
| 0x42da65 | FUN_0042da65 | Bramka: czy jednostka może produkować good | ✅ Zrozumiana |
| 0x42db20 | FUN_0042db20 | Czy good jest na liście job block | ✅ Zrozumiana |
| 0x42d848 | FUN_0042d848 | needforgood - czy jednostka ma surowce | ✅ Zrozumiana |
| 0x42d9a3 | FUN_0042d9a3 | Próg plemienia dla gooda | ✅ Zrozumiana |
| 0x4316f3 | FUN_004316f3 | Bramka budynku dla gooda (revmap) | ✅ Zrozumiana |
| 0x431f37 | FUN_00431f37 | Zwraca revmap[good] z rekordu domu | ✅ Zrozumiana |
| 0x43b305 | FUN_0043b305 | Odwołuje się do job block +0x14928 | ⚠️ Do zbadania |
| 0x455f86 | FUN_00455f86 | Aktualizacja plemienia | ⚠️ Do zbadania |
| 0x4cc99c | FUN_004cc99c | UI - buduje listę obiektów do wyświetlenia | ❌ Nie produkcja |
| 0x4cce2f | FUN_004cce2f | UI - buduje listę obiektów | ❌ Nie produkcja |
| 0x4cb028 | FUN_004cb028 | UI - buduje listę budynków/typów | ❌ Nie produkcja |
| 0x45c89e | FUN_0045c89e | Zarządzanie listą (4 wpisy, +0xaf4/+0xaf8) | ❌ Nie produkcja |

## BRAKUJĄCE - kod produkcji (do znalezienia)

Nie znaleziono funkcji, która:
1. Iteruje po instancjach budynków
2. Sprawdza czy budynek ma pracownika i towary wejściowe
3. Konsumuje input good (drewno) i tworzy output good (węgiel)

Kandydaci do sprawdzenia:
- Funkcje czytające +0x64 (stocks budynku): 0x405b27, 0x40caed, 0x412953, 0x42bb1c, 0x45c922, 0x4aa285, 0x4c198b, 0x4cb133, 0x4cca49, 0x4ccea4
- Funkcje czytające +0x60 (stock count): 0x478415, 0x478ab0, 0x47a920, 0x4b7d6d
- Funkcje z imm 0x66 (coal): 0x41ccec, 0x4283ec, 0x48da73

## Hipoteza główna

Produkcja w budynku może nie używać `unit+0x195[good]` wcale. Może być napędzana przez:
- `building+0x64` stocks + typ budynku + przypisany pracownik
- Recepturę producción z `houses.ini` (`logicproduction`)
- `jobBlock+0x330` (jobDefaultGood)

## Następne kroki RE

1. Przeszukać .text pod kątem kodu modyfikującego stocks budynku (+0x64) - write, nie tylko read
2. Znaleźć funkcję która konsumuje drewno (good 5) i tworzy węgiel (good 66)
3. Sprawdzić xrefs na `+0x64` i `+0x60` w kontekście zapisu
