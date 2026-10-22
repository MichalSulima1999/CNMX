# Wnioski z analizy: „prosty remaster" gry Cultures (mod CN.PLMOD)

**Data analizy:** 2026-10-06
**Zakres:** wyłącznie analiza statyczna (żadne pliki gry nie zostały zmodyfikowane, nic nie uruchomiono)
**Katalog badawczy:** `G:\Games\CnMod 1.2` (~13 400 plików, 982 MB)

---

## 1. Metoda i narzędzia

| Narzędzie | Zastosowanie |
|---|---|
| Python 3.11 + `pefile` | nagłówki PE, sekcje, xref-y, mapowanie VA→offset |
| Python 3.11 + `capstone` (5.0.9) | disasembler x86 (32-bit) |
| Skrypty pomocnicze | `C:\Users\Michael1099\AppData\Local\Temp\opencode\` — m.in. `pe_scan.py`, `str_scan.py`, `cmp_sec.py`, `xref_ui.py`, `ui_consts.py`, `ui_render.py`, `ts_full.py`, `present.py`, `getwh.py`, `guiinit.py`, `guiwh_xr.py`, `arith.py`, `stretch_users.py` |

Ghidra/radare2/IDA niedostępne — analiza prowadzona ręcznie przez disasembler + xref-y. Wszystkie adresy w tym dokumencie to adresy wirtualne `CN.PLMOD.exe` (ImageBase `0x400000`).

---

## 2. Co jest w katalogu

- **Gra:** Cultures / Northland (Funatics) — oryginalny exe gry pod nazwą `CN.PLMOD.exe` (`OriginalFilename=Game.exe`, `Product=Cultures`, copyright 2002).
- **Mod:** Cultures Nation (culturesnation.pl) — dane w `CN.PLMOD\` (nowe budynki, bronie, plemiona, kampanie, polskie teksty, loadscreeny 1440×900), ~120 map w `CN.PLMAPS\` i `usermaps\`.
- **Edytory:** `Edytor podstawowy.exe` i `Remik's Editor.exe` (identyczne `.text`/`.rdata`, różnice tylko w `.data` — 348 bajtów ścieżek — i `.rsrc`).
- **Narzędzia społeczności:** `mapper tools\` (cif2txt, c2mConverter, konwertery PyInstaller, BMD Tool, Zachowanie, dokumentacja PDF/listy warunków i rezultatów skryptu misji).
- **Ustawienia:** `Saves\opt_glob.ini` → `gfx_screen_width 1920 / gfx_screen_height 1080 / gfx_screen_depth 16`; `Game.ini` (zakomentowane `// gfx_fullscreen 0`).

## 3. Dowody wcześniejszych prac społeczności (RE już zrobione)

| Dowód | Znaczenie |
|---|---|
| `CN.PLMOD.exe` ma data kompilacji PE **2005-07-18**, a string `Build date Apr 30 2019 15:25:18` w sekcji `.data` | binarka **spatchowana hex-edycją** (długości stringów identyczne: `Jul 18 2005 13:28:53` = `Apr 30 2019 15:25:18`) |
| Ścieżki `data\logic\housetypes.ini` (25 B) → `cn.plmod\types\houses.ini` (25 B), `data\logic\weapontypes.ini` (26) → `cn.plmod\types\weapons.ini` (26) — podmiany „in place" w `.data` | **przekierowanie danych gry do folderu moda** przez patch binarki |
| Edytory: „Spolszczenie by ReMik, specjalnie dla ... CulturesNation.pl" | podmiana zasobów + ścieżek |
| `c2mConverter.exe` (Java) zawiera metody **`decodeCif` / `createIni`** | **format `.cif` jest już odwzorowany** (round-trip CIF→INI) |
| `cif2txt.exe` (UPX), `BMD Tool.exe` (.NET 2018), `c4_to_cnmod.exe`/`cnmod_to_c4.exe` (Python 3.7), `Zachowanie.exe` | rozszyfrowane: `.cif`, `.bmd`, `.c2m`, formula Behavior |
| `mapper tools\Lista warunków.txt`, `Lista rezultatów.txt`, PDF-y | **udokumentowany DSL skryptu misji** |

**Wniosek: nie zaczynamy od zera — formaty danych i języki skryptów są już odtworzone przez społeczność.**

## 4. Kwestie prawne

- Analiza i dekompilacja dla interoperacyjności: dozwolone (dyrektywa UE 2009/24/EC, art. 5–6).
- **Nie dystrybuować** oryginalnych exe/assetów razem z własnymi narzędziami — poprawny model: narzędzia czytają instalację gracza.
- Odtworzone formaty (opisane z analizy) są wolne.

---

## 5. Werdykt: czy „prosty remaster" jest możliwy? — TAK

Silnik **nie blokuje wysokich rozdzielczości**. Remaster jest realny na poziomie assetów + drobnych patchy; pełny remake nie jest potrzebny.

### Poziomy
- **P0 (dni):** podmiana assetów — bez RE.
- **P1 (tygodnie):** fonty `.fnt`, proporcje teł — lekkie RE.
- **P2 (miesiące):** skalowanie HUD, wrapper DirectDraw — średnie RE.
- **P3 (lata):** pełny remake — **niepotrzebny do remastera**.

---

## 6. Wynik analizy UI / rozdzielczości (punkty dowodowe)

### 6.1 Rozdzielczość jest „wolna" — żadnego patcha nie trzeba
- Odczyt `gfx_screen_width/height/depth` z INI w funkcji `0x401000` — domyślne `0x320×0x258` (800×600), zakres do `0x2710` (10000), walidacja i zapis w `0x4E1012+` (format `gfx_screen_width %d` @ `0x50BC44`).
- Struktura display: konstruktor `0x4787CB` — `+0x14=w (800)`, `+0x18=h (600)`, `+0x1c=depth (16)`, `+0x20/24=640/400`, `+0x2c/30=1600/1200`.
- Gettery: `GetWidth=0x478479`, `GetHeight=0x47848A`, `GetDepth=0x4784BF`.

### 6.2 Tła są rozciągane do pełnego ekranu (nearest-neighbour)
- **`0x40D507` = software'owy stretch**: wiersz-pikselowa pętla z `idiv`:
  `srcY = srcH·y / dstH`, `srcX = srcW·x / dstW` (odczyt piksela źródłowego, zapis do celu).
- **3 miejsca użycia** (potwierdzone przez skan `call rel32`):
  1. `0x40264A` — **titlescreen/loadscreen**: loader `0x402583` czyta ścieżki `cn.plmod\pictures\bitmaps\titlescreen.bmp` (`0x4FE2F4`) / `loadscreen.bmp` (`0x4FE2C8`), tworzy powierzchnię **o rozmiarze ekranu** (ctor `0x40C634` z `GetWidth/GetHeight` @ `0x402624–0x402634`), rozciąga tło, prezentuje przez `0x4787B3` + flip `0x479195` (×4, Sleep 10 ms).
  2. `0x402CC5` — **tło menu** (`[esi+0xd8]` → `[esi+0xdc]`; `[esi+0xd8]` = `titlescreen.bmp`, loader `0x402ed1`, potem blit na display).
  3. `0x49033B` — efekt przejścia/fade (skalowanie całej powierzchni ekranu, pętla z krokiem `−0x64`) — **nie jest assetem**.
- **HUD nie jest skalowany** — normalny blit natywny `0x47B0D7` + memcpy wierszowe `0x411327`.
- **Konsekwencja:** assety 800×600 (4:3) i 1440×900 (16:10) są rozciągane bez zachowania proporcji na 16:9 → **deformacja + blokowanie (nearest)**.

### 6.3 UI jest świadome rozdzielczości, ale bez globalnego mnożnika skali
- GUI dostaje prawdziwe wymiary: `0x49F52B` zapisuje `[0x569264]=w`, `[0x569268]=h`, `[0x56926c]=depth` i tworzy root widget `0x476643(w,h,format)`.
- **35 xref-ów do GUI width** — układ liczony względem krawędzi ekranu:
  - `x = (w − 500)/2`, `y = (h − 420)/2` — **centrowane dialogi** (wzorzec w ~15 miejscach: `0x4A39C4`, `0x4A510C`, `0x4ADF7D`, `0x4BE6E5`, `0x4C3D1E`…),
  - `x = w − 140`, `y = h − 600` — panel przy prawej/dolnej krawędzi (`0x4A8851`, push `0x258`/`0x8c`),
  - `x = w − 260`, `y = h − 340` (`0x4B0770`), `w − 160`, `w − 200`, `w − 240` — elementy HUD,
  - gettery `GetGUIWidth=0x4A8845`, `GetGUIHeight=0x4A884B` (3 wywołania każde — kod HUD).
- Pasek postępu na titlescreen: `rect((w−84)/2, h−6, 84, 4)` — **centrowany względem ekranu**, nie bitmapy (`0x402690`).
- **Nie ma nigdzie mnożnika skali** (żadnego dzielenia przez 800) → nie istnieje „UI scale"; fonty i grafiki paneli są **stałorozmiarowe** (font08/10/12 = 8/10/12 px) → na 1080p UI jest małe, choć poprawnie umieszczone.

### 6.4 Assety tła w grze (do P1)
| Plik | Rozmiar | Uwaga |
|---|---|---|
| `CN.PLMOD\pictures\bitmaps\loadscreen.bmp`, `titlescreen.bmp` | 1440×900, 24 bpp | wersje moda (16:10) — rozciągane na 16:9 |
| `Data\gui\menubgg.bmp`, `Data\gui\lang\pol\pictures\{loadscreen,menubg,titlescreen}.bmp` | 800×600, 16 bpp | **martwe — nie ładowane przez exe** (brak stringów; tłem menu jest titlescreen) |
| `DataX\Pictures\post00.bmp` | 1440×900, 24 bpp | sekwencja po misji — **też rozciągana** (ten sam `[esi+0xd8]`) |
| `datax\pictures\pre00.bmp`, `datax\pictures\%s%2.2d.bmp` | — | **nie istnieją** na dysku → loader pomija |
| `DataX\Pictures\post00.bmp` | 1440×900, 24 bpp | loader akceptuje 24 bpp ✅ |
| `Data\gui\bitmaps\*.pcx` (bg, buttons…) | 300×300, 8 bpp | kafle widgetów — **nie są rozciągane** |

---

## 7. Rekomendowane priorytety (plany w `.ai\plans\`)

| # | Priorytet | Wysiłek | Plik planu |
|---|---|---|---|
| 1 | Tła w proporcjach 16:9 (wymiana assetów; opcjonalnie letterbox w `0x40d507`) | dni–tygodnie | `plan-1-tla-16-9.md` |
| 2 | Fonty: dekodowanie `.fnt` + skalowanie/regeneracja | tygodnie | `plan-2-fonty-fnt.md` — **w toku: format odwrócony, fonty 2× zainstalowane, test** |
| 3 | Skalowanie HUD (globalny mnożnik / patche stałych layoutu) | miesiące | `plan-3-skalowanie-hud.md` |
| 4 | Wrapper DirectDraw/D3D8 (16-bit → nowoczesny present) | miesiące | `plan-4-wrapper-ddraw.md` |

Kolejność uzasadniona: P1 daje największy efekt wizualny przy najniższym ryzyku, P2 rozwiązuje główny problem „małego UI", P3 i P4 są droższe i zależne od wniosków z P1–P2.

## 8. Otwarte pytania (do kolejnej analizy)

1. ~~Kto ładuje tło menu „menubg"~~ — **ROZWIĄZANE**: `menubg.bmp` NIE jest ładowane przez exe (jedyne stringi `.bmp` w binarce: `loadscreen`, `titlescreen`, `datax\pictures\post00/pre00`, `datax\pictures\%s%2.2d`, `screenshots\...`, `mapshots\...`). Tłem menu jest **`titlescreen.bmp`** — loader `0x402ed1` wczytuje go do `[esi+0xd8]`, a funkcja z call-site `0x402CC5` rozciąga `[esi+0xd8]` na powierzchnię `[esi+0xdc]` (pełny ekran). Pliki `Data\gui\menubg.bmp`, `menubgg.bmp`, `Data\gui\lang\pol\pictures\*.bmp` są **martwe** (pozostałości po oryginalnej grze).
2. Site `0x49033B` (intro) to **efekt przejścia/fade** — skaluje całą powierzchnię ekranu (pętla `esi −= 0x64`, procent = `imul/div 0x64`), **nie** asset do podmiany.
3. Trzeci loader: `datax\pictures\post00.bmp` (istnieje, też 1440×900) i `pre00.bmp` / `%s%2.2d.bmp` (**nie istnieją** na dysku → loader pomija sekwencję i zostaje titlescreen).
2. ~~Dokładny format `.fnt`~~ — **ROZWIĄZANE (06.10.2026)**: pełna specyfikacja
   (tagi typów 1013/1012/1001, rekord 24 B, RLE skip/literal, `idx = bajt − 0x20`, CP1250,
   `advance = left + w + tracking + 1`, interlinia = pole `height`) w
   **`.ai\docs\format-fnt.md`**; round-trip bajt-w-bajt OK, fonty 2× zainstalowane (Etap 3A).
3. Czy kamera świata zwiększa widoczny obszar przy wyższej rozdzielczości (render world view) — dotąd nie analizowane.
4. Mapowanie myszy (1:1 czy przeskalowane) — prawdopodobnie 1:1 (spójne z layoutem w pikselach ekranu), do weryfikacji.
5. Próba na żywo: start gry na 1920×1080 i zrzuty ekranu (deformacja teł, wielkość UI).
