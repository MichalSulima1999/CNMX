# Skan wszystkich stalych granic (towary/domy/zawody/rekord) wzgledem tabeli patchy.
# Uruchom: python .ai\scripts\limit_scan.py
import re, struct, sys
import pefile
from capstone import Cs, CS_ARCH_X86, CS_MODE_32
from capstone.x86 import X86_OP_IMM

EXE = r"G:\Games\CnMod 1.2\CN.PLMOD.exe.orig.before_scriptfix"
PATCHES = r"G:\Games\CnMod 1.2\etapa_gen\patches_ext.h"
OUT = r"G:\Games\CnMod 1.2\.ai\re_out\limit_scan.txt"

# rva w tabeli patchy jest rva instrukcji; off = offset do immediate.
cover = {}
patch_list = []
for line in open(PATCHES, encoding="utf-8", errors="replace"):
    m = re.match(r"\s*\{\s*0x([0-9A-Fa-f]+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,", line)
    if not m:
        continue
    rva = int(m.group(1), 16); off = int(m.group(2)); size = int(m.group(3))
    m2 = re.search(r'"([^"]*)"', line)
    desc = m2.group(1) if m2 else ""
    patch_list.append((rva, off, size, desc))
    for k in range(size):
        cover.setdefault(rva + off + k, []).append((rva, off, size, desc))

OLDVALS = {0x42: "good", 0x37: "house", 0x38: "goodB", 0x35A0: "goodsTab", 0x151BC: "houseTab",
           0x58: "jobs", 0x1AE08: "recSize", 0x468D50: "recEnd", 0x4A80: "elem", 0x5D200: "pool",
           0x5D204: "poolAlloc"}

pe = pefile.PE(EXE)
sec = [s for s in pe.sections if s.Name.startswith(b".text")][0]
tva, toff = sec.VirtualAddress, sec.PointerToRawData
raw = open(EXE, "rb").read()
tdata = raw[toff:toff + sec.SizeOfRawData]

md = Cs(CS_ARCH_X86, CS_MODE_32)
md.detail = True
md.skipdata = True

NOISY = {0x4A80, 0x5D200, 0x5D204}   # obsluzone kategoriami A/B - nie raportuj szczegolowo

sites = []
for ins in md.disasm(tdata, tva):
    if ins.id == 0 or ins.mnemonic.startswith("."):
        continue
    for op in ins.operands:
        if op.type == X86_OP_IMM:
            v = op.imm & 0xFFFFFFFF
            if v in OLDVALS:
                covd = any((ins.address + p) in cover for p in range(len(ins.bytes)))
                sites.append((ins.address, ins.mnemonic, ins.op_str, v,
                              ins.bytes.hex(), covd))
                break

unc = [s for s in sites if not s[5]]
cov = [s for s in sites if s[5]]
unc_i = [s for s in unc if s[3] not in NOISY]

L = []
L.append("LIMIT SCAN  sites=%d  covered=%d  uncovered=%d (nie-szumnych uncovered=%d)"
         % (len(sites), len(cov), len(unc), len(unc_i)))
L.append("")
L.append("=== UNCOVERED != elem/pool (kandydaci brakujacych patchy) ===")
for rva, mn, ops, v, bh, _ in unc_i:
    L.append("0x%08X  %-7s %-42s imm=0x%-6X [%s]  %s"
             % (rva, mn, ops, v, OLDVALS[v], bh))
L.append("")
L.append("=== COVERED != elem/pool ===")
for rva, mn, ops, v, bh, _ in cov:
    if v in NOISY:
        continue
    L.append("0x%08X  %-7s %-42s imm=0x%-6X [%s]" % (rva, mn, ops, v, OLDVALS[v]))

out = "\n".join(L)
open(OUT, "w", encoding="utf-8").write(out)
print(out)
