#!/usr/bin/env python3
"""
Patch: Dodanie smolarni (typ 57) i węgla (goodtype 66) do CN.PLMOD.exe

Strategia: Job 26 (0x1A) — NIE wymaga rozszerzania case table (limit 46)!

Co robi:
1. Patch jump_table[2] (job 4 slot) = nowy case handler (0x46BE26)
2. Dodaje nowy case (smolarz, job 26) w wolnej przestrzeni (0x46BE26)
3. Używa istniejącego potter handler (FUN_0046D53A) — uniwersalny!

Korzystaj z patch_all.py dla pełnego patchu (INI + binarka).
"""

import sys
import struct
from pathlib import Path

EXE_PATH = Path(__file__).parent.parent / "CN.PLMOD.exe"

def main() -> int:
    if not EXE_PATH.exists():
        print(f"Nie znaleziono: {EXE_PATH}")
        return 1

    data = bytearray(EXE_PATH.read_bytes())

    # === PATCH 1: jump_table[2] = 0x0046BE26 ===
    # jump_table jest pod 0x46BE76 (18 entries × 4B)
    # Index 2 = job 4 (job 3 = index 1, job 4 = index 2, itd.)
    # Ale case_table mapuje job -> jump_table index
    # Job 26 -> case_table[25] = 0x02 (bez zmian!)
    # Jump_table[2] = 0x46BE26 (nowy case)
    
    jump_table_addr = 0x46BE76
    new_jump_offset = 2  # jump_table[2]
    new_jump_value = 0x0046BE26

    patch1_offset = jump_table_addr + new_jump_offset * 4
    old_value = struct.unpack_from('<I', data, patch1_offset)[0]
    struct.pack_into('<I', data, patch1_offset, new_jump_value)
    print(f"Patch 1: jump_table[2] @ 0x{patch1_offset:06X}")
    print(f"  0x{old_value:08X} -> 0x{new_jump_value:08X}")

    # === PATCH 2: Nowy case w wolnej przestrzeni (0x46BE26) ===
    # Kod:
    #   MOV ECX, ESI          ; 89 F1
    #   CALL 0x0046D53A       ; E8 <rel32>
    #   JMP  0x0046BE26       ; E9 <rel32> (powrót do pętli)
    #   NOP NOP NOP            ; 90 90 90 (padding)

    new_case_addr = 0x46BE26
    call_target = 0x0046D53A  # Potter handler
    jmp_target = 0x0046BE26   # Powrót do samej instrukcji (pętla)

    # Oblicz rel32 dla CALL
    call_offset = new_case_addr + 2  # po MOV ECX, ESI (2 bajty)
    call_rel = call_target - (call_offset + 5)

    # Oblicz rel32 dla JMP
    jmp_offset = new_case_addr + 7  # po CALL (5 bajtów)
    jmp_rel = jmp_target - (jmp_offset + 5)

    # Pisz kod
    data[new_case_addr:new_case_addr+2] = b'\x89\xF1'      # MOV ECX, ESI
    struct.pack_into('<I', data, new_case_addr + 2, call_rel & 0xFFFFFFFF)  # CALL rel32
    data[new_case_addr + 6] = b'\xE9'                       # JMP opcode
    struct.pack_into('<I', data, new_case_addr + 7, jmp_rel & 0xFFFFFFFF)   # JMP rel32
    data[new_case_addr + 11:new_case_addr + 14] = b'\x90\x90\x90'            # NOP padding

    print(f"Patch 2: nowy case @ 0x{new_case_addr:06X}")
    print(f"  CALL 0x{call_target:06X} (rel32: 0x{call_rel & 0xFFFFFFFF:08X})")
    print(f"  JMP  0x{jmp_target:06X} (rel32: 0x{jmp_rel & 0xFFFFFFFF:08X})")

    # === PATCH 3 (opcjonalny): Zwiększ limit jobów z 46 na 127 ===
    # 0x46BD33: CMP EAX, 0x2E  ->  CMP EAX, 0x7F
    # Instrukcja: 83 F8 2E  ->  83 F8 7F
    limit_addr = 0x46BD33
    data[limit_addr + 2] = 0x7F  # 0x2E -> 0x7F (46 -> 127)
    print(f"Patch 3: limit jobów @ 0x{limit_addr:06X}")
    print(f"  0x2E (46) -> 0x7F (127)")

    # === Zapisz ===
    EXE_PATH.write_bytes(data)
    print(f"\nZapisano: {EXE_PATH}")
    print("Patch zakończony sukcesem!")
    print("\nNastępne kroki:")
    print("1. Edytuj houses.ini - dodaj smolarnię z job 26")
    print("2. Edytuj goodtypes.ini - dodaj węgiel (goodtype 66)")
    print("3. Uruchom grę i sprawdź czy smolarnia produkuje węgiel")
    return 0

if __name__ == "__main__":
    sys.exit(main())