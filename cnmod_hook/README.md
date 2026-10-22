# CNMod Hook - Injector DLL dla CN.PLMOD.exe

Projekt umożliwia modyfikację zachowania silnika gry CN.PLMOD.exe poprzez wstrzykiwanie DLL.

## Struktura projektu

```
cnmod_hook/
├── dll_injector.py       # Główny injector DLL (Python)
├── cnmod_hook_simple.vcxproj  # Projekt Visual Studio (C++)
├── README.md             # Ten plik
└── bin/                  # Skompilowane DLL
    └── cnmod_hook.dll
```

## Metoda 1: Python Injector (bez kompilacji)

### Wymagania
- Python 3.8+
- Uruchomiona gra CN.PLMOD.exe

### Użycie

1. Uruchom grę `CN.PLMOD.exe`
2. Uruchom injector:

```bash
python dll_injector.py
```

3. Injector znajdzie proces gry i wstrzyknął DLL

## Metoda 2: C++ DLL (zaawansowane hooki)

### Wymagania
- Visual Studio 2022 (Community wystarczy)
- Windows SDK
- CMake (opcjonalnie)

### Kompilacja

1. Otwórz `cnmod_hook_simple.vcxproj` w Visual Studio
2. Wybierz konfigurację `Release` i platformę `x86`
3. Build → Build Solution (Ctrl+Shift+B)
4. Znajdź `cnmod_hook.dll` w folderze `bin\Release\`

### Użycie DLL

1. Skopiuj `cnmod_hook.dll` do folderu gry
2. Uruchom grę `CN.PLMOD.exe`
3. Uruchom `dll_injector.py` z opcją `--dll` wskazującą na DLL:

```bash
python dll_injector.py --dll .\cnmod_hook.dll
```

## Plan działań

| Element | Status | Uwagi |
|---------|--------|-------|
| Python injector | ✅ Gotowy | Wstrzykuje DLL do gry |
| C++ DLL stub | 🔄 W przygotowanu | Projekt VS gotowy |
| Hook dispatcher | ⏳ Do zrobienia | Patch case 0x19 → case 0x38 |
| Hook job assignment | ⏳ Do zrobienia | Aktualizacja job_id |
| Hook production | ⏳ Do zrobienia | Obsługa production chain |
| UI strings | ⏳ Do zrobienia | Nazwy zawodów |

## Jak to działają hooki?

### Architektura silnika

1. **Main Loop** (`0x4078C8`) wywołuje tick budynków co N ticków
2. **Dispatcher** (`0x46BAD7`) przydziela jednostki do jobów
3. **Job Assignment** przypisuje job_id do jednostki
4. **Production Handler** realizuje łańcuch produkcji

### Hooki do zaimplementowania

1. **Hook na Dispatcher** (`0x46BAD7`):
   - Interceptuj `switch(job_id)` 
   - Jeśli `job_id >= 46`, przekieruj do custom handlera

2. **Hook na Job Assignment**:
   - Sprawdzaj custom job IDs (np. 56 = smolarz)
   - Przypisuj odpowiednie job_id do jednostek

3. **Hook na Production**:
   - Interceptuj `logicproduction` check
   - Dodaj obsługę nowych łańcuchów produkcji

## Znane ograniczenia

- Gra jest 32-bitowa (x86) — DLL musi być również x86
- Niektóre funkcje mają hardcoded limity (np. 46 jobów)
- Wymagany jest patch limiterów w .text section

## Bezpieczeństwo

- Projekt służy wyłącznie celom edukacyjnym i moddingu
- Nie używaj w trybie online/wieloosobowym
- Zrób kopie zapasowe plików gry

## Autor

REA + Ghidra 12.1.4

## Licencja

MIT
