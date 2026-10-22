# -*- coding: utf-8 -*-
"""Testy regresyjne modkit.py - chronią przed bugami, które już psuły dane gry:

1. _clone_key_line / _clone_block_id:
   - podmiana id W MIEJSCU (nie doklejanie: 'LogicType 0 10' -> 'LogicType 0 56',
     a nie 'LogicType 0 1056'),
   - zwracanie None, gdy id nie występuje (wcześniej cichy fallback kopiował
   - blok bez zmian i robił duplikaty),
   - brak pochłaniania końców linii (CR/CRLF nietknięte - zero sklejanych linii).
2. _append_raw / _write_raw:
   - zero podwójnych CR (stare open(..., 'a') w trybie tekstowym psuło końcówki),
   - zachowanie kodowania (cp1250 vs utf-8),
   - rozdzielacz: pusta linia tylko przed NOWYM blokiem sekcji, wpisy wewnątrz
     sekcji dopisywane bez pustych linii.

Uruchomienie:  python .ai\\scripts\\_test_modkit.py   (nie modyfikuje danych gry)
"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import modkit as mk

ok = True


def check(label: str, got, want):
    global ok
    good = got == want
    ok &= good
    print(("OK  " if good else "BLAD"), label, "->", repr(got)[:100]
          + ("" if good else f"  (oczekiwane {want!r})"))


# ------------------------------------------------------------------ clone id
CASES = [
    ("logictype 1\r\n", "logictype", 1, 62, "logictype 62\r\n"),
    ("  logictype 10\r\n", "logictype", 10, 56, "  logictype 56\r\n"),
    ("logictype 10\r\n", "logictype", 1, 62, None),          # 1 != 10
    ("LogicType 0 10\r\n", "LogicType 0", 10, 56, "LogicType 0 56\r\n"),
    ('stringn 1 "Kwatera glowna"\r\n', "stringn", 1, 62,
     'stringn 62 "Kwatera glowna"\r\n'),
    ('stringn 12 "x"', "stringn", 1, 62, None),
    ('debugname "x"\r\nlogictype 1\r\n', "logictype", 1, 7, None),  # nie ta linia
]
for line, key, f, t, exp in CASES:
    check(f"_clone_key_line {line!r} {f}->{t}", mk._clone_key_line(line, key, f, t), exp)

blk = ('[logichousetype]\r\ndebugname "headquarters"\r\nlogictype 1\r\n'
       'logicmaintype 1\r\n')
check("blok: tylko linia z id",
      mk._clone_block_id(blk, "logictype", 1, 62),
      '[logichousetype]\r\ndebugname "headquarters"\r\nlogictype 62\r\n'
      'logicmaintype 1\r\n')
check("blok: brak id -> None", mk._clone_block_id(blk, "logictype", 99, 100), None)

# ------------------------------------------------------------------- append
tmp = Path(tempfile.mkdtemp(prefix="modkit_test_"))

# a) plik w stylu gry: sekcja [text] + wpisy cp1250, dopisek WPISU = bez pustej linii
p = tmp / "t.ini"
orig = b'[text]\r\nstringn 1 "g\xb3\xf3wna"\r\n'
p.write_bytes(orig)
mk._append_raw(p, 'stringn 62 "Dom TEST 62"')
mk._append_raw(p, 'stringn 63 "Drugi wpis"')
data = p.read_bytes()
extra = data.count(b"\r") - data.count(b"\r\n")
check("append: bez podwójnych CR", extra, 0)
check("append: oryginał nietknięty", data.startswith(orig), True)
check("append: cp1250 zachowane", b"g\xb3\xf3wna" in data, True)
check("append: wpisy ciągłe (bez pustych linii)",
      data, orig + b'stringn 62 "Dom TEST 62"\r\nstringn 63 "Drugi wpis"\r\n')

# b) dopisek NOWEGO bloku sekcji = dokładnie jedna pusta linia przed nim
mk._append_raw(p, '[logichousetype]\r\nlogictype 62\r\n')
check("append: jeden blok = jedna pusta linia",
      p.read_bytes(),
      orig + b'stringn 62 "Dom TEST 62"\r\nstringn 63 "Drugi wpis"\r\n'
             b'\r\n[logichousetype]\r\nlogictype 62\r\n')

# c) _write_raw: odczyt -> zapis bez zmian bajtowych
before = p.read_bytes()
txt = mk._read_raw(p)
mk._write_raw(p, txt)
check("write_raw: roundtrip bajtowy", p.read_bytes() == before, True)

# d) nowy plik domyślnie cp1250 (gra czyta ANSI)
p2 = tmp / "new.ini"
mk._write_raw(p2, 'stringn 1 "łza"\r\n')
check("write_raw: nowy plik = cp1250", p2.read_bytes(), 'stringn 1 "łza"\r\n'.encode("cp1250"))

# e) odmowa zapisu tekstu do binarnego .cif
try:
    mk._write_raw(tmp / "x.cif", "tekst")
    check(".cif zablokowany", False, True)
except RuntimeError:
    check(".cif zablokowany", True, True)

print("WYNIK:", "ok" if ok else "BLEDY")
sys.exit(0 if ok else 1)
