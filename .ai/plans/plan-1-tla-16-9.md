# Plan implementacyjny P1 — Tła w proporcjach 16:9 (bez deformacji)

**Priorytet:** 1 z 4 (najwyższy: najwyższy efekt / najniższe ryzyko)
**Wysiłek:** dni (faza assetów) + opcjonalnie tygodnie (faza letterbox)
**Zależności:** brak — można zacząć natychmiast
**Powiązane wnioski:** `.ai\docs\wnioski-analiza-remaster.md` §6.2, §6.4

> **STATUS (06.10.2026): ✅ PLAN ZAMKNIĘTY** — Etap 0 ✅, Etap 1 ✅, test użytkownika ✅ („jest dobrze").
> Faza B (letterbox) **odroczona** — niepotrzebna przy grze na 16:9; wrócić, jeśli użytkownik będzie grał
> na proporcjach ≠ 16:9 (21:9, 4:3). Kryteria akceptacji Fazy A spełnione.

## Cel

Gra rozciąga tła do pełnego ekranu **bez zachowania proporcji** (nearest-neighbour, `0x40D507`) — obrazy 4:3 (800×600) i 16:10 (1440×900) są zniekształcone na 16:9. Celem jest dostarczenie teł w proporcjach docelowych, tak by rozciąganie było albo tożsame z proporcjami (0 deformacji), albo kontrolowane (letterbox).

## Dowody techniczne (z analizy statycznej)

- Stretch: `0x40D507` — `srcX = srcW·x/dstW`, `srcY = srcH·y/dstH` (pętla pikselowa z `idiv`); **ignoruje aspect ratio**.
- Miejsca użycia (3 call-sites, `call rel32`):
  1. `0x40264A` — titlescreen/loadscreen (loader `0x402583`, ścieżki `cn.plmod\pictures\bitmaps\titlescreen.bmp` @ `0x4FE2F4`, `loadscreen.bmp` @ `0x4FE2C8`);
  2. `0x402CC5` — tło menu: `[esi+0xd8]` = **`titlescreen.bmp`** (loader `0x402ed1`, ten sam struct) → `[esi+0xdc]`;
  3. `0x49033B` — **efekt przejścia/fade** całej powierzchni ekranu (nie asset) — Faza A go nie dotyczy.
- Powierzchnia docelowa = rozmiar ekranu (ctor `0x40C634` z `GetWidth/GetHeight`).
- Loader akceptuje **24 bpp** (dowód: moda `loadscreen.bmp` 1440×900×24 bpp działa) i 16 bpp (oryginały).

## Zakres

- [ ] Faza A — wyłącznie assety (bez kodu): identyfikacja i wymiana wszystkich rozciąganych teł na wersje 16:9.
- [ ] Faza B (opcjonalna) — letterbox/pillarbox w kodzie: poprawka proporcji w `0x40D507` lub jego callerach.

## Poza zakresem

- Skalowanie widgetów/fontów (P2, P3).
- Wrapper DirectDraw (P4).
- Modyfikacja HUD (nie jest skalowany — patrz wnioski §6.3).

## Etapy

### Etap 0 — Inwentaryzacja (0,5 dnia) ✅ ZAKOŃCZONY
1. Zidentyfikować **wszystkie** rozciągane tła:
   - [x] titlescreen (mod: `CN.PLMOD\pictures\bitmaps\titlescreen.bmp` — ścieżka w loaderze @ `0x4FE2F4`, wybierana w `0x40259C`, prefiksy `0x405b9f`),
   - [x] loadscreen (mod: `CN.PLMOD\pictures\bitmaps\loadscreen.bmp`, @ `0x4FE2C8`),
   - [x] tło menu — **ROZWIĄZANE: to ten sam `titlescreen.bmp`** (loader `0x402ed1` → `[esi+0xd8]`); `menubg.bmp`/`menubgg.bmp`/`Data\gui\lang\pol\pictures\*.bmp` **nie są ładowane** (exe ma tylko 8 stringów `.bmp`, żaden nie zawiera „menubg") → pliki martwe, nie wymagają konwersji,
   - [x] `datax\pictures\post00.bmp` — istnieje (1440×900), ładowany do tego samego `[esi+0xd8]` (`0x402e18`) → **też rozciągany**; `pre00.bmp` i `%s%2.2d.bmp` nie istnieją na dysku (loader pomija),
   - [x] kadr intro (`0x49033B`) — to **fade/skalowanie ekranu**, nie asset — pominąć.
2. [x] Zmierzyć wymiary/format: wszystkie 3 pliki = **1440×900, 24 bpp, RGB**.
3. [x] Rozdzielczość docelowa: **1920×1080** (gracz używa 16:9; proporcja ważniejsza od pikseli).

### Etap 1 — Faza A: assety 16:9 (1–3 dni) ✅ WYKONANY (poza testem na żywo)
1. [x] Konwerter (Python + Pillow 12.1.1): center-crop 1440×900 → 1440×810 (16:9, −45 px góra/dół) → Lanczos → **1920×1080, BMP 24 bpp** (`plan1_rescale.py`).
2. Uszlachetnić istniejące assety:
   - [x] `titlescreen.bmp` 1440×900 → 1920×1080 16:9,
   - [x] `loadscreen.bmp` 1440×900 → 1920×1080 16:9,
   - [x] `DataX\Pictures\post00.bmp` 1440×900 → 1920×1080 16:9,
   - [x] ~~oryginalne 800×600~~ — **nie trzeba**: pliki `menubg`/`menubgg`/`lang\pol\pictures` są martwe (nie ładowane przez exe).
3. [x] Backupy: `titlescreen.bmp.orig`, `loadscreen.bmp.orig`, `post00.bmp.orig` (+ modowy backup `DataX\Pictures\Originals\post00.bmp`).
4. [ ] **Test na żywo (POZOSTAŁE):** uruchomić grę na 1920×1080 (`Saves\opt_glob.ini` ustawione), zrzuty: titlescreen, menu, loadscreen, ekran po misji (post00) — brak deformacji i czarnych pasów.
   Podglądy do szybkiego sprawdzenia bez gry: `...\Temp\opencode\prev_title_new.png`, `prev_load_new.png` (porównać z `prev_title_old.png`).

### Etap 2 — Faza B (opcjonalna): letterbox w kodzie (tygodnie)
Cel: poprawne proporcje nawet dla źródeł niedopasowanych (np. stare 4:3).
1. Zaprojektować obliczenie obszaru docelowego: `dstW' = min(dstW, dstH·srcW/srcH)`, wycentrowanie (`+ (dstW−dstW')/2`).
2. Miejsce patcha: **najlepiej w callerach `0x40D507`** (3 sztuki — wyliczyć rect zamiast `(0,0,w,h)`), a nie wewnątrz pętli pikselowej (mniejsze ryzyko).
3. Alternatywa bez patcha binarki: przygotować **osobne assety per proporcja ekranu** (16:9 / 16:10 / 4:3) i przełączać zawczasu — wymaga loadera wyboru (więcej pracy, zero ryzyka dla exe).
4. Weryfikacja: 1920×1080, 2560×1080 (21:9 — tu letterbox zadziała), 1280×1024 (5:4).

## Kryteria akceptacji

- [ ] Brak zniekształceń proporcji na 1920×1080 (porównanie wizualne z oryginalnym obrazem).
- [ ] Brak czarnych pasów przy typowych rozdzielczościach 16:9.
- [ ] Oryginalne pliki zachowane (rollback).
- [ ] Gra startuje się poprawnie; titlescreen, loadscreen i tło menu zweryfikowane.
- [ ] (Faza B) Letterbox działa też przy proporcjach ≠ 16:9.

## Ryzyka

| Ryzyko | Łagodzenie |
|---|---|
| Loader wymaga konkretnej głębi bitowej (16 bpp) | przetestować 24 bpp najpierw (dowód: obecne assety 24 bpp działają) |
| Inne, nieznane tło ładowane z innego miejsca | inwentaryzacja z xref-ów stretch (`stretch_users.py` — dokładnie 3 call-sites) |
| Faza B = patch binarki (ryzyko uszkodzenia) | patch tylko w 3 callerach, kopia zapasowa exe, test regression |
| Kwestie prawne: nie dystrybuować assetów gry | nowe assety tworzone od zera (własne grafiki) lub tylko w lokalnej instalacji |

## Materiały odniesienia

- Skrypty: `plan1_step0.py` (inwentaryzacja + stringi `.bmp`), `plan1_menu_loader.py` (sekcje PE, stringi, xref stretch), `plan1_scan_d8.py` (skan `[+0xd8]` w całym `.text`), `plan1_dis_menu*.py`, `plan1_verify.py` (loader `0x402583`), `plan1_prefix.py` (prefiksy ścieżek), `plan1_rescale.py` (Faza A: crop+Lanczos) — wszystkie w `...\Temp\opencode\`.
- Adresy: `0x40D507` (stretch), `0x402583` (loader title/load), `0x402ed1` (loader tła menu = titlescreen), `0x402CC5` (menu bg), `0x402e18` (datax post → `[esi+0xd8]`), `0x49033B` (fade, nie asset), `0x4787B3` (draw), `0x479195` (flip).
