# -*- coding: utf-8 -*-
"""Tymczasowa diagnostyka: stan plików danych vs .orig (CR-doubling, duplikaty)."""
import re
from collections import Counter
from pathlib import Path

ROOT = Path(r"G:\Games\CnMod 1.2")

TARGETS = [
    (r"CN.PLMOD\types\houses.ini", r"logictype (\d+)"),
    (r"CN.PLMOD\stringstext\gameobjects\houses.ini", r"stringn (\d+)"),
    (r"CN.PLMOD\budynki12\houses\houses.ini", r"LogicType 0 (\d+)"),
    (r"CN.PLMOD\types\goodtypes.ini", r"\btype (\d+)"),
    (r"CN.PLMOD\stringstext\gameobjects\goods.ini", r"stringn (\d+)"),
]


def stat(p: Path, pat: str):
    b = p.read_bytes()
    t = b.decode("cp1250", "replace")
    ids = re.findall(pat, t)
    lf = b.count(b"\n")
    crlf = b.count(b"\r\n")
    bare_cr = b.count(b"\r") - crlf
    print(f"{p.relative_to(ROOT)}")
    print(f"   size={len(b)}  LF={lf} CRLF={crlf} extraCR={bare_cr}  -> {'OK' if bare_cr==0 else 'DOUBLED CR!'}")
    c = Counter(ids)
    dups = {k: v for k, v in c.items() if v > 1}
    print(f"   entries={len(ids)} unique={len(c)} dups={dups}")
    orig = p.with_suffix(p.suffix + ".orig")
    if orig.is_file():
        ob = orig.read_bytes()
        ot = ob.decode("cp1250", "replace")
        oids = re.findall(pat, ot)
        print(f"   .orig: size={len(ob)} entries={len(oids)}")
        extra = [i for i in ids if i not in oids]
        missing = [i for i in oids if i not in ids]
        if extra:
            print(f"   + nowych id: {extra}")
        if missing:
            print(f"   - brak wobec .orig: {missing}")
        # czy tresc bez zmian liniowych sie zgadza (po normalizacji CRLF)
        norm = lambda s: s.replace("\r\n", "\n").replace("\r", "\n")
        if norm(t) == norm(ot):
            print("   tresc == .orig (po normalizacji nowlinow) + tylko dopiski")
    else:
        print("   brak .orig")
    print()


for rel, pat in TARGETS:
    p = ROOT / rel
    if p.is_file():
        stat(p, pat)
    else:
        print(f"{rel}: brak pliku\n")
