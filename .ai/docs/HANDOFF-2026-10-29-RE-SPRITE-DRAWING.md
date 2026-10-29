# HANDOFF — 2026-10-29 — RE: wpisy odpowiedzialne za rysowanie sprite'ów zasobów (HQ / magazyn / produkcja)

## 1. Cel sesji

Uzupełnienie analizy silnika pod kątem **odpowiedzialnych za rysowanie sprite'ów zasobów**
w budynkach: Kwatera Główna (HQ), magazyn i budynki produkcyjne. Kontynuacja ścieżki
`FUN_004a76fd` / `FUN_004a85cb` z poprzedniej sesji.

## 2. Wyniki RE (REA / Ghidra 12.1.4, `CN.PLMOD.exe`)

### 2.1 Warstwa lookupu sprite'ów (odpowiedzialna: HQ / magazyn / produkcja)

| Adres | Rola |
|---|---|
| `FUN_0042f710` (0x42F710) | sprite table **1**; global `DAT_00511698`; `idx*2` (+1 gdy `flag > 1`); → `FUN_0042bcae` |
| `FUN_0042f754` (0x42F754) | sprite table **2**; global `DAT_005116A0`; ten sam schemat |
| `FUN_0042f776` (0x42F776) | sprite table **3**; global `DAT_005116A4`; ten sam schemat |
| `FUN_0042bcae` (0x42BCAE) | zwraca dane sprite'u z tablicy (`this+0x10` = limit, `+0x18`/`+0x1c` = lookup) |
| `FUN_0042f798` (0x42F798) | sprite budynku/towaru: `FUN_0047FFC0(building_idx)` = `building_idx*0x8BC + 0x3C + DAT_00568C0C`; warunek `good_idx < *(uint*)(instancja+0x18)`; `FUN_0042f776(*(int*)(instancja + good_idx*4), flag)` |
| `FUN_0047ffc0` (0x47FFC0) | `param*0x8BC + 0x3C + DAT_00568C0C` — adres instancji budynku gracza |

### 2.2 Warstwa widgetu i rysowania

- `FUN_004a85cb` (0x4A85CB) — konstruktor widgetu panelu HQ (vtable `PTR_FUN_004f64C0`);
  inicjalizuje pola widgetu (`+0x2c` memset 0xE0, `+0x30`/`+0x34`, `+0x100`/`+0x104`/`+0x108`),
  woła `FUN_00478029` (vtable `PTR_FUN_004f4400`) → `FUN_00478099`.
- `FUN_00478099` → `_memset` (**adres 0x4E55D0 to faktycznie `_memset`** — Ghidra nazwa
  zewnętrznej funkcji, nie nowa procedura).
- Primitives draw: `FUN_004e2172`, `FUN_004e1e3f`, `FUN_004e162e`, `FUN_004e556b`,
  `FUN_004e5410`, `FUN_004e21b7`, `FUN_004e15b3.

### 2.3 Ścieżki wywołań (rysowanie zasobów)

- **HQ**: `FUN_004a009d` → `FUN_004a60a2` (builder) → `FUN_004a693b` (renderer) →
  `FUN_0042f776` / `FUN_0042f798` / `FUN_0042f710` / `FUN_0042f754` + primitives
  `FUN_004e2172` itd.
- **Magazyn**: `FUN_00497bc8` (lista dóbr ze stockiem, `DAT_00510BF0` — tribe house,
  pola `+0x2c`/`+0x39`/`+0x30`/`+0x34`/`+0x38`); wywoływane z `FUN_004ba72f`,
  `FUN_004bd794`, `FUN_004c227c`, `FUN_004c2ace`, `FUN_004c560b`, `FUN_004c5b0c`,
  `FUN_004cc101`. `FUN_004c227c` (lista budynków/typów UI, gałąź iVar8==1) robi
  `FUN_0042f798`, `FUN_0042bcae`, `FUN_004e2172` itd.
- **Produkcja / mapa**: `FUN_0049067f` (renderer mapy) → `FUN_00494f01` (operacja
  budynku) → `FUN_00495e0c` (zarządzanie zapasami) → `FUN_0049A65E` (produkcja);
  sprite'y budynków przez `FUN_0042f798` / `FUN_0047ffc0`.

### 2.4 Dane

- Tablice sprite'ów: `DAT_00511698` (table 1), `DAT_005116A0` (table 2), `DAT_005116A4`
  (table 3).
- `good_id*2 (+1 gdy flag>1)` → indeks; `FUN_0042bcae` zwraca ptr do danych.
- `FUN_004a765f` (0x4A765F) → `FUN_004b6384(DAT_005695B8)` → `idx*0x7E0 + DAT_00510BD0`
  → `char*` — nazwa/asset dobrej.

## 3. Uwagi i ograniczenia

- `FUN_004A693B` (z dużą literą A) **nie istnieje** — poprawny identyfikator to `FUN_004a693b`.
- `0x4E55D0` to `_memset` — nie nowa procedura.
- Call graph zwraca tylko rozwiązane odniesienia Ghidra; wywołania computed/indirect
  pozostają nieznane.

## 4. Następne kroki

1. Rozszerzyć dokumentację o `FUN_00497bc8` i `FUN_00494f01`/`FUN_00495e0c` w `.ai/docs/re/`.
2. `rea close_binary` na `G:\Games\CnMod 1.2\CN.PLMOD.exe`.
3. W razie potrzebnych wpisów do patchów EtapC (dane) / hooki cnmod_hook (zachowanie)
   dla nowych budynków — wrócić do `etapc/src/EtapC.cpp` + `etapa_gen/patches_ext.h`.
