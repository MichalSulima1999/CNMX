# -*- coding: utf-8 -*-
"""Plan 1, Faza A: tla 16:9 (crop 16:10 -> 16:9 + Lanczos do 1920x1080).
Zawsze z backupem .orig. Zadne oryginalne pliki nie sa nadpisywane bez kopii."""
import shutil, os, sys
from PIL import Image

JOBS = [
    # (sciezka zrodlowa, czy robic backup .orig)
    (r"G:\Games\CnMod 1.2\CN.PLMOD\pictures\bitmaps\titlescreen.bmp", True),
    (r"G:\Games\CnMod 1.2\CN.PLMOD\pictures\bitmaps\loadscreen.bmp", True),
    (r"G:\Games\CnMod 1.2\DataX\Pictures\post00.bmp", True),
]

TARGET_W, TARGET_H = 1920, 1080
DRY = "--apply" not in sys.argv

def crop_to_aspect(im, aspect):
    w, h = im.size
    cur = w / h
    if abs(cur - aspect) < 1e-6:
        return im, 0, 0
    if cur > aspect:  # za szerokie -> obcinaj boki
        nw = int(round(h * aspect))
        x = (w - nw) // 2
        return im.crop((x, 0, x + nw, h)), x, 0
    # za wysokie -> obcinaj gore/dol (centrum)
    nh = int(round(w / aspect))
    y = (h - nh) // 2
    return im.crop((0, y, w, y + nh)), 0, y

print("TRYB:", "DRY-RUN (bez zapisu)" if DRY else "APPLY (zapis do gry)")
for src, backup in JOBS:
    if not os.path.exists(src):
        print("  BRAK:", src)
        continue
    im = Image.open(src)
    w0, h0 = im.size
    mode0, fmt0 = im.mode, im.format
    cropped, ox, oy = crop_to_aspect(im, TARGET_W / TARGET_H)
    if not DRY:
        if backup:
            orig = src + ".orig"
            if not os.path.exists(orig):
                shutil.copy2(src, orig)
                print("  backup ->", os.path.basename(orig))
        out = cropped.resize((TARGET_W, TARGET_H), Image.LANCZOS)
        # BMP 24bpp (jak oryginal)
        if out.mode != "RGB":
            out = out.convert("RGB")
        out.save(src, "BMP")
    cw, ch = cropped.size
    print("  %-70s %sx%s %s -> crop(%d,%d)=%dx%s -> %s" % (
        os.path.relpath(src, r"G:\Games\CnMod 1.2"),
        w0, h0, mode0, ox, oy, cw, ch,
        "DRY" if DRY else "%dx%d 24bpp" % (TARGET_W, TARGET_H)))
print("OK")
