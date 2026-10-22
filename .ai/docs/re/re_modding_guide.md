# RE — Przewodnik modowania: dodawanie nowych budynków i surowców

Uzupełnienie do `.ai/docs/jak-dodac-budynek-lub-surowiec.md`. Opiera się na analizie silnika CN.PLMOD.exe.

---

## 1. Ogólne zasady

- Gra to 32-bitowy PE (ImageBase 0x400000, brak ASLR), silnik typu *Knights & Merchants*.
- ID towarów/budynków/zawodów były rozszerzone z 42 → 127 przez 535+ patchy (patches_ext.h).
- Nowe ID (>54) działają **tylko** przy uruchomieniu przez `etapc\launcher.exe` (runtime overlay Etap C). Czyste `CN.PLMOD.exe` nie wczyta nowych wpisów.
- Pliki danych: CP1250, CRLF, format `.cif` (nagłówek `<CULTURES_CIF_BEGIN>...<CULTURES_CIF_END>`, body z blokami `[section]`).

---

## 2. Dodanie nowego surowca (good)

Przykład: dodanie stali (ID 70).

### Krok 1 — Wygeneruj szablon
```bash
python .ai\scripts\modkit.py inspect
python .ai\scripts\modkit.py template-good --id 70 --name stal
```

### Krok 2 — Uzupełnij pliki

**`CN.PLMOD\types\goodtypes.ini`** (lub `Data\logic\goodtypes.ini`):
```
[goodtype]
name "stal"
type 70
landscapetype <N>
isInputGoodFlag 0
isProducedInHouseFlag 1
isProducedOnMapFlag 0
productionInputGoods 5        ; drewno (lub inne inputy)
atomicForProduction <N>
```

**`CN.PLMOD\stringstext\gameobjects\goods_pol.ini`**:
```
stringn 70 "Stal"
```

### Krok 3 — Zweryfikuj
```bash
python .ai\scripts\modkit.py validate
python .ai\scripts\modkit.py inspect
```

### Uwagi RE
- GoodTypes table stride = 0xD0, baza 0x511420.
- Validator w `FUN_0041592E` (RVA 0x159F1) był patchowany `0x42 → 0x7F` dla good 66. Dla nowych ID >66 może być potrzebny kolejny patch validatora.
- Pętle iterujące po towarach z boundem 0x35A0 (66) zostały patchowane na 0x6730 (127) w RVach 0xB02C, 0x35CD7, 0x56168. Pętla w 0x415E8A (0x15E8A) crashuje jeśli bound extended — nie patchować bez znalezienia bezpiecznej ścieżki.
- Pętla w 0x45FAFA (0x5FAFA) używa lokalnych tablic na stosie (66+102 sloty) — UNSAFE, overflow przy rozszerzeniu.

---

## 3. Dodanie nowego budynku

Przykład: dodanie kuźni (ID 60).

### Krok 1 — Wygeneruj szablon
```bash
python .ai\scripts\modkit.py limits
python .ai\scripts\modkit.py template-house --id 60 --name kuźnia
```

### Krok 2 — Uzupełnij pliki

**`CN.PLMOD\types\houses.ini`**:
```
[logichousetype]
debugname "forge"
logictype 60          ; nowy typ — musi być obsługiwany w kodzie lub przez code cave
logicmaintype 3
logicworker <job> 1
logicstock <input_good> <qty> <flag>
logicproduction <output_good>
logicstock <output_good> <cap> <flag>
debugcolor <r> <g> <b>
```

**`CN.PLMOD\budynki12\houses\houses.ini`** (sekcja [GfxHouse], minimum):
```
[GfxHouse]
id 60
model <model>
LogicMaximumSize <w> <h>
EditGroups <group>
```

**`CN.PLMOD\stringstext\gameobjects\houses.ini`**:
```
stringn 60 "Kuźnia"
```

### Krok 3 — Przetestuj
```bash
etapc\launcher.exe
```

### Uwagi RE — logictype i produkcja

`FUN_00473461` (tick jednostki) obsługuje **tylko logictype 38 i 39**. Dla nowego budynku z produkcją:
- Opcja A: użyj logictype 38 (szkoła) — obsługiwany, output good z `logicproduction`.
- Opcja B: code cave w `FUN_00473461` dla nowego logictype (wymaga nowej sekcji PE / rozszerzenia .text).
- Opcja C: jeśli budynek nie produkuje (tylko magazyn / dekoracja), dowolny logictype.

**Kolizja revmap przy good >= 66:** stock revmap `+0x37C + good*4` może kolidować z `+0x484` (production count) gdy `good*4` przesunie się poza tablicę. Dla good 66: `+0x37C + 264 = +0x484`. Obejście: `logicproduction` przed `logicstock`.

---

## 4. Dodanie nowego zawodu (job)

- Job types table: baza 0x511180 (według re_engine_overview) lub 0x511520 (według re-findings), stride 0x88, count 88→127.
- Job 56 = smolarz (nazwa z hook_GetJobString, nie z danych).
- W `tribetypes.ini` na plemię:
  ```
  jobEnablesJob <nowy_job> <nowy_job>
  jobDefaultGood <nowy_job> <output_good>
  jobEnablesGood <nowy_job> <output_good>
  allowgood <output_good>
  ```

---

## 5. Patchowanie kodu (patches_ext.h)

Format wpisu: `{ RVA, offset, size, { new_bytes[8] }, "description" }`.
Aplikuje w `base + RVA + offset` (base = 0x400000).

Typowe patchy przy rozszerzaniu ID:
- Walidatory `cmp eax, 0x42; jge` → imm `0x42` → `0x7F` (127)
- Pętle bound `0x35A0` → `0x6730` (66 → 127 towarów)
- `logicproduction` good guard `0x42 → 0x7F`
- `logicstock` good guard `0x42 → 0x7F`
- `toProduceGoodNeedHouse` guard `0x42 → 0x7F`

**Code cave GOODS_B:** RVA 0xF2300, nadpisuje 0x9E76–0x9E80 (11 B): `E9 <rel> + 6×NOP` → skok do cave → powrót `E9` na 0x9E81.

---

## 6. Checklist przed wdrożeniem nowego budynku z produkcją

- [ ] `houses.ini`: `logictype`, `logicmaintype`, `logicworker`, `logicstock`, `logicproduction`
- [ ] `budynki12\houses\houses.ini`: sekcja [GfxHouse] (model, rozmiar, grupa edycji)
- [ ] `stringstext\gameobjects\houses.ini`: nazwa
- [ ] `tribetypes.ini`: `allowhouse`, `allowgood`, `jobDefaultGood`, `jobEnablesGood`, `jobEnablesJob`, `toProduceGoodNeedHouse`
- [ ] `goodtypes.ini`: definicja output good + input good
- [ ] Patch walidatorów i boundów (patches_ext.h) jeśli ID > 66 (towary) lub > 54 (budynki)
- [ ] Uruchom przez `etapc\launcher.exe`, nie czyste `CN.PLMOD.exe`
- [ ] Sprawdź `logs\crash.txt` — musi być pusty
- [ ] Sprawdź czy Storage UI pokazuje nowy towar (pętla 0x415E8E może crashować)
- [ ] Sprawdź czy stawianie budynku nie crashuje (dodaj filtr niezdefiniowanych budynków jeśli sloty 42-126 mają śmieci)

---

## 7. Narzędzia w repo

- `.ai\scripts\modkit.py` — template-good, template-house, clone-good, clone-house, inspect, validate, limits, good-export, good-import
- `.ai\scripts\make_etap1full.py` — merger patchów (f_prov + R + ELOFF + cave → header)
- `.ai\scripts\verify_full.py` — weryfikacja bajtowa ELOFF/cave + kontrola nakładek
- `.ai\scripts\patched_disasm.py` — disasm zpatchowanego binarium (capstone)
