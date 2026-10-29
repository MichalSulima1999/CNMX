# RE-ANALIZA — panel HQ „największa ilość surowców” (grupa 0)

**Data:** 2026-10-29
**Cel:** wyjaśnić, dlaczego węgiel (good 66) w panelu HQ jest widoczny przy ilości 0
i nie sortuje się razem z innymi surowcami; wskazać poprawkę.

> **Uwaga:** wcześniejsza wersja tego dokumentu błędnie wskazywała `FUN_004c3ea4`
> (okno celów/handlu) oraz błędnie liczyła limit pętli (400/0x14 = **20**, nie 25).
> Faktyczny panel to siatka kontrolek budowana w `FUN_004a76fd`, a lista dóbr do
> sortowania pochodzi z `FUN_004a847a`. Poniżej jest stan zweryfikowany.

---

## 1. Gdzie jest ten panel

| Element | Funkcja / adres |
|---|---|
| Budowa zawartości okna (7 przycisków kategorii + siatka dóbr) | `FUN_004a76fd` |
| Budowa grup dóbr (this+0x180, 7 × 14 slotów) | `FUN_004a82bb` |
| Lista „największa ilość” (grupa 0), sortowanie malejąco | `FUN_004a847a` |
| Rysowanie kontrolek dobra (ramka, ikona, tooltip) | `FUN_004a85cb` (kontrolka) |
| Ilość dobra w budynku | `FUN_00431a83` |

Struktura okna (fragment):

- `this + 0x180 + kategoria*0x38` — 7 grup po 14 `int` (indeksy dóbr).
- `this + 0x17c` — aktualnie wybrana kategoria (0 = „największa ilość”).
- `this + 0x2d0` — grupa „Różne” (dobra spoza 7 kategorii, 14 slotów).

### 1.1 Siatka w `FUN_004a76fd`

```c
// 7 przycisków kategorii:
for (uVar1 = 0; uVar1 < 7; uVar1++) { ... }
// siatka wybranej kategorii:
for (local_8 = 0; local_8 < 14; local_8++) {
    iVar12 = *(int*)(this + (*(int*)(this+0x17c) * 0xe + local_8) * 4 + 0x180);
    if (iVar12 == 0) break;                 // pierwszy pusty slot kończy siatkę
    FUN_004a85cb(..., iVar12);              // kontrolka: ramka + ikona + ilość + tooltip
}
```

To dokładnie odpowiada opisowi: ramka z ilością, ikona surowca (dla węgla brak
assetu `gfxgood:66`), tooltip z nazwą po najechaniu.

---

## 2. Skąd bierze się grupa 0 (`this+0x180`)

`FUN_004a82bb`:

1. Wpisuje dobra z `logicstock` budynku do grup 1..6 według tabeli kategorii
   (`DAT_004f62e8`, 7 × 14 wpisów).
2. Dobra spoza tabeli (< 0x38) trafiają do grupy „Różne” (`this+0x2d0`).
3. **Nadpisuje grupę 0** wynikiem `FUN_004a847a`.
4. Zeruje pozostałe sloty grupy 0.

`FUN_004a847a` (to jest sedno):

```c
*count = 0;
for (good = 1; good < 0x38; good++) {          // <-- limit 0x38 (55)
    if (good jest w logicstock budynku) {
        qty = FUN_00431a83(budynek, good, ...);
        if (qty != 0.0) {                       // <-- tylko ilość > 0
            lista[*count] = { good, (int)qty };
            (*count)++;
        }
    }
}
// sortowanie malejąco po ilości; remis -> alfabetycznie (FUN_004e23ca)
```

Czyli grupa 0 to **posortowana malejąco lista dóbr z niezerowym stanem**,
ograniczona do 14 pozycji.

---

## 3. Prawdziwa przyczyna błędu

`hook_catbuild` (w `cnmod_hook`) po oryginalnym `FUN_004a82bb` dopisywał każde
dobro z `goodcategories.ini` do grupy `kategoria`:

```c
int base = 0x180 + cat * 0x38;
// znajdź pierwszy slot == 0 i wpisz good
```

Dla `66 = 0` (kategoria 0) węgiel był dopisywany **do grupy 0 już po sortowaniu**,
w pierwszy wolny slot (czyli za ostatnią posortowaną pozycją). Skutki:

- węgiel zawsze na końcu siatki — nigdy nie sortowany,
- widoczny także przy ilości 0 — dopisanie nie sprawdza ilości,
- pozostałe dobra zachowują się poprawnie, bo przechodzą przez `FUN_004a847a`.

Wcześniejsze próby (`hook_0x419587_qty`, patch `add edi,0x19`) dotyczyły innych
funkcji i nie mogły tego naprawić.

---

## 4. Poprawka (wdrożona)

Zgodnie z podziałem warstw:

### 4.1 `cnmod_hook` — logika

`hook_catbuild`: pomijamy kategorię 0 (`if (cat == 0) continue;`). Grupa 0 jest
własnością silnika (`FUN_004a847a`), nie wolno jej dopisywać ręcznie.

### 4.2 `EtapC` — limit/bound

Patch w `etapa_gen/patches_ext.h`:

```c
{ 0x000A8501, 0, 1, { 0x42, ... },
  "PANEL HQ max surowce: FUN_004a847a granica dobr 0x37 -> 0x42 ..." }
```

W binarce: `0x4A84FF: 83 FB 37` (`cmp ebx,0x37; jle`) → imm8 `0x37` → `0x42`.
Pętla skanuje wtedy dobra 1..66, więc węgiel 66 wchodzi do sortowanej listy
**tylko gdy `qty != 0`**, i jest sortowany razem z resztą.

`FUN_00431a83` ma już patch `0x42 -> 0x43` (RVA `0x00031A92`), więc ilość węgla
jest zwracana poprawnie (bez tego zawsze 0.0).

---

## 5. Weryfikacja

1. Zamknąć grę, uruchomić `build_all.bat`, wystartować `modlauncher.exe`.
2. `logs/etapc.log` powinien zawierać:
   `patch ... PANEL HQ max surowce: FUN_004a847a granica dobr 0x37 -> 0x42 ...`
3. W panelu HQ → zakładka „największa ilość surowców”:
   - przy 0 węgla **nie ma**,
   - przy ilości > 0 węgiel jest na właściwej pozycji (sortowanie malejąco).
4. `logs/cnmod_hook.log` nie powinien już mieć wpisów
   `[catbuild] added good 66 to category 0 ...`.

---

## 6. Pliki

- `cnmod_hook/src/main.cpp` — `hook_catbuild`
- `etapa_gen/patches_ext.h` — patch `0x000A8501`
- `.ai/re_out_batch10/functions/0x4a76fd.c` — budowa siatki panelu
- `.ai/re_out_batch10/functions/0x4a82bb.c` — budowa grup kategorii
- `.ai/re_out_batch10/functions/0x4a847a.c` — sortowana lista „największa ilość”
- `.ai/re_out_batch3/functions/0x431a83.c` — ilość dobra w budynku
- `logs/etapc.log`, `logs/cnmod_hook.log`
