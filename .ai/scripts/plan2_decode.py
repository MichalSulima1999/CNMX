# -*- coding: utf-8 -*-
"""Dekoder FNT: rekordy -> bitmapi, walidacja round-trip (dekoder+enkoder == oryginal bajt w bajt),
statystyki + contact sheet PNG + ASCII art wybranych znakow."""
import struct, os
from PIL import Image

def parse(path):
    d = open(path, "rb").read()
    p = [0]
    def u32():
        v = struct.unpack_from("<I", d, p[0])[0]; p[0] += 4; return v
    t1, v1 = u32(), u32()
    fieldA, height = u32(), u32()
    t2, v2 = u32(), u32()
    blk = struct.unpack_from("<7I", d, p[0]); p[0] += 28
    arrs = []
    if blk[1] != 0:
        for i in range(3):
            at, aux, ln = u32(), u32(), u32()
            arrs.append(d[p[0]:p[0]+ln]); p[0] += ln
    assert p[0] == len(d), "nie zjedzono calego pliku!"
    return dict(d=d, type1=t1, type2=t2, fieldA=fieldA, height=height, blk=blk,
                records=arrs[0], gdata=arrs[1], rowtab=arrs[2])

def decode(f):
    """Zwraca: glyphs[gi] = dict(enc,left,top,w,h,rb, rows=[[(v,col)...] per col], runs=per-row runs)"""
    cnt = f["blk"][1]
    n = cnt * 24
    gdata = f["gdata"]
    rowtab = [struct.unpack_from("<I", f["rowtab"], i*4)[0] for i in range(len(f["rowtab"])//4)]
    glyphs = []
    for gi in range(cnt):
        enc, left, top, w, h, rb = struct.unpack_from("<6I", f["records"], gi*24)
        g = dict(gi=gi, enc=enc, left=left, top=top, w=w, h=h, rb=rb,
                 rows=[[0]*w for _ in range(h)], runs=[None]*h, rowd=None)
        if enc != 0:
            assert enc in (1, 4), "nieznany enc %d @ %d" % (enc, gi)
            assert rb + h <= len(rowtab), "rowBase+h poza tablica @ %d" % gi
            bpp = 1 if enc == 1 else 2
            g["rowd"] = []
            for r in range(h):
                e = rowtab[rb + r]
                if e == 0xFFFFFFFF:
                    g["runs"][r] = []
                    g["rowd"].append(e)
                    continue
                startCol = e >> 22
                off = e & 0x3FFFFF
                g["rowd"].append(e)
                p = off
                col = startCol
                runs = []
                while True:
                    b = gdata[p]; p += 1
                    if b == 0:
                        break
                    ln = b & 0x7F
                    if b & 0x80:
                        assert ln > 0, "skip len 0 @ gi=%d row=%d" % (gi, r)
                        runs.append(("S", ln, b""))
                        col += ln
                    else:
                        raw = gdata[p:p+ln*bpp]; p += ln*bpp
                        runs.append(("L", ln, raw))
                        for k in range(ln):
                            if col + k >= w:
                                raise AssertionError("run poza szerokoscia gi=%d row=%d" % (gi, r))
                            if bpp == 1:
                                g["rows"][r][col+k] = raw[k]
                            else:
                                g["rows"][r][col+k] = struct.unpack_from("<H", raw, k*2)[0]
                        col += ln
                g["runs"][r] = runs
        glyphs.append(g)
    return glyphs

def encode(f, glyphs):
    """Re-encode arr1 + rowtab dokladnie wg oryginalnej struktury runow -> porownanie bajt-w-bajt."""
    gdata = bytearray()
    rowtab = bytearray()
    errs = 0
    for g in glyphs:
        if g["enc"] == 0:
            continue
        for r in range(g["h"]):
            e = g["rowd"][r]
            if e == 0xFFFFFFFF:
                rowtab += struct.pack("<I", 0xFFFFFFFF)
                continue
            startCol = e >> 22
            off = len(gdata)
            assert off <= 0x3FFFFF
            rowtab += struct.pack("<I", (startCol << 22) | off)
            for kind, ln, raw in g["runs"][r]:
                if kind == "S":
                    gdata += bytes([0x80 | ln])
                else:
                    gdata += bytes([ln]) + raw
            gdata += b"\x00"
    return bytes(gdata), bytes(rowtab)

def stats(name, f, glyphs):
    cnt = f["blk"][1]
    present = [g for g in glyphs if g["enc"] != 0]
    zeros_in_lit = sum(1 for g in present for row in g["runs"] if row
                       for kind, ln, raw in row if kind == "L" for b in raw if b == 0)
    vals = set()
    for g in present:
        for row in g["rows"]:
            vals.update(row)
    print("--- %s ---" % name)
    print("  count=%d fieldA=%d height=%d blk=%s" % (cnt, f["fieldA"], f["height"], f["blk"]))
    print("  present=%d missing=%d enc types=%s" % (len(present), cnt-len(present),
          sorted(set(g["enc"] for g in present))))
    print("  w: min=%d max=%d   h: min=%d max=%d" % (
        min(g["w"] for g in present), max(g["w"] for g in present),
        min(g["h"] for g in present), max(g["h"] for g in present)))
    print("  left: min=%d max=%d   top: min=%d max=%d" % (
        min(g["left"] for g in present), max(g["left"] for g in present),
        min(g["top"] for g in present), max(g["top"] for g in present)))
    print("  rowtab entries=%d  max(rb+h)=%d  zeros inside literal runs=%d" % (
        len(f["rowtab"])//4, max(g["rb"]+g["h"] for g in present), zeros_in_lit))
    print("  wartosci pikseli: min=%d max=%d distinct=%d" % (
        min(vals), max(vals), len(vals)))
    # ciaglosc rowBase
    seq = all(present[i]["rb"] + present[i]["h"] == present[i+1]["rb"]
              for i in range(len(present)-1))
    print("  rowBase ciagly (suma h po kolei): %s ; rb[0]=%d" % (seq, present[0]["rb"]))
    # korelacje pola bloku
    print("  sum(h)=%d  blk[3]=%d  liczba wierszy z danymi=%d  liczba runow literalnych=%d" % (
        sum(g["h"] for g in present), f["blk"][3],
        sum(1 for g in present for row in g["runs"] if row),
        sum(1 for g in present for row in g["runs"] if row
            for kind, ln, raw in row if kind == "L")))
    return present

def ascii_art(g, label):
    print("  [%s] enc=%d %dx%d left=%d top=%d rb=%d" % (label, g["enc"], g["w"], g["h"],
                                                        g["left"], g["top"], g["rb"]))
    for row in g["rows"]:
        print("    " + "".join("#" if v else "." for v in row))

def sheet(name, glyphs, path, scale=4):
    present = [g for g in glyphs if g["enc"] != 0]
    maxw = max(g["w"] for g in present) + 2
    maxh = max(g["h"] for g in present) + 2
    cols = 16
    rowsn = (len(glyphs) + cols - 1) // cols
    img = Image.new("RGB", (cols*maxw*scale, rowsn*maxh*scale), (10, 25, 60))
    px = img.load()
    for idx, g in enumerate(glyphs):
        cx = (idx % cols) * maxw * scale
        cy = (idx // cols) * maxh * scale
        if g["enc"] == 0:
            continue
        vals = [v for row in g["rows"] for v in row if v]
        if not vals:
            continue
        mx = max(1, max(vals))
        for y, row in enumerate(g["rows"]):
            for x, v in enumerate(row):
                if v == 0:
                    continue
                b = int(255 * v / mx)
                for sy in range(scale):
                    for sx in range(scale):
                        px[cx + (x+1)*scale + sx, cy + (y+1)*scale + sy] = (b, b, b)
    img.save(path)
    print("  zapisano %s (%dx%d px)" % (path, img.width, img.height))

files = [
    ("font08", r"G:\Games\CnMod 1.2\Data\gui\fonts\font08.fnt"),
    ("font10", r"G:\Games\CnMod 1.2\Data\gui\fonts\font10.fnt"),
    ("font12", r"G:\Games\CnMod 1.2\Data\gui\fonts\font12.fnt"),
    ("fontdebug", r"G:\Games\CnMod 1.2\Data\gui\fonts\fontdebug.fnt"),
]
TMP = r"C:\Users\Michael1099\AppData\Local\Temp\opencode"
for name, path in files:
    f = parse(path)
    glyphs = decode(f)
    present = stats(name, f, glyphs)
    # round-trip
    gdata2, rowtab2 = encode(f, glyphs)
    print("  ROUND-TRIP: arr1 %s | rowtab %s" % (
        "OK" if gdata2 == f["gdata"] else "ROZNICA (%d vs %d)" % (len(gdata2), len(f["gdata"])),
        "OK" if rowtab2 == f["rowtab"] else "ROZNICA"))
    print()
    if name == "font12":
        ascii_art(glyphs[0x41], "A (0x41)")
        ascii_art(glyphs[0xE1], "a-ogonek (0xE1 cp1250)")
        ascii_art(glyphs[0x20], "spacja (0x20)")
        sheet(name, glyphs, os.path.join(TMP, "fnt12_sheet.png"))
    if name == "font08":
        sheet(name, glyphs, os.path.join(TMP, "fnt08_sheet.png"))
