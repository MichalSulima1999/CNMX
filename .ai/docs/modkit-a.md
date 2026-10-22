# modkit — Etap A (inspect / validate)

Narzędzie: `.ai\scripts\modkit.py` (tylko standardowa biblioteka Pythona 3).

## Uruchomienie

```bat
cd G:\Games\CnMod 1.2
python .ai\scripts\modkit.py inspect
python .ai\scripts\modkit.py validate
python .ai\scripts\modkit.py limits
python .ai\scripts\modkit.py decode <plik.cif> [--out plik.txt]
```

Root gry wykrywany automatycznie (dwie poziomy w górę od skryptu), można nadpisać
przez `--root`, a `cif2txt.exe` przez `--cif2txt`. Przy `validate` kod wyjścia
= liczba błędów (0 = czysto); `inspect`/`limits`/`decode` zwracają 0.

## Co robi `inspect`

Dla każdej tabeli (houses, goods, weapons, vehicles, jobs, armor, tribes,
landscapes) wypisuje użyte/wolne/odsiane indeksy względem limitów z
`logicdefines.inc` + weryfikację disasemblacji exe (zakres akceptowany = `1..MAX-1`,
slot 0 = „none").

Wynik bazowy:

| tabela     | użyte                    | wolne        | odsiane |
|------------|--------------------------|--------------|---------|
| houses     | 1-54 (54/54)             | — (brak!)    | **55**  |
| goods      | 1-65 (65/65)             | — (brak!)    | —       |
| weapons    | 1-12, 15-21 (19/21)      | **13-14**    | —       |
| vehicles   | 1-6 (6/6)                | — (brak!)    | —       |
| jobs       | 1-55 (55/55)             | — (brak!)    | —       |
| armor      | 1-4 (4/4)                | — (brak!)    | —       |
| tribes     | 1-41 (41/41)             | — (brak!)    | —       |
| landscapes | 1-87 (87/87)             | — (brak!)    | —       |

Wniosek: jedyne wolne sloty w grze to **bronie 13 i 14**; pozostałe tabele pełne.

## Co sprawdza `validate`

1. **H-DEAD** — `logictype` poza `1..54` → wpis odsiewany przez exe (test akceptacyjny:
   `logictype 55` = „work murek" daje błąd).
2. **H-DUP / GOODS-… / WPN-…** — duplikaty i zakresy w każdej tabeli.
3. **Refs z `houses.ini`** — `logicworker` → zawód, `logicstock`/`logicproduction` → surowiec,
   `logicvehicletype` → pojazd, `logicmaintype` → 1..7.
4. **`[GfxHouse]`** — `LogicType <0> <id>` (drugi token!), osierocona grafika (GFX-ORPHAN),
   typy bez grafiki (H-NOGFX), `LogicConstructionGoods` (od tokenu 1), `gfxoverlaylandscape`.
5. **Nazwy** (stringstext/gameobjects) — `stringn` dla każdego użytego typu; info dla nazw
   nieużywanych przez logikę.
6. **Broń** — `tribetype` 1..41, `type` 1..21, unikalność par `(tribetype, type)`,
   `goodtype`/`jobtype` → istniejące obiekty.
7. **Surowce** — `landscapetype` / `landscapeToHarvest/Pickup/Store` → zakres 1..87 i definicja.

## Wynik bazowy

```
1 błąd  : H-DEAD logictype 55 poza 1..54 (martwy wpis "work murek")
12 WSW-ów: H-NOGFX dla typów 8, 9, 15, 19, 21, 24, 25, 26, 30, 32, 36, 41
           (np. "work bakery 01", "stock 01") — brak [GfxHouse] w aktywnym pliku;
           wykluczono inny plik w Data\ pokrywający te typy.
```

12 typów bez grafiki to albo zamierzone „typy-logika" (niewidzialne konstrukcje,
pozostałości oryginału: `work *` / `stock *`), albo śmieci do sprzątnięcia — do
rozstrzygnięcia przy okazji Etapu B.

## Struktury plików (potwierdzone przy okazji)

- `[GfxHouse] LogicType <0> <id_budynku>` — id w drugim tokenie; pierwszy zawsze 0.
- `[GfxHouse] LogicTribeType` ∈ {1,2,3,4,7} = warstwa grafiki (nie id plemienia!).
- `LogicConstructionGoods <wariant0..4> <good> …` — surowce od tokenu 1.
- `gfxoverlaylandscape 0` = brak overlay (dozwolone).
- `.cif` dekodowane do `.ai\.modkit_cache\` przez `mapper tools\cif2txt.exe C plik.cif wyjście.txt`.