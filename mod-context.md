CN.PLMOD.exe - Stan Reverse Engineeringu
Data: 2026-10-18  
Cel: Reverse engineering silnika gry typu Knights & Merchants w celu dodania nowych budynków, surowców i zawodów
1. Architektura binarnego
Pole	Wartość
Format	PE32 (x86)
ImageBase	0x400000
Rozmiar	1 146 880 B (0x118000)
Sekcje	.text, .rdata, .data, .rsrc
Język	C++ (prawdopodobnie MSVC)
Globalne tablice i struktury
Adres VA	Nazwa	Stride	Opis
0x510BC4	elem_base	0x4A80	Elementy graczy
0x511200	tribe_base	0x1AE08	Rekordy plemion
0x5113A0	house_types	0x624	Typy budynków (55 → 127)
0x511420	good_types	0xD0	Typy towarów (66 → 127)
0x510BD0	buildings	0x7E0	Instancje budynków
0x510BE0	tribe_house	0x54C	Budynki plemienia
0x568C0C	building_instances	0x8BC	Instancje budynków gracza
0x568CA8	building_type_data	—	Dane typu budynku
0x569AA0/4/8	UI context	—	Kontekst rysowania UI
2. Kluczowe struktury danych
Rekord typu budynku (house_type, 0x624 B)
DAT_005113A0 + type * 0x624
Offset	Nazwa	Opis
+0x000	category	3 = budynek
+0x008	output_good	good ID wyjściowy
+0x060	stock_count	liczba stocków
+0x064	stocks[12]	tablica stocków
+0x37C	stock_revmap[66]	revmap towarów
+0x484	production_count	liczba produkcji
+0x488	production_list[20]	lista produkcji
+0x4D8	production_revmap[66]	revmap produkcji
Instancja budynku (building, 0x7E0 B)
DAT_0x510BD0 + idx * 0x7E0
Offset	Nazwa	Opis
+0x014	house_type	index typu budynku
+0x02C	category/type	typ budynku
+0x200	built_flag	0 = niezbudowany
+0x644	owner_entries[20×4]	właściciele
Jednostka (unit)
Offset	Nazwa	Opis
+0x14	tribe	plemię
+0x18	job	zawód (56 = smolarz)
+0x1C	selected_good	wybrany towar
+0x100	building_idx	budynek przypisany
+0x158	production_timer	timer produkcji
+0x195	can_produce[good]	flaga "może produkować"
+0x21C	job_good_status[good]	status UI (0, 0xB, 0xC, 0xD, 0xE)
+0x390	building_idx	budynek przypisany
+0xACC	interaction_state	stan interakcji
+0xAD0	interaction_good	towar w interakcji
Rekord plemienia (tribe, 0x1AE08 B)
DAT_00511200 + tribe * 0x1AE08
Offset	Nazwa	Opis
+0x519C + good*0x14	req_table	wymagania surowcowe
+0x55FC + good*0x14	need_table	potrzeby dla gooda
3. Kluczowe funkcje (RE)
Główny łańcuch produkcji
FUN_004078C8 (główna pętla gry)
  └─ FUN_0040AD0A (iteracja po budynkach)
       └─ FUN_00433662 (tick budynku)
            └─ FUN_0043127A (iteracja po jednostkach)
                 └─ FUN_0044193D (tick jednostki)
                      └─ FUN_00462C70 (pętla stanu)
                           └─ FUN_0044319A (tick stanu +0x368)
                                └─ FUN_0046BAD7 (dyspozytor na job)
                                     └─ FUN_0046D53A (potter handler, job 0x19)
                                          └─ FUN_0046E52E (logika produzione)
Kluczowe funkcje
Adres	Nazwa	Rola
0x4078C8	FUN_00473461	Główna pętla gry
0x46BAD7	FUN_0046BAD7	Dyspozytor na job (obsługuje joby 1-46)
0x46D53A	FUN_0046D53A	Potter handler (uniwersalny)
0x46E52E	FUN_0046E52E	Logika produkcji (sprawdza surowce)
0x44B910	FUN_0044B910	KLUCZOWE - faktycznie dodaje towar do stock
0x4316F3	FUN_004316F3	Bramka budynku (czy ma good)
0x4319D7	FUN_004319D7	Pobiera ilość towaru w budynku
0x431FA7	FUN_00431FA7	Min qty w budynku
0x44B7B5	FUN_0044B7B5	Ustawia tribe house good (+0x37A)
0x44B910	FUN_0044B910	Dodaje towar do tribe house stock (+0x37A)
0x46E117	FUN_0046E117	Ustawia selected good w tribe house
0x46E02B	FUN_0046E02B	Ustawia stan produkcji
FUN_0044B910 - DODAWANIE TOWARU DO STOCK
void FUN_0044B910(void *this, int good_idx, int qty)
{
    // this = tribe house
    // param_1 = good index
    // param_2 = qty (>0 = produkcja, <0 = zużycie)
    
    uVar2 = FUN_0044B8E8(this, param_1);  // znajdź slot
    if (not found) {
        for (uVar2 = 0; uVar2 < 0x15; uVar2++) {
            if (slot empty) {
                this->slot[uVar2].qty += param_2;    // +0xD0 + uVar2*0xC
                this->slot[uVar2].good_idx = param_1; // +0x338 + uVar2*3*4
                this->slot[uVar2].active = 1;        // +200 + uVar2*0xC
                return;
            }
        }
    } else {
        FUN_0044B96E(this, param_1, -param_2);  // odejmij
    }
}
4. Root cause - dlaczego smolarnia nie działa
Problem 1: FUN_00473461 (unit tick)
Obsługuje tylko typy 38 (szkoła) i 39 (koszary). Typ 57 (smolarnia) → wczesny return.
Problem 2: Dispatcher (FUN_0046BAD7)
Hardcoded limit 46 jobów. Job 56 (smolarz) nie jest obsługiwany - dwipatchuje do default.
Problem 3: Kolizja revmap dla good 66
- Stock revmap: +0x37C + 66*4 = +0x484 (kolizja z production_count)
- Production revmap: +0x4D8 + 66*4 = +0x5E0 (sąsiednie z +0x5E4)
Problem 4: Brak obsługi w tick budynku
FUN_00433662 sprawdza category == 6 i type == 3, ale nie ma logiki produkcji dla typu 57.
5. Plan implementacji
Opcja A: Code cave (najlepsza)
1. Znalźć wolne miejsce w .text (między 0x4F21CB a 0x4F3000 - ~3.5 KB wolne)
2. Dodać kod obsługujący logictype 57 w tick budynku
3. Dodać obsługę job 56 w dyspozytorze
4. Patch: zmienić imm 0x6B82 → 0x8578 (ID extension)
5. Zmienić FUN_00473461 aby obsługiwał typ 57
Opcja B: DLL injection (alternatywa)
1. Skompilować DLL z hookami
2. Wstrzyknąć do gry
3. Hook: FUN_0046BAD7 (dispatcher), FUN0043242C (job assignment), FUN0046E52E (produkcja)
Opcja C: Zmiana INI (najprostsza, ale ograniczona)
- Zmienić logictype 57 na 38 (szkoła) w houses.ini
- Problem: szkoła nie produkuje goods, tylko edukuje
- Nie rozwiązuje problemu produkcji węgla
6. Stan implementacji
Element	Status	Uwagi
RE dokumentacji	✅ Gotowe	Wszystkie kluczowe funkcje zidentyfikowane
Pseudokod Rust	✅ Gotowe	.ai/re_rust/all_functions.rs
Dekompilacja kluczowych funkcji	✅ Gotowe	14 funkcji kluczowych
Dokumentacja łańcucha produkcji	✅ Gotowe	re_production_chain.md
Dokumentacja Job Assignment Chain	✅ Gotowe	re_job_assignment.md
Pseudokod Rust batch4	✅ Gotowe	batch4_functions.rs
Implementacja hooków DLL	❌ Nieukończona	Plik cnmod_hook.cpp niekompletny
Kompilacja DLL	❌ Nieudana	Brak kompilatora C++ w PATH
Testowanie w grze	❌ Nieudane	Gra crashuje z patchami binarnymi
7. Następne kroki
1. Zbudować DLL z hookami - użyć clang++ (dostępny w C:\Program Files\LLVM\bin\clang++.exe)
2. Wstrzyknąć DLL do gry - użyć dll_injector.py lub ekst injector
3. Przetestować smolarnię - czy produkuje węgiel (good 66)
4. Dodać nowe budynki/surowce - użyć INI + code cave
8. Pliki kluczowe
Plik	Opis
.ai/docs/re/re_production_chain.md	Kompletny łańcuch produkcji z pseudokodem
.ai/docs/re/re_complete_summary.md	Kompletne podsumowanie RE
.ai/docs/re/re_engine_comprehensive.md	Główna dokumentacja silnika
.ai/docs/re/re_job_assignment.md	Struktura job assignment
.ai/docs/re/re_structures.md	Struktury danych
.ai/re_rust/all_functions.rs	Pseudokod wszystkich funkcji
.ai/re_rust/batch4_functions.rs	Pseudokod funkcji batch 4
.ai/re_rust/engine_structs.rs	Struktury danych silnika
.ai/re_rust/engine_pseudocode.rs	11 kluczowych funkcji
cnmod_hook/src/cnmod_hook.cpp	Kod DLL z hookami (niekompletny)
cnmod_hook/dll_injector.py	Injector w Pythonie
cnmod_hook/patch_extend_jobs.py	Skrypt patchujący binary (nieudany)
cnmod_hook/patch_all.py	Skrypt pełnego patcha (nieudany)
9. Uwagi
- Praca RE jest całkowita - wszystkie kluczowe funkcje zidentyfikowane i zdekompilowane
- Głównym problemem jest implementacja (kompilacja DLL, wstrzyknięcie)
- Architektura produkcji jest w pełni uniwersalna - potter handler obsługuje wszystkie budynki przez INI
- Główna bariera to dyspozytor jobów (tylko 46 jobów) oraz kolizja revmap dla good 66
- Rozwiązanie wymaga hookowania kodu maszynowego lub code cave w .text section
Dokument przygotowany przez REA (reverse-engineer-anything skill)  
Źródło: REA (Ghidra 12.1.4) + ręczna analiza binarnego