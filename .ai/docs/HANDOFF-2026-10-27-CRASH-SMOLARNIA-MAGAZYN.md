# HANDOFF 2026-10-27 — crash po kliknięciu smolarni + prawdziwe źródło danych magazynu

## Streszczenie

Dwa niezależne błędy, oba naprawione:

1. **Crash `AV: READ @ 0xFFFFFF80` przy kliknięciu budynku** — cztery „wewnętrzne"
   patche `0x38 → 0x43` (`0x000A8022`, `0x000A80FC`, `0x000A81FA`, `0x000A82C6`)
   trafiały w **środek cudzych instrukcji**. Usunięte z `etapa_gen/patches_ext.h`.
2. **„W magazynie dalej nic nie ma"** — edytowaliśmy `Data/logic/houses.ini`,
   a gra czyta **`CN.PLMOD/types/houses.ini`** (`"cn.plmod\types\houses.ini"` @ VA
   `0x0050055C`, otwierane w `FUN_0041531d`). Dopisane `logicstock 66` do
   `stock 00/01/02` w pliku runtime.

## 1. Crash — root cause

`logs/crash.txt`:

```
addr_va=0x004a82c5 addr_rva=0x000A82C5
AV: READ @ 0xFFFFFF80
bajty@EIP: 8B 43 80 7B 74 00 0F 84 7A 01
EBX=0x00000000
```

Wcześniej policzono `0x004A82C5 − 0x400000 = 0xA2C5` — **błędnie**. Poprawnie
`0x000A82C5`, czyli dokładnie miejsce patcha `0x000A82C6`.

Oryginał w tym miejscu:

```
0A82C5  8B D9            MOV EBX,ECX
0A82C8  80 7B 74 00      CMP BYTE [EBX+0x74],0
```

`0xD9` to **ModRM**, nie imm8 porównania. Po podmianie na `0x43`:

```
0A82C6  8B 43 80         MOV EAX,[EBX-0x80]     ; EBX=0 -> odczyt 0xFFFFFF80
```

To wyjaśnia adres i `EBX=0` z logu. Funkcja `0x0A82BC` rysuje panel **każdego**
budynku — dlatego crash wychodził po kliknięciu smolarni.

Pozostałe trzy adresy też były zgadnięte i też były złe:

| RVA | bajt | prawdziwa instrukcja |
|---|---|---|
| `0x000A8022` | `0x00` | imm8 w `AND DWORD [EBP-4],0` |
| `0x000A80FC` | `0x18` | imm8 w `SUB EAX,0x18` |
| `0x000A81FA` | `0x8B` | opcode `MOV ECX,ESI` |
| `0x000A82C6` | `0xD9` | ModRM `MOV EBX,ECX` |

**Lekcja:** EtapC loguje `patch N ok` także wtedy, gdy podmienia bajt w dowolnym
miejscu. `N/N ok` **nie jest** weryfikacją adresu. Przed dopisaniem patcha trzeba
odczytać bajt z pliku i sprawdzić, że zgadza się z oczekiwanym.

## 2. Ile filtrów ma panel magazynu? Cztery

Dekompilator pokazywał `if (iVar7 < 0x38)` „wewnątrz pętli" jako osobny warunek —
to **ten sam** test, który na wejściu pętli kompiluje się jako `CMP reg,0x37` + `JG`.
Skan `.text` daje dokładnie 4 trafienia w obu funkcjach:

| `CMP` @ RVA | imm8 @ RVA (patch) | funkcja / zakładka |
|---|---|---|
| `0x000A7331` | `0x000A7333` | `FUN_004a693b` zakładka 5 |
| `0x000A7432` | `0x000A7434` | `FUN_004a693b` zakładka 6 |
| `0x000A7EF5` | `0x000A7EF7` | `FUN_004a76fd` zakładka 5 |
| `0x000A7FB1` | `0x000A7FB3` | `FUN_004a76fd` zakładka 6 |

Wszystkie cztery mają już patch `0x37 → 0x42` (`<=66`). **Nic więcej nie trzeba.**

## 3. Zły plik `houses.ini`

| Plik | Rola |
|---|---|
| `CN.PLMOD/types/houses.ini` | **czytany przez grę** (runtime) |
| `Data/logic/houses.ini` | kopia źródłowa z markerami `<CULTURES_CIF_BEGIN/END>` |

Dopisane 26.10 `logicstock 66 45/70/120 0` trafiły tylko do `Data/logic`.
Stan bloków w pliku runtime **przed** poprawką:

| `debugname` | `logictype` | stock | dobro 66 |
|---|---|---|---|
| `headquarters` | 1 | 50 | tak (od 19.10) |
| `stock 00` | 7 | 49 | **nie** |
| `stock 01` | 8 | 49 | **nie** |
| `stock 02` | 9 | 49 | **nie** |
| `work charcoal burner` | 57 | 2 | tak |

Dlatego Kwatera Główna była blokowana tylko filtrem kodu, a **budynki magazynowe
nie miały węgla w ogóle**.

### Zmiana danych

`CN.PLMOD/types/houses.ini` — po `logicstock 55 <limit> 0` w każdym bloku:

```
stock 00 (linia 164):  logicstock 66 45 0
stock 01 (linia 224):  logicstock 66 70 0
stock 02 (linia 284):  logicstock 66 120 0
```

* backup: `CN.PLMOD/types/houses.ini.bak_warehouse_coal_20261027_143145`
* 17416 → 17477 B, cp1250, CRLF 943, 0 × samo-LF, brak BOM, 0 × U+FFFD
* `python .ai\scripts\ini_normalize.py` (dry-run): `plikow zmienionych 0`

## 4. Układ wpisu `logicstock` (potwierdzony w `FUN_0041531d`)

`house_type`: stride `0x624`, baza `0x5113A0`.

| Offset | Znaczenie |
|---|---|
| `+0x60` | liczba wpisów |
| `+0x64` | wpisy po 12 B: `+0` good, `+4` limit (max 1000), `+8` flaga bool |
| `+0x37C` | `revmap[good]` = indeks wpisu (kolizja z `logicproduction` @ `+0x484`) |

Parser: `count != 0x42` (max 66) oraz `good < 0x43` (66 wchodzi).
Trzecia liczba w `logicstock` = flaga; `0` jest normalne (tak mają wszystkie dobra
w magazynie). Rysowanie wiersza sprawdza `CMP BYTE [entry+8],0`.

## 5. Stan techniczny

* `etapa_gen/patches_ext.h`: usunięto 4 błędne wpisy, `PATCH_COUNT` = **683**.
  Komentarz przy wpisach `MAGAZYN …` zawiera ostrzeżenie „NIE PRZYWRACAĆ".
* `EtapC.dll`: 97280 B, sha256 `eab82b61a4f636d3…`, skopiowany do roota przez
  `etapc\build.bat` (`== OK ==`).
* `EtapC.dll` w rootcie zawiera 4 opisy `MAGAZYN FUN_004a…`, **zero** wystąpień
  `wewnętrzny filtr` / `iVar7<0x38`.
* Sprzątnięte śmieci z roota → `G:\Games\CnMod-backups\_leftover_20261027\`:
  `EtapC_new.dll`, `EtapC_original.dll`, `EtapC_patched.dll`, `EtapC_tmp.dll`.
  W rootcie zostały tylko: `EtapC.dll`, `EtapD.dll`, `cnmod_hook.dll`, `DDraw.dll`,
  `gedx8musicdrv.dll`.

## 6. Do sprawdzenia w grze (użytkownik)

1. Uruchomić przez `modlauncher.exe`, w `logs/etapc.log` ma być `patches applied: 683/683 ok`.
2. **Klik na smolarnię — nie crashuje.**
3. Magazyn (`stock 00/01/02`) → zakładka zapasów → wiersz „Węgiel".
4. Kwatera Główna → zakładka zapasów → wiersz „Węgiel".
5. Dostarczyć węgiel → wartość > 0.

Jeśli wiersz się pojawi, ale bez ikony — sprawdzić `gfxgood 66`
(tooltip smolarni używa tego samego zasobu, więc ikona powinna być).

## 7. Otwarte / następne

* Okno targu (`FUN_004c7110`) nadal nie pokaże węgla — potrzebna tablica
  dostępności `+0x1e0` (`memset 0x38`, wypełniane tylko dla `0x1f..0x37`).
* `Data/logic/houses.ini` brakuje `logicworker 24 1` (smolarz), które jest w runtime
  — rozjazd z 19.10. Do wyrównania przy okazji, nie ruszać bez potrzeby.
* Ustalić, czy `Data/logic/*` jest nadpisywane przez `Edytor podstawowy.exe`
  (markery CIF) — jeśli tak, to źródłem prawdy jest `Data/logic` + repack, a nie
  edycja runtime.
