# Format plików `.fnt` (Cultures: Northland / CN mod) — pełna specyfikacja

**Status:** odwrócony w 100% (statyczna analiza exe, 06.10.2026). Round-trip
decode→encode **bajt-w-bajt identyczny** dla `font08/10/12.fnt` — dowód poprawności.
Kod: `.ai\scripts\fnt_scale.py` (parser + skaler + renderer).

## Łańcuch ładowania w exe

| Element | Adres | Opis |
|---|---|---|
| stringi | `0x50c33c` font08, `0x4fe468` font10, `0x50c320` font12, `0x50c300` fontdebug | ścieżki bez prefiksu moda |
| rejestracja | `0x4e2514..0x4e254b` | `fonts[0..3]` w tablicy globalnej `0x569aa0` = [font08, font10, font12, fontdebug] |
| wrapper | `0x41074c` | rozwiązuje ścieżkę (`0x405e4c`), woła parser, zamyka (`0x405f8c`) |
| parser typów | `0x410624` | czyta `u32 type` + `u32 ver`, switch typu → konstruktor (typ **1013** = font → alloc 0x18, ctor `0x4396fb`; typ **1012** → alloc 0x3c, ctor `0x43988d`; typ **1001** → alloc 0xc, ctor `0x42f949` = tablica bajtów `len + data`) |
| metoda fontu | `0x439633` | `CharWidth(c) = left + w + font.tracking + 1` |
| metoda fontu | `0x43965b` | `CharHeight(c) = top + h + 1` |
| pomiar tekstu | `0x43967d` / `0x4396b7` | suma advance / max wysokości komórki |
| **indeks glifu** | `0x43963e`, `0x4399a2` | `idx = bajt znaku − 0x20` (zakres 0..223 = znaki 0x20..0xFF) |
| pobranie glifu | `0x43999e` `GetGlyphInfo` | zwraca `rekord+4` albo 0 (brak) |
| hit-test piksela | `0x4399c2` | `rowTable[row]` → (startCol, offset) → RLE |

## Struktura pliku

```
u32 type = 1013          # tag typu obiektu (font)
u32 ver  = 0
u32 fieldA               # 223 w fontach głównych (zakres indeksów = count−1); 116 w fontdebug
u32 height               # interlinia: 8 / 10 / 12 (font08/10/12)
  u32 type = 1012        # tag tablicy glifów
  u32 ver  = 0
  u32[7] blok:
    [0] base   = 0       # dodatkowy offset indeksu (0)
    [1] count            # liczba glifów = 224 (fontdebug: 221)
    [2] len(arr1)        # bajty danych RLE
    [3] rows             # liczba wpisów tablicy wierszy = Σ h glifów obecnych
    [4] rows             # kopia pola [3]
    [5] emptyRows        # liczba wpisów 0xFFFFFFFF w tablicy wierszy (= rows − wiersze z danymi)
    [6] 0                # nieznane (0 we wszystkich próbkach)
  3 × tablica typu 1001:  u32 type=1001, u32 aux=0, u32 len, u8 data[len]
    arr0 = rekordy glifów:  count × 24 B
    arr1 = dane pikseli RLE
    arr2 = tablica wierszy: rows × u32
```

Plik **nie ma trailing data** — parser zjada dokładnie `size` bajtów (zweryfikowane
dla wszystkich 4 fontów UI + kopii briefingowych o tej samej strukturze).

### Rekord glifu (arr0, 24 B, 6 × u32)

| Off | Pole | Znaczenie |
|---|---|---|
| +0 | `enc` | 0 = brak glifu (spacja 0x20, NBSP 0xA0; fontdebug: ~100 znaków), **1** = RLE 8-bit/piksel, 4 = RLE 16-bit/piksel (nie występuje w fontach UI) |
| +4 | `left` | bearing poziomy (może być −1 jako `0xFFFFFFFF`) |
| +8 | `top` | przesunięcie pionowe glifu w komórce (y rośnie w dół; baseline ≈ top+h liter x-height) |
| +0xc | `w` | szerokość = **advance podstawowy** (`CharWidth = left + w + tracking + 1`) |
| +0x10 | `h` | wysokość bitmapy (wierszy w tablicy wierszy) |
| +0x14 | `rowBase` | pierwszy wpis w arr2 dla tego glifu (glify obecne tworzą ciągłą sekwencję od 0) |

### Tablica wierszy (arr2)

Każdy wiersz = 1 × u32:

* `0xFFFFFFFF` — wiersz pusty (bez atramentu), nie liczy się w RLE,
* `(startCol << 22) | offset` — `startCol` (10 bitów) = kolumna, od której zaczyna się
  strumień RLE (kolumny przed nią są przezroczyste); `offset` (22 bity) = offset w arr1.

### Strumień RLE wiersza (arr1)

```
b = dane[p++]
b == 0            → koniec wiersza
b & 0x80          → SKIP  (przezroczyste)  n = b & 0x7F, **bez** bajtów danych
b & 0x7F (b < 0x80) → LITERAL n pikseli, n bajtów danych w arr1
```
Piksel = indeks palety (`0` = przezroczysty; fonty UI używają wartości
`0, 128, 160, 192, 255` = 5 poziomów AA/cienia; fontdebug: `0, 255`).
W fontach UI **w literałach nie występują zera** → 0 ⇔ przezroczystość jest jednoznaczne.

## Semantyka kodowa

- Kodowanie tekstu w grze: **CP1250** (polskie znaki ą=0xE1 … ż=0xBF; wszystkie
  mieszczą się w indeksach 0..223 = znaki 0x20..0xFF po odjęciu 0x20).
- Krój: `Data\gui\fonts\{font08,font10,font12,fontdebug}.fnt` — **brak nadpisania
  moda** (nie ma `CN.PLMOD\data\gui\fonts`), więc podmiana = pliki w `Data`.
- Spacja/tab: mierzone jak znak `'i'` (`push 0x69` w `0x43967d`), rysowane bez glifu.
- `fieldA`: zakres indeksów (count−1); **nie skalować** (to nie jest metryka).
- `height`: interlinia — **skalować ×k** razem z `left/top/w/h` glifów.
- Palety kolorów: `font_white/dark/red/dimmed.pcx` wczytane po fontach (`0x4e2550+`),
  `font.tracking` (pole `+0xc` obiektu) ustawiane na −1/−2 dla fontów UI.

## Skalowanie (protokół ×k)

1. Dekoduj: rekordy → macierze `h × w` (per wiersz: startCol + runs).
2. Macierz nearest-neighbor ×k (każdy piksel → k×k).
3. Nowe rekordy: `left×k, top×k, w×k, h×k`, `rowBase` przeliczony narastająco
   (glify z `enc=0` — kopiowane 24 B bez zmian, nie zajmują wierszy).
4. Nowe wiersze: `startCol = pierwsza niezerowa kolumna`, runs zredagowane od niej
   (skip ≤127, literal ≤127, `0` na koniec); wiersz całkiem pusty → `0xFFFFFFFF`.
   `emptyRows` = liczba takich wierszy; `len(arr1)`, `rows` przeliczone.
5. Interlinia `height×k`. `fieldA`, `base`, `count`, pola [6] — bez zmian.
6. Walidacja: ponowny parse (zjada 100% bajtów) + `decode(nowy) == nearest(decode(oryg))`.

## Wygenerowane pliki (Etap 2/3A, 06.10.2026)

| Źródło | Wynik 2× | Rozmiar | Instalacja |
|---|---|---|---|
| font08 (21 354 B, h=8) | `font16.fnt` (49 190 B, h=16) | ×2,3 | `Data\gui\fonts\font08.fnt` podmieniony (`.orig` backup) |
| font10 (26 265 B, h=10) | `font20.fnt` (63 118 B, h=20) | ×2,4 | jw. `font10.fnt` |
| font12 (29 223 B, h=12) | `font24.fnt` (71 432 B, h=24) | ×2,4 | jw. `font12.fnt` |

Kopie `font16/20/24.fnt` zostają w `Data\gui\fonts\` (inertne — loader czyta tylko
nazwy 08/10/12/debug) jako zapas pod opcję B1 (patch exe „tablicy wyboru fontów").

## Jeszcze nieskalowane (kolejne partie)

- `Data\text\pol\hypertext\{credits,history,ingamehelp}\fonts\font10/12.fnt`,
  `fonthead16bld.fnt` (16 px bold — nagłówki briefingów; decyzja: ×2 → 32 px?).
- `CN.PLMAPS\**\Fonts\*.fnt` (fonty briefingów per mapa; część wariantów ma inne
  rozmiary = starsze wersje formatu — parser waliduje `consumed==size`, w razie
  `AssertionError` pomijamy i analizujemy osobno).
