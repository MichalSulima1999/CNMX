# HANDOFF 2026-10-26 — MAGAZYN/KATEGORIE: logika grupowania dóbr w magazynie

## 1. Cel sesji

Znaleźć i naprawić przyczynę, dla której węgiel (dobro 66) nie pojawia się w
magazynie/UI zapasów, oraz udokumentować logikę grupowania dóbr w magazynie.

## 2. Odkrycie (root cause)

**Panel budynku (magazynu)** `FUN_004a693b` w zakładkach 5 (zapasy) i 6
(szczegóły zapasów) oraz `FUN_004a76fd` (budowa zawartości zakładek) iterują
listę `logicstock` typu domu (`+0x60` licznik, `+0x64` wpisy po 12 B) i
**odrzucają dobra > 0x37 (55)** — filtr to `CMP reg,0x37` + `JBE/JG`.
Węgiel (66) nigdy nie trafiał na listę.

Dodatkowo: `logicstock 66 150 0` istniał tylko dla Kwatery Głównej
(`logictype 1`); budynki magazynowe `stock 00/01/02` (`logictype 7/8/9`) nie
miały wpisu dla dobra 66.

## 3. Co zmieniono

### Patche (EtapC)
`etapa_gen/patches_ext.h` — +4 patche `0x37 -> 0x42` dla panelu budynku/magazynu:

| RVA | Funkcja / zakładka |
|---|---|
| `0x000A7333` | `FUN_004a693b` zakładka 5 (zapasy) |
| `0x000A7434` | `FUN_004a693b` zakładka 6 (szczegóły zapasów) |
| `0x000A7EF7` | `FUN_004a76fd` zakładka 5 |
| `0x000A7FB3` | `FUN_004a76fd` zakładka 6 |

Tabela liczy teraz 683 wpisy (było 679).

### Dane
`Data/logic/houses.ini` — dodano `logicstock 66 45 0` / `70 0` / `120 0` do
`stock 00/01/02`. Backup:
`Data/logic/houses.ini.bak_warehouse_coal_20261026_222831`.
`ini_normalize.py` (dry-run): `plikow zmienionych 0`.

### Build
`build_all.bat` → `EtapC.dll` przebudowany i skopiowany do roota (gra była
zamknięta). Nowe opisy patchy obecne w binarce (sprawdzone).

## 4. Logika grupowania dóbr w magazynie (udokumentowana)

- **Kategorie dóbr** liczy `FUN_0045cbbe(good)` → 1..5 (0 = martwa gałąź).
  Używa jej okno targu/magazynu `FUN_004c7110`.
- **Nazwy kategorii** z zasobów tekstowych: `FUN_004e1b04(kategoria)` → grupa 5,
  id `0xdc..0xe2` (kategoria 6 = „wszystkie”).
- Okno targu (`FUN_004c6d91`/`FUN_004c7110`/`FUN_004c6e27`) filtruje listę
  po `FUN_0045cbbe(good) == +0x70` oraz flagę `*(char*)(good+0x1e0+tribe) != 0`.
- **Panel budynku/magazynu (`FUN_004a693b`) NIE używa kategorii** — wiersze
  idą w kolejności wpisów `logicstock` z `houses.ini` (brak grupowania).
- Kategorie widoczne w grze pochodzą z okna targu/wymiany, nie z panelu
  magazynu.

Węgiel (66) wpada do kategorii 5 („pozostałe”).

## 5. Otwarte tematy (niezrobione)

- **Okno targu (`FUN_004c7110`)** — pętli `0x4c742f/0x4c74cb/0x4c7543` nie
  rozszerzono, bo wymaga flagi `+0x1e0` (memset 0x38, tylko `0x1f..0x37`).
  Najpierw rozbudować tablicę `+0x1e0` i pętle ją wypełniające w `FUN_0044a0d9`.
- **Ikony/paleta** — `FUN_00415e8a` inicjalizuje paletę tylko dla dóbr 0..55
  (`iVar3 < 0x2CB1`, stride `0xD0`); rozszerzenie uznano za niebezpieczne.
- Weryfikacja w grze: czy węgiel pojawia się w zakładce zapasów i czy stan > 0
  po dostawie.

## 6. Jak zweryfikować

1. Uruchom grę przez `modlauncher.exe`.
2. `logs/etapc.log` → `patches applied: 683/683 ok`.
3. Panel Kwatery Głównej / budynku `stock 0x` → zakładka zapasów powinna
   pokazać „Węgiel” (ikona `good_stone`).
4. Wyprodukuj węgiel w chacie smolarza, zanieś do magazynu — stan „Węgiel”
   powinien być > 0.

## 7. Pliki źródłowe analizy

- `.ai/docs/re/RE-ANALYSIS-PART89-2026-10-26.md` — pełna analiza partia 89.
- `.ai/re_out_batch10/functions/0x4a693b.c`, `0x4a76fd.c`, `0x4a60a2.c`.
- `.ai/re_out_batch6/functions/0x4c7110.c`, `0x4c6d91.c`, `0x4c6e27.c`,
  `0x4c70cc.c`.
- `.ai/re_out_batch21/functions/0x45cbbe.c`.
- `.ai/re_out_batch13/functions/0x4e1b04.c`.
- `.ai/re_out_batch19/functions/0x41531d.c`, `0x415e8a.c`.
- `etapa_gen/patches_ext.h` (nowe patche na końcu listy).

## 8. Stan commitu

Zmiany niezacommitowane: `etapa_gen/patches_ext.h`, `Data/logic/houses.ini`
(pozagit), `EtapC.dll` (pozagitu), `.ai/docs/re/RE-ANALYSIS-PART89-…`,
`.ai/docs/HANDOFF-…`, `.ai/docs/INDEX.md`, `.ai/tmp/...` (artefakty skryptów).