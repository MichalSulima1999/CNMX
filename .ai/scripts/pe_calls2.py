# -*- coding: utf-8 -*-
"""pe_calls2.py — census vtable + callerzy presentu / glownej petli.
"""
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

def va2off(va):
    return pe.get_offset_from_rva(va - base)

def disasm(va, before=0, after=140, head=""):
    off = va2off(va)
    if off is None:
        print("\n--- 0x%08x poza sekcjam (%s) ---" % (va, head)); return
    start = max(0, off - before)
    print("\n--- okno 0x%08x [-%d,+%d] %s ---" % (va, before, after, head))
    for ins in md.disasm(bytes(data[start:off + after]), base + start):
        mark = ">>" if ins.address == va else "  "
        print("%s 0x%08x: %-7s %s" % (mark, ins.address, ins.mnemonic, ins.op_str))

# 1) census z prawidlowym maskowaniem i walidacja granic
print("=== CENSUS vtable call [reg+disp8] ===")
vt = {0x18: "CreateSurface", 0x2c: "Flip", 0x34: "Blt?", 0x40: "SetCoopLvl",
      0x44: "SetDispMode", 0x48: "WaitVB", 0x4c: "?", 0x50: "Flip(X2D)"}
allhits = []
for offs, label in sorted(vt.items()):
    hits = []
    for i in range(len(blob) - 3):
        if blob[i] == 0xFF and 0x50 <= blob[i + 1] <= 0x57 and blob[i + 2] == offs:
            try:
                ins0 = next(md.disasm(bytes(blob[i:i + 8]), 0))
            except Exception:
                ins0 = None
            if ins0 is not None and ins0.mnemonic == "call":
                hits.append(base + tv + i)
                allhits.append((offs, base + tv + i))
    print("  [reg+0x%02x] %-12s %2d : %s" % (offs, label, len(hits), ["0x%x" % x for x in hits[:16]]))

# 2) callerzy (E8 rel32) do istotnych funkcji
def callers(target):
    out = []
    for i in range(len(blob) - 5):
        if blob[i] == 0xE8:
            rel = struct.unpack_from("<i", blob, i + 1)[0]
            if base + tv + i + 5 + rel == target:
                out.append(base + tv + i)
    return out

print("\n=== CALLERZY (call E8) ===")
for t, nm in ((0x405658, "X2D::FlipDoWait(0x405658)"), (0x405579, "X2D::BltScreen(0x405579)"),
              (0x4787b3, "CDDDisplay::Draw(0x4787b3)"), (0x479195, "CDDDisplay::Message(0x479195)"),
              (0x47b0d7, "bitmap-na-ekran(0x47b0d7)"), (0x47934a, "0x47934a"),
              (0x405841, "0x405841"), (0x40589b, "0x40589b")):
    cs = callers(t)
    print("  %-38s %3d : %s" % (nm, len(cs), ["0x%x" % x for x in cs[:14]]))

# 3) glowne petle: callerzy X2D::BltScreen (0x405579)
print("\n=== X2D::BltScreen ostatni frame renderu: petle wyzej ===")
for va in callers(0x405579)[:2] + callers(0x4787b3)[:2]:
    disasm(va, before=6, after=120, head="caller")

# 4) sprawdz czy jakies miejsca uzywaja DDFLIP_WAIT / DDFLIP_DONOTWAIT jako imm
print("\n=== imm 0x4 (DDFLIP_DONOTWAIT) / 0x1 (WAIT) w okolicach flip ===")
for va in allhits:
    disasm(va, before=6, after=14, head="flip-site")