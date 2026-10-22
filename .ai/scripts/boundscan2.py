#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from pathlib import Path
from capstone import Cs, CS_ARCH_X86, CS_MODE_32
import pefile

EXE = Path(r"G:\Games\CnMod 1.2\CN.PLMOD.exe")
OUT = Path(r"G:\Games\CnMod 1.2\.ai\docs\boundscan_classified2.txt")

def main():
    pe = pefile.PE(str(EXE))
    # find text
    for sec in pe.sections:
        if b'.text' in sec.Name:
            data = sec.get_data()
            rva = sec.VirtualAddress
            break
    else:
        print('no text'); return 1
    md = Cs(CS_ARCH_X86, CS_MODE_32)
    base = pe.OPTIONAL_HEADER.ImageBase
    imgbase = base
    count = 0
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('# RVA VA imm\n')
        # iterate in chunks? but small
        for insn in md.disasm(data, imgbase + rva, len(data)):
            if insn.mnemonic == 'cmp':
                try:
                    # second op imm?
                    if len(insn.operands) >= 2 and insn.operands[1].type == 1:
                        imm = insn.operands[1].imm & 0xFFFFFFFF
                        if imm <= 0x200:  # focus small/med
                            rva_i = insn.address - imgbase
                            f.write(f'{rva_i:08X} {insn.address:08X} 0x{imm:02X}\n')
                            count += 1
                except Exception:
                    pass
    print(count)
    return 0

if __name__ == '__main__':
    sys.exit(main())
