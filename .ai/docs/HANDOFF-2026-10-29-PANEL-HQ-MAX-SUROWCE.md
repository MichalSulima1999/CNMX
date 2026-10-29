# HANDOFF — 2026-10-29 — Panel HQ „największa ilość surowców”: węgiel przy 0 i brak sortowania

## 1. Objaw

W panelu HQ (Kwatera Główna), zakładka „największa ilość surowców” (siatka
ramek: ikona + ilość + tooltip z nazwą):

- węgiel (good 66) był widoczny nawet przy ilości **0**,
- nie sortował się z resztą — zawsze na końcu.

## 2. Przyczyna (zweryfikowana w RE)

Panel buduje `FUN_004a76fd`: 7 przycisków kategorii + siatka do 14 dóbr z grupy
`this + 0x180 + kategoria*0x38`. Kategoria 0 to lista „największa ilość”.

- `FUN_004a82bb` buduje grupy 1..6 z `logicstock` i tabeli kategorii, a następnie
  **nadpisuje grupę 0** wynikiem `FUN_004a847a`.
- `FUN_004a847a` zbiera dobra **tylko z ilością != 0**, sortuje malejąco
  (remis: alfabetycznie) i ogranicza do 14 pozycji.
- `hook_catbuild` (cnmod_hook) po oryginalnym `FUN_004a82bb` dopisywał każde
  dobro z `goodcategories.ini` do grupy `kategoria`. Dla `66 = 0` węgiel był
  dopisywany do grupy 0 **po sortowaniu**, w pierwszy wolny slot → zawsze na
  końcu i bez sprawdzania ilości. Stąd objaw.

Wcześniejsze hipotezy (`FUN_004c3ea4`, `hook_0x419587_qty`, patch
`add edi,0x19`) były błędne — dotyczyły innych funkcji.

## 3. Poprawka (wdrożona)

### 3.1 `cnmod_hook/src/main.cpp` — `hook_catbuild`

Dodano `if (cat == 0) continue;` z komentarzem. Grupa 0 należy do silnika
(`FUN_004a847a`), nie wolno jej dopisywać ręcznie.

Dodatkowo `hook_0x419587_qty` przywrócono do czystego pass-through (usunięto
diagnostyczne logowanie `[qtyHook]` i błędne filtrowanie) — nie brał udziału
w rysowaniu tego panelu.

### 3.2 `etapa_gen/patches_ext.h` — nowy patch (limit/bound)

```c
{ 0x000A8501, 0, 1, { 0x42, ... },
  "PANEL HQ max surowce: FUN_004a847a granica dobr 0x37 -> 0x42 ..." }
```

W binarce `0x4A84FF: 83 FB 37` (`cmp ebx,0x37; jle`) — imm8 `0x37` → `0x42`.
Pętla skanuje dobra 1..66; węgiel wchodzi do sortowanej listy tylko przy
`qty != 0`. Ilość węgla zwraca już poprawnie patch `FUN_00431a83`
(`0x00031A92`, `0x42 -> 0x43`).

## 4. Build

```bat
build_all.bat
```

Wynik: `EtapC.dll` 97 280 B, `cnmod_hook.dll` (przebudowany po pass-through).
Gra była zamknięta (sprawdzone `tasklist`).

## 5. Weryfikacja do wykonania w grze

1. Uruchomić `modlauncher.exe`.
2. `logs/etapc.log` — wpis:
   `patch ... PANEL HQ max surowce: FUN_004a847a granica dobr 0x37 -> 0x42 ...`
3. `logs/cnmod_hook.log` — brak `[catbuild] added good 66 to category 0 ...`.
4. Panel HQ → „największa ilość surowców”:
   - przy 0 węgla nie ma,
   - przy ilości > 0 węgiel jest posortowany malejąco razem z innymi.

## 6. Dokumentacja

- Pełna analiza (poprawiona, zastępuje wcześniejszą błędną wersję):
  [`RE-ANALIZA-PANEL-HQ-MAX-SUROWCOW.md`](RE-ANALIZA-PANEL-HQ-MAX-SUROWCOW.md)
- Kluczowe funkcje: `FUN_004a76fd` (siatka), `FUN_004a82bb` (grupy),
  `FUN_004a847a` (sort), `FUN_00431a83` (ilość).

## 7. Sprzątanie

Usunięto tymczasowe pliki diagnostyczne z roota: `hexdump.txt`,
`check_hook_log.py`.
