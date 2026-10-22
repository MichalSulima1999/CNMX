# -*- coding: utf-8 -*-
"""p3_pilot_patch.py — Etap 1 Planu 3 PATCH PILOTOWY (2 miejsca layoutu).
Skala per-osiowa: s_x=1.875 (baza 1024), s_y=1.8 (baza 600).
Modyfikuje imm32 w: add eax,<neg> (pozycje) i push <size> (rozmiary).
Przed zastosowaniem tworzy backup CN.PLMOD.exe.orig (jednorazowo).
Weryfikuje bajty przed i po; raport w konsoli."""
import sys, shutil, struct, os
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pefile

PE = r"G:\Games\CnMod 1.2\CN.PLMOD.exe"
ORIG = r"G:\Games\CnMod 1.2\CN.PLMOD.exe.orig"

# (va, rodzaj, opis, stary_imm, nowy_imm)
PATCHES = [
    # --- dialog centrowany 0x4a39a0 ---
    (0x4a39ab, "add",  "y -> GUIH-420*1.8=GUIH-756",  0xfffffe5c, 0xfffffd0c),
    (0x4a39b8, "push", "h: 420 -> 756",               0x1a4,      0x2f4),
    (0x4a39bd, "push", "w: 500 -> 938",               0x1f4,      0x3aa),
    (0x4a39c8, "add",  "x -> GUIW-500*1.875=GUIW-938", 0xfffffe0c, 0xfffffc56),
    # --- prawy panel boczny 0x4a8851 ---
    (0x4a885f, "push", "h: 600 -> 1080",              0x258,      0x438),
    (0x4a8864, "add",  "y -> GUIH-600*1.8=GUIH-1080", 0xfffffda8, 0xfffffbc8),
    (0x4a8869, "push", "w: 140 -> 263",               0x8c,       0x107),
    (0x4a8874, "add",  "x -> GUIW-140*1.875=GUIW-263",0xffffff74, 0xfffffef9),
]

pe = pefile.PE(PE)
base = pe.OPTIONAL_HEADER.ImageBase

def off(va):
    o = pe.get_offset_from_rva(va - base)
    assert o is not None, "brak mapowania 0x%08x" % va
    return o

def rdimm(va):
    o = off(va) + 1  # imm32 zaczyna sie po opcode (05/68)
    return struct.unpack_from("<I", pe.__data__, o)[0]

# 1) backup
if not os.path.exists(ORIG):
    shutil.copy2(PE, ORIG)
    print("Backup: %s" % ORIG)
else:
    print("Backup juz istnieje (pomijam): %s" % ORIG)

# 2) weryfikacja stanu przed
print("\n=== WERYFIKACJA PRZED ===")
ok = True
for va, kind, desc, old, new in PATCHES:
    cur = rdimm(va)
    status = "OK" if cur == old else "NIEZGODNE!"
    if cur != old:
        ok = False
    print("  0x%08x %-4s %-32s stary=0x%08x faktyczny=0x%08x %s" % (va, kind, desc, old, cur, status))

if not ok:
    sys.exit("ABORT — oczekiwane bajty nie zgadzaja sie (exe moze byc juz zmodyfikowany)")

# 3) patch
with open(PE, "r+b") as f:
    data = bytearray(f.read())
    for va, kind, desc, old, new in PATCHES:
        o = off(va) + 1
        data[o:o + 4] = struct.pack("<I", new)
    f.seek(0)
    f.write(bytes(data))
    f.truncate()

# 4) weryfikacja po
print("\n=== WERYFIKACJA PO ===")
pe2 = pefile.PE(PE)
for va, kind, desc, old, new in PATCHES:
    o = pe2.get_offset_from_rva(va - base) + 1
    cur = struct.unpack_from("<I", pe2.__data__, o)[0]
    print("  0x%08x %-4s %-32s nowy=0x%08x faktyczny=0x%08x %s" % (
        va, kind, desc, new, cur, "OK" if cur == new else "BLAD!"))

print("\nPATCH PILOTOWY ZASTOSOWANY (8 imm32, 2 miejsca layoutu).")
print("Revert: skopiuj CN.PLMOD.exe.orig -> CN.PLMOD.exe")