# HANDOFF 2026-10-31 — STACKOWANIE WĘGLA (przyczyna: zdublowana nazwa obiektu krajobrazu)

## 1. Objaw
Po poprawnym wdrożeniu własnej grafiki węgla
([`HANDOFF-2026-10-30-WLASNA-GRAFIKA-WEGLA.md`](HANDOFF-2026-10-30-WLASNA-GRAFIKA-WEGLA.md))
został jeden błąd:

- pierwszy węgiel położony na ziemi → **czarna** sterta, podniesienie zwraca węgiel,
- dołożenie **drugiego** węgla na tę samą stertę → sterta zamieniała się w **żelazo**
  (2 węgiel = „2 żelaza", również po podniesieniu).

Próby naprawy przez dopisanie przejść `transition 4 88 1 +1 0`,
`transition 4 88 0 +1 0`, `transition 3 88 1 -1 66` w `landscapetypes.cif`
**nie działały** i dodatkowo zaśmieciły dane (patrz §3).

## 2. Prawdziwa przyczyna — zdublowana nazwa w `landscapes.cif`
W `landscapes.cif` istniały **dwa** obiekty o nazwie `coal pile 01`:

| linia (txt) | obiekt | `LogicType` | paleta | klatki |
|---|---|---|---|---|
| 3174 | `coal pile 01` (stary, pozostałość CnMod 1.2) | **19** (`iron_ore`) | `goods_iron` | 20–24 |
| 21625 | `coal pile 01` (nasz nowy) | **88** (`coal`) | `goods_coal` | 15–19 |

`GfxTransition 3/4 "coal pile 01"` w naszym obiekcie jest rozwiązywane **po nazwie**,
a nie po `LogicType`. Silnik brał **pierwszy** obiekt o tej nazwie — czyli starą sierotę
z grafiką i logiką żelaza (typ 19).

Dlatego:
- **pierwszy** węgiel był poprawny — obiekt powstawał bezpośrednio z `landscapetype 88`,
- **drugi** węgiel uruchamiał przejście graficzne `GfxTransition 4` i przełączał stertę
  na obiekt o `LogicType 19` → wygląd żelaza i podnoszenie żelaza.

Dodatkowy dowód: **żadne dobro nie używa już `landscapetype 19`** — po przełączeniu węgla
na typ 88 stary obiekt `coal pile 01` (`LogicType 19`) został całkowicie osierocony.
Wcześniej to on odpowiadał za „węgiel wygląda jak żelazo" przy `landscapetype 19`.

## 3. Co naprawiono

### 3.1 `landscapes.cif` — unikalne nazwy (właściwa naprawa)
Sierocie (`LogicType 19`) zmieniono nazwę `coal pile 01` → **`iron ore pile 01`**
(razem z jej dwoma wpisami `GfxTransition 3/4`).

Teraz nazwa `coal pile 01` występuje **wyłącznie** w obiekcie typu 88, więc przejście
graficzne wskazuje na siebie i sterta pozostaje węglem.

### 3.2 `landscapetypes.cif` — usunięte niepoprawne przejścia
Usunięto 6 linii `transition`:

- 3 dopisane przez pomyłkę do **poprzedniego** typu (`chest_magical`, koniec bloku),
- 3 z wnętrza bloku typu 88.

Powód: we **wszystkich** oryginalnych stertach trzecia liczba przejścia to **stała `2`**
(`transition 3 <typ> 2 -1 <good>` / `transition 4 <typ> 2 +1 0`) — **nie walencja**.
Wartości `1` i `0` w tym miejscu są niepoprawne. Typ 88 ma teraz dokładnie:

```
%02%transition 3 88 2 -1 66
%02%transition 4 88 2 +1 0
```

### 3.3 `cnmod_hook` — usunięty błędny patch pamięci
Przez jakiś czas w `cnmod_hook/src/main.cpp` istniała funkcja
`patch_transition_table_for_coal()`, która pod `entry + 0x78` struktury typu krajobrazu
(`0x568c24`, wpis `0x8C` B) wpisywała 20 bajtów „przejść". Była to **zła droga**:
- format przejść w pamięci nie jest 4-bajtowy (`action, valency, delta, target`),
- zapis trafiał w nieznane pole wpisu typu.

Funkcja, jej wywołania i nieużywana flaga `g_transitionTablePatched` zostały **usunięte**.
Patch pamięci nie jest potrzebny — problem leżał w danych.

## 4. Backupy
- `Data\logic\landscapetypes.cif.bak_coal_stack_20261031_114855`
- `Data\engine2d\inis\landscapes\landscapes.cif.bak_coal_stack_20261031_114855`

Metoda edycji: `mapper tools\cif2txt.exe C` → edycja tekstu → `T` → ponowne `C` i
porównanie bajtowe (roundtrip **identyczny**). Nagłówek CIF
`<CULTURES_CIF_BEGIN><03FD><NNNNNNNN>` zawiera licznik linii `%` i musi być przeliczony
po każdej edycji (nasz skrypt robi to automatycznie; `landscapetypes` 717 → 711).

## 5. Weryfikacja w grze (potwierdzona przez użytkownika)
- 1 węgiel na ziemi → czarna sterta, podniesienie daje węgiel.
- 2., 3., 4. węgiel dołożony na stertę → **nadala czarna**, sterta rośnie (klatki 15→19).
- Podniesienie z pełnej sterty → węgiel, nie żelazo.
- Tooltip i okienko nadal pokazują „Węgiel".

## 6. Wnioski dla przyszłych surowców (dodawanych przez `.ini`/`.cif`)
1. **Nazwy obiektów w `landscapes.cif` muszą być unikalne.** `GfxTransition` wskazuje
   obiekt **po nazwie**, a nie po `LogicType` — duplikat nazwy cicho przełącza obiekt
   na inny typ (i inną fizykę).
2. Każdy nowy `landscapetype` potrzebuje **dokładnie** dwóch przejść w formacie
   `transition 3 <typ> 2 -1 <good>` i `transition 4 <typ> 2 +1 0`; trzecia liczba to
   stała `2`.
3. Nowy obiekt musi mieć własny, unikalny `EditName` + `GfxTransition` na tę samą nazwę.
4. Przed dodaniem obiektu warto sprawdzić, czy w `landscapes.cif` nie istnieje już
   obiekt o tej nazwie (np. pozostałość po starym mapowaniu `landscapetype`).
