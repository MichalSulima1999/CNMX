# Jak dodać nowy budynek lub surowiec krok po kroku

Zakres: dane gry (`CN.PLMOD\`, `Data\`) + rejestr CNMX. Katalog roboczy: `G:\Games\CnMod 1.2`

## 0) Twarde limity (przeczytaj PRZED edycją)

| Co | Limit | Dlaczego |
|---|---|---|
| `good` (surowiec) | **≤ 66** | `revmap[]` ma 66 wpisów, `stan[]` jednostki (`unit+0x21C`) też; pętle silnika kończą na `0x42` |
| `type` budynku | ≤ 0x7F z Etapem C | `house_type` jest powiększony, ale tylko przez `etapc\launcher.exe` |
| nazwa obiektu krajobrazu | **unikalna** | `GfxTransition` szuka po nazwie; duplikat psuje stackowanie stert |

Wolne ID w `Data\logic\goodtypes.ini`: **0, 50, 51** (typy 27/49/59/60 mają duplikaty — to znany,
istniejący problem danych, nie dodawaj tam kolejnych).

Dobra > 66 **nie zadziałają** bez relokacji tablic per-jednostka (`unit+0x21C`..`+0x324`), czyli
Etapu C. Nie „łataj" tego przez `0x7F` — przesunie to `+0x36C`/`+0x374` (maszyna stanów jednostki).

## 1) Dostępne komendy (prototyp)

```bash
python .ai\scripts\modkit.py --help
```

Kluczowe:
- `template-house --id N [--name NAZWA]` – wygeneruj szablon nowego budynku
- `template-good --id N [--name NAZWA]` – wygeneruj szablon nowego surowca
- `good-export --id N` – wyeksportuj istniejący `[goodtype]`
- `good-import --file <plik.ini>` – zaimportuj wyeksportowany surowiec
- `clone-house --from A --to B` – sklonuj istniejący budynek
- `clone-good --from A --to B` – sklonuj istniejący surowiec
- `inspect`, `validate`, `limits` – weryfikacja

`modkit.py` jest **zamrożonym prototypem** — nie zakłada obsługi rejestru CNMX (patrz §4).

## 2) Dodanie nowego surowca

Krok 1: Wygeneruj szablon

```bash
python .ai\scripts\modkit.py inspect
python .ai\scripts\modkit.py template-good --id 50 --name stal
```

Krok 2: Uzupełnij wygenerowane pola

- `Data\logic\goodtypes.ini` – blok `[goodtype]` z `type 50`
  (m.in. `landscapetype`, `isProducedInHouseFlag`, `landscapeToStore`, `atomicForHarvesting`)
- `CN.PLMOD\stringstext\gameobjects\goods_pol.ini` – `stringn 50 "Stal"`
- grafika: paleta + `.cif` + nazwa assetu w `GfxGood` (patrz §3)

Krok 3: Zarejestruj dobro w CNMX (bez przebudowy DLL)

Dopisz blok w `CN.PLMOD\types\cnmx_goods.ini`:

```ini
[modded_good]
good            50      ; ID dobra (<= 66)
landscapetype   89      ; typ krajobrazu sterty/zasobu
job             57      ; zawód, który to produkuje
house           58      ; typ budynku produkującego
carry_type      21      ; wolny wpis tabeli renderu niesienia (0x512750)
carry_source    20      ; wpis-zrodlo kopiowany do carry_type (20 = żelazo, sprawdzony)
icon_fallback   3       ; ikona zastępcza, gdy brak własnego gfxgood; -1 = brak
```

Rejestr zastępuje dawne zaszyte w DLL „GOOD_COAL":
- `can_produce[good] = 1` dla każdego wpisu (hook `44A0D9`),
- wpis tabeli renderu niesienia `carry_type ← carry_source` z `+0x10 = good`,
- strażnik `logicstock` (`431F37`) obsługuje wszystkie dobra ≥ 66 uniwersalnie,
- filtry/logi w hookach używają rejestru, nie stałej 66.

Jeśli pliku `cnmx_goods.ini` brakuje, DLL wczytuje jeden wbudowany wpis (węgiel 66) —
zachowanie identyczne jak wcześniej.

Krok 4: Zweryfikuj

```bash
python .ai\scripts\modkit.py validate
python .ai\scripts\modkit.py inspect
python .ai\scripts\ini_normalize.py        # musi pokazać "plikow zmienionych 0"
```

Po uruchomieniu gry w `logs\cnmod_hook.log` muszą być linie:

```
[goods] Wczytano N dobr modowanych z CN.PLMOD\types\cnmx_goods.ini
[goods]   good=50 landscapetype=89 job=57 house=58 carry=21/20 icon_fallback=3
```

## 3) Grafika surowca (ikona + sterta + niesienie)

1. **Ikona w panelach** – dobro potrzebuje zasobu `gfxgood` w `ls_goods.bmd`.
   Gdy go brak, wpisz `icon_fallback = <dobro z ikoną>` (dla węgla: `3` = kamień).
   Ikona dobra rysowana jest z `good_types[g]+0x24` (patch danych `0x0015EB2`).
2. **Nazwa w tooltipie** – `CN.PLMOD\types\landscape_good_map.ini`:
   `landscapetype = good` (dla węgla `88 = 66`).
3. **Sterta na mapie** – obiekt krajobrazu musi mieć **unikalną nazwę** i unikalny
   `GfxTransition`. Zdublowana nazwa (np. dwie „iron ore pile 01") powoduje, że
   podnoszenie dokłada do niewłaściwej sterty — dokładnie ten błąd naprawiono 31.10.2026
   (`.ai/docs/HANDOFF-2026-10-31-WEGIEL-STACKOWANIE.md`).
4. **Niesienie** – `carry_type` musi wskazywać na **wolny** wpis tabeli `0x512750`
   (stride `0x184`, 88 wpisów; używane są m.in. 5–16, 19, 20). `carry_source`
   kopiujemy z wpisu, który w grze działa (20 = żelazo).

## 4) Dodanie nowego budynku

Uwaga: nowe ID budynków > 54 działają wyłącznie przy uruchomieniu gry przez
`etapc\launcher.exe` (runtime overlay Etapu C). Bez launchera oryginalny
`CN.PLMOD.exe` nie wczyta tych wpisów.

Krok 1: Wygeneruj szablon

```bash
python .ai\scripts\modkit.py limits
python .ai\scripts\modkit.py template-house --id 60 --name kuźnia
```

Krok 2: Uzupełnij wygenerowane pola

- `CN.PLMOD\types\houses.ini` – sekcja `[logichousetype]` z `logictype 60`
- `CN.PLMOD\budynki12\houses\houses.ini` – sekcja `[GfxHouse]`
  (minimum: `model`, `LogicMaximumSize`, `EditGroups`)
- `CN.PLMOD\stringstext\gameobjects\houses.ini` – `stringn 60 "Kuźnia"`

Krok 3: Jeśli budynek produkuje dobro modowane — wpisz jego `logictype`
jako `house` w bloku `[modded_good]` w `cnmx_goods.ini`.

Krok 4: Przetestuj w grze

```bash
etapc\launcher.exe
```

## 5) Export/Import surowca

```bash
python .ai\scripts\modkit.py good-export --id 1
python .ai\scripts\modkit.py good-import --file export_good_1.ini
```

`good-import` automatycznie tworzy backupy `.orig`.

## 6) Minimalny happy path

```bash
python .ai\scripts\modkit.py inspect
python .ai\scripts\modkit.py template-good --id 50 --name stal     # <= 66!
python .ai\scripts\modkit.py template-house --id 60 --name kuźnia
# uzupełnij brakujące pola w wygenerowanych plikach
# dopisz [modded_good] w CN.PLMOD\types\cnmx_goods.ini
python .ai\scripts\modkit.py validate
python .ai\scripts\ini_normalize.py
etapc\launcher.exe
```
