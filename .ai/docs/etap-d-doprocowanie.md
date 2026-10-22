# Etap D - stan obecny i plan dopracowania

## Status
Etap D (wsparcie Edytora map) został zainicjowany. Stworzyliśmy **oddzielną runtime nakładkę** `EtapD.dll` + `launcher_editor.exe` dla obu edytorów (`Edytor podstawowy.exe` i `Remik's Editor.exe`).

## Co już zrobiliśmy
- [x] Rekonesans adresów: 0x41DF9C, 0x41EDF4, 0x40A648
- [x] `etapd/` – projekt bazujący na EtapC (MinHook + log)
- [x] Patches w RAM: 
  - `0x41DF9C: cmp esi, 0x37 → 0x40`
  - `0x41EDF4: cmp esi, 0x37 → 0x40`
  - `0x40A648: cmp eax, 0x38 → 0x40`
- [x] Build i test uruchomienia – oba edytory startują z nakładką, logi: `patches applied: 3/3 ok`

## Co wymaga dopracowania
Zgodnie z `.ai/docs/edytor-etap-d.md`:

- [ ] **Inwentarzacja `tribehouseLinkData`** – potwierdzić ile tablic per-plemię ma rozmiar 55, gdzie są inicjalizowane, gdzie jest alokacja `tribehouseLinkData`
- [ ] **Rozszerzenie struktur per-plemię** – podnieść rozmiary tablic `tribehouseLinkData`/house-links pod nowy MAX_HOUSES (64)
- [ ] **Dodatkowe limity** – sprawdzić inne `cmp 0x37/0x38` w UI (lista budynków, filtry plemienne)
- [ ] **Test funkcjonalny** – wczytanie `[GfxHouse] 56`, widoczność w drzewku "Budynki", ustawienie, zapis `sethouse`, wczytanie w CN.PLMOD

## Rationale
Pełne UI wymaga nie tylko granic pętli, ale też powiększenia tablic stałego rozmiaru. Obecne 3 patche są wystarczające technicznie (edytor startuje), jednak pełne wsparcie UI jest **ewentualne do dokończenia** w przyszłości.

**Rekomendacja:** przejść do **Etapu E**, a Etap D dokończyć dopiero gdy edytor stanie się niezbędny.