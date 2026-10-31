# HANDOFF 2026-10-30 — WŁASNA GRAFIKA WĘGLA I FIZYKA UPUSZCZANIA (good 66 / landscapetype 88)

## 1. Cel
Użytkownik zażądał:
- Węgiel (good 66) musi mieć własną grafikę węgla (nie żelaza, nie kamienia).
- Grafika oparta na kształcie kamienia (sterty kamieni), ale z kolorem czarnym/antracytowym (węgiel).
- Po upuszczeniu na ziemię węgiel musi pozostać węglem (fizyka i surowiec zachowane, podnoszenie zwraca węgiel 66).

## 2. Architektura silnika a grafika i fizyka dóbr
W silniku Cultures grafika dóbr w panelach oraz obiekty leżące na ziemi są ściśle połączone poprzez `landscapetype` w `goodtypes.ini`:
1. `FUN_00415e8a` wywołuje `FUN_0047fef0(landscapetype, 1)`, które wyszukuje w `landscapes.cif` wpis o pasującym `LogicType`.
2. Zwrócony indeks wpisu jest zapisywany w `good_types[good]+0x24` i używany do renderowania tagu `{gfxgood:%d,1}` (panel HQ, smolarnia, magazyn).
3. Gdy dobra są upuszczane na mapę, silnik tworzy obiekt krajobrazu o typie `landscapetype`.
4. Plik `landscapetypes.cif` definiuje dla każdego typu zachowanie:
   - `transition 3 <type> 2 -1 <good_id>` — podniesienie z ziemi zwraca towar `<good_id>`.
   - `transition 4 <type> 2 +1 0` — upuszczenie tworzy stertę krajobrazu.

Wcześniejsze próby ustawiania `landscapetype 17` (kamień) lub `20` (żelazo) powodowały zamianę węgla w kamień lub żelazo.
Silnik w `etapa_gen/patches_ext.h` miał już rozszerzoną tablicę `landscapetypes` z 88 do 127 (`0x7F`) pod adresami `0x0016316`, `0x0016330`, `0x00163FA`. Dzięki temu wolny slot `landscapetype 88` jest w 100% natywnie obsługiwany.

## 3. Co zrobiono

### 3.1 Nowa paleta PCX: `Data\engine2d\bin\palettes\goods\goods_coal.pcx`
- Skopiowano strukturę i wymiary z `goods_stone.pcx`.
- Paletę 256 kolorów przekształcono: odcienie kamienia zmapowano na głęboki, węglisty antracyt z zachowaniem cieniowania i subtelnych refleksów (RGB w zakresie 10..55 z chłodnym tonem węgla).

### 3.2 Rejestracja palety: `Data\engine2d\inis\palettes\palettes.cif`
- Zdekodowano przez `cif2txt.exe C`.
- Dodano wpis:
  ```
  %01%GfxPalette256
  %02%editname "goods_coal"
  %02%gfxfile "data\engine2d\bin\palettes\goods\goods_coal.pcx"
  %02%gfxpreshade 1
  ```
- Zaktualizowano nagłówek linii i zakodowano przez `cif2txt.exe T`.

### 3.3 Paleta dla tragarza: `Data\engine2d\inis\humans\randompalette.cif`
- Dodano wpis palety dla noszenia węgla w dłoniach:
  ```
  %01%RandomPalette
  %02%Name "good_coal"
  %02%Patch 14 "colors grey dark" 10
  %02%Patch 15 "colors grey dark" 10
  ```

### 3.4 Powiązanie grafiki noszenia: `Data\engine2d\inis\goods\goodgraphics.cif`
- Dla `logicgood 66` zaktualizowano:
  `%02%graphicshumanrandompalette "good_coal"`

### 3.5 Nowy typ krajobrazu: `Data\logic\landscapetypes.cif`
- Dodano `landscapetype 88`:
  ```
  %01%landscapetype
  %02%type 88
  %02%name "coal"
  %02%allowedonland 1
  %02%maximumValency 6
  %02%transition 3 88 2 -1 66
  %02%transition 4 88 2 +1 0
  %02%debugcolor 20 20 20
  ```
  Kluczowe: `transition 3 88 2 -1 66` gwarantuje, że podniesienie sterty z ziemi zwraca **dobro 66 (Węgiel)**!

### 3.6 Nowy obiekt krajobrazu: `Data\engine2d\inis\landscapes\landscapes.cif`
- Dodano `coal pile 01`:
  ```
  %01%GfxLandscape
  %02%EditName "coal pile 01"
  %02%EditGroups "goods all" "good piles all" "good piles build"
  %02%LogicType 88
  %02%LogicMaximumValency 5
  %02%LogicIsWorkable 1
  %02%logicispileableonmap 1
  %02%LogicWorkArea 1 0 0 1
  %02%GfxBobLibs "data\engine2d\bin\bobs\ls_goods.bmd" "data\engine2d\bin\bobs\ls_goods_s.bmd"
  %02%GfxPalette "goods_coal"
  %02%GfxFrames 5 19
  %02%GfxFrames 4 18
  %02%GfxFrames 3 17
  %02%GfxFrames 2 16
  %02%GfxFrames 1 15
  %02%GfxStatic 1
  %02%GfxLoopAnimation 0
  %02%GfxShadingFactor 0.600000
  %02%GfxUserFXMatrix 0
  %02%GfxDynamicBackground 0
  %02%gfxdrawvoidever 0
  %02%GfxTransition 3 "coal pile 01"
  %02%GfxTransition 4 "coal pile 01"
  ```
  Używa klatek 15..19 z `ls_goods.bmd` (sterta surowca jak kamień), ale z nową czarną paletą `"goods_coal"`.

### 3.7 Definicja dobra: `Data\logic\goodtypes.ini`
- Dla węgla (`type 66`) ustawiono:
  ```ini
  [goodtype]
  name "coal"
  type 66
  landscapetype 88
  isInputGoodFlag 1
  isProducedInHouseFlag 1
  isProducedOnMapFlag 0
  landscapeToHarvest 18
  landscapeToPickup 88
  landscapeToStore 88
  atomicForHarvesting 24
  productionInputGoods 5
  atomicForProduction 46
  ```

## 4. Backupy
Wszystkie pliki przed modyfikacją zostały zarchiwizowane zgodnie z AGENTS.md §8:
- `Data\engine2d\inis\palettes\palettes.cif.bak_coal_20261030_182737`
- `Data\engine2d\inis\humans\randompalette.cif.bak_coal_20261030_182737`
- `Data\engine2d\inis\goods\goodgraphics.cif.bak_coal_20261030_182737`
- `Data\logic\landscapetypes.cif.bak_coal_20261030_182737`
- `Data\engine2d\inis\landscapes\landscapes.cif.bak_coal_20261030_182737`
- `Data\logic\goodtypes.ini.bak_coal_88_20261030_182737`

Walidacja `ini_normalize.py`: `plikow zmienionych 0, odtworzonych znakow 0, linii mojibake 0`.

## 5. Wynik
- Węgiel (good 66) ma w panelach UI (HQ, smolarnia, magazyn) ikonę czarnej sterty węgla.
- Noszony w rękach węgiel ma ciemnoszarą paletę.
- Upuszczony na ziemię węgiel leży jako czarna sterta węgla (`landscapetype 88`).
- Podniesienie węgla z ziemi dodaje do ekwipunku węgiel (good 66).

> **Aktualizacja 2026-10-31:** stackowanie (2+ węgli na jednym polu) naprawiono osobno.
> Przyczyną była zdublowana nazwa obiektu `coal pile 01` w `landscapes.cif` — szczegóły:
> [`HANDOFF-2026-10-31-WEGIEL-STACKOWANIE.md`](HANDOFF-2026-10-31-WEGIEL-STACKOWANIE.md).
