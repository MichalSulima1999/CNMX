# RE - Job Assignment & Dispatcher - Dokumentacja

**Data:** 2026-10-19
**Cel:** Zrozumieć jak dokładnie przypisywany jest job do jednostki i jak obejść limit 46.

---

## 1. Job Assignment Chain (Potwierdzone)

```
FUN_004B64A6 (unit logic)
    ↓
FUN_004C8919 (dispatcher, case 5 → FUN_004C8F14)
    ↓
FUN_004C8F14 (param_2=5 → FUN_0043242C)
    ↓
FUN_0043242C ← KLUCZOWA FUNKCJA: przypisuje job do unit
```

### FUN_0043242C pseudokod (dokładny):

```c
uint __thiscall FUN_0043242C(void *this, int param_1) {
    // this = building, param_1 = unit_id
    int *piVar9 = (int *)(*(int *)((int)this + 0x14) * 0x624 + DAT_005113A0);
    int iVar10 = param_1 * 0xC58 + DAT_00510BD8;  // unit record
    
    if (*piVar9 != 2) {  // type 2 = budynek produkcyjny
        // ... walidacja ...
        
        // PRZYPISANIE JOB:
        // unit+0x18 = house_type workers[job_idx]
        // Gdzie workers array: house_type+4, house_type+8, itd.
        
        // KOD MOŻE MIEĆ HARDCODED LIMIT:
        // if (job_idx >= 46) return 0;  ← TO JEST PROBLEM
    }
    return result;
}
```

**Wniosek:** FUN_0043242C może mieć wewnętrzny limit workerów, niezależny od limitu w dispatcherze.

---

## 2. Dispatcher Jump Table (Potwierdzone)

### Lokacja:
- **Jump Table:** VA 0x46BE76, 18 wpisów × 4B
- **Case Table:** VA 0x46BEBE, 46 wpisów × 1B
- **Limit:** `CMP EAX, 0x2E` (46)

### Mapowanie (wybrane):

| Job | Case Index | Jump Target | Handler |
|-----|------------|-------------|---------|
| 25 (potter) | 13 | 0x46BDDC | CALL 0x46D53A |
| 26 | 14 | 0x46BDF7 | — |
| 27 | 15 | 0x46BE00 | — |
| 28 | 16 | 0x46BE09 | — |
| 29-46 | 17 | 0x46BE12 | default |
| **56 (smolarz)** | **0** | **0x46BD4A** | **default/error** |

**Problem:** Job 56 → case 0 → domyślny handler (error).

---

## 3. Co już próbowaliśmy

| Metoda | Wynik | Dlaczego nie działa |
|--------|-------|---------------------|
| Patch CMP 0x2E → 0x7F | Crash | Nowe tabele w nieegzekwalnowanej pamięci (0x4F2200) |
| Przeniesienie case table | Żadnych wolnych 127B w .text | Sekcja .text jest gęsto upakowana |
| Hooking przez EtapC.dll | — | EtapC.dll już modifikuje ten sam kod |

---

## 4. Potencjalne rozwiązania

### Opcja A: Rozszerzenie case table w miejscu

1. Znajdź dokładnie 127 bajtów paddingu w .text
2. Skopiuj tam nową case table
3. Patch MOVZX disp32
4. Patch limit

**Problem:** Brak dużych wolnych obszarów w .text.

### Opcja B: Hook na dispatcher entry

Zamiast modyfikować jump table, złap wywołanie dispatchera i obsłuż nowe joby przed oryginalnym kodem:

```c
__declspec(naked) void DispatcherHook() {
    __asm {
        mov eax, [esi+0x18]  ; job ID
        cmp eax, 46
        jb OriginalDispatcher  ; < 46 → oryginał
        cmp eax, 128
        jae OriginalDispatcher ; >= 128 → oryginał
        
        ; Obsługa nowych jobów
        cmp eax, 56
        jne CheckJob57
        call FUN_0046D53A  ; potter handler dla smolarza
        jmp Done
        
    CheckJob57:
        ; ... kolejne joby ...
        
    Done:
        ret
        
    OriginalDispatcher:
        jmp [0x46BD2F]  ; oryginalny dispatcher
    }
}
```

**Zalety:**
- Zero modyfikacji .text
- Maksymalna kompatybilność z EtapC.dll
- Łatwe do debugowania

**Wady:**
- Wymaga wstrzykiwania DLL (ale to już robimy przez launcher)

---

## 5. Brakujące informacje (do sprawdzenia)

### Pytania kluczowe:

1. **Czy FUN_0043242C ma wewnętrzny limit?**
   - Trzeba zdekompilować dokładniej
   - Sprawdzić czy są dodatkowe instrukcje CMP/JA

2. **Czy EtapC.dll modyfikuje ten sam kod?**
   - EtapC.dll może już rozszerzać limity
   - Może kolidować z naszymi patchami

3. **Gdzie są wolne 127B w .text?**
   - Trzeba przeszukać padding między funkcjami
   - Albo użyć code cave w innym miejscu

4. **Jak działa EtapC.dll?**
   - Może on już robi to co próbujemy zrobić
   - Możemy go użyć jako reference

---

## 6. Następne kroki

1. **Zdekompilować FUN_0043242C** - sprawdzić czy ma limit workerów
2. **Znaleźć code cave** - minimum 127B w .text
3. **Sprawdzić EtapC.dll** - zobaczyć co on robi
4. **Zaprojektować prosty DLL hook** - tylko dispatcher + job assignment

---

## Podsumowanie

Problem jest **dwuetapowy**:
1. Dispatcher ma hardcoded limit 46 jobów
2. Job Assignment (FUN_0043242C) może mieć własny limit

Potrzebujemy **hooka DLL** który obsłuże nowe joby, zamiast modyfikować binarkę. To bezpieczniejsze i łatwiejsze do debugowania.