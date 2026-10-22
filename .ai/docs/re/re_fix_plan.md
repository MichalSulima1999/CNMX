# RE — Podsumowanie i plan fixu (Etap 5)

## Co potwierdziliśmy (wszystko działa)

| Element | Status |
|---------|--------|
| Wszystkie 645 patchy w procesie | ✅ OK (zweryfikowane bajty w pamięci) |
| Dom typ 57 | ✅ `output=66`, `prodlist[0]=66`, `prodcount=1`, `stock_count=2` |
| `GOODS_A[plemię][66]` | ✅ =1 dla plemion 1,2,3,4,7 (źródło i cel) |
| `HOUSES_A[plemię][57]` | ✅ =1 |
| `jobBlock(56)` | ✅ `+0xD8=66` (good lista), `+0x330=66` (jobDefaultGood) |
| `needforgood[66]`, `needforjob[56]` | ✅ Puste (brak wymagań) |
| Patch kodu `FUN_0044a0d9` (RVA 0x4a1c0) | ✅ Naniesiony (`8B 4B 18`) |
| `jobEnablesJob 56 56` | ✅ Dodane w 5 sekcjach plemion w `tribetypes.ini` |
| `+0x195[66]` | ✅ Utrzymuje się po ręcznym ustawieniu (nie jest zerowane) |

## Root cause (zidentyfikowany)

**`FUN_00473461` (tick jednostki/produkcja, VA 0x473461) obsługuje tylko typy budynków 0x26 (38) i 0x27 (39):**

```
0x473482: SUB EDX, 0x26   ; EDX = building_type - 38
0x473486: JZ 0x4734b6     ; jeśli type == 38 → case38 (obsługa budynku)
0x473488: DEC EDX         ; EDX = building_type - 39
0x473489: JNZ 0x473611    ; jeśli type != 39 → RETURN (nic nie robi)
```

Dla smalarni (typ 57 = 0x39): `SUB EDX,0x26` = 0x21, `DEC EDX` = 0x20 ≠ 0 → `JNZ → return`. **Funkcja robi wczesny return — brak timera produkcji, brak ustawiania `+0x195[66]`, brak produkcji.**

Dodatkowo:
- `FUN_0044a0d9` (ustawia `+0x195` dla goodów joba) jest wywoływane z `FUN_00473461` tylko gdy `job == uVar6` (job jednostki == good z budynku). Dla smalarza (job 56) i uVar6 = good z budynku (np. drewno=5), to nie przechodzi.
- Nie znaleziono osobnego kodu "building production tick" — produkcja w tym engine jest napędzana przez tick jednostki (`FUN_00473461`), który pomija typ 57.

## Rozwiązanie: zmiana `logictype` smalarni w `houses.ini`

**Hipoteza:** Zmienić `logictype` smalarni z 57 na 38 w `CN.PLMOD\types\houses.ini`. 
- Output good (66 = węgiel) pochodzi z `logicproduction 66`, **nie** z logictype — smolarnia nadal produzowałaby węgiel.
- Typ 38 (szkoła, `logicmaintype 3`) jest obsługiwany przez `FUN_00473461` (case38), który ustawia `+0x195[good]` i uruchamia łańcuch produkcji.
- Szkoła (typ 38) to budynek edukacyjny — nie produkuje towarów, więc zmiana jej typu na 57 (nieobsługiwany) nie powinien mieć wpływu na produkcję.

**Zmiany w `houses.ini`:**
1. Smolarnia (linia ~933): `logictype 57` → `logictype 38`
2. Szkoła (linia ~691): `logictype 38` → `logictype 57` (szkoła nie produkuje, więc brak obsługi typu 57 jest obojętny)

**Ryzyko:** Inne miejsca w kodzie mogą sprawdzać `logictype == 57` lub `logictype == 38` (UI, budowanie, AI). Jeśli tak, można zobaczyć nieoczekiwane zachowanie.

## Alternatywa (jeśli zmiana logictype nie pomoże)

Dodać code cave w PE — wymaga dodania nowych bajtów do pliku (obecnie nie ma miejsca w .text, max 4 zero-bajty z rzędu). Można to zrobić przez:
1. Dodanie nowej sekcji do PE, LUB
2. Rozszerzenie sekcji .text, LUB  
3. Zastąpienie małej nieistotnej funkcji jmpem do code cave (oraz przeniesienie oryginalnego kodu tej funkcji do code cave)

## Pliki zmodyfikowane (już na dysku)

- `etapa_gen\patches_ext.h` — dodany wpis `{0x004A1C0, 0, 3, {0x8B,0x4B,0x18,...}}` (FUN_0044a0d9: używa własnego joba)
- `CN.PLMOD\tribetypes12\tribetypes.ini` — dodano `jobEnablesJob 56 56` w 5 sekcjach plemion
- `EtapC.dll` (root) — odbudowany z obiema zmianami (timestamp 21:55)

## Pliki dokumentacji (utworzone w tej sesji)

- `.ai\docs\re_engine_overview.md` — mapa struktur i kluczowych funkcji
- `.ai\docs\re_production_flow.md` — przepływ produzione, analiza FUN_00473461
- `.ai\docs\re_hypothesis_logictype.md` — hipoteza zmiany logictype
- `.ai\docs\re_fix_plan.md` — plan fixu z code cave

## Następne kroki

1. Zmienić `logictype` w `houses.ini` (smolarnia: 57→38, szkoła: 38→57)
2. Uruchomić grę, wczytać zapis z chałupą węglarską + smolarzem + drewnem
3. Sprawdzić czy węgiel jest produkowany i czy jest opcja produkcji w UI
4. Jeśli nie działa → wdrożyć code cave (dodanie sekcji do PE)
