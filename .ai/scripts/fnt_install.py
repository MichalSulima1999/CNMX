# -*- coding: utf-8 -*-
"""Etap 3A: podmiana Data\\gui\\fonts\\font08/10/12.fnt wersjami 2x (backup .orig)."""
import sys, os, shutil, struct
sys.path.insert(0, r"C:\Users\Michael1099\AppData\Local\Temp\opencode")
from fnt_scale import decode, scale_encode

SRC = r"G:\Games\CnMod 1.2\Data\gui\fonts"
for n in ("font08", "font10", "font12"):
    path = os.path.join(SRC, n + ".fnt")
    orig = open(path, "rb").read()
    # jesli juz zainstalowana skala (height>oryginal) - nie podwojnie skaluj!
    f, glyphs = decode(orig)
    if f["height"] > 12:
        print("%s: juz skalowany (height=%d) - pomijam" % (n, f["height"]))
        continue
    scaled, meta = scale_encode(glyphs, 2, f["height"], f["fieldA"])
    bak = path + ".orig"
    if not os.path.exists(bak):
        shutil.copy2(path, bak)
        print("%s: backup -> %s.orig" % (n, n))
    open(path, "wb").write(scaled)
    # weryfikacja z dysku
    chk = open(path, "rb").read()
    assert chk == scaled, "zapis niezgodny!"
    f2, g2 = decode(chk)
    assert f2["height"] == f["height"] * 2 and f2["blk"][3] == meta["rows"]
    print("%s: OK  height %d -> %d, %d -> %d B, rows=%d, empty=%d" % (
        n, f["height"], f2["height"], len(orig), len(chk),
        f2["blk"][3], f2["blk"][5]))
print("\nZAINSTALOWANO. Do przywrocenia: usunac zmieniony plik i zmienic nazwe .orig")
