# RE — Kluczowe funkcje CN.PLMOD.exe (pseudocode z Ghidry)

Źródło: dekompilacje Ghidra 12.1.4 w `.ai/re_out/decomp_*.md`. Pseudocode to wyjście dekompilatora, nie oryginalne źródło.

---

## FUN_00473461 — Tick jednostki / produkcja (VA 0x473461) [ROOT CAUSE]

```c
// __cdecl lub thiscall, this = jednostka
void FUN_00473461(unit *this, int param_1) {
  // Pobierz typ budynku, w którym jest jednostka
  int bldg_type = *(int *)(*(int *)(this + 0xB34) * 0x7E0 + 0x14 + DAT_00510BD0);

  uint uVar6; int local_8;

  // TYLKO typy 38 (szkoła) i 39 (koszary)! Typ 57 (smolarnia) → wczesny return.
  if (bldg_type == 0x26) {          // typ 38
    // odczytuje uVar6 i local_8 z budynku (+8, +0xC)
  } else if (bldg_type == 0x27) {   // typ 39
    // odczytuje uVar6 z plemienia (offset 0x6740)
    local_8 = 0;
  } else {
    return;  // TYP 57 (smolarnia) NIE JEST OBSŁUGIWANY
  }

  if (uVar6 != 0) {
    // Próg z plemienia (UWAGA: używa starego imm 0x6B82, powinno być 0x8578)
    int tribe_offset = *(int *)(this + 0x14) * 0x6B82;  // STARA wartość!
    uint uVar5 = *(uint *)(DAT_00511200 + 0x6740 + (tribe_offset + uVar6) * 4);
    if (local_8 != 0)
      uVar5 += *(uint *)(DAT_00511200 + 0x6820 + (tribe_offset + local_8) * 4);

    // Timer +0x158 vs próg
    if (*(uint *)(this + 0x158) < uVar5) {
      // Inkrementuj timer
      if (10000 - param_1 < *(uint *)(this + 0x158))
        *(uint *)(this + 0x158) = 10000;
      else
        *(uint *)(this + 0x158) += param_1;
    } else {
      // Timer osiągnął próg — wykonaj akcję produkcji
      uVar5 = FUN_0042D9D7(this, uVar6);
      if ((char)uVar5 == 0) {
        *(byte *)(uVar6 + 0x15C + (int)this) = 1;   // flaga +0x15C+good
        FUN_0045BBAA(this, uVar6);                  // dźwięk
      }
      if ((local_8 != 0) && (*(char *)(local_8 + 0x195 + (int)this) == 0)) {
        *(char *)(local_8 + 0x195 + (int)this) = 1; // **USTAW +0x195[good] = 1**
        FUN_0045BB51(this, local_8);                // dźwięk
      }
      *(uint *)(this + 0x158) = 0;                  // reset timer

      if (*(uint *)(this + 0x18) == uVar6) {        // job jednostki == good
        FUN_0044A0D9(this);                         // ustaw +0x195 dla goodów joba
        FUN_0044B2FA(this);                         // ustaw status produkcji +0x21C
      } else {
        FUN_00449F2F(this, uVar6);                  // UI: zmień selected good
      }
      FUN_00449BDA(this);

      // Jeśli jednostka może produkować good local_8
      if ((local_8 != 0) && FUN_0042DA65(this, local_8)) {
        FUN_0043E8A7(this, local_8);                // UI: wybierz good do produkcji
      }
      // ...dźwięk, efekt
    }
  }
}
```

**Wniosek:** Smolarnia (typ 57) nie przechodzi tej funkcji — brak timera, brak `+0x195[66]`, brak produkcji.

---

## FUN_0044A0D9 — Ustawia +0x195 dla goodów joba (VA 0x44A0D9)

Wywoływana TYLKO z FUN_00473461 gdy `job == uVar6`. Dla smalarza (job 56) i uVar6 = good z budynku (np. drewno 5) — nie przechodzi.

```c
void FUN_0044A0D9(unit *this) {
  // Pętla po goodach z job block (+0xD8)
  // Dla każdego gooda:
  //   jeśli FUN_0042D9A3 (progi plemienia) LUB race == 2:
  //     jeśli good == 56: +0x1CD = 1, pomiń +0x195
  //     jeśli job == 16 i good == 57: +0x195[57] = 1 (fall through)
  //     jeśli job != 16: +0x195[good] = 1
  //   GOODS_A2[good] = 1; GOODS_B[good] = 1
}
```

---

## FUN_0042DA65 — Bramka "czy jednostka może produkować good" (VA 0x42DA65)

```c
bool FUN_0042DA65(unit *this, int good) {
  return *(byte *)(this + 0x195 + good) != 0
      && FUN_0042DB20(this, good)              // good na liście job block
      && (FUN_0042D848(this, good)             // needforgood: jednostka ma surowce
          || FUN_0042D9A3(this, good)          // progi plemienia
          || race == 2);
}
```

---

## FUN_004316F3 — Bramka budynku dla gooda (revmap) (VA 0x4316F3)

```c
bool FUN_004316F3(house_type *ht, int good, char flag) {
  // Używa stock revmap z rekordu domu (+0x37C)
  // Zwraca czy budynek może przyjąć/produkcja gooda
}
```

---

## FUN_00431F37 — Zwraca revmap[good] z rekordu domu (VA 0x431F37)

```c
int FUN_00431F37(house_type *ht, int good) {
  return ht->stock_revmap[good];  // +0x37C + good*4
}
```

---

## FUN_0043267F — Szukaj właściciela w building+0x644 (VA 0x43267F)

```c
// Szuka w tablicy 20 wpisów × 4 B w building+0x644 wpisu równego param_1 (owner)
// Zwraca (index+100)*0x10 + building jeśli znajdzie, 0 jeśli nie.
int FUN_0043267F(building *bldg, int owner) {
  for (int i = 0; i < 20; i++) {
    if (*(int *)(bldg + 0x644 + i * 4) == owner)
      return (i + 100) * 0x10 + (int)bldg;
  }
  return 0;
}
```

---

## FUN_004E21B7 — Renderer tekstu UI (VA 0x4E21B7) [NIE job dispatcher!]

Poprzednia dokumentacja błędnie nazywała to "job dispatcherem". To renderowanie tekstu z tagami.

```c
byte * FUN_004E21B7(void *param_1, int x, byte *start_pos, int max_width,
                    void *building_ctx, byte *font_ctx, byte *text) {
  if (text == NULL) return NULL;
  byte *pos = start_pos;
  int line_height = *(int *)((int)building_ctx + 8) + 2;
  int cursor_x = x;
  byte *p = text;

  while (true) {
    byte b = *p++;
    if (b == 0) return pos + (line_height - (int)start_pos);
    if (b == 9) {  // tab
      cursor_x += FUN_00439633(building_ctx, 0x69);
      continue;
    }
    if (b == 10 || b == 0x0D) {  // newline
      if (*p == 10) p++;
      pos += line_height;
      cursor_x = x;
      continue;
    }
    if (b == 0x20) continue;  // spacja
    if (b == 0x7B) {  // '{' — tag
      char *end = strchr((char *)p, '}');
      if (end != NULL) {
        if (FUN_004E6760(p, "newline", strlen("newline")) == 0) {
          pos += line_height;
          cursor_x = x;
        }
        p = end + 1;
      }
    } else if (b > 0x1F) {
      // Zbierz słowo
      char word[101]; int wi = 0;
      byte *q = p;
      while (wi < 100) {
        byte c = *q;
        if (c == 0 || c == 0x0D || c == 0x20 || c < 0x20 || c == 0x7B) break;
        word[wi++] = c;
        q++;
      }
      word[wi] = 0;
      int word_w = FUN_0043967D(building_ctx, word);
      if (max_width <= word_w + cursor_x) {
        pos += line_height;
        cursor_x = x;
      }
      FUN_0040ECF9(param_1, building_ctx, font_ctx, cursor_x, pos, word);
      cursor_x += word_w;
    }
  }
}
```

---

## FUN_0046D53A — Interakcja z budynkiem / panel rzemieślnika (VA 0x46D53A)

```c
void __fastcall FUN_0046D53A(void *this) {  // this = UI kontekst budynku
  // Pobierz house z listy (DAT_00511728)
  void *list = FUN_0041C61E(DAT_00511728, *(int *)(this + 0xB44));
  int *piBegin = FUN_0041C7F1(list);
  int *piEnd = FUN_0041C81F(list);

  if (piBegin == piEnd || piBegin == NULL) {
    *(int *)(this + 0x368) = 1;
    goto done;
  }

  char *building1 = NULL;
  if (FUN_0041C9DD(piBegin)) building1 = (char *)(*piBegin * 0x7E0 + DAT_00510BD0);
  char *building2 = NULL;
  if (FUN_0041C9DD(piEnd))   building2 = (char *)(*piEnd   * 0x7E0 + DAT_00510BD0);

  // Walidacja: oba budynki muszą istnieć, być zbudowane (+0x200 == 0), kategoria == 3
  if (((building1 == NULL || building2 == NULL || building1[0x7D0] != 0)) ||
      ((building2[0x7D0] != 0 || *(int *)(building1 + 0x2C) != 3 ||
        *(int *)(building2 + 0x2C) != 3))) {
    *(int *)(this + 0x36C) = 3; *(int *)(this + 0x374) = 2;
    goto done;
  }

  // ...logika stanów +0xACC (0/2/4) i +0xA68 (5/6):
  // stan 6 + good 66: inkrementuje licznik
  //   DAT_00510BC4 + 0x4A30 + (x*0x12A0 + building+0xC)*4 += 1

done:
  FUN_0041C84F(list);
  return;
}
```

---

## FUN_0046E1BE — Sprawdź dostępność budynku do interakcji (VA 0x46E1BE)

```c
uint __thiscall FUN_0046E1BE(void *this, int param_1) {
  // this = UI kontekst, param_1 = dane budynku (+0x24 = x, +0x26 = y)
  if (!FUN_0042C70A(this)) return 0;
  if (!FUN_0044BCF3(tribe_house, *(int *)(this + 4))) return 0;

  char *tribe_house = ...;
  short *pos = FUN_004411CA(tribe_house);
  if (FUN_0043F8F3(tribe_house) || *(int *)(tribe_house + 0x4FC) == 1 ||
      FUN_0042AA24(*pos, pos[1], *(short *)(param_1 + 0x24), *(ushort *)(param_1 + 0x26)) > 5) {
    *(int *)(this + 0x36C) = 0;
    *(int *)(this + 0x368) = (*(char *)(this + 0xB51) == 0) ? 0x15 : 1;
    return 1;
  }
  // ...sprawdź dystans FUN_0043B35F, ustaw +0x36C/+0x374
  return 1;
}
```

---

## FUN_004A693B — Renderer panelu informacji budynku (VA 0x4A7297)

Renderuje panel UI z nazwą, kosztem, stanem, zapasami towarów. Iteruje po goodach budynku:
- `+0x60` = stock_count
- `+0x64` = stocks (good, qty)
- Rysuje ikony `gfxgood_d_1__s_d__d__d` i wartości tekstowe
- Stany `local_1c` 0-10 renderują różne sekcje panelu (nazwa, koszt, produkcja, zapasy, itp.)

---

## FUN_004C227C — Renderer listy budynków/typów UI (VA 0x4C23D8)

Iteruje po instancjach budynków gracza (`DAT_00568C0C`, stride 0x8BC), dla każdego pobiera goodi produkcji z house_type (`+0x484` count, `+0x488` list) przez `FUN_00432A48` i renderuje wiersze listy UI.

---

## Parserzy plików danych

| Adres | Funkcja | Plik | Kluczowe walidatory (patchowane) |
|-------|---------|------|----------------------------------|
| 0x41531D | FUN_0041531D | houses.ini | parsuje [logichousetype], logictype, logicproduction |
| 0x413E7B | FUN_00413E7B | tribetypes.ini | parruje allowgood/allowhouse/jobEnablesGood |
| 0x41592E | FUN_0041592E | goodtypes.ini | alloc `mov esi, 0x35A0`→`0x6730`; validator `cmp eax,0x42;jge`→imm 0x7F |
| 0x415403 | FUN_00415403 | logictype | `cmp` type < 0x37 → patched 0x7F; `push 0x42; rep stosd` revmap -1 |
| 0x41575C | FUN_0041575C | logicstock | `cmp [esi+0x60],0x42; je skip`; good guard `cmp edi,0x42;jg` (66 accepted) |
| 0x41581D | FUN_0041581D | logicproduction | `cmp [esi+0x484],0x14; je skip`; `cmp eax,0x42;jge skip` → 0x7F |

## Nowe funkcje bâtiments i produkcji (REA)

### FUN_00494f01 (VA 0x494F01) — Główna operacja budynku

Wywoływana z `FUN_0049067f` (renderer mapy) dla każdego budynku na mapie (typ obiektu 0x02).
To jest główna funkcja operacji budynku — nie istnieje osobny "building production tick".

```c
void FUN_00494f01(uint building_idx, void *param_2, uint *param_3, uint *param_4, int param_5, void *param_6) {
  void *bldg = building_idx * 0x7E0 + DAT_00510BD0;
  FUN_004316D0(bldg);  // inicjalizacja budynku
  void *pBldgInst = house_type_idx * 0x8BC + DAT_00568C0C;
  int *bldgTypeData = building_idx * 0xD0 + DAT_00568CA8;
  // sprawdza built_flag (+0x200)
  // wywołuje FUN_0049A65E (produkcja/zawartość)
  // wywołuje FUN_0049599B
  // wywołuje FUN_00495E0c WEWNĄTRZ siebie
}
```

### FUN_00495e0c (VA 0x495E0c) — Zarządzanie zapasami/produkcją budynku

Wywoływane wewnątrz `FUN_00494f01`. Zarządza licznikami w `DAT_00568CA8 + type*0xD0` (dane typu budynku), nie w `building+0x64` (stocks instancji). Używa `_rand()` dla losowego tworzenia produktów.

### FUN_0047e062 (VA 0x47E062) — Flagi typu budynku

Ustawia flagi w tabelach danych:
- `param_1 == 0x11`: `*(byte *)(param_3 * 0xD0 + 0xcc + DAT_00568CA8) = value & 1;`
- `param_1 == 0x10`: flaga w `DAT_00568CB0`
- `param_1 == 0x0E`: flaga w `DAT_0055529C`

### Sprite'y surowców (VA)

| Funkcja | Adres | Tabela | Opis |
|---------|-------|--------|------|
| `FUN_0042f710` | 0x42F710 | `DAT_00511698` | Sprite access table 1: `idx * 2 (+1 if flag>1)` |
| `FUN_0042f754` | 0x42F754 | `DAT_005116A0` | Sprite access table 2 |
| `FUN_0042f776` | 0x42F776 | `DAT_005116A4` | Sprite access table 3 |
| `FUN_0042f798` | 0x42F798 | — | Sprite budynku/towaru: wywołuje FUN_0047FFC0 + FUN_0042f776 |

Jak good ID mapuje się na sprite: `good_id * 2` → indeks w tablicy `DAT_00511698/6A0/6A4` → `FUN_0042BCAE(tab, index)` zwraca wskaźnik na dane sprite'u (obraz z .cif).

## Parserzy plików danych (kontynuacja)

