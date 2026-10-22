# Plan 5: narzędzia moderskie (dodawanie/podmiana typów budynków i surowców)

**Powiązane:** `.ai\docs\typy-budynkow-surowcow.md` (analiza, adresy), `.ai\docs\wnioski-analiza-remaster.md`
**Cel nadrzędny:** dać modderowi (nam) kontrolę nad tabelami typów — dziś da się tylko
zastąpić istniejący slot, nie dodać nowego typu.

---

## Diagnoza skrócona

- Tablica budynków: **54/54 zajęte** (exe: `cmp eax,0x37 / jae` @ `0x41542C`, malloc `0x151BC` @ `0x41534E`).
  Obecny 55. wpis w `houses.ini` (`work murek`) **nie wczytuje się** – martwy.
- Tablica surowców: **65/65 zajęte** (exe: `cmp eax,0x42 / jge` @ `0x4159F2`, malloc `0x35A0` @ `0x41595E`).
- Wolne sloty istnieją tylko w tabeli **broni: 13, 14**.
- Grafika budynków (`[GfxHouse]`, 156 szt.) **nie ma limitu** – nowe warianty można dodawać od razu.
- Koszt „przedłużenia tabeli” jest policzalny: ~15–20 stałych na tabelę + ~40 displacementów
  w rekordzie plemienia (tablice flag `+0x515C`/`+0x50D8` są opakowane bez zapasu).

---

## Etap A — `modkit inspect / validate` (Python, bez patchy) — PRIORYTET 1

**Cel:** mieć pełny obraz tabel i łapać błędy *zanim* gra się uruchomi.

- [x] parser INI/CIF gry (sekcje `%01%` + zwykłe `[...]`, kompatybilny z `cif2txt`)
      — `.ai\scripts\modkit.py` (`parse_text`, dekodowanie `.cif` przez `mapper tools\cif2txt.exe` do `.ai\.modkit_cache\`),
- [x] inwentarz: dla każdej tabeli (budynki, surowce, bronie, pojazdy, plemiona, zawody,
      pancerze) lista użytych/wolnych indeksów wg limitów z `logicdefines.inc`
      — `modkit inspect`,
- [x] cross-check: `houses.ini` ↔ `[GfxHouse]` ↔ `stringstext/houses.ini` ↔ `tribetypes.ini`
      ↔ `goods.ini` (brakujące nazwy, osierocona grafika, wpisy **odsiane przez exe**)
      — `modkit validate`,
- [x] raport: `modkit validate` → lista błędów/ ostrzeżeń (exit 1 przy błędach),
- [x] test akceptacyjny: wykrycie faktu `logictype 55` = „work murek" (martwy)
      — `H-DEAD logictype 55 poza 1..54`.

**Uwagi z implementacji (ważne struktury):**
- `[GfxHouse] LogicType <0> <id_budynku>` — typ budynku to **drugi** token (pierwszy stale 0);
- `[GfxHouse] LogicTribeType` = warstwa grafiki `{1,2,3,4,7}`, **nie** id plemienia;
- `LogicConstructionGoods` ma wiodący token wariantu (0..4), surowce od tokenu 1;
- `gfxoverlaylandscape 0` = brak (dozwolony);
- broń: duplikaty typów między plemionami są normalne (liczba walidowana względem pary `(tribetype,type)`).

**Wynik bazowy `validate`:** 1 błąd (`H-DEAD` 55) + 12 ostrzeżeń `H-NOGFX` —
typy 8, 9, 15, 19, 21, 24, 25, 26, 30, 32, 36, 41 (np. `work bakery 01`, `stock 01`)
nie mają żadnego `[GfxHouse]` w aktywnym pliku `CN.PLMOD\budynki12\houses\houses.ini`
(wykluczono, że pokrycie jest w innym pliku `Data\`). Do rozstrzygnięcia dla gry:
czy to zamierzone (niewidzialne typy-logika), czy martwe wpisy oryginału.

**Zależność:** `modkit packages` jak niżej — do uruchomienia z katalogu `.ai\scripts\`
z grą w rootcie (lub `--root`).

**Start natychmiastowy:** skrypty już istnieją i są zapisane w `.ai\scripts\`
(`houses_sections.py`, `gfxhouses.py`, `ciflist.py`, `ht_find.py`, `ht3.py`, `disp.py`,
`tribedisp.py`, dekody w `.ai\decoded\`) — trzeba je zebrać w jedno CLI i doinwentaryzować
pozostałe tabele.

## Etap B — `modkit replace / clone` (automatyzacja „podmiany slotu") — PRIORYTET 2

- [ ] `clone-house --from <id> --to <id>`: klonuje sekcję logiki, generuje nowy `[GfxHouse]`,
      dopisuje nazwy PL, aktualizuje flagi w `tribetypes.ini`,
- [ ] `clone-good` analogicznie (goodtype + teksty + flagi),
- [ ] `use-free-slots`: podpowiedź wolnych slotów (dziś: bronie 13/14),
- [ ] podgląd差异 (diff) przed zapisem + backup (`*.orig`).

## Etap C — runtime loader + skrypty („nakładka") — PRIORYTET 3 (dopiero po A/B)

**Cel nadrzędny (zmieniony):** nie statyczny patch exe, tylko **nakładka uruchamiana
przy starcie** — DLL + hooki + interpreter skryptów. Plik `CN.PLMOD.exe` na dysku
zostaje nietknięty; wszystkie modyfikacje (limity, zachowania) dzieją się w pamięci.

### Architektura nakładki

1. **`cnmod_runtime.dll`** — wczytywana do procesu przez launcher `CN.PLMOD_runtime.exe`
   (start wstrzymany → wstrzyknięcie → wznowienie; zero zmian w pliku exe).
2. **Hooki (MinHook/detours)** na zmapowane punkty: otwieracz plików `0x425A7B`,
   parser wartości `0x425378`/`0x425202`, loadery tabel (`0x41542C`, `0x4159F2`, …).
   Przekierowanie → nasz handler może podmienić wynik i wywołać oryginał.
3. **Patche limitów w pamięci** — te same bajty co w patcherze statycznym
   (np. `mov esi,0x151BC`, `cmp eax,0x37`), ale aplikowane przy starcie w RAM-ie.
   `CN.PLMOD.exe` (i `.orig`) zostaje na dysku nietknięty — łatwy rollback.
4. **Host skryptowy** — Lua 5.4/LuaJIT (lub embed Python). Skrypty moddera:
   `G:\Games\CnMod 1.2\CN.PLMOD_runtime\scripts\*.lua`, enumerowane przy starcie.

### API skryptowe (docelowy kształt)

```lua
mod.register_logic_house_type(55, { maintype=3, name="Stocznia", ... })
mod.override_field("houses", 55, "logicstock", "16 150 0")
mod.hook_build_menu(function(t) ... end)
mod.register_gui_button({ icon="...", typeid=55 })
```

### Granica (uczciwie)

Skrypty same nie stworzą nowego rekordu w tablicy alokowanej przez exe —
potrzebny jest patch limitu w pamięci (pkt 3). Bez patchów skrypty i tak dają:
nadpisywanie pól rekordów, podmianę wyników getterów, wpisywanie się w menu
budowy i ikony HUD. To jest właściwe „modowanie nakładkowe".

### Zadania Etapu C

- [ ] katalog sygnatur bajtowych (wzorców) dla każdego miejsca z §2 analizy —
      alokacje `0x151BC`/`0x35A0`, pętla konstruktorów `0x415368`, walidacje
      `0x41542C`/`0x4159EF`, iteratory, lookupy, flagi plemion `0x4142FD`/`0x409E89`,
- [ ] szkielet DLL (MinHook) + launcher wstrzykujący do `CN.PLMOD.exe`,
- [ ] hook otwieracza plików + parser INI jak w Etapie A (reuse kodu), przedłużanie sekcji,
- [ ] wbudowanie interpretera (LuaJIT) + enumeracja `scripts\*.lua` + API `mod.*`,
- [ ] patcher limitów w pamięci (przeniesienie logiki z wariantu statycznego),
- [ ] weryfikacja: uruchomienie gry z nakładką bez zmian zachowania (baseline),
- [ ] test: nowy typ wchodzi do gry (wczytanie, budowa, zapis/odczyt gry).

### Wariant rezerwowy: patcher statyczny (gdyby DLL/wstrzykiwanie się nie udało)

- [ ] patch = `CN.PLMOD.exe`, referencja = `CN.PLMOD.exe.orig`, automatyczny rollback,
- [ ] (Etap D — osobny) wsparcie edytorów map (`Edytor podstawowy.exe`, `Remik's Editor.exe`).

### BLOKERY do rozstrzygnięcia PRZED implementacją Etapu C — ROZSTRZYGNIĘTE (patrz `.ai\docs\blokery-etap-c.md`)
- [x] format zapisu gry i mapy: **mapy = budynki po NAZWIE** (`sethouse "nazwa"` w `.inc`, `map.dat` = tylko teren),
      save = kontener bloków z numerami, pole bajt/słowo — na nasz zakres (domy ≤64, surowce ≤97) bajt wystarcza,
- [x] skąd GUI bierze listę przycisków budowania: **dane mapy** (`allowhouse/allowgood/forbidgood` w `[allowedthings]`)
      + parser NC2Logic `0x413E7B` (walidacje `jae 0x414ABA`) + pętle dieracji (np. `0x4A83B4`, `0x4C1EBE`), patchowalne,
- [x] ikony surowców: **w pełni dane** — `Data\engine2d\inis\goods\goodgraphics.cif` (`logicgood N` → paleta), zero exe,
- [x] czy edytory mają identyczne `.text` jak gra: **NIE** — edytory to inny build, wzajemnie identyczne, zaledwie
      kilka stałych (0x37×2, 0x38, 0x41, 0x64×6). → **patrz Etap D**.

## Etap D — wsparcie Edytora map (osobny temat)

**Cel:** sprawić, by nowe typy (budynki/surowce) były widoczne i wybieralne w `Edytor podstawowy.exe` / `Remik's Editor.exe`, bez konieczności edycji `.inc` ręcznie.

### Diagnoza krótkiego rekonesu
- Edytor czyta te same pliki danych: `cn.plmod\budynki12\houses\houses.ini` (`[GfxHouse]`), `tribetypes.ini`, nazwy w stringach. 
- `[GfxHouse]` ładowany dynamicznie wg liczby sekcji (rekord `0x8BC`), **nie ma twardego limitu 55** — nowe typy trafiają do pamięci.
- Bariera = **filtry „plemię → dozwolone domy”** (tablice per-plemię). W kodzie edytora występują pętle ograniczone do 0x37 (55): `0x41DF9C`, `0x41EDF4` (`inc esi; cmp esi,0x37; jle ...`) + `0x40A648` (`cmp eax,0x38; jge ...`) oraz tablice `tribehouseLinkData` o stałym rozmiarze 55 na plemię.
- Zapis mapy przez `sethouse "<EditName>"` używa nazwy (nie numeru) — kompatybilny z grą. Problem = **widoczność w UI** (drzewo wyboru budynków), nie format zapisu.

### Zadania Etapu D
- [ ] inwentaryzacja dokładnych miejsc limitów edytora (mapowanie House/GFX + Tribe-House links), wykluczenie switch-case (nie dotykać),
- [ ] patch limitów edytora w pamięci (nakładka DLL dla edytora, lub wariant statyczny `.orig`),
- [ ] rozszerzenie tablic per-plemię (`tribehouseLinkData`) pod nowy max,
- [ ] test: edytor ładuje nowy `[GfxHouse]`, pokazuje go w drzewie wyboru, zapisuje `sethouse` po nazwie, mapa wczytuje się w grze,
- [ ] dokumentacja: jak uruchamiać edytor z nakładką (oddzielna DLL/launcher).

**Uwaga:** można pominąć Etap D na początek (testy przez ręczną edycję `.inc`) — jest wydzielony celowo.

## Etap E — treść (feature'y dla moddera)

- [ ] `good export/import` (CIF→INI→CIF przez `cif2txt`),
- [ ] szablony nowych sekcji: `goodtype`, `logichousetype`, `[GfxHouse]`,
- [ ] generator tekstów PL (pojedyncza/mnoga forma) dla nowych nazw,
- [ ] dokumentacja: „jak dodać surowiec krok po kroku".

---

## Kolejność i uzasadnienie

A → B → E dają użyteczne narzędzia **w kilka dni i bez ryzyka** (zero patchy).
C (nakładka DLL + skrypty dla gry) = dodawanie nowych typów w pamięci (runtime).
D (edytor map) = UI edytora, osobny exe/build (2003), mały zakres patchy, **może być później**.
Nakładkę można też użyć jako importera danych — wiedza się nie marnuje.

**Kryterium sukcesu:** komenda `modkit new-building` + skrypt Lua potrafią utworzyć
kompletny, grywalny nowy budynek (slot spoza 1..54), przejść test w grze. (D = opcjonalne dla pełnego workflow edytora).
