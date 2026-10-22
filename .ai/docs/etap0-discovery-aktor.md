# Etap 0 — Wyniki discovery: struktura aktora CN.PLMOD

**Data:** 2026-10-09
**Narzędzia:** `bandmap.py`, `sites.py`, `seg.py`, `scan_stride.py`, `refs_class.py`, `xref.py`
(helpers, `C:\Users\Michael1099\AppData\Local\Temp\opencode\`).
**Konwencja adresów:** RVA (VA − 0x400000). Plik = RVA − 0x1000 dla `.text`.

---

## 1. Struktura aktora (element na gracza) — potwierdzona

- Baza globalna elementów: `[0x510BC4]`.
- **Liczba graczy: 20 (`0x14`).** Stride elementu: `0x4A80`.
- Pula elementów: `20 × 0x4A80 = 0x5D200` (porównania `cmp ...,0x5D200` — 28 ref).
- Tablice **per plemię (42 plemiona)**, upakowane co do bajtu (koniec jednej = początek
  następnej):

| Pole | Baza | Stride | Region [baza, koniec) | Rozmiar = 42×stride | Werdykt |
|---|---|---|---|---|---|
| jobs A | `0x18` | `0x38` (56) | `0x18..0x948` | `0x930` | bez zmian |
| jobs B | `0x948` | `0x38` (56) | `0x948..0x1278` | `0x930` | bez zmian |
| **surowce A** | `0x1278` | `0x42` (66) | `0x1278..0x1D4C` | `0xAD4` | **rozszerzana** |
| **surowce A2** | `0x1D4C` | `0x42` (66) | `0x1D4C..0x2820` | `0xAD4` | **rozszerzana** (patrz §3) |
| **domy A** | `0x2820` | `0x37` (55) | `0x2820..0x3126` | `0x906` | **rozszerzana** |
| **domy B** | `0x3126` | `0x37` (55) | `0x3126..0x3A2C` | `0x906` | **rozszerzana** |
| pojazdy | `0x3A2C` | 7 | `0x3A2C..0x3B52` | `0x126` | bez zmian |
| pola skalarne | `0x3B52` | — | `0x3B52..0x3C78` | — | bez zmian (`0x3B80`, `0x3C00/3C01`) |
| **surowce B** | `0x3C78` | **`0x38` (56!)** | `0x3C78..0x45A8` | `0x930` | **rozszerzana + fix stride** |
| pola ogonowe | `0x45A8` | — | `0x45A8..0x4A80` | — | bez zmian |

Suma kontrolna: `0x18+0x930+...` domyka się do `0x4A80` dokładnie.

Element aktora wypełniony niemal do `0x4A80` (ostatnie pole `0x4A37`, ~`0x41` B wolne).

## 2. Wzorzec dostępu

Adres pola = `[0x510BC4] + gracz×0x4A80 + plemię×stride + baza_tablicy + indeks`.

Występują **dwie formy**:
1. indeks w rejestrze: `cmp/mov byte [reg + idx + Baza]` (np. `0x1278`, `0x2820`, `0x3126`,
   `0x3C78`, `0x3A2C`);
2. **zaszyte „pośrednie" stałe** = `Baza + plemię×stride + sub` (np. `0x1770` = surowceA
   plemię 19 sub `0x12`; `0x2A48` = domyA plemię 10 sub 2; `0x3D60` = surowceB plemię 4
   sub 8). Przy relokacji **każda taka stała musi być przeliczona** na
   `NOWA_BAZA + plemię×NOWY_STRIDE + sub`, a nie przesunięta o deltę.

### Liczba stałych (baza + pośrednie) w pasmach — z `sites.py`
| Tablica | Zakres pasma | Liczba stałych | Uwagi |
|---|---|---|---|
| surowce A | `0x1278` + `0xAD4` | 42 | część niezwiązanych (np. `0x1581` = inna tablica) |
| surowce A2 | `0x1D4C` + `0xAD4` | 36 | sporo śmieci z desyncu (absolutne, `fstp/fdivr/imul z [..]`) |
| domy A | `0x2820` + `0x906` | 28 | jw. (absolutne `[0x283d]`, `[0x28a0]`, …) |
| domy B | `0x3126` + `0x906` | 10 | parę śmieci |
| surowce B | `0x3C78` + `0x930` | 22 | na siatce `0x38` — patrz §4 |
| pojazdy | `0x3A2C` + `0x126` | 1 | tylko baza |

Generator (Etap 1) musi: (a) odsiać odwołania absolutne/obcych strukturs, (b) dla każdej
reszty wyliczyć `(plemię, sub)` i przeliczyć na nowy offset.

## 3. Werdykty otwartych pytań

### Q1: czym są `0x1D4C` i `0x45A8`?
- **`0x1D4C` = pełnoprawna druga tablica surowców („surowce A2")**: region
  `0x1D4C..0x2820` ma rozmiar dokładnie `42×0x42`; odczyty inicjalizacji
  (`0x9892` — czyszczenie w pętli surowcowej) i logiki (`0x9FC9` — `cmp byte [esi+ebx+0x1D4C]`
  przy `esi` przesuniętym o `0x42`) potwierdzają indeksowanie jak surowce.
- **`0x45A8` = zwykłe pola po surowcach B** (ref `mov [esi+edi*4+0x45A8]` z
  `imul edi,edi,0x12A0` w `0x91F7` — najpewniej inny obiekt/`esi`), zostaje na miejscu.
- Wniosek: rozszerzamy **trzy** tablice surowców (A, A2, B) i **dwie** domów (A, B).

### Q2: czy surowce B mają stride `0x38` czy istnieje ścieżka `0x42`?
- **Stride `0x38` potwierdzony.** W pasmie `0x3C78..0x45A8` wszystkie zaszyte stałe leżą
  na siatce `0x38` (`sub < 0x38`); brak jakiegokolwiek dispa na siatce `0x42`. Pętla
  kopiowania flag używa `esi = 0x38` (tj. stride jobs) dla `+0x3C78`, a granica
  `cmp eax,0x42` (66 surowców) jest rzutowana na węższy stride → surowce 56..65
  nachodzą na początek kolejnego plemienia. **To bug/nachodzenie silnika** — przy
  rozszerzeniu ujednolicamy stride surowców B do `NEW_GOOD_MAX`.

### Q3: czy 246 użyć `0x4A80` dotyczy aktora?
- **Tak, bez wyjątku.** Klasyfikacja (skrypt `refs_class`): `208× imul + 33× add`
  (= 241 realnych, konwersja gracz→element i chodzenie po elementach) + 5 śmieci
  z desyncu (`or/sar/sbb/cmp`). Brak obcych struktur.
- Dodatkowo rezerwę puli `0x5D200` (20×0x4A80) czyta **52** miejsca (28 cmp + 14 mov
  + ..) — trzeba je też zaktualizować (nowy rozmiar puli).

### Q4: `NEW_HOUSE_MAX` / `NEW_GOOD_MAX`
- Rekomendacja: **oba = `0x7F` (127)** — pełny zapas bajtowy (suflit 0x7F ze znakowymi
  `jl/jge`), odstęp od niebezpiecznego `0x80`.
- Orientacyjny rozmiar nowego elementu: `0x4A80 + 5×42×0x7F = 0x4A80 + 0x6836 = 0xB2B6`
  (~45,7 KB), pule ×20 ≈ 0.91 MB (po wyrównaniu `0xB300` → `0xDFC00`).

### Q5: zapis gry
- `.sav` = **binarny, chunkowany**: nagłówki `hoix<TAG>CI` + 4-bajtowa długość
  (np. `hoixvgsx`, `hoixigsx`, `hoixneCI`, `hoixitCI`, `hoixgcCI`, `hoixpmCI`).
- Brak surowej stałej `0x4A80` w pliku (0 trafień) → zapis nie jest „sztywną kopią"
  elementów; szczegóły serializacji luster do zlokalizowania (ciąg dalszy discovery /
  Etap 6). Ryzyko R5 pozostaje: nowe liczniki zmienią układ danych w chunkach.
- Test: zapis + wczytanie po rozszerzeniu (plan testów pkt 3).

## 4. Inwentarz stałych do patchowania (Etap 1 — dane wejściowe)

| Stała | Rola | Liczba site'ów | Uwagi |
|---|---|---|---|
| `0x4A80` | stride elementu | 241 (208 imul + 33 add) | wszystkie realne |
| `0x5D200` | rozmiar puli (20×elem) | 52 | do nowego rozmiaru |
| `0x37` | stride/limit domów | 15 (14 imul + 1 add w pętli) | do `NEW_HOUSE_MAX` |
| `0x42` | stride/limit surowców | 45 (43 realne; `add al,0x42` = śmieci) | do `NEW_GOOD_MAX` |
| `0x38` | stride jobs + surowców B | 147 | **są to głównie jobs (bez zmian!)**; site'y surowców B trzeba wyodrębnić (wg sąsiedztwa bazy `0x3C78`) — do zrobienia w generatorze |
| 7 | stride pojazdów | 11 | bez zmian |
| bazy pasm | `0x1278/0x1D4C/0x2820/0x3126/0x3C78` | patrz §2 | wszystkie stałe (w tym pośrednie) |

### Kluczowe fragmenty do przepięcia w pętli kopiowania flag (`0x9DC1`–`0x9FC0`)
- `0x9DF6` `ebp-0x10 = 0x42` (stride surowców), `0x9E00` `ebp-0x20 = 0x1AE08` (rekord),
  `0x9E07` `ebp-0x18 = 0x37` (stride domów), `0x9E15` `ebp-0xc = 1` (nr plemienia),
  `0x9E0E` `ebp-0x1c = 7` (pojazdy).
- Granice pętli: `0x9E65` `0x42`, `0x9E82` `0x42` (surowce B), `0x9EA1` `0x37`,
  `0x9EC0` 7, `0x9F44` `0x38` (jobs).
- `0x9E57`/`0x9E5C` surowce A: dest `actor + 0x42 + good + 0x1278`
  (konwencja: offset plemienia liczony jako `1×stride` wprost).
- `0x9E76/0x9E79` surowce B: dest `actor + 0x38 + good + 0x3C78` ← **stride `0x38` do fixa**
  na `NEW_GOOD_MAX` (separacja wskaźnika od `esi` jobs).

## 5. Otwarte drobiazgi (nie blokują)
1. Dokładna rola tablicy „surowce A2" (dodatkowe flagi rynku/produkcji?) — wpływa tylko
   na liczbę przenoszonych tablic, nie na mechanikę.
2. Segmentacja 147 site'ów `0x38` na „jobs" vs „surowce B" — do zrobienia w generatorze
   (heurystyka: stałe w pasmie surowców B + data-flow).
3. Lokalizacja serializacji aktora w `.sav` (chunk `hoix…`) — Etap 6 / dalsze discovery.
4. Alokacja puli: `mov edi,0x5D200` (`0x185B8`) i zapis do `[0x510BC4]` (kandydaci
   `0x8087`, `0x8B77`) — potwierdzić procedurę `malloc`.

## 6. Narzędzia
Wszystkie skrypty działają na `CN.PLMOD.exe` (capstone + pefile, skipdata) i zapisują
pełne listy do plików: `strides.txt`, `s_goodsA.txt`, `s_1d4c.txt`, `s_housesA.txt`,
`s_housesB.txt`, `s_goodsB.txt`, `s_veh.txt`, `s_gap.txt`, `refs_4a80` (w stdout).
Generator Etapu 1 może je śmiało ponownie wygenerować metodami binarnymi.