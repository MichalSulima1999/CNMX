# -*- coding: utf-8 -*-
import sys, capstone, pefile

EXE = r"G:\Games\CnMod 1.2\CN.PLMOD.exe.orig.before_scriptfix"
IMG_BASE = 0x400000
start = int(sys.argv[1], 16)
end = int(sys.argv[2], 16)
if start >= IMG_BASE:
    start -= IMG_BASE
if end >= IMG_BASE:
    end -= IMG_BASE

pe = pefile.PE(EXE, fast_load=True)
text = None
for s in pe.sections:
    nm = s.Name.rstrip(b"\x00").decode(errors="replace")
    if nm == ".text":
        text = s
        break
T = text.VirtualAddress
R = text.PointerToRawData
data = pe.__data__

def rd(rva, n):
    off = R + (rva - T)
    return data[off:off + n]

lo = start & ~0xF
code = rd(lo, (end - lo) + 32)
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
md.detail = False
n = 0
for ins in md.disasm(code, lo):
    if ins.address < start:
        continue
    if ins.address > end:
        break
    print("0x%06X  %-7s %s" % (ins.address, ins.mnemonic, ins.op_str))
    n += 1
if n == 0:
    print("(brak instrukcji w zakresie) section .text VA=0x%X raw=0x%X" % (T, R))
