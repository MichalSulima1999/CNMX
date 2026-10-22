"""Test skryptu Etap 2 — weryfika składni i logiki skalowania."""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Importuj funkcje z głównego skryptu
exec(open(r'G:\Games\CnMod 1.2\.ai\scripts\p3_etap2_patch.py', encoding='utf-8').read().split("if __name__")[0])

print('Składnia OK')
print(f'ANCHORED_X: {len(ANCHORED_X)} miejsc')
print(f'ANCHORED_Y: {len(ANCHORED_Y)} miejsc')
print(f'DIMENSIONS: {len(DIMENSIONS)} miejsc')
print(f'SURFACE_SITES: {len(SURFACE_SITES)} miejsc')

print('\nTest skalowania:')
tests = [
    (200, 'x', 375),   # 200 * 1.875 = 375
    (100, 'y', 180),   # 100 * 1.8 = 180
    (140, 'w', 263),   # 140 * 1.875 = 262.5 → 263
    (600, 'h', 1080),  # 600 * 1.8 = 1080
    (160, 'x', 300),   # 160 * 1.875 = 300
    (240, 'y', 432),   # 240 * 1.8 = 432
    (170, 'w', 319),   # 170 * 1.875 = 318.75 → 319
    (250, 'h', 450),   # 250 * 1.8 = 450
    (300, 'y', 540),   # 300 * 1.8 = 540
    (360, 'y', 648),   # 360 * 1.8 = 648
]
all_ok = True
for val, axis, expected in tests:
    result = scale_imm(val, axis)
    ok = result == expected
    all_ok = all_ok and ok
    status = 'OK' if ok else 'BLAD'
    print(f'  {axis}: {val} -> {result} (oczekiwane: {expected}) [{status}]')

print(f'\nRezultat: {"WSZYSTKIE TESTY OK" if all_ok else "SA BLEDY"}')
