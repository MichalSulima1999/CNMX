# RE — Wszystkie zidentyfikowane funkcje CN.PLMOD.exe (kompletny pseudocode)

Źródło: REA (Rizin/Ghidra 12.1.4) — `procedure_pseudo_code` na `CN.PLMOD.exe` (SHA-256: 367419b7...).
Wszystkie adresy to VA (ImageBase 0x400000). Pseudocode to wyjście dekompilatora, nie oryginalne źródło.

---

## 1. Tick jednostki i produkcja

### FUN_00473461 — Unit tick / produkcja (VA 0x473461) [ROOT CAUSE]

Obsługuje TYLKO typy budynków 38 (szkoła) i 39 (koszary). Typ 57 → wczesny return.

```c
void FUN_00473461(unit *this, int param_1) {
  int bldg_type = *(int *)(*(int *)(this + 0xB34) * 0x7E0 + 0x14 + DAT_00510BD0);
  uint uVar6; int local_8;

  if (bldg_type == 0x26) {          // typ 38
    // odczytuje uVar6 i local_8 z budynku (+8, +0xC)
  } else if (bldg_type == 0x27) {   // typ 39
    // odczytuje uVar6 z plemienia (offset 0x6740)
    local_8 = 0;
  } else {
    return;  // TYP 57 NIE JEST OBSŁUGIWANY
  }

  if (uVar6 != 0) {
    // Próg z plemienia (stary imm 0x6B82!)
    int tribe_offset = *(int *)(this + 0x14) * 0x6B82;
    uint uVar5 = *(uint *)(DAT_00511200 + 0x6740 + (tribe_offset + uVar6) * 4);
    if (local_8 != 0)
      uVar5 += *(uint *)(DAT_00511200 + 0x6820 + (tribe_offset + local_8) * 4);

    if (*(uint *)(this + 0x158) < uVar5) {
      if (10000 - param_1 < *(uint *)(this + 0x158))
        *(uint *)(this + 0x158) = 10000;
      else
        *(uint *)(this + 0x158) += param_1;
    } else {
      uVar5 = FUN_0042D9D7(this, uVar6);
      if ((char)uVar5 == 0) {
        *(byte *)(uVar6 + 0x15C + (int)this) = 1;
        FUN_0045BBAA(this, uVar6);
      }
      if ((local_8 != 0) && (*(char *)(local_8 + 0x195 + (int)this) == 0)) {
        *(char *)(local_8 + 0x195 + (int)this) = 1;
        FUN_0045BB51(this, local_8);
      }
      *(uint *)(this + 0x158) = 0;

      if (*(uint *)(this + 0x18) == uVar6) {
        FUN_0044A0D9(this);
        FUN_0044B2FA(this);
      } else {
        FUN_00449F2F(this, uVar6);
      }
      FUN_00449BDA(this);

      if ((local_8 != 0) && FUN_0042DA65(this, local_8)) {
        FUN_0043E8A7(this, local_8);
      }
    }
  }
}
```

---

## 2. Bramki produkcji (gate functions)

### FUN_0042DA65 — Czy jednostka może produkować good? (VA 0x42DA65)

```c
bool FUN_0042DA65(unit *this, int good) {
  return *(byte *)(this + 0x195 + good) != 0
      && FUN_0042DB20(this, good)
      && (FUN_0042D848(this, good) || FUN_0042D9A3(this, good) || race == 2);
}
```

### FUN_0042DB20 — Czy good jest na liście job block? (VA 0x42DB20)

```c
uint FUN_0042DB20(unit *this, int good) {
  if (good != 0 && *(char *)(good + 0x195 + (int)this) != 0) {
    int *job_block = job * 0x400 + 0x6928 + DAT_00511200 + tribe * 0x1AE08;
    uint *count = job_block + 1;
    if (*count != 0) {
      int *list = job_block + 0x36;
      do {
        if (*list == good) return 1;
        list++;
      } while (++uVar2 < *count);
    }
  }
  return 0;
}
```

### FUN_0042D848 — Needforgood: czy jednostka ma surowce (VA 0x42D848)

```c
bool FUN_0042D848(unit *this, int good) {
  uint *req = DAT_00511200 + tribe * 0x1AE08 + 0x55FC + good * 0x14;
  uint needed = req[1];
  uint sum = 0;
  if (needed != 0) {
    uint *inputs = req + 2;
    do {
      sum += *(int *)(this + *inputs * 4 + 0x24);
      inputs++;
      needed--;
    } while (needed != 0);
  }
  return sum >= *req;  // *req = wymagana ilość
}
```

Struktura wymagań: `tribe_base + 0x55FC + good*0x14`:
- +0x00: wymagana ilość (target)
- +0x04: liczba typów surowców wejściowych
- +0x08+: ID surowców wejściowych

### FUN_0042D9A3 — Próg plemienia dla gooda (VA 0x42D9A3)

```c
bool FUN_0042D9A3(unit *this, int good) {
  return unit->production_timer (0x158)
       >= *(uint *)(DAT_00511200 + 0x6820 + (tribe * 0x6B82 + good) * 4);
}
```

UWAGA: Używa starego imm 0x6B82 (powinno być 0x8578 po patchu).

### FUN_0042D803 — Alternatywny needforgood (VA 0x42D803)

Identyczna logika jak FUN_0042D848, ale offset 0x519C zamiast 0x55FC.

```c
bool FUN_0042D803(unit *this, int good) {
  uint *req = DAT_00511200 + tribe * 0x1AE08 + 0x519C + good * 0x14;
  // ... ta sama logika co FUN_0042D848
}
```

### FUN_0042D97D — Alternatywny próg plemienia (VA 0x42D97D)

Identyczna logika jak FUN_0042D9A3, ale offset 0x6740 zamiast 0x6820.

---

## 3. FUN_0044A0D9 — Ustawia +0x195 dla goodów joba (VA 0x44A0D9)

Wywoływana z FUN_00473461 gdy `job == uVar6` oraz z FUN_00449F2F na końcu.

```c
void FUN_0044A0D9(unit *this) {
  FUN_0042C016(local_330);  // inicjalizacja何か
  local_320 = *(int *)(this + 4);  // owner?
  local_328 = *(int *)(this + 0x10);  // player?
  local_330[0] = 0x12;

  if (*(char *)(job * 0x88 + 0x85 + DAT_00511180) == 0) {
    *(byte *)(this + 0x194) = 0;
  } else {
    *(byte *)(this + 0x194) = 1;
  }

  local_1c = player * 0x4A80 + DAT_00510BC4;
  int *job_block = job * 0x400 + 0x6928 + DAT_00511200 + tribe * 0x1AE08;

  if (*job_block != 0) {
    int *good_list = job_block + 4;
    do {
      int good = *good_list;
      bool ok = FUN_0042D803(this, good)
             || FUN_0042D97D(this, good)
             || FUN_0042C597(this) == 2;

      if (ok) {
        int iVar3 = player * 0x4A80 + DAT_00510BC4;
        local_2c = iVar3;
        if (*(char *)(tribe * 0x38 + iVar3 + 0x18 + good) != 0) {
          *(byte *)(good + 0x15C + (int)this) = 1;
          char *flag_ptr = tribe * 0x38 + iVar3 + 0x948 + good;
          if (*flag_ptr == 0) {
            *flag_ptr = 1;
            aiStack_1f4[local_1f8++] = good;
            char *job_block2 = good * 0x400 + 0x6928 + DAT_00511200 + tribe * 0x1AE08;
            local_24 = job_block2;
            if (*(int *)(job_block2 + 4) != 0) {
              int *job_good_list = job_block2 + 0xD8;
              do {
                int jg = *job_good_list;
                if (*(char *)(good + 0x195 + (int)this) == 0
                    && *(char *)(tribe * 0x42 + jg + 0x1278 + iVar3) != 0
                    && (FUN_0042D848(this, jg) || FUN_0042D9A3(this, jg) || FUN_0042C597(this) == 2)) {
                  if (local_18 == 0x0F && jg == 0x38)
                    *(byte *)(this + 0x1CD) = 1;
                  else if (local_18 != 0x10 || jg == 0x39 || jg == 0x3A)
                    *(byte *)(jg + 0x195 + (int)this) = 1;
                  char *pcVar1 = tribe * 0x42 + jg + 0x1D4C + local_2c;
                  if (*pcVar1 == 0) {
                    *pcVar1 = 1;
                    aiStack_300[local_304++] = jg;
                  }
                }
                local_20++;
                job_good_list++;
              } while (local_20 < *(uint *)(job_block2 + 4));
            }
          }
        }
        // ... iteruje po house types (0x624 stride), sprawdza czy budynek może produkować
        // wywołuje FUN_00409ABC dla pasujących typów
      }
      local_8++;
      good_list++;
    } while (local_8 < (int *)*job_block);
  }

  // Druga pętla: jobDefaultGood (+0x330)
  if (job_block[1] != 0) {
    local_8 = job_block + 0x36;
    do {
      int good = *local_8;
      int iVar3 = tribe * 0x42 + good + local_1c;
      if (*(char *)(iVar3 + 0x1278) != 0
          && (*(char *)(good + 0x195 + (int)this) == 0 || *(char *)(iVar3 + 0x1D4C) == 0)
          && (FUN_0042D848(this, good) || FUN_0042D9A3(this, good) || FUN_0042C597(this) == 2)) {
        if (FUN_0042C676(this)) {
          if (good == 0x38) *(byte *)(this + 0x1CD) = 1;
        } else {
          if (!FUN_0042C680(this) || good == 0x39 || good == 0x3A)
            *(byte *)(good + 0x195 + (int)this) = 1;
        }
        char *pcVar5 = tribe * 0x42 + good + 0x1D4C + local_1c;
        if (*pcVar5 == 0) {
          *pcVar5 = 1;
          aiStack_300[local_304++] = good;
        }
      }
      local_10++;
      local_8++;
    } while (local_10 < (uint)job_block[1]);
  }

  // Trzecia pętla: +0xCC (house_type related)
  if (job_block[2] != 0) {
    local_8 = job_block + 0x68;
    do {
      int good = *local_8;
      bool ok = FUN_0042D88D(this, good) || FUN_0042C597(this) == 2;
      if (ok) {
        int iVar3 = tribe;
        int iVar8 = local_1c + iVar3 * 0x37;
        if (*(char *)(good * 0x198 + 0x14B38 + DAT_00511200 + iVar3 * 0x1AE08 + 0x2820) == 0
            || *(char *)(good * 0x198 + 0x14B38 + DAT_00511200 + iVar3 * 0x1AE08 + 0x3126) != 0
            || *(int *)(good * 0x624 + DAT_005113A0) == 7)
          goto skip;
        // kopiuje 0x66 dwordów z plemienia do local_4c8
        // sprawdza flagi GOODS_A i GOODS_B
        // wywołuje FUN_00409ABC
      }
      skip:
      local_10++;
      local_8++;
    } while ((uint)local_28[2] > local_10);
  }

  // Na końcu: wywołuje FUN_0043E09A dla selected good
  if (*(int *)(this + 0x1C) != 0 && !FUN_0042DB20(this, *(int *)(this + 0x1C))) {
    *(int *)(this + 0x218) = 0;
    *(int *)(this + 0x1C) = 0;
    *(int *)(this + 0x38C) = 0;
  }
  if ((*(int *)(this + 0x1C) == 0 || *(char *)(*(int *)(this + 0x1C) + 0x195 + (int)this) == 0)
      && job_block[0xCC] != 0) {
    if (FUN_0042DA65(this, job_block[0xCC])) {
      FUN_0043E09A(this, job_block[0xCC]);
    } else {
      // szuka pierwszego available good w job block
    }
  }

  _memset(this + 0x1E0, 0, 0x38);
  // ... więcej ustawiania flag +0x15C i +0x1E0 dla zakresów goodów
  // FUN_0043BF90(this);
  // jeśli jakieś flagi zostały ustawione: FUN_0042C064, FUN_004A2222, FUN_004127EF
}
```

---

## 4. UI i wybór gooda

### FUN_0043E8A7 — UI: wybierz good do produkcji (VA 0x43E8A7)

```c
void FUN_0043E8A7(unit *this, int good) {
  if (FUN_0042DB20(this, good)) {
    int local_c = 0;
    int iVar1 = job * 0x400 + 0x6928 + DAT_00511200 + tribe * 0x1AE08;
    if (*(int *)(iVar1 + 4) != 0) {
      int *local_8 = iVar1 + 0xD8;
      do {
        int iVar2 = *local_8;
        int iVar4 = FUN_0044B5D9(this, iVar2);
        if (iVar4 < 0xC && iVar4 > 0)
          FUN_0044B5E7(this, iVar2, 0);
        local_c++;
        local_8++;
      } while (local_c < *(uint *)(iVar1 + 4));
    }
    FUN_0044B5E7(this, good, 0x0B);
    *(int *)(this + 0x38C) = 0;
    *(int *)(this + 0x218) = good;
    *(int *)(this + 0x1C) = good;
  }
}
```

### FUN_0044B5D9 — Getter statusu gooda +0x21C (VA 0x44B5D9)

```c
uint FUN_0044B5D9(unit *this, int good) {
  return *(uint *)(this + good * 4 + 0x21C);
}
```

### FUN_0044B5E7 — Setter statusu gooda +0x21C (VA 0x44B5E7)

Ustawia status gooda: 0, 0xB, 0xC, 0xD, 0xE.

### FUN_0044B2FA — Ustawia status produkcji +0x21C dla goodów joba (VA 0x44B2FA)

```c
void FUN_0044B2FA(unit *this) {
  int iVar1 = job * 0x400 + 0x6928 + DAT_00511200 + tribe * 0x1AE08;
  if (*(int *)(iVar1 + 4) != 0) {
    int *good_list = iVar1 + 0xD8;
    do {
      int good = *good_list;
      if (*(char *)(this + good + 0x195) == 0) {
        *(int *)(this + good * 4 + 0x21C) = 0x0C;  // nie ma +0x195
      } else {
        if (!FUN_0042DB20(this, good)) {
          *(int *)(this + good * 4 + 0x21C) = 0x0D;  // nie w job block
        } else {
          bool can = FUN_0042DA65(this, good);
          *(int *)(this + good * 4 + 0x21C) = can ? 0x0E : 0x0C;  // 0xE = można, 0xC = nie można
        }
      }
      good_list++;
    } while (++local_c < *(uint *)(iVar1 + 4));
  }
  int job_default_good = *(int *)(iVar1 + 0x330);
  if (job_default_good != 0) {
    if (FUN_0042DA65(this, job_default_good)) {
      *(int *)(this + job_default_good * 4 + 0x21C) = 0x0B;
    } else {
      // szuka pierwszego available good
    }
  }
}
```

### FUN_00449F2F — UI: zmień selected good (VA 0x449F2F)

Wywoływana z FUN_00473461 gdy `job != uVar6`. Na końcu wywołuje `FUN_0044A0D9` i `FUN_0044B226`.

```c
void FUN_00449F2F(unit *this, int new_good) {
  *(int *)(this + 0x38C) = 0;
  if (*(int *)(this + 0x18) != new_good) {
    FUN_004127EF(DAT_00510C0C, 0x1F, 1, *(int *)(this + 4), *(int *)(this + 0x18), new_good);
  }
  if (FUN_0042C6F0(this)) {  // building_idx != -1
    if (!FUN_0042C8A8(this)) {
      void *bldg = building_idx * 0x7E0 + DAT_00510BD0;
      int iVar3 = (*(int *)(this + 0x18) != 7) ? 2 : 4;
      FUN_004320BF(bldg, *(int *)(this + 4), iVar3);
      if (FUN_00431FF5(bldg, *(int *)(this + 4), (new_good == 7) * 2 + 2)) {
        FUN_004346A2(this, *(int *)(bldg + 4));
        *(int *)(this + 0x38C) = 0;
        *(int *)(this + 0xB30) = *(int *)(bldg + 0x24);
        FUN_004530D6(this);
      }
    } else {
      FUN_004320BF(bldg, *(int *)(this + 4), 8);
    }
  }
  // ... obsługa special goodów 0x19, 0x0F
  // zmienia job jednostki (+0x18)
  // na końcu:
  FUN_0044A0D9(this);
  FUN_0044B226(this);
}
```

### FUN_0044B226 — Menu produkcji (VA 0x44B226)

Ustawia status +0x21C dla goodów 1-65:
- 0x0C (12) jeśli `+0x195[good] == 0`
- 0x0D (13) jeśli good nie w job block
- 0x0E (14) jeśli `FUN_0042DA65` true
- 0x0B (11) inaczej

Następnie ustawia +0x21C na 0x0B dla jobDefaultGood (+0x330) jeśli można produkować.

---

## 5. Funkcje pomocnicze

### FUN_0042C6F0 — Czy jednostka ma budynek? (VA 0x42C6F0)

```c
bool FUN_0042C6F0(unit *this) {
  return *(int *)(this + 0xB34) != -1;
}
```

### FUN_0042C597 — Flaga gracza (VA 0x42C597)

```c
uint FUN_0042C597(unit *this) {
  if (*(int *)(this + 0x10) > 0x13) return 0;
  return *(uint *)(DAT_00510BC4 + player * 0x4A80 + 4);
}
```

### FUN_0042C5B3 — Sprawdź job jednostki (VA 0x42C5B3)

```c
uint FUN_0042C5B3(unit *this) {
  int job = *(int *)(this + 0x18);
  if (job == 1 || job == 3 || job == 5)
    return 1;  // niektóre_joby
  if (job - 0x2F == 0)  // job == 47
    return *(int *)(this + 0x14) == 3;  // tribe == 3
  return 0;
}
```

### FUN_0042C676 — Czy job == 15? (VA 0x42C676)

```c
bool FUN_0042C676(unit *this) {
  return *(int *)(this + 0x18) == 0x0F;
}
```

### FUN_0042C6BC — Czy job w zakresie 30-41? (VA 0x42C6BC)

```c
bool FUN_0042C6BC(unit *this) {
  int job = *(int *)(this + 0x18);
  return job > 0x1E && job < 0x2A;
}
```

### FUN_0042C6CF — Czy job w zakresie 42-47? (VA 0x42C6CF)

```c
bool FUN_0042C6CF(unit *this) {
  int job = *(int *)(this + 0x18);
  return job > 0x29 && job < 0x30;
}
```

### FUN_0042C8A8 — Czy building ma owner i jest typu 4? (VA 0x42C8A8)

```c
bool FUN_0042C8A8(unit *this) {
  if (*(int *)(this + 0xB34) != -1) {
    int bldg_type = FUN_004316E0(building_idx * 0x7E0 + DAT_00510BD0);
    if (bldg_type == 4) {
      return FUN_004322DA(building_instance, owner) != 0;
    }
  }
  return 0;
}
```

### FUN_004316E0 — Zwraca house_type z building instance (VA 0x4316E0)

```c
int FUN_004316E0(int building_instance) {
  return *(int *)(building_instance + 0x14);  // house_type z building+0x14
}
```

### FUN_004322DA — Sprawdź właściciela budynku i flagę (VA 0x4322DA)

```c
uint FUN_004322DA(building *bldg, int owner) {
  if (*(int *)(bldg->house_type * 0x624 + DAT_005113A0) == 4
      && FUN_0043267F(bldg, owner) != 0
      && (*(byte *)FUN_0043267F(bldg, owner) & 8) != 0)
    return 1;
  return 0;
}
```

### FUN_0043E09A — Wybierz good do produkcji (VA 0x43E09A)

```c
uint FUN_0043E09A(unit *this, int good) {
  if (!FUN_0045C66E(this)) return 0;
  if (!FUN_0042DB20(this, good)) return 1;
  if (FUN_0042C909(this)) {
    *(int *)(this + 0xB3C) = -1;
    *(int *)(this + 0xB40) = 0;
  }
  FUN_0043E8A7(this, good);
  if (*(int *)(this + 0x18) == 7) {
    if (!FUN_0042C6F0(this)) {
      if (FUN_0042C73B(this)) FUN_0042878E(DAT_00512764, player, this + 0xB30);
      if (FUN_0042C783(this)) FUN_0042878E(DAT_00512760, player, this + 0xB30);
    }
  }
  if (FUN_0042C6F0(this)) {
    if (!FUN_0042C8A8(this) && good != 0 && good != 0x41) {
      int good_from_job = FUN_00461C14(job, good);
      if (!FUN_004316F3(building, good_from_job, 0)
          && !FUN_004316F3(building, good_from_job, 1))
        FUN_0043D037(this);
    }
  }
  return 2;
}
```

### FUN_004319D7 — Pobierz ilość towaru w budynku (VA 0x4319D7)

```c
int FUN_004319D7(house_type *ht, int good, char flag) {
  if (good < 0x42) {
    int category = *(int *)(ht + 0x14);  // house_type category
    int *ht_base = category * 0x624 + DAT_005113A0;
    if (flag == 0) {
      if (*ht_base == 2) {
        if (good == 0x0F) return *(int *)(this + 0x794);
        if (good == 0x1C) return *(int *)(this + 0x78C);
        if (good == 0x1D) return *(int *)(this + 0x784);
      }
      else if (good == 0x0F && (category == 1 || category == 0x25))
        return *(int *)(this + 0x794);
    }
    int revmap_idx = FUN_00431F37(ht, good);
    if (revmap_idx != -1
        && (*ht_base != 3 || flag == 0 || *(char *)(ht_base + revmap_idx * 3 + 0x1B) == 0)) {
      int qty = *(int *)(this + revmap_idx * 4 + 0x118);
      int *counter = this + revmap_idx * 4 + 0x430;
      if (qty == 0) {
        *counter = *counter + 1;
        return 0;
      }
      *counter = *counter - 10;
      if (*counter >= 0) return qty;
      *counter = 0;
      return qty;
    }
  }
  return 0;
}
```

### FUN_00434142 — Sprawdź czy budynek ma pracownika (VA 0x434142)

```c
bool FUN_00434142(building *bldg, int worker_idx) {
  if (worker_idx < 5)
    return *(int *)(bldg + worker_idx * 4 + 0x7A8) != 0;
  return false;
}
```

---

## 6. Struktura job block (odkryta przez REA)

`tribe_base + tribe * 0x1AE08 + 0x6928 + job * 0x400`

| Offset | Rozmiar | Nazwa | Opis |
|--------|---------|-------|------|
| +0x000 | 4 | count | liczba goodów w job block |
| +0x004 | 4 | ? | |
| +0x0D8 | 4×N | good_list | lista goodów które job może produkować |
| +0x330 | 4 | jobDefaultGood | domyślny good do produkcji |

---

## 7. Struktura plemienia — tabele wymagań i progów

`DAT_00511200 + tribe * 0x1AE08`

| Offset | Nazwa | Opis |
|--------|-------|------|
| +0x519C + good*0x14 | req_table | requirements (FUN_0042D803): +0=target, +4=count, +8+=input goods |
| +0x55FC + good*0x14 | need_table | needs (FUN_0042D848): +0=target, +4=count, +8+=input goods |
| +0x6740 + (tribe*0x6B82 + good)*4 | threshold1 | próg produkcji 1 (FUN_0042D97D) |
| +0x6820 + (tribe*0x6B82 + good)*4 | threshold2 | próg produkcji 2 (FUN_0042D9A3) |
| +0x6928 + job*0x400 | job_block | job block dla danego zawodu |

---

## 8. Nowe funkcje z analizy REA (batch 1-2)

### FUN_00494996 — Dodaj wpis do tablicy (VA 0x494996)

Wywoływane z `FUN_0049599B`. Dodaje wpis do tablicy o maksymalnie 0x14 (20) wpisach, każdy 0x10 B:

```c
uint FUN_00494996(void *table, void *param_1, int param_2, int param_3, int param_4) {
  // table+0x00 = count (max 0x14)
  // table+0x04+ = entries, each 0x10 B: [ptr, int, int, int]
  if (*(int *)table != 0x14 && FUN_00439ab3(param_1, param_2)) {
    *(void **)((*(int *)table * 0x10) + 4 + (int)table) = param_1;
    *(int *)((*(int *)table * 0x10) + 8 + (int)table) = param_2;
    *(int *)((*(int *)table * 0x10) + 0x0C + (int)table) = param_3;
    int iVar1 = (*(int *)table + 1) * 0x10;
    *(int *)(iVar1 + (int)table) = param_4;
    *(int *)table = *(int *)table + 1;
    return 1;
  }
  return 0;
}
```

Struktura wpisu (0x10 B):
| Offset | Pole | Opis |
|--------|------|------|
| +0x00 | ptr | wskaźnik (void*) |
| +0x04 | val1 | int |
| +0x08 | val2 | int |
| +0x0C | val3 | int |

---

### FUN_0042c016 — Inicjalizacja struktury (VA 0x42C016)

Inicjalizuje strukturę o rozmiarze 0x304 B:

```c
void *FUN_0042c016(void *ptr) {
  memset(ptr, 0, 0x304);
  *(ushort *)(ptr + 0x28) = 0xFFFF;
  *(ushort *)(ptr + 0x2A) = 0xFFFF;
  *(int *)(ptr + 0x08) = -1;
  *(int *)(ptr + 0x10) = -1;
  *(int *)(ptr + 0x18) = -1;
  *(int *)(ptr + 0x20) = -1;
  *(int *)(ptr + 0x30) = 0;
  *(int *)(ptr + 0x13C) = 0;
  *(int *)(ptr + 0x200) = 0;
  *(int *)(ptr + 0x2E0) = 0;
  return ptr;
}
```

---

### FUN_0042c064 — Kopiuj dane z tablic globalnych (VA 0x42C064)

Kopiuje wartości z trzech tablic globalnych do struktury:

```c
void FUN_0042c064(int ptr) {
  if (*(int *)(ptr + 0x10) != -1)
    *(int *)(ptr + 0x14) = *(int *)(DAT_00510BD8 + *(int *)(ptr + 0x10) * 0xC58 + 8);
  if (*(int *)(ptr + 0x18) != -1)
    *(int *)(ptr + 0x1C) = *(int *)(DAT_00510BD0 + *(int *)(ptr + 0x18) * 0x7E0 + 8);
  if (*(int *)(ptr + 0x20) != -1)
    *(int *)(ptr + 0x24) = *(int *)(DAT_00510BE0 + *(int *)(ptr + 0x20) * 0x54C + 8);
  *(byte *)(ptr + 0x04) = 1;
}
```

Struktura docelowa:
| Offset | Źródło | Opis |
|--------|--------|------|
| +0x10 | index | index do DAT_00510BD8 (stride 0xC58) |
| +0x14 | wartość | skopiowane z DAT_00510BD8+8 |
| +0x18 | index | index do DAT_00510BD0 (stride 0x7E0) |
| +0x1C | wartość | skopiowane z DAT_00510BD0+8 |
| +0x20 | index | index do DAT_00510BE0 (stride 0x54C) |
| +0x24 | wartość | skopiowane z DAT_00510BE0+8 |
| +0x04 | flaga | ustawiana na 1 |

---

### FUN_00431ff5 — Dodaj do tablicy building+0x644 (VA 0x431FF5)

Dodaje wpis do tablicy 20 wpisów × 0x10 B w building+0x644:

```c
uint FUN_00431ff5(void *bldg, int param_1, int param_2) {
  // building+0x644: tablica 20 wpisów × 4 B (indeksy buildingów)
  // building+0x640: tablica 20 bajtów flag
  if (FUN_0043230a(bldg, param_1, param_2)) return 0;
  
  // Szukaj pustego slotu w building+0x640
  for (int i = 0; i < 0x14; i++) {
    if (*(byte *)(bldg + 0x640 + i * 0x10) == 0) {
      *(int *)(bldg + 0x644 + i * 0x10) = param_1;
      *(byte *)(bldg + (i + 100) * 0x10 + (int)bldg) = (byte)param_2;
      return 1;
    }
  }
  
  // Jeśli full i param_2 == 1, szukaj slotu z flagą 0x04
  if (param_2 == 1) {
    for (int i = 0; i < 0x14; i++) {
      if (*(byte *)(bldg + 0x640 + i * 0x10) == 4) {
        *(byte *)(bldg + (i + 100) * 0x10 + (int)bldg) = 0;
        int idx = *(int *)(bldg + 0x644 + i * 0x10);
        fun_00441800(DAT_00510BD8 + idx * 0xC58);
        *(byte *)(bldg + (i + 100) * 0x10 + (int)bldg) = 1;
        *(int *)(bldg + 0x644 + i * 0x10) = param_1;
        return 1;
      }
    }
  }
  return 0;
}
```

---

### FUN_004320bf — Usuń z tablicy building+0x644 (VA 0x4320BF)

Usuwa wpis z tablicy building+0x644:

```c
uint FUN_004320bf(void *bldg, int param_1, int param_2) {
  // Szukaj wpisu z param_1 w building+0x644
  for (int i = 0; i <= 0x13; i++) {
    if (*(byte *)(bldg + 0x644 + i * 0x10 - 1) == 0 || *(int *)(bldg + 0x644 + i * 0x10) != param_1)
      continue;
    
    // Czyść flagę param_2
    byte *flag = (byte *)(bldg + (i + 100) * 0x10);
    *flag = *flag & ~(byte)param_2;
    
    if (param_2 == 1) {
      FUN_004417C7(param_1 * 0xC58 + DAT_00510BD8);
    } else if (param_2 == 2 || param_2 == 4) {
      FUN_00441800(param_1 * 0xC58 + DAT_00510BD8);
    } else {
      if (param_2 - 8 == 0) {
        FUN_00441800(param_1 * 0xC58 + DAT_00510BD8);
        void *slot = (void *)(bldg + i * 0x10);
        *(int *)(slot + 0x648) = 0;
        *(int *)(slot + 0x64C) = 0;
      }
    }
    
    if (*flag == 0)
      *(int *)(bldg + 0x644 + i * 0x10) = -1;
    return 1;
  }
  return 0;
}
```

---

### FUN_004346a2 — Ustaw building_idx i wywołaj FUN_0044A0D9 (VA 0x4346A2)

```c
void FUN_004346a2(unit *this, int building_idx) {
  *(int *)(this + 0xB34) = building_idx;
  *(uint *)(this + 0xB38) = *(uint *)(DAT_00510BD0 + building_idx * 0x7E0 + 8);
  FUN_0044A0D9(this);
  FUN_0044B2FA(this);
}
```

Ustawia `+0xB34` (building_idx) i `+0xB38` (wartość z building+8), następnie wywołuje `FUN_0044A0D9` i `FUN_0044B2FA`.

---

### FUN_0043bf90 — Czyść flagi w tablicy +0x390 (VA 0x43BF90)

Iteruje 0x57 (87) wpisów z stride 0x14 zaczynając od +0x390:

```c
void FUN_0043bf90(void *param_1) {
  byte *ptr = param_1 + 0x390;
  for (int i = 0; i < 0x57; i++) {
    if (*ptr != 0) {
      if (FUN_0043BFBC(param_1, ptr)) {
        *ptr = 0;
      }
    }
    ptr += 0x14;
  }
}
```

---

### FUN_004530d6 — Zarządzaj obiektem z DAT_00510BE8 (VA 0x4530D6)

```c
void FUN_004530d6(int param_1) {
  int idx = FUN_00453067(param_1);
  void *obj = idx == -1 ? NULL : DAT_00510BE8 + idx * 0x18;
  bool flag = FUN_00452FE6(param_1);
  
  if (obj == NULL) {
    if (flag) FUN_0040BA80(DAT_00510BEC, 1, param_1 + 0xB30, *(int *)(param_1 + 4));
  } else if (flag) {
    FUN_00438CCC(obj, param_1 + 0xB30);
  } else {
    FUN_0040BAE1(DAT_00510BEC, *(int *)(obj + 4));
  }
}
```

---

### FUN_0044b5e7 — Setter statusu gooda +0x21C (VA 0x44B5E7)

```c
void FUN_0044b5e7(void *this, int good, uint status) {
  *(uint *)(this + good * 4 + 0x21C) = status;
}
```

---

### FUN_0045c66e — Sprawdź flagę jednostki (VA 0x45C66E)

```c
uint FUN_0045c66e(int param_1) {
  if (*(int *)(param_1 + 0xAB8) == 1) {
    int idx = *(int *)(param_1 + 0xC) * 0x58;
    return *(byte *)(DAT_00510BF0 + idx + 0x2C) == 0;
  }
  if (*(byte *)(param_1 + 0xABC) != 0) {
    int idx = *(int *)(param_1 + 0xAC0) * 0x138;
    return *(byte *)(DAT_005112FC + idx + 0x38);
  }
  return 1;
}
```

---

### FUN_00461c14 — Mapuj good ID (VA 0x461C14)

```c
int FUN_00461c14(int job, int good) {
  if (job == 0x0F && good == 0x38) return 0x15;  // job 15 + good 56 -> good 21
  if (good == 0x16) return 0x10;                  // good 22 -> good 16
  return good;
}
```

---

### FUN_0042878e — Wyczyść flagę w tablicy (VA 0x42878E)

```c
void FUN_0042878e(void *this, int param_1, short *param_2) {
  uint *arr = *(uint **)(param_1 * 4 + *(int *)(this + 4));
  uint count = *arr;
  uint *entry = arr + 2;
  for (uint i = 0; i < count; i++) {
    if (*(short *)entry == *param_2 && *(short *)(entry + 1) == param_2[1]) {
      char *flag = (char *)(arr + (i * 3 + 6) * 2);
      if (*flag != 0) {
        *flag = 0;
        int *counter = (int *)(*(int *)(*(int *)(this + 4) + param_1 * 4) + 4);
        *counter = *counter - 1;
      }
      return;
    }
    entry = (uint *)((byte *)entry + 6);
  }
}
```

---

### FUN_0042c73b / FUN_0042c783 — Sprawdź jednostkę job==7 (VA 0x42C73B / 0x42C783)

Obie funkcje sprawdzają czy jednostka ma job == 7 i wykonują dodatkowe operacje na buildingu (DAT_00512764 i DAT_00512760).

---

### FUN_0042c909 — Sprawdź zakres selected_good (VA 0x42C909)

```c
int FUN_0042c909(int param_1) {
  int good = *(int *)(param_1 + 0x1C);
  if (good > 0x3A && good < 0x40) return 1;
  return 0;
}
```

Sprawdza czy selected_good (+0x1C) jest w zakresie 59-63 (0x3B-0x3F).

---

### FUN_0043d037 — Fallback gdy good nie można wyprodukować (VA 0x43D037)

```c
uint FUN_0043d037(int param_1) {
  if (*(int *)(param_1 + 0x18) != 7) {
    if (!FUN_0045C66E(param_1)) return 0;
    if (FUN_0042C6F0(param_1)) {
      if (!FUN_0042C8A8(param_1)) {
        if (FUN_004320BF(DAT_00510BD0 + *(int *)(param_1 + 0xB34) * 0x7E0,
                         *(int *)(param_1 + 4), 2))
          return 2;
        FUN_0045BCAC(param_1);
      }
    }
  }
  return 1;
}
```

---

### FUN_00409abc — Ustaw flagi w tablicy (VA 0x409ABC)

```c
void FUN_00409abc(void *this, int p1, int p2) {
  *(byte *)(p1 * 0x37 + p2 + 0x310E + (int)this) = 1;
  if (p2 == 10) *(byte *)(p1 * 0x42 + 0x1D35 + (int)this) = 1;
  if (p2 == 0x0B) *(byte *)(p1 * 0x42 + 0x1D40 + (int)this) = 1;
  if (p2 == 0x11) {
    *(byte *)(this + p1 * 0x42 + 0x1D49) = 1;
    *(byte *)(this + p1 * 0x42 + 0x1D3D) = 1;
    *(byte *)(this + p1 * 0x42 + 0x1D3E) = 1;
  }
}
```

---

## 8.1. Dodatkowe funkcje z analizy REA (batch 3)

### FUN_004417c7 — Czyszczenie tablicy budynku (VA 0x4417C7)

Wywoływane z `FUN_004320BF`. Czyści wpis w tablicy budynku i resetuje stan:

```c
void FUN_004417c7(int param_1) {
  bool bVar1 = FUN_0042C63B(param_1);
  if (bVar1 && *(int *)(param_1 + 0xACC) != 0 && *(int *)(param_1 + 0xACC) != 1) {
    FUN_00441B83(param_1);
    *(int *)(param_1 + 0xAD0) = 0;
  }
  *(int *)(param_1 + 0xB28) = 0xFFFFFFFF;
  *(int *)(param_1 + 0xB2C) = 0;
}
```

### FUN_00441800 — Czyszczenie tablicy budynku (VA 0x441800)

Wywoływane z `FUN_004320BF`. Resetuje stan budynku w zależności od selected_good (+0x1C):

```c
void FUN_00441800(void *param_1) {
  int iVar1 = *(int *)((int)param_1 + 0x1C);
  if (*(int *)((int)param_1 + 0xACC) != 0 &&
      (iVar1 == *(int *)((int)param_1 + 0xAD0) || iVar1 == 0x41 || iVar1 == 0x3A || iVar1 == 0x39)) {
    FUN_00441B83((int)param_1);
    *(int *)((int)param_1 + 0xAD0) = 0;
  }
  FUN_00441EE3(param_1);
}
```

### FUN_0043BFBC — Walidacja flagi (VA 0x43BFBC)

Wywoływane z `FUN_0043BF90`. Sprawdza czy flaga o podanej wartości może zostać wyczyszczona, w zależności od typu jednostki:

```c
bool FUN_0043BFBC(void *this, byte *param_1) {
  byte bVar1 = *param_1;
  if (bVar1 < 0x19) {
    if (bVar1 != 0x18) {
      switch (bVar1) {
        default: return true;
        case 0x04: case 0x05: case 0x07: case 0x08: case 0x09: case 0x0A:
        case 0x0B: case 0x0C: case 0x0F: case 0x10: case 0x11: case 0x12:
        case 0x15: case 0x16: case 0x17: break;  // fall through → return true
        case 0x06: case 0x0D: case 0x0E: {
          int iVar4 = FUN_0042C6BC((int)this);
          bool bVar2 = FUN_0042C66C((int)this);
          uint uVar5 = FUN_0042C68A((int)this);
          if ((iVar4 == 0 && !bVar2 && uVar5 == 0)) return false;
          return true;
        }
        case 0x13: case 0x14: {
          char cVar3 = FUN_0042C66C((int)this);
          return cVar3 == 0;
        }
      }
    }
  } else if (bVar1 < 0x24) {
    if (bVar1 != 0x23) {
      switch (bVar1) {
        case 0x19: case 0x1A: case 0x1B: case 0x20: case 0x21: case 0x22: break;
        case 0x1C: case 0x1D: return FUN_0042C64F((int)this);
        case 0x1E: case 0x1F: {
          char cVar3 = FUN_0042C64F((int)this);
          return cVar3 == 0;
        }
        default: return true;
      }
    }
  } else if (bVar1 < 0x2A) {
    if (bVar1 != 0x29) {
      if (bVar1 == 0x24 || bVar1 == 0x25) {
        uint uVar5 = FUN_0042C68A((int)this);
        return uVar5 == 0;
      }
      if (bVar1 != 0x26 && bVar1 != 0x27 && bVar1 != 0x28) return true;
    }
  } else if (bVar1 != 0x2A) {
    if (bVar1 < 0x2B) return true;
    if (0x30 < bVar1 && 0x33 < bVar1 && 0x57 < bVar1) return true;
  }
  return false;
}
```

### FUN_00439AB3 — Walidacja zakresu tablicy (VA 0x439AB3)

Wywoływane z `FUN_00494996`. Sprawdza czy indeks mieści się w zakresie tablicy i czy wpis nie jest pusty:

```c
uint FUN_00439AB3(void *this, int param_1) {
  uint uVar1 = param_1 - *(int *)((int)this + 4);
  if (uVar1 < *(uint *)((int)this + 8)) {
    return (*(int *)(*(int *)((int)this + 0x24) + uVar1 * 0x18) != 0);
  }
  return 0;
}
```

### FUN_0043230A — Walidacja typu wpisu (VA 0x43230A)

Wywoływane z `FUN_00431FF5`. Rozdzela walidację na pod-funkcje w zależności od `param_2`:

```c
uint FUN_0043230A(void *this, int param_1, int param_2) {
  if (param_2 == 1)      return FUN_0043234D(this, param_1);
  else if (param_2 == 2) return FUN_0043242C(this, param_1);
  else if (param_2 == 4) return FUN_0043256B(this, param_1);
  else if (param_2 == 8) return FUN_00432516(this, param_1);
  else                   return 0;
}
```

---

## 8.2. Dodatkowe funkcje z analizy REA (batch 4)

### FUN_0042c63b — Czy job == 5 (VA 0x42C63B)

```c
bool FUN_0042c63b(int param_1) {
  return *(int *)(param_1 + 0x18) == 5;  // job == 5
}
```

### FUN_0042c64f — Czy job == 7 (VA 0x42C64F)

```c
bool FUN_0042c64f(int param_1) {
  return *(int *)(param_1 + 0x18) == 7;  // job == 7
}
```

### FUN_0042c68a — Czy job == 0x19 lub 0x1a (VA 0x42C68A)

```c
uint FUN_0042c68a(int param_1) {
  int job = *(int *)(param_1 + 0x18);
  return (job != 0x19 && job != 0x1a) ? 0 : 1;
}
```

### FUN_0043234d — Walidacja typu 2 (dom) dla param_2 == 1 (VA 0x43234D)

Wywoływane z `FUN_0043230A` gdy `param_2 == 1`.

```c
bool FUN_0043234d(void *this, int param_1) {
  if (!FUN_004325db(this, param_1)) return false;
  int *house_type = *(int *)(this + 0x14) * 0x624 + DAT_005113A0;
  if (*house_type != 2) return false;
  byte *owner_entry = FUN_0043267f(this, param_1);
  if (owner_entry == NULL || (*owner_entry & 1) == 0) {
    int iVar6 = param_1 * 0xc58 + DAT_00510BD8;
    bool b1 = (*(int *)(iVar6 + 0xb14) == -1)
        || (*(int *)(*(int *)(iVar6 + 0xb14) * 0xc58 + 0xb28 + DAT_00510BD8) != *(int *)(this + 4));
    bool b2 = (*(int *)(iVar6 + 0xb18) == -1)
        || (*(int *)(*(int *)(iVar6 + 0xb18) * 0xc58 + 0xb28 + DAT_00510BD8) != *(int *)(this + 4));
    bool b3 = (*(int *)(iVar6 + 0xb24) == -1)
        || (*(int *)(*(int *)(iVar6 + 0xb24) * 0xc58 + 0xb28 + DAT_00510BD8) != *(int *)(this + 4));
    bool b4 = (*(int *)(iVar6 + 0xb20) == -1)
        || (*(int *)(*(int *)(iVar6 + 0xb20) * 0xc58 + 0xb28 + DAT_00510BD8) != *(int *)(this + 4));
    if (b1 && b2 && b3 && b4) {
      uint u_var4 = FUN_00432753(this, NULL);
      return u_var4 < (uint)*house_type[1];
    }
  }
  return true;
}
```

### FUN_0043242c — Walidacja typu 2 (dom) dla param_2 == 2 (VA 0x43242C)

Wywoływane z `FUN_0043230A` gdy `param_2 == 2`.

```c
uint FUN_0043242c(void *this, int param_1) {
  if (!FUN_004325db(this, param_1)) return 0;
  int *house_type = *(int *)(this + 0x14) * 0x624 + DAT_005113A0;
  int iVar10 = param_1 * 0xc58 + DAT_00510BD8;
  if (*house_type != 2) {
    bool b_var1 = false;
    byte *pb_var3 = FUN_0043267f(this, param_1);
    if (pb_var3 != NULL && (*pb_var3 & 2) != 0) b_var1 = true;
    uint u_var4 = FUN_00435504(iVar10);
    int i_var6 = house_type[3];
    int i_var8 = 0;
    if (i_var6 > 0) {
      uint *pu_var7 = house_type + 4;
      do {
        if (*pu_var7 == u_var4) break;
        i_var8++;
        pu_var7 += 2;
      } while (i_var8 < i_var6);
    }
    uint u_var2 = u_var4;
    if (i_var8 != i_var6 && (b_var1 || (int)FUN_0043289b(this, u_var4) < house_type[i_var8 * 2 + 5])) {
      if ((u_var4 != 0x1e || i_var6 = 0, *(int *)(this + 0x14) != 0x25)
          && (i_var6 = *(int *)(iVar10 + 0x1c), i_var6 != 0x41 && i_var6 != 0)) {
        int i_var10_inner = FUN_00461c14(*(int *)(iVar10 + 0x18), i_var6);
        uint u_var5 = FUN_004316f3(this, i_var10_inner, 1);
        if (u_var5 == 0) {
          u_var5 = FUN_004316f3(this, i_var10_inner, 0);
          if (u_var5 == 0) return 0;
        }
        return 1;
      }
      return (uint)(i_var6 >> 8) & 1;
    }
  }
  return 0;
}
```

### FUN_00432516 — Walidacja typu 4 (dom) dla param_2 == 8 (VA 0x432516)

Wywoływane z `FUN_0043230A` gdy `param_2 == 8`.

```c
bool FUN_00432516(void *this, int param_1) {
  if (!FUN_004325db(this, param_1)) return false;
  int *house_type = *(int *)(this + 0x14) * 0x624 + DAT_005113A0;
  if (*house_type != 4) return false;
  byte *owner_entry = FUN_0043267f(this, param_1);
  if (owner_entry == NULL || (*owner_entry & 8) == 0) {
    uint u_var3 = FUN_004326ec(this, 8);
    return u_var3 < (uint)house_type[2];
  }
  return true;
}
```

### FUN_0043256b — Walidacja typu 7 (dom) dla param_2 == 4 (VA 0x43256B)

Wywoływane z `FUN_0043230A` gdy `param_2 == 4`.

```c
bool FUN_0043256b(void *this, int param_1) {
  if (!FUN_004325db(this, param_1)) return false;
  int i_var3 = FUN_00435504(param_1 * 0xc58 + DAT_00510BD8);
  if (i_var3 != 7) return false;
  if (*(int *)(this + 0x2c) != 3 && FUN_00433386(this)) return false;
  byte *pb_var4 = FUN_0043267f(this, param_1);
  if (pb_var4 != NULL && (*pb_var4 & 4) != 0) return true;
  int i_var3_inner = FUN_004326ec(this, 4);
  uint u_var5 = FUN_00433056(this);
  return i_var3_inner < (int)u_var5;
}
```

### FUN_00441b83 — Czyszczenie stanu jednostki (VA 0x441B83)

Wywoływane z `FUN_004417C7` i `FUN_00441800`. Złożona funkcja zarządzania stanem jednostki w zależności od +0xACC.

```c
void FUN_00441b83(int param_1) {
  int i_var7 = *(int *)(param_1 + 0xACC);
  // ... złożona logika zarządzania stanem budynku jednostki
  // Obsługuje stany: 1, 2, 3, 4, 5
  // Wywołuje: FUN_0042D7D3, FUN_00431D2A, FUN_0044B7B5, FUN_0045C709, FUN_0044B9AB
  *(int *)(param_1 + 0xACC) = 0;
}
```

---

## 9. Podsumowanie wszystkich funkcji z pseudokodem

Łącznie **59 funkcji** z pełną implementacją w pseudokodzie Rust (`.ai/re_rust/all_functions.rs`) i dokumentacji C (`.ai/docs/re/re_functions_comprehensive.md`).

### Kategorie:

| Kategoria | Liczba | Przykłady |
|-----------|--------|-----------|
| Tick jednostki i produkcja | 8 | FUN_00473461, FUN_0042DA65, FUN_0042DB20, FUN_0042D848, FUN_0042D9A3, FUN_0044A0D9, FUN_0043E8A7, FUN_0044B2FA |
| Operacje budynku | 12 | FUN_00494f01, FUN_00495e0c, FUN_0049599B, FUN_00494996, FUN_00431ff5, FUN_004320bf, FUN_004346a2, FUN_0042c016, FUN_0042c064, FUN_004417c7, FUN_00441800, FUN_0043bfbc |
| UI i wybór gooda | 7 | FUN_00449F2F, FUN_0044B226, FUN_0044B5D9, FUN_0044B5E7, FUN_0043D037, FUN_0042c909, FUN_00409abc |
| Helpery i bramki | 14 | FUN_0042c6f0, FUN_0042c597, FUN_0042c5b3, FUN_0042c676, FUN_0042c6bc, FUN_0042c6cf, FUN_0042c8a8, FUN_004316e0, FUN_004322da, FUN_0043e09A, FUN_004319d7, FUN_00434142, FUN_0042c63b, FUN_0042c64f |
| Sprite'y | 4 | FUN_0042f710, FUN_0042f754, FUN_0042f776, FUN_0042f798 |
| Inne (REA batch 1-4) | 14 | FUN_0047e062, FUN_0042878e, FUN_0042c73b, FUN_0042c783, FUN_0045c66e, FUN_00461c14, FUN_0043bf90, FUN_004530d6, FUN_0042c68a, FUN_0043234d, FUN_0043242c, FUN_00432516, FUN_0043256b, FUN_00441b83 |

---

## 10. Niezbywalne problemy i kolejne kroki

| # | Zadanie | Priorytet |
|---|---------|-----------|
| 1 | Dodać kod konwersji drewno→węgiel dla typu 57 | Krytyczny |
| 2 | Zweryfikować patch na imm 0x6B82 w FUN_00473461, FUN_0042D9A3, FUN_0042D97D | Wysoki |
| 3 | Sprawdzić czy FUN_00495e0c modyfikuje building+0x64 czy tylko DAT_00568CA8 | Wysoki |
| 4 | Znaleźć gdzie ładuje się goodtypes.cif do DAT_00511698/6A0/6A4 | Średni |
| 5 | Naprawić Storage UI (pętla 0x415E8E crashuje dla bound extended) | Średni |
| 6 | Dodać filtr niezdefiniowanych budynków (Etap 4) | Średni |
| 7 | Przetestować zmianę logictype (opcja A) w houses.ini | Wysoki |
| 8 | Zbadać przyczynę braku animacji idle mieszkańców | Niski |
