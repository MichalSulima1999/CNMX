#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dump kontekstu disasm (±8 instr) dla kandydatow bound-cand 0x37/0x38/0x42."""
from pathlib import Path
from capstone import Cs, CS_ARCH_X86, CS_MODE_32
import pefile

BASE = Path(__file__).resolve().parents[2]
EXE = BASE / "CN.PLMOD.exe"
SRC = Path(r"C:\Users\Michael1099\AppData\Local\Temp\opencode\bounds_all.txt")
OUT = BASE / ".ai" / "docs" / "etapc_ctx_short.txt"

IMMS = {0x37, 0x38, 0x42}


def load_targets():
    targets = {}
    pat = "cmp"
    with open(SRC, encoding="utf-8", errors="replace") as f:
        for line in f:
            if pat not in line:
                continue
            # format: "  0x004097E9. cmp      eax, 0x37" / z * zamiast .
            if "0x" not in line:
                continue
            try:
                va = int(line.strip().split()[0].rstrip(".*"), 16)
                imm = int(line.rsplit("0x", 1)[1], 16)
            except (ValueError, IndexError):
                continue
            if imm in IMMS:
                targets.setdefault(va, imm)
    return sorted(targets.items())


def main():
    if not EXE.is_file():
        print("no exe")
        return 1
    pe = pefile.PE(str(EXE))
    for sec in pe.sections:
        if b".text" in sec.Name:
            data = sec.get_data()
            rva_text = sec.VirtualAddress
            break
    else:
        print("no .text")
        return 1

    md = Cs(CS_ARCH_X86, CS_MODE_32)
    md.detail = False
    img = pe.OPTIONAL_HEADER.ImageBase
    ts = img + rva_text

    targets = load_targets()
    print(f"targets: {len(targets)}")

    wnd = 8
    with open(OUT, "w", encoding="utf-8") as f:
        for va, imm in targets:
            f.write(f"=== {va:08X} cmp imm=0x{imm:02X} ({imm})\n")
            off = va - ts
            if not (0 <= off < len(data)):
                f.write("  <poza .text>\n\n")
                continue
            s = max(0, off - 64)
            e = min(len(data), off + 96)
            for insn in md.disasm(data[s:e], ts + s):
                if insn.address < va - wnd:
                    continue
                if insn.address > va + wnd:
                    break
                mark = " <<<" if insn.address == va else ""
                f.write(f"  {insn.address:08X}: {insn.mnemonic} {insn.op_str}{mark}\n")
            f.write("\n")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
