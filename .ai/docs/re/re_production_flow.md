# RE — Przepływ produkcji w CN.PLMOD.exe (Etap 2)

## Funkcja tick jednostki: FUN_00473461 (VA 0x473461)

To jest główna funkcja "pracy/tick" jednostki. Wywoływana co tick dla każdej jednostki.

### Pseudocode (skrócony)

```c
void FUN_00473461(unit *this, int param_1) {
  // Pobierz typ budynku, w którym jest jednostka
  int bldg_type = *(int *)(*(int *)(this + 0xb34) * 0x7e0 + 0x14 + DAT_00510bd0);
  
  uint uVar6; int local_8;
  if (bldg_type == 0x26) {  // typ 38
    // ... odczytuje uVar6 i local_8 z budynku (offset +8, +0xc)
  } else if (bldg_type == 0x27) {  // typ 39
    // ... odczytuje uVar6 z plemienia (0x6740 offset)
    local_8 = 0;
  } else {
    return;  // TYLKO typy 38 i 39! Dla smalarni (57) nic nie robi
  }
  
  if (uVar6 != 0) {
    // Oblicz próg z plemienia (UWAGA: używa 0x6b82, stary rozmiar rekordu!)
    int tribe_offset = *(int *)(this + 0x14) * 0x6b82;
    uVar5 = *(uint *)(DAT_00511200 + 0x6740 + (tribe_offset + uVar6) * 4);
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
      // Timer osiągnął próg — wykonaj akcję
      uVar5 = FUN_0042d9d7(this, uVar6);
      if ((char)uVar5 == 0) {
        *(byte *)(uVar6 + 0x15c + this) = 1;   // ustaw flagę +0x15c+good
        FUN_0045bbaa(this, uVar6);
      }
      if ((local_8 != 0) && (*(char *)(local_8 + 0x195 + this) == 0)) {
        *(char *)(local_8 + 0x195 + this) = 1;  // **USTAW +0x195[good] = 1**
        FUN_0045bb51(this, local_8);
      }
      *(uint *)(this + 0x158) = 0;  // reset timer
      
      if (*(uint *)(this + 0x18) == uVar6) {  // job jednostki == good
        FUN_0044a0d9(this);   // ustaw +0x195 dla wszystkich goodów joba
        FUN_0044b2fa(this);   // ustaw status produkcji +0x21c
      } else {
        FUN_00449f2f(this, uVar6);
      }
      FUN_00449bda(this);
      
      // Jeśli jednostka może produkować good iVar3 (local_8)
      if ((local_8 != 0) && FUN_0042da65(this, local_8)) {
        FUN_0043e8a7(this, local_8);  // UI: wybierz good do produkcji
      }
      
      // ...więcej kodu (dźwięk, efekt)
    }
  }
}
```

### Kluczowe obserwacje z FUN_00473461

1. **Obsługuje tylko typy budynków 0x26 (38) i 0x27 (39)** — dla smalarni (typ 57 = 0x39) robi wczesny `return`. **To znaczy, że produkcja w chałupie węglarskiej NIE jest obsługiwana przez tę funkcję.**

2. **Używa `0x6b82` (stary rozmiar rekordu plemienia)** — powinno być `0x8578` po patchu. Sprawdzić czy jest patch na ten imm w tej funkcji.

3. **Ustawia `+0x195[good] = 1`** gdy timer osiąga próg — to jest źródło flagi "może produkować" w normalnym toku gry.

4. **Wywołuje `FUN_0043e8a7(this, local_8)`** — to UI (wybór gooda do produkcji), nie samo wykonanie produkcji.

### Co to oznacza dla smalarni (typ 57)

- `FUN_00473461` nic nie robi dla smalarni → brak ustawiania `+0x195[66]`, brak timera produkcji
- Nawet jeśli ręcznie ustawimy `+0x195[66]=1`, nie ma kodu który by zużywał drewno i tworzył węgiel
- **Trzeba znaleźć funkcję "building tick" lub "production tick"** która iteruje po budynkach i wykonuje produkcję dla wszystkich typów domów

## Funkcje związane z produkcją (znalezione)

| Adres | Nazwa | Co robi | Uwagi |
|-------|-------|---------|-------|
| 0x473461 | FUN_00473461 | Tick jednostki — timer produkcji, ustawia +0x195 | Tylko typy 38, 39 |
| 0x43e8a7 | FUN_0043e8a7 | UI: wybiera good do produkcji (+0x218, +0x1c, +0x38c) | Nie wykonuje produkcji |
| 0x44a0d9 | FUN_0044a0d9 | Ustawia +0x195 dla wszystkich goodów z job block | Wywoływane z FUN_00473461 |
| 0x44b2fa | FUN_0044b2fa | Ustawia status +0x21c dla goodów joba | UI |
| 0x42da65 | FUN_0042da65 | Bramka: czy jednostka może produkować good | Sprawdza +0x195, job block, budynek |
| 0x4316f3 | FUN_004316f3 | Bramka budynku: czy może przyjąć/produkcja good | Używa revmap |
| 0x44b5d9 | FUN_0044b5d9 | ? | Wywoływane w FUN_0043e8a7 |
| 0x44b5e7 | FUN_0044b5e7 | Ustawia status gooda (0, 0xb, 0xc, 0xd, 0xe) | UI |

## BRAKUJĄCE: Building tick / Production tick

Nie znaleziono funkcji która:
1. Iteruje po instancjach budynków gracza (`DAT_00568c0c`, stride 0x8bc)
2. Dla każdego budynku sprawdza typ i `logicproduction`
3. Zużywa input good (drewno) i tworzy output good (węgiel)

Kandydaci do sprawdzenia (refs do DAT_00568c0c):
- FUN_0047ffc0 (0x47ffc6)
- FUN_0048ea9f (0x48eabd)
- FUN_00494f01 (0x494f31)
- FUN_0049599b (0x4959bd)
- FUN_00495a6d (0x495a95)
- FUN_00495aca (0x495afa)
- FUN_00495e0c (0x495e3a)
- FUN_00495eee (0x495f19)
- FUN_00495f75 (0x495fa0)
- FUN_00495ffc (0x49600f)
- FUN_004c1d1e (0x4c1dd3)
- FUN_004c560b (0x4c5679)

## Następne kroki

1. Zdekomponować FUN_0047ffc0, FUN_00494f01, FUN_00495e0c — szukać pętli po budynkach z logiką produkcji
2. Sprawdzić czy jest patch na `0x6b82` w FUN_00473461 (stary rozmiar rekordu)
3. Jeśli nie ma kodu produkcji dla typów > 39, dodać patch lub code cave
