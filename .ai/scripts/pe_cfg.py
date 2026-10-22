# -*- coding: utf-8 -*-
"""pe_cfg.py — konfiguracja graficzna (game.ini/gfx_*) + zrodlo flagi vsync (bit 0x40 [..+0x18])."""
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

def cstr_va(sva):
    off = pe.get_offset_from_rva(sva - base)
    if off is None: return ""
    s = off
    while s > 0 and data[s - 1] != 0: s -= 1
    e = data.find(b"\x00", off, off + 80)
    return bytes(data[s:e]).decode("cp1250", "replace")

def disasm(va, before=0, after=200, head=""):
    off = pe.get_offset_from_rva(va - base)
    if off is None:
        print("\n--- 0x%08x poza (%s) ---" % (va, head)); return
    start = max(0, off - before)
    print("\n--- 0x%08x [-%d,+%d] %s ---" % (va, before, after, head))
    for ins in md.disasm(bytes(data[start:off + after]), base + start):
        mark = ">>" if ins.address == va else "  "
        print("%s 0x%08x: %-7s %s" % (mark, ins.address, ins.mnemonic, ins.op_str))

# stringi konfiguracji -> VA
kws = []
for off, nm in ((0x0fe164, "gfx_screen_depth"), (0x0fe178, "gfx_screen_height"),
                (0x0fe18c, "gfx_screen_width"), (0x0fe1a0, "gfx_fullscreen_toggle"),
                (0x0fe1b8, "gfx_fullscreen"), (0x0fe1fc, "game.ini"),
                (0x0ff08c, ".ini"), (0x0ff88e, "currentusermap\\map.ini")):
    sva = pe.get_rva_from_offset(off) + base
    kws.append((nm, sva))
for nm in ("gfx_screen_depth", "gfx_screen_height", "gfx_screen_width", "gfx_fullscreen_toggle", "gfx_fullscreen", "game.ini"):
    # znajdz w sekcji .rdata
    p = bytes(data).find(nm.encode())
    if p >= 0:
        kws.append((nm, pe.get_rva_from_offset(p) + base))

print("=== XREFY push imm -> stringi cfg ===")
xr = {}
for nm, sva in kws:
    refs = []
    for i in range(len(blob) - 5):
        if blob[i] == 0x68:
            imm = struct.unpack_from("<I", blob, i + 1)[0]
            if imm == sva:
                refs.append(base + tv + i)
    xr[nm] = refs
    print("  %-24s %r xrefy: %s" % (nm, cstr_va(sva), ["0x%x" % x for x in refs[:10]]))

print("\n=== skan: or byte ptr [reg+0x18], imm  (ustawianie flagi 0x40) ===")
hits = []
for i in range(len(blob) - 4):
    if blob[i] == 0x80 and 0x40 <= blob[i + 1] <= 0x47 and blob[i + 2] == 0x18:
        imm = blob[i + 3]
        if imm & 0x40:
            hits.append((base + tv + i, imm))
    if blob[i] == 0x81 and 0x40 <= blob[i + 1] <= 0x47 and blob[i + 2] == 0x18:
        imm = struct.unpack_from("<I", blob, i + 3)[0]
        if imm & 0x40:
            hits.append((base + tv + i, imm))
    # or dword ptr [reg+0x18] = 0x40 (short) — niby 83 4? 18 40
    if blob[i] == 0x83 and 0x40 <= blob[i + 1] <= 0x47 and blob[i + 2] == 0x18 and blob[i + 3] == 0x40:
        hits.append((base + tv + i, 0x40))
print("  %d trafien: %s" % (len(hits), ["0x%x(imm=%#x)" % (a, b) for a, b in hits]))
for va, imm in hits[:6]:
    disasm(va, before=8, after=30, head="or imm=%#x" % imm)

print("\n=== callerzy wrapperow WaitVBL (0x4057d7) / BltPath (0x477c78) ===")
def callers(target):
    out = []
    for i in range(len(blob) - 5):
        if blob[i] == 0xE8:
            rel = struct.unpack_from("<i", blob, i + 1)[0]
            if base + tv + i + 5 + rel == target:
                out.append(base + tv + i)
    return out
for t, nm in ((0x4057d7, "WaitVBL(0x4057d7)"), (0x4057ea, "GetFlipStatus?(0x4057ea)"),
              (0x477c78, "blit(0x477c78)"), (0x47712b, "petla runtime blit(0x47712b)"),
              (0x477de1, "0x477de1 (mode switch wait)")):
    cs = callers(t)
    print("  %-30s %3d : %s" % (nm, len(cs), ["0x%x" % x for x in cs[:14]]))

# kto ustawia flagi [obj+0x18] w kontekscie 0x477xe0? pokaz okolice 0x477dff/0x477e10 (mode restore)
disasm(0x477dd0, 10, 130, "mode restore / flagi")