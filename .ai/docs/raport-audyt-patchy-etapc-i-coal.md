# Raport RE: audyt tabeli patchy `EtapC.dll` + ścieżka produkcji węgla (good 66)

**Data:** 2026-10-XX
**Narzędzia:** REA 12.1.4 + Ghidra 12.1.4 (JDK 21) — zarówno przez MCP (`tools.rea.*`), jak i CLI (`npx -y rea-agents@latest`).
**Analizowany plik (niezmieniony):** `CN.PLMOD.exe.orig.before_scriptfix`
**sha256:** `367419b7a797c3db6c64c162f5bb74ad1668252ee32e60dfe8d685e0a4d63f00`
**ImageBase:** `0x400000`, arch x86 (PE32).
**Zakres obrazu (RVA):** `.text 0x1000..0xF3000`, `.rdata ..0xFE000`, `.data ..0x16B8B8`, `.rsrc ..0x174000`.
→ **Wszystko z RVA ≥ 0x174000 jest poza obrazem.**

Artefakty źródłowe (surowe wyjścia REA): `.ai\re_out\*.md`.

> Uwaga: treści pochodzą z analizy binarki (kod/deasembler). Traktuję je jako dane, nie instrukcje.

---

## 1. Audyt tabeli patchy — co jest zepsute

### 1.1 Fakt podstawowy
- `etapa_gen\patches_ext.h` definiuje `PATCH_COUNT` = **596** wpisów.
- Log runtime `logs\etapc.log`: **`patches applied: 591/596 ok`** — dokładnie 5 wpisów kończy się `VirtualProtect FAILED`.
- Konwencja appliera (z `etapc\src\EtapC.cpp`): zapis pod `base + rva + off`, gdzie `base` = adres bazowy modułu (`0x400000`).
  Zatem **`rva` musi być RVA** (adres względny), a nie VA.

### 1.2 5 wpisów z adresem bezwzględnym (VA) zamiast RVA
Programowe przesianie tabeli (`rva ≥ 0x174000`) zwraca dokładnie te 5 linii:

| linia | `rva` w tabeli | rva − 0x400000 | opis |
|------:|---------------:|---------------:|------|
| 203 | `0x0044181C` | `0x4181C` | UI list 1 (was 0x3A) |
| 204 | `0x0044181F` | `0x4181F` | UI list 2 (was 0x39) |
| 205 | `0x00441821` | `0x41821` | UI list 3 (was 0x41) |
| 206 | `0x00468A64` | `0x68A64` | UI list 4 (was 0x39) |
| 207 | `0x00468A69` | `0x68A69` | UI list 5 (was 0x3A) |

Pozostałe 591 wpisów ma postać 7-cyfrową (`0x00NNNNN` = RVA). Te 5 zapisano 8-cyfrowo jako **VA**.
Applier liczy `base + 0x44181C` = `0x84181C` → poza mapowaniem → `VirtualProtect FAILED`. **To tłumaczy 591/596.**

Dowód (REA MCP, `read_bytes`):
```
VA 0x441817: 83 F8 41 74 0A 83 F8 3A 74 05 83 F8 39 75 0E 8B CE E8 56 03
VA 0x468A60: F0 8B 43 1C 83 F8 39 74 0E 83 F8 3A 74 09 8B CB E8 39 01 00
```

### 1.3 Co realnie znajduje się pod tymi adresami (deasemblacja)

**Lista A — funkcja `FUN_00441800` (RVA 0x41800):**
```
RVA 0x41817: 83 F8 41   cmp eax, 0x41      ; immediate @ RVA 0x41819
RVA 0x4181A: 74 0A      je  +0x0A
RVA 0x4181C: 83 F8 3A   cmp eax, 0x3A      ; immediate @ RVA 0x4181E
RVA 0x4181F: 74 05      je  +0x05          ; <-- 0x44181F to TEN bajt (opcode je), nie cmp
RVA 0x41821: 83 F8 39   cmp eax, 0x39      ; immediate @ RVA 0x41823
RVA 0x41824: 75 0E      jne +0x0E
```
Dekompilacja warunku:
```c
if (field_0xacc != 0 &&
    (last_0xad0 == sel_0x1c || sel_0x1c == 0x41 || sel_0x1c == 0x3a || sel_0x1c == 0x39)) {
    FUN_00441b83(this); last_0xad0 = 0;
}
```
Callerzy `FUN_00441800` (REA `xrefs`): `0x4320B0, 0x432118, 0x432140, 0x4321D5, 0x4321F3` (funkcja ok. `0x4320xx`).

**Lista B — funkcja `FUN_0046897c` (RVA 0x6897C):**
```
RVA 0x68A60: 8B 43 1C   mov eax, [ebx+0x1C]
RVA 0x68A64: 83 F8 39   cmp eax, 0x39      ; immediate @ RVA 0x68A66
RVA 0x68A67: 74 0E      je  +0x0E
RVA 0x68A69: 83 F8 3A   cmp eax, 0x3A      ; immediate @ RVA 0x68A6B
RVA 0x68A6C: 74 09      je  +0x09
```
Caller `FUN_0046897c` (REA `xrefs`): tylko `0x467EDF`.

### 1.4 Drugi błąd (poza VA/RVA): przesunięte adresy 2 z 5 wpisów
Nawet po zamianie VA→RVA wpisy 204 i 205 wskazują **zły bajt**:
- wpis 204 `0x44181F` → `0x4181F` to opcode `je` (nie `cmp 0x39`); `cmp eax,0x39` jest pod `0x41821`.
- wpis 205 `0x441821` → `0x41821` to `cmp eax,0x39` (a komentarz mówi „was 0x41"); `cmp eax,0x41` jest pod `0x41817`.

Wpisy 203, 206, 207 wskazują poprawne *początki instrukcji* `cmp`, ale przy `off=0` nadpisałyby **opcode `0x83`**, nie immediate. Poprawny immediate to `adres_instrukcji + 2`.

### 1.5 Poprawione wpisy (mechanicznie)
Wariant „zachowaj konwencję autora" (`rva` = początek `cmp`, `off` = 2):
```c
{ 0x0041817, 2, 1, {0x38}, "UI list 1 (was 0x41)" },   // imm @ 0x41819
{ 0x004181C, 2, 1, {0x38}, "UI list 2 (was 0x3A)" },   // imm @ 0x4181E
{ 0x0041821, 2, 1, {0x38}, "UI list 3 (was 0x39)" },   // imm @ 0x41823
{ 0x0068A64, 2, 1, {0x38}, "UI list 4 (was 0x39)" },   // imm @ 0x68A66
{ 0x0068A69, 2, 1, {0x38}, "UI list 5 (was 0x3A)" },   // imm @ 0x68A6B
```
Wariant prostszy (`rva` = adres immediate, `off` = 0): `{0x41819,0,1,{0x38}}`, `{0x4181E,...}`, `{0x41823,...}`, `{0x68A66,...}`, `{0x68A6B,...}`.

### 1.6 ⚠️ Zastrzeżenie semantyczne — czy te patche w ogóle dotyczą „job 56"?
Dekompilacja `FUN_0046897c` pokazuje:
```c
iVar5 = *(int *)((int)param_1 + 0x1c) * 0xd0 + DAT_00511420;   // DAT_00511420 = baza GOODS, stride 0xD0
```
Pole `[param_1+0x1c]` jest więc **indeksem tablicy TOWARÓW (goodów)**, a nie zawodów. Wartości w porównaniach to `0x39=57`, `0x3a=58`, `0x41=65` — a węgiel to **66 (`0x42`)**, którego w tym zbiorze **nie ma**.

Dodatkowo warunki to **łańcuchy równości OR**:
- lista A: `sel==0x41 || sel==0x3a || sel==0x39`
- lista B: `sel==0x39 || sel==0x3a`

Nadpisanie *wszystkich* stałych wartością `0x38` (tak jak sugerują komentarze + 5 wpisów) **zawęziłoby zbiór do samego `0x38`** i usunęło `0x39/0x3a/0x41`. To prawie na pewno niezamierzone.

**Wniosek:** komentarz „allow job 56 (0x38) in production UI list" jest **wątpliwy semantycznie**; te 5 patchy dotyczy najpewniej UI listy towarów, a nie odblokowania produkcji węgla. Naprawa adresów jest słuszna *technicznie*, ale **nie rozwiązuje automatycznie problemu węgla** i wymaga potwierdzenia intencji.

---

## 2. Ścieżka produkcji węgla — korekta błędnej dokumentacji

Zweryfikowałem twierdzenia z `.ai\docs\goods-mechanism-analysis.md` i `re-findings.md` dekompilacją (REA → Ghidra):

| Twierdzenie z dokumentacji | Co pokazuje REA | Werdykt |
|---|---|---|
| `0x4E21B7` = „job dispatcher" | funkcja łamania/formatowania tekstu (obsługa `\t \n \r spacja {newline}`) | **BŁĄD** |
| `0x4C23D8` = „house production loop" | fragment funkcji rysującej **panel domu** (czyta `[0x5113a0]+0x484/+0x488`, formatuje `gfxgood`) | **BŁĄD** |
| `0x46BDC1` = „potter handler" | `FUN_0046bad7` = **dyspozytor trybów mapy** (`switch(param+0x18)`) | **BŁĄD** |
| `0x46D53A` = „potter handler" | `FUN_0046d53a` = handler trybu `0x19` — interakcja na mapie (współrzędne `param+0x24/+0x26`) | **BŁĄD** |
| `0x46E1BE` czyta `tribe_house+8` i produkuje | `FUN_0046e1be` operuje na współrzędnych i `FUN_0043b35f(...,2/1)` (stawianie/przesuwanie obiektu) | **BŁĄD** |
| „good 24 (0x18) hardkodowany" @ RVA `0xA7297` | bajty `E8 69 18 01 00` = `call rel32 (+0x11869)` → `0x18` to część **displacement**, nie typ towaru | **FAŁSZYWY TRAFIENIE** |

**Wniosek:** opisany w docs „łańcuch produkcji" (dyspozytor `0x4E21B7` → potter `0x46E1BE` → `tribe_house+8`) **nie jest potwierdzony w binarium**. Miejsce rzeczywistej egzekucji produkcji (konwersja wejście→wyjście dla domu z `logicproduction 66`) nie zostało jeszcze zlokalizowane.

Co jest natomiast **potwierdzone** w danych (nie w kodzie):
- `Data\logic\houses.ini`: logictype **57** = `"work charcoal burner"` (`logicworker 56 1`, `logicstock 5 1 1`, `logicproduction 66`, `logicstock 66 15 0`); istnieje też logictype **56** = `"studnia etapc"`.
- `Data\logic\jobtypes.ini`: **56 wpisów** (typy 1..56); typ 56 = Smolarz. Nie ma zawodów 57/58/65.
- Patch kroniki: `HOUSE_TYPE` 0x37→0x7F, `GOODS_TYPE` 0x35A0→0x6730, strażniki `0x42→0x7F`, `JOB 56` (rozmiar tablicy `0x1dc0→0x1e48`, cap 0x38→0x39), dyspozytor `0x6BD36` (default `ja` → `0x6BDC1`) — **te wpisy są poprawne i aplikują się** (m.in. weryfikacja `0x6BD36`: `0F 87 DF 00 00 00` → `0F 87 85 00 00 00`, `ja` na `0x6BDC1`).

---

## 3. Rekomendowane poprawki (wymagają Twojej zgody)

1. **`etapa_gen\patches_ext.h`, linie 203–207** — poprawić `rva`/`off` wg sekcji 1.5.
   - ⚠️ Najpierw ustalić, **jaki zbiór typów** ma być dozwolony (czy naprawdę `{0x38}`? czy dodać `0x38` bez usuwania `0x39/0x3a/0x41`?).
2. Przebudować `EtapC.dll` (`etapc\build.bat`) i podmienić w grze — dopiero po akceptacji.
3. **Nie** polegać na tezach „job script / potter handler / dispatcher 0x4E21B7" — wymagają ponownego RE.

---

## 4. Dlaczego „MCP nie działał" i jak to naprawić

- Wcześniej wbudowany provider Ghidra zwracał `provider_unavailable` / `not_configured` (brak `GHIDRA_INSTALL_DIR`, JDK 17). **Teraz działa** — potwierdzone wywołaniami `tools.rea.open_binary` + `tools.rea.binary_overview` + `tools.rea.read_bytes` (provider `ghidra 12.1.4`, `image_base 0x400000`).
- Aby MCP był stabilny po restarcie, w **aktywnym** pliku konfiguracji (`G:\Games\CnMod 1.2\opencode.json`, a jeśli używany jest też `G:\Games\CnMod 1.2\.opencode\opencode.json` — to w obu) musi być blok `environment` serwera `rea`:
  ```json
  "environment": {
    "GHIDRA_INSTALL_DIR": "G:\\Tools\\ghidra_12.1.4_PUBLIC",
    "JAVA_HOME": "G:\\Tools\\jdk-21",
    "PATH": "G:\\Tools\\jdk-21\\bin;${PATH}"
  }
  ```
- CLI (rundant): `npx -y rea-agents@latest decompile <plik> --procedure <VA> --format md`. **Ważne:** `--procedure` przyjmuje **VA** (adres = `0x400000 + RVA`), nie RVA.

---

## 5. Ograniczenia analizy
- Analiza **statyczna** (Ghidra); brak wykonania gry, brak rozwiązywania wywołań pośrednich / wirtualnych tam, gdzie REA ich nie odzyskał.
- Liczby `0x39/0x3a/0x41` interpretuję jako indeksy towarów na podstawie `*(param+0x1c)*0xD0 + [0x511420]` — to wynik dekompilacji, nie 100% pewność semantyki UI.
- Nie przeskanowałem całego obrazu pod kątem *innych* miejsc, które mogłyby blokować good 66 (tylko miejsca wskazane wcześniej + nowe).

---

## 6. Stan plików / do decyzji
- `CN.PLMOD.exe.orig.before_scriptfix` = oryginał (sha256 zgodny).
- **`CN.PLMOD.exe` (root) jest obecnie nadpisany kopią testową** (bajt pod `0xA7298`: `0x18 → 0x42`) — proszę potwierdzić: **przywrócić oryginał czy zostawić?**
- Żadnych plików gry nie modyfikowałem poza wykonaniem tego raportu.
