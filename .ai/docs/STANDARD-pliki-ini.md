# Standard plików `.ini` — CnMod Extended (CNMX)

**Data:** 2026-10-22
**Narzędzie:** `.ai/scripts/ini_normalize.py` (dry-run domyślnie, `--apply` zapisuje)

## 1. Obowiązujący format

Każdy plik `.ini` w `Data\` i `CN.PLMOD\` musi mieć:

| Cecha | Wartość | Dlaczego |
|---|---|---|
| Kodowanie | **cp1250** (Windows-1250), bez BOM | Silnik czyta dane jako bajty jednobajtowe; oryginalne `.cif` dekodują się poprawnie jako cp1250. Pliki UTF-8 dają krzaki (`Ĺ‚`, `?`). |
| Końce linii | **CRLF** (`\r\n`), także po ostatniej linii | Pliki oryginalne są CRLF; mieszane EOL utrudnia diffy i bywa źródłem problemów przy edycji. |
| Znaki zastępcze | **0 × U+FFFD** | U+FFFD = bezpowrotnie utracona litera przy złej konwersji kodowania. |
| Podwójne kodowanie | **brak** (`M³yn` → `Młyn`) | Objaw: znaki `³ ¶ ¼ ¹ œ ¿ Â` w miejscu polskich liter. |

## 2. Co zostało naprawione (2026-10-22)

| Plik | Problem | Naprawa |
|---|---|---|
| `Data\text\pol\strings\gameobjects\goods.ini` | UTF-8, 103 × U+FFFD (37 wpisów) | odtworzone litery ze `goods.cif` (89 tokenów), zapis cp1250 |
| `CN.PLMOD\stringstext\gameobjects\houses.ini` | UTF-8, 43 × U+FFFD (18 wpisów) | odtworzone litery z `houses.ini.orig` + `houses.cif` (37 tokenów) |
| `CN.PLMOD\budynki12\houses\houses.ini` | 19 linii podwójnego kodowania (`Ferma byd³a`) | odwrócone `latin1 → cp1250` |
| `Data\text\pol\strings\gameobjects\experiences.ini` | brak końcowego CRLF | dodany |
| `CN.PLMOD\types\vehiclestype\jobgraphics.ini` | brak końcowego CRLF | dodany (plik poza gitem — `/CN.PLMOD/types/*` w `.gitignore`) |

Weryfikacja: 21/21 plików `.ini`, 0 × U+FFFD, 0 × BOM, 0 × mieszane EOL. Liczba linii i ID
`stringn` bez zmian — naprawa nie ruszyła treści ani struktury.

### Jak odtwarzane są litery

Uszkodzenie jest regularne: 1 znak U+FFFD = utracona litera (seria 2–3 znaków = tyle samo
sąsiadujących liter, np. `W??cznia` ← `Włócznia`). Narzędzie:

1. czyta tekst źródłowy **dla tego samego ID** (`*.orig` w tym samym katalogu albo `.cif`
   o tej samej nazwie przekonwertowany przez `mapper tools\cif2txt.exe`),
2. zamienia w tokenie każdą literę nie-ASCII na `?` i szuka tokenu o identycznym szkielecie
   w źródle,
3. jeśli szkielet nie pasuje (utracono więcej niż jedną literę, np. `Wół` → `W?`), dopasowuje
   wzorcem `.+` **tylko w obrębie tego samego ID**,
4. przy braku jednoznacznego kandydata **nie zgaduje** — zgłasza token do recenzji.

Dzięki temu zachowana jest treść moda (np. skrócone `Kamień` zamiast oryginalnego
`Nieobrobiony Kamień`), a odtwarzane są wyłącznie litery.

## 3. Znane pozostałości (świadome)

- `CN.PLMOD\budynki12\houses\houses.ini`: `gfxoverlaylandscape 2 0 0 0 "wonder semiramis schr`
  — nazwa assetu była uszkodzona już we wszystkich backupach (`*.orig`, `*.etapc.bak`,
  `*.broken.bak`); nie da się jej odtworzyć bez listy assetów. Usunięto tylko znaki
  niekodowalne w cp1250. Grafika i tak nie mogła się wczytać pod uszkodzoną nazwą.
- `Data\logic\goodtypes.ini`: duplikaty `type` 27/49/59/60 — to **treść, nie formatowanie**;
  wygrywa ostatni blok. Do decyzji osobno.
- `CN.PLMOD\types\weapons.ini`: audyt zgłasza „duplikaty" typów 1–21, ale bloki różnią się
  `tribetype` — **fałszywy alarm**.

## 4. Zasady na przyszłość

1. Pliki `.ini` edytuj **tylko** w cp1250 i CRLF. Nie otwieraj ich edytorem zapisującym UTF-8.
2. Po każdej zmianie danych uruchom `python .ai\scripts\ini_normalize.py` (dry-run) —
   powinno pokazać `plikow zmienionych 0`.
3. Nie „naprawiaj" U+FFFD zgadywaniem polskich znaków. Użyj źródła per-ID; jeśli źródła brak,
   zgłoś problem.
4. Backup przed zapisem: narzędzie tworzy `*.bak_format_<stamp>` obok pliku.
5. Gra musi być zamknięta przed nadpisaniem danych.
