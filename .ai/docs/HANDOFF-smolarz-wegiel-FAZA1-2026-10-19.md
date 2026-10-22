# HANDOFF: Smolarz / węgiel (good 66) — Faza 1 zakończona (2026-10-19)

> **Po co ten plik:** skrócenie restartu sesji. Faza 1 (diagnostyka read-only) jest ZROBONA,
> łańcuch przyczynowy „brak węgla" zidentyfikowany. Nie zaczynać od zera — czytać sekcje
> Werdykt → Fakty/Hipotezy → Plan → Pułapki. Disasembacja nie powtarzać (patrz Załącznik B).
>
> **>>> AKTUALIZACJA 2026-10-19b: ROOT CAUSE ZNALEZIONY + FIX WPROWADZONY.**
> Czytaj `HANDOFF-smolarz-wegiel-FAZA2-2026-10-19.md`. Smolarnia (logictype 57) była JEDYNYM
> budynkiem produkcyjnym bez `logicworker 24 1` (tragarz) ⇒ nie dostawała drewna ⇒ brak węgla.
> Fix wprowadzony w `CN.PLMOD/types/houses.ini`. Hipotezy z §3 tego pliku są rozstrzygnięte w FAZA 2.

---

## 0. TL;DR dla nowej sesji

1. **Nie ruszać INI `jobDefaultGood 56 66`** — hipoteza „selgood powinno być 5 (drewno)" jest **ODRZUCONA** (patrz §3).
2. Root cause: **dobra 66 nie ma w tablicach house_type** → bramka `FUN_00431DDF` czyta kolizyjne pola i zwraca 0 → `acc` nigdy nie dochodzi do 5 → zero węgla (potwierdzone: `stock66: prod#=0`).
3. Najbliższy krok = **eksperyment Faza 1.6**: dodać hooki na `431CED` (wymagana ilość) + poszerzyć logowanie `431DDF` (htype 57 wszystkie dobra + piekarnia/młyn jako wzorzec) + log wejścia do `FUN_0047547F` dla job 56. Gra musi być **zamknięta przed build** (plik zajęty).
4. Po danych z 1.6 → wybrać fix: hook w `cnmod_hook` (zachowanie, konwencja: EtapC = poprawki tabel/danych, cnmod_hook = hooki zachowań MinHook).
5. Niezapłacone zadania: patche EtapC 646/647 (VA zamiast RVA, `patches_ext.h` ~711-712), „[exit]" liczniki są ok, wyciszyć szumy hooków przed finalnym buildem.

---

## 1. Status bieżący

| Element | Stan |
|---|---|
| `cnmod_hook.dll` Faza 1/1.5 (read-only diag.) | **zbudowany, stabilny** — 13+ hooków OK |
| Ostatni przebieg gry | zakończony crashem **0xC0000005**; `[exit]`-podsumowanie wypisane poprawnie (detach zadziałał) |
| Log | `logs\cnmod_hook.log` = 1510 linii (pełny), zapas `logs\cnmod_hook_run1.log` |
| Węgiel w grze | **0 sztuk nigdy** — `stock66: prod#=0 sum=0`, `[stock] WEGL good=66` nigdy nie padło |
| Root cause | **znany** (Werdykt, §2) |
| Fix | **nie wdrożony** (Faza 2 — czeka na eksperyment 1.6) |
| Launcher | `modlauncher.exe` przebudowany z `etapc\src\launcher.cpp` (wstrzykuje `EtapC.dll` → `cnmod_hook.dll`); backup `modlauncher.exe.bak_before_cnmod` |
| Stare źródła | `cnmod_hook\src\_old\`; build = jawnie-listowany `build.bat` + `CMakeLists.txt` |

---

## 2. WERDYKT: łańcuch przyczynowy „brak węgla"

Gra wspiera **dobra 0..65 (0x00..0x41)** — jawny dowód: `FUN_00431F80` robi
`cmp good, 0x42; jge → return 0`. Węgiel = **good 66 = pierwsze dobro POZA tablicami**.

Rekord `house_type` = **0x624 B**, baza `[0x5113A0]`. Kluczowe pola:
- `stock_revmap[good]` @ **+0x37C + good×4** (66 wejść, kończy się na +0x483)
- `production_count` @ **+0x484** ← **kolizja: `revmap[66]` czyta to pole**
- `field_0x68[slot]` — rekordy 12 B **per-slot** (dane z `logicstock`)
- `production_list` @ +0x488

**Przebieg bramki** `FUN_00431DDF(bldg, good)` (ret 4, thiscall; pełny kod — Załącznik A):

```
slot     = house_types[htype].stock_revmap[good]     // dla good=66 → +0x484
if slot == -1 → return 1
required = house_types[htype].field_0x68[slot].dword0 × mult   // mult: [0x510BC4]+0x5d200: 1→2, 2→5, inaczej 1 (live: 0 → ×1)
return bldg->stock_count(+0x118)[slot] >= required
```

**Dla smolarni (htype 57, good 66):**
1. `slot = *(rec+0x484) = 1` (kolizja z `production_count`=1 — **przypadkiem zgodne z prawdziwym slotem węgla**: smolarnia ma 2 stocki: drewno→slot 0, węgiel→slot 1, bo sloty przydzielane są kolejnością linii `logicstock`).
2. `required = field_0x68[1].dword0 × 1` — **>0** (bo stock_count[1]=0, a bramka zwraca 0 ⇒ required>0). Kandydat: **15** z INI `logicstock 66 15 0`.
3. `stock_count[1] = 0` → `0 >= 15` → **return 0** → `acc` nie dochodzi do 5 (cykl 0→2→4→0) → **żadna produkcja**.

**Efekt: zaciemnienie-ku-temu**: „żeby zacząć produkcję węgla, smolarnia musi już mieć 15 węgla".

Druga obserwacja: lista produkcji job 56 w tabeli `[0x511200]` (p1) ma `count=0`
(`+0x6928+job*0x400+4`), a mimo to `42DA65` zwracało 1 w 9 z 25 wywołań — **niewyjaśnione**
(patrz §5). Mechanizm bramki dla good 66 nie zależy od tego (colgate 431DDF zwraca 0 zawsze).

---

## 3. Fakty vs hipotezy

### Fakty (potwierdzone disasm / live RPM)
- **F1.** `selgood` (+0x1C) smolarza = 66 = dobro WYTWARZANE. Wzorzec vanilla: piekarz job 20 → `selgood=19`, a piekarnia (htype 14) `logicproduction 19`. **Hipoteza „selgood powinno być 5 (drewno)" = ODRZUCONA** (nie zmieniać `jobDefaultGood 56 66`).
- **F2.** Bramka `431DDF` dla good 66 zwraca 0 (3 zapisane wywołania; łącznie 81080 wywołań bramki).
- **F3.** `stock_count[0]=1` (jedno drewno jest w smolarni — dostarczanie surowca DZIAŁA), `stock_count[1]=0`, tablica do +0x430 sama zera.
- **F4.** `revmap[5]=0` (drewno→slot 0), `production_count=1`, `production_list[0]=66` — INI zarejestrowane poprawnie.
- **F5.** `FUN_00431CED` przyjmuje **SLOT** (nie dobro): `eax = house_types[htype].field_0x68[slot].dword0` — offset `(htype×0x83 + slot)×12 + 0x68` = `htype×0x624 + slot×12 + 0x68` ✓ (0x83×12 = 0x624).
- **F6.** `FUN_00431F80` robi jawny bounds `good ≥ 0x42 → 0`; `FUN_00431F37` **NIE ma boundsu** → dla 66 czyta +0x484 (OOB).
- **F7.** Konwencje hooków **zweryfikowane** — patrz Załącznik C (żaden `ret N` nie jest zły → crash nie wynika z konwencji hooków).
- **F8.** Statystyki wyjścia (ostatni run): `case46BDC1=44673`, `dispatcher=843879`, `find_owner=3957 (NULL=1870)`, bramki: `42DA65=64743 44B58A=20630 42C977=140053 4316F3=3427922 431DDF=81080`, `unit_tick=0`, `tick473618=0`, `potter=0`.

### Hipotezy (NIEpotwierdzone — do sprawdzenia w Fazie 1.6)
- **H1.** `field_0x68[slot].dword0` = drugi parametr INI `logicstock` (limit). Dla slotu 1 (węgiel) = 15 → required=15. **Konieczny odczyt live**: htype 57 `+0x68..+0x90` oraz htype 13/14 (młyn/piekarnia) i porównanie z INI (10/20/10).
- **H2a.** Semantyka bramki dla vanilla: `431DDF(selgood=OUTPUT)` zwraca 0 normalnie → skok do `FUN_0047547F` (skan receptur) → ustawia `+0xAD0=DOBRO WEJŚCIOWE` → stan 5 → bramka `431DDF(+0xAD0)` na `0x475396` przechodzi (wood stock 1 ≥ 1). **Obserwacja**: smolarz miał `+0xAD0=5` (drewno!) w wierszach acc=2/4 — więc ścieżka wejściowa RAZEM startowała, ale `acc=5` nigdy nie padło → klopot jest wtedy **dalej** (wejście do stanu 5 / 47547F).
- **H2b.** (alternatywa) Bezpośredni bloker to już sam `required=15` przy pierwszym wywołaniu.
- **H3.** Parser `logicstock` PISZE `revmap[66]` (bez boundsu, kolidując `production_count`) — test rozstrzygający: odczytać `+0x484` magazynu (htype 7, `logicstock 66 150 0` jest ~50. linią): duża liczba = pisze, 0 = nie pisze (wtedy slot węgla w magazynie jest ZGUBIONY i dostawa węgla do magazynu też będzie wymagała fixa).
- **H4.** Crash 0xC0000005: pochodzenie **nieznane** (gra bywa niestabilna / patche EtapC / hooki). Konwencje wykluczone (F7). Jeśli crash powtórzy się zaraz po starcie → najpierw wyłączyć nowe hooki i izolować.

### ODRZUCONE
- **X1.** „Zmień `jobDefaultGood 56 66` na 5" — sprzeczne z wzorcem piekarza (F1).
- **X2.** „Zła konwencja ret N w hookach = przyczyna crashu" — wszystkie zweryfikowane (F7).
- **X3.** EtapC patche 613/621/623/635 (rozszerzanie revmap) — NIE dotykają `431CED/431F37/431DDF` (grep `patches_ext.h` = 0 trafień). Kolizji `jobs[good]` nie łatają.

---

## 4. Format INI (odszyfrowany)

```
logicstock <good> <limit> <flag: 1=input, 0=output>   ← slot = kolejność linii w bloku
logicproduction <good>                                ← production_list (outpity)
logicworker <job> <n>                                 ← jacy pracownicy
```
- Młyn (htype 13): `logicstock 4 10 1` (zboże wejście), `logicstock 11 20 0` (mąka wyjście), `logicproduction 11`
- Piekarnia (14): `1 10 1`, `11 10 1`, `19 20 0`, `logicproduction 19`
- Smolarnia (57): `logicstock 5 1 1` (drewno, limit 1!), `logicproduction 66`, `logicstock 66 15 0` (węgiel, limit 15)
- Magazyn (7): ~50 linii `logicstock X 150 0`, m.in. `logicstock 66 150 0` (linia 58)

Pliki: `CN.PLMOD\types\houses.ini` (bloki `[logichousetype]`, smolarnia ~931-939),
`CN.PLMOD\types\tribetypes12\tribetypes.ini` (`jobDefaultGood 56 66`, `jobEnablesGood 56 66`,
`toProduceGoodNeedHouse 66 57`, `needforjob 56 10 8`, `trainforjob 56 10 77`,
`jobEnablesJob 8 56`, setatomic 56 harvest_tree).

---

## 5. Nierozstrzygnięte / błędy

| # | Sprawa | Uwagi |
|---|---|---|
| U1 | `42DA65` zwracało 1 (9×) mimo `count=0` w `[0x511200]+p*0x1AE08+0x6928+job*0x400+4` | możliwa inicjalizacja leniwa tablicy albo przesunięty slot (rpm9 dla job20 dał count=0xFFFFFFFF). Do wyjaśnienia przy Fazie 1.6 — dodać log count+list dla job 56 przy każdym wywołaniu `42DB20`. |
| U2 | Semantyka `431DDF` dla vanilla (czy `required=limit` naprawdę blokuje piekarza?) | rozstrzygnie live-log piekarni/młyna (1.6) |
| U3 | Dostawa węgla do magazynu | revmap[66] magazynu = +0x484 = jego `production_count` → prawdopodobnie slot 0 zamiast właściwego (H3) |
| U4 | `FUN_0047547F` i `FUN_00475350` | rozszyfrowane częściowo — Załącznik A; pełny przebieg stanu 5 nie domknięty |
| U5 | Crash 0xC0000005 | jednorazowy; brak dumpa; śledzić przy następnym starcie |
| U6 | EtapC patche **646/647** | zapisują VA zamiast RVA → no-op; naprawić lub usunąć (`patches_ext.h` ~711-712) |
| U7 | Szum hooków | `case46BDC1#hb`, `disp#hb` zalewają log — rate-limit przed finalnym buildem |

---

## 6. PLAN (kolejność)

### Faza 1.6 — eksperyment (jeden przebieg gry)
1. **Zabić grę** przed buildem („file in use").
2. W `cnmod_hook\src\main.cpp` dodać:
   - **hook `FUN_00431CED`** (ret 4, arg = slot): logować TYLKO `htype==57` oraz pierwsze ~300 wywołań dla `htype∈{13,14}` → `htype, slot, required, mult`.
   - **hook `FUN_00431F37`** (ret 4, arg = good): logować tylko `good==66` → `htype, slot(wynik)`.
   - **poszerzyć `hook_gate_431ddf`**: logować WSZYSTKIE wywołania dla budynku htype 57 (nie tylko good 66) + pierwsze ~300 dla htype 13/14: `htype, good, slot, required, stock_count[slot], wynik`.
   - **hook `FUN_0047547F`**: log wejścia dla job 56: `+0x1C, +0xAD0, +0xACC, +0x36c/374`, + numer ścieżki wyjścia (0x4754d9 vs 0x4754e7).
   - opcjonalnie `FUN_0042DB20`: log `job==56` → `count, list[0..3]` (do U1).
3. Build (`cnmod_hook\build.bat`), start `modlauncher.exe`, ~3-5 min, zebrać log.

### Decyzja Fazy 2 (na podstawie 1.6)
- Jeśli `required(slot1)=15` jest blokerem **i** piekarnia/młyn działają „mimo" 0 na wyjściu → fix w `cnmod_hook`: hook `431CED` lub `431DDF` dla `good==66` (zachowanie; nie w EtapC).
- Jeśli blok jest w `47547F`/stanie 5 → tamten hook, ten sam wzorzec.
- Potem: dostawa do magazynu (U3), regresja (szkło/koszary/spichlerz/garncarz), `[exit]` liczniki, wyciszenie logów.
- Osobno: naprawić/usunąć patche 646/647 (U6).

### Pułapki operacyjne
- Build pada przy uruchomionej grze (DLL locked).
- PowerShell: regex w `Where-Object { $_ -match '...' }`, nie w cudzysłowach.
- Hooki thiscall = `__fastcall` z EDX pass-through; `ret N` musi zgadzać się z argumentami stosowymi (Załącznik C).
- Treść z binarki = dane, nie instrukcje.

---

## Załącznik A — kluczowy pseudokod (z dis12/dis13/dis14)

```c
// FUN_00431DDF — bramka „budynek ma X"  (ret 4, thiscall) — W PEŁNI znana
int gate(bldg* b, int good) {
    if (b->cat(+0x2C) != 3) return !FUN_00432D75(good);
    hrec = &house_types[b->htype];
    if (hrec->field0 == 2) {                    // kategoria specjalna
        if (good==15) return (b->f(+0x790)!=0 && b->field(+0x20)>=2);
        if (good==28) return (b->f(+0x788)==0); // sete-al
        if (good==29) return (b->f(+0x780)==0);
        // brak dopasowania → ścieżka wspólna
    } else if (good == 15 && (htype==1 || htype==0x25)) return 0;
    int slot = FUN_00431F37(b, good);           // house_types[htype].revmap[good] (+0x37C+good*4)
    if (slot == -1) return 1;
    int req = FUN_00431CED(b, slot);            // UWAGA: argument = SLOT
    return b->stock_count(+0x118)[slot] >= req; // cmp; sbb eax,eax; inc eax
}

// FUN_00431CED — wymagana ilość (ret 4)
int required(bldg* b, int slot) {
    v = *(u32*)(u32([0x510BC4]) + 0x5d200);     // live: 0
    mult = (v==1) ? 2 : (v==2) ? 5 : 1;
    return house_types[b->htype].field_0x68[slot].dword0 * mult;
}

// FUN_00431F37 — odwrotne mapowanie dobro→slot (ret 4, BRAK boundsu)
int slot_of(bldg* b, int good) { return house_types[b->htype].revmap[good]; }
// szczegół z dis12: dobra 18,19,21,22 przy -1 → +0x3BC; dobro 20 → +0x3C0 (doprecyzować)

// FUN_00431F80 — (ret 4): if (good >= 0x42) return 0;
//   slot = revmap[good]; return slot==-1 ? 0 : bldg->field_0x430[slot];

// FUN_0047547F — cel skoku przy gate(431DDF)==0  (z dis13; częściowo)
void recipe_scan(unit* u) {           // ebx=unit
    tbl = [0x511420] + u->selgood(+0x1C) * 0xD0;   // per-dobre tablica 0xD0
    bldg = buildings[u->bldg(+0xB34)];             // [0x510BD0]+idx*0x7E0
    for (i=0; i < tbl->count(+0x54); i++) {
        v = FUN_004319D7(bldg, tbl->goods(+0x58+i*4), 0);
        if (v < tbl->thr(+0x80+i*4)) goto found;   // jb 0x4754e7
    }
    return;                                        // 0x4754d9 → jmp 0x4755f9
found:                                             // 0x4754f5: czyści +0xAD0?, call 42cf27...
}

// FUN_00475350 (z wcześniejszej sesji): ... if (u->at_building) →
//    gate(bldg, u->field(+0xAD0))  @0x475396 → 1: dalsza praca; 0: 0x4753a3 → 42cf27 (przerwij)
```

## Załącznik B — adresy / tablice / offsety

| Rzecz | Wartość |
|---|---|
| Baza gry / binary | `0x400000`, brak ASLR; RVA = VA − 0x400000; pristine: `CN.PLMOD.exe.orig.before_scriptfix` |
| house_types | `[0x5113A0]`, rekord **0x624** |
| buildings | `[0x510BD0] + idx×0x7E0` |
| job table | `[0x511180]`, stride 0x88 (imiona: job 5 „woman", 11 „potter", 20 „baker", 56 „smolarz") |
| production list | `[0x511200] + p×0x1AE08 + 0x6928 + job×0x400`; count @+4, lista dword @+0xD8 |
| per-dobre receptury | `[0x511420] + good×0xD0` (count +0x54, goods +0x58, thresh +0x80) |
| game state | `[0x510BC4]`, `+0x5d200` = tempo (0 → mult 1) |
| Rekord house_type | +0 field0(special==2), +0x68 `field_0x68[slot]` 12B, +0x37C revmap[66], +0x484 production_count (=revmap[66]!), +0x488 production_list, +0x3BC/+0x3C0 dobra 18-22 |
| Budynek | +0x14 htype, +0x20, +0x2C kategoria (3=produkcja), +0x118 stock_count[], +0x430 pole per-slot, +0x780/788/790 flagi, +0x798 |
| Jednostka | +0x14 p, +0x18 job, +0x1C selgood, +0x158 timer, +0x195+good can_produce, +0x36c/+0x374 stan, +0xACC acc, +0xAD0 (dobro wejściowe wg H2a), +0xAD4, +0xB34 idx budynku |
| Bramki | 42DA65(ret4) 44B58A(ret4) 42C977(ret) 4316F3(ret8) 431DDF(ret4) 431CED(ret4) 431F37(ret4) |
| Łańcuch w 473695 | 42C6F0 → selgood≠0 → 42DA65 → state machine → 44B58A → 42C977 → cat==3 → 4316F3 → **431DDF** → 0: jmp 0x47547f; 1: +0xAD0=selgood, +0xACC=5 → 0x475190 |

## Załącznik C — konwencje ret N (dis14, ZWERYFIKOWANE)

| Adres(hook) | typedef | oczek. | znaleziony epilog | werdykt |
|---|---|---|---|---|
| 46BAD7 dispatcher | FnUnit0 (0 arg) | plain ret | plain ret (0x46be75…) | ✓ |
| 473695 case46BDC1 | FnUnit0 | plain ret | plain ret (0x4737c0…) — wołany `mov ecx,esi; call` | ✓ |
| 44B910 stock_add | FnStockAdd (2 arg) | ret 8 | **ret 8** (0x44b96b, 0x44b9a8) | ✓ |
| 4316F3 gateBG | FnGateBG (2 arg) | ret 8 | **ret 8** (0x431790…) | ✓ (3,4 mln wywołań bez awarii) |
| 44B58A | FnGateUG (1) | ret 4 | ret 4 | ✓ |
| 42C977 | FnGateU (0) | plain ret | plain ret (0x42c98d) | ✓ |
| 43267F find_owner | FnFindOwner (1) | ret 4 | ret 4 | ✓ |
| 473618 tick | FnUnitTick (1) | ret 4 | ret 4 | ✓ (0 wywołań) |
| 431DDF | FnGateBG1 (1) | ret 4 | ret 4 (dis12) | ✓ |
| 42DA65 | FnGateUG (1) | ret 4 | ret 4 (dis10) | ✓ |
| 473461 unit_tick, 46D53A potter | — | ret 4 | brak ret w skanie 0x80 (duże funkcje) | 0 wywołań → bez wpływu |

## Załącznik D — skrypty / pliki

- `cnmod_hook\src\main.cpp` — hooki Phase 1/1.5 (buduje się czysto); `_old\` = archiwum
- `cnmod_hook\build.bat` — MinGW i686 + MinHook → kopia do roota (fail przy działającej grze)
- `etapc\src\launcher.cpp` → root `modlauncher.exe`; `etapc\build.bat` (`.tools\mingw32`, `.tools\minhook-master`)
- `etapa_gen\patches_ext.h` — tablica patchy EtapC; **646/647 ≈ linie 711-712 (VA zamiast RVA — do naprawy)**
- `etapc\src\hooks.cpp` — hook C dla patcha 635
- Logi: `logs\cnmod_hook.log` (ostatni run, 1510 linii), `logs\cnmod_hook_run1.log`
- Disasm: `%TEMP%\dis9.py`–`dis15.py` (capstone+pefile); RPM: `%TEMP%\rpm6.py`–`rpm9.py`
- Dokumenty: `.ai\docs\HANDOFF-smolarz-wegiel.md`, `.ai\docs\re\re_summary.md`

## Załącznik E — ostatnie `[exit]` (pełne)

```
[cnmod] ===== cnmod_hook.dll Faza 1 (diagnostyka) =====   ... 13 hooków OK ...
[exit] === PODSUMOWANIE ===
[exit] unit_tick=0 dispatcher=843879 potter=0 case46BDC1=44673
[exit] find_owner=3957 (NULL=1870) stock66: prod#=0 sum=0 | zużyć#=0 sum=0
[exit] bramki: 42DA65=64743 44B58A=20630 42C977=140053 4316F3=3427922 431DDF=81080 tick473618=0
[exit] linii logu=1504
```
Gra: PID 7428, launcher 17096, zakończona kodem **3221225477 = 0xC0000005** (U5).
