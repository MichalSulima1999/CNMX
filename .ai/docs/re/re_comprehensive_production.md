# RE — Kompleksowa analiza produkcji w CN.PLMOD.exe (Etap 6)

## Struktura produkcji (potwierdzona)

### Główny cykl: FUN_00473461 (VA 0x473461)
Funkcja tick jednostki. Wywoływana z pętli jednostek (`FUN_004680ea` @0x4681ab).

**Typy budynków obsługiwane:**
- `0x473482: SUB EDX, 0x26` — building_type - 38
- `0x473486: JZ 0x4734b6` — type == 38 → case 38 (szkoła)
- `0x473488: DEC EDX` — building_type - 39
- `0x473489: JNZ 0x473611` — type != 39 → **RETURN (nic nie robi)**

**Smalarnia (typ 57 = 0x39):**
- `SUB EDX, 0x26` = 0x21, `DEC EDX` = 0x20 ≠ 0 → `JNZ → return`
- **Brak timera, brak ustawiania `+0x195`, brak produkcji**

### Case 38 (szkoła) w FUN_00473461 (VA 0x4734b6–0x4734cc)
```
0x4734b6: PUSH [ESI+0x4]          ; owner/player
0x4734b9: IMUL ECX, ECX, 0x7e0    ; building_idx * stride
0x4734bf: ADD ECX, EAX            ; building instance
0x4734c1: CALL FUN_0043267f       ; szuka w building+0x644 wpisu z owner
0x4734c6: MOV EDI, [EAX+0x8]      ; wartość z wyszukanego wpisu
0x4734c9: MOV EBX, [EAX+0xc]
0x4734cc: TEST EDI, EDI
0x4734d1: JZ 0x473611             ; jeśli EDI==0 → return
```
`FUN_0043267f` (VA 0x43267f): szuka w building+0x644 (20 wpisów × 4 B) wpisu równego param_1. Zwraca (index+100)*0x10 + building jeśli znajdzie, 0 jeśli nie.

### Wspólny kod produkcji (od 0x4734cc)
Dla typów 38 i 39, jeśli FUN_0043267f zwróci non-zero:
1. Oblicz `tribe * 0x6b82` (stary rozmiar rekordu — zpatchowane na 0x8578 @RVA 0x734E0)
2. Próg plemienia: `DAT_00511200 + 0x6740 + (tribe*REC + uVar6)*4`
3. Sprawdź timer `+0x158` vs próg
4. Gdy timer osiąga próg:
   - Ustaw `+0x15c + uVar6 = 1`
   - Wywołaj `FUN_0045bbaa(unit, uVar6)` (dźwięk)
   - Jeśli `local_8 != 0`: ustaw `+0x195[local_8] = 1`, wywołaj `FUN_0045bb51(unit, local_8)` (dźwięk)
   - Resetuj timer `+0x158 = 0`
   - Jeśli `job == uVar6`: wywołaj `FUN_0044a0d9(unit)` + `FUN_0044b2fa(unit)`
   - Inaczej: wywołaj `FUN_00449f2f(unit, uVar6)` (UI zmiana selected good)
   - Wywołaj `FUN_00449bda(unit)`
   - Jeśli `FUN_0042da65(unit, local_8)`: wywołaj `FUN_0043e8a7(unit, local_8)` (UI wybór gooda)

### FUN_0044a0d9 (ustawia +0x195 dla goodów joba)
Pętla po goodach z job block (+0xD8). Skomplikowana logika:
- Sprawdza `FUN_0042d9a3` (progi plemienia) LUB `race == 2` (FUN_0042c597 == 2)
- Sprawdza `FUN_0042c676(unit)`
- Jeśli true: jeśli good == 56, ustaw `+0x1cd = 1`; SKIP +0x195
- Jeśli false: jeśli `FUN_0042c680(unit)` (job == 16):
  - Jeśli good == 57: ustaw `+0x195[57] = 1` (fall through JZ)
  - Jeśli good == 58: SKIP
  - Jeśli good inny: SKIP
- Jeśli `FUN_0042c680 == false` (job != 16): ustaw `+0x195[good] = 1`
- Ustawia też `GOODS_A2[good] = 1` i `GOODS_B[good] = 1`

**Kluczowe:** `FUN_0044a0d9` jest wywoływana TYLKO z `FUN_00473461` gdy `job == uVar6` (job jednostki == good z budynku). Dla smalarza (job 56) w smalarni (uVar6 = good z budynku, np. drewno=5), to się nie zdarza.

### FUN_0042da65 (bramka "czy może produkować")
Sprawdza: `+0x195[good] != 0` AND `FUN_0042db20(unit, good)` (good na liście job block) AND (`FUN_0042d848` (needforgood) LUB `FUN_0042d9a3` (progi plemienia) LUB `race == 2`).

## Root cause (potwierdzony)

**`FUN_00473461` nie obsługuje typu budynku 57 (smolarnia).** Dla smolarza w chałupie węglarskiej:
- Nie jest ustawiany timer produkcji
- Nie jest ustawiana flaga `+0x195[66]`
- Nie jest wywoływane `FUN_0044a0d9` (które ustawiłoby +0x195 dla goodów joba)
- **Brak produkcji węgla, brak opcji w UI**

Ręczne ustawienie `+0x195[66]=1` nie pomogło, bo:
1. Nie ma timera produkcji (nie ma "cyklu" produkcji)
2. `FUN_0044a0d9` nie jest wywoływane (nie ustawia +0x195 dla innych goodów, nie ustawia +0x21c statusu UI)
3. Nie ma kodu który by zużywał drewno i tworzył węgiel

## Miejsca sprawdzające logictype 57 (0x39) w kodzie

| Adres | Funkcja | Kontekst |
|-------|---------|----------|
| 0x441821 | FUN_00441800 | `cmp eax,0x39` — obsługa goodów 65,58,57 (zwierzęta?), jump jeśli == |
| 0x44a4d3 | FUN_0044a0d9 | `cmp eax,0x39` — w pętli ustawiania +0x195, good==57 traktowany specjalnie (fall through) |
| 0x468a64 | FUN_0046897c | `cmp eax,0x39` — nieznane |

Miejsca sprawdzające logictype 38 (0x26):
| Adres | Funkcja |
|-------|---------|
| 0x403eaa | FUN_00403e34 |
| 0x4a3913 | FUN_004a3891 |
| 0x473482 | FUN_00473461 (SUB EDX,0x26) |

## Hipoteza naprawy: zmiana logictype smalarni 57→38

**Zalety:**
- Typ 38 (szkoła) jest obsługiwany przez `FUN_00473461` (case 38)
- Output good (66 = węgiel) pochodzi z `logicproduction 66`, nie z logictype
- Typ 38 ma `logicmaintype 3` (jak smolarnia)
- Szkoła (typ 38) nie produkuje towarów, więc zmiana jej na 57 jest obojętna

**Ryzyko:**
- Case 38 wymaga `FUN_0043267f(building, owner) != 0` — budynek musi mieć wpis w `+0x644` dla ownera. Nie wiemy czy smolarnia go ma.
- Inne miejsca w kodzie mogą sprawdzać `logictype == 57` lub `== 38` i zachowywać się inaczej.

## Pliki dokumentacji (utworzone)
- `.ai\docs\re_engine_overview.md`
- `.ai\docs\re_production_flow.md`
- `.ai\docs\re_hypothesis_logictype.md`
- `.ai\docs\re_fix_plan.md`

## Następne kroki

1. **Opcja A (zalecana):** Zmień `logictype` w `houses.ini`:
   - Smolarnia (linia ~933): `logictype 57` → `logictype 38`
   - Szkoła (linia ~691): `logictype 38` → `logictype 57`
   - Uruchom grę, przetestuj produkcję węgla

2. **Opcja B (jeśli A nie zadziała):** Code cave w `FUN_00473461` dla typu 57 — wymaga dodania bajtów do PE (brak miejsca w .text, max 4 zero-bajty).

3. **Opcja C:** Zmień `JNZ` (0x473489) na `JZ` — ale to zepsuje koszary (typ 39). Odrzucane.

## Pliki zmodyfikowane (już na dysku)
- `etapa_gen\patches_ext.h` — wpis `{0x004A1C0, 0, 3, {0x8B,0x4B,0x18,...}}`
- `CN.PLMOD\tribetypes12\tribetypes.ini` — `jobEnablesJob 56 56` w 5 sekcjach
- `EtapC.dll` (root) — odbudowany (timestamp 21:55)
