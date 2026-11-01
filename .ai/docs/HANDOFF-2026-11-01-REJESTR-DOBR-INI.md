# HANDOFF 2026-11-01 — rejestr dóbr modowanych w INI (koniec zaszytego „GOOD_COAL")

**Cel:** nowy surowiec ma dać się dodać samymi danymi (`.ini` + `.cif` + paleta) — bez
przebudowy DLL. Węgiel (good 66) zostaje pierwszym, wbudowanym przypadkiem użycia.

**Status:** DLL przebudowany i linkuje się czysto (`cnmod_hook\build.bat` → `== OK ==`).
**Nieprzetestowane w grze** — wymaga uruchomienia i sprawdzenia logów (patrz §5).

---

## 1) Co powstało

### `cnmod_hook/src/main.cpp` — rejestr dóbr (`struct ModdedGood`)

```c
struct ModdedGood { uint32_t good, landscapetype, job, house, carryType, carrySource; int32_t iconFallback; };
static ModdedGood g_modGoods[32];
static uint32_t   g_modGoodN;
```

Funkcje: `AddModdedGood`, `FindModdedGood`, `FindModdedGoodByJob`,
`FindModdedGoodByHouse`, `IsModdedGood/Job/House`, `ModdedSampleGood`,
`LoadModdedGoodsIni()` (wołane z `install_hooks()` zaraz po `LoadLandscapeGoodMapIni()`).

Brak pliku INI ⇒ jeden wbudowany wpis `good=66` (węgiel) — zachowanie 1:1 jak wcześniej.

### Nowy plik danych

`CN.PLMOD\types\cnmx_goods.ini` (cp1250, CRLF, bez BOM, 1576 B):

```ini
[modded_good]
good            66
landscapetype   88
job             56
house           57
carry_type      19
carry_source    20
icon_fallback   3
```

Klucze: `good` (≤ 66), `landscapetype`, `job`, `house`, `carry_type` (wpis tabeli renderu
niesienia `0x512750`, stride `0x184`), `carry_source` (wpis źródłowy kopiowany), `icon_fallback`
(dobro, którego ikona jest rysowana zamiast własnej; `-1` = brak).

### Co przestało być zaszyte

| Miejsce | Wcześniej | Teraz |
|---|---|---|
| `hook_sched_44a0d9` | `can_produce[66] = 1` | pętla po rejestrze (`good < 0x83`) |
| patch tabeli `0x512750` (w `hook_gate_431f37`) | `typ 19 ← typ 20`, `+0x10 = 66` | pętla po rejestrze, maska `g_tablePatchMask` |
| `hook_gate_431f37` | `good >= 66` | `good >= REVMAP_COUNT` (66), usunięty martwy blok i martwy `slotgood` check |
| `hook_stock_add`, `hook_gate_42da65`, `hook_gate_44b58a`, `hook_gate_4316f3`, `hook_gate_431ddf`, `hook_gate_431ced`, `hook_unit_tick`, `hook_find_owner` | porównania z 66/56/57 | `IsModdedGood/Job/House` |
| `hook_action_loop_46b621` | `job == 56 && (ad0/ad4 == 66)` | `FindModdedGoodByJob(job)` + `mg->good` |
| `hook_carry_lookup_45c94b`, `hook_gate_46b696`, `hook_pickup_4760bf`, `hook_anim_lookup_45d14f`, `hook_anim_setup_45c23e`, `hook_carry_render_42d575`, `hook_set_action`, `hook_prod_finish`, `hook_stock_write`, `hook_draw_good_icon` | stała 66 / typ 19 | rejestr (`hook_draw_good_icon` → `iconFallback`) |
| `dump_carry_table_once` | wymuszał wpis typu 19 | tylko diagnostyka wpisów z rejestru |

Usunięto stałe `JOB_SMOLARZ` i `TYPE_SMOLARNIA`; `GOOD_COAL = 66` została **wyłącznie**
jako wartość awaryjna (`ModdedSampleGood`, fallback rejestru).

---

## 2) Dlaczego NIE podnosimy limitu dobra do 0x7F

Przejrzano wszystkie 47 miejsc z granicami `0x42`/`0x43` w `etapa_gen/patches_ext.h`
(pełna inwentaryzacja: `_sites.txt`, do usunięcia). Podział:

- **filtry list danych** (magazyn, menu produkcji, kategorie) — bezpieczne, już rozszerzone;
- **tablice per-jednostka** — blokada:
  - `stan[good]` = `[unit + good*4 + 0x21C]`, 66 wpisów (`0x21C..0x324`),
  - rekord jednostki ma stride **`0xC58`** (`imul reg,0xC58` + `DAT_00510bD8`),
  - pod `stan[]` leżą `+0x36C`/`+0x374` (maszyna stanów jednostki, setki odwołań),
  - własne pętle silnika kończą na `0x42`.

`can_produce[]` (`unit+0x195`, bajty) mieści dobra do 126 — to **nie** jest limitem;
limitem jest `stan[]`. Rozszerzenie = relokacja tablicy w rekordzie jednostki = Etap C.

Wolne ID w `Data\logic\goodtypes.ini`: **0, 50, 51** (duplikaty 27/49/59/60 to
istniejący problem danych).

---

## 3) Weryfikacja statyczna (zrobiona)

- `0x4316F3` woła `0x431F37` (w `0x43176D`), a `0x431DDF` woła `0x432D75` — uniwersalny
  strażnik `logicstock` w `0x431F37` pokrywa oba, więc EtapC nie wymagał rozszerzenia.
- Build: `cnmod_hook\build.bat` → `== OK ==` (gra była zamknięta).
- `python .ai\scripts\ini_normalize.py` → dry-run: **plików zmienionych 0**.

## 4) Zmiany w danych (poza kodem)

| Plik | Zmiana | Backup |
|---|---|---|
| `CN.PLMOD\types\cnmx_goods.ini` | **nowy** (rejestr dóbr) | — |
| `CN.PLMOD\types\landscape_good_map.ini` | przekonwertowany UTF-8 → cp1250 (standard), przykłady `89 = 69 / 90 = 70` → `50 / 51` (dobra > 66 nie działają) | `landscape_good_map.ini.bak_format_20261101_205737` |
| `.ai\docs\jak-dodac-budynek-lub-surowiec.md` | przepisany: twarde limity, rejestr `cnmx_goods.ini`, reguła unikalnej nazwy obiektu, wolne ID 0/50/51, przykłady `--id 50` zamiast `--id 70` | — |

## 5) Do sprawdzenia w grze (kolejna sesja)

1. Uruchom grę, otwórz `logs\cnmod_hook.log`, znajdź:
   - `[goods] Wczytano 1 dobr modowanych z CN.PLMOD\types\cnmx_goods.ini`
   - `[goods]   good=66 landscapetype=88 job=56 house=57 carry=19/20 icon_fallback=3`
   - `[table] good=66: typ 19 <- 20 (first=1)`
2. Smolarnia: produkcja węgla, ikona czarna, sterta czarna, podniesienie zwraca węgiel,
   stackowanie węgla zostaje węglem, tooltip „Węgiel".
3. Test rejestru: skopiuj blok na `good=50` (po dodaniu `[goodtype] type 50`), sprawdź czy
   pojawia się `[goods]` z 2 wpisami — bez przebudowy DLL.
4. Jeśli coś nie działa: `cnmod_hook.dll.old` nie istnieje, poprzednia wersja jest w gicie
   (`git checkout -- cnmod_hook/src/main.cpp` + rebuild).

## 6) Otwarte / następne kroki

- Etap C: relokacja `stan[]` w rekordzie jednostki — dopiero to znosi limit `good ≤ 66`.
- Duplikaty `type` 27/49/59/60 w `goodtypes.ini` (istniejący problem danych).
- `modkit.py` (zamrożony prototyp) nie zna `cnmx_goods.ini` — do dopisania przy M0/M1.
- `carry_type` dla nowych dóbr trzeba wybierać ręcznie z wolnych wpisów tabeli `0x512750`
  (obecnie 5–16, 19, 20 zajęte).
- `hook_sched_44a0d9` ustawia `can_produce[good] = 1` **każdej** jednostce dla **każdego**
  wpisu rejestru. To bezpieczne, bo produkcję i tak bramkuje `prodmap[job]`, ale przy wielu
  modowanych dobrach warto sprawdzić, czy nie pojawiają się w menu produkcji obcych zawodów.

