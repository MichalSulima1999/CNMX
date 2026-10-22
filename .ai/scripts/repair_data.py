#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Naprawa plików danych uszkodzonych przez stare clone-house:
  - podwójne CR (zapis w trybie tekstowym), sklejane linie (debugname + logictype),
  - duplikaty: logictype 1 x2, logictype 62 x3, zbędny [GfxHouse] dla id 1,
  - mojibake w nazwach (cp1250 czytane jako utf-8 i z powrotem).

Bazujemy na kopiach *.orig (surowe kopie oryginalnych plików gry).
Aktualne (uszkodzone) pliki trzymamy jako *.broken.bak.

Co przywracamy:
  types\\houses.ini             : .orig (logictype 1..55) + czysty blok logictype 56
  stringstext\\gameobjects\\... : .orig (stringn 0..55, CP1250) + para stringn/string 56
  budynki12\\houses\\houses.ini : .orig + osobny [GfxHouse] dla LogicType 0 56
                                  (sklon z bloku "viking well", tak jak planował Etap C)

Potem (osobno, gotowym skryptem):
  python .ai\\scripts\\modkit.py clone-house --from 1 --to 62 --name "Dom TEST 62"
"""
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import modkit as mk

ROOT = Path(__file__).resolve().parents[2]

TYPES = ROOT / "CN.PLMOD" / "types" / "houses.ini"
NAMES = ROOT / "CN.PLMOD" / "stringstext" / "gameobjects" / "houses.ini"
GFX = ROOT / "CN.PLMOD" / "budynki12" / "houses" / "houses.ini"

ID56 = 56
DBG56 = "studnia etapc"      # debugname musi być unikalne - mapy się do niego odwołują
NAME56 = "Studnia EtapC"     # stringn (lm. r.) - tak nazywa się testowy budynek Etapu C
NAME56_PL = "Studnie EtapC"  # string (liczba mnoga)


def to_crlf(s: str) -> str:
    # Kolejność WAŻNA: uszkodzony plik ma końce \r\r\n (stary skrypt dublował CR).
    # Najpierw \r\r\n -> \n, potem \r\n -> \n, na końcu \r -> \n; w przeciwnym razie
    # \r\r\n rozkłada się na DWIE nowe linie (pusta linia pomiędzy każdą linią bloku).
    s = s.replace("\r\r\n", "\n").replace("\r\n", "\n").replace("\r", "\n")
    return s.replace("\n", "\r\n")


def orig_path(p: Path) -> Path:
    o = p.with_suffix(p.suffix + ".orig")
    if not o.is_file():
        raise SystemExit(f"[E] brak kopii .orig dla {p}")
    return o


def broken_backup(p: Path):
    b = p.with_suffix(p.suffix + ".broken.bak")
    if p.is_file() and not b.is_file():
        shutil.copy2(p, b)
        print(f"[i] kopia uszkodzonego pliku: {b}")


def extract_block(text: str, header: str, pattern: str) -> str:
    for _s, _e, b in mk._section_blocks(text, header):
        if re.search(pattern, b, re.M):
            return b
    raise SystemExit(f"[E] nie znalazłem bloku [{header}] pasującego do {pattern!r}")


def set_debugname(block: str, dbg: str) -> str:
    return re.sub(r'(^|\n)([^\S\n]*debugname\s+")[^"]*(")',
                  lambda m: m.group(1) + m.group(2) + dbg + m.group(3), block, count=1)


def set_editname(block: str, name: str) -> str:
    return re.sub(r'(^|\n)([^\S\n]*EditName\s+")[^"]*(")',
                  lambda m: m.group(1) + m.group(2) + name + m.group(3), block, count=1)


def report(p: Path, pat: str):
    data = p.read_bytes()
    ids = re.findall(pat, mk.decode_bytes(data))
    lf, crlf = data.count(b"\n"), data.count(b"\r\n")
    extra = data.count(b"\r") - crlf
    print(f"    {p.name}: wpisy={len(ids)} LF={lf} extraCR={extra} -> {ids}")


def main() -> int:
    # ------------------------------------------------------------------ types
    print("[1] types\\houses.ini")
    broken_backup(TYPES)
    # Blok 56 bierzemy z kopii uszkodzonego pliku (.broken.bak): aktualny plik mógł
    # już zawierać nieczysty wariant (wcześniejszy przebieg), a .broken.bak to stan
    # wyjściowy z liniami \r\r\n (poprawnie rozwiązanymi przez to_crlf).
    src56 = TYPES.with_suffix(TYPES.suffix + ".broken.bak")
    if not src56.is_file():
        src56 = TYPES
    cur = mk.decode_bytes(src56.read_bytes())
    b56 = extract_block(cur, "logichousetype", r"(^|\n|\r)\s*logictype\s+56\b")
    b56 = set_debugname(to_crlf(b56).strip("\r\n"), DBG56)
    # Stary skrypt zapisał blok z pustą linią PO KAŻDEJ linii (\r\r\n\r\r\n).
    # W danych gry blok [logichousetype] jest ciągły - puste linie wewnątrz wycinamy.
    b56 = "\r\n".join(ln for ln in b56.split("\r\n") if ln.strip()).strip("\r\n")
    if not re.search(r"(^|\n)\s*logictype\s+56\b", b56):
        raise SystemExit("[E] wyciągnięty blok nie zawiera logictype 56")
    TYPES.write_bytes(orig_path(TYPES).read_bytes())   # przywróć surowy oryginał
    mk._append_raw(TYPES, b56)                          # dopisz czysty blok 56
    report(TYPES, r"logictype (\d+)")

    # ------------------------------------------------------------------ names
    print("[2] stringstext\\gameobjects\\houses.ini")
    broken_backup(NAMES)
    NAMES.write_bytes(orig_path(NAMES).read_bytes())
    mk._append_raw(NAMES, f'stringn {ID56} "{NAME56}"\r\nstring "{NAME56_PL}"')
    report(NAMES, r"stringn (\d+)")

    # ------------------------------------------------------------------- gfx
    print("[3] budynki12\\houses\\houses.ini")
    broken_backup(GFX)
    og = orig_path(GFX).read_bytes()
    bgfx = extract_block(mk.decode_bytes(og), "GfxHouse",
                         r'(^|\n|\r)[^\S\n]*EditName\s+"viking well"')
    bgfx = mk._clone_block_id(to_crlf(bgfx).strip("\r\n"), "LogicType 0", 10, ID56)
    if bgfx is None or f"LogicType 0 {ID56}" not in bgfx:
        raise SystemExit("[E] nie udało się sklonować bloku GfxHouse dla 56")
    bgfx = set_editname(bgfx, NAME56)
    GFX.write_bytes(og)
    mk._append_raw(GFX, bgfx)
    report(GFX, r"LogicType 0 (\d+)")

    print("\n[OK] dane naprawione. Teraz:")
    print('    python .ai\\scripts\\modkit.py clone-house --from 1 --to 62 --name "Dom TEST 62"')
    print("    python .ai\\scripts\\modkit.py validate")
    return 0


if __name__ == "__main__":
    sys.exit(main())
