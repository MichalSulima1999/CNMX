# HANDOFF 2026-10-21 — NAPRAWA ZAPISU + ZADANIA SMOLARZA

Plik roboczy dla szybkiego startu kolejnej sesji. UTF-8.

---

## 1. ZROBIONE: crash przy zapisywaniu / wczytywaniu

### Objaw
- `logs/crash.txt`: `code=0xC000001D` (nielegalna instrukcja), `addr_rva=0x000D97D7`.
- Windows Event Log: `CN.PLMOD.exe`, `0xc000001d`, offset `0x000d97d7` — powtórzył się 3x
  (19:54:55, 20:06:58, 22:53:28).
- Plik zapisu **powstawał poprawnie** (`Saves\singleplayer\savegames\user_001.sav`, 6 574 602 B,
  22:53:26), crash następował ~2 s później.
- W zrzucie stosu widoczna była ścieżka `Saves\singleplayer\savegames\user_001.sav`.
- `bajty@EIP = FF FF E8 F1 2E F3 FF ...` → EIP trafiał **w środek instrukcji**
  `lea ecx,[ebp-0x88]` w `FUN_004d88dc`, czyli nastąpił skok do nieprawidłowego adresu.

### Przyczyna (znaleziona 2026-10-21)
Patch EtapC `0x0030D4F` (5 bajtów → `jmp 0x4F2340`) skakał do **źle wygenerowanej jaskini**
`"tribe_house init"` pod `0x4F2340`. Łańcuch:

```
0x42705E  call 0x430D1B           ; FUN_00430d1b = init/loader rekordu tribe_house
0x430D4F  jmp  0x4F2340           ; PATCH EtapC
0x4F234A  call 0x4D97D7           ; ZLY displacement (mial byc call 0x42A237)
0x4D97D7  FF FF ...               ; srodek instrukcji lea -> 0xC000001D
```

Jaskinia miała **trzy błędy generatora**:
1. brakowało przeniesionych bajtów `89 46 2C` (`mov [esi+0x2C],eax`),
2. `imul ecx,ecx,0x624` rozbite na `69 C9 24` + `03 0D ...` → śmieć `imul ecx,ecx,0xA00D0324`,
3. `call 0x42A237` miał displacement policzony dla złego adresu → `0x4D97D7`,
   a `jmp` powrotny celował w `0x430D59` (środek `push 0x78616861`).

Dodatkowo: **cała jaskinia była pozostałością po OBALONYM modelu produkcji**
(`.ai/docs/HANDOFF-smolarz-wegiel.md`, pkt 5 — „Teorie OBALONE"), więc nie realizowała
żadnej potrzebnej funkcji.

### Fix
Usunięte z `etapa_gen/patches_ext.h` (sekcja przy `logicproduction`):
- wpis `{ 0x0030D4F, ... }` (JMP do jaskini),
- 8 wpisów jaskini `0xF2340 … 0xF2361`.

W ich miejscu jest komentarz z pełnym wyjaśnieniem i oryginalnymi bajtami
(`89 46 2C 53 8D 45 FC 50 68 61 68 61 78 89 5D FC E8 D3 94 FF FF`).
**Nie przywracać tej jaskini.**

Zostawiony świadomie: patch `0x0015843` (`mov [esi+8],eax` w handlerze `logicproduction`) —
wg dokumentacji „może być sensowny", nie bierze udziału w crashu.

### Wdrożenie
- Backup: `EtapC.dll.bak_savefix_20261021_230549` (94208 B, stary).
- Nowy: `EtapC.dll` **93696 B** (2026-10-21 23:05), zbudowany `etapc\build.bat` (sam kopiuje do roota).
- Weryfikacja binarne: w nowym DLL **nie ma** wpisów `rva=0x30D4F` ani `rva=0xF2340`.
- Przy okazji w tym buildzie są **3 patche crashu ikony węgla** (`0x7E7D1`, `0x8A193`, `0x8A254`)
  z sekcji „IKONY DÓBR" — wcześniej niezabudowane.

### Jak sprawdzić
1. Uruchomić grę, wczytać zapis, zapisać grę, wczytać ponownie.
2. Po teście: `logs/crash.txt` powinien być pusty/nieaktualny;
   `Get-WinEvent` nie powinien pokazać nowego `0xc000001d` @ `0xd97d7`.
3. Jeśli crash wróci — sprawdzić, czy `addr_rva` jest nadal `0x000D97D7`
   (to by znaczyło, że jakaś kopia starego DLL jest ładowana).

### Poprawka dodatkowa: crash PRZY STARCIE (23:09, `0xC0000005` @ `0x47E7D0`)
Po wdrożeniu powyższego builda gra crashowała od razu przy starcie:
`AV: WRITE @ 0x00000043`, `bajty@EIP: 83 43 42 7C 04 ...`.

Przyczyna: patch ikony węgla miał **zły offset**.
`{ 0x007E7D1, 0, 1, {0x43} }` pisał 0x43 na bajt **ModRM**, a nie na immediate:

```
0x47E7D0  83 F8 42   cmp eax,0x42     <- F8 = ModRM, 42 = immediate
patch 0x7E7D1+0 -> 0x43:
0x47E7D0  83 43 42   add dword ptr [ebx+0x42], 0x7C   -> zapis pod 0x43 = AV
```

Poprawione na `{ 0x007E7D0, 2, 1, {0x43} }` (konwencja pliku: rva = adres instrukcji,
off = pozycja bajtu). Po patchu: `83 F8 43 7C 04` ✓.

Pozostałe dwa patche węgla były poprawne (sprawdzone w oryginalnym EXE):
- `0x48A192  BE 08 01 00 00` → imm na `0x8A193` ✓ (`mov esi,0x10C`),
- `0x48A252  83 FB 42` → imm na `0x8A254` ✓ (`cmp ebx,0x43`).

Dodatkowo przeskanowałem wszystkie 643 patche pod kątem tego samego błędu
(bajt patchowany trafia w ModRM po `83`/`81`) — **0 trafień** (`.ai\tmp\audit_modrm.py`).
Narzędzia pomocnicze:
- `.ai\tmp\verify_patched_image.py` — nakłada `PATCHES[]` na EXE i sprawdza kluczowe bajty,
- `.ai\tmp\audit_modrm.py` — audyt offsetów,
- `.ai\tmp\scan_bad_calls.py` — szuka `call`/`jmp` poza `.text`.


---

## 2. DO ZROBIENIA (kolejność wg ważności)

### 2.1 Smolarz (job 56, ht 57): panel wyboru produkcji — ✅ NAPRAWIONE (2026-10-21)
**Objaw:** w oknie pracownika-smolarza nie było w ogóle sekcji produkcji, więc
smolarz produkował węgiel bez przerwy (nie dało się wybrać ani wyłączyć produkcji).

**Przyczyna:** pętla budująca listę dóbr w `FUN_004c6a05` (okno „produkcja pracownika")
chodziła tylko po dobrach **1..65**:

```
0x4c6b5b  push edi                    ; good
0x4c6b5f  call FUN_0042db20           ; can_produce[good] && good w prodmap[job]
0x4c6b70  call FUN_0042da65           ; czy budynek pozwala (FUN_004316f3)
0x4c6b8a  cmp  [unit+0x1C], edi       ; zaznaczenie = selgood
0x4c6b92  lea  eax,[edi+0x2710]       ; id przycisku = 10000+good
0x4c6bf6  inc  edi
0x4c6bf7  cmp  edi, 0x42              ; <-- TYLKO 1..65
0x4c6bfa  jb   0x4c6b5b
```

Węgiel ma id **66**, więc nigdy nie trafiał na listę → lista pusta → brak sekcji.

**Dane były poprawne** (sprawdzone w RAM działającej gry):
- `jobEnablesGood 56 66` (5 plemion), `toProduceGoodNeedHouse 66 57`,
- `can_produce[66] = 1`, `selgood = 66` (jednostka `0x1d85cb90`),
- `prodmap[job 56] = [66]` — **stride plemienia to `0x215E0`, nie `0x1AE08`**.

**Patch (EtapC):** `{ 0x004C6BF7, 2, 1, { 0x43 } }` → `cmp edi,0x43` (dobra 0..66).
Węgiel pokaże się tylko pracownikowi z `can_produce[66] != 0` (smolarz); pozostali
są odfiltrowani przez `FUN_0042db20` (wymaga wpisu w `prodmap` danego joba).

**Kliknięcie:** handler `0x4C6C8A` przyjmuje id `0x2710..0x2AF7` → `good = id - 10000`
(brak limitu 66), więc wybór węgla działa.

**Uwaga o diagnostyce:** `cnmod_hook` loguje `listCount` ze **złym** stride
(`STRIDE_PLIST = 0x1AE08`) — stąd mylące `listCount=0` w `logs/cnmod_hook.log`.
Poprawna wartość: `0x215E0` (patrz `NEW_REC_SIZE` w `etapa_gen\patches_ext.h`).

**Do potwierdzenia w grze:** czy w oknie smolarza jest teraz pozycja „węgiel"
i czy kliknięcie jej drugi raz wyłącza produkcję (czyli czy „ilość" jest
osobnym mechanizmem — w tym oknie nie ma pola liczbowego, jest tylko lista wyboru).


### 2.2 Ikona węgla (dobro 66)
Ikony dóbr są naprawione przez `landscapetype` w `Data\logic\goodtypes.ini`
(59 zmian, backup `goodtypes.ini.bak5_20261021_223524`).
Węgiel (66) nie ma odpowiednika w `landscapetypes.cif` — potrzebna nowa ikona.
- Warianty: (a) przypisać węglowi `landscapetype` istniejącego typu o ciemnej grafice
  (np. coś z 1..87) — najtańsze, zero nowych assetów; (b) dodać nowy typ do
  `landscapetypes.cif` + grafika — wymaga edycji CIF i assetu.
- Crash rysowania ikony (NULL deref) jest już załatany 3 patchami w EtapC,
  więc teraz najwyżej ikona będzie „pusta", nie wywali gry.

### 2.3 Smolarz nie dostaje doświadczenia po wyprodukowaniu węgla
Inne zawody dostają XP. Trzeba znaleźć miejsce nadawania XP w pętli produkcji
i sprawdzić, czemu dla job 56 / dobra 66 jest pomijane (np. brak wpisu w tabeli
job→good, albo XP liczone z `selgood`).

### 2.4 Spam w `logs/etapc.log` (56 MB!)
Dwie gorące linie:
- `[EtapC] GetJobString(job=56,plural=1)==NULL -> fallback "Smolarz"` (~2000 na 4000 linii),
- `[owner] NULL!` (hook `find_owner`: 10060 wywołań z NULL).
Do zrobienia: logować raz (flaga static bool) albo dodać filtr poziomu.
Plik rośnie w MB na minutę — spowalnia grę i utrudnia diagnostykę.

### 2.5 Transport między budynkami (NIEROZWIĄZANE)
Nie potwierdzono, czy jednostki `job 24` (carrier) w ogóle powstają.
Kwatera Główna ma `logicworker 24 3` — hipoteza: przewoźników trzeba **zatrudnić w HQ**.
Do sprawdzenia w grze.

### 2.6 Duplikaty `type` w `goodtypes.ini`
27/49/59/60 — wygrywa ostatni blok; dobra „iron ore", „gold ore", „cannon", „ammunition"
faktycznie nie istnieją. Opcjonalnie rozdzielić na wolne id 68+.

---

## 3. Szybkie przypomnienia techniczne
- Ikona dobra = `landscapetype` w `goodtypes.ini`; nazwy typów w `Data\logic\landscapetypes.cif`.
- Nazwy dóbr: `Data\text\pol\strings\gameobjects\goods.ini` (`stringn <id>`).
- Struktura patcha: `{ rva, off, size, {bajty}, "opis" }` — RVA, nie VA.
- Budowa: `etapc\build.bat` (wymaga zamkniętej gry; sam kopiuje DLL do roota).
- Weryfikacja binarne tabeli patchy: szukaj `struct.pack('<I', rva)` w `EtapC.dll`.
- Podgląd „jak wygląda exe po patchach" bez uruchamiania gry:
  `.ai\tmp\dis_cave.py` (nakłada `PATCHES[]` na plik i deasembluje Capstone'em).
