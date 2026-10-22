# -*- coding: utf-8 -*-
import re
import capstone, pefile

EXE  = r"G:\Games\CnMod 1.2\CN.PLMOD.exe.orig.before_scriptfix"
SCAN = r"G:\Games\CnMod 1.2\.ai\re_out\limit_scan.txt"

ALL = {
    0x50a0:"tribe.job(50a0)", 0x50d8:"tribe.goodA(50d8)", 0x511a:"tribe.goodB(511a)",
    0x515c:"tribe.houseA(515c)", 0x5193:"tribe.veh(5193)",
    0x948:"elem+948", 0x1278:"elem+1278(goodA)", 0x1d4c:"elem+1d4c",
    0x3c78:"elem+3c78(goodB)", 0x2820:"elem+2820(houseA)", 0x3126:"elem+3126(houseB)",
}
CONDJ = {"je","jne","jz","jnz","jl","jle","jg","jge","jb","jbe","ja","jae","jc","jnc","jns","js"}

pe = pefile.PE(EXE, fast_load=True)
text = next(s for s in pe.sections if s.Name.rstrip(b"\x00") == b".text")
TRVA, TRaw = text.VirtualAddress, text.PointerToRawData
DATA = pe.__data__

def read(rva, n):
    off = TRaw + (rva - TRVA)
    return DATA[off:off+n]

uncovered = []
sec = False
for line in open(SCAN, encoding="utf-8", errors="replace"):
    if line.startswith("=== UNCOVERED"):
        sec = True; continue
    if line.startswith("=== COVERED"):
        sec = False; continue
    if not sec:
        continue
    m = re.match(r"0x([0-9A-Fa-f]+)\s+cmp\s+(eax|ebx|ecx|edx|esi|edi),\s+0x(37|38|42)\b", line)
    if m:
        uncovered.append((int(m.group(1),16), m.group(2), int(m.group(3),16)))

md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)

def near_flags(rva):
    region = read(rva-0x60, 0xC0)
    found = set()
    for ins in md.disasm(region, rva-0x60):
        if not (rva-0x60 <= ins.address <= rva+0x60):
            continue
        m = re.search(r"\[([^\]]+)\]", ins.op_str)
        if not m:
            continue
        inner = m.group(1)
        if "ebp" in inner or "+" not in inner:
            continue
        for tok in inner.split("+"):
            tok = tok.strip()
            mm = re.fullmatch(r"0x([0-9a-fA-F]+)", tok)
            if mm and int(mm.group(1),16) in ALL:
                found.add((ins.address, ins.mnemonic, ins.op_str, ALL[int(mm.group(1),16)]))
    return found

def is_loop_bound(rva):
    for ins in md.disasm(read(rva, 10), rva):
        if ins.address == rva:
            continue
        return ins.mnemonic in ("jl","jle","jg","jge","jb","jbe","ja","jae","jc","jnc","js","jns")
    return False

hits = []
for (rva, reg, imm) in uncovered:
    found = near_flags(rva)
    if found and is_loop_bound(rva):
        hits.append((rva, reg, imm, found))

print("petle-kopiujace po tablicach flag (wysoka pewnosc): %d" % len(hits))
print("="*90)
for rva, reg, imm, found in sorted(hits):
    labs = sorted({f[3] for f in found})
    print("0x%06X  cmp %s,0x%02X  ->  %s" % (rva, reg, imm, ", ".join(labs)))
    for (a, mn, op, lab) in sorted(found)[:4]:
        print("        [0x%06X] %s %s   ; %s" % (a, mn, op, lab))
