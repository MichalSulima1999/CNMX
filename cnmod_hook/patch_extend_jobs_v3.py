#!/usr/bin/env python3
"""
Patch rozszerzający limit jobów z 46 na 128 - wersja bez nowego kodu.
Mapuje job 56 (smolarz) na istniejącą obsługę garncarza (case 13).
"""

import sys
import struct
from pathlib import Path

EXE_PATH = Path(__file__).parent.parent / "CN.PLMOD.exe"

def main():
    EXE_PATH = Path(__file__).parent.parent / "CN.PLMOD.exe"
    if not EXE_PATH.exists():
        print(f"Nie znaleziono: {EXE_PATH}")
        return 1
    
    data = bytearray(EXE_PATH.read_bytes())
    print(f"Rozmiar pliku: {len(data)} bajtów")
    
    # 1. PATCH LIMIT: CMP EAX, 0x2E -> CMP EAX, 0x7F (127)
    # 0x46BD33: 83 F8 2E  ->  83 F8 7F
    data[0x6BD35] = 127  # 0x7F
    print(f"Patch 1: Limit jobów @ 0x6BD35: 46 -> 128")
    
    # 2. NOWA CASE TABLE (VA 0x4F2200, offset 0xF2200)
    # Job 56 (smolarz) -> case 13 (ten sam co garncarz)
    new_case = bytearray(128)
    orig_mapping = {
        1:0,2:0,3:0,4:1,5:2,6:3,7:4,8:5,9:5,10:5,11:5,12:5,13:5,14:5,15:6,16:7,
        17:7,18:7,19:7,20:8,21:2,22:9,23:10,24:2,25:2,26:11,27:12,28:13,
        29:2,30:2,31:2,32:2,33:14,34:15,35:16,36:17,37:1,38:2,39:2,40:2,
        41:2,42:2,43:2,44:2,45:2,46:2,
    }
    for job_id in range(1, 129):
        new_case[job_id - 1] = orig_mapping.get(job_id, 0)
    
    # Job 56 (smolarz) -> case 13 (ten sam co garncarz job 25)
    new_case[55] = 13  # job 56 - 1 = 55
    
    data[0xF2200:0xF2200+128] = new_case
    print(f"Patch 2: Nowa case table @ 0xF2200 (128B), job 56 -> case 13")
    
    # 3. NOWA JUMP TABLE (VA 0x4F2280, offset 0xF2280)
    # Kopia oryginalnej + case 18 -> ten sam handler co case 13 (garncarz)
    new_jump = bytearray(128 * 4)
    orig_jump = {
        0:  0x46BD4A, 1: 0x46BD6A, 2: 0x46BDE5, 3: 0x46BD76,
        4:  0x46BD82, 5: 0x46BD8E, 6: 0x46BD9A, 7: 0x46BDC1,
        8:  0x46BDA6, 9: 0x46BDAF, 10: 0x46BDB8, 11: 0x46BDCA,
        12: 0x46BDD3, 13: 0x46BDDC, 14: 0x46BDF7, 15: 0x46BE00,
        16: 0x46BE09, 17: 0x46BE12,  # case 17 -> default
    }
    for i in range(128):
        target = 0x46BE1B if i not in orig_jump else orig_jump[i]
        struct.pack_into('<I', new_jump, i * 4, target)
    
    # Case 18 -> ten sam handler co case 13 (garncarz)
    struct.pack_into('<I', new_jump, 18 * 4, 0x46BDDC)
    
    data[0xF2280:0xF2280+512] = new_jump
    print(f"Patch 3: Nowa jump table @ 0xF2280 (512B), case 18 -> 0x46BDDC")
    
    # 4. PATCH MOVZX: zmień disp32 na nową case table (VA 0x4F2200)
    data[0x6BD3E:0x6BD42] = struct.pack('<I', 0x4F2200)
    print(f"Patch 4: MOVZX disp32 @ 0x6BD3E = 0x4F2200")
    
    # 5. PATCH JMP TABLE REF: JMP DWORD PTR [EAX*4 + disp32]
    data[0x6BD46:0x6BD4A] = struct.pack('<I', 0x4F2280)
    print(f"Patch 5: JMP table ref @ 0x6BD46 = 0x4F2280")
    
    # 6. LIMIT: CMP EAX, 0x2E -> 0x7F (127)
    data[0x6BD35] = 127
    print(f"Patch 6: Limit jobów @ 0x6BD35: 46 -> 128")
    
    # ZAPISZ
    EXE_PATH = Path(__file__).parent.parent / "CN.PLMOD.exe"
    EXE_PATH.write_bytes(data)
    print(f"\n✅ Zapisano: CN.PLMOD.exe")
    print(f"Limit jobów: 46 -> 128")
    print(f"Job 56 (smolarz) -> case 13 (garncarz handler)")
    return 0

if __name__ == "__main__":
    sys.exit(main())