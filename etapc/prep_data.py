#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EtapC - przygotowanie danych testowych (spike).
1. types/houses.ini   : usun duplikat 'work well 00' (logictype 10 x2), dopisz logictype 56
2. budynki12/...      : dopisz 'LogicType 0 56' (wspoldzielona grafika z 'viking well')
3. stringstext/...    : dopisz stringn 56
Plik jest bezpieczny do ponownego odpalenia (idempotentne: sprawdzamy czy pola istnieja).
"""
import shutil
from pathlib import Path

ROOT = Path(r"G:\Games\CnMod 1.2")
TYPES = ROOT / "CN.PLMOD" / "types" / "houses.ini"
GFXH = ROOT / "CN.PLMOD" / "budynki12" / "houses" / "houses.ini"
NAMES = ROOT / "CN.PLMOD" / "stringstext" / "gameobjects" / "houses.ini"


def backup(p: Path):
    orig = p.with_suffix(p.suffix + ".etapc.bak")
    if not orig.is_file():
        shutil.copy2(p, orig)


def main():
    # 1. types/houses.ini
    backup(TYPES)
    txt = TYPES.read_text(encoding="utf-8")
    # wytnij ostatni blok logichousetype 'work well 00'
    blocks = []
    cur = None
    for line in txt.splitlines(keepends=True):
        if line.startswith("[logichousetype]"):
            cur = [line]
        elif cur is not None:
            cur.append(line)
    if cur and blocks and blocks[-1] is cur:
        pass
    # prostsze: ostatni logichousetype w pliku to duplikat z logictype 10 - zamien na 56
    idx = txt.rfind("[logichousetype]")
    if idx < 0:
        raise SystemExit("no section")
    sec = txt[idx:]
    if "logictype 56" in sec:
        print("types: logictype 56 juz jest - pominieto")
    else:
        sec_new = sec.replace("logictype 10", "logictype 56", 1)
        txt = txt[:idx] + sec_new
        TYPES.write_text(txt, encoding="utf-8")
        print("types: zaktualizowano duplikat -> logictype 56")

    # 2. GfxHouse: dostaw LogicType 0 56 po pierwszym 'LogicType 0 10'
    backup(GFXH)
    gfxtxt = GFXH.read_text(encoding="utf-8")
    anchor = "LogicType 0 10\n"
    needle = "LogicType 0 56\n"
    if needle in gfxtxt:
        print("gfx: LogicType 0 56 juz jest - pominieto")
    elif anchor not in gfxtxt:
        print("gfx: brak kotwicy 'LogicType 0 10'")
    else:
        gfxtxt = gfxtxt.replace(anchor, anchor + needle, 1)
        GFXH.write_text(gfxtxt, encoding="utf-8")
        print("gfx: dodano LogicType 0 56")

    # 3. nazwa
    backup(NAMES)
    ntxt = NAMES.read_text(encoding="utf-8")
    entry = 'stringn 56 "Studnia EtapC"\n'
    if "stringn 56" in ntxt:
        print("names: stringn 56 juz jest - pominieto")
    else:
        ntxt = ntxt.rstrip("\n") + "\n\n" + entry
        NAMES.write_text(ntxt, encoding="utf-8")
        print("names: dodano stringn 56")


if __name__ == "__main__":
    main()