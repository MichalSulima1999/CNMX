# Jak dodać nowy budynek lub surowiec krok po kroku

Zakres: `modkit.py` (Etap A–E). Katalog roboczy: `G:\Games\CnMod 1.2`

## 1) Dostępne komendy

```bash
python .ai\scripts\modkit.py --help
```

Kluczowe:
- template-house --id N [--name NAZWA] – wygeneruj szablon nowego budynku
- template-good --id N [--name NAZWA] – wygeneruj szablon nowego surowca
- good-export --id N – wyeksportuj istniejący [goodtype]
- good-import --file <plik.ini> – zaimportuj wyeksportowany surowiec
- clone-house --from A --to B – sklonuj istniejący budynek
- clone-good --from A --to B – sklonuj istniejący surowiec
- inspect, validate, limits – weryfikacja
2) Dodanie nowego surowca
Krok 1: Wygeneruj szablon
python .ai\scripts\modkit.py inspect
python .ai\scripts\modkit.py template-good --id 70 --name stal
Krok 2: Uzupełnij wygenerowane pola
- CN.PLMOD\types\goodtypes.ini – sekcja [goodtype] type 70
- CN.PLMOD\stringstext\gameobjects\goods_pol.ini – stringn 70 "Stal"
Krok 3: Zweryfikuj
python .ai\scripts\modkit.py validate
python .ai\scripts\modkit.py inspect
3) Dodanie nowego budynku
Uwaga: Nowe ID budynków > 54 działają wyłącznie przy uruchomieniu gry przez etapc\launcher.exe (runtime overlay Etap C). Bez launchera oryginalne CN.PLMOD.exe nie wczyta tych wpisów.
Krok 1: Wygeneruj szablon
python .ai\scripts\modkit.py limits
python .ai\scripts\modkit.py template-house --id 60 --name kuźnia
Krok 2: Uzupełnij wygenerowane pola
- CN.PLMOD\types\houses.ini – sekcja [logichousetype] logictype 60
- CN.PLMOD\budynki12\houses\houses.ini – sekcja [GfxHouse] (minimum: model, LogicMaximumSize, EditGroups)
- CN.PLMOD\stringstext\gameobjects\houses.ini – stringn 60 "Kuźnia"
Krok 3: Przetestuj w grze
etapc\launcher.exe
4) Export/Import surowca
python .ai\scripts\modkit.py good-export --id 1
python .ai\scripts\modkit.py good-import --file export_good_1.ini
good-import automatycznie tworzy backupy .orig.
5) Minimalny happy path
python .ai\scripts\modkit.py inspect
python .ai\scripts\modkit.py template-good --id 70 --name stal
python .ai\scripts\modkit.py template-house --id 60 --name kuźnia
# uzupełnij brakujące pola w wygenerowanych plikach
python .ai\scripts\modkit.py validate
etapc\launcher.exe