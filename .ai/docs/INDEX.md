# Indeks dokumentacji — CnMod Extended (CNMX)

Punkt startowy dla nowej sesji. Czytaj **od góry** — najnowsze na początku.

## 0. Decyzje projektowe

| Plik | Co zawiera |
|---|---|
| [`DECYZJA-2026-10-22-NAZWA-PROJEKTU.md`](DECYZJA-2026-10-22-NAZWA-PROJEKTU.md) | **Obowiązująca nazwa i zakres:** CnMod Extended (CNMX) = rozszerzenie silnika + ModKit. Węgiel drzewny to tylko pierwszy przypadek użycia. Tu też: czego świadomie **nie** zmieniamy (DLL, katalog, logi). |

## 1. Zacznij tutaj

| Plik | Co zawiera |
|---|---|
| [`../../AGENTS.md`](../../AGENTS.md) | **Zasady pracy agenta:** podział EtapC vs cnmod_hook, twarde ograniczenia, konwencje patchy i danych, pułapki środowiska, stan projektu. |
| [HANDOFF-2026-10-26-MAGAZYN-KATEGORIE.md](HANDOFF-2026-10-26-MAGAZYN-KATEGORIE.md) | **Najnowszy.** Magazyn/kategorie: panel budynku FUN_004a693b filtr <=0x37 (4 patche 0x000A7333/0xA7434/0xA7EF7/0xA7FB3), logicstock 66 dla stock 00/01/02; udokumentowano logike grupowania dobr (FUN_0045cbbe -> FUN_004e1b04, kategorie w oknie targu, panel magazynu bez kategorii). Tabela 683 wpisow, EtapC.dll przebudowany. |
| [`HANDOFF-2026-10-24-WEGIEL-OBRAZEK-I-MAGAZYN.md`](HANDOFF-2026-10-24-WEGIEL-OBRAZEK-I-MAGAZYN.md) | **Najnowszy.** Brak obrazka i magazynu dla węgla (good 66): dodano `logicgood 66` / `good_stone` do `goodgraphics.cif`; patche EtapC `0x42→0x43` już zastosowane (678/678) w tym magazyn `0x497D63`, ikona `0x7E7D0`, tablica `0x8A193`. |
| [`HANDOFF-2026-10-22-WIERSZ-PRODUKTU-PRACA.md`](HANDOFF-2026-10-22-WIERSZ-PRODUKTU-PRACA.md) | Wiersz „Węgiel ∞" w sekcji „Praca" (root cause `0x4AC6E9`), strażnik `revmap[66]` (węgiel→mąka), stan wdrożenia, lista otwartych tematów. |
| [`HANDOFF-2026-10-22-DOSWIADCZENIE-SMOLARZ.md`](HANDOFF-2026-10-22-DOSWIADCZENIE-SMOLARZ.md) | Doświadczenie job 56: rekord typu 71, `humanjobexperiencetypes.ini`, „Wypalanie Węgla". |
| [`HANDOFF-2026-10-21-ZAPIS-SMOLARZ.md`](HANDOFF-2026-10-21-ZAPIS-SMOLARZ.md) | Crash przy zapisie/wczytaniu, `STRIDE_PLIST`, spam w logach. |
| [`HANDOFF-2026-10-20-PRODUKCJA-ROOT-CAUSE.md`](HANDOFF-2026-10-20-PRODUKCJA-ROOT-CAUSE.md) | Root cause produkcji węgla (bramka `0x42DA65`, `prodmap`, `can_produce`). |

## 2. Chronologia prac nad smolarzem / węglem

| Plik | Etap |
|---|---|
| [`HANDOFF-smolarz-wegiel.md`](HANDOFF-smolarz-wegiel.md) | Start: rozpoznanie, plan dodania dobra 66 i pracy 56. |
| [`HANDOFF-smolarz-wegiel-FAZA1-2026-10-19.md`](HANDOFF-smolarz-wegiel-FAZA1-2026-10-19.md) | Faza 1: dane, typy, grafiki. |
| [`HANDOFF-smolarz-wegiel-FAZA2-2026-10-19.md`](HANDOFF-smolarz-wegiel-FAZA2-2026-10-19.md) | Faza 2: produkcja, przypisanie pracy, UI. |
| [`analiza-brakujacych-patchy-parser-coal.md`](analiza-brakujacych-patchy-parser-coal.md) | Audyt: które miejsca parsera/limitów trzeba rozszerzyć. |
| [`raport-audyt-patchy-etapc-i-coal.md`](raport-audyt-patchy-etapc-i-coal.md) | Audyt tabeli patchy pod kątem węgla. |

## 3. Wiedza o silniku (reverse engineering)

| Plik | Temat |
|---|---|
| [`re/re_complete_summary.md`](re/re_complete_summary.md) | **Przegląd całości** — struktury, funkcje, przepływy. |
| [`re/re_engine_comprehensive.md`](re/re_engine_comprehensive.md) | Silnik: init, pętla, ładowanie danych. |
| [`re/re_production_flow.md`](re/re_production_flow.md), [`re/re_building_production.md`](re/re_building_production.md), [`re/re_production_pipeline.md`](re/re_production_pipeline.md) | Produkcja: od rekrutacji po zapis do magazynu. |
| [`re/re_structures.md`](re/re_structures.md) | `house_type`, `unit`, `tribe`, `good_type` — offsety. |
| [`re/re_ui_system.md`](re/re_ui_system.md) | Okna, dispatcher `0x4E21B7`, sekcje panelu człowieka. |
| [`re/re_job_assignment.md`](re/re_job_assignment.md), [`re/re_jobblock_structure.md`](re/re_jobblock_structure.md) | Prace i bloki `prodmap`. |
| [`re/runtime_hook_plan.md`](re/runtime_hook_plan.md) | Podział EtapC vs cnmod_hook, zasady hookowania. |
| [`re/re_fix_plan.md`](re/re_fix_plan.md) | Plan napraw (historyczny). |
| [`layout-constants.md`](layout-constants.md) | Stałe layoutu UI/HUD. |
| [`typy-budynkow-surowcow.md`](typy-budynkow-surowcow.md) | Budynki i surowce — ściąga. |
| [`goods-mechanism-analysis.md`](goods-mechanism-analysis.md) | Mechanika dóbr, `revmap`, magazyny. |
| [`rozszerzenie-slotow-budynkow-weryfikacja.md`](rozszerzenie-slotow-budynkow-weryfikacja.md) | Sloty budynków (`+0x84 + slot*0x40`). |

## 4. Instrukcje i plany

| Plik | Temat |
|---|---|
| [`jak-dodac-budynek-lub-surowiec.md`](jak-dodac-budynek-lub-surowiec.md) | Procedura dodania dobra/budynku. |
| [`PLAN-narzedzia-gui.md`](PLAN-narzedzia-gui.md) | **Docelowe narzędzie z GUI** (zastąpi `modkit.py`): zakres MVP, model danych, architektura, otwarte decyzje. |
| [`STANDARD-pliki-ini.md`](STANDARD-pliki-ini.md) | **Format danych:** cp1250, CRLF, bez BOM; co naprawiono 2026-10-22 i jak działa odtwarzanie utraconych liter (`.ai/scripts/ini_normalize.py`). |
| [`Instrukcja-modkit.md`](Instrukcja-modkit.md), [`modkit-a.md`](modkit-a.md) | *Archiwalne.* Prototyp CLI `modkit.py` — źródło logiki, nie produkt. |
| [`edytor-etap-d.md`](edytor-etap-d.md), [`etap-d-doprocowanie.md`](etap-d-doprocowanie.md) | Edytor Etap D. |
| [`status-ctest.md`](status-ctest.md), [`final-status.md`](final-status.md) | Statusy etapów (historyczne). |
| [`../plans/`](../plans/) | Plany: skalowanie HUD, fonty, wrapper ddraw, narzędzia. |

## 5. Surowce analityczne

| Ścieżka | Zawartość |
|---|---|
| [`../re_out/`](../re_out/) | Zdekompilowane funkcje (dispatcher, produkcja, potter, UI). |
| [`../decoded/`](../decoded/) | Zrzuty tabel `.cif` → tekst (`goodtypes`, `jobtypes`, `housetypes`). |
| [`../re_rust/`](../re_rust/) | Pseudokod struktur i funkcji w Rust (notatki). |
| [`../reports/`](../reports/) | Raporty etapów i klasyfikacje. |
| [`../scripts/`](../scripts/) | Narzędzia: PE, dysasemblacja, CIF↔TXT, fonty. |

## 6. Zasady, które trzeba znać przed zmianą kodu

1. `EtapC` = dane/tabele; `cnmod_hook` = zachowanie. Bez duplikacji.
2. `cnmod_hook` **nie** patchuje `0x46BAD7` ani `FUN_0044A0D9` (własność EtapC).
3. Frida tylko tam, gdzie MinHook nie hookuje; tylko RAM, nigdy `Interceptor`.
4. Granica dóbr `0x42 → 0x43`; nigdy `0x7F`.
5. Zawsze kończ sesję wpisem `HANDOFF-<data>-<temat>.md` i dopisz go do tego indeksu.
