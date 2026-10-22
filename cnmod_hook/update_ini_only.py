#!/usr/bin/env python3
"""Tylko aktualizacja plików INI - bez patchowania binarki."""

from pathlib import Path
import sys

ROOT = Path(__file__).parent.parent
HOUSES_INI = ROOT / "CN.PLMOD" / "types" / "houses.ini"
GOODTYPES_INI = ROOT / "Data" / "logic" / "goodtypes.ini"

SMOLARNIA_HOUSE = """[logichousetype]
debugname "smolarnia"
logictype 57
logicmaintype 3
logicworker 56 1
logicstock 5 10 1
logicstock 66 15 0
logicproduction 66
debugcolor 100 0 0
"""

WEGIEL_GOOD = """[goodtype]
goodtype 66
type 66
name "wegiel"
landscapetype 7
isInputGoodFlag 1
isProducedInHouseFlag 1
atomicForProduction 1
"""

def patch_houses_ini():
    if not HOUSES_INI.exists():
        print(f"Nie znaleziono: {HOUSES_INI}")
        return 1
    content = HOUSES_INI.read_text(encoding='cp1250')
    if 'logictype 57' in content:
        print("Smolarnia (logictype 57) już istnieje w houses.ini")
        return 0
    lines = content.splitlines()
    insert_idx = len(lines)
    for i, line in enumerate(lines):
        if line.strip().startswith('[tribetypes') or line.strip().startswith('[logictribetype'):
            insert_idx = i
            break
    if insert_idx > 0 and lines[insert_idx - 1].strip() != '':
        lines.insert(insert_idx, '')
        insert_idx += 1
    lines.insert(insert_idx, SMOLARNIA_HOUSE.strip())
    HOUSES_INI.write_text('\n'.join(lines), encoding='cp1250')
    print(f"Zaktualizowano: {HOUSES_INI}")
    return 0

def patch_goodtypes_ini():
    if not GOODTYPES_INI.exists():
        print(f"Nie znaleziono: {GOODTYPES_INI}")
        return 1
    content = GOODTYPES_INI.read_text(encoding='cp1250')
    if 'type 66' in content and 'landscapetype 7' in content:
        print("Węgiel (type 66) z landscape 7 już istnieje w goodtypes.ini")
        return 0
    lines = content.splitlines()
    lines.append('')
    lines.append("""[goodtype]
goodtype 66
type 66
name "wegiel"
landscapetype 7
isInputGoodFlag 1
isProducedInHouseFlag 1
atomicForProduction 1
""")
    GOODTYPES_INI.write_text('\n'.join(lines), encoding='cp1250')
    print(f"Zaktualizowano: {GOODTYPES_INI}")
    return 0

def main():
    print("Aktualizacja plików INI...")
    if patch_houses_ini(): return 1
    if patch_goodtypes_ini(): return 1
    print("✅ INI zaktualizowane")
    return 0

if __name__ == "__main__":
    sys.exit(main())