# Decyzja: nazwa i zakres projektu — „CnMod Extended" (CNMX)

**Data:** 2026-10-22
**Status:** przyjęta (obowiązuje)
**Dotyczy:** nazewnictwa projektu, README, wersjonowania i sposobu opisywania zakresu prac

---

## 1. Kontekst

Prace zaczęły się od węgla drzewnego, ale okazało się, że to nie jest istota projektu.
Realny cel: **rozszerzyć silnik** *Ósmego Cudu Świata* (seria Cultures) tak, aby dało się
**dodawać** nowe budynki, zawody i łańcuchy produkcji, a nie tylko podmieniać istniejące
wpisy — plus **narzędzia**, które pozwolą robić to bez ręcznej edycji binarnego pliku.

Stan wyjściowy (potwierdzony w `.ai/plans/plan-5-narzedzia-moderskie.md`):

* budynki: 54/54 sloty zajęte, 55. wpis w `houses.ini` nie jest wczytywany,
* dobra: 65/65 (limit `0x42` w exe),
* zawody: dispatcher obsługuje 1–46, tabela ma 55,
* wolne sloty są tylko w tabeli broni (13, 14).

Dlatego projekt nie jest „modem dodającym treść", tylko **warstwą rozszerzającą silnik
i warsztatem narzędziowym**. Węgiel/smolarz to pierwszy pełny przypadek użycia (proof of concept).

---

## 2. Decyzja

| Element | Wartość |
|---|---|
| Nazwa | **CnMod Extended** |
| Skrót | **CNMX** |
| Identyfikator repo / katalogu | `cnmod-extended` |
| Wersjonowanie | `CNMX 0.1`, `0.2`, … — **własne**, niezależne od wersji CnModa |
| Kompatybilność | `wymaga CnMod 1.2` (Culturesnation Mod) |
| Nazwa wyświetlana w dokumentacji | `CnMod Extended (CNMX)` |

Uzasadnienie: „Extended" w moddingu znaczy „rozszerzenie istniejącego moda", a nie „nowy mod".
Skrót `CNMX` jest krótki, unikalny i wygodny w nazwach plików oraz logów. Nazwa jawnie
odwołuje się do CnModa, więc pochodzenie jest oczywiste, ale numeracja 0.x jasno mówi,
że **nie udajemy CnMod 1.3**.

---

## 3. Odrzucone alternatywy

| Nazwa | Dlaczego nie |
|---|---|
| **Kuźnia CnModa** (`cnmod-kuznia`) | Najlepszy klimat (rzemiosło, warsztat), ale metafora nie mówi nic o *silniku*; wybrano czytelność nad klimat. |
| **Cech CnModa** (`cnmod-cech`) | Semantycznie najcelniejsza (cech przyjmuje nowe zawody), ale „Cech" brzmi jak skrót i gorzej działa w tytule. |
| **CnMod Engine Kit** (`CNEK`) | Precyzyjna, ale zero klimatu i „kit" sugeruje tylko narzędzia, nie warstwę runtime. |
| Użycie podtytułów serii (`Saga`, `Northland`, `Asgard`) | Koliduje z tytułami gier z serii Cultures — myli użytkownika. |

---

## 4. Konsekwencje

**Zmienia się:**

* tytuł i framing `README.md` (cel = silnik + narzędzia, nie „mod o węglu"),
* wersjonowanie w dokumentacji: `CNMX 0.1`, z tabelą kompatybilności,
* sposób opisywania nowych prac: „warstwa 1 (EtapC) / warstwa 2 (hooki) / warstwa 3 (ModKit)".

**Nie zmienia się (świadomie):**

* **katalog roboczy** `G:\Games\CnMod 1.2` — ścieżki danych i skryptów buildowania,
* **nazwy DLL** `EtapC.dll` i `cnmod_hook.dll` — są wpisane w `modlauncher.exe`;
  zmiana wymagałaby rekompilacji launchera i aktualizacji wszystkich buildów,
* **nazwy logów** `logs\etapc.log`, `logs\cnmod_hook.log` — analiza historii i skryptów,
* **nazwa narzędzia** `modkit.py` (ModKit) — już udokumentowana w `Instrukcja-modkit.md`.

---

## 5. Zasada stabilności

Nazwa jest **zamknięta**. Zmiana wymaga nowej decyzji w tym katalogu
(`.ai/docs/DECYZJA-<data>-*.md`) oraz świadomej aktualizacji README i INDEX.
Nie zmieniamy nazwy „przy okazji" innej pracy.
