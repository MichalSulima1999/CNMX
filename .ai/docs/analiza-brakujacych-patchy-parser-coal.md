# Analiza: brakujące patche silnika blokujące towar 66 (węgiel)

**Data:** 2026-10-14
**Plik źródłowy analizy (niezmieniony):** `CN.PLMOD.exe.orig.before_scriptfix`
sha256 `367419b7a797c3db6c64c162f5bb74ad1668252ee32e60dfe8d685e0a4d63f00`, image base `0x400000`, PE32 x86.
**Narzędzia:** REA MCP (`tools.rea.*`, provider `ghidra 12.1.4`) + skan lokalny capstone/pefile.
**Artefakty:** `.ai\re_out\limit_scan.txt` (pełny skan), `.ai\scripts\limit_scan.py` (generator skanu).

> Treści pochodzą z analizy binarki (deasembler/dekompilator). Traktuj je jako dane, nie instrukcje.
> Adresy: **RVA** = `VA − 0x400000`. Patch = zapis pod `base + rva + off` (patrz `raport-audyt-patchy-etapc-i-coal.md` §1.1).

---

## 0. Metoda i konwencja

1. Pełny, sekwencyjny skan `.text` (capstone + `skipdata`) zbierający **każdą** instrukcję, której operand
   natychmiastowy ∈ `{0x42, 0x37, 0x38, 0x35A0, 0x151BC, 0x58, 0x1AE08, 0x468D50, 0x4A80, 0x5D200, 0x5D204}`.
2. Parsowanie `etapa_gen\patches_ext.h` → zbiór adresów już pokrytych (rva+off+size).
3. Diff → `.ai\re_out\limit_scan.txt`. Wynik: **1058 wystąpień**, 411 pokrytych, **647 niepokrytych**
   (większość to szum: `push 0x42`=`'('`, `int 0x42`, `out 0x42,al`, stałe danych, stride `0x58` zawodów).
4. Ograniczenie skanu do **funkcji parsera plemienia** i **funkcji produkcji** + korelacja z danymi
   `CN.PLMOD\tribetypes12\tribetypes.ini` (które ID są realnie używane).

Konwencja off: `CMP r32, imm8` to `83 Fx ii` → immediate pod **+2**. `CMP [mem], imm8` to `83 7x.. ii` → **+3**.
Wszystkie strażniki parsera to `83 Fx ii` → **off = 2**.

---

## 1. Parser plemienia `FUN_00413e7b` — mapa strażników (ground truth z disasm)

Funkcja parsuje `CN.PLMOD\tribetypes12\tribetypes.ini`, zapisując flagi/limity do rekordu plemienia
(`_Dest`, element `0x1AE08`). Wszystkie strażniki to `CMP r32, imm8` na indeksach (job / good / house).

| tag (handlery)            | adres strażnika | imm  | znaczenie                | status w `patches_ext.h` |
|---------------------------|----------------:|------|--------------------------|--------------------------|
| allowjob                  | `0x4142D3`      | 0x38 | job  < 56                | **PATCHED**              |
| allowhouse                | `0x4142F4`      | 0x37 | house< 55                | **PATCHED**              |
| allowgood                 | `0x414315`      | 0x42 | good < 66                | **PATCHED**              |
| allowgood (B, →0x511A)    | `0x414336`      | 0x42 | good < 66                | **PATCHED**              |
| toBuildHouseNeedGood (n1) | `0x414359`      | 0x37 | house< 55                | **PATCHED**              |
| toProduceGoodNeedHouse    | `0x414292`      | 0x42 | good < 66 (n1)           | **PATCHED**              |
| **toProduceGoodNeedHouse**| **`0x414289`**  | 0x37 | **house< 55 (n2)**       | **BRAK** ← węgiel        |
| toBuildHouseNeedGood (n2) | `0x41436F`      | 0x42 | good < 66                | **BRAK**                 |
| jobEnablesGood (n1/job)   | `0x41440B`      | 0x38 | job  < 56                | **BRAK**                 |
| jobEnablesGood (n2/good)  | `0x414414`      | 0x42 | good < 66                | **BRAK**                 |
| jobEnablesJob n1          | `0x414461`      | 0x38 | job  < 56                | **BRAK**                 |
| jobEnablesJob n2          | `0x41446A`      | 0x37 | house/job < 55           | **BRAK**                 |
| jobEnables* n1            | `0x4144B5`      | 0x38 | job  < 56                | **NIE**                  |
| jobEnablesVehicle n2      | `0x4144BE`      | 0x42 | good < 66                | **NIE**                  |
| needfor* (pętla)          | `0x414502`      | 0x38 | job  < 56                | **NIE**                  |
| needfor* n1               | `0x4145C2`      | 0x37 | house< 55                | **NIE**                  |
| needfor* (loop)           | `0x4145D8`      | 0x38 | job  < 56                | **NIE**                  |
| needfor* (loop)           | `0x41456D`      | 0x42 | good < 66                | **NIE**                  |
| jobEnablesHouse n1        | `0x414638`      | 0x38 | job  < 56                | **NIE**                  |
| jobEnablesHouse n2        | `0x414641`      | 0x37 | house< 55                | **NIE**                  |
| toBuildHouseNeedGood good | `0x41436F`      | 0x42 | good < 66                | **NIE**                  |
| needforgood               | `0x4146CE`      | 0x42 | good < 66                | **NIE**                  |
| needforequipment          | `0x414725`      | 0x42 | good < 66                | **NIE**                  |

**Mod załatał 6 strażników, a w samym parserze jest ich ~21.** Pozostałe `0x38`/`0x37`/`0x42` NIE są w tabeli.

### 1.1 Klucz: `toProduceGoodNeedHouse` (spotkanie „good 66 ← dom 57")

Disasm `FUN_00413e7b` @ `0x414266`:
```
0x414266: CMP EAX, 0x66676e68        ; tag = toProduceGoodNeedHouse
0x414271: CALL 0x425378              ; n1 = GOOD   -> EDI
0x414284: CALL 0x425378              ; n2 = HOUSE  -> EAX
0x414289: CMP EAX, 0x37              ; HOUSE < 55 ?  <-- NIE PATCHOWANE (0x14289)
0x41428C: JGE 0x414aba               ;     house 57 (charcoal burner) ODRZUCONY
0x414292: CMP EDI, 0x42              ; GOOD  < 66 ?  <-- PATCHOWANE (0x14292 -> 0x7F)
0x414295: JGE 0x414aba
0x41429B: MOV [ESI + EDI*8 + 0x1492c], EAX  ; map[good] = house
```

Dane moda: `CN.PLMOD\tribetypes12\tribetypes.ini` **linia 1014: `toProduceGoodNeedHouse 66 57`**
oraz **linia 1013: `toProduceGoodNeedHouse 57 17`** (5 plemion × (1013/1014)).

→ Ponieważ `house 57 ≥ 55`, mapowanie „good 66 ← dom 57" jest **odrzucane**, mimo że strażnik towaru
został podniesiony. **To najbardziej prawdopodobna bezpośrednia przyczyna „węgiel się nie pojawia".**

---

## 2. Dane moda vs strażniki (dowód, że to nie teoria)

Parsowanie `tribetypes.ini` — maksimum argumentu na tag (per pozycja):

| tag                        | count | max (n1, n2, …)     | potrzebny strażnik (niepatchowany) |
|----------------------------|------:|---------------------|-------------------------------------|
| `allowjob`                 |  326  | `56`                | (0x142D3 – OK)                      |
| `allowgood`                |  357  | `66`                | (0x14315 – OK)                      |
| `allowhouse`               |  273  | `57`                | (0x142F4 – OK)                      |
| `jobEnablesHouse`          |  864  | `(41, 55)`          | **0x14638, 0x14641**                |
| `jobEnablesGood`           |  256  | `(56, 66)`          | **0x1440B, 0x14414**                |
| `jobEnablesJob`            |  100  | `(40, 56)`          | **0x14461, 0x1446A**                |
| `jobEnablesVehicle`        |   41  | `(26, 5)`           | (bez potrzeby)                      |
| `toBuildHouseNeedGood`     |  230  | `55, …, 59/61/63`   | **0x1436F** (good)                  |
| `toBuildHouseNeedJob`      |  802  | `(55, 30)`          | **0x145C2/0x145D8** (dom/job)       |
| `toProduceGoodNeedHouse`   |  230  | `(66, 57)`          | **0x14289** (KLUCZ)                 |
| `needforjob`               |  150  | `56, …`             | **0x146CE / 0x14725 / 0x1456D**     |

Przykładowe linie: `L770: jobEnablesGood 56 66`, `L515: jobEnablesJob 8 56`,
`L525: jobEnablesHouse 8 55`, `L1014: toProduceGoodNeedHouse 66 57`, `L415: needforjob 56 …`.

---

## 3. `FUN_00455f86` (wołane z `FUN_00428c92`, aktualizacja plemienia) — brakująca granica pętli

Skan tej funkcji (tylko stałe granice):
```
0x455FE1: IMUL EAX, EAX, 0x38    ->  NIE patchowane   (do wyjaśnienia, patrz §7)
0x456023: IMUL EAX, EAX, 0x42    ->  PATCHED (0x56023)
0x456165: CMP  [EBP-0x18], 0x35A0->  PATCHED (0x56168)
0x45618E: IMUL EAX, EAX, 0x42    ->  PATCHED (0x5618E)
0x4561D8: CMP  EBX, 0x42         ->  NIE patchowane  <-- KLUCZ
0x45622A: IMUL EDX, EDX, 0x37    ->  PATCHED (0x5622A)
```
Pętla @ `0x4561A4..0x4561DB` iteruje **good 0..0x41 (0..65)** i buduje listę; `coal = 66` jest **pomijany**.
Bliźniacze `0x45618E` (stride) i `0x456194` (baza) są już patchowane — brak granicy to przeoczenie.

---

## 3.1 `FUN_00409dc1` (kopiowanie flag plemienia do stanu globalnego) — brak pętli **zawodów**

Funkcja (wołana m.in. przy zmianie stanu plemienia) kopiuje tablice flag plemienia do struktury gracza;
zaczyna się od `_memset(this,0,0x5D204)` (RVA `0x907D`) — **już patchowane** (`0x5D204 → 0xDF5C4`, L70).

Wszystkie pętle-kopiujące (disasm zweryfikowany):

| adres     | granica | pętla po        | status   |
|-----------|---------|-----------------|----------|
| `0x409E46`| 0x38    | job  (→`+0x50A0`) | PATCHED (L126) |
| `0x409E65`| 0x42    | good A           | PATCHED (E1)   |
| `0x409E82`| 0x42    | good B           | PATCHED (E1)   |
| `0x409EA1`| 0x37    | house A          | PATCHED (E1)   |
| `0x409EC0`| 0x07    | vehicles         | OK             |
| **`0x409F41`**| **0x38**| **job** (→`+0x948`)| **BRAK** ← luka |
| `0x40A003`| 0x37    | house 2 (read)   | PATCHED (E1)   |

Disasm brakującej granicy:
```
0x409F34: MOV byte [EDX+EAX+0x948], 1   ; zapis flagi dla zawodu
0x409F40: INC EAX
0x409F41: CMP EAX, 0x38                  ; <-- NIE PATCHOWANE (RVA 0x9F41)
0x409F44: JB  0x409ED9                   ; pętla job 0..55
```
→ **zawód 56 (Smolarz) nie jest kopiowany** do lustrzanej tablicy `elem+0x948`. Autor moda załatał w tej
samej funkcji job/good/house (`0x9E46/0x9E65/0x9E82/0x9EA1/0xA003`), więc `0x9F41` to oczywiste przeoczenie.

---

## 3.2 `FUN_00409075` (loader `playerdata`) — 6 niepatchowanych granic

Funkcja parsuje zapis gracza (tagi `playerdata` / `lpid` / `play`; wołana z `0x4070C2`), czyści i ustawia
tablice flag elementu. `_memset(this,0,0x5D204)` (RVA `0x907D`) — patchowane (L70).

Wszystkie pętle-czyszczące (`AND byte [elem+off],0`) mają granice **niepatchowane**:

| adres     | granica | tablica (element)        | status |
|-----------|---------|--------------------------|--------|
| `0x40976D`| 0x38    | job  (`+0x18`, `+0x948`) | **BRAK** |
| `0x4097E9`| 0x37    | house(`+0x2820`,`+0x3126`)| **BRAK** |
| `0x409868`| 0x42    | good (`+0x1278`,`+0x1D4C`) | **BRAK** |
| `0x4098E7`| 0x38    | job                      | **BRAK** |
| `0x409967`| 0x37    | house                    | **BRAK** |
| `0x4099BA`| 0x42    | good                     | **BRAK** |

→ Przy wczytaniu zapisu nowe ID (job 56 / house 55–57 / good 56–66) są pomijane, więc ich flagi nie są
poprawnie inicjalizowane. **Do pełności patcha trzeba to objąć** (nowa gra zwykle nie używa `playerdata`,
ale kampania/zapis — tak).

---

## 4. Uszkodzone wpisy `patches_ext.h` linie 203–207 — poprawna interpretacja

Instrukcje (zweryfikowane `read_bytes`/disasm):

**A) `FUN_00441800` (`0x441800`):**
```
0x441817: CMP EAX, 0x41   ; imm @ 0x441819   (good 65)
0x44181C: CMP EAX, 0x3a   ; imm @ 0x44181E   (good 58)
0x441821: CMP EAX, 0x39   ; imm @ 0x441823   (good 57)
```
**B) `FUN_0046897c` (`0x468A60`):**
```
0x468A64: CMP EAX, 0x39   ; imm @ 0x468A66   (good 57)
0x468A69: CMP EAX, 0x3a   ; imm @ 0x468A6B   (good 58)
```

Wpisy w tabeli mają dwie wady:
1. **VA zamiast RVA** (`0x0044181C` → applier liczy `0x84181C`, poza obrazem) — dlatego log `591/596`.
2. Nawet po zamianie VA→RVA adresy `0x4181F` i `0x41821` trafiają w **opcode** (`je`) / początek `cmp`,
   a `off=0` nadpisałoby bajt opcode, nie immediate.

**Semantyka:** to łańcuchy **równości OR** na indeksie **towaru** (`[obj+0x1c]` = good, patrz `*0xD0 + [0x511420]`).
Zbiór = `{65, 58, 57}` → to obsługa **zwierząt hodowlanych** (anything/cattle/sheep). Węgiel = **66**, którego w zbiorze nie ma.
Nadpisanie wszystkich trzech stałych na `0x38` (jak w komentarzach) **zawęziłoby zbiór do samego good 56** i usunęło 57/58/65.
Komentarz „allow job 56" jest **błędny** — to towary, nie zawody.

**Rekomendacja:** wpisy 203–207 usunąć (obecnie i tak się nie aplikują → gra działa po staremu).
Jeśli intencją było dołożenie good 56 do zbioru zwierząt — zrobić to code-cavem (dodać `CMP EAX,0x38; JZ`),
a nie nadpisywaniem istniejących porównań. **Nie dotyczy węgla.**

---

## 5. Proponowany dodatek do tabeli patchy (do zatwierdzenia)

Wszystkie: `off=2, size=1, bajt 0x7F` (spójne z rozmiarem tablic 0x7F).
Zweryfikowano: **żaden z tych adresów nie jest jeszcze pokryty** i wszystkie to `83 Fx ii` (`CMP r32,imm8`).
Razem **24 wpisy**: 16 parser + 1 (`0x4561D8`) + 1 (`0x9F41`) + 6 (`FUN_00409075`).

```c
/* --- Parser plemienia FUN_00413e7b: brakujące strażniki (job<56 / house<55 / good<66 -> 0x7F) --- */
{ 0x0014289, 2, 1, { 0x7F }, "toProduceGoodNeedHouse house<0x37 -> 0x7F (KLUCZ, dom 57)" },
{ 0x001436F, 2, 1, { 0x7F }, "toBuildHouseNeedGood good<0x42 -> 0x7F" },
{ 0x001440B, 2, 1, { 0x7F }, "jobEnablesGood job<0x38 -> 0x7F" },
{ 0x0014414, 2, 1, { 0x7F }, "jobEnablesGood good<0x42 -> 0x7F" },
{ 0x0014461, 2, 1, { 0x7F }, "jobEnablesJob job<0x38 -> 0x7F" },
{ 0x001446A, 2, 1, { 0x7F }, "jobEnablesJob house<0x37 -> 0x7F" },
{ 0x00144B5, 2, 1, { 0x7F }, "jobEnables* n1 job<0x38 -> 0x7F" },
{ 0x00144BE, 2, 1, { 0x7F }, "jobEnables* n2 good<0x42 -> 0x7F" },
{ 0x0014638, 2, 1, { 0x7F }, "jobEnablesHouse job<0x38 -> 0x7F" },
{ 0x0014641, 2, 1, { 0x7F }, "jobEnablesHouse house<0x37 -> 0x7F" },
{ 0x0014502, 2, 1, { 0x7F }, "needfor* job<0x38 -> 0x7F" },
{ 0x001456D, 2, 1, { 0x7F }, "needfor* good<0x42 -> 0x7F" },
{ 0x00145C2, 2, 1, { 0x7F }, "needfor* house<0x37 -> 0x7F" },
{ 0x00145D8, 2, 1, { 0x7F }, "needfor* job<0x38 -> 0x7F" },
{ 0x00146CE, 2, 1, { 0x7F }, "needforgood good<0x42 -> 0x7F" },
{ 0x0014725, 2, 1, { 0x7F }, "needforequipment good<0x42 -> 0x7F" },
/* --- FUN_00455f86: granica pętli listy towarów --- */
{ 0x00561D8, 2, 1, { 0x7F }, "goods loop bound 0x42->0x7F @4561D8" },
/* --- FUN_00409dc1: brakująca pętla zawodów --- */
{ 0x0009F41, 2, 1, { 0x7F }, "job copy-loop bound 0x38->0x7F @409F41 (elem+0x948)" },
/* --- FUN_00409075 (loader playerdata): 6 granic tablic flag --- */
{ 0x000976D, 2, 1, { 0x7F }, "playerdata jobs bound 0x38->0x7F" },
{ 0x00097E9, 2, 1, { 0x7F }, "playerdata houses bound 0x37->0x7F" },
{ 0x0009868, 2, 1, { 0x7F }, "playerdata goods bound 0x42->0x7F" },
{ 0x00098E7, 2, 1, { 0x7F }, "playerdata jobs bound 0x38->0x7F" },
{ 0x0009967, 2, 1, { 0x7F }, "playerdata houses bound 0x37->0x7F" },
{ 0x00099BA, 2, 1, { 0x7F }, "playerdata goods bound 0x42->0x7F" },
```

Alternatywna, równoważna postać (adres immediate, `off=0`): `{0x1428B,0,1,{0x7F}}`, `{0x1440D,...}` itd.

### 5.1 Kategoria B — prawdopodobne, ale wymagają weryfikacji rozmiaru magazynu

Też pętle po 0x42/0x37, ale poza funkcjami już tkniętymi przez mod; patch zmienia liczbę wpisów, więc
**najpierw trzeba potwierdzić, że magazyn docelowy też jest powiększony** (inaczej przepełnienie):

| adres     | instrukcja     | co robi (disasm)                                                          |
|-----------|----------------|--------------------------------------------------------------------------|
| `0x4B277` | `CMP EDI,0x42` | buduje tablicę kodów 66×dword, potem indeksuje rekord plemienia           |
| `0x2C93C` | `CMP ESI,0x42` | skanuje tablicę 66×dword (`[obj+0x21C]`) — funkcja towarowa               |
| `0x4A82D` | `CMP EAX,0x37` | pętla `eax=0x2B..0x37` po `elem+0x3C78` (GOODS_B, stride 0x38)            |

**Rekomendacja:** wgrać najpierw 24 wpisy (§5) i przetestować węgiel; §5.1 dołożyć tylko jeśli objaw
(nowe towary nie pojawiają się w konkretnym panelu) nadal wystąpi.

---

## 6. Czego NIE ruszać (potwierdzone jako poprawne / obojętne)

- `0x456023`, `0x45618E`, `0x456194`, `0x456165`, `0x45622A`, `0x456323`, `0x45635B` — patchowane, OK.
- `0x435CD7`, `0x40B02C` (granice `0x35A0`) — patchowane, OK.
- `0x409E46`, `0x409E65`, `0x409E82`, `0x409EA1`, `0x40A003` — patchowane, OK (brakuje tylko `0x409F41`).
- `0x4561D8` — jedyna brakująca granica `0x42` w `FUN_00455f86`.
- Większość z 647 „niepokrytych" trafień skanu to szum (stałe danych, `push/int/out`, stride `0x58`).

---

## 7. Ograniczenia i co potwierdzić w runtime

1. Analiza **statyczna** — brak wykonania gry. Korelacja tag↔handler dla części `jobEnables*`/`needfor*`
   wynika z **wzorca zapisu** (bazy `0x69xx/0x6Cxx`, stride `0x100/0x400`), nie z pełnej tabeli stringów.
2. `0x455FE1` (`IMUL EAX,EAX,0x38`) nie jest patchowane; sąsiednie `0x37`/`0x42` są. Uznaję za **niepewne** —
   do sprawdzenia, czy `0x38` to tu licznik domów/poziom (wtedy też `->0x7F`). Nie dodaję, by nie ryzykować.
3. Podniesienie strażnika do `0x7F` jest bezpieczne dla realnych danych (job ≤56, house ≤57, good ≤66):
   wszystkie indeksy mieszczą się w rekordzie `0x1AE08` (house×0x198: 57×0x198=0x5B68; good×8: 66×8=0x210;
   job×0x400: 56×0x400=0xE000; +0x14B3C/0x692C < 0x1AE08).
4. **Test po wgraniu:** czy węgiel pojawia się w drzewku produkcji plemienia i czy Smolarz (job 56) go wytwarza.

---

## 8. Status (wykonane 2026-10-14)

- [x] Dodano **24 wpisy** z §5 do `etapa_gen\patches_ext.h` (16 parser + `0x561D8` + `0x9F41` + 6 `FUN_00409075`).
- [x] Usunięto uszkodzone wpisy `0x44181C/1F/21`, `0x468A64/69` (były linie 203–207).
- [x] Walidacja tabeli: **615 wpisów**, 0 kolizji, 0 wpisów poza obrazem, 24/24 nowe trafiają w immediate `0x37/0x38/0x42`.
- [x] Przebudowano `EtapC.dll` (`etapc\EtapC.dll`, SHA256 `80757FC0…`) i zainstalowano do root (`EtapC.dll`, `launcher.exe`).
- [x] Przywrócono `CN.PLMOD.exe` z oryginału (SHA256 `367419B7…3F00`, byte `0xA7298` = `0x18`).
- [ ] **Do sprawdzenia w grze:** czy węgiel (good 66) pojawia się w drzewku produkcji plemienia i czy Smolarz (job 56) go wytwarza; oczekiwany log `patches applied: 615/615 ok`.
- [ ] Ewentualnie: §5.1 (3 wpisy) po weryfikacji rozmiarów magazynów.

**Backupy** (`.ai\backup\`): `patches_ext.h.20261014-203122.bak`, `EtapC.dll.20261014-203122.bak`
(dodatkowo kopia root `EtapC.dll`/`launcher.exe` z `…-203327.bak`).
