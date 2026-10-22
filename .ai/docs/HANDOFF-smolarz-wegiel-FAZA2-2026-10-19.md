# HANDOFF: Smolarz / węgiel (good 66) — FAZA 2: ROOT CAUSE ZNALEZIONY (2026-10-19b)

> **Po co ten plik:** Faza 1 (`HANDOFF-smolarz-wegiel-FAZA1-2026-10-19.md`) opisała łańcuch
> przyczynowy „brak węgla" i zostawiła 3 hipotezy. Ta faza je **rozstrzygnęła** i **wprowadziła fix**.
> Nowa sesja: czytaj TL;DR → Dowód → Co zmieniono → Co zostało. Disasembacji nie powtarzać.

---

## 0. TL;DR (najważniejsze, 6 linii)

1. **ROOT CAUSE: budynek `work charcoal burner` (logictype 57) jako JEDYNY budynek produkcyjny
   w `types/houses.ini` nie ma `logicworker 24 1`** (24 = tragarz/serf). Bez tragarza **nic nie
   dostarcza drewna** do smolarni → `stock[5] = 0` na zawsze → smolarz nie ma z czego zrobić węgla.
2. **FIX (danych, bez rebuildu):** dodane `logicworker 24 1` do bloku logictype 57
   (`G:\Games\CnMod 1.2\CN.PLMOD\types\houses.ini`). Exe czyta ten plik w runtime
   (zawiera string `logicworker` + `houses.ini`) → wystarczy restart gry.
3. **NIE jest to wina `jobDefaultGood 56 66`** — hipoteza „selgood=5" pozostaje ODRZUCONA.
4. Łańcuch produkcyjny smolarza **działa** (bramki przechodzą), dochodzi do skanu receptury
   `0x47547F`, ale skan znajduje `drewno = 0` → odsyła go po drewno → pętla bez produkcji.
5. Naprawione **2 zepsute patche EtapC** (#647/#648): używały VA zamiast RVA → były **no-opami**.
   Dodatkowo błędny bajt skoku (`EB 32` → ma być `EB 2E`).
6. Osobne, **nierozwiązane** zjawisko: w całej żywej grze `4755F9` (start produkcji) = 0 wywołań —
   receptury innych budynków wskazują dobra nieobecne w ich slotach (np. `good 74`). To NIE blokuje
   fixu smolarni, ale psuje ekonomię moda.

---

## 1. DOWÓD (to, co przesądziło)

### 1.1 Żywy log `logs/cnmod_hook.log` (ostateczny, cap 20002 linii)
```
[g431DDF] bldg=0a492f40 htype=57 good=5  slotR=0 stock=0 -> 0 (#1475)   <- drewno: stock=0
[g431DDF] bldg=0a492f40 htype=57 good=66 slotR=1 stock=0 -> 0 (#1479)   <- węgiel: 431DDF=0 (przechodzi do skanu)
[g431CED] bldg=0a492f40 htype=57 slot=0 field0=1  field1=1 -> req=5   (#22295)
[g431CED] bldg=0a492f40 htype=57 slot=1 field0=15 field1=0 -> req=75  (#22358)  <- mult=5 (szybkosc x5)
[g431F37] bldg=0a492f40 htype=57 good=66 -> slot=1  (#614710)
[gate 4316F3 REVMap] building=0a492f40 htype=57 good=66 flag=1 -> 1 (wywolanie 342568)
```
Wniosek: `431DDF(bldg,66) == 0` → kod **skacze do skanu receptury 0x47547F** (nie do „work").
Skan wywołuje `4319D7(bldg, 5, 0)` = stan drewna = **0 < 1** → gałąź „brakuje" → `+0xAD0 = 5` (idź po drewno).

### 1.2 Porównanie z innymi budynkami produkcyjnymi (`houses.ini`)
Parser: bloki `logicmaintype 3` = 29. Wszystkie 27 produkcyjnych mają `logicworker 24 1`.
Wyjątki: `work temple` (typ 37 — brak jakichkolwiek `logicworker`/`logicstock`/`logicproduction`,
to nie jest budynek produkcyjny) oraz:

```
typ 56  "studnia etapc"          workers=[24]        <- mod DODAŁ tragarza
typ 57  "work charcoal burner"   workers=[56]        <- BRAK 24  <-- BUG
```

**Smolarnia to jedyny prawdziwy budynek produkcyjny bez tragarza.**

### 1.3 Rozstrzygnięcie hipotez z Fazy 1
| Hipoteza F1 | Wynik |
|---|---|
| H: `431DDF` źle czyta kolizyjne pole (+0x484) → zwraca 1 | **ODRZUCONA** — live: `431DDF(66)=0`, `slotR=1` poprawne |
| H: selgood powinno być 5 (drewno) | **ODRZUCONA** (bez zmian) |
| H2a: skan receptury wysyła po brakujące wejście | **POTWIERDZONA** (kod + live) |
| H-nowa: brak tragarza = brak dostaw drewna | **POTWIERDZONA** (§1.2) |
| H: patch 646/647 (routing typu 57) jest potrzebny | **ODRZUCONA** — `FUN_00473461` jest martwe (patrz §3) |

---

## 2. PEŁNY ŁAŃCUCH PRODUKCJI (zweryfikowany disasm + live)

```
=== wybór jednostki do dyspozytora (0x443A4x) ===
0x443A49  if (unit[0x368] == 7) -> skip
0x443A52  if (unit[0x378] == 0) -> call 0x46BAD7 (dyspozytor)
          else -> unit[0x36C]=0; unit[0x368]=9; call 0x444BCE

=== dyspozytor 0x46BAD7 (this=unit) ===
  clear +0x370
  if (+0xACC == 0 && +0xAD4 != 0) -> 0x46BB5A
  job = unit[0x18];  if (job-1 > 0x2E) -> 0x46BE1B (nieznany zawod)
  tabela bajtowa @0x46BEBE / dword-jumptable @0x46BE76
  0x46BDC1 (grupa case 7: zawody 11,12,13,14,17,19,20,21) : mov ecx,esi; call 0x473695
      ^ EtapC patch 614 przepina JA @0x46BD36 na 0x46BDC1 -> zawody >47 dziedziczą case 7

=== FUN_00473695 (this=unit) — handler warsztatowy ===
  42C6F0(unit)==0                    -> +0x374=2; +0x36C=3; ret
  unit[0x1C]==0                      -> +0x374=2; +0x36C=3; ret
  42DA65(unit,selgood)==0            -> +0x374=0; +0x36C=3; ret
  switch(unit[0xACC]): 0->0x4736FF  2->0x474B13  4->0x474693  5->0x475190  else ret
  0x4736FF (acc==0):
    unit[0xAD4]!=0                    -> 0x444C6E
    44B58A(unit,selgood)!=0           -> 0x44B51C
    bldg = buildings[unit[0xB34]]
    (42C977(unit)!=0 && bldg[0x2C]!=3) -> abort
    bldg[0x798]!=0                     -> abort
    4316F3(bldg,selgood,1)==0          -> abort
    if (431DDF(bldg,selgood)==0) -> JMP 0x47547F   ; SKAN RECEPTURY
    else: unit[0xAD0]=selgood; unit[0xACC]=5; JMP 0x475190  ; PRACA
    abort (0x473765): +0x374=2; +0x36C=3

=== skan receptury 0x47547F (this=unit) ===
  rec = [0x511420] + unit[0x1C]*0xD0
  if (rec[+0x54] (liczba wejsc) == 0) -> 0x4754D9 -> JMP 0x4755F9   ; PRODUKCJA
  i=0..count-1:
        4319D7(bldg, rec[+0x58+i*4], 0)  <  rec[+0x80+i*4]  -> 0x4754E7 (brakuje)
  wszystkie OK -> 0x4754D9 -> JMP 0x4755F9                          ; PRODUKCJA
  0x4754E7:
    unit[0xAD0]=0; 42CF27(unit)
    i=0..count-1:
      if (4319D7(bldg, good_i, 0) < amt_i):
          unit[0xAD0] = good_i
          475590(unit)              ; "zalatw dostarczenie dobra"
          if (al != 0) -> return    ; stan zachowany -> jednostka idzie po dobro
    unit[0xACC]=0; unit[0x36C]=3; ret

=== 431DDF(this=bldg, good) — "czy magazyn spelnia wymog wyjscia" ===
  if (bldg[0x2C] != 3) return !432D75(good)
  rec = [0x5113A0] + bldg[0x14]*0x624
  if (rec[0]==2) { specjalne: good 0x0F / 0x1C / 0x1D -> pola bldg+0x780/0x788/0x790 }
  else if (good==15 && (htype==1 || htype==0x25)) return 0
  slot = 431F37(bldg, good);  if (slot == -1) return 1
  return  stock[slot] >= 431CED(bldg, slot)
=== 431CED(this=bldg, slot) ===
  req = house_types[bldg[0x14]].field_0x68[slot].dword0   tj. limit slotu @ +0x68+slot*12
  * mnoznik([GS+0x5D200]: 0->x1, 1->x2, 2->x5)
```

### Układ slotów budynku (potwierdzony live)
`logictype` (stride `0x624`): `+0x60` = liczba slotów; slot s = `{ good @+0x64+s*12, limit @+0x68+s*12,
flag @+0x6C+s*12 }` (flag 1 = wejście, 0 = wyjście); revmap good->slot @ `+0x37C+good*4`
(dla good 66 → `+0x484`, bo tablica ma 66 wpisów 0..65).

Live smolarnia (htype 57, bldg `0a492f40`):
```
hdr[+0x00..0x1C] = [3, 0, 66, 1, 56, 1, 0, 0]      (maintype, ?, good=66, ?, job=56)
slot_count       = 2
slot0 = good 5  limit 1  flag 1   (drewno, wejscie)
slot1 = good 66 limit 15 flag 0   (wegiel, wyjscie)
rev[5]=0  rev[66]=1 (poprawne)
```

---

## 3. DLACZEGO PATCHY 646/647 BYŁY BEZ SENSU (a nie tylko zepsute)

`FUN_00473461` (0x473461) **nie jest wołane dla smolarza** — jest wołane z `0x4681AB` tylko gdy
`unit[0xAB8] == 0x59 (89)` (animacja 89); `unit[0xAB8] == 90` → `0x473618`.
Licznik hooka `[exit] unit_tick=0` w całej sesji → funkcja jest praktycznie martwa dla htype 57.

**Mimo to naprawiono** (poprawność + brak „cichych" no-opów w tabeli):
- `{ 0x00473482, ... }` → `{ 0x00073482, ... }`  (był VA, SizeOfImage = `0x174000`, patch nie aplikował się)
- `{ 0x0047348A, ... }` → `{ 0x0007348A, ... }`
- bajt skoku `0x32` → `0x2E` (`EB 2E` z 0x473488 → **0x4734B6** = case38; `EB 32` trafiał w 0x4734BA = środek `IMUL`)

Skan całej tabeli: **tylko te 2 wpisy** miały rva ≥ 0x400000 (na 648 patchy).

---

## 4. CO ZMIENIONO W TEJ FAZIE

| Plik | Zmiana |
|---|---|
| `CN.PLMOD\types\houses.ini` | blok `debugname "work charcoal burner"` (logictype 57): dodane **`logicworker 24 1`** |
| `etapa_gen\patches_ext.h` | wpisy #647/#648: RVA `0x00073482` / `0x0007348A`; bajt `EB 2E`; komentarz |

**Uwaga:** zmiana `houses.ini` działa od razu po restarcie gry (exe wczytuje plik sam).
`patches_ext.h` wymaga **rebuildu EtapC.dll** (i tylko wtedy, gdy chce się utrzymywać routing typu 57).

---

## 5. JAK ZWERYFIKOWAĆ (kolejna sesja, 5 minut)

1. Uruchom grę (modlauncher), wczytaj zapis, zbuduj **smolarnię** (`work charcoal burner`).
2. Obserwuj `logs/cnmod_hook.log` (hook `431DDF` loguje htype 57):
   - **sukces:** `[g431DDF] htype=57 good=5 ... stock=1..N -> ...` (drewno w magazynie),
     następnie produkcja węgla (`stock[66]` rośnie), `[stock] WEGL good=66 ...`.
   - **porażka:** nadal `good=5 ... stock=0` → tragarz nie dostarcza; wtedy sprawdzić
     `jobEnablesGood 24 <dobro>` w `tribetypes.ini` i czy job 24 ma ścieżkę do tego budynku.
3. Kontrola stanu jednostki smolarza (Frida, `[GS]` / adresy live): oczekiwane
   `+0xACC` cyklicznie 0→5, `+0xAD0` = 66 (nie 5), `+0x36C` != 3 trwale.
4. Log line-cap (`cnmod_hook.log` = 20002 linii) — **podnieść limit** przed testem.

---

## 6. CO ZOSTAŁO (osobne problemy, nie blokują smolarni)

1. **Globalny brak startu produkcji:** w żywej sesji `4755F9` (start produkcji) = 0 wywołań
   przy `47547F` (skan) = tysiące. Receptury wskazują dobra, których nie ma w slotach budynku:
   - `good 11 ("food")` = wejścia `wheat(4)` + **`good 74`** (dobro spoza używanej numeracji),
   - `good 9 / 19 ("leat")` = łańcuchy na `58`/`9`,
   - przy `4319D7: good >= 0x42 -> 0` każdy taki input = 0 → „brakuje" na zawsze.
   Do ustalenia: czy to defekt tabeli receptur (runtime, budowana z danych moda), czy ślad po
   przesunięciu numeracji dóbr przez mod.
2. **`431F37` dla `good >= 66`** — obecnie `good >= 0x43` → 0 (brak linii). Wartość `revmap[66]`
   realnie istnieje (`+0x484`), więc skan po `+0x64+s*12` dla `s < count(+0x60)` byłby poprawny.
   Kandydat na patch EtapC (regresja: szkoła/baraki/magazyn/garncarz).
3. **`jobEnablesHouse 56 …` brak** (0 wystąpień dla 56, jak dla 24). Nie blokuje — smolarz jest
   przypisany i dyspozytor go obsługuje. Do rozstrzygnięcia, czy dodanie `jobEnablesHouse 56 57`
   (5 plemion) cokolwiek zmienia (prawdopodobnie nie).
4. **`logicstock 5 1 1`** w smolarni — limit drewna = **1** (młyn ma 10). Przy tragarzu to sprawne,
   ale przepustowość = 1 szt. na kurs. Kandydat na `logicstock 5 10 1` (do decyzji użytkownika).
5. **Hook `47547F`/`4319D7` w Frida nie zobaczył htype 57**, choć log MinHook dowodzi, że skan
   działa (431DDF=0). Rozbieżność filtrów/samplingu skryptu Frida — nie wpływa na wnioski.

---

## 7. PUŁAPKI OPERACYJNE (powtórka + nowe)

- Gra **auto-pauzuje bez fokusu** okna (`[GS+0x5D200]` → 0), ale liczniki rosły → nie zakładać pauzy.
- **Frida:** nie da się dwóch attach na ten sam adres; MinHook już trzyma:
  `473461, 46BAD7, 46D53A, 473695, 43267F, 44B910, 42DA65, 44B58A, 42C977, 4316F3, 431DDF,
  431CED, 431F37, 473618`. Do diagnostyki używać **call-site'ów wewnątrz** `FUN_00473695`
  (`0x47369A`, `0x4736B5`, `0x473715`, `0x47373A`, `0x47375C`, `0x47377C`) — te nie są hookowane.
- Sesja Frida **ginie** bez ostrzeżenia (gra zamknięta/crash) → po `frida_session_status`
  sprawdzać `list_frida_processes`.
- **Zapis gry:** smolarnia zbudowana na żywo NIE jest w żadnym save (`Saves/.../user_001.sav` 17.10)
  — przed jakimkolwiek restartem **zapisać**.
- `CN.PLMOD.exe` = 32-bit, ImageBase `0x400000`, `SizeOfImage` `0x174000` (RVA = VA − 0x400000).
- Tabele runtime (heap), **nie ma ich statycznie w exe**: `[0x511420]` (dobra/receptury, stride 0xD0),
  `[0x5113A0]` (house types, 0x624), `[0x510BD0]` (budynki, 0x7E0), `[0x511180]` (zawody, 0x88),
  `[0x511200]` (listy produkcji per plemię, 0x1AE08).
- Nazwa zawodu 56 w tabeli `[0x511180]` to **`"smol"`**; rekord bajtowo identyczny z zawodem 11
  (garncarz) w zakresie `+0x20..+0x84` — spójne z „dziedziczy case 7".

---

## 8. MAPA ADRESÓW (skrót, do nawigacji; pełna w FAZA 1)

| Adres | Rola |
|---|---|
| `0x443A6A` | call dyspozytora (jedyne) |
| `0x46BAD7` | dyspozytor zawodów (this=unit) |
| `0x46BDC1` | grupa case 7 → `call 0x473695` |
| `0x473695` | `FUN_00473695` workshop handler |
| `0x475190` | praca (`ad4==0` → jmp `0x475350`) |
| `0x47547F` | skan receptury (`0x4754E7` = brakuje, `0x4754D9` → produkcja) |
| `0x475590` | „zalatw dostarczenie dobra" (→ `0x45EE0C`, `0x45C4AC`) |
| `0x4755F9` | **start produkcji** |
| `0x431DDF` | czy magazyn spełnia wymóg wyjścia |
| `0x431CED` | wymagana ilość (limit slotu × mnożnik) |
| `0x4319D7` | stan dobra w budynku (flag 0 = stock, 1 = slot wyjścia) |
| `0x431F37` | good → slot (revmap) |
| `0x473461` | `FUN_00473461` — animacja 89 (martwe dla htype 57) |
| `0x42DA65` | „czy jednostka może produkować dobro" |
| `0x42DB20` | „czy dobro jest na liście produkcyjnej zawodu" |

---

# FAZA 3 — 2026-10-19 (wieczór)

## 1. WERYFIKACJA: MOJE NARZĘDZIE vs PRAWDZIWY EXE MODA

Porównanie `CN.PLMOD.exe` z `CN.PLMOD.exe.orig.before_scriptfix` (pefile, sekcja po sekcji):

| sekcja | różnych bajtów |
|---|---|
| `.text` | **81** (zakres `0x4A885F .. 0x4BDE0D`) |
| `.rdata`, `.data`, `.rsrc` | 0 |

**Wniosek:** cały disassembly funkcji `0x42CCCC`, `0x431xxx`, `0x45Cxxx`, `0x468xxx`,
`0x473xxx`, `0x474xxx`, `0x475xxx` jest **aktualny** — EtapC nie ruszył tych rejonów.

## 2. BŁĄD W MOICH WCZEŚNIEJSZYCH ODCZYTACH (naprawiony)

Globale czytam jako `ImageBase + (VA - 0x400000)`. Wcześniej podałem `0x10bd0` / `0x113a0`
zamiast `0x110bd0` / `0x1113a0` → „śmieciowe" wskaźniki. **Poprawne wartości live:**

| global | VA | offset od base | wartość w tej sesji |
|---|---|---|---|
| receptury | `0x511420` | `0x111420` | `0x354C330` |
| htype | `0x5113A0` | `0x1113A0` | `0xB013878` |
| budynki | `0x510BD0` | `0x110BD0` | `0x1DA40020` |
| joby | `0x511180` | `0x111180` | `0x35390A8` |
| per-tribe | `0x511200` | `0x111200` | `0xC446020` |
| akcje | `0x5112FC` | `0x1112FC` | `0xB08C508` |
| GS | `0x510BC4` | `0x110BC4` | `0xAE3B020` |

Smolarnia: `unit+0xB34 = 5` → budynek = `pBld + 5*0x7E0 = 0x1DA42780` ✓ (zgodne z logiem hooka).

## 3. POTWIERDZONY UKŁAD REKORDU htype (live, htype 57)

```
ht57[0..7] = 3, 0, 66, 2, 56, 1, 24, 1
             |  |  |   |  |  |  |  |
             |  |  |   |  |  |  |  +-- logicworker 24, szt. 1
             |  |  |   |  |  |  +----- job 24
             |  |  |   |  |  +-------- logicworker 56, szt. 1
             |  |  |   |  +----------- job 56
             |  |  |   +-------------- liczba slotów = 2
             |  |  +------------------ logicproduction = dobro 66
             |  +--------------------- (nieużywane)
             +------------------------ logicmaintype = 3
sloty (+0x60): 2 | (5,1,1) | (66,15,0)
revmap: rev(5)=0, rev(66)=1
```
`mult` z `[GS+0x5D200]` = **0** w tej sesji, ale hook `431CED` loguje `req=5` dla `field0=1`
→ źródło mnożnika w `431CED` wymaga jeszcze raz przeczytać (możliwe, że to inny global).

## 4. PEŁNY ŁAŃCUCH ZAKOŃCZENIA PRODUKCJI (NOWE — kluczowe)

```
47547F  skan receptury: dla i<[rec+0x54]: 4319D7(bldg, [rec+0x58+4i], 0) >= [rec+0x80+4i] ?
        TAK  -> 4755F9
        NIE  -> 4754E7 (ścieżka "brakuje", ad0 = brakujące dobro)
4755F9  start pracy:
        42CCC4(unit) = "gotowy?" (patrz §6)
        == 1 -> 475606: czy 42CFCE(unit)=unit+0xA6C  == bldg+0x1C ?
                            i 42CFC7(unit)=unit+0xA70  == bldg+0x24 ?
                        -> 4756BA  (STANOWISKO PRACY, właściwa ścieżka)
        == 0 -> 47565D: 45C23E(unit, &bldg+0x1C, &bldg+0x24) -> 42D008 (marsz)
0x4756BA  sprawdza wejścia, potem:
         45C17B(unit, rec[+0x4C], -1)     <-- USTAWIENIE AKCJI PRODUKCJI
         unit[0x36C] = 1
         4340CF(bldg, 3, sound) ; 4340CF(bldg, 4, sound)
```

Zakończenie (kiedy akcja się wykona) — wykonawca zadań `0x468xxx`:

```
0x4689C7:  dla i<[rec+0x54]: stock(rec+0x58+4i) >= rec+0x80+4i ?   (inaczej 36C=3)
0x468A1B:  431DDF(bldg, selgood) != 0  -> 36C=3 (wyjście pełne)
0x468A33:   zużycie wejść: dla i<[rec+0x50]: 431B3D(bldg, rec[+0xA8+4i], -1, 0)
0x468A70:  -> 468BAE  (jeśli selgood != 0x39 i != 0x3A)
468BAE:     eax = 4421A5(unit)          ; ilość (całkowita)
            amount = eax / 10 ; frac = eax % 10
            431B53(bldg, selgood, amount, frac, 0)
            unit[0xACC] = 0 ; unit[0xAD0] = 0
```

**`431B53(bldg, good, amount, frac, flag)` to JEDYNA funkcja dodająca towar do magazynu
budynku.** Zapisuje `[bldg + slot*4 + 0x118] += amount` oraz
`[bldg + slot*4 + 0x220] = frac` (ułamki /10, clamp 1000). Wywołania:
`0x42080C`, `0x42082D`, `0x431B4B`, `0x433DF6`, **`0x46810A`**, **`0x468BE2`**.
- `0x46810A` — produkcja „bez receptury" (dobro = `[task+8]`, ilość = `4421A5`) — farms/ule/kopalnie.
- `0x468BE2` — produkcja **rzemieślnicza** przez `468BAE`.

## 5. `45C17B` — USTAWIANIE AKCJI JEDNOSTKI (rozszyfrowane)

```
45C17B(unit, actionId, param)   ; actionId = rec[+0x4C]
  if actionId == 1                       -> return 0
  if !45C66E(unit)                       -> return 0
  jobRec = pJob + unit[0x18]*0x88
  if byte[jobRec + 0x24 + actionId] == 0 -> return 0        <-- WHITELIST AKCJI
  idx = [pTribe + (unit[0x14]*0x6B82 + job*0x5C + actionId)*4 + 0x20]
  if idx == -1 -> job = [jobRec+0x20]; retry; jeśli 0 -> return 0
  unit[0xAC4] = 0 ; unit[0xAC8]++ ; unit[0xAC0] = idx
  unit[0xAB8] = actionId ; byte[unit[0xABC]] = 1
  zagraj dźwięk z tablicy akcji [0x5112FC] + idx*0x138 + 0x34
  return 1
```

**`45C66E(unit)`:** jeśli `unit[0xAB8] == 1` → zwraca `(byte[tribeRec + 0x2C] == 0)`,
w przeciwnym razie `(unit[0xABC] != 0 ? tab[ac0].b8 : 1)`.
W tej sesji `tribeRec+0x2C = 0` → bramka przepuszcza.

## 6. `42CCC4` — „CZY GOTOWY DO PRACY?"

```
42CCC4(unit):
  if !42CF57(unit) -> 0
  a = unit[0xA68]
  a in 1..5 -> sprawdź 42CEA6(unit) == unit+0xA70  (pozycja docelowa) -> 1/0
  a == 6    -> sprawdzenie snu (unit+0xA7C == unit+0xB48, unit+0xB51) -> 1/0
  a in 7..8 -> 1
  a == 0    -> 0
```
`42D008` (start marszu) ustawia `unit[0xA68] = 5` lub `1`; `42CF27` zeruje `a68 = 0`.

## 7. ZNALEZIONY KONKRETNY DEFEKT: WHITELIST AKCJI JOBA 56

Rekord joba `pJob + job*0x88` ma na `+0x24 .. +0x87` tablicę **100 bajtów** = dozwolone
`actionId` (koreluje z listą `setatomic <job> <id>` w `tribetypes.ini`, plus zbiór domyślny).

```
job 56 allow[0..99] = 0111111110111111010011110000000000000000000011000000110010000000
                                                                 ^^ indeks 38 = 0
```

`rec[+0x4C]` (actionId) dla dóbr:

| dobro | actionId | job producenta | allow |
|---|---|---|---|
| 4 (pszenica), 5 (drewno), 11 (mąka), 58 | 0 | – | – |
| 12 (miód) | 1 | 24 | 1 |
| 19 (chleb) | 33 | 20 | 0 |
| 20 (cukierki) | 32 | 20 | 0 |
| 24 (ceramika) | 29 | 11 | 0 |
| 31 (deski) | 29 | 9 | 0 |
| 32 | 33 | 13 | 0 |
| 43 (piwo) | 32 | 21 | 0 |
| 57 | 33 | 16 | 0 |
| **66 (węgiel)** | **38** | **56 (smolarnia)** | **0** |
| 8 | 51 | 14 (mennica) | **1** (jest `setatomic 14 51`) |

**`45C17B(unit, 38, -1)` dla job 56 zwraca 0** → akcja produkcji nigdy nie startuje
(`unit[0xAB8]` pozostaje 1, `unit[0xABC]` = 0, `unit[0xAC0]` nie wskazuje akcji węgla).

**Test live (odwracalny, tylko RAM):**
1. `allow[38] = 1` (`pJob + 56*0x88 + 0x24 + 38`) — potwierdzone, że bajt się zmienia.
2. `je` na `0x45C1AB` → `90 90` (bypass whitelisty) + jednorazowe `unit[0x36C] = 3`.
   **Efekt:** jednostka przestała zamarzać i zaczęła cyklicznie wykonywać akcje
   (`ab8` = 2/3/4, `abc` = 1, `a68` 5↔0) — ale **`ab8` nigdy nie = 38**, `ac0` zostaje 76,
   węgiel = 0, drewno = 5.

**Wniosek:** whitelista `allow[38]` to **realna, pierwsza bramka**, ale **nie jedyna** —
`45C17B` nadal nie dochodzi do skutku (albo nie jest wołane, bo `42CCC4` zwraca 0 przy `a68=0`).

## 8. POZYCJA JEDNOSTKI — POTWIERDZONE, ŻE JEST NA STANOWISKU

```
unit+0xA6C = (80, 424)   ==  bldg+0x1C   ✓
unit+0xA70 = (78, 425)   ==  bldg+0x24   ✓
bldg+0x2C  = 3  ✓   (warunek 42C977)
```
Czyli to **nie** jest problem z dojściem/ścieżką — jednostka stoi dokładnie tam, gdzie trzeba.

## 9. `[owner] NULL!` — NIEZBADANE, A PODEJRZANE

Hook `find_owner(0x43267F)` loguje **ponad 10 000 razy** `[owner] NULL! building=1DA42780
key=0x4 htype=57`. Wcześniej były też `key=0xA`. Dla smolarni zdarzył się **jeden** sukces
(`key=0x4 → ret=1DA42DC0`). Nie wiadomo jeszcze, czy `key` to gracz/plemię, ani czy NULL
blokuje produkcję — ale sprawdzić to warto, bo to jedyny „nienaturalny" sygnał w logu.

## 10. LOG PRZESTAŁ DZIAŁAĆ

`cnmod_hook.log` osiągnął limit (`[cnmod] LIMIT linii osiagniety - dalsze logi wylaczone`)
przy 58755 liniach. **Bez podniesienia limitu dalsza obserwacja przez log jest niemożliwa.**

## 11. FRIDA — CO DZIAŁA, A CO NIE (potwierdzone empirycznie)

| operacja | status |
|---|---|
| `readU32/readU16/readU8` na `ptr(x)` | ✅ (ale `Memory.readU32` **nie istnieje**) |
| `writeU32/writeU8/writeByteArray` | ✅ (działa na danych **i na kodzie** po `Memory.protect`) |
| `Memory.protect` | ✅ |
| `send` + `setInterval` | ✅ |
| `Interceptor.attach` | ❌ callbacki nigdy nie odpalają |
| `File.write` | ❌ rzuca wyjątkiem |
| `setTimeout` | ❌ brak w Code Mode (używać `Start-Sleep` w shellu) |

## 12. NASTĘPNY KROK (do decyzji użytkownika)

**Wariant A — danych (bez rebuildu DLL):**
`tribetypes.ini`, 5 plemion: dodać `setatomic 56 38 "<nazwa animacji>"` obok istniejących
`setatomic 56 2..7`. Jeśli `allow[]` jest budowane z `setatomic`, da to `allow[38] = 1`.
Nazwa animacji: bezpiecznie `viking_collector_harvest_tree` (dla każdego plemienia jego
odpowiednik). **Wymaga restartu gry.**

**Wariant B — hook w `cnmod_hook.dll`:**
detour na `0x45C1AB` (sam `je`) albo na `0x45C17B` z wymuszeniem `actionId = 38` dla
`htype == 57`, gdy whitelista zawodzi. Nie koliduje z EtapC ani z dyspozytorem `0x46BAD7`.
**Wymaga zamknięcia gry i rebuildu.**

**Wariant C — zmiana joba smolarni:**
dać htype 57 job, który ma akcję produkcji (np. 11 / 13), ale to nadal nie da `allow[38]`.

**Przed kolejnym testem konieczne:**
1. podnieść limit logu w `cnmod_hook/src/main.cpp`,
2. dodać hooki: `45C17B` (arg actionId + wynik), `468BAE`, `431B53` (good 66),
3. zapisać grę i **zamknąć** ją przed rebuildem DLL.

**Nierozstrzygnięte:** dlaczego `a68 = 0` w stanie spoczynku (powinno być 1..5, żeby
`42CCC4` w ogóle dopuściło ścieżkę pracy) — to najbardziej prawdopodobny „drugi" bloker.


---

# FAZA 4 (2026-10-20) � ROZWI�ZANE: root cause produkcji

**Czytaj najpierw:** `HANDOFF-2026-10-20-PRODUKCJA-ROOT-CAUSE.md`

Skr�t:
* `atomicForProduction` w `Data\logic\goodtypes.ini` pochodzi z wanilii i NIE nale�y
  do zawod�w moda -> `allow[job][atomic]==0` -> `45C17B` zwraca 0 -> jednostka w `36C=1`
  i deadlock (`ABC=0`, `AB8=1`, `A68=5`).
* `productionInputGoods` wskazywa� dobra nieistniej�ce (74) lub niemieszczone w budynku.
* Produkcj� ko�czy **event animacji typu 21** (`0x468280[20] = 0x467EDD -> FUN_46897C`).
* Dow�d end-to-end: m�yn wyprodukowa� m�k� po ustawieniu `atomic=46` i `inputs=[4]`.
* Poprawki wprowadzone w `goodtypes.ini` (73 zmiany) i `tribetypes.ini`
  (`setatomic 56 46` w 5 plemionach). Wymagany restart gry.
