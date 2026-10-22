# Weryfikacja: rozszerzenie slotów budynków (ID > 54)

**Data:** 2026-10-08
**Plik wejściowy:** `mod-context.md` (= kopia `.ai/docs/rozszerzenie-slotow-budynkow.md`)
**Zakres:** niezależna weryfikacja analizy na `CN.PLMOD.exe` (pefile + capstone), plikach danych
i edytorach. Adresy w tekście to **RVA** (VA = 0x400000 + RVA), o ile nie napisano inaczej.

> **Werdykt skrócony:** kierunek (rozszerzenie rekordem/flag) jest *sensowny*, ale plan z
> `mod-context.md` **nie nadaje się do wdrożenia tak jak jest**. Lista patchy jest błędnie
> sformatowana, niekompletna, a kluczowe elementy (rozmiar rekordu, walidacje loaderów, pętle
> iteracji, edytory) w ogóle nie są ujęte. Poniżej dowody i propozycja bezpieczniejszej drogi,
> która **eliminuje przesuwanie displacementów**.

---

## 1. Co zweryfikowałem (metodyka)

Napisane od zera skany na `CN.PLMOD.exe`:
- pełny liniowy deasembl (`capstone`, `skipdata=True`) całego `.text` (VA 0x401000..0x4F21CB),
- skan operandów pamięci z `disp` w `[0x515C, 0x1AE08)`,
- skan natychmiastowych: `0x37`(55), `0x38`(56), `0x42`(66), `0x1AE08`, `0x468D50`, `0x151BC`, `0x35A0`,
- deasembl kontekstowy kluczowych funkcji (0x9E60, 0x14270, 0x15340, 0x41534E, 0x4A83B4, 0x4C1EBE),
- skan edytorów `Edytor podstawowy.exe` / `Remik's Editor.exe`,
- licznik sekcji/typów w `CN.PLMOD\types\houses.ini` i `tribetypes.ini`.

### Uwaga o metodyce (ważna!)
`tribedisp.py` używa `md.disasm(...)` **bez `skipdata`**. Capstone w tym trybie *zatrzymuje się na
pierwszym niepoprawnym bajcie*. W tym exe skan kończy się na **RVA 0x1FB05**, czyli przed ~84%
kodu `.text`. Wszystkie liczby w `mod-context.md` („36 displacementów / 41 operandów",
„~22 wystąpienia 0x37") pochodzą z tego **obciętego** przebiegu i są zaniżone.

---

## 2. Błędy i braki w `mod-context.md`

### 2.1 Lista patchy jest w złym formacie (nie da się jej użyć)
Dla wpisu:
```c
{ 0x05193, 3, 4, { 156, 81, 0, 0 }, "disp +9 @0x05193" },
```
- pierwsza kolumna (`rva`) to **stara wartość displacementu** (0x5193), **nie** adres instrukcji;
- `bytes` to **nowa** wartość (0x519C = old+9).
- Dla drugiego wpisu `0x0519C` → `{165,81,...}` = 0x51A5 = old+9; itd. W całej liście
  `bytes == first_column + 9` — to dowód, że pierwsza kolumna to displacement, nie RVA.

`Patch.rva` w `patches.h` jest adresem instrukcji. Wstawienie tam 0x5193 spowoduje zapis
w losowym miejscu `.text` → uszkodzenie kodu. **Ta lista jest nieużywalna.**

### 2.2 Lista jest niekompletna (liczba operacji ≠ 30)
- Dokument deklaruje „36 różnych / 41 operandów", ale wypisuje **30** wpisów.
- W rzeczywistości trzeba załatać **41 operandów** (bo część displacementów powtarza się w
  różnych instrukcjach: 0xAD48 ×3, 0x14B38 ×2, 0x5193 ×2, 0x519C ×2, 0x519C w kilku miejscach).
- Brakuje m.in. wartości `0x5B24`, `0x5F70`, `0x6588`, `0x6740`, `0x6820`, `0x6938`.

### 2.3 `off` nie jest zawsze równe 3
Dokument pisze „size=4, off=3 – typowy". W rzeczywistości **7 operandów ma `off=2`**
(`lea ecx,[esi+disp32]`, kod `8D 8E disp32`): RVA `0x007E67, 0x007EA5, 0x007EB0, 0x007EBB,
0x008033, 0x008146, 0x0081E2`. Użycie `off=3` uszkodzi te instrukcje.

### 2.4 Brak rozmiaru rekordu plemienia
Zwiększenie o 9 B tablicy flag „w środku" rekordu wymaga **powiększenia rekordu**
`0x1AE08 → 0x1AE11`. Stała `0x1AE08` występuje w **4 miejscach**, a `0x468D50` (42×rekord) w **2**:
| RVA | Instrukcja |
|---|---|
| `0x009E00` | `mov dword [ebp-0x20], 0x1AE08` |
| `0x00A032` | `add dword [ebp-0x20], 0x1AE08` |
| `0x00AF4A` | `add esi, 0x1AE08` |
| `0x013F56` | `imul esi, esi, 0x1AE08` |
| `0x00AF51` | `cmp esi, 0x468D50` |
| `0x013EAB` | `mov esi, 0x468D50` (allokacja 42 rekordów) |

Bez tego ostatnie pola „wyciekną" do rekordu sąsiedniego plemienia. Dokument tego nie ujmuje.

### 2.5 Brak kluczowych walidacji i pętli (bez nich ID≥55 w ogóle się nie wczyta)
- **Loader `houses.ini`** `0x01542C`: `cmp eax,0x37 / jae` → **odrzuca logictype ≥ 55**.
  Obecny EtapC tego **nie patchuje** (jego „walidator" to inne miejsce, `0x014289`).
- **Konstruktor** `0x015368`: `mov dword [ebp-4], 0x37` → inicjalizuje tylko **55** rekordów.
  `malloc` podniesiono do 64, ale pętla nadal 55 → rekordy 55–63 niezainicjalizowane.
- **Iteratory** `0x0158D5`, `0x015923`: `cmp …,0x37 / jb` → zatrzymują się na 55.
- **Pętla kopiująca flagi domów** `0x009EA1`: `cmp eax,0x37 / jl` (do bufora `+0x2820`).
- **Guard zapisu flagi** `0x0142F4`: `cmp eax,0x37 / jae`.

Pełny skan pokazuje **74** wystąpienia `0x37` (nie ~22), z czego znacząca część w kodzie
menu/UI powyżej RVA 0x1FB05 (m.in. `0x04A83B4`, `0x04C1EBE`, `0x0A3DD5`, `0x0AA4AB`…).

### 2.6 Pętle menu budowy faktycznie istnieją (ale nie „0x37" liniowo)
`0x4A83B4` (`cmp edi,0x37 / jle`) i `0x4C1EBE` (`cmp ecx,0x37 / jle`) to realne pętle listy
budowania — i **zostały pominięte** przez obcięty skan. Potwierdza to, że „widoczność w menu"
zależy od tych pętli, a nie tylko od displacementów.

### 2.7 Edytory: nie da się wstawić tych samych displacementów
`Edytor podstawowy.exe` / `Remik's Editor.exe`:
- **nie zawierają** stałych `0x1AE08`, `0x468D50`, `0x151BC`, `0x35A0` (skan = 0 trafień),
- mają inny rozkład `.text` (VA 0x401000, rozmiar 0xDE000), ich „displacementy" w zakresie
  `[0x515C,0x1AE08)` to `0x8014, 0x8038, …` — czyli **nie ten sam rekord**.

Wniosek: punkt **B** z `mod-context.md` („dodaj te same 29 displacement-patchy do EtapD")
jest technicznie niemożliwy. EtapD wymaga **własnego** rozpoznania struktur edytora.

### 2.8 Surowce (goods) – ukryte ryzyko
EtapC podnosi walidator goods do `0x61` (97) i `malloc` do `97*0xD0`, ale:
- tablice flag per plemię mają **po 66 B** (`+0x50D8`, `+0x511A`),
- pętle kopiujące `0x009E65`/`0x009E82` nadal `cmp eax,0x42`.
Czyli ID surowca ≥ 66 nie jest realnie obsłużone i może nadpisywać sąsiednie pola.

### 2.9 Drobiazgi
- Wartości w opisie patchy są błędne: `64*0x624 = 0x18900` (nie `0x25140`),
  `97*0xD0 = 0x4ED0` (nie `0x61C0`). Kod `patches.h` liczy poprawnie – mylący jest tylko opis.
- `+9` psuje wyrównanie pól 32-bit do 4 B (x86 to toleruje, ale rośnie liczba niealignowanych
  dostępów; `+12` zachowałoby wyrównanie).

---

## 3. Skala problemu „przesunięcia +9" (dlaczego to ryzykowne)

Pełny skan `[0x515C,0x1AE08)` daje **560 operandów pamięci / 146 różnych** `disp`
(wobec 43/37 w obciętym skanie). Wiele z nich to inne struktury o przypadkowo podobnych
offsetach, ale **znaczna część to prawdziwe pola rekordu plemienia** — używane daleko poza
niskim regionem, np.:

```
0x545CB  mov edx,[edx+0x6168]        0x72B4D  and dword [ecx+0x5CB4],0
0x57BB7  cmp byte [esi+0x5B1C],bl    0x58E36  lea eax,[esi+0x6168]
0x028A44 lea edi,[esi+0xAA18]        0x02D81C lea eax,[esi+eax*4+0x519C]
0x0A592C lea esi,[eax+esi+0x6928]    0x03B32F mov edx,[edi+edx*8+0x14928]
```
Są tu m.in. offsety `0x6168`, `0x5B1C`, `0x5CB4`, `0x6740`, `0x6820`, `0xAA18`, `0xAD48`,
`0x14B38`, `0x14928`, `0x519C`, `0x55FC`, `0x5B24`, `0x5FFC` — czyli te same pola co w
niskim regionie. **Rozmiar „kompletnej" listy przesunięć jest więc nieznany i liczony w setkach,
nie w 40.** Pomyłka w jednym miejscu = cicha korupcja stanu gry/zapisu.

Metoda „łatamy wszystkie `disp` w zakresie liczbowym" dodatkowo grozi uszkodzeniem
**niepowiązanych** struktur (offsety `0x801E…`, `0x94E0…`, `0xA9C0…` itp. należą do innych
rekordów). Właściwa metoda to identyfikacja **bazy rekordu** (data-flow), nie zakres liczbowy.

---

## 4. Rekomendowana, bezpieczniejsza droga (bez przesuwania displacementów)

Kluczowa obserwacja: tablica flag domów `0x515C` (55 B) leży **bezpośrednio przed** tablicą
pojazdów `0x5193` (8 B, pętla 7). Brakuje nam dokładnie **9 B** (55 → 64). Tablica pojazdów
jest używana w **całym `.text` tylko w 2 miejscach**:

| RVA | Instrukcja |
|---|---|
| `0x009EA8` | `cmp byte [ecx+eax+0x5193], 0` |
| `0x0142BB` | `mov byte [eax+esi+0x5193], 1` |

**Pomysł:** przenieść 8-bajtową tablicę pojazdów na koniec rekordu (`+0x1AE08`) i powiększyć
rekord o 8 B (`0x1AE08 → 0x1AE10`). Wtedy:
- flagi domów zajmują `0x515C…0x519B` (64 B) — **bez ruszania czegokolwiek od `0x519C` w górę**,
- żaden `disp` pola istniejącego nie zmienia się → **zero setek patchy displacementów**,
- zmieniamy tylko 2 odwołania do pojazdów + rozmiar rekordu + pętle limitów.

### 4.1 Patche (wariant zalecany)

**a) limity `0x37 → 0x40` (offset wg faktycznego kodowania):**
```c
{ 0x000A003, 2, 1, { 0x40 }, "loop houses"      },   // już jest w EtapC
{ 0x0009EA1, 2, 1, { 0x40 }, "flag copy loop"   },
{ 0x00142F4, 2, 1, { 0x40 }, "flag write guard" },
{ 0x0014289, 2, 1, { 0x40 }, "validator (NC2Logic)" }, // już jest
{ 0x001542C, 2, 1, { 0x40 }, "houses.ini loader validator" },
{ 0x00158D5, 3, 1, { 0x40 }, "iterator 1" },
{ 0x0015923, 2, 1, { 0x40 }, "iterator 2" },
{ 0x0015368, 3, 4, { 0x40, 0, 0, 0 }, "ctor: 64 rekordów" },
```
**b) przeniesienie tablicy pojazdów (`0x5193 → 0x1AE08`):**
```c
{ 0x0009EA8, 3, 4, { 0x08, 0xAE, 0x01, 0x00 }, "vehicles read -> tail" },
{ 0x00142BB, 3, 4, { 0x08, 0xAE, 0x01, 0x00 }, "vehicles write -> tail" },
```
**c) rozmiar rekordu (`0x1AE08 → 0x1AE10`, `0x468D50 → 0x468EA0`):**
```c
{ 0x0009E00, 3, 4, { 0x10, 0xAE, 0x01, 0x00 }, "tribe size" },
{ 0x000A032, 3, 4, { 0x10, 0xAE, 0x01, 0x00 }, "tribe size strided" },
{ 0x000AF4A, 2, 4, { 0x10, 0xAE, 0x01, 0x00 }, "tribe size lookup" },
{ 0x0013F56, 2, 4, { 0x10, 0xAE, 0x01, 0x00 }, "tribe imul" },
{ 0x000AF51, 2, 4, { 0xA0, 0x8E, 0x46, 0x00 }, "tribe array end (cmp)" },
{ 0x0013EAB, 1, 4, { 0xA0, 0x8E, 0x46, 0x00 }, "tribe array malloc" },
```
(wartości wyliczyć programowo; `42*0x1AE10 = 0x468EA0`).

### 4.2 Co jeszcze trzeba zweryfikować w tym wariancie
- Bufor docelowy pętli `0x009E98` (`[edx+eax+0x2820]`) — musi mieć ≥64 B na dom.
- czy nie ma dalszych pętli iterujących flagi domów (poza `0x9EA1`/`0x142F4`).
- zapis/odczyt gry (`.sav`) — pole typu musi pomieścić 63 (bajt wystarcza).
- **dopiero po tym** warto wracać do edytorów.

---

## 5. Wniosek

1. Cel „nowe sloty > 54 widoczne w menu" jest **osiągalny**, ale **nie tym planem**.
2. `mod-context.md` ma konkretne, weryfikowalne wady (format listy, brak rozmiaru rekordu,
   pominięte walidacje/pętle, błędny skan, edytory).
3. Zamiast przesuwać rekord (setki niepewnych displacementów), **przenieść 8-bajtową tablicę
   pojazdów** i wykorzystać zwolnione 9 B na flagi domów. To redukuje zmianę do kilkunastu
   punktowych patchy + rozmiar rekordu.
4. EtapD (edytory) to **osobne** przedsięwzięcie — nie współdzieli struktur z grą.
5. Listę patchy należy **generować skryptem z binarki** (RVA + off + długość liczone z kodowania),
   a nie przepisywać ręcznie.

### Skrypty pomocnicze (do zatwierdzenia)
Proponuję dodać `.ai/scripts/gen_tribe_patches.py`, który wypisze gotowe wpisy `Patch[]`
(RVA/off/size/bytes) dla wariantu 4 oraz zweryfikuje każdy offset przez deasembl instrukcji.
