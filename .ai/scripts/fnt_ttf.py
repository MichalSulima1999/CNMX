# -*- coding: utf-8 -*-
"""fnt_ttf.py — Etap 5 (plan-2): przebudowa fontow UI .fnt na TTF z antyaliasingiem.

Wariant TTF x1.5 (uzgodniony):
  * font08 -> Tahoma (auto ~14px), font12 -> Tahoma (auto ~22px), x-height x1.5,
  * font10 to font WASKI (oryginal ~27% wezszy od font12 przy tej samej wysokosci):
    instalowane warianty bierne do wyboru: font10_tahoma.fnt (+64% — ryzyko
    przelewania) i font10_impact.fnt (Impact ~18px, +22% — waski, inny styl);
    domyslnie font10.fnt = oryginal (bez zmian),
  * metryki plaskie: height = T + D (najciezsza interlinia bez nachodzenia glifow),
  * wartosc piksela = pokrycie tuszu 0..255 (pelna rampa palet font_*.pcx = AA),
    pokrycie < INK_MIN -> przezroczystosc (brak danych w RLE),
  * count / fieldA / uklad indeksow / znaki bez tuszu (enc=0) — bez zmian vs oryginal.

Uzycie (python 3.11):
    python fnt_ttf.py --dry   # tylko budowa + walidacja + podglady, bez zapisu Data
    python fnt_ttf.py         # nadpisuje font{08,12}.fnt (backup: *.fnt.orig)
Podglady: TMP\\prev_ttf_*.png (1:1) i prev_ttf_*_z2.png (zoom2).
"""
import os, sys, struct
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fnt_scale as F

SRC = r"G:\Games\CnMod 1.2\Data\gui\fonts"
TMP = r"C:\Users\Michael1099\AppData\Local\Temp\opencode"
TAHOMA = r"C:\Windows\Fonts\tahoma.ttf"
IMPACT = r"C:\Windows\Fonts\impact.ttf"
FACTOR = 1.5          # skala wzgledem oryginalu (wg wysokosci x)
INK_MIN = 40          # prog przezroczystosci (ponizej: brak tuszu w RLE)
PAD = 6
TEST = ("Zażółć gęślą jaźń ĄĆĘŁŃÓŚŹŻ\n"
        "Buduj targowisko i zwiadowcy!\n"
        "0123456789 ?! -=%()")

# (zrodlo, krój, wynik, factor | None = domyslny), wynik w Data\gui\fonts
# dla font10 warianty sa bierne (plik nie jest ladowany przez gre)
JOBS = [
    ("font08", TAHOMA, "font08", None),
    ("font12", TAHOMA, "font12", None),
    ("font10", TAHOMA, "font10_tahoma", None),     # wariant bierny
    ("font10", IMPACT, "font10_impact", None),     # wariant bierny x1.5
    ("font10", IMPACT, "font10_impact125", 1.25),  # wariant bierny x1.25
]


def signed(x):
    return x - 0x100000000 if x >= 0x80000000 else x


def xheight_at100(fp):
    ft = ImageFont.truetype(fp, 100)
    b = ft.getbbox("x")
    return b[3] - b[1]


def rastify(font, ch, size):
    """Rasteryzuj jeden znak. Zwraca (left, t, w, h, mat, d) albo None (brak tuszu).

    t = od gory linii do gory tuszu przy baseline B0 (do globalnego wyliczenia T);
    d = od baseline do dolu tuszu (do globalnego D). left = bearing od pozycji pisaka.
    """
    B0 = 2 * size
    cw = size * 6
    ch_h = 3 * size + 2 * PAD
    im = Image.new("L", (cw, ch_h), 0)
    d = ImageDraw.Draw(im)
    d.text((PAD, PAD + B0), ch, font=font, fill=255, anchor="ls")
    bbox = im.getbbox()
    if not bbox:
        return None
    x0, y0, x1, y1 = bbox
    w, h = x1 - x0, y1 - y0
    data = list(im.crop((x0, y0, x1, y1)).getdata())
    mat = []
    for r in range(h):
        row = data[r * w:(r + 1) * w]
        mat.append([0 if v < INK_MIN else int(v) for v in row])
    return (x0 - PAD, B0 - y0, w, h, mat, y1 - B0)


def build_slot(name, ttf_path, out_stem, install, factor=FACTOR):
    orig = open(os.path.join(SRC, name + ".fnt"), "rb").read()
    f0, g0 = F.decode(orig)

    # --- rozmiar kroju: x1.5 wzgledem oryginalnego x-height ---
    xi = 0x78 - 0x20                       # 'x'
    if xi >= len(g0) or not g0[xi]["enc"]:
        raise SystemExit("%s: brak glifu 'x' do pomiaru" % name)
    xh0 = g0[xi]["h"]
    target = xh0 * factor
    xh100 = xheight_at100(ttf_path)
    size = max(6, int(round(target * 100.0 / xh100)))
    font = ImageFont.truetype(ttf_path, size)
    kr = os.path.splitext(os.path.basename(ttf_path))[0]

    # --- rasteryzacja wszystkich glifow z tuszem ---
    glyphs = []
    T = 0
    D = 0
    no_ink = []
    for g in g0:
        if not g["enc"]:
            glyphs.append(g)               # oryginalny rekord 1:1 (spacja/NBSP/itp.)
            continue
        ch_b = g["gi"] + 0x20
        try:
            ch = bytes([ch_b]).decode("cp1250")
        except UnicodeDecodeError:
            # bajt niezdefiniowany w CP1250 (0x81/0x8D/0x8F/...) — oryginalny glif 1:1
            glyphs.append(g)
            continue
        r = rastify(font, ch, size)
        if r is None:
            # znak bez tuszu mimo enc=1 — zachowaj oryginalny advance, pusta linia
            no_ink.append(ch)
            w = g["w"] if g["w"] else 1
            glyphs.append(dict(gi=g["gi"], enc=1, left=signed(g["left"]), top=0,
                               w=w, h=1, mat=[[0] * w]))
            continue
        left, t, w, h, mat, dd = r
        T = max(T, t)
        D = max(D, dd)
        glyphs.append(dict(gi=g["gi"], enc=1, left=left, top=t, w=w, h=h, mat=mat,
                           _t=t))

    # --- korekta top do wspolnej linii bazowej + interlinia ---
    for g in glyphs:
        if "_t" in g:
            g["top"] = T - g["_t"]
            del g["_t"]
    height = T + D
    if height <= 0:
        raise SystemExit("%s: pusta metryka" % name)

    # --- enkoduj ---
    data2 = F.encode_glyphs(glyphs, height, f0["fieldA"])

    # --- walidacja round-trip ---
    f2, g2 = F.decode(data2)
    assert f2["fieldA"] == f0["fieldA"], "fieldA zmienione!"
    assert f2["blk"][1] == f0["blk"][1], "count zmieniony!"
    assert f2["height"] == height, "height!"
    assert len(g2) == len(g0), "liczba glifow!"
    vals = set()
    for a, b in zip(glyphs, g2):
        assert a["enc"] == b["enc"], "enc gi=%d" % a["gi"]
        if not a["enc"]:
            assert a["raw"] == b["raw"], "raw gi=%d" % a["gi"]
            continue
        assert (b["left"], b["top"], b["w"], b["h"]) == \
               (a["left"] & 0xFFFFFFFF, a["top"] & 0xFFFFFFFF, a["w"], a["h"]), \
               "metryki gi=%d" % a["gi"]
        assert b["mat"] == a["mat"], "mat gi=%d" % a["gi"]
        for row in a["mat"]:
            for v in row:
                if v:
                    assert v >= INK_MIN, "wartosc %d < INK_MIN" % v
                    vals.add(v)

    # --- porownanie szerokosci testu: oryginal vs nowy ---
    p_orig = os.path.join(TMP, "w_%s_orig.png" % name)
    p_new = os.path.join(TMP, "w_%s_%s.png" % (name, out_stem))
    F.render(f0, TEST, p_orig, zoom=1)
    F.render(f2, TEST, p_new, zoom=1)
    from PIL import Image as I
    wo = I.open(p_orig).width
    wn = I.open(p_new).width

    # --- podglady ---
    F.render(f2, TEST, os.path.join(TMP, "prev_ttf_%s.png" % out_stem), zoom=1)
    F.render(f2, TEST, os.path.join(TMP, "prev_ttf_%s_z2.png" % out_stem), zoom=2)

    if install:
        with open(os.path.join(SRC, out_stem + ".fnt"), "wb") as fh:
            fh.write(data2)
    else:
        with open(os.path.join(TMP, out_stem + ".fnt"), "wb") as fh:
            fh.write(data2)

    print("%-14s <- %s %dpx: x %d->%.1f (x%.2f)  T=%d D=%d height %d->%d  "
          "szer. %d->%d (%+.0f%%)  %s%s" % (
              out_stem + ".fnt", kr, size, xh0, xh100 * size / 100.0,
              xh100 * size / 100.0 / xh0, T, D, f0["height"], height, wo, wn,
              100.0 * wn / wo - 100.0,
              "Zapisano Data" if install else "TMP (bierne)",
              ("; bez tuszu: %r" % "".join(no_ink)) if no_ink else ""))
    return data2


def main():
    install = "--dry" not in sys.argv
    print("=== Etap 5: TTF re-raster (x%.1f, INK_MIN=%d) %s ===" % (
        FACTOR, INK_MIN, "INSTALACJA" if install else "DRY-RUN"))
    for src, ttf, out, fac in JOBS:
        # font10_*.fnt sa plikami biernymi (gra ich nie laduje) — tez trafiaja do Data
        build_slot(src, ttf, out, install, fac or FACTOR)
    print("OK. Podglady: %s\\prev_ttf_*.png" % TMP)


if __name__ == "__main__":
    main()
