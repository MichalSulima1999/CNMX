# -*- coding: utf-8 -*-
"""Analiza importow CN.PLMOD.exe — naddirectdraw / timing / grafika."""
import sys, struct
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pefile

PE = r"G:\Games\CnMod 1.2\CN.PLMOD.exe"
pe = pefile.PE(PE)
print("=== IMPORTY (grupowane po DLL) ===")
total = 0
for e in pe.DIRECTORY_ENTRY_IMPORT:
    names = []
    for i in e.imports:
        if i.name:
            names.append(i.name.decode())
        else:
            names.append("ord#%d" % (i.ordinal or 0))
    total += len(names)
    dll = e.dll.decode()
    print("%-22s (%d): %s" % (dll, len(names), ", ".join(sorted(set(names)))))
print("lacznie: %d" % total)

# szukaj ciekawych tekstow w sekcji .rdata/.data (wskazowki na timing/vsync)
print("\n=== CIEKAWE CIAGI ===")
needles = [b"ddraw", b"DDraw", b"DirectDraw", b"vsync", b"VSync", b"timeGetTime",
           b"QueryPerformance", b"Sleep", b"GetTickCount", b"fps", b"FPS",
           b"DDLOCK", b"Flip", b"WaitForVerticalBlank", b"winmm"]
data = pe.__data__
for n in needles:
    idx = []
    start = 0
    while True:
        p = data.find(n, start)
        if p < 0: break
        idx.append(p)
        start = p + 1
        if len(idx) > 6: break
    if idx:
        print("%-24s -> %s" % (n.decode(errors="replace"), ["0x%x" % x for x in idx]))
