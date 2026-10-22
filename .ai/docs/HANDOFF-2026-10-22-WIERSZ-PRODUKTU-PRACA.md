# HANDOFF 2026-10-22 (noc) - WIERSZ PRODUKTU W SEKCJI "PRACA" (smolarz, dobro 66)

## 1. Objaw (naprawiony)

Okno pracownika-smolarza pokazywalo w sekcji **Praca** tylko wiersz miejsca pracy
("Chata smolarza"), bez wiersza produktu. U mlynarza byly dwa wiersze:

```
Praca
  [ikony] Mlyn
  > Maka <inf>            <- wiersz produktu (strzalka + nazwa + nieskonczonosc + przyciski)
```

Po poprawce smolarz ma:

```
Praca
  [ikony] Chata smolarza
  > Wegiel <inf>
```

## 2. Root cause - JEDNA GRANICA PETLI

Okno czlowieka buduje wiersze produkcji petla po **dobrach** (nie po prodmapie):

```
0x4AC5C8  xor edi,edi
0x4AC5CA  inc edi                  ; g = 1
0x4AC5DD  mov ecx,[ebp-4]          ; unit
0x4AC5E0  push edi
0x4AC5E1  call 0x44B59D            ; stan[g] == 0xC ? -> wiersz POMIJANY
0x4AC5EE  push [ebp-0x10]
0x4AC5F4  call 0x44B5B1            ; stan[g] == 0xD ? -> wiersz POMIJANY
0x4AC60F  push 1 / push g
0x4AC612  call 0x42F710            ; GetGoodString(g, plural=1)
...
0x4AC6E8  inc edi
0x4AC6E9  cmp edi, 0x42            ; <<< GRANICA: g = 1..65
0x4AC6EF  jl  0x4AC5DD
```

Wegiel to dobro **66**, wiec petla nigdy go nie odwiedzala i wiersz nie powstawal.
Zadne dane nie byly zepsute - to wylacznie granica petli w kodzie UI.

## 3. Semantyka tablicy stanow produkcji

`stan[g] = *(u32*)(unit + 0x21C + g*4)` (tablica dwordow, po jednym na dobro):

| stan | znaczenie | efekt w wierszu |
|------|-----------|-----------------|
| `0xB` | "bez limitu" | nazwa + **grafika 0xB4 (= nieskonczonosc)** |
| `0xC` | (wiekszosc dobr) | wiersz pomijany (`0x44B59D`) |
| `0xD` | (np. dobro 5) | wiersz pomijany (`0x44B5B1`) |
| inne | limit liczbowy | format `"%s [%d]"` (`0x507838`) |

Akcesory (thiscall, `ecx = unit`):
```
0x44B576  stan == 0xB   (to jest galaz "inf")
0x44B58A  stan == 0
0x44B59D  stan == 0xC
0x44B5B1  stan == 0xD
0x44B5C5  stan == 0xE
0x44B5D9  get(unit, good) -> stan
0x44B5E7  set(unit, good, val)
0x44B5F9  inc/dec z nasyceniem na 0xB (`cmp [eax],0xB; jge skip`)
```

Ustawianie stanu przy przypisaniu produkcji (`0x44AD58`):
```
0x44AD5B  mov byte [unit+0x195+good], 1     ; can_produce[good] = 1
0x44AD63  call 0x42DA65                     ; bramka "czy moze produkowac"
0x44AD68  neg al / sbb / and -14 / add 0xE   ; bramka != 0 -> 0 ; == 0 -> 0xE
0x44AD76  call 0x44B5E7                     ; set(unit, good, val)
```

Dla smolarza w RAM (PID, sesja 22.10.2026 ~22:50):
```
unit=0x1d8dcb90  job=56  tribe=1  selgood=66
stan[66] = 0xB      <- dokladnie galaz "inf"
can_produce[66] = 1
prodmap = pTribe + 1*0x215E0 + 56*0x400 + 0x6928 -> count=1, lista=[66]
```
czyli wszystko gotowe, brakowalo tylko iteracji.

## 4. Format tekstu wiersza

| adres | format |
|-------|--------|
| `0x500DF4` | `"%s"` (galaz stan == 0xB; potem doklejana grafika `0xB4`) |
| `0x507838` | `"%s [%d]"` (stan liczbowy) |
| `0x507840` | `"%s [%s]"` (menu wyboru dobra) |
| `0x50782C` | `"%s - %d %s"` (wiersze "niedostepne") |
| `0x50720C` / `0x507210` | `">"` / `"<"` (znacznik aktualnie wybranego dobra = strzalka) |

## 5. Poprawka

```c
{ 0x000AC6E9, 2, 1, { 0x43 }, "okno czlowieka 0x4AC6E9: petla wierszy produkcji 0x42 -> 0x43 (wiersz 'Wegiel + inf' w sekcji Praca)" },
```

`etapa_gen\patches_ext.h` -> `EtapC.dll` (przebudowany 22.10.2026 23:1x, wpis obecny w DLL).

Weryfikacja dwojstopniowa:
1. patch **w RAM** (Frida, `Memory.patchCode`, bajt `0x4AC6EB` = `0x42` -> `0x43`) -
   po zamknieciu i ponownym otwarciu okna smolarza wiersz sie pojawil (potwierdzone
   przez uzytkownika).
2. patch **trwaly** w EtapC - do sprawdzenia po restarcie gry (w `logs\etapc.log`
   musi byc linia `patch N ok: okno czlowieka 0x4AC6E9 ...`).

## 6. Mapa okna czlowieka (przydatne na przyszloroczne sesje)

- Getter stringow: `0x4E15B3(sel, id)`, 14 tabel: `sel = [0x569998 + sel*4]`,
  wpisy przez `0x42BCAE(tab, idx)` (count @ `tab+0x10`, offsety @ `[tab+0x18]+8`,
  baza @ `[tab+0x1C]+8`). Fallback (brak wpisu) -> sprintf do bufora `0x5699D0`.
- **`sel 7` = okno czlowieka** (getter `0x4E164A`). Id:
  `1 Ogolne, 2 Wojsko, 3 Praca, 4 Ekwipunek, 5 Doswiadczenie, 6 Handel, 7 Rozne`,
  `10..15` statystyki, `20..29` rodzina/dom, `30..36` miejsce pracy,
  `37..39` wehikul, `40 niemozliwe, 41 brak miejsca pracy, 42 nieskonczone`,
  `50 Zmien produkcje na, 51 Zatrzymaj, 52 Obniz, 53 Zwicksz, 54 Tylko produkuj,
  55 Dalsze informacje o`, `60..73` ekwipunek, `80..84` zolnierz/doswiadczenie.
- Inne tabele (dla odroznienia): `sel 3` = lista ludzi ("Wybierz..."), `sel 4` =
  okno budynku (`1 Uzyj Zezwolenia, 2 Wszystko, 3 Praca, 4 Magazyn, 5 Dom`),
  `sel 8` = okno budynku (Ogolny/Obrona/Miejsce Budowy/...), `sel 0` = menu, `sel 1` = tooltipy.
- Kod okna czlowieka: `0x4AA1xx-0x4AE0xx`; sekcja Praca: `0x4AC2AB-0x4AC9xx`.
- Menu "Zmien produkcje na": petla `0x4AC5DD-0x4AC6EF` (dobra 1..65), tworzy
  kontrolki `0x2737/0x2738/0x2739`; druga, niezalezna lista wyboru dobra:
  `0x4C6BF7` (patch `0x000C6BF7` w tabeli EtapC - inna funkcja, zostawiony).

## 7. Przy okazji naprawione / posprzatane

- `cnmod_hook`: `STRIDE_PLIST` `0x1AE08` -> `0x215E0`. Wczesniejszy log
  `listCount=0` byl **blędem hooka**, nie gry (gral poprawna stala po patchu
  `0x000AC6FE`). Teraz hook pokaze prawdziwe `count=1, list=[66]`.
- `etapc.log` rosl do **91 MB** (1 299 877 linii `GetJobString(job=56)==NULL`).
  Log w hooku `GetJobString` jest teraz dlawiony (pierwsze 8 + co 5000 wystapienie).
  Stary log zrotowany do `logs\etapc_przed_rotacja_tail.txt` (ogon) i usuniety.
- `logs\cnmod_hook.log` -> `logs\cnmod_hook_przed_rotacja.log`.

## 8. Co zostalo (niezrobione)
1. **Transport mezi budynkami** - nadal niepotwierdzone jednostki `job 24`;
   HQ ma `logicworker 24 3` (hipoteza: przewoznikow trzeba zatrudnic w Kwaterze Glownej).
2. Duplikaty `type` w `Data\logic\goodtypes.ini` (27, 49, 59, 60) - wygrywa ostatni blok.
3. Ikona wegla (66) w `landscapetypes.cif` - `landscapetype 16`; do sprawdzenia wizualnie.
4. Opcjonalnie `Data\text\pol\strings\gameobjects\jobs.ini` z `stringn 56 "Smolarz"`
   (wzorzec: `experiences.ini`, cp1250, BEZ `[control]`, naglowek `<00000073>`).
   Teraz nazwa dziala przez fallback w EtapC, wiec to juz tylko kosmetyka.
5. Potencjalny off-by-one: `0x4AC9A7` i `0x44AD7E` licza `tribe * 0x42` dla
   tablicy bajtow `+0x1278`/`+0x1D4C` (66 wpisow na plemie). Przy dobru 66
   indeks wchodzi w nastepne plemie - dotyczy wierszy "niedostepnych", nie naszej
   sciezki. Nie ruszane (brak objawow).

## 9. Jak szybko sprawdzic po restarcie

```
Select-String logs\etapc.log -Pattern "0x4AC6E9"
Select-String logs\cnmod_hook.log -Pattern "listCount" | Select-Object -Last 3
```
W oknie smolarza: sekcja Praca ma dwa wiersze, drugi `> Wegiel <inf>` z przyciskami.

---

## 10. BUG ZNALEZIONY PO POPRAWCE: "wegiel zamienia sie w make" (revmap[66])

Objaw (zgloszony przez uzytkownika): smolarz wywozi wegiel ze smolarni do **piekarni**
(mial pelny magazyn), a w piekarni wegiel "zamienia sie w make".

### 10.1 Root cause

`house_type` ma tablice `revmap[]` pod `+0x37C`, ale ma ona **tylko 66 wpisow (dobra 0..65)**.
Dla dobra 66 odczyt `[rec + 0x37C + 66*4] = [rec + 0x484]` trafia w pole
**licznika listy `logicproduction`** (ktory prawie zawsze wynosi 1).

Skutek: w **kazdym** budynku `revmap[66] = 1`, czyli "dobro 66 lezy w slocie 1".
Slot 1 to w piekarni mąka (jej `logicstock`: `4` -> slot 0, `11` -> slot 1), wiec wegiel
wchodzil do slotu maki.

Potwierdzone w RAM (22.10.2026, PID 7744):

```
piekarnia  bldg=0x0bef5740 htype=13: rev[4]=0  rev[11]=1  rev[66]=1  rev[67]=11
                                     logicstock: count=2 -> (4,10,1) (11,20,0)
chata smol bldg=0x0bef6700 htype=57: rev[5]=0  rev[66]=1  rev[67]=66
                                     logicstock: count=2 -> (5,1,1) (66,15,0)
```
Czyli `rev[67]` to juz nie revmap, a `logicproduction` (count @ +0x484, lista @ +0x488).
Smolarnia dzialala "przez przypadek" - jej licznik produkcji = 1, wiec trafiala w slot 1,
ktory faktycznie jest slotem wegla.

### 10.2 Poprawka (cnmod_hook)

Strażnik w `hook_gate_431f37` (`FUN_00431F37` = "good -> slot" w budynku). Dla dobr >= 66
weryfikuje, ze zwrocony slot faktycznie trzyma to dobro wg `logicstock` tego htype
(count @ `rec+0x60`, wpisy `{good, qty, flag}` po 12 B od `rec+0x64`). Jesli nie - zwraca `-1`.

```
nowe stale:  OFF_STOCK_LIST = 0x60   (w house_type)
             STOCK_ENTRY_SIZE = 0x0C
```

Efekt:
- chata smolarza (ht 57), slot 1 -> good 66 == 66 -> **przepuszcza** (bez zmian),
- piekarnia (ht 13), slot 1 -> good 11 != 66 -> **-1, nie przyjmuje wegla**,
- kazdy inny budynek, ktory nie ma `logicstock 66`, tez nie przyjmie (zamiast
  zapisac wegiel jako inne dobro).

Log: `[g431F37 BLOCK] bldg=... htype=... good=66 -> slot N (tam dobro M) => -1`.

### 10.3 Do sprawdzenia po restarcie

1. Smolarz nie wywozi juz wegla do piekarni (brak `BLOCK` w logu = nie bylo proby).
2. W piekarni mąka nie rosnie "z wepla".
3. Chata smolarza nadal przyjmuje/Przetwarza wegiel (`[g431F37] htype=57 good=66 -> slot=1`).

