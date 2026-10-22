# -*- coding: utf-8 -*-
"""pe_waitvb.py — konteksty WaitForVerticalBlank / SetDisplayMode / SetCooperativeLevel."""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pefile
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

PE = r"G:\Games\CnMod 1.2\CN.PLMOD.exe"
pe = pefile.PE(PE)
base = pe.OPTIONAL_HEADER.ImageBase
data = pe.__data__
ttext = [s for s in pe.sections if s.Name.rstrip(b"\x00") == b".text"][0]
tv, ts, tn = ttext.VirtualAddress, ttext.PointerToRawData, ttext.Misc_VirtualSize
md = Cs(CS_ARCH_X86, CS_MODE_32)

def disasm(va, before=0, after=200, head=""):
    off = pe.get_offset_from_rva(va - base)
    if off is None:
        print("\n--- 0x%08x poza (%s) ---" % (va, head)); return
    start = max(0, off - before)
    print("\n--- 0x%08x [-%d,+%d] %s ---" % (va, before, after, head))
    for ins in md.disasm(bytes(data[start:off + after]), base + start):
        mark = ">>" if ins.address == va else "  "
        print("%s 0x%08x: %-7s %s" % (mark, ins.address, ins.mnemonic, ins.op_str))

# tryb/rozdzielczosc: SetDisplayMode 0x478144 (init display) i 0x47b00c/0x47b099 (render)
disasm(0x478100, 40, 240, "CDDDisplay init SetDisplayMode")
disasm(0x47afe0, 30, 220, "natywne ustawienie trybu render")
disasm(0x4b8140, 20, 160, "SetDisplayMode w grze (settings apply?)")

# WaitVB strona przełączania trybu
disasm(0x4057a0, 20, 130, "present/mode change region (WaitVB 0x4057e6)")
disasm(0x477180, 30, 110, "WaitVB 0x4771b6 kontekst")
disasm(0x4dc640, 30, 130, "WaitVB 0x4dc67a kontekst (transition?)")

# SetCooperativeLevel 0x40460b i 0x47a97e — flaga windowed vs fullscreen
disasm(0x4045e0, 30, 90, "SetCoop 0x40460b kontekst")