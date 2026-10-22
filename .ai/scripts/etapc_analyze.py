#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etap C: klasyfikacja blokow cmp HOUSE/GOOD na patch-candidates vs dispatch.

Wejscie : bounds_all.txt (UTF-16, z kontekstem, naglowki '### cmp LABEL IMM ...')
Wyjscie : .ai/docs/etapc_patch_candidates.txt
Klasy   :
  BOUND  - po cmp skok warunkowy bounds (jl/jge/jg/jb/jae/jbe/ja/jle)
  LOOP   - wzorzec petli (inc/dec ... cmp ... jb/ja/jnz)
  DISP   - je/jne/switch-like (NIE patchowac bez kontekstu)
  OTHER  - brak skoku w oknie
"""
from __future__ import annotations

import re
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
SRC = Path(r"C:\Users\Michael1099\AppData\Local\Temp\opencode\bounds_all.txt")
OUT = BASE / ".ai" / "docs" / "etapc_patch_candidates.txt"

BOUNDS_JUMPS = {"jl", "jge", "jg", "jb", "jae", "jbe", "ja", "jle", "jns", "js"}
DISP_JUMPS = {"je", "jne", "jz", "jnz"}


def parse_blocks(path: Path):
    blocks = []
    cur = None
    with open(path, encoding="utf-16") as f:
        for line in f:
            if line.startswith("### "):
                if cur:
                    blocks.append(cur)
                m = re.match(r"### cmp (\S+) (\S+).*?0x([0-9A-Fa-f]+)", line)
                cur = (
                    {
                        "label": m.group(1),
                        "imm": m.group(2),
                        "va": int(m.group(3), 16),
                        "lines": [line.rstrip()],
                    }
                    if m
                    else None
                )
            elif cur is not None:
                cur["lines"].append(line.rstrip())
    if cur:
        blocks.append(cur)
    return blocks


def classify(block) -> tuple[str, str]:
    lines = block["lines"]
    star = next((i for i, l in enumerate(lines) if "*" in l), -1)
    if star < 0:
        return "OTHER", ""
    # skok w 3 liniach po oznaczonym cmp
    jump = ""
    for l in lines[star + 1 : star + 4]:
        m = re.search(r"[.*]\s+(j\w+)\s", l)
        if m:
            jump = m.group(1)
            break
    ctx = " ".join(lines[max(0, star - 3) : star + 3])
    is_loop = bool(re.search(r"(inc|dec)\s+\w+\s*$", lines[star - 1] or "")) or (
        "inc" in (lines[star - 1] if star >= 1 else "")
    )
    if jump in BOUNDS_JUMPS:
        return ("LOOP" if is_loop and jump in ("jb", "ja", "jne", "jnz") else "BOUND"), jump
    if jump in DISP_JUMPS:
        return "DISP", jump
    if jump == "jmp":
        return "OTHER", jump
    return "OTHER", jump or "-"


def main() -> int:
    if not SRC.is_file():
        print(f"missing {SRC}")
        return 1
    blocks = parse_blocks(SRC)
    stats: dict[str, dict[str, int]] = {}
    rows = []
    for b in blocks:
        if b["label"] not in ("HOUSE", "GOOD"):
            continue
        cls, jump = classify(b)
        stats.setdefault(b["label"], {}).setdefault(cls, 0)
        stats[b["label"]][cls] += 1
        rows.append((b["label"], b["va"], int(b["imm"], 10), cls, jump))

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("# label VA imm class jump\n")
        for label, va, imm, cls, jump in sorted(rows, key=lambda r: (r[0], r[1])):
            f.write(f"{label:5s} {va:08X} {imm:3d} {cls:5s} {jump}\n")

    for label in sorted(stats):
        print(label, stats[label])
    print(f"total {len(rows)} -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
