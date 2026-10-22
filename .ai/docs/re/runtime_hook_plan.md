# Runtime Hook System — Plan dla platformy moderskiej

**Cel:** System runtime hooków pozwalający na dodawanie nowych zawodów, budynków, łańcuchów produkcji bez limitów jobów (46) i bez modyfikacji binarki (oprócz jednego hooka).

**Data:** 2026-10-18  
**Autor:** REA + Ghidra 12.1.4

---

## 1. Architektura ogólna

```
┌─────────────────────────────────────────────────────────────┐
│                    CN.PLMOD.exe (Runtime)                    │
├─────────────────────────────────────────────────────────────┤
│  Oryginalny kod                                              │
│  ├─ FUN_0046BAD7 (Dispatcher) ──► HOOK 1 (Job Dispatcher)  │
│  ├─ FUN_0043242C (Job Assignment) ──► HOOK 2 (Job Map)    │
│  ├─ FUN_0046D53A (Potter Handler) ──► HOOK 3 (Production) │
│  └─ FUN_0044B910 (Stock Update) ──► HOOK 4 (Stock System) │
├─────────────────────────────────────────────────────────────┤
│  Runtime Hook System (nasza pamięć)                          │
│  ├─ JobRegistry: job_id → JobDefinition                    │
│  ├─ ProductionRegistry: building_type → ProductionChain    │
│  ├─ GoodRegistry: good_id → GoodDefinition                 │
│  └─ UIRegistry: job_id → UIStrings                         │
├─────────────────────────────────────────────────────────────┤
│  Modding Tools API (IPC/Shared Memory)                      │
│  ├─ RegisterJob()           │  UnregisterJob()              │
│  ├─ RegisterProduction()    │  UnregisterProduction()       │
│  ├─ RegisterGood()          │  UnregisterGood()             │
│  ├─ RegisterUIStrings()     │  GetUIStrings()               │
│  └─ HotReload()             │  SaveConfig()                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Punkty zaczepienia (Hook Points)

### Hook 1: Job Dispatcher (FUN_0046BAD7, 0x46BD2F)

**Lokalizacja:** `0x46BD2F` - `MOV EAX, [ESI+0x18]` → `CMP EAX, 0x2E` → `JA 0x46BE1B`

**Obecny kod:**
```asm
0x46BD2F: MOV EAX, [ESI+0x18]     ; job ID
0x46BD32: DEC EAX                  ; job - 1
0x46BD33: CMP EAX, 0x2E            ; limit 46
0x46BD36: JA  0x46BE1B             ; default
0x46BD3C: MOVZX EAX, [EAX+0x46BEBE] ; case_table
0x46BD43: JMP [EAX*4+0x46BE76]     ; jump_table
```

**Hook:**
```asm
; Nasz kod (w code cave):
HookedDispatcher:
    mov eax, [esi+0x18]        ; job ID
    cmp eax, 0x2E              ; 46
    jb  OriginalDispatcher     ; < 46 → oryginał
    ; >= 46 → sprawdź naszą mapę
    mov edx, [g_CustomJobMap]  ; nasza tablica
    test edx, edx
    jz  OriginalDefault
    mov eax, [edx+eax*4]       ; lookup handler
    test eax, eax
    jz  OriginalDefault
    jmp eax                    ; wywołaj custom handler
OriginalDefault:
    jmp 0x46BE1B               ; oryginalny default
```

### Hook 2: Job Assignment (FUN_0043242C, 0x43242C)

**Lokalizacja:** Przypisuje `unit+0x18 = house_type_workers[job_idx]`

**Obecny kod:**
```c
// FUN_0043242C pseudocode:
iVar6 = piVar9[3];                    // worker_count
puVar7 = (uint *)(piVar9 + 4);        // workers array
do {
    if (*puVar7 == uVar4) break;      // znajdź worker
    puVar7 = puVar7 + 2;
} while (iVar8 < iVar6);
unit+0x18 = *puVar7;                  // ← TU JOB!
```

**Hook:** Pozwala rejestrować nowe joby bez limitu workerów w house_type.

### Hook 3: Production Chain (FUN_0046D53A → FUN_0046E52E)

**Lokalizacja:** Potter handler → logika produkcji → FUN_0044B910 (stock update)

**Cel:** Pozwala na dowolne łańcuchy produkcji zdefiniowane w INI.

### Hook 4: Stock System (FUN_0044B910)

**Lokalizacja:** Dodaje towar do tribe house stock.

---

## 3. Struktury danych (Runtime)

### JobDefinition
```c
typedef struct {
    uint32_t job_id;                  // np. 26
    char name[32];                    // "Smolarz"
    char description[128];            // "Produkuje węgiel z drewna"
    uint32_t building_type;           // house_type (np. 57)
    uint32_t output_good;             // good_id (np. 66)
    uint32_t input_goods[8];          // lista good_id wejściowych
    uint32_t input_counts[8];         // ilości
    uint32_t worker_count;            // ile pracowników
    void* handler;                    // custom handler (opcjonalnie)
    uint32_t flags;                   // bitflags
} JobDefinition;
```

### ProductionChain
```c
typedef struct {
    uint32_t building_type;           // house_type
    uint32_t output_good;             // wynik
    uint32_t input_goods[8];          // surowce
    uint32_t input_counts[8];
    uint32_t production_time;         // ticków na cykl
    uint32_t worker_job;              // job_id pracownika
    uint32_t max_workers;             // max pracowników
    bool requires_building_completion; // true = po budowie
} ProductionChain;
```

### GoodDefinition
```c
typedef struct {
    uint32_t good_id;
    char name[32];
    char description[128];
    uint32_t type;                    // 12 = surowiec, itp.
    bool is_input;                    // czy wejściowy
    bool is_produced_in_house;        // czy produkowany w budynku
    uint32_t atomic_for_production;   // dla mapy atomów
    // ... reszta z goodtypes.ini
} GoodDefinition;
```

---

## 4. API dla Modding Tools (GUI)

### IPC Interface (Named Pipe / Shared Memory)

```cpp
// Named Pipe: \\.\pipe\CNMod_ModdingAPI
// Lub Shared Memory: "CNMod_Modding_Shared"

// Komendy:
enum Command {
    CMD_REGISTER_JOB = 1,
    CMD_UNREGISTER_JOB = 2,
    CMD_REGISTER_PRODUCTION = 3,
    CMD_UNREGISTER_PRODUCTION = 4,
    CMD_REGISTER_GOOD = 5,
    CMD_UNREGISTER_GOOD = 6,
    CMD_REGISTER_UI_STRINGS = 7,
    CMD_HOT_RELOAD = 8,
    CMD_SAVE_CONFIG = 9,
    CMD_GET_STATUS = 10,
};

// Struktura żądania:
struct Request {
    uint32_t command;
    uint32_t request_id;
    uint32_t payload_size;
    uint8_t payload[];  // JSON
};

// Odpowiedź:
struct Response {
    uint32_t request_id;
    int32_t result;  // 0 = OK, <0 = error
    uint32_t payload_size;
    uint8_t payload[];  // JSON
};
```

### JSON Payloads

**RegisterJob:**
```json
{
  "job_id": 26,
  "name": "Smolarz",
  "description": "Produkuje węgiel z drewna",
  "building_type": 57,
  "output_good": 66,
  "input_goods": [5],
  "input_counts": [10],
  "worker_count": 1,
  "flags": 0
}
```

**RegisterProduction:**
```json
{
  "building_type": 57,
  "output_good": 66,
  "input_goods": [5],
  "input_counts": [10],
  "production_time": 100,
  "worker_job": 26,
  "max_workers": 1,
  "requires_building_completion": true
}
```

**RegisterUIStrings:**
```json
{
  "job_id": 26,
  "ui_name": "Smolarz",
  "ui_description": "Produkuje węgiel z drewna",
  "ui_icon": "smolarz.bmp"
}
```

---

## 5. Implementacja Hooków (Kroki)

### Krok 1: Alokacja pamięci (DLL Inject / Loader)

```cpp
// W loaderze (przed uruchomieniem gry):
void* g_JobRegistry = VirtualAlloc(NULL, 0x10000, MEM_COMMIT|MEM_RESERVE, PAGE_READWRITE);
void* g_ProductionRegistry = VirtualAlloc(NULL, 0x10000, MEM_COMMIT|MEM_RESERVE, PAGE_READWRITE);
void* g_GoodRegistry = VirtualAlloc(NULL, 0x10000, MEM_COMMIT|MEM_RESERVE, PAGE_READWRITE);
void* g_UIRegistry = VirtualAlloc(NULL, 0x10000, MEM_COMMIT|MEM_RESERVE, PAGE_READWRITE);

// Inicjalizuj domyślne joby (z oryginalnej gry)
InitializeDefaultJobs();
```

### Krok 2: Hook Dispatcher (FUN_0046BAD7)

```asm
; Code cave na końcu .text lub w nowej sekcji
HookDispatcher:
    pushad
    mov eax, [esi+0x18]     ; job ID
    cmp eax, 0x2E           ; 46
    jb OriginalDispatcher
    
    ; Custom job lookup
    mov edi, [g_JobRegistry]
    test edi, edi
    jz OriginalDefault
    
    mov eax, [edi + eax*4]  ; handler
    test eax, eax
    jz OriginalDefault
    
    popad
    jmp eax                 ; custom handler
    
OriginalDefault:
    popad
    jmp 0x46BE1B            ; oryginalny default
```

### Krok 3: Named Pipe Server (w wątku)

```cpp
DWORD WINAPI ModdingAPIThread(LPVOID) {
    HANDLE pipe = CreateNamedPipe(
        L"\\\\.\\pipe\\CNMod_ModdingAPI",
        PIPE_ACCESS_DUPLEX,
        PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE | PIPE_WAIT,
        1, 4096, 4096, 0, NULL
    );
    
    while (ConnectNamedPipe(pipe, NULL)) {
        Request req = ReadRequest(pipe);
        Response resp = ProcessRequest(req);
        WriteResponse(pipe, resp);
        DisconnectNamedPipe(pipe);
    }
    return 0;
}
```

---

## 6. Integracja z łańcuchami produkcji

### Rejestracja nowego łańcucha (przykład smolarni):

```json
// 1. Rejestracja zawodu
{
  "command": "REGISTER_JOB",
  "payload": {
    "job_id": 26,
    "name": "Smolarz",
    "building_type": 57,
    "output_good": 66,
    "input_goods": [5],
    "input_counts": [10],
    "worker_count": 1
  }
}

// 2. Rejestracja produkcji
{
  "command": "REGISTER_PRODUCTION",
  "payload": {
    "building_type": 57,
    "output_good": 66,
    "input_goods": [5],
    "input_counts": [10],
    "production_time": 100,
    "worker_job": 26,
    "max_workers": 1,
    "requires_building_completion": true
  }
}

// 3. Rejestracja UI
{
  "command": "REGISTER_UI_STRINGS",
  "payload": {
    "job_id": 26,
    "ui_name": "Smolarz",
    "ui_description": "Produkuje węgiel z drewna"
  }
}
```

### Wgrywanie do gry (Hot Reload):

```cpp
void HotReload() {
    // 1. Załaduj INI do registrów
    LoadHousesINI();      // parsuje logicworker, logicstock, logicproduction
    LoadGoodTypesINI();   // parsuje goodtypes
    LoadTribeTypesINI();  // parsuje jobDefaultGood, jobEnablesGood
    
    // 2. Zbuduj rejestry
    RebuildJobRegistry();
    RebuildProductionRegistry();
    RebuildGoodRegistry();
    
    // 3. Odśwież UI (jeśli otwarte)
    InvalidateUI();
}
```

---

## 7. Szczegóły implementacji hooków

### Hook 1: Dispatcher (JMP Hook)

**Adres:** `0x46BD2F` (5 bajtów: `8B 46 18 48 3D`)

**Patch:**
```asm
; Oryginalny (5 bajtów):
8B 46 18          MOV EAX, [ESI+0x18]
48                DEC EAX
3D 2E 00 00 00    CMP EAX, 0x2E

; Patch (JMP do hooka - 5 bajtów):
E9 XX XX XX XX    JMP HookDispatcher
90                NOP (padding)
```

### Hook 2: Job Assignment (CALL Hook)

**Adres:** `0x43242C` (przed pętlą szukania workera)

**Hook:** Wstrzyknięcie sprawdzenia naszego rejestru przed pętlą.

### Hook 3: Production (FUN_0046E52E)

**Lokalizacja:** Wywoływana z potter handlera.

---

## 8. Pliki konfiguracyjne (INI → Registry)

### Automatyczna synchronizacja:

```cpp
void LoadHousesINI() {
    INIParser parser("CN.PLMOD/types/houses.ini");
    for (auto& block : parser.GetBlocks("logichousetype")) {
        JobDefinition job;
        job.job_id = block.GetInt("logictype");
        job.building_type = block.GetInt("logictype");
        job.worker_count = 0;
        
        // logicworker job_id count
        for (auto& worker : block.GetMulti("logicworker")) {
            job.input_goods[job.worker_count] = worker.job_id;
            job.worker_count++;
        }
        
        // logicstock
        for (auto& stock : block.GetMulti("logicstock")) {
            if (stock.is_output) job.output_good = stock.good_id;
            else job.input_goods.push_back(stock.good_id);
        }
        
        // logicproduction
        job.output_good = block.GetInt("logicproduction");
        
        g_JobRegistry[job.job_id] = job;
    }
}
```

---

## 9. Plan wdrożenia (Fazy)

| Faza | Zadanie | Czas | Status |
|------|---------|------|--------|
| 1 | **Analiza hook points** (gotowe) | 1d | ✅ |
| 2 | **Loader DLL** (inject + alloc) | 2d | 🔄 |
| 3 | **Hook 1: Dispatcher** (JMP) | 1d | ⏳ |
| 4 | **Named Pipe Server** | 1d | ⏳ |
| 5 | **JSON Parser + Registry** | 2d | ⏳ |
| 6 | **Hook 2: Job Assignment** | 1d | ⏳ |
| 7 | **Hook 3: Production** | 1d | ⏳ |
| 8 | **Hot Reload + INI Sync** | 1d | ⏳ |
| 9 | **GUI Modding Tool** | 5d | ⏳ |
| **Total** | | **~12 dni** | |

---

## 10. Testowanie

### Test 1: Smolarnia (Job 26)
1. Zastosuj patchy (Job 26)
2. Zarejestruj przez API: Job 26, Building 57, Good 66
3. Zbuduj smolarnię → zatrudnij smolarza → sprawdź produkcję węgla

### Test 2: Nowy zawód (Job 100)
1. Zarejestruj Job 100 przez API
2. Zarejestruj produkcję
3. Sprawdź czy działa bez patchy binarki

### Test 4: Hot Reload
1. Zmień INI w locie
2. Wywołaj `HOT_RELOAD`
4. Sprawdź czy zmiany weszły bez restartu

---

## 11. Bezpieczeństwo i stabilność

- **Walidacja:** Wszystkie ID sprawdzane przed zapisem do rejestru
- **Fallback:** Błąd w hooku → oryginalny kod
- **Thread Safety:** CriticalSection dla registrów
- **Crash Recovery:** Watchdog restartuje hook przy crashu
- **Logging:** Wszystkie operacje logowane do pliku

---

## 12. Narzędzia dołączone

| Narzędzie | Opis |
|-----------|------|
| `cnmod_loader.exe` | Loader z hookami |
| `cnmod_cli.exe` | CLI do rejestracji (do CI/CD) |
| `cnmod_gui.exe` | GUI do dodawania zawodów/budynków |
| `cnmod_validator.exe` | Waliduje INI przed wgraniem |

---

## 13. Następne kroki

1. **Napisz Loader (C++)** - inject DLL, alokuje pamięć, instaluje hooki
2. **Zaimplementuj Hook 1** - Dispatcher (najważniejszy)
3. **Named Pipe Server** - komunikacja z GUI
4. **Registry System** - Job/Production/Good/UI
4. **Hot Reload** - synchronizacja INI
5. **GUI** - Qt/Dear ImGui dla modderów

---

**Gotowe do implementacji?** Rozpoczynamy od **Loadera + Hook 1 (Dispatcher)**.