# Blokery Etapu C — rozstrzygnięte (rekonens 2026-10)

**Powiązane:** `.ai\plans\plan-5-narzedzia-moderskie.md` (Etap C), `.ai\docs\typy-budynkow-surowcow.md`.
**Status:** wszystkie 4 blokery zbadane — żaden nie jest „niemożliwy"; każdy ma konkretny koszt.

---

## 1) Format zapisu gry i mapy: bajt czy słowo? → **nie jest barierą**

### Mapy — budynki po NAZWIE (tekst), nie po numerze
- Mapa = katalog (np. `CN.PLMAPS\2Forty\`) z `map.ini` + binarne `map.dat` + tekstowe `.inc`.
- `map.ini` includuje `mission.inc / staticobjects.inc / ai.inc / player.inc / misc.inc`.
- **Budynki na mapie definiowane przez NAZWĘ** (nie id!):
  ```
  sethouse 2 "frank barn" 0 1 270 40 0
  addgoods "fish" 30
  ```
  w `staticobjects.inc`; surowce w `[GfxHouse] LogicConstructionGoods` też po nazwie/ide.
- `map.dat` **NIE zawiera budynków** (test: 0 z 18 nazw budynków mapy obecnych w binarium;
  plik to teren/wysokość/landscape + kontener bloków `hoixigol`/`hoixmmgl`).
- Parser `sethouse` w exe (struna `StaticObjects` @ `0x41D2A0`) i rejestr `[GfxHouse] EditName`
  (`CN.PLMOD\budynki12\houses\houses.ini`, 156 wpisów) — nowy typ = nowa nazwa. **Zero limitu na mapie.**

### Save-y — numery, ale na nasze skale bajt wystarcza
- `.sav` = kontener bloków z magic-nagłówkami `hoixvgsx`/`hoixigsx`/… (identyczny schemat jak
  `map.dat`). EXE nie zawiera tych magic-stringów → bloki czytane po kolei wg ustalonego układu
  (dyspozytor bloków `0x4127EF` + id bloków, np. `0x13`/`0x16`).
- House'y w save trzymane **numerycznie** (żadne nazwy budynków z mapy nie występują w save).
- **Pole typ = bajt lub słowo — obojętne:** planowany zakres (domy do ~64, surowce do ~97)
  mieści się w jednym bajcie (oba < 128). Ostateczna szerokość pola ustalana w Etapie C
  (hook zapisu/odczytu), ale **nie blokuje** rozszerzenia.
- Rekordy (stride potwierdzone w exe):
  - dom = `0x624` (1572 B), tablica `55 × 0x624 = 0x151BC` (malloc @ `0x41534E`),
  - surowiec = `0xD0` (208 B), tablica `66 × 0xD0 = 0x35A0` (malloc @ `0x41595E`).
  - Przy nowych limitach malloc = `(nowy_max+1) × stride` — czysta arytmetyka, patrzenie z runtime.

## 2) Skąd GUI bierze listę przycisków budowania → **dane mapy + pętle; patchowalne**

- Listy dozwolonych rzeczy są **per-gracz w danych mapy**: `allowhouse`, `allowgood`,
  `forbidgood <gracz> <ids>` w `[allowedthings]` (`player.inc`/`mission.inc`),
  parsowane przez **parser skryptów NC2Logic @ `0x413E7B`**.
- Ten parser buduje słownik ID→wartość (prod „allowhouse/allowgood/allowjob/forbid*…")
  i zawiera ~22 wspólne walidacje `cmp …; jae 0x414ABA` (id poza zakresem → błąd). To one
  odrzucają nowe typy zanim trafią do menu.
- Menu budowy = iteracje po typach domów (np. `0x4A83B4`: pętla `edi 1..55` do tablic
  dozwolonych per gracz, `0x4C1EBE`: budowa listy typów). Są wśród 35 miejsc `cmp ..,0x37`.
- **Wniosek:** menu jest sterowane danymi + pętlami; po podniesieniu limitów i dodaniu wpisów
  nowe typy pojawiają się same. Wymaga podniesienia granic pętli (ten sam zbiór patchy co loadery).

## 3) Ikony surowców w HUD → **w pełni sterowane danymi**

- `Data\engine2d\inis\goods\goodgraphics.cif` (dekod: przez `cif2txt C`):
  ```
  %01%goodgraphics
  %02%logicgood 3
  %02%graphicshumanrandompalette "good_stone"
  ```
  — specyfikacja „o typie surowca → paleta" (osobno w pliku `Data\engine2d\bin\palettes\goods\goods_*.pcx`).
- Klucze `{gfxgood:%d}` / `{gfxhouse:%d,%d}` w exe (`0x4E1EE7`, `0x4F80A0`) = wyszukiwanie
  w rejestrze gfx engine2d (biblioteki `.bmd`, np. `ls_goods.bmd`) **indeksowane typem**.
- Nowy surowiec = linijka w `goodgraphics.cif` + nowy `goods_*.pcx` + nazwa w
  `Data\text\pol\strings\gameobjects\goods.ini`. Zero zmian w exe.

## 4) Edytory → **inny build, mniej limitów, identyczne wzajemnie**

- `Edytor podstawowy.exe` i `Remik's Editor.exe` to **ten sam build** (identyczne bajty `.text`).
- To **nie ten sam build co gra**: w adresach loaderów gry (`0x41542C`, `0x4159F2`, `0x41350F`…) edytory
  mają inny kod; skan: edytory mają tylko **2× cmp ..,0x37 i 0× cmp ..,0x42** (gra: 16/19),
  a limity to głównie `0x64` (100). Edytory są dużo bardziej pojemne.
- Realne miejsca limitu w edytorze: `0x37`(55)×2 @ `0x41DF9C`/`0x41EDF4`, `0x38`(56) @ `0x40A648`,
  `0x41`(65) @ `0x40CADF` + 6× `0x64` — do ewentualnej podniesienia przy dodawaniu przez edytor.

---

## Werdykt

**Wykonalne.** Nie istnieje żaden „twardy" format, który uniemożliwiłby dodanie typów poza limity:
- mapy → nazwy (bez limitów), save'y → mieszczą się (bajt), HUD → dane, menu → dane + pętle,
- edytory → osobne, mało ograniczone buildy (lub patch 4–6 stałych).

Koszt to: **podniesienie stałych `cmp` w pamięci w całym exe** (semantyczne limity: domy 35,
surowce 37, zawody 48, plemiona 20, bronie 43 unikalnych adresów) + **malloki**
(`0x151BC`/`0x35A0` → `nowy_max × stride`) + rozróżnienie od DISPATCH-ów
(`cmp eax,0x7/0x8/0x5` — ~300 miejsc — których NIE wolno ruszać; to switch po typach, nie granice tablic).

Ryzyko nie leży w „czy się da", tylko w **kompletności listy miejsc** — stąd pierwszym zadaniem
Etapu C jest dokładny, wyrównany do granic instrukcji skan `cmp r32,imm` (fix `boundscan.py`).

**Zalecana ścieżka:** (1) wyrównany skan + atrament tabeli patchy; (2) spike DLL+MinHook na
jednym punkcie (malloc domów); (3) test w grze: nowy typ lives through zapis/odczyt.