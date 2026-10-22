# RE — System UI w CN.PLMOD.exe

Uzupełnienie do dokumentacji RE. UI jest renderowane przez funkcje z dekompilacji Ghidry.

---

## 1. Funkcje renderujące UI

| Adres VA | Nazwa | Role |
|----------|-------|------|
| 0x4E21B7 | FUN_004E21B7 | **Renderer tekstu z tagami** — obsługuje `{newline}`, tab, spację, enter. Nie jest dispatcherem jobów (błąd w starszej dokumentacji). |
| 0x46D53A | FUN_0046D53A | Interakcja z budynkiem / panel rzemieślnika (potter handler). Stany +0xACC, +0xA68. |
| 0x46E1BE | FUN_0046E1BE | Sprawdzenie dostępności budynku do interakcji (zasięg, właściciel, flaga +0xB51). |
| 0x4A7297 | FUN_004A693B | Renderer panelu informacji budynku (nazwa, koszt, stan, zapasy towarów, przychody). |
| 0x4C23D8 | FUN_004C227C | Renderer listy budynków/typów UI (iteruje po building_instances, goodi produkcji). |
| 0x44B2FA | FUN_0044B2FA | Ustawia status produkcji +0x21C dla goodów joba (UI). |
| 0x44B5E7 | FUN_0044B5E7 | Ustawia status gooda (0, 0xB, 0xC, 0xD, 0xE) (UI). |
| 0x43E8A7 | FUN_0043E8A7 | UI: wybór gooda do produkcji (+0x218, +0x1C, +0x38C). Nie wykonuje produkcji. |

---

## 2. FUN_004E21B7 — Renderer tekstu (szczegóły)

Wejście: tekst źródłowy z tagami formatowania. Obsługa:
- `0x09` (tab) → przesunięcie o szerokość znaku z `FUN_00439633(ctx, 0x69)`
- `0x0A` / `0x0D` (newline) → nowa linia, `pos += line_height`, `cursor_x = x`
- `0x20` (spacja) → pominięte
- `0x7B '{'` → tag, np. `{newline}` przez `FUN_004E6760`
- Inne drukowalne → render słowa przez `FUN_0040ECF9`, z zawijaniem gdy `max_width <= word_w + cursor_x`

Używane w FUN_0046D53A i FUN_004C227C do opisów budynków/towarów.

---

## 3. FUN_0046D53A — Interakcja z budynkiem

Stan maszyny stanów (+0xACC, +0xA68):
- **+0xACC == 0**: inicjalizacja, sprawdzenie zapasów i kosztów
- **+0xACC == 2**: anulowanie interakcji
- **+0xACC == 4**: potwierdzenie pobrania towaru (state 6)

Przy stanie +0xA68 == 6 i good 66:
```
licznik = DAT_00510BC4 + 0x4A30 + (x * 0x12A0 + building + 0xC) * 4
*licznik += 1
```

BUG: `tribe_house + 8` (output good ID) nigdy nie jest ustawiane dla smalarza (pozostaje 0). Fix: patch logicproduction (RVA 0x15843) zapisuje good do `global_house + 8`, kopiowane do `tribe_house + 8` przy budowie.

---

## 4. FUN_004A7297 — Panel informacji budynku

Renderuje sekcje panelu (`local_1c` 0-10):
- 0: nazwa budynku + pasek postępu
- 1: koszt budowy / utrzymania
- 2: produkcja (lista goodów z `gfxgood_d_1__s_d__d__d`)
- 3: statystyki (praca, wydajność)
- 4-6: zakładki zapasów / towary
- 5: lista towarów w zapasie (iteruje `+0x60` count, `+0x64` stocks)
- 6: szczegóły zapasów
- 9: status pracy
- 10: lista zatrudnionych (iteruje przez `FUN_0041CB32` po goodach)

---

## 5. FUN_004C227C — Lista budynków UI

Iteruje po `DAT_00568C0C` (stride 0x8BC). Dla każdego budynku:
1. Pobiera `house_type_idx` z instancji
2. Odczytuje `production_count` (`+0x484`) i `production_list` (`+0x488`) przez `FUN_00432A48`
3. Renderuje wiersz z nazwą, typem, goodami produkcji
4. Dla kategorii 1,3,5 renderuje dodatkowe sekcje zapasów

---

## 6. Problemy UI przy rozszerzeniu ID do 127

| Problem | Lokalizacja | Skutek |
|---------|-------------|--------|
| Storage UI nie pokazuje nowych towarów | pętla 0x415E8E | crash jeśli bound extended (wywołuje 0x47FEF0 z zewnętrzną tablicą) |
| Lokalne tablice stosu overflow | 0x45FAFA (`sub esp,0x2A4`, 66+102 sloty) | UNSAFE do patchowania bound |
| Menu budowania pokazuje "śmieciowe" budynki sloty 42-126 | brak definicji nazw/kosztów | crash przy stawianiu niezdefiniowanego budynku |

**Rozwiązanie:** dodać filtr niezdefiniowanych budynków (Etap 4) oraz walidatory menu.
