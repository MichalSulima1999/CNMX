# Plan implementacyjny P4 — Wrapper DirectDraw/D3D8 (nowoczesny present)

**Priorytet:** 4 z 4 (największy nakład inżynieryjny; najbardziej „odporne na przyszłość" rozwiązanie)
**Wysiłek:** miesiące
**Zależności:** opcjonalnie po P1–P3; **niezależny** — można robić równolegle jako osobny wątek
**Powiązane wnioski:** `.ai\docs\wnioski-analiza-remaster.md` §6.1, §6.4

## Cel

Gra renderuje w 16-bit (depth 16) przez DirectDraw (prawdopodobnie z realnym trybem pełnoekranowym
i interfejsem z 2005 r.). Wrapper (proxy DLL) ma:
1. przechwycić prezentację klatki,
2. przeskalować ją do rozdzielczości okna/ekranu nowoczesnym filterem (lub pozostawić 1:1 przy natywnej),
3. umożliwić **borderless windowed**, brak migotania, poprawne skalowanie bez zależności od sterowników
   (stare DDraw na modern Windows bywa problematyczne),
4. (opcjonalnie) przełączyć na 32-bit surface + konwersję palety (eliminacja artefaktów 16-bit).

Daje to remasterowi „bezpiecznik": nawet jeśli sam exe zostanie stary, warstwa prezentacji jest nowa.

## Dowody techniczne

- **ddraw/d3d8 NIE występują w tablicy importów** — ładowane dynamicznie:
  `LoadLibraryA("DDRAW.DLL")` → `GetProcAddress("DirectDrawCreateEx")` → `DirectDrawCreateEx(NULL,&dd,IID@0x4fba30,NULL)` → QI **IDirectDraw2** (string „Couldn't QI DDraw2").
  Init: 0x478540 i 0x4786b3; fallback przy `[+0x54] < 0x700`: 0x47891d.
- String `D3D8.DLL` istnieje (0x50592c), ale **census nie wykazuje realnych wywołań metod D3D8** → Wariant 2 (proxy d3d8) zbędny.
- Prezentacja: Flip = **0x405658/0x40567e** (`do { hr=Flip(this,0); } while(hr==DDERR_WASSTILLDRAWING)` z `Sleep(10)`); blit do ekranu 0x405579; draw 0x4787b3; 0x479195 to **dyspozytor wiadomości**, nie flip.
- **WaitForVerticalBlank nie występuje w pętli klatek** (wrapper 0x4057d7 — 1 wywołanie init 0x40503c; raw `[reg+0x48]` — 9 miejsc, tylko zmiana trybu/ścieżki przejściowe; gated vsync w pętli blitu 0x477197 gdy `bit 0x40` w `[obj+0x18]`).
- **Brak ogranicznika FPS** w głównej pętli; brak `timeBeginPeriod` (Sleep-ki realnie ~15,6 ms).
- Tryb z `Game.ini` (root): `gfx_fullscreen`, `gfx_fullscreen_toggle`, `gfx_screen_width/height/depth` (parser 0x401084–0x40125a, loader 0x4e1020); **brak klucza vsync**.
- Display ctor 0x4787CB: okno 800×600@16, małe 640×400@8, fullscreen 1600×1200@32; stan trybu w `+0x14` (0/1/2).
- Szczegóły: `.ai\docs\wnioski-analiza-prezentacja.md` (2026-10-06).

## Zakres

- [x] Wariant 1: proxy `ddraw.dll` (DirectDrawCreate/DirectDrawCreateEx) → forward + własny present.
- [x] ~~Wariant 2: proxy `d3d8.dll`~~ — zamknięte w Etapie 0 (D3D8 nie jest realnie używane).
- [x] **BASELINE ZALICZONY (06.10.2026):** dgVoodoo2 v2.87.5 (`DDraw.dll` + `dgVoodoo.conf` z `ForceVerticalSync=true` w katalogu gry) — użytkownik: „Działa i przestało rwać obraz”. **Tearing usunięty**, diagnoza potwierdzona. Decyzja: zostać przy dgVoodoo2 (0 własnego kodu) vs budować własny wrapper — patrz §Status.
- [ ] Konfiguracja (INI): borderless, skalowanie (nearest/linear), vsync, skalowanie 16→32-bit.
- [ ] Testy na modern Windows 10/11.

## Poza zakresem

- Zmiany assetów/UI (P1–P3).
- Własny renderer 3D (gra i tak rysuje 2D blitem).

## Status (06.10.2026)

**Etap 0 [ANALIZA] ✅ + BASELINE dgVoodoo2 ✅ („Działa i przestało rwać obraz”).**
Diagnoza (brak vsync w pętli klatek + retry `Sleep(10)`) potwierdzona empirycznie — zewnętrzny wrapper
z vsync usuwa objawy przy zerowym nakładzie na własny kod.

**DECYZJA UŻYTKOWNIKA (06.10.2026): wariant A — zostajemy przy dgVoodoo2. Plan 4 ZAMKNIĘTY.**
- P4 był wykorzystany **diagnostycznie**; własny wrapper (B) nie będzie budowany na razie.
- W dystrybucji modu: wskazać link do dgVoodoo2 (autorskie prawa — nie dołączamy plików bez zgody;
  opcjonalnie prosty launcher kopiujący skonfigurowane pliki przy zwolnieniu).
- Priorytet wraca do **Planu 3 (skalowanie HUD)**.

Obecnie: **w katalogu gry zainstalowany dgVoodoo2** (DDraw.dll, dgVoodoo.conf, dgVoodooCpl.exe) — patrz
`.ai\docs\wnioski-analiza-prezentacja.md` §5/§6.

## Etapy

### Etap 0 — Ustalenie ścieżki renderowania (2–4 dni) [ANALIZA] — **WYKONANY (2026-10-06)**
- [x] Importy PE: **ddraw/d3d8 nieobecne w tablicy importów** — ładowanie dynamiczne (LoadLibrary „DDRAW.DLL" + GetProcAddress „DirectDrawCreateEx").
- [x] D3D8: string `D3D8.DLL` jest, ale brak realnych wywołań metod D3D8 w census → **D3D8 nieużywane; proxy tylko ddraw**.
- [x] Tryb okna vs pełny ekran: `Game.ini` (root) — `gfx_fullscreen`/`gfx_fullscreen_toggle` + `gfx_screen_width/height/depth`; domyślne okno 800×600@16 / fullscreen 1600×1200@32 (ctor), brak klucza vsync.
- [x] Krytyczne metody ddraw do hookowania (census): CreateSurface (+0x18), SetDisplayMode (+0x44), SetCooperativeLevel (+0x40), Flip (+0x2c), Blt, WaitVBL (+0x48); **prezentacja per-frame przechodzi przez wrapper X2D 0x405658 → Flip retry `WASSTILLDRAWING + Sleep(10)`, bez czekania na vblank**.
- [x] Decyzja: **ddraw-proxy (Wariant 1)**; d3d8-proxy niepotrzebny. Wyniki: `.ai\docs\wnioski-analiza-prezentacja.md`.

### Etap 1 — Szkielet proxy (1–2 tygodnie)
- [ ] Projekt C/CMake: `ddraw.def` z eksportami forwardującymi do systemowego `ddraw.dll`
      (LoadLibrary + GetProcAddress w `DllMain`/pierwszym wywołaniu — **uwaga na cykl**, klasyczny
      wzorzec „proxy DLL": ładować `%SystemRoot%\System32\ddraw.dll` jawnie).
- [ ] Przechwycenie `DirectDrawCreate(Ex)`: utworzyć prawdziwy obiekt, **opakować** w interfejs
      (klasa wrapper na `IDirectDraw7`/`IDirectDrawSurface7`) — vtable hook na:
      - `SetDisplayMode` (zapisywać deklarowaną rozdzielczość),
      - `CreateSurface` (oznaczyć backbuffer),
      - `Flip` / `Blt` → **tu oryginalny present**: konwersja + skalowanie + Blt do okna docelowego.
- [ ] Wersja build = Debug (logi) / Release.

### Etap 2 — Prezentacja i skalowanie (1–2 tygodnie)
- [ ] Mapowanie 16-bit RGB565 → 32-bit (szybka tablica LUT) — jeśli zostajemy przy 16-bit źródle.
- [ ] Skalowanie: nearest (domyślnie, retro) + opcjonalnie linear; D3DX absent → własny shader
      (najprościej: `StretchRect` z D3D9 helper, albo GDI `StretchBlt` dla startu, potem D3D9/D3D11
      oddzielne okno prezentacyjne).
- [ ] Borderless windowed: okno dokładnie na rozmiar monitora, styl bez ramki, ukryty kursor opcjonalnie.
- [ ] VSync + usunięcie pętli `Sleep(10)` (nie da się z poziomu DLL — ale flip stanie się nieblokujący).

### Etap 3 — Opcjonalnie: 32-bit i paleta (1–3 tygodnie)
- [ ] Wariant 8-bit window: obsługa palety (`X2DDDDisplayPalette.cpp`) → konwersja paletowa w hooku.
- [ ] Wymuszenie 32-bit surface + konwersja 16→32 (kompromis: mniej problemów z gamma/artefaktami).
- [ ] Test: `gfx_screen_depth` 16 vs 32.

### Etap 4 — Dystrybucja i testy (1 tydzień)
- [ ] Instalacja: kopiować `ddraw.dll`/`d3d8.dll` **obok exe gry** (Ładowanie przez DLL search path);
      **nie** podmieniać systemowego DLL.
- [ ] `ddraw.ini`: `scaling=nearest|linear`, `borderless=1`, `vsync=1`.
- [ ] Testy: Win10/Win11 (Intel/NVIDIA/AMD), 1080p/1440p/4K, monitor 60/144 Hz, wielomonitorowe.
- [ ] Regression: bez wrapper gra wciąż działa (wrapper opcjonalny).

## Kryteria akceptacji

- [ ] Gra startuje z wrapperem i bez; z wrapperem: brak migotania, brak problemów z trybem pełnym.
- [ ] Skalowanie obrazu 16:9 bez deformacji (współpraca z P1) — wrapper zna proporcje.
- [ ] Borderless windowed działa na Win11.
- [ ] Brak spadku FPS (wrapper nie dodaje kopii >1 na klatkę).
- [ ] Konfiguracja bez kompilacji (INI).

## Ryzyka

| Ryzyko | Łagodzenie |
|---|---|
| Gra używa nieoczekiwanych exportów ddraw | Etap 0 — pełna lista importów; pełny forward wszystkich exportów |
| Vtable/heurystyka w grze (sprawdza wskaźniki) | opakowywać oryginalny obiekt, nie fałszować — zwracać prawdziwe LPDIRECTDRAW |
| D3D8 zamiast/w dodatku do DirectDraw | ustalić w Etapie 0; proxy obu DLL dla pewności |
| Prawa: dystrybucja — nie dołączać systemowych DLL | własny proxy = własny kod; forward do systemu |
| Starsze gry mają timing zależny od flip (vsync/10 ms) | zachować opcję „oryginalny timing" w INI |

## Alternatywy (nie robić od zera)

- **dgVoodoo2** (zewnętrzne, zamknięte): konwertuje DDraw/D3D8→D3D11 — do **przetestowania od razu**
  jako baseline: jeśli gra na dgVoodoo działa dobrze, P4 jest mniej pilny (nie dystrybuować — linkować).
- **cnc-ddraw** (open source, GPL): gotowa baza proxy DDraw (nie kopiować kodu GPL do własnego —
  study only, albo osobna licencja).
- **Wynik testu baseline** zapisać w `.ai\docs\` — to może zamknąć P4 bez własnego kodu.

## Materiały odniesienia

- Adresy (po aktualizacji RE 2026-10-06): DDraw init 0x478540/0x4786b3, draw 0x4787b3, dyspozytor msg 0x479195,
  **flip 0x405658/0x40567e (retry WASSTILLDRAWING+Sleep(10))**, blit 0x405579, wrappery WaitVBL 0x4057d7,
  pętla blitu runtime 0x47712b (gated vsync bit 0x40), tryb display ctor 0x4787cb, parser Game.ini 0x401084–0x40125a, loader 0x4e1020.
- Stringi: `X2DDDDisplayPalette.cpp`, `Can only work with 8 or 16 bit bitmaps in window mode...`, `D3D8.DLL`.
- Pliki: `Game.ini` (klucze `gfx_*`, **brak vsync**), `Saves\opt_glob.ini` (ustawienia pozostałe).
- Skrypty: `pe_imports.py`, `pe_present.py`, `pe_calls2.py`, `pe_waitvb.py`, `pe_cfg.py` (wszystkie w `.ai\scripts`).
- Wnioski: `.ai\docs\wnioski-analiza-prezentacja.md`.
