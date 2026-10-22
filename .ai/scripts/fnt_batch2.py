# -*- coding: utf-8 -*-
"""fnt_batch2.py — Etap batch-2: fonty hypertext (credits/history/ingamehelp)
oraz briefingow kampanii (CN.PLMAPS\\**), wariant KONTUROWY x1.25.

Zakres wg plan-2-fonty-fnt.md (Etap 6 -> batch-2):
  - font12.fnt        -> kontur x1.25 (height 12->15)   [tak jak GUI, zaakceptowany]
  - fonthead16bld.fnt -> kontur x1.25 (height 16->20)
  - font10.fnt / font_10.fnt -> ORYGINAL (font wąski — decyzja użytkownika z GUI)
  - inne nazwy        -> raportowane, bez zmian

Kazdy plik: dekod + round-trip encode(decode)==oryginal (dowod pelnego odczytu),
przy instalacji backup '<plik>.fnt.orig' (jesli nie istnieje) i walidacja nowego pliku.

Uzycie (python 3.11):
    python fnt_batch2.py           # DOMYSLNIE: inwentaryzacja + walidacja + podglady
    python fnt_batch2.py --install # nadpisanie plikow skali x1.25 (z backupami)
"""
import os, sys, hashlib, collections
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fnt_scale as F
import fnt_contour as C

GAME = r"G:\Games\CnMod 1.2"
ROOTS = [
    os.path.join(GAME, r"Data\text\pol\hypertext"),
    os.path.join(GAME, "CN.PLMAPS"),
]
TMP = r"C:\Users\Michael1099\AppData\Local\Temp\opencode"
WINDIR = r"C:\Windows\Fonts"

SCALE = {"font12.fnt", "fonthead16bld.fnt"}   # skala konturowa x1.25
KEEP = {"font10.fnt", "font_10.fnt"}          # oryginal (font waski)
TEXT = ("Historia kampanii — briefings\n"
        "Zażółć gęślą jaźń ĄĆĘŁŃÓŚŹŻ\n"
        "Buduj targowisko i zwiadowcy!\n"
        "0123456789 ?! -=%()\n"
        "Twoim zadaniem jest zbudowanie osady\n"
        "przed nadejściem zimy. Zbierz 120 drewna\n"
        "i wyslij zwiadowce na poludnie.")


def md5(data):
    return hashlib.md5(data).hexdigest()


def scan():
    """[(path, name_lower, md5)] dla wszystkich *.fnt w ROOTS."""
    out = []
    for root in ROOTS:
        for dp, dn, fn in os.walk(root):
            for n in fn:
                if n.lower().endswith(".fnt"):
                    p = os.path.join(dp, n)
                    with open(p, "rb") as fh:
                        out.append((p, n.lower(), md5(fh.read())))
    return out


def main():
    install = "--install" in sys.argv
    files = scan()
    # grupowanie po (nazwa, zawartosc)
    groups = collections.defaultdict(list)
    for p, name, h in files:
        groups[(name, h)].append(p)
    print("=== Batch 2: %d plikow .fnt, %d unikalnych (nazwa+md5) ==="
          % (len(files), len(groups)))
    print("    tryb: %s" % ("INSTALACJA" if install else "inwentaryzacja/podglad"))

    # wczytaj tresci unikalne
    contents = {}
    for key in groups:
        with open(groups[key][0], "rb") as fh:
            contents[key] = fh.read()

    scaled = []      # (name, size, data_nowa, data_orig, h1, h2, n_kopii)
    new_by_key = {}  # (name, md5) -> nowe bajty
    kept = []
    other = []
    for (name, h) in sorted(groups):
        data = contents[(name, h)]
        f0, g0 = F.decode(data)
        # dowod poprawnosci: round-trip bajt-w-bajt
        rt = F.encode_glyphs(g0, f0["height"], f0["fieldA"])
        ok = (rt == data)
        nenc = sum(1 for g in g0 if g["enc"])
        tag = "RT-OK" if ok else "RT-FAIL!!!"
        if name in SCALE:
            height2 = int(round(f0["height"] * C.K))
            g2 = C.variant_contour(g0, C.K)
            new = F.encode_glyphs(g2, height2, f0["fieldA"])
            # walidacja nowego pliku (twarda)
            f2, g2d = F.decode(new)
            assert F.encode_glyphs(g2d, f2["height"], f2["fieldA"]) == new, "round-trip nowego!"
            assert f2["height"] == height2 and f2["fieldA"] == f0["fieldA"]
            assert len(g2d) == len(g0)
            for a, b in zip(g2, g2d):
                assert a["enc"] == b["enc"] and a["mat"] == b["mat"], "mat gi=%d" % a["gi"]
            if not ok:
                tag = tag.replace("RT-FAIL!!!", "RT-FAIL(oryg)>nowy OK")
            new_by_key[(name, h)] = new
            scaled.append((name, len(data), new, data, f0["height"], height2,
                           len(groups[(name, h)])))
            print("  [SCALE] %-20s %6d B  h %d->%d  glyf=%d  %s  kopii=%d"
                  % (name, len(data), f0["height"], height2, len(g0), tag,
                     len(groups[(name, h)])))
        elif name in KEEP:
            kept.append((name, len(data), f0["height"], len(g0), tag, len(groups[(name, h)])))
            print("  [KEEP ] %-20s %6d B  h %d    glyf=%d  %s  kopii=%d"
                  % (name, len(data), f0["height"], len(g0), tag,
                     len(groups[(name, h)])))
        else:
            other.append((name, len(data), f0["height"], len(g0), tag, len(groups[(name, h)])))
            print("  [???  ] %-20s %6d B  h %d    glyf=%d  %s  kopii=%d"
                  % (name, len(data), f0["height"], len(g0), tag,
                     len(groups[(name, h)])))

    # statystyka zawartosci
    uniq = collections.defaultdict(lambda: [0, set()])
    for (name, h) in groups:
        uniq[name][0] += 1
        uniq[name][1].add(h)

    if not install:
        # podglad: dla KAZDEGO wariantu (nazwa + rozmiar) before/after do TMP
        for (name, size, new, orig, h1, h2, ncopy) in scaled:
            base = "b2_%s_%d" % (name[:-4], size)
            f_new, _ = F.decode(new)
            f_old, _ = F.decode(orig)
            F.render(f_old, TEXT, os.path.join(TMP, base + "_before.png"), zoom=1)
            F.render(f_new, TEXT, os.path.join(TMP, base + "_after.png"), zoom=1)
            F.render(f_new, TEXT, os.path.join(TMP, base + "_after_z2.png"), zoom=2)
        print("(podglady: %s\\b2_*.png — bez zapisu do gry)" % TMP)
        return

    # instalacja: zapis kazdej unikalnej zawartosci pod wszystkimi sciezkami
    n_written = n_backup = 0
    for key in sorted(new_by_key):
        new = new_by_key[key]
        for p in groups[key]:
            bak = p + ".orig"
            if not os.path.exists(bak):
                os.replace(p, bak)
                n_backup += 1
            with open(p, "wb") as fh:
                fh.write(new)
            n_written += 1
    print("Zapisano %d plikow (%d nowych backupow .orig)" % (n_written, n_backup))


if __name__ == "__main__":
    main()
