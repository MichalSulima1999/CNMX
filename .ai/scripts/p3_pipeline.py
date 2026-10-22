# -*- coding: utf-8 -*-
"""p3_pipeline.py — szczegóły pipeline'u (C vs B): render-target, draw callery, tail-jmp 47B0D7, mysz."""
import sys, struct
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pefile
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

PE = r"G:\Games\CnMod 1.2\CN.PLMOD.exe"
pe = pefile.PE(PE)
base = pe.OPTIONAL_HEADER.ImageBase
data = pe.__data__
ttext = [s for s in pe.sections if s.Name.rstrip(b"\x00") == b".text"][0]
tv, ts, tn = ttext.VirtualAddress, ttext.PointerToRawData, ttext.Misc_VirtualSize
blob = data[ts:ts + tn]
md = Cs(CS_ARCH_X86, CS_MODE_32)

def dis(va, before=0, after=260):
    off = pe.get_offset_from_rva(va - base)
    if off is None:
        print("\n--- 0x%08x poza ---" % va); return
    start = max(0, off - before)
    print("\n--- 0x%08x [-%d,+%d] ---" % (va, before, after))
    for ins in md.disasm(bytes(data[start:off + after]), base + start):
        print(" %s 0x%08x: %-7s %s" % (">>" if ins.address == va else "  ", ins.address, ins.mnemonic, ins.op_str))

def callers(target):
    out = []
    for i in range(len(blob) - 5):
        if blob[i] == 0xE8:
            rel = struct.unpack_from("<i", blob, i + 1)[0]
            if base + tv + i + 5 + rel == target:
                out.append(base + tv + i)
    return out

def jmppers(target):
    out = []
    for i in range(len(blob) - 5):
        if blob[i] in (0xE9, 0xEB):
            sz = 5 if blob[i] == 0xE9 else 2
            if sz == 5:
                rel = struct.unpack_from("<i", blob, i + 1)[0]
                if base + tv + i + 5 + rel == target:
                    out.append(base + tv + i)
    return out

print("=== tail-jmp do 0x47B0D7 (blit HUD) ===")
print(jmppers(0x47B0D7))
print("=== tail-jmp do 0x40D507 (stretch) ===")
print(jmppers(0x40D507))

# render target / glowna funkcja klatki
dis(0x4025c0, 40, 240)   # ctor powierzchni + stretch 0x4025e9..0x40264a
dis(0x402cb0, 30, 160)   # stretch 0x402cc5 + draw 0x402cd8 w tej samej funkcji?

# draw callers — krótkie okna
for va in (0x4020b6, 0x402cd8, 0x403491):
    dis(va - 20, 0, 120)

# mysz: importy GetCursorPos / GetAsyncKeyState -> xrefy
print("\n=== mysz: GetCursorPos/GetAsyncKeyState xrefy (FF15/FF25/E8) ===")
imps = {}
for e in pe.DIRECTORY_ENTRY_IMPORT:
    for i in e.imports:
        if i.name and i.name.decode() in ("GetCursorPos", "GetAsyncKeyState", "SetCursorPos", "ScreenToClient", "ClientToScreen", "GetWindowRect", "GetClientRect"):
            imps[i.name.decode()] = i.address
for nm, at in sorted(imps.items()):
    sites = []
    for i in range(len(blob) - 5):
        if blob[i] == 0xFF and blob[i + 1] == 0x15:
            va = struct.unpack_from("<I", blob, i + 2)[0]
            if va == at:
                sites.append(base + tv + i)
    print("  %-20s IAT 0x%08x — %d miejsc: %s" % (nm, at, len(sites), ["0x%x" % x for x in sites[:12]]))