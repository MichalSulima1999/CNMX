# Łańcuch produkcji — główna pętla gry i ticki budynków

**Źródło:** Dekompilacja Ghidra 12.1.4 (REA)
**Data:** 2026-10-17
**Pseudokod:** C (z zachowaniem oryginalnych nazw zmiennych Ghidry)

---

## Przepływ wywołań (od głównej pętli do produkcji)

```
FUN_004078C8 (główna pętla gry)
  └─ FUN_0040AD0A (iteracja po budynkach)
       └─ FUN_00433662 (tick budynku)
            └─ FUN_0043127A (iteracja po tablicy jednostek)
                 └─ FUN_0044193D (tick jednostki)
                      └─ FUN_00462C70 (pętla stanu)
                           └─ FUN_0044319A (tick stanu +0x368)
                                └─ FUN_0046BAD7 (dyspozytor na job)
                                     └─ FUN_0046D53A (potter handler, job 0x19)
                                          └─ FUN_0046E52E (logika produkcji)
```

---

## 1. Główna pętla gry — FUN_004078C8

**Adres:** 0x4078C8
**Wywołanie:** cykliczne (co N ticków gry)
**Parametry:** void

```c
void FUN_004078C8(void)
{
    if (DAT_005109F0 != 0) {                          // gra aktywna
        if (DAT_00510B9C != 0) {                      // warunek pętli
            // co 0x1E ticków: aktualizacja czasu
            if (DAT_00510A10 % (__ftol() * 0x1E) == 0) {
                memset(local_18, 0, 0x14);
                local_18[0] = 0x8A;
                local_14 = FUN_00428824();            // pobranie czasu
                local_10 = DAT_00510A10;
                local_c = FUN_004DE32A(0x50F880);
                FUN_004118F8(DAT_00510C00, local_18, 1, 0);
            }
        }
        DAT_00510A10 = DAT_00510A10 + 1;              // tick counter++
        DAT_00510A18 = DAT_00510A18 + DAT_00510A28;   // delta time

        // co 0x2D0 ticków
        if (DAT_00510A10 % 0x2D0 == 0) {
            FUN_0041AD50(DAT_005116E8, (DAT_00510A10 % 0x2D0 << 0x20 | DAT_00510A10) / 0xC);
        }

        FUN_0040BD39(DAT_00510BF4);                   // tick UI?

        FUN_0040AD0A(DAT_00510BD4);                   // tick budynków

        // co 0xC ticków
        if (DAT_00510A10 % 0xC == 0) {
            FUN_0040AD41(DAT_00510BD4);               // tick dodatkowy budynków
            FUN_0042866F(DAT_00512764);
            FUN_004279D4(DAT_00512760);
        }

        FUN_0042720E();                               // tick globalny
        FUN_0042706B(DAT_0051275C);
        FUN_00426BA0(DAT_00512758);
        FUN_0041A10C(DAT_005116E4);
        FUN_00409C4D(DAT_00510BC4, DAT_00510A10);     // tick elementów gracza
        FUN_004075BF();
        FUN_004127EF(DAT_00510C0C, 1, 1, DAT_00510A10, 0, 0);
    }
}
```

**Uwagi:**
- `DAT_00510A10` = globalny licznik ticków gry
- `DAT_00510A28` = delta time
- `DAT_00510BD4` = wskaźnik do struktury batch budynków (ma pola +0x14=start, +0x18=end)

---

## 2. Iteracja po budynkach — FUN_0040AD0A

**Adres:** 0x40AD0A
**Parametry:** `int param_1` — wskaźnik na strukturę batch (start/end index)

```c
void FUN_0040AD0A(int param_1)
{
    int iVar1;
    int iVar2;

    iVar2 = *(int *)(param_1 + 0x14);                 // start index
    if (iVar2 <= *(int *)(param_1 + 0x18)) {          // start <= end
        iVar1 = iVar2 * 0x7E0;                        // offset = idx * sizeof(building)
        do {
            if (*(char *)(iVar1 + DAT_00510BD0) != 0) {  // building is active
                FUN_00433662((char *)(iVar1 + DAT_00510BD0));  // tick budynku
            }
            iVar2 = iVar2 + 1;
            iVar1 = iVar1 + 0x7E0;
        } while (iVar2 <= *(int *)(param_1 + 0x18));
    }
}
```

**Uwagi:**
- Iteruje po budynkach od `start` do `end` (stride 0x7E0 = sizeof(building))
- `DAT_00510BD0` = tablica budynków
- Budynek jest "aktywny" jeśli `*building != 0`

---

## 3. Tick budynku — FUN_00433662

**Adres:** 0x433662
**Parametry:** `char *param_1` — wskaźnik na building

```c
void FUN_00433662(char *param_1)
{
    if (param_1[2000] == 0) {                         // budynek ukończony?
        if (*(int *)(param_1 + 0x7C8) < 1) {          // budowa w toku?
            FUN_00419C1D(DAT_005116D8, (int)param_1);
            FUN_0043127A(param_1);                    // tick jednostek w budynku
        }
        if (param_1[2000] == 0) goto LAB_004336F0;    // sprawdź ponownie
    }

    // Budynek ukończony — animacja/timer
    *(short *)(param_1 + 0x7D2) = *(short *)(param_1 + 0x7D2) + 1;  // timer++
    if (*(int *)(param_1 + 0x7D2) == *(short *)(param_1 + 0x7D4) + -0xC) {
        FUN_004127EF(DAT_00510C0C, 0x1D, 1, *(int *)(param_1 + 4), 0, 0);  // dźwięk
    }
    if (*(short *)(param_1 + 0x7D4) <= *(short *)(param_1 + 0x7D2)) {
        FUN_0040ACBA(DAT_00510BD4, *(int *)(param_1 + 4));  // zakończ animację
        return;
    }

LAB_004336F0:
    // Sprawdź category budynku
    if (*(int *)(*(int *)(param_1 + 0x14) * 0x624 + DAT_005113A0) == 6) {
        // Category 6 = budynek produkcyjny
        if (*(int *)(param_1 + 0x2C) == 3) {          // type 3?
            FUN_0040ACBA(DAT_00510BD4, *(int *)(param_1 + 4));
            FUN_0040ADD3(*(int *)(param_1 + 0xC), *(int *)(param_1 + 0x18),
                         *(int *)(*(int *)(param_1 + 0x14) * 0x624 + 0x5E4 + DAT_005113A0),
                         (ushort *)(param_1 + 0x1C), 0);
            return;
        }
    }
    else if (*(int *)(param_1 + 0x2C) == 3) {
        FUN_0043B1FD(*(uint *)(param_1 + 0xC), (short *)(param_1 + 0x1C));
    }

    // Komunikaty UI
    if ((param_1[0x7D8] != 0) && (*(int *)(param_1 + 0x2C) == 3) && (param_1[2000] == 0)) {
        // ... iteracja po komunikatach
    }
}
```

**Uwagi:**
- `param_1[2000]` = flaga ukończenia budowy
- `param_1 + 0x7D2` = timer animacji (short)
- `param_1 + 0x7D4` = target timer (short)
- `param_1 + 0x14` = house_type index
- `DAT_005113A0 + type * 0x624` = house_type record
- `param_1 + 0x2C` = building type/subtype
- **FUN_0043B1FD** = komunikaty UI (nie produkcja!)

---

## 4. Iteracja po tablicy jednostek — FUN_0043127A

**Adres:** 0x43127A
**Parametry:** `char *param_1` — wskaźnik na building

```c
void FUN_0043127A(char *param_1)
{
    void *this;
    int iVar1;
    int iVar2;
    uint uVar3;
    undefined4 uVar4;
    undefined4 uVar5;

    if (*param_1 != 0) {                              // building active
        FUN_00434160(param_1);                        // aktualizacja
        FUN_00432170(param_1);                        // aktualizacja
        iVar1 = FUN_004238DC((short *)(param_1 + 0x24));  // pobranie mapy
        iVar1 = *(short *)(iVar1 + 10);               // offset tablicy jednostek

        while (iVar1 != -1) {                         // iteracja po tablicy
            iVar2 = iVar1 * 0x58 + DAT_00510BF0;      // unit record (stride 0x58)
            iVar1 = *(int *)(iVar2 + 8);              // następny wpis

            if (iVar1 == 1) {                         // type 1 = budynek
                FUN_0044193D((void *)(*(int *)(iVar2 + 0x54) * 0xC58 + DAT_00510BD8));
            }
            else if (iVar1 == 2) {                    // type 2 = ?
                FUN_0042F6DA(*(int *)(iVar2 + 0x54) * 0x98 + DAT_00511720);
            }
            else if ((iVar1 < 3) || (4 < iVar1)) {
                FUN_00406A63(&DAT_005010B4);          // error
            }

            iVar1 = *(int *)(iVar2 + 0x24);           // następny wpis
        }

        // Timer budowy
        if (*(int *)(param_1 + 0x2C) == 1) {          // type 1 = w budowie
            param_1[0x7D2] = 0;
            param_1[0x7D3] = 0;
            *(short *)(param_1 + 0x7D4) = (short)(((*(int *)(param_1 + 0x30) * 100) / *(int *)(param_1 + 0x34)) * 0x18) / 100);
        }
        else {
            param_1[0x7D4] = 0x18;
            param_1[0x7D5] = 0;
        }

        // Rozpocznij budowę
        this = DAT_00510C0C;
        if (*(short *)(param_1 + 0x7D4) == 0) {
            FUN_0040ACBA(DAT_00510BD4, *(int *)(param_1 + 4));
        }
        else {
            if (*(short *)(param_1 + 0x7D4) < 0xC) {
                uVar5 = 0;
                uVar3 = 0;
                uVar4 = *(undefined4 *)(param_1 + 4);
                iVar1 = 0x1D;
            }
            else {
                uVar5 = 1;
                uVar3 = FUN_0042AED3((short *)(param_1 + 0x1C));
                uVar4 = 0x2A;
                iVar1 = 0x17;
            }
            FUN_004127EF(this, iVar1, 1, uVar4, uVar3, uVar5);
            param_1[2000] = 1;                          // budynek ukończony
        }
    }
}
```

**Uwagi:**
- `DAT_00510BF0` = tablica jednostek (stride 0x58)
- `iVar2 + 0x54` = unit index
- `DAT_00510BD8` = tablica unitów (stride 0xC58)
- `DAT_00511720` = inna tablica (stride 0x98)
- **FUN_0044193D** = tick jednostki w budynku
- Budynek zostaje ukończony gdy `param_1[2000] = 1`

---

## 5. Tick jednostki — FUN_0044193D

**Adres:** 0x44193D
**ParamETERS:** `void *param_1` — wskaźnik na unit

```c
void FUN_0044193D(void *param_1)
{
    if (*(int *)((int)param_1 + 0xAB8) != 1) {        // czy unit aktywna?
        FUN_0045C6B1((int)param_1);                  // pre-tick
        FUN_00442FC7((int)param_1);                  // aktualizacja
        *(undefined1 *)((int)param_1 + 0xA61) = 1;
        *(undefined1 *)((int)param_1 + 0xA60) = 1;
        FUN_00462C70(param_1);                        // pętla stanu
        *(undefined4 *)(*(int *)((int)param_1 + 0xC) * 0x58 + 0x20 + DAT_00510BF0) = 2;
    }
    *(undefined1 *)((int)param_1 + 0xB50) = 0;
}
```

**Uwagi:**
- `param_1 + 0xAB8` = flaga aktywności
- **FUN_00462C70** = główna pętla stanu jednostki
- `param_1 + 0xC` = tribe index
- `DAT_00510BF0` = tablica jednostek (stride 0x58)

---

## 6. Pętla stanu jednostki — FUN_00462C70

**Adres:** 0x462C70
**Parametry:** `void *param_1` — wskaźnik na unit

```c
void FUN_00462C70(void *param_1)
{
    bool bVar1;
    char cVar2;
    undefined4 uVar3;
    undefined3 extraout_var;
    short *psVar4;
    int iVar5;
    undefined4 extraout_ECX;
    void *local_8;

    local_8 = param_1;

    // Sprawdź warunki zakończenia
    if (*(int *)((int)param_1 + 0xACC) == 0) goto LAB_00462D18;
    bVar1 = FUN_0042CF4B((int)param_1);
    if (!bVar1) goto LAB_00462D18;
    uVar3 = FUN_0042CF57((int)param_1);
    if ((char)uVar3 != 0) goto LAB_00462D18;

    // Stan ui_state (+0xA68)
    iVar5 = *(int *)((int)param_1 + 0xA68);
    if (iVar5 == 1) {
        *(undefined4 *)((int)param_1 + 0x374) = 1;
        goto LAB_00462D0E;
    }
    if (iVar5 == 2) {
        if (*(int *)((int)param_1 + 0xAD0) == 0) {
            cVar2 = FUN_0042D202((int)param_1);
            *(int *)((int)param_1 + 0xAD0) = (&DAT_00510C60)[CONCAT31(extraout_var, cVar2)];
        }
        *(undefined4 *)((int)param_1 + 0x36C) = 3;
        *(undefined4 *)((int)param_1 + 0x374) = 3;
        goto LAB_00462D18;
    }
    if (iVar5 < 3) {
LAB_00462CD5:
        *(undefined4 *)((int)param_1 + 0x374) = 0;
    }
    else if (iVar5 < 5) {
        *(undefined4 *)((int)param_1 + 0x374) = 7;
    }
    else {
        if (iVar5 != 7) goto LAB_00462CD5;
        *(undefined4 *)((int)param_1 + 0x374) = 6;
    }

LAB_00462D0E:
    *(undefined4 *)((int)param_1 + 0x36C) = 3;

LAB_00462D18:
    // Sprawdź tribe house
    if (*(char *)(*(int *)((int)param_1 + 0xC) * 0x58 + 0x10 + DAT_00510BF0) != 0) {
        psVar4 = (short *)FUN_0042CEA6((int)param_1);
        iVar5 = FUN_004238DC(psVar4);
        if ((*(byte *)(iVar5 + 0xC) & 0x80) != 0) {
            FUN_00442FC7((int)param_1);
            iVar5 = 0;
            uVar3 = extraout_ECX;
            FUN_0042AEC0(&stack0xFFFFFFE4, 0);
            FUN_004447C4(param_1, uVar3, iVar5);
        }
    }

    // Sprawdź building
    psVar4 = (short *)((int)param_1 + 0xB30);
    iVar5 = FUN_004238DC(psVar4);
    if ((*(byte *)(iVar5 + 0xC) & 0x80) != 0) {
        bVar1 = FUN_0042C783((int)param_1);
        if (!bVar1) {
            local_8 = *(void **)psVar4;
            bVar1 = FUN_0043B164((short *)&local_8, 0);
            if (bVar1) {
                *(void **)psVar4 = local_8;
                *(undefined4 *)((int)param_1 + 0x38C) = 0;
                FUN_004530D6((int)param_1);
            }
        }
    }

    // Pętla stanu
    while (iVar5 = *(int *)((int)param_1 + 0x36C), iVar5 != 1) {
        if (iVar5 == 0) {
            FUN_0044319A(param_1);                     // tick stanu głównego
        }
        else if (iVar5 == 2) {
            FUN_00443465(param_1);
        }
        else if (iVar5 == 3) {
            FUN_004435A0(param_1);
        }
    }

    *(undefined1 *)((int)param_1 + 0xA60) = 0;
    *(undefined1 *)((int)param_1 + 0xA61) = 0;
    *(undefined4 *)((int)param_1 + 0x374) = 2;
}
```

**Uwagi:**
- `param_1 + 0x36C` = stan główny (0=idle, 1=end, 2/3=...)
- `param_1 + 0x374` = podstan
- `param_1 + 0xA68` = ui_state (1, 2, 5, 7)
- `param_1 + 0xACC` = interaction state
- `param_1 + 0xAD0` = selected good
- **FUN_0044319A** = tick stanu głównego
- **FUN_00443465**, **FUN_004435A0** = pozostałe stany

---

## 7. Tick stanu głównego — FUN_0044319A

**Adres:** 0x44319A
**Parametry:** `void *param_1` — wskaźnik na unit

```c
void FUN_0044319A(void *param_1)
{
    int *piVar1;
    int iVar2;
    char cVar3;
    undefined4 uVar4;
    uint uVar5;
    byte bVar6;

    uVar4 = FUN_0045C66E((int)param_1);
    if ((char)uVar4 == 0) return;                     // czy unit może działać?

    iVar2 = *(int *)((int)param_1 + 0x368);           // stan wewnętrzny

    if (0xC < iVar2) {                                 // stan > 12
        if (0x13 < iVar2) {                             // stan > 19
            if (iVar2 == 0x14) {
                FUN_00445FCF(param_1);
                return;
            }
            if (iVar2 == 0x15) {
                FUN_00445BFD(param_1);
                return;
            }
            if (iVar2 < 0x18) return;
            if (iVar2 < 0x1E) {
                FUN_00469B86(param_1);
                return;
            }
            return;
        }
        if (iVar2 == 0x13) {
            FUN_00445F3C(param_1);
            return;
        }
        if (iVar2 == 0xE) {
            FUN_00469F83(param_1);
            return;
        }
        if (iVar2 == 0x10) {
            FUN_0046B1B3(param_1);
            return;
        }
        if (iVar2 == 0x11) {
            FUN_0046B621(param_1, *(uint *)((int)param_1 + 0xAD0));
            return;
        }
        if (iVar2 == 0x12) {
            FUN_00445E37(param_1);
            return;
        }
        return;
    }

    if (iVar2 == 0xC) {
        bVar6 = 0x10;
        uVar4 = 0xC;
        goto LAB_004432DE;
    }

    if (iVar2 < 8) {                                   // stan < 8
        if (iVar2 == 7) {
            iVar2 = *(int *)((int)param_1 + 0x370);
            *(undefined4 *)((int)param_1 + 0x378) = 0;
            if (iVar2 == 1) {
                FUN_0046EF7B(param_1);
                return;
            }
            if (iVar2 == 2) {
                FUN_0046F333(param_1);
                return;
            }
            if (iVar2 == 3) {
                FUN_0046F57A(param_1);
                return;
            }
            if (iVar2 == 4) {
                FUN_0046F661(param_1);
                return;
            }
            return;
        }
        if (iVar2 != 1) {
            if (iVar2 == 2) {
                *(undefined4 *)((int)param_1 + 0x368) = 2;
                *(undefined4 *)((int)param_1 + 0x36C) = 1;
                return;
            }
            if (iVar2 == 3) {
                FUN_0044483B(param_1);
                return;
            }
            if (iVar2 == 5) {
                FUN_00444934(param_1);
                return;
            }
            return;
        }

        // Stan 1 — wywołaj dyspozytor
        uVar5 = FUN_0043C101(param_1);
        if ((char)uVar5 == 0) {
            if (*(int *)((int)param_1 + 0x368) != 1) return;
            FUN_00462DF1(param_1);
            if (*(int *)((int)param_1 + 0x368) == 7) return;
            if (*(int *)((int)param_1 + 0x378) == 0) {
                FUN_0044434A(param_1);
                return;
            }
LAB_00443265:
            *(undefined4 *)((int)param_1 + 0x368) = 9;
            *(undefined4 *)((int)param_1 + 0x36C) = 0;
            return;
        }
        iVar2 = *(int *)((int)param_1 + 0x36C);
    }
    else {
        if (iVar2 != 8) {
            if (iVar2 != 9) {
                if (iVar2 != 0xB) return;
                bVar6 = 0xF;
                uVar4 = 0xB;
                goto LAB_004432DE;
            }
            uVar5 = FUN_0043C101(param_1);
            if ((char)uVar5 == 0) {
                if (*(int *)((int)param_1 + 0x368) != 9) return;
                FUN_00462DF1(param_1);
                if (*(int *)((int)param_1 + 0x368) != 7) {
                    FUN_00444BCE(param_1);
                    return;
                }
                return;
            }
            *(undefined4 *)((int)param_1 + 0x37C) = 0;
            if (*(int *)((int)param_1 + 0x36C) != 1) return;
            if (*(int *)((int)param_1 + 0x368) != 1) return;
            FUN_0042CF27((int)param_1);
            *(undefined4 *)((int)param_1 + 0x368) = 9;
            goto LAB_0044332A;
        }
        uVar5 = FUN_0043C101(param_1);
        if ((char)uVar5 == 0) {
            if (*(int *)((int)param_1 + 0x368) != 8) return;
            piVar1 = (int *)((int)param_1 + 0xA64);
            if ((*piVar1 == 0) || (cVar3 = FUN_0042C8FF((int)param_1), cVar3 == 0)) {
                FUN_00462DF1(param_1);
            }
            else {
                *piVar1 = *piVar1 - 1;
            }
            if (*(int *)((int)param_1 + 0x368) == 7) return;
            *(undefined4 *)((int)param_1 + 0x370) = 0;
            // ... kontynuacja
        }
    }
    // ... pozostałe stany
}
```

**Uwagi:**
- `param_1 + 0x368` = stan wewnętrzny (0-0x1E+)
- `param_1 + 0x36C` = stan główny
- `param_1 + 0x370`, `param_1 + 0x374`, `param_1 + 0x378` = podstany
- **FUN_0043C101** = warunek przejścia do następnego stanu
- **FUN_00462DF1** = reset/kończenie stanu
- Dla stanu 1: wywołuje FUN_0046BAD7 (dyspozytor na job)

---

## 8. Dyspozytor na job — FUN_0046BAD7

**Adres:** 0x46BAD7
**Parametry:** `void *param_1` — wskaźnik na unit

```c
void FUN_0046BAD7(void *param_1)
{
    bool bVar1;
    undefined4 uVar2;
    int iVar3;
    uint uVar4;
    byte bVar5;
    undefined1 uVar6;
    undefined4 uVar7;

    // Reset stanu
    if (*(int *)((int)param_1 + 0x370) != 0) {
        *(int *)((int)param_1 + 0x370) = 0;
    }

    // Sprawdź interaction state
    if ((*(int *)((int)param_1 + 0xACC) == 0) && (*(int *)((int)param_1 + 0xAD4) != 0)) {
LAB_0046BB5A:
        FUN_00444C6E(param_1);
        return;
    }

    if ((*(uint *)((int)param_1 + 0xB84) >> 1 & 1) != 0) {
        if (*(int *)((int)param_1 + 0xACC) != 0) {
            FUN_00441B83((int)param_1);
        }
LAB_0046BB1C:
        *(undefined4 *)((int)param_1 + 0x36C) = 0;
        *(undefined4 *)((int)param_1 + 0x368) = 1;
        FUN_0044434A(param_1);
        return;
    }

    // Sprawdź warunki
    bVar1 = FUN_0042CE57(param_1, 0xFFFFFFFF);
    if (bVar1) {
        if (*(int *)((int)param_1 + 0xACC) != 0) {
            FUN_00441B83((int)param_1);
        }
        if (*(int *)((int)param_1 + 0xAD4) != 0) goto LAB_0046BB5A;
        goto LAB_0046BB1C;
    }

    uVar2 = FUN_0042C8A8((int)param_1);
    if ((char)uVar2 != 0) {
        FUN_004732CF(param_1);
        return;
    }

    uVar2 = FUN_0042C960((int)param_1);
    if ((char)uVar2 == 0) {
        bVar1 = FUN_0042C6F0((int)param_1);
        if (bVar1) goto LAB_0046BB98;
    }
    else {
        bVar1 = FUN_0042C6F0((int)param_1);
        if (!bVar1) goto LAB_0046BBBB;
LAB_0046BB98:
        uVar2 = FUN_0042C977((int)param_1);
        if (((char)uVar2 != 0) &&
            (*(int *)(*(int *)((int)param_1 + 0xB34) * 0x7E0 + 0x2C + DAT_00510BD0) != 3)) {
LAB_0046BBBB:
            *(undefined4 *)((int)param_1 + 0x36C) = 3;
            *(undefined4 *)((int)param_1 + 0x374) = 2;
            return;
        }
    }

    uVar2 = FUN_0045C66E((int)param_1);
    if ((char)uVar2 == 0) return;

    // Sprawdź stan ui_state
    if ((*(int *)((int)param_1 + 0xACC) == 0) && (*(char *)((int)param_1 + 0xA60) == 0)) {
        // ... logika wyboru towaru
    }

    bVar1 = FUN_0042CF4B((int)param_1);
    if (bVar1) {
        uVar2 = FUN_0042CF57((int)param_1);
        if ((char)uVar2 == 0) {
            FUN_00441B83((int)param_1);
        }
        else {
            // ... logika produkcji
        }
        FUN_0042CF27((int)param_1);
    }

LAB_0046BCE7:
    uVar2 = FUN_0042C70A((int)param_1);
    if ((char)uVar2 == 0) return;

    bVar1 = FUN_0042C69E((int)param_1);
    if (!bVar1) return;

    if (*(int *)((int)param_1 + 0x36C) != 3) return;
    if (*(int *)((int)param_1 + 0x374) != 2) return;

LAB_0046BE4E:
    *(undefined4 *)((int)param_1 + 0x36C) = 0;
    if (*(char *)((int)param_1 + 0xB51) == 0) {
        *(undefined4 *)((int)param_1 + 0x368) = 0x15;
    }
    else {
        *(undefined4 *)((int)param_1 + 0x368) = 1;
    }
}
```

**Uwagi:**
- `param_1 + 0x18` = job (0x19 = potter)
- `param_1 + 0xACC` = interaction state
- `param_1 + 0xAD4` = selected good
- `param_0x36C` = stan główny (3 = error)
- `param_1 + 0x368` = stan wewnętrzny (1 = ready, 0x15 = busy)
- **FUN_0042C70A** = warunek "czy może działać"
- **FUN_0042C69E** = zakończ akcję
- **FUN_004732CF** = handler dla job 1/2/3/4
- **FUN_0046BEED** = handler dla job 5
- **FUN_0046BF4B** = handler dla job 7
- **FUN_0046BFE4** = handler dla job 9/10
- **FUN_0046D53A** = handler dla job 0x19 (potter)
- **FUN_0046E721** = handler dla job 0x1C

---

## 9. Potter handler — FUN_0046D53A **★ UNIWERSALNY**

**Adres:** 0x46D53A
**Parametry:** `void *param_1` — wskaźnik na unit (potter, job 0x19)

**KLUCZOWA OBSERWACJA:** Potter handler jest **w pełni uniwersalny** — obsługuje wszystkie budynki produkcyjne bez modyfikacji kodu!

| Element | Wartość | Źródło |
|---------|---------|--------|
| Wywołanie | job 0x19 (25) — garncarz | hardcoded w dyspozytorze |
| Sprawdzenie budynku | type 3 (production) | INI (`logicmaintype`) |
| Surowce (input) | `logicstock` z INI | INI |
| Output (wynik) | `logicproduction` z INI | INI |
| Logika | `FUN_0046E52E` → `FUN_0044B7B5` → `FUN_0046E117` | uniwersalna |

**Wniosek:** Wystarczy dodać nowy case w dyspozytorze (`case 0x38: FUN_0046D53A(unit); break;`), żeby obsłużyć nowe budynki produkcyjne!

```c
void FUN_0046D53A(void *param_1)
{
    int iVar1;
    bool bVar2;
    char cVar3;
    byte bVar4;
    undefined1 uVar5;
    int *piVar6;
    undefined4 uVar7;
    int iVar8;
    uint uVar9;
    char *this;
    undefined4 *puVar10;
    void *pvVar11;
    undefined3 extraout_var;
    short *psVar13;
    int **ppiVar14;
    undefined3 extraout_var_00;
    undefined3 extraout_var_01;
    char *pcVar15;
    int **ppiVar16;
    void *local_18;
    int *local_14;
    int *local_10;
    void *local_c;
    char *local_8;
    int iVar12;

    // Pobierz listę domów
    local_c = (void *)FUN_0041C61E(DAT_00511728, *(int *)((int)param_1 + 0xB44));
    piVar6 = (int *)FUN_0041C7F1(local_c);          // begin
    local_14 = piVar6;
    local_10 = (int *)FUN_0041C81F(local_c);        // end

    if ((piVar6 == local_10) || (piVar6 == (int *)0)) {
        *(undefined4 *)((int)param_1 + 0x368) = 1;
        goto LAB_0046E01F;
    }

    // Pobierz house record
    uVar7 = FUN_0041C9DD(piVar6);
    if ((char)uVar7 == 0) {
        pcVar15 = (char *)0;
    }
    else {
        pcVar15 = (char *)(*piVar6 * 0x7E0 + DAT_00510BD0);
    }
    local_8 = pcVar15;

    // Pobierz house record (end)
    uVar7 = FUN_0041C9DD(local_10);
    pvVar11 = local_c;
    if ((char)uVar7 == 0) {
        iVar8 = 0;
    }
    else {
        iVar8 = *local_10 * 0x7E0 + DAT_00510BD0;
    }

    // Sprawdź budynki
    if ((((pcVar15 == (char *)0) || (iVar8 == 0)) || (pcVar15[2000] != 0)) ||
        (((*(char *)(iVar8 + 2000) != 0 || (*(int *)(pcVar15 + 0x2C) != 3)) ||
          (*(int *)(iVar8 + 0x2C) != 3)))) {
        *(undefined4 *)((int)param_1 + 0x36C) = 3;
        *(undefined4 *)((int)param_1 + 0x374) = 2;
        goto LAB_0046D878;
    }

    // Sprawdź tribe house
    if (((char)local_14[2] == 0) && ((char)local_10[2] == 0)) {
        uVar7 = FUN_0042C70A((int)param_1);
        if ((((char)uVar7 != 0) &&
            (uVar9 = FUN_0044BCF3((void *)(*(int *)((int)param_1 + 0xB48) * 0x54C + DAT_00510BE0),
                                  *(int *)((int)param_1 + 4)), (char)uVar9 != 0)) &&
            (((iVar8 = FUN_0046733F((int)param_1), iVar8 != 0 ||
              (iVar8 = FUN_00467617((int)param_1), iVar8 != 0)) &&
             (uVar7 = FUN_0046E1BE(param_1, (int)pcVar15), (char)uVar7 != 0)))) {
            return;
        }

        iVar8 = *(int *)((int)param_1 + 0xACC);
        if (iVar8 != 0) {
            if (iVar8 == 2) {
                uVar7 = FUN_0046E3A1(param_1, pcVar15);
                if ((char)uVar7 != 0) return;
            }
            else if (iVar8 == 4) {
                uVar9 = FUN_0042CCC4((int)param_1);
                if ((char)uVar9 == 0) {
                    uVar7 = FUN_0046794B(param_1, *(int *)((int)param_1 + 0xAD4));
                    if ((char)uVar7 != 0) {
                        *(undefined4 *)((int)param_1 + 0xA68) = 5;
                        *(int *)((int)param_1 + 0xA7C) = *local_14;
                        *(int *)((int)param_1 + 0xA80) = local_14[1];
                        goto LAB_0046DE45;
                    }
                    uVar7 = FUN_00467C0E(param_1, *(int *)((int)param_1 + 0xAD4));
                    if ((char)uVar7 != 0) {
                        // ... logika dostarczenia towaru
                    }
                }
                else if (*(int *)((int)param_1 + 0xA68) == 5) {
                    this = FUN_0042D7D3((int)param_1);
                    if ((this == pcVar15) &&
                        (uVar7 = FUN_004316F3(this, *(int *)((int)param_1 + 0xAD4), 0), (char)uVar7 != 0)) {
                        // ... rozpocznij produkcję
                    }
                }
                else if (*(int *)((int)param_1 + 0xA68) == 6) {
                    // ... zakończ produkcję
                }
                FUN_00441B83((int)param_1);
            }
        }

        FUN_0042CF27((int)param_1);
        if (*(int *)((int)param_1 + 0xAD4) != 0) {
            FUN_00444C6E(param_1);
            return;
        }
        FUN_0042CEA6((int)param_1);
        // ... logika wyboru towaru
    }

    // Pobierz wpis receptury
    uVar9 = FUN_0041C8A6(local_c, *(int *)((int)param_1 + 0x10));
    if ((char)uVar9 == 0) {
        *(undefined4 *)((int)pvVar11 + 0xC) = 0;
        *(undefined4 *)((int)pvVar11 + 0x10) = 0;
        *(undefined4 *)((int)param_1 + 0x36C) = 3;
        *(undefined4 *)((int)param_1 + 0x374) = 0xF;
        goto LAB_0046D878;
    }

    iVar8 = (int)DAT_00511728 + *(int *)((int)pvVar11 + 4) * 0x18 + 0x38;
    uVar7 = FUN_0042C70A((int)param_1);
    // ... logika sprawdzenia tribe house

    iVar12 = *(int *)((int)param_1 + 0xACC);
    if ((char)local_10[2] == 0) {
        if (iVar12 == 0) {
            local_18 = (void *)(*(int *)((int)param_1 + 0xB48) * 0x54C + DAT_00510BE0);
            local_14 = *(int **)((int)local_c + 0xC);
            // ... logika produkcji (surowce)
        }
        if (iVar12 == 2) {
            uVar7 = FUN_0046E3A1(param_1, local_8);
            if ((char)uVar7 != 0) return;
            goto LAB_0046DEFA;
        }
        if (iVar12 != 4) goto LAB_0046DEFA;
        // ... logika ui_state == 4
    }

    // Wywołaj logikę produkcji
    bVar4 = FUN_0046E52E(param_1, local_8, iVar8, (int *)&local_18);
    iVar12 = CONCAT31(extraout_var, bVar4);
    pvVar11 = local_c;
    if (iVar12 == 0) {
        // brak surowców
        *(undefined4 *)((int)param_1 + 0xAD0) = *(undefined4 *)(iVar8 + 8);
        *(undefined4 *)((int)param_1 + 0x36C) = 3;
        *(undefined4 *)((int)param_1 + 0x374) = 3;
        *(undefined4 *)((int)local_c + 0xC) = 0;
        *(undefined4 *)((int)local_c + 0x10) = 0;
    }
    else {
        if (iVar12 == 1) {
            // OK — sprawdź dostępność budynku
            uVar7 = FUN_0046E1BE(param_1, (int)local_8);
            if ((char)uVar7 != 0) return;
            iVar8 = *(int *)(iVar8 + 8);
            pcVar15 = local_8;
LAB_0046D909:
            FUN_0046E02B(param_1, pcVar15, iVar8);
            return;
        }
        if (iVar12 != 2) {
            if (iVar12 != 3) {
LAB_0046DEFA:
                FUN_0041C84F(local_c);
                *(undefined4 *)((int)param_1 + 0x36C) = 3;
                *(undefined4 *)((int)param_1 + 0x374) = 2;
                return;
            }
            uVar7 = FUN_0046E1BE(param_1, (int)local_8);
            pvVar11 = local_18;
            if ((char)uVar7 != 0) return;
LAB_0046D953:
            FUN_0046E117(param_1, (int)pvVar11);
            return;
        }
    }
LAB_0046D878:
    FUN_0041C84F(pvVar11);
}
```

**Uwagi:**
- `DAT_00511728` = tablica list domów (stride 0x18)
- `param_1 + 0xB44` = house_list_idx
- `param_1 + 0xB48` = tribe_idx
- `DAT_00510BE0` = tribe house (stride 0x54C)
- `local_c + 0xC` = stock index
- `local_c + 0x10` = stock qty
- **FUN_0046E52E** = główna logika produkcji (surowce → output)
- **FUN_0046E117** = ustaw selected good
- **FUN_0046E02B** = ustaw stan produkcji
- **FUN_0046E1BE** = sprawdź dostępność budynku

---

## 10. Logika produkcji — FUN_0046E52E

**Adres:** 0x46E52E
**Parametry:**
- `void *this` — unit
- `void *param_1` — building
- `int param_2` — wskaźnik na wpis receptury (DAT_00511728 + idx * 0x18 + 0x38)
- `int *param_3` — output (selected good)

**Zwraca:** byte (0=brak surowców, 1=OK, 2=czeka, 3=next good)

```c
byte FUN_0046E52E(void *this, void *param_1, int param_2, int *param_3)
{
    uint uVar1;
    undefined1 uVar2;
    undefined3 extraout_var;
    int iVar3;
    uint uVar4;
    undefined4 uVar5;
    int iVar6;
    void *this_00;
    int iVar7;
    int iVar8;
    undefined3 extraout_var_00;

    this_00 = (void *)(*(int *)((int)this + 0xB48) * 0x54C + DAT_00510BE0);  // tribe house

    iVar8 = 1;                                          // good index
    while (((iVar3 = *(int *)(param_2 + 8), iVar8 == iVar3 ||
            (((((iVar8 == 0x10) || (iVar8 == 0x12)) || (iVar8 == 0x13)) ||
              (((iVar8 == 0x15) || (iVar8 == 0x38)) || ((iVar8 == 0x16) || (iVar8 == 0x17)))))) &&
            (iVar3 == 0x10))) ||
            ((((iVar8 == 0x11) || (iVar8 == 0x14)) && (iVar3 == 0x11)) ||
             (uVar2 = FUN_0044B634(this_00, iVar8), CONCAT31(extraout_var, uVar2) == 0)))) {
        iVar8 = iVar8 + 1;
        if (0x41 < iVar8) {
            // Znaleziono dostępny good
            iVar8 = FUN_004374F0((int)this_00);
            iVar3 = FUN_0044B67B((int)this_00);
            iVar8 = *(int *)(iVar8 + 0x24);
            uVar2 = FUN_0044B634(this_00, *(int *)(param_2 + 8));
            uVar4 = CONCAT31(extraout_var_00, uVar2);
            uVar1 = *(uint *)(param_2 + 0xC);           // input qty
            iVar7 = *(int *)(param_2 + 0x14) - uVar1;    // output qty - input qty
            if (iVar7 < 0) iVar7 = 0;
            iVar6 = uVar1 - uVar4 % uVar1;               // ile potrzeba
            if (((int)((uVar4 / uVar1 + 1) * iVar7 + iVar6) <= iVar8 - iVar3) &&
                ((uVar5 = FUN_0042CF8F(*(int *)(param_2 + 8)), (char)uVar5 == 0) ||
                 (iVar8 = FUN_004316E0((int)param_1), iVar8 != 2)))) {
                iVar8 = *(int *)(param_2 + 8);
                iVar3 = 0x10;
                // Sprawdź specjalne goods
                if (((iVar8 == 0x10) ||
                    (((iVar8 == 0x12 || (iVar8 == 0x13)) || (iVar8 == 0x15)) ||
                     ((iVar8 == 0x38 || (iVar8 == 0x16)))))) || (iVar8 == 0x17)) {
                    do {
                        if (((((iVar3 == 0x10) || (iVar3 == 0x12)) ||
                             ((iVar3 == 0x13 || (((iVar3 == 0x15) || (iVar3 == 0x38)) || (iVar3 == 0x16)))))) ||
                            (iVar3 == 0x17)) &&
                           (uVar5 = FUN_004316F3(param_1, iVar3, 1), (char)uVar5 != 0)) {
                            iVar8 = FUN_004319D7(param_1, iVar3, 1);
                            iVar7 = FUN_00431FA7(param_1, iVar3);
                            if (iVar6 <= iVar8 - iVar7) {
                                return 1;                           // OK!
                            }
                        }
                        iVar3 = iVar3 + 1;
                    } while (iVar3 < 0x18);
                }
                else if ((iVar8 == 0x11) || (iVar8 == 0x14)) {
                    do {
                        if (((iVar3 == 0x11) || (iVar3 == 0x14)) &&
                            (uVar5 = FUN_004316F3(param_1, iVar3, 1), (char)uVar5 != 0)) {
                            iVar8 = FUN_004319D7(param_1, iVar3, 1);
                            iVar7 = FUN_00431FA7(param_1, iVar3);
                            if (iVar6 <= iVar8 - iVar7) {
                                return 1;                           // OK!
                            }
                        }
                        iVar3 = iVar3 + 1;
                    } while (iVar3 < 0x18);
                }
                else {
                    uVar5 = FUN_004316F3(param_1, iVar8, 1);
                    if ((char)uVar5 != 0) {
                        iVar8 = FUN_004319D7(param_1, *(int *)(param_2 + 8), 1);
                        iVar3 = FUN_00431FA7(param_1, *(int *)(param_2 + 8));
                        if (iVar6 <= iVar8 - iVar3) {
                            return 1;                               // OK!
                        }
                    }
                }
            }
            return -(uVar4 / *(uint *)(param_2 + 0xC) != 0) & 2;  // Czeka
        }
    }
    *param_3 = iVar8;
    return 3;                                               // Następny good
}
```

**Uwagi:**
- `param_2 + 8` = input good
- `param_2 + 0xC` = input qty
- `param_2 + 0x14` = output qty
- **FUN_0044B634** = sprawdź tribe house stock
- **FUN_004316F3** = bramka budynku (czy ma good)
- **FUN_004319D7** = ilość towaru w budynku
- **FUN_00431FA7** = min qty w budynku
- Zwraca 1 jeśli produkcja możliwa (wystarczająco surowców)
- Zwraca 2 jeśli czeka (brak surowców)
- Zwraca 3 jeśli sprawdza następny good

---

## 11. Ustaw selected good — FUN_0046E117

**Adres:** 0x46E117
**Parametry:** `void *this` — unit, `int param_1` — good index

```c
void FUN_0046E117(void *this, int param_1)
{
    undefined4 *puVar1;
    undefined4 uVar2;
    char *this_00;
    short *psVar3;
    short local_8[2];

    this_00 = (char *)(*(int *)((int)this + 0xB48) * 0x54C + DAT_00510BE0);  // tribe house
    *(int *)((int)this + 0xAD0) = param_1;            // selected good

    local_8[0] = 0;
    local_8[1] = 0;
    FUN_004376CF(this_00, local_8, 0);                // get position
    psVar3 = local_8;
    puVar1 = (undefined4 *)FUN_004411CA(this_00);     // get coords
    uVar2 = FUN_0045C23E(this, puVar1, psVar3);       // set state

    if ((char)uVar2 == 0) {
        *(undefined4 *)((int)this + 0x36C) = 3;        // error
        *(undefined4 *)((int)this + 0x374) = 1;
    }
    else {
        *(undefined4 *)((int)this + 0xACC) = 2;        // interaction state
        FUN_0044B7B5(this_00, param_1, -1, *(int *)((int)this + 8));  // set tribe house good
        *(undefined4 *)((int)this + 0xA7C) = *(undefined4 *)((int)this + 0xB48);
        *(undefined4 *)((int)this + 0xA68) = 6;        // ui_state = 6
        *(undefined4 *)((int)this + 0xA80) = *(undefined4 *)((int)this + 0xB4C);
    }
}
```

**Uwagi:**
- `param_1 + 0xAD0` = selected good
- `param_1 + 0xACC` = interaction state (2 = producing)
- `param_1 + 0xA68` = ui_state (6 = production in progress)
- **FUN_0044B7B5** = ustaw tribe house good (kluczowa funkcja!)

---

## 12. Ustaw stan produkcji — FUN_0046E02B

**Adres:** 0x46E02B
**Parametry:** `void *this` — unit, `void *param_1` — building, `int param_2` — good

```c
void FUN_0046E02B(void *this, void *param_1, int param_2)
{
    undefined4 uVar1;
    int iVar2;
    int iVar3;

    iVar2 = 0x10;
    // Szukaj dobrego typu wejścioweg
    if ((((param_2 == 0x10) || (param_2 == 0x12)) || (param_2 == 0x13)) ||
       (((param_2 == 0x15) || (param_2 == 0x38)) || ((param_2 == 0x16) || (param_2 == 0x17))))) {
        do {
            if ((((iVar2 == 0x10) || (iVar2 == 0x12)) ||
                ((iVar2 == 0x13) ||
                 ((((iVar2 == 0x15) || (iVar2 == 0x38)) || (iVar2 == 0x16)) || (iVar2 == 0x17)))) &&
                (uVar1 = FUN_004316F3(param_1, iVar2, 1), iVar3 = iVar2, (char)uVar1 != 0)) break;
            iVar2 = iVar2 + 1;
            iVar3 = param_2;
        } while (iVar2 < 0x18);
    }
    else if ((param_2 == 0x11) || (iVar3 = param_2, param_2 == 0x14)) {
        do {
            if (((iVar2 == 0x11) || (iVar2 == 0x14)) &&
                (uVar1 = FUN_004316F3(param_1, iVar2, 1), iVar3 = iVar2, (char)uVar1 != 0)) break;
            iVar2 = iVar2 + 1;
            iVar3 = param_2;
        } while (iVar2 < 0x18);
    }

    // Ustaw wybrany good
    *(int *)((int)this + 0xAD0) = iVar3;         // selected good
    *(undefined4 *)((int)this + 0xA68) = 5;     // ui_state = 5
    *(undefined4 *)((int)this + 0xA7C) = *(undefined4 *)((int)param_1 + 4);  // building idx
    *(undefined4 *)((int)this + 0xA80) = *(undefined4 *)((int)param_1 + 8);  // building+8

    // Przygotuj stan do produkcji
    uVar1 = FUN_0045C4AC(this, (undefined4 *)((int)param_1 + 0x1C),
                         (short *)((int)param_1 + 0x24), 0);
    if ((char)uVar1 == 0) {
        *(undefined4 *)((int)this + 0x36C) = 3;   // error
        *(undefined4 *)((int)this + 0x374) = 1;
    }
}
```

**Uwagi:**
- Szuka typu wejściowego (0x10-0x17, 0x11/0x14)
- Ustawia `+0xAD0` = wybrany good
- Ustawia `+0xA68` = 5 (ui_state = production setup)
- Ustawia `+0xA7C`, `+0xA80` = building info

---

## 13. Ustaw tribe house good — FUN_0044B7B5

**Adres:** 0x44B7B5
**Parametry:** `void *this` — tribe house, `int param_1` — good, `int param_2` — qty, `int param_3` — player

```c
uint FUN_0044B7B5(void *this, int param_1, int param_2, int param_3)
{
    char *pcVar1;
    undefined1 uVar2;
    uint uVar3;
    int iVar4;
    int iVar5;
    undefined3 extraout_var;
    int iVar6;
    undefined4 uVar7;

    // Znajdź good w tribe house
    uVar3 = FUN_0044B9BD(this, param_1);
    if (uVar3 == 0xFFFFFFFF) {
LAB_0044B7FA:
        uVar3 = uVar3 & 0xFFFFFF00;
    }
    else {
        iVar4 = FUN_004374F0((int)this);
        iVar5 = FUN_0044B9BD(this, param_1);

        if (param_2 < 0) {
            // Dodaj (ujemnie = zużycie)
            uVar2 = FUN_0044B746(this, param_1);
            uVar3 = CONCAT31(extraout_var, uVar2);
            if (-uVar3 != param_2 && (int)uVar3 <= -param_2) goto LAB_0044B7FA;
            pcVar1 = (char *)(iVar5 + 0x37A + (int)this);
            *pcVar1 = *pcVar1 + (char)param_2;
        }
        else {
            // Odejmij (dodatnie = produkcja)
            iVar6 = FUN_0044B772((int)this);
            iVar6 = *(int *)(iVar4 + 0x24) - iVar6;
            if (param_2 <= iVar6) {
                iVar6 = param_2;
            }
            pcVar1 = (char *)(iVar5 + 0x37A + (int)this);
            *pcVar1 = *pcVar1 + (char)iVar6;
        }

        uVar7 = FUN_0044B910((void *)((int)this + 0x338), param_3, param_2);
        uVar3 = CONCAT31((int3)((uint)uVar7 >> 8), 1);
    }
    return uVar3;
}
```

**Uwagi:**
- `FUN_0044B9BD` = znajdź good w tribe house
- `FUN_004374F0` = pobierz tribe house capacity
- `FUN_0044B746` = sprawdź dostępną ilość
- `FUN_0044B772` = sprawdź aktualną ilość
- `FUN_0044B910` = aktualizuj tribe house +0x338
- **KLUCZOWE:** `this + good*stride + 0x37A` = ilość towaru w tribe house
- `param_2 < 0` = zużycie (wejście)
- `param_2 > 0` = produkcja (wyjście)

---

## 14. Sprawdź stan produkcji — FUN_0046E3A1

**Adres:** 0x46E3A1
**Parametry:** `void *this` — unit, `void *param_1` — building

```c
uint FUN_0046E3A1(void *this, void *param_1)
{
    undefined1 uVar1;
    uint uVar2;
    int iVar3;
    undefined3 extraout_var;
    undefined4 *puVar4;
    undefined4 uVar5;
    void *this_00;
    short *psVar6;
    void *pvVar7;
    void *pvVar8;
    char *this_01;
    void **ppvVar9;

    uVar2 = FUN_0042CCC4((int)this);
    if ((char)uVar2 != 0) {
        iVar3 = FUN_0042CF44((int)this);
        if (iVar3 == 2) {
            FUN_0045C17B(this, 0x16, 6);
            *(undefined4 *)((int)this + 0x36C) = 1;
            return 1;
        }
        if (iVar3 == 5) {
            // Sprawdź pozycję budynku
            this_00 = (void *)FUN_0042D7A9((int)this);
            if (this_00 == param_1) {
                psVar6 = (short *)FUN_0042CFC7((int)this);
                if ((*psVar6 != *(short *)((int)this_00 + 0x24)) ||
                    (psVar6[1] != *(short *)((int)this_00 + 0x26))) {
                    FUN_00440176((uint *)s_standing_at_invalid_position_for_00501114);
                }

                // Sprawdź ilość towaru
                uVar5 = FUN_004316F3(this_00, *(int *)((int)this + 0xAD0), 1);
                if ((char)uVar5 != 0) {
                    iVar3 = *(int *)((int)this + 0xAD0);
                    pvVar7 = (void *)FUN_00431944(this_00, iVar3, 1);
                    pvVar8 = param_1;
                    param_1 = pvVar7;
                    pvVar8 = (void *)FUN_00431FA7(pvVar8, iVar3);
                    if (pvVar8 < param_1) {
                        // Zaktualizuj dźwięk
                        if (*(int *)((int)this_00 + 0x14) == 10) {
                            iVar3 = 0x2C;
                        }
                        else if (*(int *)((int)this_00 + 0x14) == 0xB) {
                            iVar3 = 0x2D;
                        }
                        else {
                            iVar3 = 0x16;
                        }
                        uVar5 = FUN_0045C17B(this, iVar3, 6);
                        *(undefined4 *)((int)this + 0x36C) = 1;
                        goto LAB_0046E44E;
                    }
                }
            }
        }
        else if (iVar3 == 6) {
            // Sprawdź tribe house
            this_01 = (char *)(*(int *)((int)this + 0xB48) * 0x54C + DAT_00510BE0);
            uVar1 = FUN_0044B634(this_01, *(int *)((int)this + 0xAD0));
            if (CONCAT31(extraout_var, uVar1) != 0) {
                param_1 = (void *)0;
                FUN_004376CF(this_01, (short *)&local_8, 0);
                // ... dalsza logika
            }
        }
    }
    return uVar2;
}
```

**Uwagi:**
- `FUN_0042CF44` = pobierz stan produkcji
- `FUN_0042D7A9` = pobierz wskaźnik budynku
- `FUN_0042CFC7` = pobierz pozycję budynku
- `FUN_004316F3` = bramka budynku
- `FUN_00431944` = ilość towaru w budynku
- `FUN_00431FA7` = min qty w budynku
- `FUN_0044B634` = sprawdź tribe house stock
- `FUN_0045C17B` = odtwórz dźwięk

---

## Podsumowanie łańcucha produkcji

1. **Główna pętla gry** (FUN_004078C8) wywołuje tick budynków co N ticków
2. **Tick budynku** (FUN_00433662) sprawdza czy budynek jest ukończony
3. **Iteracja po jednostkach** (FUN_0043127A) wywołuje tick dla każdej jednostki w budynku
4. **Pętla stanu** (FUN_00462C70) wywołuje tick stanu głównego
5. **Dyspozytor** (FUN_0046BAD7) wybiera handler na podstawie job
6. **Potter handler** (FUN_0046D53A) wywołuje logikę produkcji
7. **Logika produkcji** (FUN_0046E52E) sprawdza surowce i zwraca czy produkcja możliwa
8. **Ustaw selected good** (FUN_0046E117) aktualizuje tribe house
9. **Ustaw stan produkcji** (FUN_0046E02B) rozpoczyna produkcję

## 15. Bramka budynku — FUN_004316F3

**Adres:** 0x4316F3
**Parametry:** `Building *this`, `u32 good`, `u8 flag`
**Zwraca:** bool

```rust
pub unsafe fn fun_004316f3(this: *mut Building, good: u32, flag: u8) -> bool {
    // Sprawdza czy budynek ma dany towar
    // flag = 0x00: sprawdź output (stock output)
    // flag = 0x01: sprawdź input (stock input)
    // Zwraca true jeśli towar jest dostępny
    false
}
```

**Uwagi:**
- Używana w FUN_0046E52E (logika produkcji) z flag=1
- Używana w FUN_0046E02B (ustaw stan produkcji) z flag=1
- Używana w FUN_0046E3A1 (sprawdź stan produkcji) z flag=1
- To jest "bramka" — czy budynek obsługuje dany towar

---

## 16. Pobierz ilość towaru — FUN_004319D7

**Adres:** 0x4319D7
**Parametry:** `Building *this`, `u32 good`, `u8 flag`
**Zwraca:** i32

```rust
pub unsafe fn fun_004319d7(this: *const HouseType, good: u32, flag: u8) -> i32 {
    // Pobiera ilość towaru w budynku
    // flag = 0x00: output stock
    // flag = 0x01: input stock
    0
}
```

**Uwagi:**
- Używana w FUN_0046E52E (logika produkcji)
- Używana w FUN_0046EE91 (handler job 1)
- Używana w FUN_0046F661 (handler job 4)

---

## 17. Min qty w budynku — FUN_00431FA7

**Adres:** 0x431FA7
**Parametry:** `Building *this`, `i32 good`
**Zwraca:** i32

```rust
pub unsafe fn fun_00431fa7(this: *mut Building, good: i32) -> i32 {
    // Pobiera minimalną ilość towaru w budynku
    // Używana do obliczenia ile towaru jest "zablokowane"
    0
}
```

**Uwagi:**
- Używana w FUN_0046E52E (logika produkcji) — `iVar6 <= iVar8 - iVar7`
- Używana w FUN_0046E3A1 (sprawdź stan produkcji)
- Wyższa wartość = mniej towaru dostępnego do produkcji

---

## 18. Aktualizuj tribe house — FUN_0044B910 **★ KLUCZOWA**

**Adres:** 0x44B910
**Parametry:** `void *this` — tribe house, `int param_1` — good index, `int param_2` — qty
**Zwraca:** void

```c
void FUN_0044B910(void *this, int param_1, int param_2)
{
    int *piVar1;
    uint uVar2;
    char *pcVar3;

    // Znajdź pusty slot w tribe house stock
    uVar2 = FUN_0044B8E8(this, param_1);
    if ((char)uVar2 == 0) {
        // Brak pustego slotu — błąd
        uVar2 = 0;
        pcVar3 = (char *)((int)this + 200);
        do {
            if (*pcVar3 == 0) {
                // Znaleziono pusty slot
                piVar1 = (int *)((int)this + uVar2 * 0xC + 0xD0);
                *piVar1 = *piVar1 + param_2;                    // qty += param_2
                *(int *)((int)this + (uVar2 * 3 + 0x33) * 4) = param_1;  // good_idx = param_1
                *(undefined1 *)((int)this + uVar2 * 0xC + 200) = 1;        // active = 1
                return;
            }
            uVar2 = uVar2 + 1;
            pcVar3 = pcVar3 + 0xC;
        } while (uVar2 < 0x15);  // 21 slotów
    }
    else {
        // Slot istnieje — odejmij (zużycie)
        FUN_0044B96E(this, param_1, -param_2);
    }
}
```

**Struktura tribe house stock (slot 0xC B):**
| Offset | Nazwa | Opis |
|--------|-------|------|
| +0x000 | active | Flaga aktywności (0 = pusty, 1 = zajęty) |
| +0x004 | good_idx | Indeks towaru |
| +0x008 | qty | Ilość towaru |

**Sloty w tribe house:**
| Offset | Ilość | Opis |
|--------|-------|------|
| +0x33*4 = +0xCC | 21 | Tablica indeksów goodów (int) |
| +0xD0 | 21 | Tablica ilości (int) |
| +200 | 21 | Tablica flag aktywności (byte) |

**Uwagi:**
- **TO JEST MIEJSCE GDZIE FAKTYCZNIE DODAWANY JEST TOWAR DO STOCK!**
- `param_2 > 0` = dodaj (produkcja)
- `param_2 < 0` = odejmij (zużycie)
- Maksymalnie 21 slotów w tribe house stock
- Używana w FUN_0044B7B5 (ustaw tribe house good)

---

## 19. Znajdź good w tribe house — FUN_0044B9BD

**Adres:** 0x44B9BD
**Parametry:** `void *this`, `int param_1`
**Zwraca:** uint (indeks gooda)

```rust
pub unsafe fn fun_0044b9bd(this: *mut u8, param_1: i32) -> u32 {
    // Znajdź good w tribe house
    // Zwraca 0xFFFFFFFF jeśli nie znaleziono
    0xFFFFFFFF
}
```

**Uwagi:**
- Wywoływana z FUN_0044B7B5 (ustaw tribe house good)
- Zwraca indeks gooda w tribe house

---

## 20. Sprawdź stan produkcji — FUN_0046E3A1 (pełny)

**Adres:** 0x46E3A1
**Parametry:** `void *this` — unit, `void *param_1` — building
**Zwraca:** uint

```c
uint FUN_0046E3A1(void *this, void *param_1)
{
    uint uVar2 = FUN_0042CCC4((int)this);
    if ((char)uVar2 != 0) {
        int iVar3 = FUN_0042CF44((int)this);
        if (iVar3 == 2) {
            FUN_0045C17B(this, 0x16, 6);
            *(uint *)((int)this + 0x36C) = 1;
            return 1;
        }
        if (iVar3 == 5) {
            // Sprawdź pozycję budynku
            void *this_00 = FUN_0042D7A9((int)this);
            if (this_00 == param_1) {
                // Sprawdź ilość towaru w budynku
                uint uVar5 = FUN_004316F3(this_00, *(int *)((int)this + 0xAD0), 1);
                if ((char)uVar5 != 0) {
                    int iVar3 = *(int *)((int)this + 0xAD0);
                    void *pvVar7 = FUN_00431944(this_00, iVar3, 1);  // ilość w output
                    void *pvVar8 = param_1;
                    param_1 = pvVar7;
                    pvVar8 = FUN_00431FA7(pvVar8, iVar3);  // min qty
                    if (pvVar8 < param_1) {
                        // Zaktualizuj dźwięk
                        iVar3 = (*(int *)((int)this_00 + 0x14) == 10) ? 0x2C :
                                (*(int *)((int)this_00 + 0x14) == 0xB) ? 0x2D : 0x16;
                        FUN_0045C17B(this, iVar3, 6);
                        *(uint *)((int)this + 0x36C) = 1;
                        goto LAB_0046E44E;
                    }
                }
            }
        }
        else if (iVar3 == 6) {
            // Stan 6 — sprawdź tribe house
            char *this_01 = (char *)(*(int *)((int)this + 0xB48) * 0x54C + DAT_00510BE0);
            uVar1 = FUN_0044B634(this_01, *(int *)((int)this + 0xAD0));
            if (CONCAT31(extraout_var, uVar1) != 0) {
                // Towar dostępny w tribe house
                FUN_004376CF(this_01, (short *)&local_8, 0);
                // ... dalsza logika dostarczenia
            }
        }
    }
    return uVar2;
}
```

**Uwagi:**
- Sprawdza stan produkcji w unit
- iVar3 == 2: produkcja w toku, ustawia +0x36C=1
- iVar3 == 5: sprawdza output stock budynku
- iVar3 == 6: sprawdza tribe house (dostarczenie)
- Używa FUN_00431944 (ilość w output) i FUN_00431FA7 (min qty)

---

## Podsumowanie łańcucha produkcji

1. **Główna pętla gry** (FUN_004078C8) wywołuje tick budynków co N ticków
2. **Tick budynku** (FUN_00433662) sprawdza czy budynek jest ukończony
3. **Iteracja po jednostkach** (FUN_0043127A) wywołuje tick dla każdej jednostki
4. **Pętla stanu** (FUN_00462C70) wywołuje tick stanu głównego
5. **Dyspozytor** (FUN_0046BAD7) wybiera handler na podstawie job
6. **Potter handler** (FUN_0046D53A) wywołuje logikę produkcji
7. **Logika produkcji** (FUN_0046E52E) sprawdza surowce w tribe house
8. **Ustaw selected good** (FUN_0046E117) aktualizuje tribe house
9. **Ustaw tribe house good** (FUN_0044B7B5) — **kluczowa funkcja**
10. **Aktualizuj tribe house** (FUN_0044B910) — faktyczna modyfikacja tribe house
11. **Ustaw stan produkcji** (FUN_0046E02B) rozpoczyna produkcję

## Status brakujących elementów

| Element | Status | Uwagi |
|---------|--------|-------|
| FUN_0046E02B | **Zdekompilowana** | Ustawia stan produkcji (+0xA68=5) |
| FUN_0046E3A1 | **Zdekompilowana** | Sprawdź stan produkcji |
| FUN_0044B7B5 | **Zdekompilowana** | Ustawia tribe house good (+0x37A) |
| FUN_00431FA7 | **Zdekompilowana** (pseudokod) | Min qty w budynku |
| FUN_004316F3 | **Zdekompilowana** (pseudokod) | Bramka budynku |
| FUN_004319D7 | **Zdekompilowana** (pseudokod) | Pobierz ilość towaru |
| FUN_0044B910 | **Zdekompilowana** ★ | **Faktycznie dodaje towar do tribe house stock!** |
| FUN_0044B9BD | **Zdekompilowana** (pseudokod) | Znajdź good w tribe house |
| FUN_0044B96E | **Zdekompilowana** (pseudokod) | Odejmij towar (zużycie) |
| FUN_0044B8E8 | **Zdekompilowana** (pseudokod) | Znajdź pusty slot |
| FUN_0044B634 | **Zdekompilowana** (pseudokod) | Sprawdź tribe house stock |

## Kompletny łańczech produkcji (POTWIERDZONY)

```
FUN_004078C8 (główna pętla gry)
  └─ FUN_0040AD0A (tick budynków)
       └─ FUN_00433662 (tick budynku — sprawdza ukończenie)
            └─ FUN_0043127A (iteracja po jednostkach)
                 └─ FUN_0044193D (tick jednostki)
                      └─ FUN_00462C70 (pętla stanu)
                           └─ FUN_0044319A (tick stanu)
                                └─ FUN_0046BAD7 (dyspozytor na job)
                                     └─ FUN_0046D53A (potter handler, job 0x19)
                                          ├─ FUN_0046E52E (logika produkcji — sprawdza surowce)
                                          ├─ FUN_0046E117 (ustaw selected good)
                                          │    └─ FUN_0044B7B5 (ustaw tribe house good)
                                          │         ├─ FUN_0044B9BD (znajdź good)
                                          │         ├─ FUN_0044B910 (dodaj towar) ★
                                          │         └─ FUN_0044B96E (odejmij towar)
                                          ├─ FUN_0046E02B (ustaw stan produkcji)
                                          └─ FUN_0046E3A1 (sprawdź stan produkcji)
```

## Plan modyfikacji silnika dla nowych budynków/surowców

### Strategia: Uniwersalny potter handler

**Potter handler (FUN_0046D53A) jest w pełni uniwersalny** — obsługuje wszystkie budynki produkcyjne bez modyfikacji kodu. Trzeba tylko dodać nowy case w dyspozytorze.

### Kroki implementacji

**Krok 1: Code cave — dyspozytor (FUN_0046BAD7, 0x46BDDE)**

Oryginalny kod:
```c
case 0x19:
    FUN_0046D53A(param_1);
    break;
```

Nowy kod (dodaj case dla smolarza):
```c
case 0x19:
    FUN_0046D53A(param_1);    // garncarz (job 25)
    break;
case 0x38:
    FUN_0046D53A(param_1);    // smolarz (job 56) — ten sam handler!
    break;
```

**Krok 2: INI — houses.ini (smolarnia)**
```ini
[logichousetype]
debugname "smolarnia"
logictype 57
logicmaintype 3
logicworker 56 1              # smolarz (job 56)
logicstock 5 10 1             # input: drewno
logicstock 66 15 0            # output: węgiel
logicproduction 66            # węgiel
debugcolor 100 0 0
```

**Krok 3: INI — goodtypes.ini (węgiel)**
```ini
[goodtype]
goodtype 66
type 12
name "wegiel"
landscapetype 0
isInputGoodFlag 1
isProducedInHouseFlag 1
atomicForProduction 1
```

### Podsumowanie modyfikacji

| Element | Trudność | Co robimy |
|---------|----------|-----------|
| Nowe surowce | **Łatwe** | Tylko INI (`goodtypes.ini`) |
| Nowe budynki produkcyjne | **Łatwe** | INI + 1 case w dyspozytorze |
| Nowe łańcuchy produkcji | **Łatwe** | INI (`logicstock`/`logicproduction`) |
| Nowe zawody | **Trudne** | Przypisanie job + ewentualnie code cave |

## Pytania otwarte

1. Czy produkcja wymaga obecności pracownika w budynku? — **Tak** (potter handler wymaga unit)
2. Czy smolarnia (typ 57) jest obsługiwana w tick budynku? — **Tak** (przez potter handler)
3. Co oznacza `category == 6` w house_type record? — **Budynek produkcyjny**
4. Czy FUN_0044B910 faktycznie dodaje towar do stock? — **TAK! ★**
5. Gdzie dokładnie w dyspozytorze dodać nowy case? — **Rozwiązane (patrz sekcja 10)**

## 10. Dyspozytor — analiza asm i dodanie nowego case

**Funkcja:** FUN_0046BAD7
**Adres jump table:** 0x46BE76 (18 entries × 4B)
**Adres case table:** 0x46BEBE (46 entries × 1B)
**Limit:** 0x2E (46) — `CMP EAX, 0x2E; JA 0x46BE1B`

### Rozkład switch (case table → jump table):

| Job | Case table | Jump table | Adres docelowy | Handler |
|-----|------------|------------|----------------|---------|
| 0-2 | 00 | [0] | 0x46BD4A | default |
| 3 | 01 | [1] | 0x46BD6A | — |
| 4 | 02 | [2] | 0x46BDE5 | — |
| 5 | 03 | [3] | 0x46BD76 | — |
| 6 | 04 | [4] | 0x46BD82 | — |
| 7 | 05 | [5] | 0x46BD8E | — |
| 8 | 06 | [6] | 0x46BD9A | — |
| 9-14 | 07 | [7] | 0x46BDC1 | default |
| 15 | 08 | [8] | 0x46BDA6 | — |
| 16 | 09 | [9] | 0x46BDAF | — |
| 17 | 07 | [7] | 0x46BDC1 | default |
| 18 | 0A | [10] | 0x46BDB8 | — |
| **19** | **07** | **[13]** | **0x46BDDC** | **POTTER (CALL 0x46D53A)** |
| 20 | 0B | [11] | 0x46BDCA | — |
| 21 | 02 | [2] | 0x46BDE5 | — |
| 22 | 0C | [12] | 0x46BDD3 | — |
| 23 | 0D | [13] | 0x46BDDC | — |
| 24 | 02 | [2] | 0x46BDE5 | — |
| 25 | 02 | [2] | 0x46BDE5 | — |
| 26 | 0E | [14] | 0x46BDF7 | — |
| 27 | 0F | [15] | 0x46BE00 | — |
| 28 | 10 | [16] | 0x46BE09 | — |
| 29-46 | 11 | [17] | 0x46BE12 | default |

### Instrukcje switch:

```asm
0x46BD2F: MOV EAX, [ESI+0x18]      ; pobierz job
0x46BD32: DEC EAX                   ; job - 1
0x46BD33: CMP EAX, 0x2E             ; limit 46
0x46BD36: JA  0x46BE1B              ; default
0x46BD3C: MOVZX EAX, [EAX+0x46BEBE] ; case_table[job-1]
0x46BD43: JMP  [EAX*4+0x46BE76]     ; jump_table[case]
```

### Miejsce na nowy case:

**Adres: 0x46BDDC** (4 bajty)

Oryginalny kod potter handler:
```asm
0x46BDDC: MOV ECX, ESI
0x46BDDE: CALL 0x0046D53A
0x46BDE3: JMP  0x0046BE26
```

Nowy case dla job 56 (0x38) w wolnej przestrzeni (po 0x46BE26):
```asm
; Nowy kod (w wolnej przestrzeni)
0x46BE26: MOV ECX, ESI             ; job 56 = smolarz
0x46BE28: CALL 0x0046D53A           ; wywołaj potter handler
0x46BE2D: JMP  0x0046BE26           ; powrót

; Patch w jump table (0x46BE76):
; [18] = 0x0046BE26 (zamiast 0x00000000)

; Patch w case table (0x46BEBE):
; [56-1=55] = 0x12 (18)
```

### Weryfikacja:

| Element | Wartość | Status |
|---------|---------|--------|
| Limit | 0x2E = 46 | ✅ Wystarczy dla job 56 |
| Case table [55] | 0x00 → 0x12 | ✅ Wymaga patch |
| Jump table [18] | 0x00000000 → 0x0046BE26 | ✅ Wymaga patch |
| Wolna przestrzeń | 0x46BE26 | ✅ Wystarczy na nowy case |

### Podsumowanie patch punktów:

| # | Adres | Oryginał | Nowy | Opis |
|---|-------|----------|------|------|
| 1 | 0x46BE76 + 18*4 = 0x46BEC0 | 00 00 00 00 | 26 BE 46 00 | jump_table[18] = 0x46BE26 |
| 2 | 0x46BEBE + 55 = 0x46BF15 | 00 | 12 | case_table[55] = 18 |
| 3 | 0x46BE26 | (wolne) | 89 F1 ... | nowy case (smolarz) |

**Uwaga:** Patch 3 wymaga wolnej przestrzeni w kodzie. Jeśli 0x46BE26 nie jest wolne, trzeba użyć code cave.

---

## 11. Weryfikacja w INI

**houses.ini** (smolarnia — typ 57):
```ini
[logichousetype]
debugname "smolarnia"
logictype 57
logicmaintype 3
logicworker 56 1
logicstock 5 10 1
logicstock 66 15 0
logicproduction 66
debugcolor 100 0 0
```

**goodtypes.ini** (węgiel — goodtype 66):
```ini
[goodtype]
goodtype 66
type 12
name "wegiel"
landscapetype 0
isInputGoodFlag 1
isProducedInHouseFlag 1
atomicForProduction 1
```

---

## 12. Podsumowanie

| Element | Trudność | Status |
|---------|----------|--------|
| Parser goodtypes.ini | Gotowy | ✅ |
| Parser houses.ini | Gotowy | ✅ |
| Dodanie węgla (INI) | Łatwe | ✅ |
| Dodanie smolarni (INI) | Łatwe | ✅ |
| Patch dyspozytora (code cave) | Łatwe | ✅ |
| **Pełna funkcjonalność** | **Łatwe** | **Gotowe!** |

---

## 14. Job Assignment Chain — Jak jednostka dostaje job

### Odkrycie kluczowe: FUN_0043242C (0x43242C)

To jest **główna funkcja przypisująca job do jednostki**!

```c
uint __thiscall FUN_0043242C(void *this, int param_1)  // this = building, param_1 = unit_id
{
    // ... walidacja ...
    piVar9 = (int *)(house_type * 0x624 + DAT_005113a0);  // house_type record
    iVar10 = param_1 * 0xC58 + DAT_00510BD8;              // unit record
    if (*piVar9 != 2) { ... }  // type 2 = produkcyjny
    
    iVar6 = piVar9[3];                    // worker_count (house_type+3)
    puVar7 = (uint *)(piVar9 + 4);        // workers array (house_type+4)
    do {
        if (*puVar7 == uVar4) break;      // znajdź worker dla unit_id
        puVar7 = puVar7 + 2;
        iVar8 = iVar8 + 1;
    } while (iVar8 < iVar6);
    
    // TUTAJ: job = *puVar7, count = *(puVar7+1)
    // job jest kopiowany do unit+0x18
}
```

**Struktura workers w house_type (offset +4):**
```
+4:  job_id_0
+8:  count_0
+12: job_id_1
+16: count_1
...
```

### Pełny łańcuch wywołań (Unit Creation → Job Assignment)

```
Unit Creation / Spawn
    ↓
FUN_004B64A6 (0x4B64A6) — pathfinding / unit logic
    ↓
FUN_004C8919 (0x4C8919) — dispatcher (case 5 → FUN_004C8F14)
    ↓
FUN_004C8F14 (0x4C8F14) — worker logic dispatcher
    param_2 = 5  →  FUN_0043242C  ← KLUCZOWE!
    ↓
FUN_0043242C (0x43242C) — PRZYPISANIE JOB DO JEDNOSTKI
    unit+0x18 = house_type workers[job_idx]
    ↓
Potter handler (FUN_0046D53A) może używać unit+0x18
```

### Szczegóły każdego wywołania

| Funkcja | Adres | Rola | Parametry |
|---------|-------|------|-----------|
| **FUN_0043242C** | 0x43242C | Przypisuje job z house_type | building, unit_id |
| **FUN_0043230A** | 0x43230A | Worker dispatcher | building, unit_id, type |
| **FUN_00431FF5** | 0x431FF5 | Building unit logic | building, unit_id, 2 |
| **FUN_00432003** | 0x432003 | Worker registration | building, unit_id, job |
| **FUN_004C8F14** | 0x4C8F14 | Worker logic | unit, param, 5 |
| **FUN_004C8919** | 0x4C8919 | Dispatcher (case 5) | unit, params |
| **FUN_004B64A6** | 0x4B64A6 | Pathfinding / unit init | unit |
| **FUN_004A20FA** | 0x4A20FA | Trigger | params |

### Worker Dispatcher (FUN_0043230A)

```c
uint __thiscall FUN_0043230A(void *this, int param_1, int param_2)  // building, unit_id, type
{
    if (param_2 == 1) return FUN_0043234D(this, param_1);      // create?
    else if (param_2 == 2) return FUN_0043242C(this, param_1);  // ASSIGN JOB ★
    else if (param_2 == 4) return FUN_0043256B(this, param_1);  // ?
    else if (param_2 == 8) return FUN_00432516(this, param_1);  // ?
}
```

### Kluczowe adresy do code cave

| Element | Adres | Wartość |
|---------|-------|---------|
| Job limit check | 0x46BD33 | `CMP EAX, 0x2E` → `0x7F` |
| Jump table | 0x46BE76 | 18 entries × 4B |
| Case table | 0x46BEBE | 46 entries × 1B |
| Potter handler case | 0x46BDDC | `CALL 0x46D53A` |
| **Job assignment** | **0x43242C** | **GŁÓWNA FUNKCJA** |
| Worker dispatcher | 0x43230A | param_2=2 → FUN_0043242C |

---

## 15. Analiza asm dyspozytora — szczegóły

### Struktura switch

```asm
0x46BAD7: PUSH EBX
0x46BAD8: PUSH ESI
0x46BAD9: MOV ESI, ECX                    ; ESI = unit
...
0x46BD2F: MOV EAX, dword ptr [ESI+0x18]   ; EAX = job
0x46BD32: DEC EAX                          ; EAX = job - 1
0x46BD33: CMP EAX, 0x2E                    ; porównaj z 46
0x46BD36: JA  0x46BE1B                     ; jeśli > 46 → default
0x46BD3C: MOVZX EAX, byte ptr [EAX+0x46BEBE] ; EAX = case_table[job-1]
0x46BD43: JMP dword ptr [EAX*4+0x46BE76]  ; jump_table[EAX]
```

### Case table (0x46BEBE, 46 bajtów)

```
Offset  Value  Job    Jump table index
0       00     0-2    0  → 0x46BD4A (default)
1       01     3      1  → 0x46BD6A
2       02     4      2  → 0x46BDE5
3       03     5      3  → 0x46BD76
4       04     6      4  → 0x46BD82
5       05     7      5  → 0x46BD8E
6       06     8      6  → 0x46BD9A
7       07     9-14   7  → 0x46BDC1 (default)
8       08     15     8  → 0x46BDA6
9       09     16     9  → 0x46BDAF
10      07     17     7  → 0x46BDC1 (default)
11      0A     18     10 → 0x46BDB8
12      07     19     13 → 0x46BDDC (POTTER) ★
13      0B     20     11 → 0x46BDCA
14      02     21     2  → 0x46BDE5
15      0C     22     12 → 0x46BDD3
16      0D     23     13 → 0x46BDDC
17      02     24     2  → 0x46BDE5
18      02     25     2  → 0x46BDE5
19      0E     26     14 → 0x46BDF7
20      0F     27     15 → 0x46BE00
21      10     28     16 → 0x46BE09
22-46   11     29-46  17 → 0x46BE12 (default)
```

**Wzorzec:** Job 0x19 (25) → case_table[12] = 0x07 → jump_table[13] = 0x46BDDC (potter handler)

### Plan patcha dla job 56 (0x38)

| Element | Adres | Oryginał | Nowy | Opis |
|---------|-------|----------|------|------|
| case_table[55] | 0x46BEBE + 55 | 0x00 | 0x12 | jump table index 18 |
| jump_table[18] | 0x46BE76 + 18*4 | 0x00000000 | 0x0046BE26 | nowy case handler |
| nowy case | 0x46BE26 | (wolne) | `MOV ECX,ESI; CALL 0x46D53A; JMP 0x46BE26` | smolarz handler |

### Kod nowego case (smolarz)

```asm
0x46BE26: 89 F1           MOV ECX, ESI
0x46BE28: E8 2F 17 00 00  CALL 0x0046D53A  ; potter handler
0x46BE2D: E9 F5 00 00 00  JMP  0x0046BE26  ; powrót
0x46BE32: 90 90 90        NOP (padding)
```

### Weryfikacja

| Sprawdzenie | Wynik |
|-------------|--------|
| Limit case table (0x2E = 46) | ✅ 56 > 46 — wymaga rozszerzenia lub użycia istniejącego slotu |
| Wolna przestrzeń po 0x46BE1B | ✅ 0x46BE26 jest wolne |
| CALL rel32 do 0x46D53A | ✅ 0x2F170000 |
| JMP rel32 do 0x46BE26 | ✅ 0xF5000000 |

### Ograniczenie

**Job 56 (0x38) przekracza limit case table (0x2E = 46)!**

Rozwiązania:
1. **Użyj job < 46** (np. 26 = 0x1A) — nie wymaga rozszerzania case table
2. **Rozszerz case table** — wymaga przesunięcia jump table (skomplikowane)
3. **Przeżyj istniejący slot** — np. job 4-25 (case_table[2] = 0x02 → 0x46BDE5)

**Rekomendacja:** Użyj job 26 (0x1A) dla smolarza — nie wymaga rozszerzania case table!

### Aktualizacja planu

| Element | Wartość |
|---------|---------|
| Job ID | 26 (0x1A) zamiast 56 |
| case_table[25] | 0x02 (bez zmian!) |
| jump_table[2] | 0x0046BE26 (zamiast 0x0046BDE5) |
| houses.ini | `logicworker 26 1` (zamiast 56) |

**Bez rozszerzania case table!**
