# Plan implementacyjny P3 — Skalowanie HUD i UI (globalny mnożnik)

**Priorytet:** 3 z 4 (najwyższe ryzyko wizualne/techniczne — robić **po** P1 i P2)
**Wysiłek:** miesiące
**Zależności:** P2 (fonty) powinien być zamknięty — bez czytelnych fontów skalowanie HUD nie ma sensu
**Powiązane wnioski:** `.ai\docs\wnioski-analiza-remaster.md` §6.3

## Cel

Doprowadzić do tego, by cały interfejs (panele, przyciski, ikony, zasoby, minimapa/HUD) był
**proporcjonalnie większy** na wysokich rozdzielczościach — obecnie UI jest poprawnie *rozstawiony*
(krawędzie, centrowanie), ale **stałorozmiarowy** (brak mnożnika skali), więc na 1920×1080 wygląda na małe.

## Dowody techniczne

- GUI dostaje prawdziwe wymiary: `0x49F52B` → `[0x569264]=w`, `[0x569268]=h`, `[0x56926c]=depth`,
  root widget `0x476643(w,h,format)`.
- **35 xref-ów do GUI width** — układ liczony względem krawędzi, ale **w pikselach bezwzględnych**:
  - centrowane dialogi: `x=(w−500)/2`, `y=(h−420)/2` (~15 miejsc: `0x4A39C4`, `0x4A510C`, `0x4ADF7D`,
    `0x4BE6E5`, `0x4C3D1E`…),
  - prawa/dolna krawędź: `x=w−140`, `y=h−600` (`0x4A8851`, push `0x258`/`0x8c`),
    `w−260`/`h−340` (`0x4B0770`), `w−160`, `w−200`, `w−240`.
- Gettery: `GetGUIWidth=0x4A8845`, `GetGUIHeight=0x4A884B` (3 wywołania każde).
- **Brak jakiegokolwiek mnożnika skali** w exe (brak dzielenia przez 800) — trzeba go *wprowadzić*.
- Blity HUD są 1:1 (`0x47B0D7`, `0x411327` — memcpy wierszowe); bitmapy widgetów 300×300 kafli.

## Zakres

- [ ] Pełna katalogizacja stałych layoutu (~30+ miejsc).
- [ ] Określenie strategii skalowania (3 warianty poniżej) + wybór.
- [ ] Implementacja + testy wizualne na wielu rozdzielczościach.

## Poza zakresem

- Skalowanie samych fontów (P2 — realizowane niezależnie).
- Proporcje teł (P1).
- Wrapper DirectDraw (P4).

## Warianty strategii (decyzja po Etapie 0)

| Wariant | Opis | Zalety | Ryzyko |
|---|---|---|---|
| **A. Skalowanie zasobów + proste przesunięcia** | podmiana bitmap widgetów (300×300 → 600×600 itd.) bez zmiany stałych | zero patchy kodu | tekstury rozmyte/rozciągnięte; stałe `500×420` dialogów nie rosną → rozjazd |
| **B. Globalny mnożnik (rekomendowany)** | wprowadzić `scale` (np. 2.0) — modyfikować obliczenia `x=(w−500)/2` → `x=(w−500·s)/2`, `w−140` → `w−140·s`, i mnożyć rozmiary rysowanych bitmap o `s` | spójny, kontrolowany efekt | wymaga patcha **wielu** miejsc + znalezienia miejsca, gdzie powierzchnie są tworzone (ctor `0x40C634`) |
| **C. Render do mniejszego bufora + upscale** | UI rysowany na powierzchni 800×600/1024×768, potem stretched do ekranu (jak `0x40D507`) | **najmniejsza liczba patchy** — 1 miejsce prezentacji | rozmycie (nearest 2×), kolizja z stretchingiem teł, trzeba rozdzielić tła od UI w pipeline |
| **D. Akceptacja stanu** | UI małe, ale czytelne po P2 (fonty 2×) | 0 pracy | HUD wciąż „miniature" na 1080p |

**Deczyzja (Etap 0, 06.10.2026):** **Wariant B — globalny mnożnik skali layoutu.** Wariant C odpadł po
zweryfikowaniu pipeline'u: UI i tła rysowane tą samą ścieżką do powierzchni ekranu (brak osobnego małego
bufora), więc C przeskalowałoby też mapę/natywne tła (konflikt z P1). B pasuje do pipeline'u 1:1
(uzasadnienie: `.ai\docs\pipeline-prezentacji.md`).

## Etapy

### Etap 0 — Rozpoznanie (3–7 dni) [ANALIZA, bez modyfikacji] — **WYKONANY (2026-10-06)**
- [x] **Katalogizacja stałych:** skrypt `p3_etap0.py` → `.ai\docs\layout-constants.md`
      (37 odwołań GUIW / 61 GUIH; gettery: GetGUIWidth 3, GetGUIHeight 3, GetWidth/Height 13×;
      push-stałe: 0x1f4(500)×19, 0x8c(140)×19, 0x104(260)×17, 0x1a4(420)×14, 0x190(400)×14,
      0x12c(300)×10, 0xc8(200)×24, 0x258(600)×4, 0x154(340)×4, 0x96(150)×2; pełny histogram w dok.).
- [x] **Tabela wyboru fontów:** `data\gui\fonts\font08/10/12/debug.fnt` wczytywane przy
      0x4E2514/0x4E251E/0x4E252D/0x4E253C (fonthead16bld — uzupełnić w Etapie 2, może być w innym zestawie).
- [x] **Pipeline prezentacji:** tło (stretch 0x40D507) i UI (blit 1:1 0x47B0D7 przez tail-jmp z draw 0x4787B3)
      idą **tą samą ścieżką** do wspólnego kontekstu ekranu — brak osobnej powierzchni UI.
      Szczegóły: `.ai\docs\pipeline-prezentacji.md`.
- [x] **Tworzenie powierzchni widgetów:** ctor 0x40C634 — **30 wywołań** (lista w layout-constants.md §2);
      tu wchodzi mnożnik rozmiarów.
- [x] **Mapowanie myszy:** potwierdzone 1:1 (przesunięcie o offset okna, bez mnożnika); **choke point**
      0x478B23→0x478E03 — podział przez skalę w jednym miejscu.
- [x] **DECYZJA: wariant B (globalny mnożnik skali layoutu).** C odpadł — pipelines UI/teł wspólny,
      C przeskalowałby też mapę/natywne tła (konflikt z P1); B pasuje do pipeline'u 1:1
      (uzasadnienie: `.ai\docs\pipeline-prezentacji.md` §2).

Szczegółowy plan wdrożenia B w Etapie 1–2: mnożnik `s` wszedłby w (a) stałe layoutu,
(b) 0x40C634 (rozmiary powierzchni widgetów), (c) 0x478E03 (mysz), (d) stretch istniejący przy blit.

### Etap 1 — Pilot na jednym elemencie (3–5 dni) — **PATCH WYKONANY, TEST UŻYTKOWNIKA W TOKU (2026-10-06)**
- [x] Dialog centrowany: **`0x4A39A0`** — skala per-osiowa `s_x=1.875` (baza 1024) / `s_y=1.8` (baza 600),
      patch imm32 ×4: `x=(w−938)/2`, `y=(h−756)/2`, rozmiar `938×756`.
- [x] Element krawędziowy: **`0x4A8851`** — panel prawy: `x=w−263`, `y=h−1080`, rozmiar `263×1080`.
- [x] **Weryfikacja binarnego patcha** (`p3_pilot_patch.py`): 8 imm32, bajty przed/po zgodne,
      dezasemblacja czysta; backup `CN.PLMOD.exe.orig` (revert: skopiować na `CN.PLMOD.exe`).
- [ ] **Test użytkownika na żywo:** czy dialog `938×756` jest centrowany i czytelny; czy panel boczny
      `263×1080` przylega do prawej krawędzi i NIE wystaje; ogólne wrażenie skali.
- [ ] Uwaga z pilota: `s=1.875` jednolite NIE mieści się w pionie (600·1.875=1125>1080 → y<0) —
      stąd decyzja **per-osiowa**. Potwierdza konieczność trzymania stałych wysokościowych wg `s_y≤1.8`.

### Etap 2 — Pełne wdrożenie (tygodnie) — **SKRYPT GOTOWY, TEST UŻYTKOWNIKA PENDING**
- [x] **Skrypt wdrożeniowy** `p3_etap2_patch.py` — patchuje:
  - 9 zakotwiczonych x (prawy róg: `w−K` → `w−K·s_x`)
  - 9 zakotwiczonych y (dolny róg: `h−K` → `h−K·s_y`)
  - 18 wymiarów widgetów (w×s_x, h×s_y)
  - 30 powierzchni (ctor `0x40C634` — width/height ×s_x/s_y)
  - 3 stretch blit (`0x40D507`)
  - Transformacja myszy (`0x478E03` — podział przez s_x/s_y)
- [x] **Testy skalowania** (`p3_etap2_test.py`) — wszystkie OK (round half up)
- [ ] **Test użytkownika na żywo:** uruchomić grę po patchu, sprawdzić:
  - Czy dolne prawe panele (200×100, 160×240, 140×160, 160×300, 160×360) przylegają do krawędzi
  - Czy prawy panel (140×600 → 263×1080) jest poprawnie skalowany
  - Czy mysz klika w odpowiednie przyciski
  - Czy fonty (P2) pasują do skalowanych widgetów
- [ ] Ewentualne poprawki po testach wizualnych
- [ ] Prezentacja na żywo: stopniowo (component po komponencie) — HUD zasobów → przyciski →
      listy → dialogi → minimapa.

### Etap 3 — Walidacja (3–5 dni)
- [ ] Matryca: 1280×720, 1920×1080, 2560×1440, 3840×2160 + 800×600 (brak regresji!).
- [ ] Scenariusze: menu, budowa, walka, rozmowa NPC, lista misji, zapis/wczytanie, credits.
- [ ] Wydajność: czy skala nie spowalnia (software blit) — mierzyć FPS.

## Kryteria akceptacji

- [ ] Na 1920×1080 UI zajmuje porównywalny **udział** ekranu co na 800×600 (wizualny benchmark: zrzuty obu).
- [ ] Brak regresji na 800×600 (scale=1 → identyczny layout jak dziś).
- [ ] Klikanie trafia w przyciski (mapowanie myszy spójne).
- [ ] Brak tekstów wychodzących poza widgety (współpraca z P2).
- [ ] Tła wciąż w poprawnych proporcjach (P1 niezepsute).

## Ryzyka

| Ryzyko | Łagodzenie |
|---|---|
| ~30+ stałych layoutu — łatwo coś przeoczyć | katalogizacja jako osobny artefakt + przegląd checklisty |
| Patch binarki = ryzyko uszkodzenia | kopia zapasowa exe; patchować małymi partiami; test po każdej |
| Rozjazd tekstu vs. skali widgetów | zależność: **najpierw P2** |
| Mapowanie myszy rozjechane | Etap 0 — weryfikacja 1:1; jeśli nie 1:1, transformacja w jednym miejscu |
| Software'owy stretch = wolne | mierzyć FPS; cache'ować przeskalowane bitmapy |
| Wariant C okazuje się niemożliwy (wspólna powierzchnia) | fallback do wariantu B |

## Materiały odniesienia

- Adresy: GUI init `0x49F52B`, globals `0x569264/0x569268/0x56926c`, root widget `0x476643`,
  `GetWidth=0x478479`, `GetHeight=0x47848A`, `GetGUIWidth=0x4A8845`, `GetGUIHeight=0x4A884B`,
  stretch `0x40D507`, ctor powierzchni `0x40C634`, draw `0x4787B3`, flip `0x479195`,
  blit HUD `0x47B0D7`, memcpy `0x411327`.
- Przykłady stałych: `0x1f4`(500), `0x1a4`(420), `0x258`(600), `0x8c`(140), `0x104`(260), `0x154`(340).
- Skrypty: `guiwh_xr.py` (35 xref-ów), `arith.py` (wzory odejmowania), `guiinit.py` (init GUI),
  `stretch_users.py` (3 call-sites).
