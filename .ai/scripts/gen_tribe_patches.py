#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_tribe_patches.py — generator wpisow Patch[] dla rozszerzenia slotow budynkow
do 64 (wariant "pojazdy -> ogon rekordu", bez przesuwania displacementow).

Uruchomienie (z katalogu gry lub z --exe):
    python .ai\\scripts\\gen_tribe_patches.py [--exe CN.PLMOD.exe] [--check]

Skrypt:
  1) dla kazdego "zamiaru" patch (rva + stara/nowa wartosc) dekoduje instrukcje,
  2) sprawdza, ze stare bajty sa dokladnie tam, gdzie oczekiwano,
  3) wylicza off/size z kodowania (imm8 / imm32 / disp32),
  4) wypisuje gotowe wpisy C do wklejenia w etapc/src/patches.h.

Uwaga: lista imul-ow 0x1AE08 pochodzi z PELNEGO skanu (skipdata=True) calego .text.
Bez skipdata capstone zatrzymuje sie na RVA 0x1FB05 i gubi 24 z 28 wystapien.
"""
import argparse, struct, sys

try:
    import pefile
    from capstone import Cs, CS_ARCH_X86, CS_MODE_32
except ImportError as e:
    sys.exit("Brak zaleznosci: %s (pip install pefile capstone)" % e)

# --- stale docelowe -----------------------------------------------------------
NEW_HOUSE_MAX   = 0x40        # 64
REC_SIZE_OLD    = 0x1AE08
REC_SIZE_NEW    = 0x1AE10     # +8 B na przeniesiona tablice pojazdow
REC_ARR_NEW     = 42 * REC_SIZE_NEW   # 0x468EA0
VEH_DISP_OLD    = 0x5193
VEH_DISP_NEW    = REC_SIZE_OLD        # tablica pojazdow na koncu rekordu = 0x1AE08

# kind: 'imm8' | 'imm32' | 'disp32'
# (rva, kind, old, new, desc)
INTENTS = [
    # --- limity 0x37 -> 0x40 (domy) ---
    (0x000A003, 'imm8',  0x37, NEW_HOUSE_MAX, "loop houses 0x37->0x40"),
    (0x0009EA1, 'imm8',  0x37, NEW_HOUSE_MAX, "flag copy loop 0x37->0x40"),
    (0x00142F4, 'imm8',  0x37, NEW_HOUSE_MAX, "flag write guard 0x37->0x40"),
    (0x0014289, 'imm8',  0x37, NEW_HOUSE_MAX, "validator NC2Logic 0x37->0x40"),
    (0x001542C, 'imm8',  0x37, NEW_HOUSE_MAX, "houses.ini loader validator 0x37->0x40"),
    (0x00158D5, 'imm8',  0x37, NEW_HOUSE_MAX, "iterator 1 0x37->0x40"),
    (0x0015923, 'imm8',  0x37, NEW_HOUSE_MAX, "iterator 2 0x37->0x40"),
    (0x0015368, 'imm32', 0x37, NEW_HOUSE_MAX, "ctor: 64 rekordow"),
    # --- przeniesienie tablicy pojazdow na ogon rekordu ---
    (0x0009EA8, 'disp32', VEH_DISP_OLD, VEH_DISP_NEW, "vehicles read -> tail"),
    (0x00142BB, 'disp32', VEH_DISP_OLD, VEH_DISP_NEW, "vehicles write -> tail"),
    # --- rozmiar rekordu plemienia 0x1AE08 -> 0x1AE10 ---
    (0x0009E00, 'imm32', REC_SIZE_OLD, REC_SIZE_NEW, "tribe size (mov)"),
    (0x000A032, 'imm32', REC_SIZE_OLD, REC_SIZE_NEW, "tribe size (strided)"),
    (0x000AF4A, 'imm32', REC_SIZE_OLD, REC_SIZE_NEW, "tribe size (advance)"),
    (0x0013F56, 'imm32', REC_SIZE_OLD, REC_SIZE_NEW, "tribe size (imul)"),
    # --- koniec tablicy plemion: 0x468D50 -> 0x468EA0 ---
    (0x000AF51, 'imm32', 0x468D50, REC_ARR_NEW, "tribe array end (cmp)"),
    (0x0013EAB, 'imm32', 0x468D50, REC_ARR_NEW, "tribe array malloc"),
]

# 24 imul ...,0x1AE08 w kodzie menu/logiki (pelny skan). off/size liczone automatycznie.
IMUL_1AE08 = [
    0x02D80A, 0x02D84F, 0x02D894, 0x02D8D9, 0x02D91E, 0x02D940,
    0x02DB3A, 0x03E8C7, 0x04A147, 0x04A216, 0x04A365, 0x04A5AF,
    0x04A9AF, 0x04AA9E, 0x04ABED, 0x04AE56, 0x04B282, 0x04B313,
    0x04CB19, 0x0A5356, 0x0A57E7, 0x0A5AF6, 0x0AC6FE, 0x0C7821,
]
for rva in IMUL_1AE08:
    INTENTS.append((rva, 'imm32', REC_SIZE_OLD, REC_SIZE_NEW, "tribe stride imul"))


def load(path):
    pe = pefile.PE(path)
    data = open(path, 'rb').read()
    ib = pe.OPTIONAL_HEADER.ImageBase
    text = [s for s in pe.sections if s.Name.startswith(b'.text')][0]
    tdata = data[text.PointerToRawData:text.PointerToRawData + text.SizeOfRawData]
    return pe, data, ib, text, tdata


def file_off(pe, rva):
    for s in pe.sections:
        if s.VirtualAddress <= rva < s.VirtualAddress + s.SizeOfRawData:
            return s.PointerToRawData + (rva - s.VirtualAddress)
    raise ValueError("rva poza sekcjami: 0x%X" % rva)


def find_off(ins_bytes, kind, old):
    if kind == 'imm8':
        pat = bytes([old & 0xFF])
    else:
        pat = struct.pack('<I', old & 0xFFFFFFFF)
    pos = ins_bytes.find(pat)
    if pos < 0:
        return None
    return pos


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--exe', default=r'CN.PLMOD.exe')
    ap.add_argument('--check', action='store_true', help='tylko weryfikacja, bez wypisywania')
    args = ap.parse_args()

    pe, data, ib, text, tdata = load(args.exe)
    tva = ib + text.VirtualAddress
    md = Cs(CS_ARCH_X86, CS_MODE_32); md.detail = True
    md.skipdata = True

    # mapa rva -> (bytes, mnemonik)
    want = {rva for rva, *_ in INTENTS}
    found = {}
    for ins in md.disasm(tdata, tva):
        if ins.id == 0:
            continue
        r = ins.address - ib
        if r in want:
            found[r] = bytes(ins.bytes), (ins.mnemonic + ' ' + ins.op_str)

    ok = 0
    print("/* --- wygenerowane przez gen_tribe_patches.py --- */")
    for rva, kind, old, new, desc in INTENTS:
        if rva not in found:
            print("    /* !! BRAK DEKODU @0x%06X (%s) */" % (rva, desc))
            continue
        ibs, txt = found[rva]
        off = find_off(ibs, kind, old)
        if off is None:
            print("    /* !! NIE ZNALEZIONO 0x%X @0x%06X | %s | %s */" % (old, rva, txt, desc))
            continue
        size = 1 if kind == 'imm8' else 4
        # sanity: operand faktycznie wystepuje
        nb = struct.pack('<I', new & 0xFFFFFFFF) if size == 4 else bytes([new & 0xFF])
        if not args.check:
            print("    { 0x%06X, %d, %d, { %3d, %3d, %3d, %3d }, \"%s\" },   /* %s */" % (
                rva, off, size, nb[0], nb[1] if size > 1 else 0,
                nb[2] if size > 2 else 0, nb[3] if size > 3 else 0, desc, txt))
        ok += 1
    sys.stderr.write("zweryfikowano %d/%d zamiarow\n" % (ok, len(INTENTS)))
    return 0 if ok == len(INTENTS) else 1


if __name__ == '__main__':
    sys.exit(main())
