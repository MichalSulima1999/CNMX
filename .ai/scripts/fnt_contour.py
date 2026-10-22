# -*- coding: utf-8 -*-
"""fnt_contour.py — wariant KONTUROWY skali x1.25 dla fontow UI (font08/font12).

Zamiast nearest-neighbour (nierowne bloki 1-2 px) algorytm:
  1. sledzi kontur glifu metoda marching squares na WARTOSCIACH AA (nie binarnie) —
     izolinia 127.5 = geometria krawedzi 50% pokrycia (linia w polowie piksela),
  2. skaluje wspolrzedne konturu x1.25 (dokladnie, ulamkowo),
  3. rasteryzuje z supersamplingiem 16x + box-downsample => pelny antyaliasing,
  4. progiem INK_MIN usuwa slabe resztki (jak w fnt_ttf.py).

Wymiary glifow (left/top/w/h po skalowaniu) identyczne jak nearest x1.25,
czyli advance i layout = zatwierdzony podglad prev_px125_*.height = round(height*k).

Uzycie (python 3.11):
    python fnt_contour.py          # DOMYSLNIE: tylko podglady + walidacja (bez zapisu Data)
    python fnt_contour.py --install  # nadpisuje font08.fnt / font12.fnt
                                     # (oryginaly: *.fnt.orig; wersje Tahoma odtwarzalne: fnt_ttf.py)
Podglady: TMP\\prev_contour_fontNN.png (1:1), _z2 (zoom2),
          TMP\\cmp125_fontNN_z4.png (nearest vs kontur, zoom4).
"""
import os, sys
from PIL import Image, ImageChops, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fnt_scale as F

SRC = r"G:\Games\CnMod 1.2\Data\gui\fonts"
TMP = r"C:\Users\Michael1099\AppData\Local\Temp\opencode"
WINDIR = r"C:\Windows\Fonts"
K = 1.25          # skala (jak zatwierdzony wariant x1.25)
S = 16            # supersampling
INK_MIN = 40      # prog przezroczystosci (spójny z fnt_ttf.py)
ISO = 127.5       # izolinia = 50% pokrycia tuszu
TEXT = ("Zażółć gęślą jaźń ĄĆĘŁŃÓŚŹŻ\n"
        "Buduj targowisko i zwiadowcy!\n"
        "0123456789 ?! -=%()\n"
        "\n"
        "Buduj dom | Zwiadowca 28/30 HP\n"
        "Koszty: 120 drewna, 45 zelaza\n"
        "Zapisz gre  Wczytaj  Wyjscie")

# tablica przypadkow marching squares: n = a<<3|b<<2|c<<1|d (a=TL, b=TR, c=BR, d=BL)
# -> pary krawedzi przejscia (T gore, R prawo, B dol, L lewo)
CASES = {
    1: [("L", "B")], 2: [("B", "R")], 3: [("L", "R")],
    4: [("T", "R")], 6: [("T", "B")], 7: [("T", "L")],
    8: [("T", "L")], 9: [("T", "B")], 11: [("T", "R")],
    12: [("L", "R")], 13: [("B", "R")], 14: [("L", "B")],
    # 5 i 10 (rozwiazanie niejednoznaczne) — rozwiazywane srednia srodkowa
}


def signed(x):
    return x - 0x100000000 if x >= 0x80000000 else x


def _flat(im):
    try:
        return list(im.get_flattened_data())
    except AttributeError:
        return list(im.getdata())


def _v(mat, w, h, x, y):
    if 0 <= x < w and 0 <= y < h:
        return mat[y][x]
    return 0


def iso_loops(mat):
    """Kontury izolinii 127.5 na interpolowanych wartosciach AA. Zwraca petle
    [(x, y), ...] w wspolrzednych bitmapy glifu (0..w, 0..h; piksel = [x,x+1])."""
    w = len(mat[0]) if mat else 0
    h = len(mat)
    segs = []
    for py in range(-1, h):
        for px in range(-1, w):
            v0 = _v(mat, w, h, px, py)
            v1 = _v(mat, w, h, px + 1, py)
            v2 = _v(mat, w, h, px + 1, py + 1)
            v3 = _v(mat, w, h, px, py + 1)
            b0, b1, b2, b3 = v0 >= ISO, v1 >= ISO, v2 >= ISO, v3 >= ISO
            n = (b0 << 3) | (b1 << 2) | (b2 << 1) | b3
            if n in (0, 15):
                continue

            def pt(e):
                if e == "T":
                    t = (ISO - v0) / (v1 - v0)
                    return (px + 0.5 + t, py + 0.5)
                if e == "R":
                    t = (ISO - v1) / (v2 - v1)
                    return (px + 1.5, py + 0.5 + t)
                if e == "B":
                    t = (ISO - v3) / (v2 - v3)
                    return (px + 0.5 + t, py + 1.5)
                t = (ISO - v0) / (v3 - v0)          # "L"
                return (px + 0.5, py + 0.5 + t)

            if n in (5, 10):
                ctr = (v0 + v1 + v2 + v3) / 4.0
                if n == 5:      # b,d = 1
                    pairs = [("T", "L"), ("B", "R")] if ctr >= ISO else [("T", "R"), ("L", "B")]
                else:           # a,c = 1
                    pairs = [("T", "R"), ("L", "B")] if ctr >= ISO else [("T", "L"), ("B", "R")]
            else:
                pairs = CASES[n]
            for e1, e2 in pairs:
                p1 = (round(pt(e1)[0], 6), round(pt(e1)[1], 6))
                p2 = (round(pt(e2)[0], 6), round(pt(e2)[1], 6))
                if p1 != p2:
                    segs.append((p1, p2))
    if not segs:
        return []

    # laczenie segmentow w petle (stopien wezla <= 2)
    adj = {}
    for i, (a, b) in enumerate(segs):
        adj.setdefault(a, []).append((b, i))
        adj.setdefault(b, []).append((a, i))
    used = [False] * len(segs)
    loops = []
    for i0 in range(len(segs)):
        if used[i0]:
            continue
        used[i0] = True
        a0, b0 = segs[i0]
        loop = [a0, b0]
        cur = b0
        while True:
            nxt = None
            for (other, si) in adj.get(cur, []):
                if not used[si]:
                    nxt = (other, si)
                    break
            if nxt is None:
                break
            used[nxt[1]] = True
            if nxt[0] == a0:
                break
            loop.append(nxt[0])
            cur = nxt[0]
        if len(loop) >= 3:
            loops.append(loop)
    return loops


def rasterize_glyph(mat, w2, h2):
    """Rasteryzuj kontury do macierzy w2 x h2 (skala juz naniesiona na kontury)."""
    w = len(mat[0]) if mat else 0
    h = len(mat)
    loops = iso_loops(mat)
    if not loops or w2 < 1 or h2 < 1:
        return [[0] * max(w2, 0) for _ in range(max(h2, 0))]
    cw, ch = w2 * S, h2 * S
    sx, sy = cw / float(w), ch / float(h)
    acc = Image.new("L", (cw, ch), 0)
    for lp in loops:
        pts = [(x * sx, y * sy) for x, y in lp]
        tmp = Image.new("L", (cw, ch), 0)
        ImageDraw.Draw(tmp).polygon(pts, fill=255)
        acc = ImageChops.difference(acc, tmp)      # XOR (even-odd => dziury)
    small = acc.resize((w2, h2), Image.BOX)
    data = _flat(small)
    out = []
    for r in range(h2):
        row = data[r * w2:(r + 1) * w2]
        out.append([0 if v < INK_MIN else int(v) for v in row])
    return out


def variant_contour(g0, k):
    out = []
    for g in g0:
        if not g["enc"]:
            out.append(g); continue
        w2 = int(round(g["w"] * k)); h2 = int(round(g["h"] * k))
        left = int(round(signed(g["left"]) * k))
        top = int(round(signed(g["top"]) * k))
        mat = rasterize_glyph(g["mat"], w2, h2)
        out.append(dict(gi=g["gi"], enc=1, left=left, top=top, w=w2, h=h2,
                        mat=mat, raw=g["raw"]))
    return out


def variant_nearest(g0, k):
    """Referencja nearest (do porownania w podgladzie)."""
    out = []
    for g in g0:
        if not g["enc"]:
            out.append(g); continue
        w2 = int(round(g["w"] * k)); h2 = int(round(g["h"] * k))
        left = int(round(signed(g["left"]) * k))
        top = int(round(signed(g["top"]) * k))
        mat = []
        for r in range(h2):
            src = g["mat"][min(g["h"] - 1, int(r / k))]
            mat.append([src[min(g["w"] - 1, int(c / k))] for c in range(w2)])
        out.append(dict(gi=g["gi"], enc=1, left=left, top=top, w=w2, h=h2,
                        mat=mat, raw=g["raw"]))
    return out


def build(name, install):
    orig = open(os.path.join(SRC, name + ".fnt.orig"), "rb").read()
    f0, g0 = F.decode(orig)
    height = int(round(f0["height"] * K))

    g2 = variant_contour(g0, K)
    gn = variant_nearest(g0, K)
    data = F.encode_glyphs(g2, height, f0["fieldA"])

    # walidacja
    f2, g2d = F.decode(data)
    assert f2["fieldA"] == f0["fieldA"] and f2["blk"][1] == f0["blk"][1], "naglowek!"
    assert f2["height"] == height, "height!"
    assert len(g2d) == len(g0), "count!"
    vals = set()
    for a, b, nn in zip(g2, g2d, gn):
        assert a["enc"] == b["enc"]
        if not a["enc"]:
            assert a["raw"] == b["raw"], "raw gi=%d" % a["gi"]
            continue
        # wymiary = nearest (identyczny layout/advance)
        assert (b["w"], b["h"]) == (nn["w"], nn["h"]), "wymiar gi=%d" % a["gi"]
        assert (b["left"], b["top"]) == (a["left"] & 0xFFFFFFFF,
                                         a["top"] & 0xFFFFFFFF), "polozenie gi=%d" % a["gi"]
        assert b["mat"] == a["mat"], "mat gi=%d" % a["gi"]
        for row in a["mat"]:
            for v in row:
                if v:
                    assert v >= INK_MIN, "wartosc %d" % v
                    vals.add(v)

    # podglady + porownanie z nearest
    p_c1 = os.path.join(TMP, "prev_contour_%s.png" % name)
    p_c2 = os.path.join(TMP, "prev_contour_%s_z2.png" % name)
    F.render(f2, TEXT, p_c1, zoom=1)
    F.render(f2, TEXT, p_c2, zoom=2)

    fn = F.encode_glyphs(gn, height, f0["fieldA"])
    f_n, _ = F.decode(fn)
    p_n4 = os.path.join(TMP, "_n_%s_z4.png" % name)
    p_c4 = os.path.join(TMP, "_c_%s_z4.png" % name)
    szn = F.render(f_n, TEXT, p_n4, zoom=4)
    F.render(f2, TEXT, p_c4, zoom=4)

    # porownanie ukladane: nearest (gora) vs kontur (dol)
    lab_font = ImageFont.truetype(os.path.join(WINDIR, "arial.ttf"), 28)
    a = Image.open(p_n4).convert("RGB")
    b = Image.open(p_c4).convert("RGB")
    lab_h, pad = 44, 12
    W = max(a.width, b.width) + pad * 2
    H = (lab_h + a.height + lab_h + b.height + pad * 3)
    canvas = Image.new("RGB", (W, H), (18, 18, 22))
    d = ImageDraw.Draw(canvas)
    d.text((pad, pad - 4), "NEAREST x1.25 (bloki 1-2 px)", font=lab_font, fill=(255, 230, 120))
    canvas.paste(a, (pad, lab_h + pad))
    y2 = lab_h + pad + a.height + pad
    d.text((pad, y2 - 4), "KONTUR x1.25 (iso-50%%, AA x%d)" % S, font=lab_font, fill=(120, 255, 180))
    canvas.paste(b, (pad, y2 + lab_h))
    p_cmp = os.path.join(TMP, "cmp125_%s_z4.png" % name)
    canvas.save(p_cmp)

    # szerokosc testu (potwierdzenie = nearest)
    po = os.path.join(TMP, "_o_%s.png" % name)
    F.render(f0, TEXT, po, zoom=1)
    from PIL import Image as I
    wo = I.open(po).width
    wn = I.open(p_c1).width

    if install:
        with open(os.path.join(SRC, name + ".fnt"), "wb") as fh:
            fh.write(data)

    print("%s: height %d->%d  szer. %d->%d (%+.0f%%)  tusz=%d wart. [%d..%d]  %s" % (
        name, f0["height"], height, wo, wn, 100.0 * wn / wo - 100.0,
        len(vals), min(vals), max(vals), "ZAINSTALOWANO" if install else "podglad"))
    print("   -> %s" % p_c1)
    print("   -> %s" % p_cmp)


def main():
    install = "--install" in sys.argv
    print("=== Kontur x1.25 (iso=%.1f, supersampling x%d, INK_MIN=%d) %s ===" % (
        ISO, S, INK_MIN, "INSTALACJA" if install else "PODGLAD"))
    for name in ("font08", "font12"):
        build(name, install)
    if not install:
        print("(bez zapisu — uruchom z --install po akceptacji podgladu)")


if __name__ == "__main__":
    main()
