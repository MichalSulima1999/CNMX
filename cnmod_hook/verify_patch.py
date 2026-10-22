import struct
from pathlib import Path

data = bytearray(Path('../CN.PLMOD.exe').read_bytes())

print('=== WERYFIKACJA PATCHA ===')

# 1. Limit jobów
limit = data[0x6BD35]
print(f'Limit jobów (0x6BD35): {hex(data[0x6BD35])} = {data[0x6BD35]}')

# 2. MOVZX disp32
movzx_disp = struct.unpack('<I', bytes(data[0x6BD3E:0x6BD42]))[0]
print(f'MOVZX disp32 (0x6BD3E): {hex(movzx_disp)} (oczekiwane 0x4F2200)')

# 2b. JMP table ref disp32
jmp_disp = struct.unpack('<I', bytes(data[0x6BD46:0x6BD4A]))[0]
print(f'JMP table disp32 (0x6BD46): {hex(jmp_disp)} (oczekiwane 0x4F2280)')

# 3. Case table
print(f'Case table[0..10]: {[hex(b) for b in data[0xF2200:0xF220A]]}')
print(f'Case table[55] (job 56): {hex(data[0xF2200+55])} (oczekiwane 0x12)')

# 4. Jump table
print('Jump table[0]:', hex(struct.unpack('<I', bytes(data[0xF2280:0xF2284]))[0]))
print(f'Jump table[18] (case 18): {hex(struct.unpack("<I", bytes(data[0xF2280+18*4:0xF2280+18*4+4]))[0])} (oczekiwane 0x4F2480)')

# 4. Kod case 18
code_start = 0xF2480
print(f'Case 18 code (0xF2480): {" ".join(hex(b) for b in data[0xF2480:0xF2490])}')

# Sprawdź CALL
call_rel = struct.unpack('<i', bytes(data[0xF2482:0xF2486]))[0]
call_target = 0xF2480 + 2 + 5 + call_rel
print(f'CALL rel32: {hex(call_rel)} -> target: {hex(call_target)} (oczekiwane 0x46D53A)')

# Sprawdź JMP
jmp_rel = struct.unpack('<i', bytes(data[0xF2487:0xF248B]))[0]
jmp_target = 0xF2480 + 7 + 5 + jmp_rel
print(f'JMP rel32: {hex(jmp_rel)} -> target: {hex(jmp_target)} (oczekiwane 0x46BE1B)')