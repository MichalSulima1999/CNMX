# RE — Hipoteza: zmiana logictype smalarni (Etap 3)

## Problem
`FUN_00473461` (tick jednostki/produkcja) obsługuje tylko typy budynków 0x26 (38) i 0x27 (39). Dla smalarni (typ 57 = 0x39) robi wczesny `return` — brak ustawiania `+0x195[66]`, brak timera, brak produkcji.

## Hipoteza
Zmienić `logictype` smalarni z 57 na 38 w `houses.ini`. Output good (66) pochodzi z `logicproduction 66`, nie z logictype, więc smolarnia nadal producirałaby węgiel, ale z logiką typu 38 (która jest obsługiwana przez `FUN_00473461`).

## Co trzeba sprawdzić
1. Jaki dom ma `logictype 38` w `houses.ini`?
2. Czy zmiana logictype smalarni na 38 nie spowoduje kolizji (dwa domy z tym samym logictype)?
3. Czy typ 38 ma `logicmaintype 3` (jak smolarnia)?

## Pliki do sprawdzenia
- `CN.PLMOD\types\houses.ini` — znaleźć dom z logictype 38, sprawdzić logictype smalarni (~linia 931)

## Alternatywa (jeśli hipoteza nie zadziała)
Dodać code cave w `FUN_00473461` dla typu 57: ustawiać `+0x195[66]=1` i wywoływać `FUN_0044a0d9` + `FUN_0044b2fa`.
