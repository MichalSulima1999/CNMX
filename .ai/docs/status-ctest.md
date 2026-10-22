# Eksperyment C-test (izolacja regresji idle) — 11.10.2026

## Cel
Odseparować regresję zachowań mieszkańców od pakietu relokacji tablic elementu.
Teoria: zapisy tablic przeniesiono na nowe bazy (0x4A80+), a ~473 niezałatane odczyty
(REVIEW) czytają stare bazy (0x1278/0x1D4C/0x2820/0x3126/0x3C78) = zera -> jednostki
„chodzą w miejscu", nie otwierają skrzyń, nie budują.

## Wariant C-test (AKTYWNY w root)
- Header: `etapa_gen\patches_ext.h` = **380 patchy** (backup 541 w
  `patches_ext_live541.h`).
- USUNIĘTO kategorie relokacji tablic elementu:
  - F (disp relokacje 85)
  - goodstride (43) / housestride (16) — imul stride 0x7F
  - ELOFF (8)
  - E1 (limity pętli kopiowania 4)
  - CAVE GOODS_B (5)
- ZOSTAŁO: A_elemstride (246), B_pool (58), REC/rekord (41), R_rect/UI (30),
  CAVE div0 (5). Tablice elementu wracają na STARE bazy/stride/limity (spójne),
  rekord nadal rozszerzony do 0x7F, menu naprawione, krytyczny crash naprawiony.

## Smoke test
- Build: `etapc\build.bat` OK.
- Uruchomienie launchera: DLL wstrzyknięty, `patches applied: 380/380 ok`.
- Kopie wersji 541 w root: `EtapC.dll.live541.bak`, `launcher.exe.live541.bak`.

## Test użytkownika (do wykonania)
1. Uruchom grę via launcher.exe.
2. Sprawdź mieszkańców: idle/chodzenie, otwieranie skrzyń, budowanie.
3. Sprawdź budynek Test55 z menu budowy.

## Interpretacja wyników
- **Idle OK + Test55 działa** -> relokacja tablic elementu zbędna dla celu;
  wariant gotowy (rozszerzony rekord wystarcza). Można dokończyć „czysto" bez F.
- **Idle OK + Test55 nie działa** -> rozszerzenie tablic elementu jest konieczne
  dla Test55; trzeba dokończyć relokację odczytów (473 REVIEW) albo mirror zapisów.
- **Idle nadal zepsuty** -> przyczyna NIE jest (tylko) w relokacji; szukać dalej
  (np. A/B/R/REC/div0/cave region).