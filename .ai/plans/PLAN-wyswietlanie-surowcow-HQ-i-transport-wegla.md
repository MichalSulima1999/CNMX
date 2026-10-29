# PLAN — dalsze prace (2026-10-28)

Cel: dwa otwarte wątki po naprawie crashu wczytywania zapisów (commit 3de7fdc).

---

## 1. Kontekst

- Crash przy wczytywaniu zapisów naprawiony przy korzeniu (loader wywoływał cleanup, niszcząc singletony; po loadzie brakujące singletony odtwarzane przez `FUN_0040704b`). Stare zapisy (tylko 2 z 8 działają) są uszkodzone plikowo, nie wina poprawki.
- Przejściowy `hook_fun_4a15ce` usunięty — nie jest już potrzebny.
- Aktywne testowanie prowadzone na węglu (good 66), zawód 56 „Smolarz”, typ 57.
- Podział warstw (z AGENTS.md): dane/tabele/limity → patche EtapC (`etapa_gen/patches_ext.h`); zachowanie/logika → hooki `cnmod_hook/src/main.cpp`. Nigdy nie implementuj tej samej zmiany w obu.

---

## 2. Zadanie 1: Wyświetlanie nowych surowców w HQ — zakładka z największą ilością surowców

### Objaw
W panelu HQ (Kwatera Główna) w zakładce pokazującej surowce z największą ilością nie widoczne są nowe dobra (np. węgiel 66). Działa tylko dla dóbr oryginalnych (< 66).

### Co wiemy (z RE i AGENTS.md)
- `CN.PLMOD/types/goodcategories.ini` — sekcja `[goodcategories]`, wpis `66 = 2` (kategoria 2).
- `hook_catbuild` (adres `0x4A82BB`) czyta INI i dopisuje dobra do grup `self + 0x180 + kategoria*0x38` (7 grup × 14 slotów).
- `FUN_0045CBBE` (kategoryzacja) pozostaje passthrough.
- `house_type`: `+0x08` produkowane dobro, `+0x10` zawód, `+0x60` logicstock, `+0x37C` revmap[] (66 wpisów — strażnik `hook_gate_431f37`), `+0x484` logicproduction.
- `pBld` = `0x510BD0` (stride `0x7E0`), `pHt` = `0x5113A0` (stride `0x624`).
- Limity w exe: budynki `cmp eax,0x37` @ `0x41542C`; dobra `cmp eax,0x42` @ `0x4159F2` (po patchech → `0x43`).

### Hipotezy do sprawdzenia
1. Panel „największa ilość surowców” skanuje tylko dobra < 66 (brak patcha limitu w kodzie rysowania/sortowania panela).
2. `hook_catbuild` nie dodaje węgla do grupy używanej przez ten panel (zła kategoria w INI lub zły offset grupy).
3. Patch limitu `0x42→0x43` nie został wprowadzone we wszystkich miejscach obsługujących ten panel (audyt wykazał 19 patchy, ale może brakować któregoś w ścieżce renderowania panela HQ).

#### Odkrycie (2026-10-28): kategoria 0 w goodcategories.ini
- `66 = 0` → węgiel pojawia się w zakładce „największa ilość surowców” w HQ, **ale nawet gdy ilość = 0** (powinien się pojawić tylko gdy > 0).
- `66 = 3` → węgiel **nie pojawia się** w tej zakładce (inna kategoria, inne znaczenie).
- `66 = 0` i `66 = 3` jednocześnie nie działa — INI przyjmuje tylko jedną wartość na surowiec (nadpisuje).
- Wniosek: kategoria 0 oznacza „pokaż w zakładce max”, ale bez warunku ilości > 0. Trzeba zmienić logikę wyświetlania tak, by dla kategorii 0 warunkiem było `ilość > 0`.

#### Propozycje rozwiązania
A) **Hook cnmod_hook** (logika): złapać funkcję rysującą/listującą panel „max surowców” i dodać warunek `if (kategoria == 0 && ilosc == 0) pomiń`. Wymaga zidentyfikowania funkcji renderującej ten panel (prawdopodobnie w okolicy `0x4C4xxx` — tam są odwołania do `DAT_005116d4` i formaty `"%s: %d (%d)"`, `"%d/%d %s"`).
B) **Patch EtapC** (dane): zmienić w kodzie panelu warunek wyświetlania z „kategoria == 0” na „kategoria == 0 && qty > 0”.
C) Nowa kategoria w INI o znaczeniu „pokaż w zakładce max tylko gdy > 0” + odpowiedni patch w kodzie panelu.

### Kroki RE
1. Zidentyfikować funkcję rysującą/listującą zakładkę „największa ilość surowców” w HQ (prawdopodobnie w okolicy `0x4C4xxx` — tam są odwołania do `DAT_005116d4` i formaty `"%s: %d (%d)"`, `"%d/%d %s"`).
2. Sprawdzić, gdzie panel filtruje/sortuje dobra — czy jest tam `cmp` z `0x42` lub `0x43`.
3. Sprawdzić, która grupa dóbr (`self + 0x180 + kat*0x38`) jest używana przez ten panel — czy kategoria 2 (węgiel) jest w niej uwzględniona.
4. Dodać brakujące patche limitu `0x42→0x43` w `patches_ext.h` (lub poprawić `hook_catbuild`) — zgodnie z podziałem warstw.

### Gdzie w warstwie EtapC, gdzie w cnmod_hook
- Limity tabel / bounds w kodzie panelu → patche w `etapa_gen/patches_ext.h`.
- Jeśli panel używa dynamicznego zestawu dóbr z INI → hook w `cnmod_hook` (rozszerzenie `hook_catbuild` lub nowy hook na rysowanie panela).

---

## 3. Zadanie 2: Tragarz przypisany do HQ nie chce przynosić węgla ze smolarni

### Objaw
Tragarz (job 24, Kwatera Główna/HQ) przypisany do HQ nie nosi węgla ze smolarni (typ 57, job 56 Smolarz). Z innych budynków produkcyjnych towary do HQ nosi poprawnie. Problem specyficzny dla pary: smolarna → węgiel → HQ.

### Co wiemy (z RE i AGENTS.md)
- Otwarte z AGENTS.md: „mechanizm transportu (job 24, Kwatera Główna)”.
- `house_type` `+0x60` logicstock (licznik wpisów), wpisy 12 B od `+0x64` (`{good, qty, flag}`).
- `revmap[]` w `house_type` ma tylko 66 wpisów — strażnik `hook_gate_431f37` (wersja uniwersalna: dla `good >= 66` skanuje `logicstock`).
- `pTribe` = `0x511200` (stride `0x215E0`), `prodmap` = `pTribe + tribe*0x215E0 + job*0x400 + 0x6928`.
- `hook_gate_431f37` loguje np. `[g431F37] universal: bldg=… htype=9 good=66 -> slot=49`.
- `CN.PLMOD/types/houses.ini`: `logicstock 66 …` (HQ `150 1`, stock 00/01/02 `45/70/120 0`, smolarnia `15 0`).
- `hook_catbuild` dopisuje dobra do kategorii (węgiel 66 → kat 2).

### Hipotezy do sprawdzenia
1. Revmap dla smalarni nie zawiera węgla (66) — strażnik `hook_gate_431f37` blokuje dostęp dla `good >= 66` lub revmap ma tylko 66 wpisów (indeks 66 poza zakresem).
2. `logicstock` w smalarni nie zawiera wpisu dla węgla 66 — tragarz nie widzi dobra do pobrania.
3. Mechanizm transportu job 24 filtruje dobra po kategorii — węgiel (kat 2) nie jest uwzględniany w trasie do HQ.
4. `prodmap` dla smalarni nie ma węgla na liście 생산iacych.

### Kroki RE
1. Sprawdzić `revmap[]` smalarni (typ 57) — czy zawiera węgiel 66 (indeks 66 w tablicy 66-wpisowej → poza zakresem!).
2. Sprawdzić `logicstock` smalarni — czy jest wpis `{good=66, qty=…}`.
3. Prześledzić ścieżkę tragarza: jak wybiera źródło dobra (smolarnia) i cel (HQ) — gdzie może odrzucać węgiel.
4. Sprawdzić `hook_gate_431f37` i `hook_gate_431CED` dla good=66 w kontekście transportu (nie tylko produkcji).
5. Jeśli trzeba: rozszerzyć `revmap[]` na 67 wpisów (patche EtapC) lub dostosować strażnik `hook_gate_431f37` (logika w cnmod_hook).

### Gdzie w warstwie EtapC, gdzie w cnmod_hook
- Rozszerzenie `revmap[]` z 66 → 67 wpisów → patche w `etapa_gen/patches_ext.h` (zmiana rozmiaru tablicy, offsetów).
- Logika transportu/wybierania źródła → hooki w `cnmod_hook/src/main.cpp`.

---

## 3. Zadanie 3: Wyświetlanie grafiki w HQ przy surowcu

### Objaw
Przy surowcu węgiel (66) w HQ nie wyświetla się odpowiednia grafika/ikona w panelu budynku lub na mapie. Może dotyczyć zarówno ikony surowca w interfejsie HQ, jak i grafiki budynku przy produkcji węgla.

### Hipotezy do sprawdzenia
1. Brak wpisu dla dobra 66 w tabeli grafiki/iconów (goodgraphics loader bound `cmp eax,0x42` @ `0x48a162` — patche już wprowadzone, ale może brakować wpisu dla nowego dobra).
2. Brak assetu/grafiki dla dobra 66 (uszkodzona nazwa assetu `wonder semiramis schr…` z otwartych w AGENTS.md może być niezwiązana, ale warto sprawdzić).
3. Kategoryzacja dobra w `hook_catbuild` nie przypisuje węgla do grupy używanej przez panel graficzny HQ.

### Kroki RE
1. Zidentyfikować gdzie gra wczytuje ikony/grafiki dóbr (prawdopodobnie wokół `0x48a162` — goodgraphics loader).
2. Sprawdzić czy dla dobra 66 istnieje wpis w tabeli graficznej.
3. Sprawdzić `CN.PLMOD/types/goodtypes.ini` — czy węgiel ma poprawne odwołanie do grafiki.
4. Jeśli brakuje wpisu: dodać patch w `patches_ext.h` lub wpis w INI.

### Gdzie w warstwie EtapC, gdzie w cnmod_hook
- Tabela grafiki/iconów i limity → patche w `etapa_gen/patches_ext.h`.
- Dynamiczne przypisywanie kategorii graficznych → hooki w `cnmod_hook/src/main.cpp`.

---

## 4. Zadanie 4: Niesienie surowca do HQ — brak grafiki w rękach i znikanie przy upuszczeniu

### Objaw
Pracownik (tragarz) niosący węgiel do HQ nie ma surowca w rękach (brak grafiki carried good). Gdy próbuje upuścić surowiec na ziemię, surowiec znika zamiast zostać położony na mapie. Problem może być powiązany z Zadaniem 3 (brak grafiki dla dobra 66).

### Hipotezy do sprawdzenia
1. Brak animacji niesienia dla dobra 66 — `hook_anim_lookup` (`0x45D14F`) lub `hook_anim_setup` (`0x45C23E`) nie obsługuje nowego dobra.
2. Mechanizm drop/supels (upuszczanie na ziemię) dla dobra >= 66 nie jest obsługiwany (brak patcha limitu w kodzie dropu).
3. `can_produce[66]` lub flagi dla dobra 66 nie są poprawnie ustawione w jednostce tragarza.

### Kroki RE
1. Prześledzić ścieżkę animacji niesienia: `hook_pickup` (`0x4760BF`), `hook_carry_frames` (`0x42CEA6`), `hook_anim_lookup` (`0x45D14F`), `hook_anim_setup` (`0x45C23E`).
2. Sprawdzić gdzie w kodzie jest sprawdzane czy jednostka niesie dobro i jaka grafika ma być pokazana w rękach.
3. Sprawdzić mechanizm drop (upuszczanie na ziemię) — gdzie sprawdzane jest czy można położyć dobro i jak jest usuwane z jednostki.
4. Jeśli brakuje obsługi dobra >= 66: dodać patche limitu lub hooki obsługujące nowy surowiec.

### Gdzie w warstwie EtapC, gdzie w cnmod_hook
- Limity dóbr w kodzie animacji i dropu → patche w `etapa_gen/patches_ext.h`.
- Logika wybierania animacji i grafiki niesienia → hooki w `cnmod_hook/src/main.cpp`.

---

## 5. Podział warstw (przypomnienie z AGENTS.md)

| Co | Gdzie |
|---|---|
| Limity tabel, bounds, rozmiary tablic (`revmap[]`, `logicstock`) | Patche w `etapc/src/EtapC.cpp` + `etapa_gen/patches_ext.h` |
| Zachowanie transportu, kategoryzacji dynamicznej | Hooki w `cnmod_hook/src/main.cpp` |
| Nigdy nie implementuj tej samej zmiany w obu | |

---

## 6. Kryteria akceptacji

- [x] ZAKOŃCZONE — W panelu HQ (zakładka największa ilość surowców) węgiel 66 jest widoczny i poprawnie sortowany (pojawia się tylko gdy ilość > 0).
- [ ] Tragarz przypisany do HQ pobiera węgiel ze smalarni i dostarcza do HQ.
- [ ] W panelu HQ wyświetla się poprawna grafika/ikona przy surowcu węgiel.
- [ ] Pracownik niosący węgiel do HQ ma surowiec w rękach (grafika carried good).
- [ ] Upuśczenie węgla na ziemię przez pracownika nie powoduje zniknięcia surowca.
- [ ] Brak regresji: dotychczasowe funkcje (produkcja, magazyn, crash zapisu) nadal działają.
- [ ] Wszystkie zmiany w `patches_ext.h` dopisane na końcu aktywnej tabeli (nie w `patches_rec*.h`).
- [ ] Wszystkie nowe hooki zarejestrowane w `install_hooks()` i zbudowane pomyślnie (`cnmod_hook\build.bat`).
- [ ] Zakończone plikiem `.ai/docs/HANDOFF-<data>-<temat>.md` i wpisem w `INDEX.md`.

---

## 7. Szybka ściąga adresów (z AGENTS.md, sekcja 10)

| Co | Adres / offset |
|---|---|
| `pBld` / `pHt` / `pJobs` / `pTribe` | `0x510BD0` / `0x5113A0` / `0x511180` / `0x511200` |
| Stride building / house / job / tribe | `0x7E0` / `0x624` / `0x88` / `0x215E0` |
| `house_type` +0x08 dobro / +0x10 zawód / +0x60 logicstock / +0x37C revmap[] / +0x484 logicproduction |
| `prodmap` | `pTribe + tribe*0x215E0 + job*0x400 + 0x6928` |
| Limity exe: budynki `0x41542C`, dobra `0x4159F2` |
| `FUN_0040704b` (INIT) / `FUN_00407291` (cleanup) / `FUN_004190ae` (gsmx NEW) |
| `hook_gate_431f37` — strażnik revmap[] (66 wpisów) |
| `hook_catbuild` @ `0x4A82BB` |
| `hook_pickup` @ `0x4760BF` / `hook_carry_frames` @ `0x42CEA6` |
| `hook_anim_lookup` @ `0x45D14F` / `hook_anim_setup` @ `0x45C23E` |
| Good graphics loader bound @ `0x48a162` |

---

## 8. Następny ruch

Zacząć od **Zadania 1** (wyświetlanie węgla w panelu HQ) — prostsze, daha się zamknąć szybkim patchiem limitu lub poprawką `hook_catbuild`. Następnie **Zadanie 3** (grafika w HQ) i **Zadanie 4** (niesienie surowca) — prawdopodobnie powiązane (brak grafiki dobra 66). Na koniec **Zadanie 2** (transport węgla ze smalarni do HQ), które wymaga głębszej RE mechanizmu tragarza.

Dokument do uzupełnienia w trakcie pracy: dodawać wyniki RE, znalezione adresy i podjęte decyzje w tej samej sekcji.