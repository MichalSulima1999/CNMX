# Plan: narzędzie z GUI do edycji danych CNMX

**Data:** 2026-10-22
**Status:** szkic do zatwierdzenia (nie rozpoczęty)
**Zastępuje:** `modkit.py` (prototyp CLI) — patrz sekcja 6

---

## 1. Po co osobne narzędzie

`modkit.py` powstał jako skrypt pomocniczy (Etap A: `inspect`/`validate`) i sprawdził się jako
**źródło logiki**, ale nie jako produkt. Edycja danych gry przez CLI wymaga znajomości offsetów,
nazw pól i kolejności zapisu — czyli dokładnie tej wiedzy, której modder mieć nie powinien.

Cel: **aplikacja desktopowa**, w której dodanie budynku czy łańcucha produkcji to wypełnienie
formularza z walidacją na żywo, a nie seria komend i ręcznych edycji INI.

---

## 2. Zakres MVP

| # | Funkcja | Kryterium akceptacji |
|---|---|---|
| 1 | **Wczytanie i inwentarz** | Odczyt wszystkich tabel (dobra, budynki, zawody, grafiki, stringi), raport: użyte / wolne / duplikaty / sieroty |
| 2 | **Edycja dobra** | Formularz pól `goodtype` + nazwa PL/EN + ikona (`landscapetype`); walidacja przy każdej zmianie |
| 3 | **Edycja / klonowanie budynku** | Deep copy z relacjami: `logicproduction`, `logicstock`, `logicworker`, `[GfxHouse]`, stringi |
| 4 | **Walidacja krzyżowa** | Wykrywa: brak nazwy, brak grafiki, produkcję dobra bez receptury, duplikat `type`, ID poza limitem |
| 5 | **Bezpieczny zapis** | Backup, `diff` przed zapisem, zachowanie kodowania cp1250 i końców linii, zapis atomowy |

Poza MVP (świadomie): podgląd w runtime, uruchamianie gry, edycja map, modyfikacja binarki.

---

## 3. Model danych (fundament)

Narzędzie nie może być „edytorem INI" — musi rozumieć encje i relacje:

```
Dobro (good) ──produkowane w──> Budynek (house_type) ──wymaga──> Praca (job)
   │                                  │
   ├─ nazwa (strings/goods.ini)       ├─ nazwa (stringstext/houses.ini)
   ├─ ikona (landscapetype)           ├─ grafika ([GfxHouse])
   ├─ receptury (tribetypes)          ├─ logicworker / logicstock / logicproduction
   └─ doświadczenie (jobexp)          └─ str_house_type → grafika
```

Relacje do wymuszenia w UI: każde nowe dobro musi mieć nazwę i ikonę; każdy budynek musi mieć
typ, grafikę i nazwę; produkcja musi wskazywać istniejące dobro i istniejącą pracę.

---

## 4. Ograniczenia techniczne (wynikające z silnika)

1. **Kodowanie cp1250, bez nagłówka `%01%`/`%02%`** — pliki `.ini` to tekst CIF; zapis musi
   zachować kodowanie i EOL bajt w bajt poza zmienionymi liniami.
2. **Duplikaty `type`** — w `goodtypes.ini` są powtórzone bloki (27, 49, 59, 60); wygrywa
   ostatni. Narzędzie musi je pokazać i zaproponować scalenie, a nie dokładać kolejny.
3. **Limity w exe, nie w danych** — budynki `cmp eax,0x37` (`0x41542C`), dobra `cmp eax,0x42`
   (`0x4159F2`). Dodanie ID powyżej limitu wymaga wpisu w `etapa_gen/patches_ext.h`.
4. **Nakładka na nakładkę** — dane są w `Data/...` i w `CN.PLMOD/...`; trzeba wiedzieć, który
   plik jest „live" (dziś: `CN.PLMOD/types/houses.ini`), i nie tworzyć trzeciej kopii prawdy.
5. **Gra musi być zamknięta** przy podmianie DLL/EXE; pliki danych można edytować w trakcie,
   ale zmiany wejdą dopiero po restarcie — UI powinien o tym przypominać.

---

## 5. Architektura (propozycja)

Rozdzielenie **rdzenia** (testowalny, bez UI) od **interfejsu**:

```
cnmx-toolkit/
├─ core/
│  ├─ model.py        encje: Good, HouseType, Job, String, GfxHouse
│  ├─ store.py        odczyt/zapis INI+CIF, wykrywanie kodowania, backup, atomic write
│  ├─ validate.py     reguły krzyżowe (port z modkit.py)
│  ├─ limits.py       logicdefines.inc + limity z exe
│  └─ patches.py      wykrywanie „potrzebny patch" + przewodnik (bez auto-edycji .h)
├─ ui/                widoki (lista + formularz + panel walidacji + diff)
└─ tests/             testy na kopiach danych z repo
```

**Logika do przejęcia z `modkit.py`** (nie przepisywać od zera): `sniff_encoding`,
`_backup_once`, `parse_text`, `load_defines`, `validate`, `clone_*`.

---

## 6. Status `modkit.py`

* **Zostaje w repo** jako historia i źródło logiki → `.ai/scripts/modkit.py`.
* **Nie rozwijamy go** i nie przenosimy do `modkit/` w roocie (planowana zmiana lokalizacji
  została anulowana).
* Dokumentacja `Instrukcja-modkit.md` i `modkit-a.md` ma status **archiwalny**.

---

## 7. Kamienie milowe

| Etap | Zakres | Efekt |
|---|---|---|
| **M0** | decyzje (stack, repo), szkielet, odczyt danych read-only + inwentarz | aplikacja pokazuje tabele, nic nie zapisuje |
| **M1** | edycja dobra + walidacja + zapis z backupem/diff | pierwszy realny użytek |
| **M2** | klonowanie budynku z relacjami | dodanie budynku bez ręcznego INI |
| **M3** | kreator produkcji (dobro → budynek → praca) + graf łańcucha | pełny przepływ |
| **M4** | limity i patche: wykrywanie potrzeby + instrukcja wpisu | świadome przekraczanie limitów |

---

## 8. Decyzje (podjęte 2026-10-22)

| # | Decyzja | Wybór | Uzasadnienie |
|---|---|---|---|
| 1 | **Stack** | **web UI lokalnie** — Python (`http.server`) + HTML/JS w przeglądarce | zero zależności, brak ryzyka wheels dla Pythona 3.15, dobre grafy łańcuchów; rdzeń i tak jest w modelu danych, nie w widżetach. Później opcjonalnie opakowanie w `pywebview`/Electron |
| 2 | **Lokalizacja repo** | **osobne repo `cnmx-toolkit`** (proponowany katalog: `G:\Games\cnmx-toolkit`) | narzędzie ma własne wydania i historię; katalog gry zostaje czysty |
| 3 | **Dystrybucja** | do ustalenia przy M1 (skrypt + `run.bat`, potem opcjonalnie pakiet) | — |
| 4 | **Język UI** | do ustalenia przy M1 (domyślnie PL) | — |
| 5 | **Zakres M0** | odczyt + inwentarz (read-only, bez zapisu) | najpierw dowód, że model danych zgadza się z plikami |

Odrzucone: **PySide6** (wymagałby drugiego interpretera lub czekania na wheels pod 3.15),
**Electron/Tauri** (najcięższy projekt, bez przewagi na tym etapie), **tkinter** (słaby UX
przy dużych tabelach).

**Stan realizacji:** plan zatwierdzony, kod **nie rozpoczęty**.

---

## 9. Ryzyka i obserwacje z danych (do weryfikacji)

1. **`Data/text/pol/strings/gameobjects/goods.ini` jest częściowo uszkodzony kodowaniem.**
   Plik jest UTF-8, ale zawiera **103 wystąpienia znaku U+FFFD** (`EF BF BD`, czyli „utracony
   znak"), a poprawnych polskich diakrytyków jest tylko 2. Przykład: `stringn 66 "Węgiel"`
   jest poprawny, ale większość pozostałych nazw ma w miejscu diakrytyku znak zastępczy.
   **Do ustalenia:** czy silnik czyta nazwy dóbr z tego `.ini`, czy z `goods.cif` — jeśli z
   `.ini`, część nazw w grze może być zniekształcona. Nie ruszać bez testu w grze.
2. **Duplikaty `type` w `goodtypes.ini`** (27, 49, 59, 60) — wygrywa ostatni blok. Narzędzie
   ma to pokazywać i scalać, nie dokładać kolejny.
3. **Dwa źródła prawdy dla budynków:** `Data/logic/houses.ini` i `CN.PLMOD/types/houses.ini`
   (live). Narzędzie musi jawnie wskazywać, który plik edytuje.
4. **Granica dóbr `0x42 → 0x43`** jest zrobiona punktowo (pętle UI, bramki). Kolejne dobra
   (68+) będą wymagały nowych wpisów — to nie jest „raz na zawsze".

