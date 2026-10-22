#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Etap E helpers (scaffolding) dla modkit - dodane komendy: template-house, template-good.
Brak ingerencji w istniejące funkcje."""
import sys
from pathlib import Path

TEMPLATE_HOUSE = """[logichousetype]

debugname "NEW_BUILDING"

logictype {to_id}

logicmaintype 3

debugcolor 0 128 0
"""

TEMPLATE_GFX = """[GfxHouse]

EditName "NEW_BUILDING"

EditGroups "none"

LogicMaximumSize 1

LogicType 0 {to_id}

LogicTribeType 1

logichitpoints 0 100000
"""

TEMPLATE_GOOD = """[goodtype]

type {to_id}

name "NEW_GOOD"

category 1

isresource 1

debugcolor 0 128 0
"""

TPL_NAMES_H = '''stringn {to_id} "Nowy budynek"
'''

TPL_NAMES_G = '''stringn {to_id} "Nowy surowiec"
'''

# append helpers (minimal)
def _append_file(p: Path, s: str):
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, 'a', encoding='utf-8') as f:
        f.write(s)

def cmd_template_house(root: Path, _cif, args):
    to_id = int(args.id)
    # types
    p = root / 'CN.PLMOD' / 'types' / 'houses.ini'
    _append_file(p, '\n\n' + TEMPLATE_HOUSE.format(to_id=to_id))
    # gfx
    pg = root / 'CN.PLMOD' / 'budynki12' / 'houses' / 'houses.ini'
    _append_file(pg, '\n\n' + TEMPLATE_GFX.format(to_id=to_id))
    # names
    pn = root / 'CN.PLMOD' / 'stringstext' / 'gameobjects' / 'houses.ini'
    _append_file(pn, '\n\n' + TPL_NAMES_H.format(to_id=to_id))
    print(f'szablon domu {to_id} dodany (pamiętaj o limicie exe bez overlayu)')
    return 0

def cmd_template_good(root: Path, _cif, args):
    to_id = int(args.id)
    pg = root / 'CN.PLMOD' / 'types' / 'goodtypes.ini'
    _append_file(pg, '\n\n' + TEMPLATE_GOOD.format(to_id=to_id))
    pn = root / 'CN.PLMOD' / 'stringstext' / 'gameobjects' / 'goods_pol.ini'
    if not pn.is_file():
        pn = root / 'CN.PLMOD' / 'stringstext' / 'gameobjects' / 'goods.ini'
    _append_file(pn, '\n\n' + TPL_NAMES_G.format(to_id=to_id))
    print(f'szablon surowca {to_id} dodany')
    return 0
