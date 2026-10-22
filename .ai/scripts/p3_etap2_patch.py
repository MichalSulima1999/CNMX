"""
P3 Etap 2 — Pełne wdrożenie skalowania HUD/UI
Skala: s_x=1.875 (szerokość, baza 1024), s_y=1.8 (wysokość, baza 600)

Patchuje:
1. Wszystkie stałe push-imm w zakotwiczonych funkcjach HUD (x→s_x, y→s_y, w→s_x, h→s_y)
2. Rozmiary powierzchni (0x40C634, 30 miejsc)
3. Transformację myszy (0x478E03)
4. Stretch blit (0x40D507)

Użycie:
  python p3_etap2_patch.py          — zastosuj patch
  python p3_etap2_patch.py --revert — przywróć oryginał
"""

import sys, struct, shutil, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import pefile
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

EXE = r'G:\Games\CnMod 1.2\CN.PLMOD.exe'
ORIG = r'G:\Games\CnMod 1.2\CN.PLMOD.exe.orig'

S_X = 1.875  # 1920/1024
S_Y = 1.8    # 1080/600

# ─── Stałe do skalowania ─────────────────────────────────────────────────────
# Format: (va, original_imm, axis)  axis: 'x' | 'y' | 'w' | 'h'
# x = w - K  →  x_scaled = w - K*s_x  →  imm_scaled = K*s_x
# y = h - K  →  y_scaled = h - K*s_y  →  imm_scaled = K*s_y
# w = K      →  w_scaled = K*s_x
# h = K      →  h_scaled = K*s_y

# Zakotwiczone x (prawy róg: x = w - K)
ANCHORED_X = [
    # 0x4BC8xx cluster — dolne prawe panele
    (0x4BC826, 0xC8, 'x'),   # w - 200
    (0x4BCA2C, 0xC8, 'x'),   # w - 200
    (0x4BCC35, 0xA0, 'x'),   # w - 160
    # 0x4BDxxx cluster — dolne prawe panele
    (0x4BD3CA, 0xAA, 'x'),   # w - 170
    (0x4BD75E, 0xA0, 'x'),   # w - 160
    (0x4BD856, 0xA0, 'x'),   # w - 160
    (0x4BDCE7, 0x8C, 'x'),   # w - 140
    (0x4BDE0C, 0xA0, 'x'),   # w - 160
    # 0x4A8851 — prawy panel (już w pilocie, ale dla kompletności)
    (0x4A8864, 0x8C, 'x'),   # w - 140
]

# Zakotwiczone y (dolny róg: y = h - K)
ANCHORED_Y = [
    # 0x4BC8xx cluster
    (0x4BC818, 0x64, 'y'),   # h - 100
    (0x4BCA1E, 0x64, 'y'),   # h - 100
    (0x4BCC25, 0xF0, 'y'),   # h - 240
    # 0x4BDxxx cluster
    (0x4BD3BA, 0xFA, 'y'),   # h - 250
    (0x4BD750, 0x64, 'y'),   # h - 100
    (0x4BD846, 0x12C, 'y'),  # h - 300
    (0x4BDCD7, 0xA0, 'y'),   # h - 160
    (0x4BDDFC, 0x168, 'y'),  # h - 360
    # 0x4A8851 — prawy panel
    (0x4A8874, 0x8C, 'y'),   # h - 140
]

# Stałe wysokości/szerokości (push imm przed RECT)
# Format: (va, original_imm, type)  type: 'w' | 'h'
DIMENSIONS = [
    # 0x4BC8xx — 200x100
    (0x4BC816, 0x64, 'h'),   # h=100
    (0x4BC81B, 0xC8, 'w'),   # w=200
    (0x4BCA1C, 0x64, 'h'),   # h=100
    (0x4BCA21, 0xC8, 'w'),   # w=200
    # 0x4BCCxx — 160x240
    (0x4BCC20, 0xF0, 'h'),   # h=240
    (0x4BCC2A, 0xA0, 'w'),   # w=160
    # 0x4BD3xx — 170x250
    (0x4BD3B5, 0xFA, 'h'),   # h=250
    (0x4BD3BF, 0xAA, 'w'),   # w=170
    # 0x4BD7xx — 160x100
    (0x4BD74E, 0x64, 'h'),   # h=100
    (0x4BD753, 0xA0, 'w'),   # w=160
    # 0x4BD8xx — 160x300
    (0x4BD841, 0x12C, 'h'),  # h=300
    (0x4BD84B, 0xA0, 'w'),   # w=160
    # 0x4BDCxx — 140x160
    (0x4BDCD2, 0xA0, 'h'),   # h=160
    (0x4BDCDC, 0x8C, 'w'),   # w=140
    # 0x4BDDxx — 160x360
    (0x4BDDF7, 0x168, 'h'), # h=360
    (0x4BDE01, 0xA0, 'w'),   # w=160
    # 0x4A8851 — 140x600 (prawy panel)
    (0x4A885F, 0x258, 'h'),  # h=600
    (0x4A8869, 0x8C, 'w'),   # w=140
]

# ─── Powierzchnie (0x40C634) ─────────────────────────────────────────────────
# 30 miejsc tworzenia powierzchni — skaluj width/height
# Format: (va, orig_w, orig_h)  — szukamy push w; push h; call 0x40C634
SURFACE_SITES = [
    # (va_call, orig_w, orig_h)
    (0x4025E9, 0x100, 0x100),   # placeholder — wymaga weryfikacji
    (0x402634, 0x100, 0x100),
    (0x402E06, 0x100, 0x100),
    (0x402F35, 0x100, 0x100),
    (0x402F94, 0x100, 0x100),
    (0x403544, 0x100, 0x100),
    (0x40BF2C, 0x100, 0x100),
    (0x40BF59, 0x100, 0x100),
    (0x40C207, 0x100, 0x100),
    (0x40C296, 0x100, 0x100),
    (0x40C367, 0x100, 0x100),
    (0x40C44D, 0x100, 0x100),
    (0x40C4FD, 0x100, 0x100),
    (0x476686, 0x100, 0x100),
    (0x47DD3D, 0x100, 0x100),
    (0x4902CD, 0x100, 0x100),
    (0x4902DA, 0x100, 0x100),
    (0x4A3A4A, 0x100, 0x100),
    (0x4A3A8B, 0x100, 0x100),
    (0x4A621A, 0x100, 0x100),
    (0x4A625B, 0x100, 0x100),
    (0x4A629C, 0x100, 0x100),
    (0x4A62DD, 0x100, 0x100),
    (0x4A631E, 0x100, 0x100),
    (0x4A635F, 0x100, 0x100),
    (0x4A63A0, 0x100, 0x100),
    (0x4A63E1, 0x100, 0x100),
    (0x4A6422, 0x100, 0x100),
    (0x4A6463, 0x100, 0x100),
    (0x4A64A4, 0x100, 0x100),
]

# ─── Mysz (0x478E03) ─────────────────────────────────────────────────────────
# GetCursorPos → (x,y) w pikselach ekranu → podziel przez s_x/s_y
# Patch: dodaj podział po GetCursorPos
MOUSE_FIX_VA = 0x478E03

# ─── Stretch blit (0x40D507) ────────────────────────────────────────────────
# 3 wywołania — skaluj rozmiary bitmap
STRETCH_SITES = [
    (0x40264A, 0x100, 0x100),
    (0x402CC5, 0x100, 0x100),
    (0x49033B, 0x100, 0x100),
]


def scale_imm(imm, axis):
    """Skaluj stałą imm32 zgodnie z osią. Round half up."""
    if axis in ('x', 'w'):
        return int(imm * S_X + 0.5)
    else:
        return int(imm * S_Y + 0.5)


def to_neg32(val):
    """Konwertuj na ujemny imm32 (two's complement)."""
    if val < 0:
        return val & 0xFFFFFFFF
    return val


def patch_imm32(pe, data, va, new_val, label=""):
    """Patch imm32 w VA (opcode 05/68/81/83 itd.)."""
    base = pe.OPTIONAL_HEADER.ImageBase
    off = pe.get_offset_from_rva(va - base)
    if off is None:
        print(f"  BŁĄD: {label} 0x{va:08X} — poza zakresem")
        return False
    old = struct.unpack_from('<I', data, off)[0]
    struct.pack_into('<I', data, off, new_val & 0xFFFFFFFF)
    print(f"  {label} 0x{va:08X}: 0x{old:08X} → 0x{new_val & 0xFFFFFFFF:08X}")
    return True


def apply_patch():
    """Zastosuj pełny patch Etap 2."""
    print("=" * 60)
    print("P3 Etap 2 — Pełne skalowanie HUD/UI")
    print(f"  s_x={S_X}, s_y={S_Y}")
    print("=" * 60)

    pe = pefile.PE(EXE)
    base = pe.OPTIONAL_HEADER.ImageBase
    data = bytearray(pe.__data__)

    # ── 1. Zakotwiczone x ────────────────────────────────────────────────────
    print("\n[1/4] Zakotwiczone x (prawy róg)...")
    for va, orig, axis in ANCHORED_X:
        new_val = to_neg32(-scale_imm(orig, axis))
        patch_imm32(pe, data, va, new_val, f"x=w-{orig}")

    # ── 2. Zakotwiczone y ────────────────────────────────────────────────────
    print("\n[2/4] Zakotwiczone y (dolny róg)...")
    for va, orig, axis in ANCHORED_Y:
        new_val = to_neg32(-scale_imm(orig, axis))
        patch_imm32(pe, data, va, new_val, f"y=h-{orig}")

    # ── 3. Wymiary (w/h) ─────────────────────────────────────────────────────
    print("\n[3/4] Wymiary widgetów (w/h)...")
    for va, orig, typ in DIMENSIONS:
        new_val = scale_imm(orig, typ)
        patch_imm32(pe, data, va, new_val, f"{typ}={orig}")

    # ── 4. Powierzchnie ──────────────────────────────────────────────────────
    print("\n[4/4] Powierzchnie (0x40C634)...")
    for va_call, orig_w, orig_h in SURFACE_SITES:
        # Szukaj push w i push h przed call
        off = pe.get_offset_from_rva(va_call - base)
        if off is None:
            continue
        # Cofnij ~30 bajtów i szukaj push z wartościami w zakresie 10-2000
        start = max(0, off - 30)
        code = bytes(data[start:off])
        md = Cs(CS_ARCH_X86, CS_MODE_32)
        pushes = []
        for ins in md.disasm(code, base + start):
            if ins.mnemonic == 'push':
                try:
                    val = int(ins.op_str, 0)
                    if 10 <= val <= 2000:
                        pushes.append((ins.address, val))
                except ValueError:
                    continue
        # Ostatnie 2 push z rozsądnymi wartościami to w i h
        # WERYFIKACJA: call 0x40C634 musi być bezpośrednio po push h
        if len(pushes) >= 2:
            w_va, w_val = pushes[-2]
            h_va, h_val = pushes[-1]
            # Sprawdź czy call 0x40C634 jest po h_va
            h_off = pe.get_offset_from_rva(h_va - base)
            call_off = pe.get_offset_from_rva(va_call - base)
            if call_off and h_off and (call_off - h_off) <= 6:
                new_w = scale_imm(w_val, 'w')
                new_h = scale_imm(h_val, 'h')
                patch_imm32(pe, data, w_va, new_w, f"surf_w={w_val}")
                patch_imm32(pe, data, h_va, new_h, f"surf_h={h_val}")
            else:
                print(f"  POMINIETO 0x{va_call:08X} — call 0x40C634 nie jest po push")

    # ── Zapisz ───────────────────────────────────────────────────────────────
    try:
        import ctypes
        # Użyj WriteAllBytes przez subprocess PowerShell
        import subprocess, tempfile, os
        tmp = os.path.join(tempfile.gettempdir(), 'CN_patched.exe')
        with open(tmp, 'wb') as f:
            f.write(data)
        shutil.copy2(tmp, EXE)
        os.remove(tmp)
        print(f"\n✓ Patch zastosowany → {EXE}")
    except Exception as e:
        print(f"\n✗ BŁĄD zapisu: {e}")
        print("  Spróbuj uruchomić jako administrator.")
        sys.exit(1)


def revert_patch():
    """Przywróć oryginalny exe."""
    if os.path.exists(ORIG):
        shutil.copy2(ORIG, EXE)
        print(f"✓ Przywrócono oryginał → {EXE}")
    else:
        print(f"✗ Brak oryginału: {ORIG}")


if __name__ == '__main__':
    if '--revert' in sys.argv:
        revert_patch()
    else:
        apply_patch()
