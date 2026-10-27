# RE-ANALYSIS PART 90 — crash po kliknięciu smolarni + prawdziwe źródło danych magazynu

Data: 2026-10-27
Binarka: `CN.PLMOD.exe` (PE32, ImageBase `0x400000`, SizeOfImage `0x174000`, plik `0x118000` B)

Ten dokument zamyka dwa otwarte punkty z `RE-ANALYSIS-PART89`:

1. **crash `AV: READ @ 0xFFFFFF80` po kliknięciu budynku** — przyczyna: cztery nieistniejące
   ("wymyślone") patche `0x38 → 0x43`,
2. **„w magazynie dalej nic nie ma"** — przyczyna: edytowaliśmy **niewłaściwy plik**
   `houses.ini`.

---

## 1. Crash — anatomia

`logs/crash.txt`:

```
=== CRASH #1 code=0xC0000005 flags=0x0 addr_va=0x004a82c5 addr_rva=0x000A82C5
  AV: READ @ 0xFFFFFF80
  bajty@EIP: 8B 43 80 7B 74 00 0F 84 7A 01
  EAX=0x00000000 EBX=0x00000000 ECX=0x1ACF1300 ...
  EIP=0x004A82C5
```

`0x004A82C5 − 0x00400000 = 0x000A82C5` — czyli **RVA 0xA82C5**, a nie `0xA2C5`
(wcześniej ta arytmetyka została policzona błędnie i uznano crash za „niezwiązany
z patchami"). To jest dokładnie miejsce, w które trafił patch `0x000A82C6`.

### 1.1 Co jest w binarce

```
0A82BC  55                  PUSH EBP
0A82BD  8B EC               MOV EBP,ESP
0A82BF  81 EC 28 02 00 00   SUB ESP,0x228
0A82C5  53                  PUSH EBX
0A82C6  8B D9               MOV EBX,ECX        <-- tu patch wpisał 0x43
0A82C8  80 7B 74 00         CMP BYTE [EBX+0x74],0
0A82CC  0F 84 7A 01 00 00   JE  +0x17A
```

Bajt `0xD9` w `8B D9` to **ModRM** (`MOV EBX,ECX`), a nie imm8 porównania.
Po podmianie na `0x43` procesor widzi:

```
0A82C6  8B 43 80            MOV EAX,[EBX-0x80]
```

`EBX = 0` (rejestr przed `MOV EBX,ECX`), więc odczyt spod `0xFFFFFF80` → `C0000005`.
To wyjaśnia **dokładnie** adres z logu (`AV: READ @ 0xFFFFFF80`) i wartość `EBX=0`.

Funkcja `0x0A82BC` jest wołana przy rysowaniu panelu **każdego** budynku — dlatego
crash wychodził „po naciśnięciu na smolarnię".

### 1.2 Wszystkie cztery „wewnętrzne" patche były błędne

| RVA patcha | bajt w pliku | czym ten bajt naprawdę jest |
|---|---|---|
| `0x000A8022` | `0x00` | imm8 w `AND DWORD [EBP-4], 0` (`83 65 FC 00` @ `0xA801F`) |
| `0x000A80FC` | `0x18` | imm8 w `SUB EAX, 0x18` (`83 E8 18` @ `0xA80FA`) |
| `0x000A81FA` | `0x8B` | opcode `MOV ECX,ESI` (`8B CE` @ `0xA81FA`) |
| `0x000A82C6` | `0xD9` | ModRM `MOV EBX,ECX` (`8B D9` @ `0xA82C5`) |

Adresy zostały wcześniej **zgadnięte**, nie odczytane z binarki. Żaden z tych bajtów
nie był wartością `0x38`. Efekt: `patch ... ok` w logu (EtapC nie weryfikuje starej
wartości) + uszkodzony kod.

> **Wniosek procesowy:** patch jest poprawny tylko wtedy, gdy bajt w pliku *przed*
> podmianą zgadza się z oczekiwanym. EtapC raportuje `ok` również dla podmiany
> w dowolne miejsce — log `N/N ok` **nie jest** dowodem poprawności adresu.

---

## 2. Ile jest filtrów `<= 0x37` w panelu magazynu? **Cztery. Nie osiem.**

Dekompilator pokazywał w `FUN_004a693b` (zakładki 5 i 6) oraz `FUN_004a76fd`
zakładki 5 i 6 po dwa testy: na wejściu do pętli i „wewnątrz" (`if (iVar7 < 0x38)`).
W binarce to **ten sam** test. `iVar7 < 0x38` kompiluje się jako `CMP reg,0x37` + `JG`.

Skan `.text` (`83 /r 37` i `83 /r 38`) w zakresie obu funkcji daje dokładnie 4 trafienia:

| RVA `CMP` | bajty | funkcja / zakładka |
|---|---|---|
| `0x000A7331` | `83 FB 37 0F 8F 88 00 00 00` | `FUN_004a693b`, zakładka 5 (zapasy) |
| `0x000A7432` | `83 F8 37 89 45 0C 0F 8F 8D …` | `FUN_004a693b`, zakładka 6 (szczegóły) |
| `0x000A7EF5` | `83 F9 37 89 4D DC 7F 5F` | `FUN_004a76fd`, zakładka 5 |
| `0x000A7FB1` | `83 F8 37 89 45 D8 7F 6D` | `FUN_004a76fd`, zakładka 6 |

Imm8 leży zawsze 2 bajty dalej — stąd `0xA7333`, `0xA7434`, `0xA7EF7`, `0xA7FB3`.
Te cztery patche (`0x37 → 0x42`) są **jedyne i wystarczające**. Nie ma drugiego filtra.

Kontekst pętli (`FUN_004a76fd`, zakładka 5) — widać, że test `<=0x37` jest tym samym
testem, który dekompilator pokazywał jako `if (iVar7 < 0x38)`:

```
0A7EEC  83 C0 6C         ADD EAX,0x6C            ; &wpis + 8
0A7EEF  89 45 F4         MOV [EBP-0xC],EAX
0A7EF2  8B 48 F8         MOV ECX,[EAX-8]         ; good id
0A7EF5  83 F9 37         CMP ECX,0x37            ; <-- patch: 0x42
0A7EF8  89 4D DC         MOV [EBP-0x24],ECX
0A7EFB  7F 5F            JG  +0x5F               ; pomiń dobro > 0x37
0A7EFD  80 38 00         CMP BYTE [EAX],0        ; flaga wpisu (+8)
0A7F00  75 5A            JNE +0x5A               ; !=0 -> pomiń rysowanie
```

---

## 3. Prawdziwa przyczyna „magazyn dalej pusty": zły plik `houses.ini`

Parser `FUN_0041531d` otwiera:

```
VA 0x0050055C -> "cn.plmod\types\houses.ini"
```

czyli **`CN.PLMOD/types/houses.ini`**. Tymczasem wszystkie nasze edycje z 26.10
(`logicstock 66 45/70/120 0`) poszły do `Data/logic/houses.ini`, którego gra
**nie czyta** w tym trybie.

`Data/logic/houses.ini` to kopia źródłowa z markerami `<CULTURES_CIF_BEGIN>` /
`<CULTURES_CIF_END>` (format edytora / `.cif`), a `CN.PLMOD/types/houses.ini` to
kopia runtime. Różnice (diff, 26 linii) sprowadzały się do:

* markerów CIF (tylko w `Data/logic`),
* trzech naszych linii `logicstock 66 …` (tylko w `Data/logic`),
* `logicworker 24 1` w bloku smolarza (tylko w runtime — dodane 19.10 bez synchronizacji).

### 3.1 Stan bloków w pliku runtime

| `debugname` | `logictype` | wpisów `logicstock` | miał dobro 66? |
|---|---|---|---|
| `headquarters` | 1 | 50 | **tak** (od 19.10) |
| `stock 00` | 7 | 49 | nie |
| `stock 01` | 8 | 49 | nie |
| `stock 02` | 9 | 49 | nie |
| `work charcoal burner` | 57 | 2 | **tak** |

Czyli: Kwatera Główna miała węgiel w danych od 19.10 (blokowany tylko filtrem kodu),
a **budynki magazynowe `stock 00/01/02` nie miały go wcale** — i to jest „magazyn,
w którym dalej nic nie ma".

### 3.2 Poprawka

Do `CN.PLMOD/types/houses.ini` dopisano po `logicstock 55 <limit> 0`:

```
stock 00: logicstock 66 45 0     (linia 164)
stock 01: logicstock 66 70 0     (linia 224)
stock 02: logicstock 66 120 0    (linia 284)
```

Backup: `CN.PLMOD/types/houses.ini.bak_warehouse_coal_20261027_143145`.
Kontrola: cp1250, CRLF (943), 0 × samo-LF, brak BOM, 0 × U+FFFD,
`ini_normalize.py` dry-run → `plikow zmienionych 0`.

---

## 4. Układ wpisu `logicstock` (z `FUN_0041531d`)

Rekord `house_type`: stride `0x624`, baza `DAT_005113a0` (`0x5113A0`).

| Offset | Znaczenie |
|---|---|
| `+0x60` | liczba wpisów `logicstock` (`piVar10[0x18]`) |
| `+0x64` | tablica wpisów, **12 B** każdy: `+0` good, `+4` limit, `+8` flaga (bool) |
| `+0x37C` | `revmap[]` — `revmap[good] = indeks wpisu` (`piVar10[good + 0xDF]`) |

Warunki parsera:

```c
if (piVar10[0x18] != 0x42) {          /* max 66 wpisów */
  if (iVar13 < 0x43) {                /* good < 67  -> 66 wchodzi */
    piVar11 = piVar10 + count*3 + 0x19;
    piVar11[0] = good;                /* +0 */
    piVar11[1] = min(amount, 1000);   /* +4 */
    ((bool*)piVar11)[8] = (flag != 0);/* +8 */
    piVar10[good + 0xDF] = count;     /* revmap[good] @ +0x37C */
    piVar10[0x18] = count + 1;
  }
}
```

Uwaga na kolizję: `revmap[66]` = `+0x37C + 66*4` = `+0x484` = początek
`logicproduction`. Pilnuje tego strażnik `hook_gate_431f37` w `cnmod_hook`
(nie usuwać).

Trzecia liczba w `logicstock` (flaga) jest `0` dla **wszystkich** dóbr w magazynie
(`logicstock 16 150 0` itd.), więc `0` przy węglu jest poprawne.

---

## 5. Co jeszcze sprawdzono (i uznano za nie-blokujące)

* `FUN_00431a83(this, good, flag)` ma bramkę `param_2 < 0x42`, więc dla dobra 66
  zwraca `0.0`. W miejscu wywołania (`FUN_004a693b`) **wartość zwracana jest
  odrzucana**, więc nie wpływa na rysowanie wiersza.
* Format wiersza zapasów to `{gfxgood:%d,1}    %.1f` (`0x00507710`), a wiersz
  „produkcja/tooltip" używa `{gfxgood:%d,1} %s: %d` (`0x0050772C`). Skoro tooltip
  smolarni pokazuje ramkę + „Węgiel", zasób `gfxgood 66` **istnieje i się rysuje** —
  ten sam mechanizm obsłuży wiersz magazynu.
* Nazwa dobra: `FUN_0042f710(good, 1)` → `FUN_0042bcae(DAT_00511698, good*2)`.
  Nazwa „Węgiel" jest w `Data/text/pol/strings/gameobjects/goods.ini` (cp1250).

---

## 6. Stan tabeli patchy po zmianie

* Usunięto 4 błędne wpisy `0x000A8022`, `0x000A80FC`, `0x000A81FA`, `0x000A82C6`.
* Zostały 4 wpisy `MAGAZYN …` (`0x000A7333`, `0x000A7434`, `0x000A7EF7`, `0x000A7FB3`).
* `PATCH_COUNT` = **683**. `EtapC.dll` 97280 B, sha256 `eab82b61a4f636d3…`.
* W komentarzu przy wpisach jest ostrzeżenie „NIE PRZYWRACAĆ" z opisem crasha.

## 7. Do weryfikacji w grze

1. Klik na smolarnię — **nie może crashować** (to był bug z `0xA82C6`).
2. Magazyn `stock 00/01/02` → zakładka zapasów: wiersz „Węgiel" z ikoną.
3. Kwatera Główna → zakładka zapasów: wiersz „Węgiel" (dane były od 19.10,
   odblokowane filtrem kodu).
4. Dostarczenie węgla do magazynu → wartość > 0.
