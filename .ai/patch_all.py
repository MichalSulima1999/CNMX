#!/usr/bin/env python3
"""
Pełny patch smolarni — INI + binarka

Używa strategii Job 26 (0x1A) — nie wymaga rozszerzania case table!

Wymagane pliki:
- CN.PLMOD.exe (binarka)
- CN.PLMOD/types/houses.ini
- Data/logic/goodtypes.ini
"""

import sys
import struct
import configparser
from pathlib import Path

ROOT = Path(__file__).parent.parent
EXE_PATH = ROOT / "CN.PLMOD.exe"
HOUSES_INI = ROOT / "CN.PLMOD" / "types" / "houses.ini"
GOODTYPES_INI = ROOT / "Data" / "logic" / "goodtypes.ini"

SMOLARNIA_HOUSE = """[logichousetype]
debugname "smolarnia"
logictype 57
logicmaintype 3
logicworker 26 1
logicstock 5 10 1
logicstock 66 15 0
logicproduction 66
debugcolor 100 0 0
"""

WEGIEL_GOOD = """[goodtype]
goodtype 66
type 12
name "wegiel"
landscapetype 0
isInputGoodFlag 1
isProducedInHouseFlag 1
atomicForProduction 1
"""

def patch_binary() -> int:
    """Patch CN.PLMOD.exe"""
    if not EXE_PATH.exists():
        print(f"Nie znaleziono: {EXE_PATH}")
        return 1

    data = bytearray(EXE_PATH.read_bytes())

    # === PATCH 1: jump_table[2] = 0x0046BE26 ===
    jump_table_addr = 0x46BE76
    new_jump_offset = 2  # job 4 slot (case_table[25] = 0x02 -> jump_table[2])
    new_jump_value = 0x0046BE26

    patch1_offset = jump_table_addr + new_jump_offset * 4
    old_value = struct.unpack_from('<I', data, patch1_offset)[0]
    struct.pack_into('<I', data, patch1_offset, new_jump_value)
    print(f"Patch 1: jump_table[2] @ 0x{patch1_offset:06X}")
    print(f"  0x{old_value:08X} -> 0x{new_jump_value:08X}")

    # === PATCH 2: Nowy case (smolarz, job 26) ===
    new_case_addr = 0x46BE26
    call_target = 0x0046D53A
    jmp_target = 0x0046BE26

    call_offset = new_case_addr + 2
    call_rel = call_target - (call_offset + 5)
    jmp_offset = new_case_addr + 7
    jmp_rel = jmp_target - (jmp_offset + 5)

    data[new_case_addr:new_case_addr+2] = b'\x89\xF1'
    struct.pack_into('<I', data, new_case_addr + 2, call_rel & 0xFFFFFFFF)
    data[new_case_addr + 6] = b'\xE9'
    struct.pack_into('<I', data, new_case_addr + 7, jmp_rel & 0xFFFFFFFF)
    data[new_case_addr + 11:new_case_addr + 14] = b'\x90\x90\x90'

    print(f"Patch 2: nowy case @ 0x{new_case_addr:06X}")
    print(f"  CALL 0x{call_target:06X} (rel32: 0x{call_rel & 0xFFFFFFFF:08X})")
    print(f"  JMP  0x{jmp_target:06X} (rel32: 0x{jmp_rel & 0xFFFFFFFF:08X})")

    # === PATCH 3: Zwiększ limit jobów (opcjonalnie) ===
    limit_addr = 0x46BD33
    data[limit_addr + 2] = 0x7F
    print(f"Patch 3: limit jobów @ 0x{limit_addr:06X} (46 -> 127)")

    EXE_PATH.write_bytes(data)
    print(f"Zapisano: {EXE_PATH}")
    return 0


def patch_houses_ini() -> int:
    """Dodaj smolarnię do houses.ini"""
    if not HOUSES_INI.exists():
        print(f"Nie znaleziono: {HOUSES_INI}")
        return 1

    content = HOUSES_INI.read_text(encoding='cp1250')

    # Sprawdź czy już istnieje
    if 'logictype 57' in content:
        print("Smolarnia (logictype 57) już istnieje w houses.ini")
        return 0

    # Dodaj na końcu przed sekcją tribetypes (jeśli jest) lub na końcu
    lines = content.splitlines()
    insert_idx = len(lines)
    for i, line in enumerate(lines):
        if line.strip().startswith('[tribetypes') or line.strip().startswith('[logictribetype'):
            insert_idx = i
            break

    # Dodaj pustą linię przed nową sekcją
    if insert_idx > 0 and lines[insert_idx - 1].strip() != '':
        lines.insert(insert_idx, '')
        insert_idx += 1

    lines.insert(insert_idx, SMOLARNIA_HOUSE.strip())

    HOUSES_INI.write_text('\n'.join(lines), encoding='cp1250')
    print(f"Zaktualizowano: {HOUSES_INI}")
    return 0


def patch_goodtypes_ini() -> int:
    """Dodaj węgiel do goodtypes.ini"""
    if not GOODTYPES_INI.exists():
        print(f"Nie znaleziono: {GOODTYPES_INI}")
        return 1

    content = GOODTYPES_INI.read_text(encoding='cp1250')

    if 'goodtype 66' in content:
        print("Węgiel (goodtype 66) już istnieje w goodtypes.ini")
        return 0

    # Dodaj na końcu
    lines = content.splitlines()
    lines.append('')
    lines.append(WEGIEL_GOOD.strip())

    GOODTYPES_INI.write_text('\n'.join(lines), encoding='cp1250')
    print(f"Zaktualizowano: {GOODTYPES_INI}")
    return 0


def main() -> int:
    print("=" * 60)
    print("PEŁNY PATCH SMOLARNI (Job 26)")
    print("=" * 60)

    if patch_binary():
        return 1
    if patch_houses_ini():
        return 1
    if patch_goodtypes_ini():
        return 1

    print("\n" + "=" * 60)
    print("WSZYSTKIE PATCHY ZASTOSOWANE POMYŚLNIE!")
    print("=" * 60)
    print("\nNastępne kroki:")
    print("1. Uruchom CN.PLMOD.exe")
    print("2. Zbuduj smolarnię (typ 57)")
    print("3. Sprawdź czy produkuje węgiel (good 66)")
    print("4. Jeśli nazwa zawodu w UI to 'Potter' -> wymaga hooka DLL")
    return 0


if __name__ == "__main__":
    sys.exit(main())