# Pipeline prezentacji: UI vs tła (Plan 3, Etap 0 — decyzja C vs B)

**Data:** 2026-10-06 · **Metoda:** statyczna RE (pefile + capstone), skrypty `p3_etap0.py`, `p3_pipeline.py`
**Wniosek:** pipeline UI i teł **wspólny** (ta sama ścieżka rysowania do powierzchni ekranu) →
**wariant C (osobny mały bufor) wymaga przebudowy; rekomendacja: wariant B (globalny mnożnik skali layoutu).**

---

## 1. Przepływ rysowania (potwierdzony)

```
[CDDDisplay::Draw] 0x4787B3  (wywoływany: 0x4020B6, 0x4022E7, 0x402795, 0x402CD8, 0x403491)
        │  mov eax,[ecx+0x4c] → eax=[eax+8] → jmp 0x47B0D7   (tail-jump, jedyne przejście)
        ▼
[blit HUD / bitmap-na-ekran] 0x47B0D7   (1:1; memcpy wierszowe 0x411327 z 1 wywołań: 0x40CBFA)
        ▼
[stretch teł] 0x40D507   (3 wywołania: 0x40264A, 0x402CC5, 0x49033B)
        ▼
[flip] 0x405658 (retry WASSTILLDRAWING+Sleep(10); vsync zapewnia dgVoodoo2)
```

- **Te same funkcje** (np. 0x402CC5→stretch i 0x402CD8→draw — ta sama funkcja aktualizacji kanału) rysują
  tła (stretch) i HUD (blit 1:1) **do wspólnego kontekstu ekranu** `[0x554F38]` (CDDDisplay).
- Brak osobnej, niższorozdzielczej powierzchni UI — UI jest rozkładane bezpośrednio przy aktualnej
  rozdzielczości okna/ekranu.
- GUI init (0x49F52B): `[0x569264]=w, [0x569268]=h, [0x56926C]=depth` z bieżącego trybu wyświetlania,
  root widget 0x476643(w,h,format). → **GUI zawsze pełna rozdzielczość, stałe w pikselach absolutnych.**

## 2. Konsekwencje dla wariantów

| Wariant | Werdykt wg pipeline'u |
|---|---|
| **C** (render do 800×600 + upscale) | **Odrzucony.** Nie ma osobnej powierzchni UI; C przeskalowałby CAŁĄ klatkę — w tym mapę na natywnej rozdzielczości (P1 straciłoby sens) i wymagał już istniejącego podziału tło/UI. Dodatkowo nadal potrzebna transformacja wejścia. |
| **B** (mnożnik skali w stałych layoutu) | **Rekomendowany.** Pasuje do obecnego pipeline'u: UI rysowane 1:1 w pikselach — wystarczy przeskalować stałe (x=(w−500·s)/2), rozmiary powierzchni widgetów i bitmapy (runtime-stretch przy blit 0x40D507 albo assety 2×), a tła/mapa zostają natywne. |

## 3. Mapowanie myszy (potwierdzenie 1:1 + jeden punkt transformacji)

- Jedyne `GetCursorPos` (0x478B23) w funkcji 0x478B14: pobiera kursor → **odejmuje offset okna**
  (`0x47849B`/`0x4784AD` = położenie wyświetlacza) → `push x,y; 0x478E03` (konwersja do GUI).
- Czyste przesunięcie, **bez mnożnika** (w fullscreen offset=0, czyli 1:1 z pikselami ekranu).
- **Choke point dla wariantu B:** jedno miejsce (0x478B53 → 0x478E03) — pod warunkiem B wystarczy
  tam podzielić x,y przez skalę przed przekazaniem do GUI.
- Uwaga: wzorce `0x478AF6..` to dodatkowe transformacje `[esi]/[esi+4]` (region klikalny, nie mysz GUI).

## 4. Dodatkowe ustalenia

- **Brak gettera** blit HUD przez `call` — tylko tail-jmp z draw (0x4787B3). Skalowanie bitmap HUD można
  zrobić już przy samym blit (0x47B0D7) lub wcześnie, przy tworzeniu powierzchni (0x40C634 / memcpy 0x40CBFA).
- Stretch 0x40D507 jest stosowany per-kanał (też w lokowaniu `0x40264A` przy tworzeniu docelowej
  powierzchni `[esi+0x15c]`); istniejący kod stretch** może posłużyć w B do rysowania powiększonych widgetów.
- **Fonty:** tablice wczytania `data\gui\fonts\font08/10/12/debug.fnt` w 0x4E2514/0x4E251E/0x4E252D/0x4E253C —
  czy używany jest fonthead16bld poza tym zestawem → sprawdzić przy Etapie 2 (P2 już je przeskalował).
- Ctor powierzchni 0x40C634 — **30 wywołań**: tam wchodzi mnożnik rozmiarów widgetów (obok stałych layoutu).

## 5. Rekomendacja dla planu

Robić **wariant B**:
1. `s` = skala (np. GUIW / rozdz. bazowej lub wartość z konfiguracji; do ustalenia w pilocie).
2. Mnożnik w 3 typach miejsc: (a) stałe layoutu `(x = (w−500·s)/2, w−140·s)` (katalog: `layout-constants.md`),
   (b) rozmiary tworzonych powierzchni widgetów (0x40C634, 30 miejsc), (c) podział myszy (0x478E03 / 0x478B53).
3. Skalowanie bitmap: istniejący stretch przy blit (0x40D507/0x47B0D7) — barka nowego kodu prezentacji.