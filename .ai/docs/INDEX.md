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
| [HANDOFF-2026-10-29-RE-SPRITE-DRAWING.md](HANDOFF-2026-10-29-RE-SPRITE-DRAWING.md) | **Najnowszy.** RE: wpisy odpowiedzialne za rysowanie sprite'ów zasobów (HQ / magazyn / produkcja) — lookup `FUN_0042f710/754/776` + tablice `DAT_00511698/0x116A0/0x116A4`, `FUN_0042bcae`, `FUN_0042f798` + `FUN_0047ffc0` (instancje `*0x8BC+0x3C+DAT_00568C0C`), widget `FUN_004a85cb` (vtable `PTR_FUN_004f64C0`), primitives `FUN_004e2172`/`FUN_004e1e3f`/`FUN_004e162e`/`FUN_004e556b`/`FUN_004e5410`/`FUN_004e21b7`; ścieżki: HQ `FUN_004a009d→FUN_004a60a2→FUN_004a693b`, magazyn `FUN_00497bc8`/`FUN_004c227c`, produkcja `FUN_0049067f→FUN_00494f01→FUN_00495e0c`. |
| [HANDOFF-2026-10-29-PANEL-HQ-MAX-SUROWCE.md](HANDOFF-2026-10-29-PANEL-HQ-MAX-SUROWCE.md) | Panel HQ „największa ilość surowców”: węgiel widoczny przy 0 i zawsze na końcu. Przyczyna: `hook_catbuild` dopisywał dobra kategorii 0 do grupy `this+0x180` **po** sortowaniu w `FUN_004a847a`. Poprawka: hook pomija kategorię 0 + patch EtapC `0x000A8501` (`cmp ebx,0x37 -> 0x42`) włączający dobro 66 do sortowanej listy (tylko `qty != 0`). Analiza: [`RE-ANALIZA-PANEL-HQ-MAX-SUROWCOW.md`](RE-ANALIZA-PANEL-HQ-MAX-SUROWCOW.md). |
| [HANDOFF-2026-10-28-fix-crash-ladowania-zapisu.md](HANDOFF-2026-10-28-fix-crash-ladowania-zapisu.md) | Crash `AV: READ @ 0x00000000` przy ladowaniu zapisu na `FUN_004a15ce (0x4A15CE)`: przy ladowaniu `FUN_00405a79()` zwraca false, a `DAT_005116d4` jest NULL — oryginalny kod robi `CMP byte ptr [EAX], 0` z EAX=0. Naprawiono hookiem `hook_fun_4a15ce` w cnmod_hook.dll z null-checkiem na `DAT_005116d4` (zwraca false zamiast crashować). |
| [HANDOFF-2026-10-27-CRASH-SMOLARNIA-MAGAZYN.md](HANDOFF-2026-10-27-CRASH-SMOLARNIA-MAGAZYN.md) | Crash `AV: READ @ 0xFFFFFF80` po kliknięciu budynku = cztery **błędne** patche `0x38→0x43` (`0x000A8022/0xA80FC/0xA81FA/0xA82C6` trafiały w środek cudzych instrukcji) — usunięte, `PATCH_COUNT` = 683. Panel magazynu ma **4** filtry (`0x37→0x42`), nie 8. „Magazyn pusty" = edytowany zły plik: gra czyta `CN.PLMOD/types/houses.ini` (`0x0050055C`), nie `Data/logic/houses.ini`; dopisano `logicstock 66 45/70/120 0` do `stock 00/01/02`. Szczegóły: [`re/RE-ANALYSIS-PART90-2026-10-27-CRASH-MAGAZYN.md`](re/RE-ANALYSIS-PART90-2026-10-27-CRASH-MAGAZYN.md). |
| [RE-ANALYSIS-PART91-2026-10-27-WIERSZ-IKONA-KATEGORIA.md](re/RE-ANALYSIS-PART91-2026-10-27-WIERSZ-IKONA-KATEGORIA.md) | Trzy problemy z węglem (66): (1) brak wiersza w magazynie — flaga `logicstock` = 0, zmieniono na 1 we wszystkich 5 wpisach (`houses.ini` + backup); (2) brak ikony — powinna pojawić się po fladze=1 (`goodgraphics.cif` ma `logicgood 66/good_stone`, `goods_stone.pcx` istnieje); (3) kategoria ini-configurable — nowy hook cnmod_hook nad `FUN_0045cbbe @ 0x45CBBE`, plik `CN.PLMOD/types/goodcategories.ini` (`66 = 5`), cnmod_hook.dll odbudowane (264192 B). |
| [HANDOFF-2026-10-26-MAGAZYN-KATEGORIE.md](HANDOFF-2026-10-26-MAGAZYN-KATEGORIE.md) | Magazyn/kategorie: panel budynku FUN_004a693b filtr <=0x37 (4 patche 0x000A7333/0xA7434/0xA7EF7/0xA7FB3), logicstock 66 dla stock 00/01/02; udokumentowano logike grupowania dobr (FUN_0045cbbe -> FUN_004e1b04, kategorie w oknie targu, panel magazynu bez kategorii). Tabela 683 wpisow, EtapC.dll przebudowany. |
| [`HANDOFF-2026-10-24-WEGIEL-OBRAZEK-I-MAGAZYN.md`](HANDOFF-2026-10-24-WEGIEL-OBRAZEK-I-MAGAZYN.md) | Brak obrazka i magazynu dla węgla (good 66): dodano `logicgood 66` / `good_stone` do `goodgraphics.cif`; patche EtapC `0x42→0x43` już zastosowane (678/678) w tym magazyn `0x497D63`, ikona `0x7E7D0`, tablica `0x8A193`. |
| [`HANDOFF-2026-10-22-WIERSZ-PRODUKTU-PRACA.md`](HANDOFF-2026-10-22-WIERSZ-PRODUKTU-PRACA.md) | Wiersz „Węgiel ∞" w sekcji „Praca" (root cause `0x4AC6E9`), strażnik `revmap[66]` (węgiel→mąka), stan wdrożenia, lista otwartych tematów. |
| [`HANDOFF-2026-10-22-DOSWIADCZENIE-SMOLARZ.md`](HANDOFF-2026-10-22-DOSWIADCZENIE-SMOLARZ.md) | Doświadczenie job 56: rekord typu 71, `humanjobexperiencetypes.ini`, „Wypalanie Węgla". |
| [`HANDOFF-2026-10-21-ZAPIS-SMOLARZ.md`](HANDOFF-2026-10-21-ZAPIS-SMOLARZ.md) | Crash przy zapisie/wczytaniu, `STRIDE_PLIST`, spam w logach. |
| [`HANDOFF-2026-10-20-PRODUKCJA-ROOT-CAUSE.md`](HANDOFF-2026-10-20-PRODUKCJA-ROOT-CAUSE.md) | Root cause produkcji węgla (bramka `0x42DA65`, `prodmap`, `can_produce`). |

## 2. Chronologia prac nad smolarzem / węglem

| Plik | Etap |
|---|---|
| [`HANDOFF-smolarz-wegiel.md
- HANDOFF-2026-10-27-wegiel-w-hq.md`](HANDOFF-smolarz-wegiel.md
- HANDOFF-2026-10-27-wegiel-w-hq.md) | Start: rozpoznanie, plan dodania dobra 66 i pracy 56. |
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
