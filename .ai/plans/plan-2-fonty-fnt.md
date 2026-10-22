# Plan implementacyjny P2 — Fonty: dekodowanie `.fnt` i skalowanie do HiDPI

> **STATUS (06.10.2026):** Etap 0–2 ✅ (format w 100% odwrócony; round-trip bajt-w-bajt
> identyczny). **Etap 3A (fonty 2× pixel) ODRZUCONY teście na żywo** — użytkownik:
> „czcionka się nie mieści i jest za duża, bardzo rozpikselowana” → pełny rollback
> na oryginały. **Etap 5 (TTF ×1.5 Tahoma) ✅ test na żywo POZYTYWNY**
> („Te fonty działają”), ale użytkownik poprosił o wariant **bliższy oryginału**.
> **Etap 6 (kontur ×1.25) ✅ ZAAKCEPTOWANY — test na żywo „Wygląda dobrze”:**
> `font08.fnt`/`font12.fnt` = wariant konturowy ×1.25 (marching squares na AA,
> supersampling ×16), height 8→10 / 12→15, szer. +24% / +20%.
> **Etap batch-2 (hypertext + briefingi) ✅ ZAINSTALOWANY (344 pliki):**
> font12 → h 12→15, fonthead16bld → h 14→18 (std.) / 16→20 (warianty modowe),
> font10/font_10 bez zmian; backupy `.fnt.orig` przy każdym pliku — **oczekuje
> testu na żywo** (credits/history/ingamehelp + briefings kampanii).
> **✅ Test batch-2 ZAAKCEPTOWANY („Jest OK”, 06.10.2026) — PLAN 2 ZAMKNIĘTY.**
> Wyjątek: `font10`/`font_10` pozostają oryginalne (decyzja użytkownika, font wąski).
> font10 zostaje oryginalny (font wąski — warianty bierne `font10_{tahoma,impact,impact125}.fnt`).
> Warianty w `Data\gui\fonts\`: `*_tahoma.fnt` (Etap 5), `*.fnt.orig` (oryginały),
> `font16/20/24.fnt` (inertne 2×). Poprawiony też błąd renderera (`advance = left + w + 1`).
> Specyfikacja formatu: `.ai\docs\format-fnt.md`; skrypty: `.ai\scripts\fnt_scale.py`,
> `.ai\scripts\fnt_ttf.py`, `.ai\scripts\fnt_contour.py`.

**Priorytet:** 2 z 4 (rozwiązuje główny problem „małego UI" na 1080p)
**Wysiłek:** tygodnie
**Zależności:** brak (niezależny od P1); warto zrobić **po** P1 dla spójnego testu wizualnego
**Powiązane wnioski:** `.ai\docs\wnioski-analiza-remaster.md` §6.3

## Cel

Gra nie ma globalnego mnożnika skali UI — fonty są stałorozmiarowe (font08/10/12 = 8/10/12 px),
więc na 1920×1080 tekst jest proporcjonalnie 2,4× za mały względem ekranu. Celem jest:
(1) pełny dekoder+enkoder formatu `.fnt`, (2) wygenerowanie skalowanych fontów (2×),
(3) integracja z grą tak, by tekst był czytelny na HiDPI bez rozjazdu layoutu.

## Dowody techniczne

- Pliki: `Data\gui\fonts\font08.fnt`, `font10.fnt`, `font12.fnt`, `fontdebug.fnt`
  (+ kopie `font10.fnt` w `Data\text\pol\hypertext\credits\fonts\` — ~26 265 B).
- Obserwowany nagłówek `font08.fnt` (little-endian u32):

  ```
  f5 03 00 00   00 00 00 00   df 00 00 00   08 00 00 00
  f4 03 00 00   00 00 00 00   00 00 00 00   e0 00 00 00
  9e 24 00 00   5d 06 00 00   ...
  ```
  **Potwierdzone znaczenie (06.10.2026):** `0x3f5`(1013) = *tag typu* „font" (parser `0x410624`),
  `0xdf`(223) = `fieldA` = zakres indeksów (count−1), `08` = interlinia, `0x3f4`(1012) = tag typu
  tablicy glifów, `0x249e`(9374) = długość danych RLE, `0x65d`(1629) = liczba wierszy.
  Pełna specyfikacja: **`.ai\docs\format-fnt.md`** (odwrócona, round-trip OK).
- Nie ma nigdzie w exe mnożnika skali ani dzielenia przez 800 → skalowanie musi wynikać z **nowych assetów**
  albo z patcha kodu rysującego tekst (patrz Etap 3).
- Layout jest rozdzielczościowo świadomy (dialogi centrowane `(w−500)/2`), więc **większy font mieści się
  w centrowanych dialogach**, ale może wylewać się z stałoszerokościowych widgetów (przyciski, listy).

## Zakres

- [x] Dekoder `.fnt` (nagłówek + mapa glifów + bitmapy znaków) — Python.
- [x] Enkoder (round-trip: decode → encode → bit-identyczny plik) — dowód poprawności formatu.
- [x] Generator skalowanych fontów (2×: 16/20/24 px) lub skala rysowania istniejących danych.
- [ ] Test integracji w grze (podmiana ✅ zrobiona — zostaje weryfikacja wizualna).

## Poza zakresem

- Zmiana rozkładu UI/HUD (P3).
- Nowe fonty w stylu graficznym (tylko skala).

## Etapy

### Etap 0 — Pełna inwentaryzacja fontów (0,5 dnia) ✅
- [x] Skrypt: znaleźć **wszystkie** `.fnt` w drzewie (`Data`, `CN.PLMOD`, `DataX`) + rozmiary.
      (UI: `Data\gui\fonts\*`; hypertext: `Data\text\pol\hypertext\{credits,history,ingamehelp}\fonts\*`;
      briefingi: `CN.PLMAPS\**\Fonts\*`; **brak** plików fontów w `CN.PLMOD`.)
- [x] Znaleźć w exe stringi ścieżek/fontów — tablica globalna `0x569aa0` =
      [font08, font10, font12, fontdebug], rejestracja `0x4e2514..0x4e254b`, loader `0x41074c` → `0x410624`.
- [x] Ustalić, których fontów używa HUD, a których hypertext — HUD/ GUI = `Data\gui\fonts`
      (bez nadpisania moda); hypertext/credits/briefing = własne kopie `.fnt` ładowane
      innymi xrefami loadera (`0x4d08f3`, `0x4d1b14`, `0x4d1b38`, `0x42505a`, `0x48fb5e`).

### Etap 1 — Dekodowanie formatu (2–5 dni) ✅
- [x] Parser nagłówka: zrzut pól dla 08/10/12 → `height` = 8/10/12 (interlinia), `fieldA`=223.
- [x] Tablica metryk: rekord 24 B × 224 glifów (`enc,left,top,w,h,rowBase`) — `advance = left+w+tracking+1`.
- [x] Sekcja bitmap: **RLE 8-bit** (skip/literal/0=EOF, wiersz = `startCol<<22|offset`) — render PNG
      `fnt_scale.py` (kontakty `fnt08_sheet.png`, `fnt12_sheet.png`).
- [x] Polskie znaki: kodowanie **CP1250**, `idx = bajt − 0x20` → zakres 0..223 = znaki 0x20..0xFF
      (łącznie z ą=0xE1…ż=0xBF); brakujące tylko idx 0 (spacja) i 128 (NBSP).
- [ ] **Kryterium wyjścia Etapu 1:** render PNG gotowy (`prev_*.png`) — porównanie ze zrzutem
      z gry = test użytkownika (Etap 4).

### Etap 2 — Round-trip i skaler (2–4 dni) ✅
- [x] Enkoder: re-encode **bajt-w-bajt identyczny** dla font08/10/12 (skrypt `plan2_decode.py`).
- [x] Skaler 2×: nearest (piksel → 2×2), `height×2`, `left/top/w/h×2`, `rowBase` przeliczony,
      `emptyRows`/`len(arr1)`/`rows` przeliczone; `fieldA`/`base`/`count` bez zmian.
- [x] Wygenerować `font16.fnt`, `font20.fnt`, `font24.fnt` (2× z 08/10/12) — walidacja:
      `decode(wynik) == nearest(decode(oryginał))` ✓ (skrypt `fnt_scale.py`).
- [x] Walidacja: renderer statyczny → PNG z polskim zdaniem
      (`prev_font08_orig.png`/`prev_font16.png`, `prev_font12_orig.png`/`prev_font24.png`).

### Etap 3 — Integracja (3–10 dni) — DWIE OPCJE
**Opcja A — podmiana istniejących plików (bez patcha exe):** ✅ wykonane 06.10.2026
- [x] Zamienić `font08/10/12.fnt` wersjami 2× (backupy `.orig` w `Data\gui\fonts\`).
      Dodatkowo `font16/20/24.fnt` zostają jako inertne kopie pod opcję B1.
- [x] **Test na żywo: NEGATYWNY** — 2× pixel → „za duża / nie mieści / rozpikselowana”;
      przelewania: przyciski/menu główne, listy/HUD. Rollback: `.orig` → `font*.fnt`
      (przywrócone 21 354 / 26 265 / 29 223 B). Przyczyny: skala 2× = **+91% szerokości**
      (skalują się też odstępy między literami) + bloki pikseli nearest-neighbour.
- [x] Kierunek naprawczy uzgodniony: **wariant TTF z antyaliasingiem ×1.5** (Etap 5)
      zamiast pixel-art 2×.

**Opcja B — patch kodu rysującego (nieaktualna — wariant TTF działa na ścieżce A):**
- [ ] Znaleźć funkcję rysowania tekstu (xref do loadera fontu / pętla blitu glifu — szukać po
      `GetGUIWidth` xrefs w kodzie HUD oraz po wywołaniach loadera `.fnt`).
- [ ] Dodać skalę: albo wybór większego pliku wg rozmiaru (8→16, 10→20, 12→24 — **najmniejszy patch:
      zmiana tablicy wskaźników/nazw plików**), albo mnożnik przy blit-gu.
- [ ] Minimalna wersja B1: **podmiana nazw fontów w tablicy wyboru** (jeśli istnieje tablica
      `font08/font10/font12`) → gra sama wczyta większe pliki, zero zmian w pętlach renderujących.
- [ ] Weryfikacja pozycji: centrowane dialogi przesuwają się poprawnie (`x=(w−500)/2` — jeśli widget
      rozmiaru 500 dostanie większy tekst, trzeba zweryfikować centrowanie tekstu wewnątrz widgetu).

**Rekomendacja:** Etap 3A jako szybki pilot (godziny), potem 3B1 jeśli tekst się nie mieści.

### Etap 4 — Weryfikacja (1 dzień)
- [ ] Zrzuty: menu, dialog NPC, lista budynków, HUD gry, credits, tekst misji.
- [ ] Matryca rozdzielczości: 1280×720, 1920×1080, 2560×1440 (i 800×600 — brak regresji!).

### Etap 5 — TTF re-raster z antyaliasingiem (06.10.2026) ✅ zbudowany — test na żywo
Po odrzuceniu 2× pixel (Etap 3A): re-rasterizacja glifów z TTF zamiast skalowania bitmap.
- [x] Ustalić semantykę wartości pikseli: palety `Data\gui\palettes\font_*.pcx` to pełne
      rampy 256-kolorowe → format obsługuje pełne AA (nie tylko oryginalne {128,160,192,255}).
      Budujemy z progiem `INK_MIN=40` (poniżej → przezroczystość, brak danych w RLE).
- [x] Poprawka renderera `fnt_scale.py`: `advance = left + w + 1` (było `left + len(mat) + 1`
      = wysokość — przekłamywało szerokości podglądów o ~30–90%).
- [x] Skrypt `.ai\scripts\fnt_ttf.py`: rasteryzacja TTF (PIL) → wspólne metryki (`T` = max
      ink nad baseline, `D` = max ink pod), `height = T+D` (najcieńsza interlinia bez
      nachodzenia glifów), enkoder `encode_glyphs`, walidacja round-trip (count/fieldA/raw
      enc=0 bez zmian, mat identyczne, brak wartości < 40).
- [x] **Zainstalowane w `Data\gui\fonts\`:**
  | plik | krój | rozmiar | height | szer. testu vs oryginał |
  |---|---|---|---|---|
  | `font08.fnt` | Tahoma 14 px (x 5→7.7, ×1.54) | 14 | 8→18 | +16% |
  | `font12.fnt` | Tahoma 22 px (x 8→12.1, ×1.51) | 22 | 12→26 | +23% |
  | `font10.fnt` | **oryginał, bez zmian** | — | 10 | 0% |
- [x] Font10 to font **wąski** (~27% węższy od font12 przy tej samej wysokości) — ×1.5
      w normalnym kroju = +69% (prawdopodobne przelewanie w listach/HUD). Warianty bierne
      (do podmiany jednego pliku): `font10_tahoma.fnt` (+69/75%), `font10_impact.fnt`
      (Impact 18 px, ×1.46, +44/46%), `font10_impact125.fnt` (Impact 15 px, ×1.22, +25/27%).
- [x] Test na żywo Tahoma: przyciski/menu, listy/HUD — pozytywny („Te fonty działają”),
      ale prośba o wariant bliższy oryginału → Etap 6.
- [ ] Po akceptacji UI: Etap batch-2 (fonty hypertext `Data\text\pol\hypertext\**` + briefingi).

### Etap 6 — wariant konturowy ×1.25 (06.10.2026) ✅ ZAAKCEPTOWANY
Zamiast skalowania bitmap (nearest = bloki 1–2 px, szorstkie krawędzie): rasteryzacja
oryginalnych konturów w skali ×1.25 z pełnym AA — oryginalne kształty liter, ostre krawędzie.
- [x] Skrypt `.ai\scripts\fnt_contour.py` (domyślnie tylko podglądy; `--install` zapisuje):
  1. **interpolowany marching squares** na wartościach AA glifu — izolinia `127.5`
     = geometria krawędzi przy 50% pokrycia (linia w połowie piksela; przypadki niejednoznaczne
     5/10 rozwiązywane średnią środkową),
  2. skalowanie konturów ×1.25 z dokładnością ułamkową,
  3. rasteryzacja: supersampling **×16** + box-downsample → pełne 216 wartości tuszu w rampie
     `[40…255]` (próg `INK_MIN=40`, jak w `fnt_ttf.py`),
  4. pary `(left, top, w, h)` = nearest ×1.25 → advance/identyczny layout co podgląd `prev_px125_*`.
- [x] Walidacja: nagłówek/count/height bez zmian, round-trip decode(encode) == macierze,
      wymiary = nearest, brak wartości < 40.
- [x] Podglądy: `prev_contour_font{08,12}.png` (+`_z2`), porównanie z nearest ×4
      `cmp125_font{08,12}_z4.png`.
- [x] **Instalacja + test na żywo: POZYTYWNY** („Wygląda dobrze”):
  | plik | height | szer. testu vs oryginał | wariant |
  |---|---|---|---|
  | `font08.fnt` | 8→10 | +24% | kontur ×1.25 (aktywny) |
  | `font12.fnt` | 12→15 | +20% | kontur ×1.25 (aktywny) |
  | `font10.fnt` | 10 | 0% | oryginał |
- Kopie w `Data\gui\fonts\`: `font{08,12}_tahoma.fnt` (Etap 5), `font{08,12}.fnt.orig` (oryginały).

### Etap batch-2 — hypertext + briefingi (06.10.2026) ✅ ZAINSTALOWANY
Skrypt `.ai\scripts\fnt_batch2.py` (domyślnie inwentaryzacja + podglądy; `--install` zapisuje).
Zakres: `Data\text\pol\hypertext\{credits,history,ingamehelp}\fonts\` + `CN.PLMAPS\**\*.fnt`.
- [x] Inwentaryzacja: **484 pliki `.fnt` = 14 unikalnych wariantów** (grupowanie nazwa+md5).
- [x] **Naprawka enkodera `fnt_scale.encode_glyphs`:** oryginał **pomija tylne przebiegi zer**
      (kodowanie do ostatniego piksela tuszu, bez skipa) — wcześniej RT-FAIL na wszystkich
      oryginałach; po poprawce round-trip font08/10/12 = **bajt-w-bajt OK**. Kontury GUI
      przebudowane poprawionym enkoderem.
- [x] Warianty modowe (19757/17840/29346 font12, 25581/23016/41535 fonthead, font10 16689/15083)
      mają nietypową strukturę (dodatkowy wiersz na glif, nieciągłe `rb`, cieńsza waga kroju,
      RIV: pudełka h=17>height) — dekod zweryfikowany renderem (litery czytelne); nowe pliki
      zapisywane w standardowym layoucie z twardym round-tripem nowego pliku.
- [x] **Instalacja: 344 pliki** (344 backupy `.fnt.orig`):

  | plik | warianty (rozmiar→kopia) | height | kopii |
  |---|---|---|---|
  | `font12.fnt` | 29223 std + 19757/17840/29346 mod | 12→15 | 172 |
  | `fonthead16bld.fnt` | 41369 std + 41535/25581/23016 mod | 14→18 / 16→20 | 172 |
  | `font10.fnt`, `font_10.fnt` | 7 wariantów | **bez zmian** | 148 |
- [ ] Test na żywo: credits, historia kampanii, in-game help, briefings (kampania + mody).

## Kryteria akceptacji

- [x] `.fnt` w pełni opisany (dokumentacja formatu w `.ai\docs\format-fnt.md`).
- [x] Round-trip bit-identyczny (font08/10/12).
- [ ] Tekst 2× większy, czytelny na 1920×1080 (test na żywo).
- [ ] Brak wylewania tekstu poza widgety (spójność: przyciski, listy, dialogi).
- [x] Polskie znaki (ą ę ć ł ń ó ś ź ż) renderowane poprawnie (renderer PNG; CP1250 → idx < 224).
- [x] Oryginalne fonty zachowane (`.orig`).

## Ryzyka

| Ryzyko | Łagodzenie |
|---|---|
| Format nieznany / RLE-owy | iteracja na renderze wizualnym; wzorce z innych gier Funatics (Cultures 1/2/3 używają `.fnt` — szukać w `mapper tools`) || Tekst nie mieści się w widgetach | Opcja B1 + eventualne powiększenie stałych `500×420` w dialogach (patch stały layout → łącz z P3) |
| Hypertext (credits/kampania) używa innej ścieżki | Etap 0 — pełna inwentaryzacja xref-ów |
| Skalowanie zniszczy pixel-art | nearest 2× bez interpolacji; ewentualnie ręczne doglądy |

## Materiały odniesienia

- Pliki: `Data\gui\fonts\font08.fnt` (21 354 B), `font10.fnt` (26 265 B), `font12.fnt` (29 223 B),
  `fontdebug.fnt` (13 161 B); kopia `Data\text\pol\hypertext\credits\fonts\font10.fnt`.
- Skrypty: `.ai\scripts\fnt_scale.py` (parser+skaler+renderer), `.ai\scripts\fnt_install.py`
  (podmiana z backupem), `.ai\scripts\plan2_decode.py` (walidacja round-trip).
- Adresy: loader fontu `0x41074c` → parser typów `0x410624` (typ 1013 = font);
  GUI init `0x49F52B`; gettery `GetWidth=0x478479`, `GetHeight=0x47848A`.
