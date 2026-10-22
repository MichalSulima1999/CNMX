# Wnioski: Prezentacja obrazu i wydajność (rywanie obrazu + zacinanie)

**Data:** 2026-10-06
**Obszar:** CN.PLMOD.exe — warstwa DirectDraw, timing klatek, konfiguracja graficzna.
**Metoda:** wyłącznie statyczna RE (pefile + capstone), brak uruchamiania binaru.
**Skrypty:** `.ai\scripts\pe_imports.py`, `pe_present.py`, `pe_calls2.py`, `pe_waitvb.py`, `pe_cfg.py`.

---

## 1. Kontekst

Użytkownik po instalacji etapów P1/P2 zgłosił dwa objawy przy *oryginalnym* działaniu gry:
1. **rozrywanie obrazu (tearing)** podczas przewijania mapy,
2. **okazjonalne spadki FPS / zacinanie**.

Pytanie analityczne: czy to cecha samego silnika (2005, X2D/ProjectD „Funatics”), wada emulacji DirectDraw na współczesnym Windows, czy jedno i drugie — i jak to naprawia Plan 4 (wrapper DDraw).

---

## 2. Ustalenia architektoniczne

### 2.1. Ładowanie DirectDraw — dynamiczne (brak w tablicy importów)
W tablicy importów **nie ma** `ddraw.dll`/`d3d8.dll`. Gra ładuje DDraw w locie:

- `LoadLibraryA("DDRAW.DLL")` → `GetProcAddress("DirectDrawCreateEx")` → `DirectDrawCreateEx(NULL, &dd, IID@0x4fba30, NULL)` → QI do **IDirectDraw2**.
- Adresy: init 0x478540 i 0x4786b3; guard `[+0x54] >= 0x700` → fallback 0x47891d.
- Stringi: `0x504fcc` „DDRAW.DLL”, `0x504fb8` „DirectDrawCreateEx”, `0x5059ac` „Couldn't QI DDraw2”.
- String `D3D8.DLL` (0x50592c) **istnieje, ale census nie wykazuje żadnych realnych wywołań metod D3D8** — ścieżka D3D8 nie jest używana w znalezionym kodzie prezentacji.

### 2.2. Sygnatury kompilatora
- Kod 32-bitowy, konwencja `__fastcall` (this w `ecx`), sekwencje `ret N`, alokacje `4e7740/4e55bd` → **Borland C++ Builder** (ProjectD BaseLibs XSystem/X2DApp). Plik nie jest pakowany (UPX nie wykryty).

### 2.3. Prezentacja klatki (konkret)
- **Flip = pętla retry z Sleep:** funkcja `0x405658` (wrapper X2DSurface::Flip):
  ```
  do {
      hr = surface->Flip(this, flags=0);     // 0x40568d: call [vtable+0x50]
      if (hr == 0x88780096)                  // DDERR_WASSTILLDRAWING
          Sleep(10);                         // 0x40569c
  } while (hr != 0);                         // 0x4056a4
  ```
  Łańcuch: `BltScreen 0x405579` → `FlipWait 0x405658`; tryb/render → `0x4056b8/0x4057b8`.
- **Brak czekania na pionowy odśwież w pętli klatek.** Wrapper WaitForVerticalBlank (`0x4057d7`) ma **dokładnie 1 wywołanie** (init display `0x40503c`). Raw `WaitForVerticalBlank` (`[reg+0x48]`) — 9 miejsc, wszystkie w kodzie przełączania trybu/ścieżek przejściowych (0x4057e6, 0x4771b6, 0x4ca9bf, 0x4dc67a…), **zero w renderze per-frame**.
- Istnieje **brama vsync w kodzie blitu runtime** (pętla 0x47712b): gdy flaga `bit 0x40` w `[obj+0x18]`, przed blitem wołane jest WaitForVerticalBlank (0x477197–0x4771b6). Źródło flagi — pisane innym wzorcem (brak `or [m+0x18],0x40` w .text); nie sterowane przez Game.ini (patrz §4).
- **Brak ogranicznika FPS w głównej pętli.** Wykryte Sleep-y: retry-flip `Sleep(10)`, utility 4×draw+`Sleep(10)` (0x40277e), `Sleep(50)` w kodzie kampanii/map (0x4d92cf, 0x4d9621) — żaden nie jest stałym pacerem klatek.
- WINMM: importowane **tylko `timeGetTime`** — **brak `timeBeginPeriod`** → każdy `Sleep(10)` realnie kosztuje kwantum timera Windows (~15,6 ms przy domyślnej rozdzielczości).

### 2.4. Census wywołań vtable DDraw (zwalidowany, `call [reg+disp8]`)
| Offset | Hipotetyczna metoda | Liczba miejsc | Kluczowe adresy |
|---|---|---|---|
| +0x18 | CreateSurface | 11 | 0x403a7d, 0x40475e, 0x405345, 0x4772b1, 0x477ef5, 0x479f0e, 0x47a481, 0x47a5ec, 0x47a940, 0x4cf1a2, 0x4dcda7 |
| +0x2c | Flip (surface) | 8 | 0x4055c3, 0x4776f1, 0x477753, 0x477e3e, 0x477ec3, 0x477f5a, 0x47abc3, 0x47baed |
| +0x40 | SetCooperativeLevel | 3 | 0x40460b, 0x4057cc, 0x47a97e |
| +0x44 | SetDisplayMode | 6 | 0x40576f, 0x478144, 0x47b00c, 0x47b099, 0x4b8166, 0x4b85b2 |
| +0x48 | WaitForVerticalBlank | 9 | 0x4057e6, 0x4771b6, 0x4ca9bf, 0x4dc67a, 0x4dc863, 0x4dc8ba, 0x4dc969, 0x4dc9ca |
| +0x50 | Flip/wrap X2D | ~132 | m.in. 0x40568d (retry-loop) |

Pomiar mówi wprost: **gra ma wszyte vsync-opcje (WaitVBL), ale nie używa ich w ścieżce per-frame** — jedyna synchronizacja prezentacji to retry `WASSTILLDRAWING + Sleep(10)`.

### 2.5. Tryb wyświetlania i konfiguracja
- CDDDisplay ctor (0x4787cb): defaults okno 800×600@16 (pola +0x14/0x18/0x1c), okno małe 640×400@8, fullscreen 1600×1200@32 (+0x2c/+0x30/+0x34); stan trybu w +0x14 (0/1/2 — automaty 0x47810f-0x478195, przeliczanie rozdzielczości przez SetDisplayMode 0x478144, przywracanie 0x477de1).
- **Game.ini** (root gry, obecnie zawiera tylko `set_language 6` + zakomentowany `gfx_fullscreen 0`):
  - klucze czytane w init: `gfx_fullscreen` (0x401181), `gfx_fullscreen_toggle` (0x4011ad), `gfx_screen_width` (0x4011ed), `gfx_screen_height` (0x401220), `gfx_screen_depth` (0x401244); osobny loader 0x4e1020.
  - **brak klucza vsync** — wszystkie dostępne dziś przełączniki to rozdzielczość, głębia i fullscreen.

---

## 3. Diagnoza objawów

1. **Rozrywanie przy przewijaniu mapy:** prezentacja nie jest zsynchronizowana z odświeżaniem monitora (brak WaitVBL/brak DDFLIP_WAIT ciasno w pętli klatek; flags=0 przy Flip). Przewijanie = ciągłe blity nowych fragmentów mapy do backbuffer + Flip w losowej fazie odświeżania → klasyczny tear line.
2. **Zacinanie:**
   - Napotkany `DDERR_WASSTILLDRAWING` zmienia każdą taką klatkę w `Sleep(10)` **ale realnie ~15,6 ms** (brak timeBeginPeriod) → mikro-zacięcia o widocznej amplitudzie na współczesnym Windows.
   - Główna pętla bez limitera klatek → fluktuacje obciążenia CPU/GPU (DWM, migotanie priorytetów wątków), szczególnie przy fullscreen exclusive.
   - DDraw na Windows 10/11 jest emulowany (tłumaczony na DirectX) — ścieżki 16-bit i tryb exclusive są droższe i mniej stabilne czasowo niż w 2005 r.; emulator bywa zwraca `WASSTILLDRAWING` w sytuacjach, w których stary sprzęt blokował się wprost.
3. **Refleks:** część problemu to *cechy silnika* (2005), część to *emulacja DDraw na nowym Windows* — wrapper z prawdziwym vsync + pacingiem leczy oba czynniki.

---

## 4. Co użytkownik może zrobić dziś (bez łatek)

- **Game.ini:** odkomentować/ustawić `gfx_fullscreen 1|0`, `gfx_screen_width/height/depth`. Tryb okna potrafi przenieść obraz pod DWM (kompozycja vsync), co dla wielu starych gier usuwa tearing — do przetestowania.
- Nie istnieje klucz vsync — limitu tego nie da się ominąć z poziomu ini.

---

## 5. Rekomendacje (ścieżka naprawy)

### Etap natychmiastowy (bezpisaniowy, 15 min) — baseline wrappera:
Test **dgVoodoo2** (wrapper DDraw→D3D11/D3D9, vsync sterowany z `dgVoodoo.conf`, skalowanie wg ustawień) lub **cnc-ddraw**: wrzucamy `DDRAW.DLL` do katalogu gry, `vsync=1`, rozdzielczość natywna bez skalowania. Jeśli objawy znikną (tearing + stutter) — potwierdzona diagnoza i tłusty argument za wariantem B.

> **STATUS BASELINE (06.10.2026) — ZAINSTALOWANY do testu użytkownika:**
> - `G:\Games\CnMod 1.2\DDraw.dll` — dgVoodoo2 v2.87.5 (MS/x86, hash zgodny ze źródłem, 32-bit, eksporty DirectDrawCreate/Ex).
> - `G:\Games\CnMod 1.2\dgVoodoo.conf` — domyślny + `[DirectX] ForceVerticalSync=true`, `dgVoodooWatermark=false`.
> - `G:\Games\CnMod 1.2\dgVoodooCpl.exe` — konfigurator GUI (opcjonalny).
> **Procedura testu:** uruchom grę, przesuwaj mapę (w lewo/prawo) i sprawdź: 1) czy zniknęło rozrywanie, 2) czy zniknęło zacinanie, 3) czy tryb pełnoekranowy działa poprawnie. Porównanie bez wrappera (revert: usuń `DDraw.dll` + `dgVoodoo.conf` + `dgVoodooCpl.exe`).
> **Noty:** jeśli NVIDIA i sterownik < 616.56 → ewentualne crashe D3D12 (zmień `OutputAPI=d3d11_fl11_0`); skalowanie zostawione „unforced" (tryb gry 1:1), strojenie (centered_ar / resampling / FPSLimit) do zrobienia po wyniku testu.
> **Wynik testu:** zapisać w §6 poniżej (wpis z datą).

### Plan 4 (właściwy remaster prezentacji):
Wg `plan-4-wrapper-ddraw.md`, własny proxy `ddraw.dll`:
1. wyłapywanie `DirectDrawCreateEx` + obiektu IDirectDraw2 (+ powierzchnie, blit, flip, WaitVBL),
2. **vsync + frame pacing** (QPC, ewentualnie timeBeginPeriod),
3. skalowanie do natywnej (kontynuacja P1, letterbox),
4. opcjonalnie 32-bit surface + konwersja palety (eliminacja bandingu/artefaktów 16-bit).

### Opcja środkowa (łatka exe):
Wymusić ścieżkę „vsync on” — ustawienie `bit 0x40` w `[obj+0x18]` przy starcie (flaga czekana w pętli blitu 0x477197). Ryzykowne (nie zbadaliśmy źródła flagi, łatki w exe sięgają poza wrapper), dlatego traktowane jako rezerwa.

---

## 6. Status Planu 4

**Etap 0 (wstępne RE) — WYKONANY:** sciezka prezentacji zmapowana (adresy wyżej), wrapper ma komplet punktów zaczepienia. Plan: patrz `plan-4-wrapper-ddraw.md`.
**Baseline dgVoodoo2 — ZAINSTALOWANY (06.10.2026), oczekuje na test użytkownika** (patrz §5).

**Dalsze kroki (do decyzji po wyniku testu):**
- [ ] Test w grze: przewijanie mapy (tearing?), ogólna płynność (stutter?), tryb pełnoekranowy.
- [x] **Test TEARING OK (06.10.2026)** — użytkownik: „Działa i przestało rwać obraz”.
- [ ] Stutter: dopytać użytkownika o odczucia (retry-loop `Sleep(10)` → vsync dgVoodoo2 powinno go też wyeliminować).
- [ ] Jeśli OK → decyzja: zostawić dgVoodoo2 jako rozwiązanie (0 własnego kodu) vs budować własny wrapper (P4) dla pełnej kontroli skalowania/32-bit.
- [ ] Jeśli NIE OK → kalibracja conf (OutputAPI, FPSLimit, resampling) lub powrót do analizy; jednocześnie P3 (HUD) w trybie równoległym.

**Plan 4 — ZAMKNIĘTY (06.10.2026):** wstępne RE zrealizowane, butina naprawy = **dgVoodoo2** (vsync, bez własnego kodu), akceptacja użytkownika; własny wrapper tylko na wyraźne życzenie (wariant B).
**Kolejny priorytet:** **Plan 3 (skalowanie HUD)**.

**Wynik testu dgVoodoo2 (wpis użytkownika):**
- **06.10.2026 — „Działa i przestało rwać obraz” ✅** Tearing przy przewijaniu mapy zniknął.
- Stutter/znaczenie FPS: przy kolejnej sesji użytkownik potwierdza (brak zgłoszeń → ścieżka zamknięta).