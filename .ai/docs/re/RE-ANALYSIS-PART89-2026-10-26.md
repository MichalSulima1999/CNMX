# RE — Analiza partia 89 (PRZEŁOM: grupowanie dóbr w magazynie i kategorie)

Data: 2026-10-26
Cel: znaleźć logikę, która grupuje surowce w magazynie i wyjaśnić, dlaczego
węgiel (dobro 66) nie pojawia się na liście zapasów.

## 1. Wnioski w skrócie

1. **Kategorie dóbr** liczy funkcja `FUN_0045cbbe(good)` → 1..5 („kategoria
   handlowa”). Używa jej okno targu/magazynu `FUN_004c7110`.
2. **Panel budynku (magazynu)** `FUN_004a693b` w zakładkach 5 („zapasy”) i 6
   („szczegóły zapasów”) iteruje **listę `logicstock` danego typu domu**
   (`+0x60` licznik, `+0x64` wpisy po 12 B) i **pomija dobra > 0x37 (55)**.
3. To samo ograniczenie `<= 0x37` ma `FUN_004a76fd` (budowa zawartości
   zakładek 5/6).
4. W binarce filtr to `CMP reg, 0x37` + `JBE`/`JG` — **nie** `0x38`. Dlatego
   wcześniejsze szukanie bajtu `0x38` nic nie dawało.
5. Dane: `logicstock 66 150 0` ma **tylko Kwatera Główna** (`logictype 1`).
   Budynki magazynowe `stock 00/01/02` (`logictype 7/8/9`) **nie miały** wpisu
   dla dobra 66.

## 2. Kategorie dóbr — `FUN_0045cbbe`

```c
undefined4 FUN_0045cbbe(int good) {
  if (0x24 < good && good < 0x2b) return 1;   // 37..42
  if (0x20 < good && good < 0x25) return 2;   // 33..36
  if (good == 0x1f || good == 0x20) return 3; // 31,32
  if (good == 0x1e) return 4;                 // 30
  if (good < 0x2b && 0x37 < good) return 0;   // gałąź martwa (niemożliwa)
  return 5;                                   // wszystko inne, w tym 66
}
```

Dobra 30..55 dzielą się na kategorie 1–5; dobro 66 wpada do kategorii 5.
Patch `0x0005CBF8` (`0x37 -> 0x43`) dotyczy tylko martwej gałęzi i animacji
niesienia — **nie** ma wpływu na listę magazynu.

## 3. Okno targu/magazynu — `FUN_004c7110` (+ `FUN_004c6d91`, `FUN_004c6e27`)

- `FUN_004c6d91` tworzy okno 0x1A4 x 300 z parametrami
  `this+0x70 = kategoria`, `this+0x74 = filtr dobra (-1 = wszystkie)`.
- `FUN_004c7110` rysuje listę: pętla `good = 0x1e .. 0x37`, filtr
  `FUN_0045cbbe(good) == this+0x70`, oraz flaga dostępności
  `*(char*)(good + 0x1e0 + tribe) != 0`.
- `FUN_004c6e27` obsługuje kliknięcia i dobiera ikonę/dźwięk kategorii
  (0x46–0x53).
- **Filtr pętli**: `0x4c742f`, `0x4c74cb`, `0x4c7543` → `CMP ESI/EDI/ESI,0x37`
  + `JBE`. Czyli dobra 56..66 nigdy nie trafiają na listę.

### 3a. Co dokładnie odpowiada za „kategorie dóbr”

Łańcuch jest krótki i domknięty — **trzy** elementy:

| Element | Rola |
|---|---|
| `FUN_0045cbbe(good)` (`0x45cbbe`) | jedyne miejsce w exe, które mapuje numer dobra na numer kategorii (0..5) |
| `FUN_004e1b04(kategoria)` (`0x4e1b04`) | nazwa kategorii z zasobów tekstowych: grupa `5`, id `0xdc..0xe2` (kategoria 0..6; **6 = „wszystkie”**) |
| `FUN_004c7110` (+ `0x4c6d91`, `0x4c6e27`) | okno z zakładkami kategorii: `+0x70` = wybrana kategoria, `+0x74` = filtr pojedynczego dobra |

Mapowanie `FUN_0045cbbe` (stan faktyczny z dekompilacji):

| Zakres dóbr | Kategoria | Uwaga |
|---|---|---|
| 30 | 4 | `0x1e` |
| 31, 32 | 3 | `0x1f`, `0x20` |
| 33..36 | 2 | `0x21..0x24` |
| 37..42 | 1 | `0x25..0x2a` |
| 43..55 | 5 | „pozostałe” |
| 1..29, 56..66 | 5 | wszystko inne, **w tym węgiel 66** |
| (gałąź `good<0x2b && good>0x37`) | 0 | **martwa** — warunki wykluczają się |

Kategoria 0 nie występuje w praktyce (stąd `0` = brak kategorii). Patch
`0x0005CBF8` (`0x37 -> 0x43`) zmienia tylko tę martwą gałąź, więc nie ma
wpływu na przydział dóbr do zakładek.

Okno targu otwiera `FUN_004a192c(kategoria, filtr)`; z UI (zdarzenie `0xbd2`)
wywoływane jest `FUN_004a192c(6, 0xffffffff)`, czyli „wszystkie”. Zakładki
kategorii obsługuje `FUN_004c6e27` (dźwięki `0x46..0x53`, ikony zależne od
kategorii) i tam ustawiany jest `+0x70`.

**Ważne rozróżnienie:** panel budynku/magazynu (`FUN_004a693b`) **nie woła**
`FUN_0045cbbe` — nie ma tam kategorii. Wiersze zakładki „zapasy” idą w kolejności
wpisów `logicstock` z `houses.ini`. Kategorie widoczne w grze pochodzą z okna
targu/wymiany (`FUN_004c7110`), nie z panelu magazynu.

## 4. Panel budynku / magazynu — `FUN_004a693b`

Wywoływany z konstruktora okna budynku `FUN_004a60a2` (razem z `FUN_004a76fd`).

Zakładka 5 (zapasy), uproszczone:

```c
if (*(int*)(house_type + 0x60) != 0) {        // logicstock count
  p = house_type + 0x6c;                       // wpisy 12 B
  do {
    good = *(int*)(p - 8);                     // +0x64
    if (good <= 0x37) {                        // <-- FILTR (CMP EBX,0x37; JG)
      ... FUN_00431a83(house, good, isWarehouse);
      ... FUN_0042f710(good, 1);               // nazwa dobra
      ... FUN_004b8b04(...);                   // widget wiersza
    }
    p += 0xc;
  } while (idx < *(int*)(house_type + 0x60));
}
```

Zakładka 6 (szczegóły zapasów) — identyczna pętla, drugi filtr
`CMP EAX,0x37; JG`.

Wiersze są rysowane sekwencyjnie (brak tablicy indeksowanej numerem dobra),
więc podniesienie granicy jest bezpieczne.

`FUN_004a76fd` (budowa zawartości zakładek) robi to samo dla zakładek 5/6
(`CMP ECX,0x37` i `CMP EAX,0x37`, oba z `JG`).

### Adresy filtrów (imm8 `0x37` → `0x42`)

| VA instrukcji | imm8 (RVA) | Funkcja / zakładka |
|---|---|---|
| `0x4a7331` | `0x000A7333` | `FUN_004a693b` zakładka 5 |
| `0x4a7432` | `0x000A7434` | `FUN_004a693b` zakładka 6 |
| `0x4a7ef5` | `0x000A7EF7` | `FUN_004a76fd` zakładka 5 |
| `0x4a7fb1` | `0x000A7FB3` | `FUN_004a76fd` zakładka 6 |
| `0x4c742f` | `0x000C7431` | `FUN_004c7110` pętla 1 (targ) |
| `0x4c74cb` | `0x000C74CD` | `FUN_004c7110` pętla 2 (targ) |
| `0x4c7543` | `0x000C7545` | `FUN_004c7110` pętla 3 (targ) |

`CMP reg,0x37` + `JBE/JG` znaczy „przepuść dobro `<= 0x37`”. Wartość `0x42`
(66) przepuszcza dobro 66, a odrzuca 67 (tar, poza zakresem walidatora
`< 0x43`).

## 5. Dane — `logicstock` w `houses.ini`

Stan przed zmianą:

| Typ | debugname | logicstock 66 |
|---|---|---|
| 1 | headquarters | **TAK** (`66 150 0`, linia 59) |
| 7 | stock 00 | nie |
| 8 | stock 01 | nie |
| 9 | stock 02 | nie |
| 57 | work charcoal burner | TAK (`66 15 0`) |

Po zmianie dodano:

```
logicstock 66 45 0    ; stock 00
logicstock 66 70 0    ; stock 01
logicstock 66 120 0   ; stock 02
```

Backup: `Data/logic/houses.ini.bak_warehouse_coal_20261026_222831`.
`ini_normalize.py` (dry-run): `plikow zmienionych 0`.

## 6. Parser `logicstock` (`FUN_0041531d`, okolice linii 160–176)

```c
else if (key == "logicstock") {
  if (count != 0x42) {                 // zabezpieczenie przed przepelnieniem
    good = ...; amount = ...; flag = ...;
    if (good < 0x43) {                 // dobro 0..66 — węgiel 66 OK
      entry[count] = { good, min(amount,1000), flag };
      revmap[good] = count;            // +0x37C + good*4
      count++;
    }
  }
}
```

Ważne: `revmap[66]` leży pod `+0x484`, czyli **nakłada się na
`logicproduction`**. Dla Kwatery Głównej i magazynów `logicproduction` nie jest
używane, więc to bezpieczne. Dla chaty smolarza (typ 57) kolejność
`logicproduction 66` → `logicstock 66 15 0` powoduje nadpisanie
`+0x484 = 1`; pilnuje tego strażnik `hook_gate_431f37` w `cnmod_hook`.

## 7. Ograniczenie okna targu (`FUN_004c7110`) — niełatane

Okno targu dodatkowo wymaga flagi `*(char*)(good + 0x1e0 + tribe) != 0`.
Tablica `+0x1e0` jest czyszczona `memset(...,0,0x38)` w `FUN_0044a0d9`
i wypełniana tylko dla dóbr `0x1f..0x37`. Dla dobra 66 flaga leży pod
`+0x222` (poza czyszczonym zakresem, może zawierać śmieci). Dlatego **nie
rozszerzono** pętli targu (`0x4c742f/0x4c74cb/0x4c7543`) — najpierw trzeba by
rozszerzyć tablicę `+0x1e0` i pętle ją wypełniające. To osobny krok.

## 8. Co zmieniono w tej sesji

- `etapa_gen/patches_ext.h`: +4 patche `0x000A7333`, `0x000A7434`,
  `0x000A7EF7`, `0x000A7FB3` (`0x37 -> 0x42`) dla panelu budynku/magazynu.
  Tabela liczy teraz **683** wpisy.
- `Data/logic/houses.ini`: `logicstock 66` dla `stock 00/01/02` (+ backup).
- `EtapC.dll`: przebudowany i skopiowany do roota (gra była zamknięta);
  binarka zawiera nowe opisy patchy (sprawdzone `strings`).

## 9. Jak zweryfikować

1. Uruchom grę przez `modlauncher.exe`.
2. `logs/etapc.log` → `patches applied: 683/683 ok` (było 679).
3. Otwórz panel Kwatery Głównej lub budynku `stock 0x` → zakładka zapasów
   powinna pokazać „Węgiel” (ikona `good_stone` z `goodgraphics.cif`).
4. Postaw chatę smolarza, wyprodukuj węgiel, zanieś do magazynu — pozycja
   „Węgiel” powinna mieć stan > 0.

## 10. Pliki źródłowe analizy

- `.ai/re_out_batch10/functions/0x4a693b.c` — panel budynku (zakładki 5/6)
- `.ai/re_out_batch10/functions/0x4a76fd.c` — zawartość zakładek
- `.ai/re_out_batch10/functions/0x4a60a2.c` — konstruktor okna budynku
- `.ai/re_out_batch10/functions/0x4a192c.c` — otwarcie okna targu (`FUN_004a192c`)
- `.ai/re_out_batch6/functions/0x4c7110.c` — lista targu/magazynu
- `.ai/re_out_batch6/functions/0x4c6d91.c`, `0x4c6e27.c`, `0x4c70cc.c` — okno targu
- `.ai/re_out_batch21/functions/0x45cbbe.c` — kategorie dóbr
- `.ai/re_out_batch13/functions/0x4e1b04.c` — nazwy kategorii (zasoby `0xdc..0xe2`)
- `.ai/re_out_batch19/functions/0x41531d.c` — parser `logicstock`
- `.ai/re_out_batch19/functions/0x415e8a.c` — inicjalizacja palet ikon (0..55)
