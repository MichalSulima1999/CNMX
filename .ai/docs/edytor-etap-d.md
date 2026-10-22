# Edytor map — Etap D (osobny)

**Cel:** sprawić, by nowe typy (budynki/surowce) były widoczne i wybieralne w `Edytor podstawowy.exe` / `Remik's Editor.exe`. Nie jest wymagane dla grywalności nowych typów w `CN.PLMOD.exe`.

---

## Krótka diagnoza

- Edytor czyta te same pliki: `cn.plmod\budynki12\houses\houses.ini` (`[GfxHouse]`, `EditName`, `EditGroups`), `tribetypes.ini`, stringi PL. 
- `[GfxHouse]` ładowany dynamicznie — rekord ma rozmiar `0x8BC` (2236 B), alokacja `imul eax, liczba_sekcji, 0x8BC` — **brak twardego limitu 55**. Nowe typy trafiają do pamięci.
- **Bariery:** pętle ograniczone do 0x37 (55) i mapowanie **plemię → dozwolone domy** (`tribehouseLinkData` o stałym rozmiarze 55 na plemię).
- Zapis mapy przez `sethouse "<EditName>" ...` w `staticobjects.inc` — używa nazwy, więc mapa (tekstowa) jest **kompatybilna** z grą, gdyż gra mapę czyta przez parser `sethouse` + nazwy.

---

## Znane miejsca (z rekonesu)

- `0x41DF9C`: `inc esi; cmp esi,0x37; jle 0x41DF83` — inicjalizacja/listowanie linków plemię–domy
- `0x41EDF4`: `inc esi; cmp esi,0x37; jle 0x41ED99` — druga pętla (per-plemienne filtry)
- `0x40A648`: `cmp eax,0x38; jge ...` — setter limitu

Wszystkie to **iteracje po tablicach stałego rozmiaru** (55 na plemię). Nowy max = np. `0x3F` (63) / `0x40` (64) — po podniesieniu tych stałych trzeba też powiększyć tablice `tribehouseLinkData`.

---

## Zadania

- [ ] Inwentarzacja: potwierdzić ile dokładnie tablic per-plemię używa rozmiaru 55, czy są inicjalizowane przez te pętle, gdzie jest alokacja `tribehouseLinkData`.
- [ ] Podniesienie limitów w pamięci (runtime-nakładka DLL dla edytora, lub statyczny patch `.orig` + copy przy użyciu).
- [ ] Rozszerzenie struktur (tablice houseLinks) pod nowy `MAX_HOUSES`.
- [ ] Testy: edytor ładuje nowe `[GfxHouse]`, pokazuje w drzewie „Budynki”, pozwala ustawić, zapisuje poprawny `sethouse` z `EditName`, mapa wczytuje się bez błędów w grze.
- [ ] Dokumentacja: uruchamianie edytora z nakładką (oddzielny `cnmod_editor_runtime.dll` / launcher). 

---

## Wskazówki

- Nie ruszać switch-case (`cmp eax, 5/7/8/...`), tylko **granice iteracji/pętli** (jak w Etapie C).
- Zapis po nazwie = bezpieczny — nie trzeba modyfikować formatu `staticobjects.inc`.
- Można **odroczyć** ten etap i testować nowe typy wyłącznie przez ręczną edycję `.inc` aż do momentu, gdy edytor stanie się potrzebny.