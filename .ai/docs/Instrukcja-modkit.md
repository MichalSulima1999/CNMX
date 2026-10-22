Jak dodać nowy budynek lub surowiec krok po kroku
Zakres: modkit.py (Etap A–E). Katalog roboczy: G:\Games\CnMod 1.2
1) Dostępne komendy
python .ai\scripts\modkit.py --help
Kluczowe:
- template-house --id N [--name NAZWA]
- template-good --id N [--name NAZWA]
- good-export --id N
- good-import --file <plik.ini>
- clone-house --from A --to B
- clone-good --from A --to B
- inspect, validate, limits
2) Dodanie nowego surowca
Krok 1: Szablon
python .ai\scripts\modkit.py inspect
python .ai\scripts\modkit.py template-good --id 70 --name stal
Krok 2: Uzupełnij
- CN.PLMOD\types\goodtypes.ini – [goodtype] type 70
- CN.PLMOD\stringstext\gameobjects\goods_pol.ini – stringn 70 "Stal"
Krok 3: Weryfikacja
python .ai\scripts\modkit.py validate
python .ai\scripts\modkit.py inspect
3) Dodanie nowego budynku
Uwaga: ID > 54 działają wyłącznie przy uruchomieniu przez etapc\launcher.exe (Etap C runtime overlay).
Krok 1: Szablon
python .ai\scripts\modkit.py limits
python .ai\scripts\modkit.py template-house --id 60 --name kuźnia
Krok 2: Uzupełnij
- CN.PLMOD\types\houses.ini – [logichousetype] logictype 60
- CN.PLMOD\budynki12\houses\houses.ini – [GfxHouse] (min. model, LogicMaximumSize, EditGroups)
- CN.PLMOD\stringstext\gameobjects\houses.ini – nazwy PL
Krok 3: Test w grze
etapc\launcher.exe
4) Export/Import surowca
python .ai\scripts\modkit.py good-export --id 1
python .ai\scripts\modkit.py good-import --file export_good_1.ini
Import tworzy backupy .orig.
5) Minimalny happy path
python .ai\scripts\modkit.py inspect
python .ai\scripts\modkit.py template-good --id 70 --name stal
python .ai\scripts\modkit.py template-house --id 60 --name kuźnia
# uzupełnij pola
python .ai\scripts\modkit.py validate
etapc\launcher.exe