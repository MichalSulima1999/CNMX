#!/usr/bin/env python3
"""
Pełny patch rozszerzający limit jobów z 46 na 128.

Strategia:
1. Nowe tabele (case + jump) w wolnej przestrzeni między .text a .rdata (VA 0x4F2200)
2. Patch dyspozytora by używał nowych tabel
4. Zmiana limitu CMP z 46 na 128
5. Dodanie case'a dla job 56 (smolarz)
"""

import sys
import struct
from pathlib import Path

EXE_PATH = Path(__file__).parent.parent / "CN.PLMOD.exe"
IMAGE_BASE = 0x400000

def va_to_offset(va):
    """Konwertuj Virtual Address na file offset"""
    return va - 0x400000

# ============================================================================
# Adresy oryginalne (VA) i ich file offsety
# ============================================================================
# Instrukcje w .text section
VA_CMP_LIMIT      = 0x46BD33      # CMP EAX, 0x2E
VA_MOVZX          = 0x46BD3C      # MOVZX EAX, BYTE PTR [EAX + disp32]
VA_JMP_TABLE_REF  = 0x46BD43      # JMP DWORD PTR [EAX*4 + disp32]
VA_ORIG_DEFAULT   = 0x46BE1B      # Default handler
VA_CASE_TABLE     = 0x46BEBE      # Oryginalna case table (VA)
VA_JUMP_TABLE     = 0x46BE76      # Oryginalna jump table (VA)
VA_POTTER_HANDLER = 0x46D53A      # Potter handler
VA_ORIG_DEFAULT2  = 0x46BE1B      # Default handler (drugi)

# File offsety
def va_to_off(va): return va - 0x400000

OFF_CMP_LIMIT      = va_to_offset(0x46BD33)
OFF_MOVZX          = va_to_offset(0x46BD3C)
OFF_JMP_TABLE_REF  = va_to_offset(0x46BD43)
OFF_ORIG_DEFAULT   = va_to_offset(0x46BE1B)
OFF_CASE_TABLE     = va_to_offset(0x46BEBE)
OFF_JUMP_TABLE     = va_to_offset(0x46BE76)
OFF_POTTER_HANDLER = va_to_offset(0x46D53A)
OFF_ORIG_DEFAULT2  = va_to_offset(0x46BE1B)
OFF_POTTER_HANDLER = va_to_offset(0x46D53A)

# ============================================================================
# Nowe adresy (VA) w wolnej przestrzeni między .text a .rdata
# .text kończy się na VA 0x4F21CB, .rdata zaczyna na 0x4F3000
# Wolne: 0x4F2200 - 0x4F2FFF (~3.5 KB)
# ============================================================================
NEW_TABLE_BASE_VA = 0x4F2200          # VA nowych tabel
NEW_CASE_TABLE_VA = 0x4F2200          # 128 entries × 1B
NEW_JUMP_TABLE_VA = 0x4F2200 + 128    # 128 × 4B = 512B
NEW_CASE_CODE_VA = 0x4F2200 + 128 + 512  # Kod nowych case'ów

NEW_JOB_LIMIT = 128
JOB_SMOLARZ = 56
JOB_POTTER = 25

def va_off(va): return va - 0x400000

# ============================================================================
# Generowanie nowej case table (128 entries)
# ============================================================================

def build_new_case_table():
    orig_mapping = {
        1: 0, 2: 0, 3: 0, 4: 1, 5: 2, 6: 3, 7: 4, 8: 5,
        9: 5, 10: 5, 11: 5, 12: 5, 13: 5, 14: 5, 15: 6, 16: 7,
        17: 7, 18: 7, 19: 7, 20: 8, 21: 2, 22: 9, 23: 10,
        24: 2, 25: 2, 26: 11, 27: 12, 28: 13,
        29: 2, 30: 2, 31: 2, 32: 2, 33: 14, 34: 15, 35: 16,
        36: 17, 37: 1, 38: 2, 39: 2, 40: 2, 41: 2, 42: 2, 43: 2,
        44: 2, 45: 2, 46: 2,
    }
    
    new_table = bytearray(128)
    for job_id in range(1, 129):
        new_table[job_id - 1] = orig_mapping.get(job_id, 0)
    
    # Job 56 (smolarz) -> case 18
    new_table[55] = 18  # job 56 - 1 = 55
    return new_table

def build_new_jump_table():
    orig_jump = {
        0:  0x46BD4A, 1: 0x46BD6A, 2: 0x46BDE5, 3: 0x46BD76,
        4:  0x46BD82, 5: 0x46BD8E, 6: 0x46BD9A, 7: 0x46BDC1,
        8:  0x46BDA6, 9: 0x46BDAF, 10: 0x46BDB8, 11: 0x46BDCA,
        12: 0x46BDD3, 13: 0x46BDDC, 14: 0x46BDF7, 15: 0x46BE00,
        16: 0x46BE09, 17: 0x46BE12,  # case 17 -> default
    }
    
    jump_table = bytearray(128 * 4)
    for i in range(128):
        target = orig_jump.get(i, 0x46BE1B)  # default
        struct.pack_into('<I', jump_table, i * 4, target)
    
    # Case 18 (job 56) -> nowy kod
    struct.pack_into('<I', jump_table, 18 * 4, 0x4F2200 + 128 + 512)
    return jump_table

def build_new_case_code():
    code = bytearray()
    # Case 18: Job 56 (Smolarz)
    # MOV ECX, ESI
    code.extend([0x89, 0xF1])
    # CALL 0x46D53A (potter handler)
    call_rel = 0x46D53A - (0x4F2200 + 128 + 512 + 2 + 5)
    code.extend([0x89, 0xF1])  # MOV ECX, ESI
    code.extend(struct.pack('<i', 0x46D53A - (0x4F2200 + 128 + 512 + 2 + 5)))
    # JMP OriginalDefault (0x46BE1B)
    jmp_rel = 0x46BE1B - (0x4F2200 + 128 + 512 + 7 + 5)
    code.extend([0xE9])
    code.extend(struct.pack('<i', 0x46BE1B - (0x4F2200 + 128 + 512 + 7 + 5)))
    code.extend([0x90, 0x90, 0x90])  # NOP padding
    
    # Case 19-127 -> JMP default
    for i in range(19, 128):
        rel = 0x46BE1B - (0x4F2200 + 128 + 512 + 10 + (i - 19) * 5 + 5)
        code.extend([0xE9])
        code.extend(struct.pack('<i', rel))
    return code

def main():
    EXE_PATH = Path(__file__).parent.parent / "CN.PLMOD.exe"
    if not EXE_PATH.exists():
        print(f"Nie znaleziono: {EXE_PATH}")
        return 1
    
    data = bytearray(EXE_PATH.read_bytes())
    print(f"Rozmiar pliku: {len(data)} bajtów")
    
    # ========================================================================
    # 1. PATCH LIMIT: CMP EAX, 0x2E -> CMP EAX, 0x7F (127)
    # Adres: 0x46BD33 (file offset 0x6BD33), bajt +2
    # ========================================================================
    off_cmp = va_to_offset(0x46BD33)  # 0x6BD33
    old = data[0x6BD33 + 2]
    data[0x6BD33 + 2] = 127  # 0x7F
    print(f"Patch 1: Limit @ 0x6BD35: 0x46 -> 0x7F (128)")
    
    # ========================================================================
    # 2. NOWA CASE TABLE (VA 0x4F2200, file offset 0xF2200)
    # ========================================================================
    new_case_table = build_new_case_table()
    off_case = va_to_offset(0x4F2200)  # 0xF2200
    
    # Weryfikuj miejsce
    for i in range(128):
        if data[0xF2200 + i] != 0:
            print(f"UWAGA: 0xF2200+{i} = 0x{data[0xF2200+i]:02X}")
    
    data[0xF2200:0xF2200+128] = build_new_case_table()
    print(f"Patch 2: Nowa case table @ 0xF2200 (128B)")
    
    # ========================================================================
    # 3. NOWA JUMP TABLE (VA 0x4F2280, offset 0xF2280)
    # ========================================================================
    new_jump = build_new_jump_table()
    data[0xF2280:0xF2280+512] = build_new_jump_table()
    print(f"Patch 3: Nowa jump table @ 0xF2280 (512B)")
    
    # ========================================================================
    # 5. PATCH MOVZX: zmień disp32 na nową case table (VA 0x4F2200)
    # Instrukcja: 0F B6 80 disp32  (MOVZX EAX, BYTE PTR [EAX + disp32])
    # Adres instrukcji: 0x46BD3C (offset 0x6BD3C)
    # disp32 jest w bajtach +2..+5 instrukcji (po 0F B6 80)
    # Nowy disp32 = VA nowej case table = 0x4F2200
    # ========================================================================
    off_movzx = 0x6BD3C  # file offset instrukcji MOVZX
    new_disp32 = 0x4F2200  # VA nowej case table
    data[0x6BD3C + 2:0x6BD3C + 6] = struct.pack('<I', 0x4F2200)
    print(f"Patch MOVZX: disp32 @ 0x6BD3E = 0x4F2200")
    
    # ========================================================================
    # 5. PATCH JMP TABLE REF: JMP DWORD PTR [EAX*4 + disp32]
    # Instrukcja: FF 24 85 disp32
    # Adres: 0x46BD43 (offset 0x6BD43)
    # disp32 w bajtach +3..+6 (po FF 24 85)
    # Nowy disp32 = VA nowej jump table = 0x4F2280
    # ========================================================================
    new_jump_table_va = 0x4F2280  # 0x4F2200 + 128
    data[0x6BD43 + 3:0x6BD43 + 7] = struct.pack('<I', 0x4F2280)
    print(f"Patch JMP table ref: disp32 @ 0x6BD46 = 0x4F2280")
    
    # ========================================================================
    # 3. NOWA JUMP TABLE (VA 0x4F2280, offset 0xF2280)
    # ========================================================================
    new_jump = build_new_jump_table()
    data[0xF2280:0xF2280+512] = build_new_jump_table()
    print(f"Patch 3: Nowa jump table @ 0xF2280 (512B)")
    
    # ========================================================================
    # 4. NOWY KOD CASE'ÓW (VA 0x4F2480, offset 0xF2480)
    # ========================================================================
    case_code_va = 0x4F2200 + 128 + 512  # 0x4F2480
    off_code = va_to_offset(case_code_va)  # 0xF2480
    
    # Generuj kod
    case_code = bytearray()
    # Case 18: Job 56 (Smolarz)
    # MOV ECX, ESI
    case_code.extend([0x89, 0xF1])
    # CALL 0x46D53A
    call_rel = 0x46D53A - (0x4F2200 + 128 + 512 + 2 + 5)
    case_code.extend([0xE8])
    case_code.extend(struct.pack('<i', call_rel))
    # JMP OriginalDefault (0x46BE1B)
    jmp_rel = 0x46BE1B - (0x4F2200 + 128 + 512 + 2 + 5 + 5)
    case_code.extend([0xE9])
    case_code.extend(struct.pack('<i', 0x46BE1B - (0x4F2200 + 128 + 512 + 7 + 5)))
    # NOP padding
    case_code.extend([0x90, 0x90, 0x90])
    
    # Case 19-127 -> JMP default
    for i in range(19, 128):
        rel = 0x46BE1B - (0x4F2200 + 128 + 512 + 10 + (i - 19) * 5 + 5)
        case_code.extend([0xE9])
        case_code.extend(struct.pack('<i', rel))
    
    off_code = va_to_offset(0x4F2200 + 128 + 512)  # 0xF2480
    data[0xF2480:0xF2480 + len(case_code)] = case_code
    print(f"Patch 4: Kod case'ów @ 0xF2480 ({len(case_code)}B)")
    
    # ========================================================================
    # ZAPISZ
    # ========================================================================
    EXE_PATH = Path(__file__).parent.parent / "CN.PLMOD.exe"
    EXE_PATH.write_bytes(data)
    print(f"\n✅ Zapisano: CN.PLMOD.exe")
    print(f"Limit jobów: 46 -> 128")
    print(f"Nowe tabele: VA 0x4F2200 - 0x4F2800")
    print(f"Job 56 (smolarz) w case 18")
    return 0

def va_off(va): return va - 0x400000

if __name__ == "__main__":
    sys.exit(main())