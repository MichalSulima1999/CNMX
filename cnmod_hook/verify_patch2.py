import struct
from pathlib import Path

data = bytearray(Path('../CN.PLMOD.exe').read_bytes())

print('=== WERYFIKACJA PATCHA ===')

# 1. Limit jobów
print(f'Limit jobów (0x6BD35): {hex(data[0x6BD35])} = {data[0x6BD35]}')

# 2. MOVZX disp32
movzx_disp = struct.unpack('<I', bytes(data[0x6BD3E:0x6BD42]))[0]
print(f'MOVZX disp32 (0x6BD3E): {hex(movzx_disp)} (oczekiwane 0x4F2200)')

# 2b. JMP table ref
jmp_disp = struct.unpack('<I', bytes(data[0x6BD46:0x6BD4A]))[0]
print(f'JMP table disp32 (0x6BD46): {hex(jmp_disp)} (oczekiwane 0x4F2280)')

# 3. Case table
print(f'Case table[0..10]: {[hex(b) for b in data[0xF2200:0xF220A]]}')
print(f'Case table[55] (job 56): {hex(data[0xF2200+55])} (oczekiwane 0x12)')

# 3. Jump table
print(f'Jump table[0]: {hex(struct.unpack("<I", bytes(data[0xF2280:0xF2284]))[0])}')
print(f'Jump table[18] (case 18): {hex(struct.unpack("<I", bytes(data[0xF2280+18*4:0xF2280+18*4+4]))[0])} (oczekiwane 0x4F2480)')

# 4. Kod case 18 (VA 0x4F2480, offset 0xF2480)
print(f'Case 18 code (0xF2480): {" ".join(hex(b) for b in data[0xF2480:0xF24A0])}')

# Sprawdź CALL - rel32 jest po E8 (bajty 1-4)
call_rel = struct.unpack('<i', bytes(data[0xF2483:0xF2487]))[0]
call_target = 0x4F2480 + 2 + 5 + call_rel
print(f'CALL rel32: {hex(call_rel)} -> target: {hex(call_target)} (oczekiwane 0x46D53A)')

# Sprawdź JMP - rel32 po E9 (bajty 1-4 po E9)
# Kod case 18: 89 F1 E8 xx xx xx xx E9 xx xx xx xx 90 90 90
# E9 jest na offset 7 od początku case 18 (po 89 F1 E8 xx xx xx xx)
# rel32 JMP jest na offset 8-11 od początku
jmp_rel = struct.unpack('<i', bytes(data[0xF2488:0xF248C]))[0]
jmp_target = 0xF2480 + 8 + 5 + struct.unpack('<i', bytes(data[0xF2488:0xF248C]))[0]
# Wait, let me check the exact layout
print(f'Bytes at 0xF2480: {" ".join(hex(b) for b in data[0xF2480:0xF24A0])}')

# JMP is at offset 7 from start of case code (after 89 F1 E8 xx xx xx xx = 7 bytes)
# So JMP rel32 is at offset 8-11 from start
jmp_rel2 = struct.unpack('<i', bytes(data[0xF2488:0xF248C]))[0]
jmp_target2 = 0xF2480 + 8 + 5 + struct.unpack('<i', bytes(data[0xF2488:0xF248C]))[0]
print(f'JMP rel32 (offset 8): {hex(struct.unpack("<i", bytes(data[0xF2488:0xF248C]))[0])} -> target: {hex(0xF2480 + 8 + 5 + struct.unpack("<i", bytes(data[0xF2488:0xF248C]))[0])} (oczekiwane 0x46BE1B)')

# Sprawdź target CALL
call_rel = struct.unpack('<i', bytes(data[0xF2483:0xF2487]))[0]
call_target = 0xF2480 + 2 + 5 + call_rel
print(f'CALL target: {hex(call_target)} (oczekiwane 0x46D53A)')