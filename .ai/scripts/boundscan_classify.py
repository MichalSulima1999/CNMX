#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from pathlib import Path

try:
    from capstone import Cs, CS_ARCH_X86, CS_MODE_32
    import pefile
except Exception as e:
    print(e)
    sys.exit(1)

EXE = Path(r"G:\Games\CnMod 1.2\CN.PLMOD.exe")
OUT = Path(r"G:\Games\CnMod 1.2\.ai\docs\boundscan_classified.txt")

SWITCH_SMALL = set(range(1, 21))
BOUNDS_CAND = {
    'house': {0x37},  # 55
    'good': {0x42, 0x37, 0x30},  # 66,55,48? per targets
    'weapon': {0x2b, 0x16},  # 43,22
    'vehicle': {0x4e, 0x07},
    'job': {0x38, 0x30},
    'armor': {0x66, 0x2b, 0x05},
    'tribe': {0x2a, 0x14},
    'landscape': {0x72, 0x58},
    'maintype': {0x72, 0x08},
}
# general large bounds we care
CAREFUL = {0x37, 0x38, 0x42, 0x43, 0x30, 0x2b, 0x4e, 0x66, 0x2a, 0x14, 0x72, 0x58, 0x08, 0x0E, 0xC8, 0x76}

def main():
    if not EXE.is_file():
        print("no exe")
        sys.exit(1)
    pe = pefile.PE(str(EXE))
    # find .text
    rva = None
    data = None
    for sec in pe.sections:
        if b".text" in sec.Name:
            data = sec.get_data()
            rva = sec.VirtualAddress
            break
    if data is None:
        print("no text"); sys.exit(1)
    md = Cs(CS_ARCH_X86, CS_MODE_32)
    base = pe.OPTIONAL_HEADER.ImageBase + rva
    res = []
    # disasm all small? 2-3M ok
    try:
        for insn in md.disasm(data, base):
            if insn.mnemonic == "cmp":
                try:
                    op = insn.operands[1]
                    if op.type == 1:  # imm
                        imm = op.imm & 0xFFFFFFFF
                        if imm > 0x200:
                            continue
                        # record
                        res.append((insn.address - pe.OPTIONAL_HEADER.ImageBase, imm))
                except Exception:
                    pass
    except Exception as e:
        print(e)
    # dedupe by addr
    seen = {}
    for a, imm in res:
        if a not in seen:
            seen[a] = imm
    # sort
    out = []
    for a in sorted(seen):
        imm = seen[a]
        cls = "switch?"
        if imm > 20:
            cls = "bound?"
        elif imm in SWITCH_SMALL:
            cls = "switch?"
        # flags
        note = []
        if imm == 0x37: note.append("HOUSES_MAX-1/COUNT? (55)")
        if imm == 0x38: note.append("HOUSES_MAX+1? (56)")
        if imm == 0x42: note.append("GOODS 66")
        out.append((a, imm, cls, " ".join(note)))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("# VA(VA_rel?) better RAV relative? addr shown as VA-ImageBase? using RVA+Base in capstone gave VA\n")
        f.write("# format: RVA VA imm cls notes\n")
        for a, imm, cls, n in out:
            va = pe.OPTIONAL_HEADER.ImageBase + a
            f.write(f"{a:08X} {va:08X} cmp imm=0x{imm:02X} ({imm}) {cls} {n}\n")
    print(f"wrote {OUT} {len(out)} entries")
    return 0

if __name__ == "__main__":
    sys.exit(main())
