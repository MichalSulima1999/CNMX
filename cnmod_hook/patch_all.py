#!/usr/bin/env python3
"""
Pełny patch smolarni — INI + binarka (Job 56, limit 128)

Używa strategii Job 56 (rozszerzony limit 128) - poprawny limit!

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
logicworker 56 1
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
    """Patch CN.PLMOD.exe - limit 128, job 56"""
    if not EXE_PATH.exists():
        print(f"Nie znaleziono: {EXE_PATH}")
        return 1

    data = bytearray(EXE_PATH.read_bytes())

    # === PATCH 1: Limit jobów 46 -> 128 ===
    # 0x46BD33: 83 F8 2E -> 83 F8 7F
    limit_addr = 0x6BD33
    old = data[0x6BD35]
    data[0x6BD35] = 127  # 0x7F
    print(f"Patch 1: Limit jobów @ 0x6BD35: {old} -> 127")

    # === PATCH 2: MOVZX disp32 -> nowa case table (VA 0x4F2200) ===
    # 0x46BD3C: 0F B6 80 XX XX XX XX
    data[0x6BD3E:0x6BD42] = struct.pack('<I', 0x4F2200)
    print(f"Patch 2: MOVZX disp32 @ 0x6BD3E = 0x4F2200")

    # === PATCH 3: JMP table ref disp32 -> nowa jump table (VA 0x4F2280) ===
    data[0x6BD46:0x6BD4A] = struct.pack('<I', 0x4F2280)
    print(f"Patch 3: JMP table ref @ 0x6BD46 = 0x4F2280")

    # === PATCH 4: Nowa case table (VA 0x4F2200, offset 0xF2200) ===
    new_case = bytearray(128)
    # Oryginalne mapowanie job -> case_index
    orig_mapping = {
        1:0,2:0,3:0,4:1,5:2,6:3,7:4,8:5,9:5,10:5,11:5,12:5,14:5,15:6,16:7,
        17:7,18:7,19:7,20:8,21:2,22:9,23:10,24:2,25:2,26:11,27:12,28:13,
        29:2,30:2,31:2,32:2,33:14,34:15,35:16,36:17,37:1,38:2,39:2,40:2,
        41:2,42:2,43:2,44:2,45:2,46:2
    }
    for job_id in range(1, 129):
        new_case[job_id - 1] = orig_mapping.get(job_id, 0)
    # Job 56 (smolarz) -> case 18
    new_case[55] = 18  # job 56 - 1 = 55

    # Zapisz case table (offset 0xF2200)
    data[0xF2200:0xF2200+128] = new_case
    print(f"Patch 4: Case table @ 0xF2200 (128B)")

    # Nowa jump table (VA 0x4F2280, offset 0xF2280)
    new_jump = bytearray(128 * 4)
    orig_jump = {
        0: 0x46BD4A, 1: 0x46BD6A, 2: 0x46BDE5, 3: 0x46BD76,
        4: 0x46BD82, 5: 0x46BD8E, 6: 0x46BD9A, 7: 0x46BDC1,
        8: 0x46BDA6, 9: 0x46BDAF, 10: 0x46BDB8, 11: 0x46BDCA,
        12: 0x46BDD3, 13: 0x46BDDC, 14: 0x46BDF7, 15: 0x46BE00,
        16: 0x46BE09, 17: 0x46BE12,  # case 17 -> default
    }
    for i in range(128):
        target = 0x46BE1B if i not in orig_jump else orig_jump[i]
        struct.pack_into('<I', new_jump, i * 4, target)
    # Case 18 -> nowy kod
    struct.pack_into('<I', new_jump, 18 * 4, 0x4F2480)

    data[0xF2280:0xF2280+512] = new_jump
    print(f"Patch 5: Jump table @ 0xF2280 (512B)")

    # Nowy kod case'ów (VA 0x4F2480, offset 0xF2480)
    case_code = bytearray()
    # Case 18: Job 56 (Smolarz)
    case_code.extend([0x89, 0xF1])  # MOV ECX, ESI
    # CALL 0x46D53A
    call_rel = 0x46D53A - (0x4F2480 + 2 + 5)
    case_code.extend([0xE8])
    case_code.extend(struct.pack('<i', call_rel))
    # JMP OriginalDefault (0x46BE1B)
    jmp_rel = 0x46BE1B - (0x4F2480 + 2 + 5 + 5)
    case_code.extend([0xE9])
    case_code.extend(struct.pack('<i', jmp_rel))
    case_code.extend([0x90, 0x90, 0x90])  # NOP padding

    # Case 19-127 -> JMP default
    for i in range(19, 128):
        rel = 0x46BE1B - (0x4F2480 + 10 + (i - 19) * 5 + 5)
        case_code.extend([0xE9])
        case_code.extend(struct.pack('<i', rel))

    data[0xF2480:0xF2480 + len(case_code)] = case_code
    print(f"Patch 6: Kod case'ów @ 0xF2480 ({len(case_code)}B)")

    EXE_PATH.write_bytes(data)
    print(f"✅ Binarka zpatchowana")
    return 0


def patch_houses_ini() -> int:
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

    lines.insert(insert_idx, """[logichousetype]
debugname "smolarnia"
logictype 57
logicmaintype 3
logicworker 56 1
logicstock 5 10 1
logicstock 66 15 0
logicproduction 66
debugcolor 100 0 0
""")

    HOUSES_INI.write_text('\n'.join(lines), encoding='cp1250')
    print(f"Zaktualizowano: {HOUSES_INI}")
    return 0


def patch_goodtypes_ini() -> int:
    if not GOODTYPES_INI.exists():
        print(f"Nie znaleziono: {GOODTYPES_INI}")
        return 1

    content = GOODTYPES_INI.read_text(encoding='cp1250')

    if 'goodtype 66' in content:
        print("Węgiel (goodtype 66) już istnieje w goodtypes.ini")
        return 0

    lines = content.splitlines()
    lines.append('')
    lines.append("""[goodtype]
goodtype 66
type 12
name "wegiel"
landscapetype 0
isInputGoodFlag 1
isProducedInHouseFlag 1
atomicForProduction 1
""")

    GOODTYPES_INI.write_text('\n'.join(lines), encoding='cp1250')
    print(f"Zaktualizowano: {GOODTYPES_INI}")
    return 0


def main() -> int:
    print("=" * 60)
    print("PEŁNY PATCH SMOLARNI (Job 56, Limit 128)")
    print("=" * 60)

    if patch_binary(): return 1
    if patch_houses_ini(): return 1
    if patch_goodtypes_ini(): return 1

    print("\n" + "=" * 60)
    print("✅ WSZYSTKIE PATCHY ZASTOSOWANE POMYŚLNIE!")
    print("=" * 60)
    print("\nNastępne kroki:")
    print("1. Uruchom CN.PLMOD.exe")
    print("2. Zbuduj smolarnię (typ 57)")
    print("3. Zatrudnij smolarza (job 56)")
    print("3. Sprawdź czy produkuje węgiel (good 66)")
    print("4. Nazwa zawodu w UI będzie 'Potter' - wymaga hooka DLL dla nazwy")
    return 0


if __name__ == "__main__":
    sys.exit(main())