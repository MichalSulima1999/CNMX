#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
modkit — narzędzie inspekcji/walidacji tabel typów gry Cultures (CN.PLMOD).

Etap A (patrz .ai/plans/plan-5-narzedzia-moderskie.md, .ai/docs/typy-budynkow-surowcow.md).

Podkomendy:
  inspect           inwentarz tabel: użyte / wolne / odsiane typy wg limitów exe
  validate          walidacja krzyżowa -> błędy/ostrzeżenia/info (exit 1 przy błędach)
  decode <cif>      dekoduje .cif do tekstu przez mapper tools\\cif2txt.exe
  limits            wypisz limity z logicdefines.inc

Zależności: tylko standardowa biblioteka. Opcjonalnie zewnętrzny cif2txt.exe
dla plików .cif (do dekodowania do cache).

Uruchomienie:
  python modkit.py inspect
  python modkit.py validate
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

# --------------------------------------------------------------------------
# Ścieżki i konfiguracja
# --------------------------------------------------------------------------

ROOT_DEFAULT = Path(__file__).resolve().parents[2]  # .ai/scripts -> root gry (CnMod 1.2)

LIMITS_FILE = "logicdefines.inc"          # w root gry (i Data\GameSourceIncludes)
CIF2TXT_REL = Path("mapper tools") / "cif2txt.exe"
CACHE_REL = Path(".ai") / ".modkit_cache"

# Tabela -> sekcje w pliku, klucz id, ścieżki (kolejność = priorytet exe: ini > cif)
TABLES = {
    "houses": dict(
        sections=["logichousetype"],
        id_key="logictype",
        paths=["CN.PLMOD\\types\\houses.ini", "Data\\logic\\housetypes.cif"],
        maxdef="HOUSE_TYPE_MAXIMUM",
    ),
    "goods": dict(
        sections=["goodtype"],
        id_key="type",
        paths=["Data\\logic\\goodtypes.ini", "Data\\logic\\goodtypes.cif"],
        maxdef="GOOD_TYPE_MAXIMUM",
    ),
    "weapons": dict(
        sections=["weapontype"],
        id_key="type",
        paths=["CN.PLMOD\\types\\weapons.ini"],
        maxdef="WEAPON_TYPE_MAXIMUM",
    ),
    "vehicles": dict(
        sections=["vehicletype"],
        id_key="type",
        paths=["Data\\logic\\vehicletypes.ini", "Data\\logic\\vehicletypes.cif"],
        maxdef="VEHICLE_TYPE_MAXIMUM",
    ),
    "jobs": dict(
        sections=["jobtype"],
        id_key="type",
        paths=["Data\\logic\\jobtypes.ini", "Data\\logic\\jobtypes.cif"],
        maxdef="JOB_TYPE_MAXIMUM",
    ),
    "armor": dict(
        sections=["armortype"],
        id_key="type",
        paths=["Data\\logic\\armortypes.ini", "Data\\logic\\armortypes.cif"],
        maxdef="ARMOR_TYPE_MAXIMUM",
    ),
    "tribes": dict(
        sections=["tribetype"],
        id_key="type",
        paths=["CN.PLMOD\\tribetypes12\\tribetypes.ini"],
        maxdef="TRIBE_TYPE_MAXIMUM",
    ),
    "landscapes": dict(
        sections=["landscapetype"],
        id_key="type",
        paths=["Data\\logic\\landscapetypes.ini", "Data\\logic\\landscapetypes.cif"],
        maxdef="LANDSCAPE_TYPE_MAXIMUM",
    ),
}

# Pliki nazw (lang = pol domyślnie). Sprawdzamy .ini i .cif.
NAME_PATHS = {
    "houses":    ["CN.PLMOD\\stringstext\\gameobjects\\houses.ini"],
    "goods":     ["Data\\text\\%s\\strings\\gameobjects\\goods.ini",
                  "Data\\text\\%s\\strings\\gameobjects\\goods.cif"],
    "jobs":      ["Data\\text\\%s\\strings\\gameobjects\\jobs.ini",
                  "Data\\text\\%s\\strings\\gameobjects\\jobs.cif"],
    "tribes":    ["Data\\text\\%s\\strings\\gameobjects\\tribes.ini",
                  "Data\\text\\%s\\strings\\gameobjects\\tribes.cif"],
    "vehicles":  ["Data\\text\\%s\\strings\\gameobjects\\vehicletypes.ini",
                  "Data\\text\\%s\\strings\\gameobjects\\vehicletypes.cif"],
}

# Plik graficzny budynków ([GfxHouse]) - bez limitu na liczbę wpisów.
GFX_HOUSES_PATH = "CN.PLMOD\\budynki12\\houses\\houses.ini"

# Dodatkowe tabele pomocnicze (wartości z logicdefines.inc; używane do walidacji zakresów)
AUX_DEFINES = {
    "maintype_max": "HOUSE_MAIN_TYPE_MAXIMUM",
}

def _ensure_dir(p: Path):
    p.parent.mkdir(parents=True, exist_ok=True)


def sniff_encoding(data: bytes) -> str:
    """Kodowanie pliku danych gry: UTF-8, gdy dane są poprawnym UTF-8, inaczej CP1250 (ANSI).

    Kluczowe: te same kodowanie przy odczycie i zapisie -> brak mojibake przy kolejnych
    modyfikacjach (wcześniej cp1250 'udawało' się zawsze, więc pliki UTF-8 psuły się
    przy każdym odczycie).
    """
    try:
        data.decode("utf-8")
        return "utf-8"
    except UnicodeDecodeError:
        return "cp1250"


def _eol_of(data: bytes) -> str:
    """Dominujące zakończenie linii w pliku (domyślnie CRLF jak w oryginalnych danych gry)."""
    if not data:
        return "\r\n"
    crlf = data.count(b"\r\n")
    lf = data.count(b"\n")
    return "\r\n" if crlf * 2 >= lf else "\n"


def _backup_once(p: Path) -> str | None:
    """Utwórz kopię .orig tylko raz (nie nadpisuj). Zwraca ścieżkę kopii albo None."""
    if not p.is_file():
        return None
    orig = p.with_suffix(p.suffix + ".orig")
    if not orig.is_file():
        try:
            import shutil
            shutil.copy2(p, orig)
            return str(orig)
        except Exception:
            return None
    return None


def _read_raw(p: Path) -> str:
    return decode_bytes(p.read_bytes())


def _write_raw(p: Path, s: str, encoding: str | None = None):
    """Zapisz treść bez zmiany końców linii (zero podwójnych CR) i w kodowaniu pliku."""
    if p.suffix.lower() == ".cif":
        raise RuntimeError(f"odmowa zapisu tekstu do binarnego pliku .cif: {p} "
                           f"(użyj pliku .ini obok - loader ma priorytet ini > cif)")
    _ensure_dir(p)
    _backup_once(p)
    data = p.read_bytes() if p.is_file() else b""
    # nowe pliki danych gry zapisujemy w ANSI gry (cp1250), istniejące - w ich kodowaniu
    enc = encoding or (sniff_encoding(data) if data else "cp1250")
    if not data:
        # nowy plik - styl gry: CRLF (dekodowany .cif ma \\n, a sanitywny .ini gry \\r\\n)
        s = s.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "\r\n")
    p.write_bytes(s.encode(enc, errors="replace"))


def _append_raw(p: Path, s: str, encoding: str | None = None,
                before: bytes | None = None) -> str | None:
    """Dopisz treść na końcu pliku (lub przed blokiem `before`, np. <CULTURES_CIF_END>).

    - nie tłumaczy newline -> żadnych podwójnych CR (poprzednie open(..., 'a') w trybie
      tekstowym zamieniało \\n w \\r\\n i każdy dopisek psuł końcówki linii),
    - zachowuje kodowanie pliku (cp1250 vs utf-8),
    - rozdzielacz (pusta linia) tylko w stylu, jaki plik już stosuje.

    Zwraca ścieżkę kopii .orig albo None.
    """
    _ensure_dir(p)
    if p.suffix.lower() == ".cif":
        raise RuntimeError(f"odmowa dopisania tekstu do binarnego pliku .cif: {p}")
    bak = _backup_once(p)
    data = p.read_bytes() if p.is_file() else b""
    enc = encoding or (sniff_encoding(data) if data else "cp1250")
    eol = _eol_of(data)
    body = s.replace("\r\n", "\n").replace("\r", "\n").strip("\n")
    chunk = body.replace("\n", eol).encode(enc, errors="replace")
    if data:
        if not data.endswith(b"\n"):
            data += eol.encode("ascii")
        # Rozdzielacz - dokładnie jedna pusta linia i tylko wtedy, gdy styl pliku
        # tego wymaga:
        #  - dopisujemy NOWY bloek sekcji ([logichousetype]/[GfxHouse]) -> gry trzymają
        #    pustą linię między blokami sekcji,
        #  - dopisujemy wpis wewnątrz sekcji (stringn/string) -> wpisy są ciągłe,
        #    żadnych pustych linii (stara reguła "jakikolwiek blank w pliku" dawała
        #    podwójną pustą linię w pliku nazw).
        e = eol.encode("ascii")
        starts_section = bool(re.match(r"\s*(\[|%01%)", body))
        has_sections = re.search(rb"^\s*(\[|%01%)", data, re.M) is not None
        blank_style = (e + e) in data
        sep = e if (starts_section or (blank_style and not has_sections)) and not data.endswith(e + e) else b""
        chunk = sep + chunk + e
    else:
        chunk = chunk + eol.encode("ascii")
    if before:
        m = re.search(before, data)
        new = (data[:m.start()] + chunk + data[m.start():]) if m else data + chunk
    else:
        new = data + chunk
    p.write_bytes(new)
    return bak


def _section_blocks(text: str, section_name: str) -> list[tuple[int, int, str]]:
    """
    Znajdź bloki sekcji [section_name] (INI) lub %01%section_name (CIF-text).
    Zwraca (start, end, block_text) — indeksy w oryginalnym tekście.
    """
    blocks: list[tuple[int, int, str]] = []
    # INI [section]
    pat_ini = re.compile(r"^\s*\[" + re.escape(section_name) + r"\]\s*$", re.M)
    for m in pat_ini.finditer(text):
        s = m.start()
        # koniec bloku: następny [xxx] na początku linii
        m2 = re.search(r"^\s*\[[^\]]+\]\s*$", text[m.end():], re.M)
        if m2:
            e = m.end() + m2.start()
        else:
            e = len(text)
        blocks.append((s, e, text[s:e]))
    # CIF %01%section
    pat_cif = re.compile(r"^\s*%01%" + re.escape(section_name) + r"\s*$", re.M)
    for m in pat_cif.finditer(text):
        s = m.start()
        m2 = re.search(r"^\s*(?:%01%|\[)[^\]]*\]?\s*$", text[m.end():], re.M)
        if m2:
            e = m.end() + m2.start()
        else:
            e = len(text)
        blocks.append((s, e, text[s:e]))
    # unikalne po start
    uniq: list[tuple[int, int, str]] = []
    seen = set()
    for s,e,b in blocks:
        if s not in seen:
            seen.add(s); uniq.append((s,e,b))
    return sorted(uniq, key=lambda x: x[0])


def _find_section_containing(text: str, section_name: str, predicate) -> tuple[int,int,str] | None:
    for s,e,b in _section_blocks(text, section_name):
        if predicate(b):
            return (s,e,b)
    return None


def _append_block(text: str, block_text: str) -> str:
    """Dopisz bloek sekcji na końcu tekstu.

    Zachowuje końce linii tekstu (wcześniej doklejało '\\n\\n' nawet do pliku
    CRLF - wychodził mieszany styl) i pilnuje stylu gry: jeden bloek = jedna
    pusta linia przed nim, linie wewnątrz bloku ciągłe.
    """
    body = block_text.replace("\r\n", "\n").replace("\r", "\n").strip("\n")
    if not text:
        return body + "\n"
    eol = "\r\n" if text.count("\r\n") * 2 >= text.count("\n") else "\n"
    if not text.endswith(("\n", "\r")):
        text += eol
    if not text.endswith(eol + eol):      # brak pustej linii przed nowym blokiem
        text += eol
    return text + body.replace("\n", eol) + eol


def _replace_block(text: str, start: int, end: int, new_block: str) -> str:
    return text[:start] + new_block.rstrip("\r\n") + "\n" + text[end:]


def _clone_key_line(line: str, id_key: str, from_id: int, to_id: int) -> str | None:
    """Podmień id w jednej linii ('logictype 1' -> 'logictype 62').

    Zwraca None, gdy linia nie zawiera szukanego id. Końce wierszy zostają nietknięte.
    Wcześniejsze regexy trzymały \n w osobnej grupie (niezapisanej) i pochłaniały \s*,
    przez co po podmianie linie się sklejały (np. debugname + logictype w jednej linii).
    """
    m = re.match(r"(\s*(?:%02%)?" + re.escape(id_key) + r"\s+)" + str(from_id) + r"\b", line)
    if not m:
        return None
    # m.end() obejmuje stare id - trzeba je zastąpić, a nie dokleić nowe po nim
    return line[:m.end() - len(str(from_id))] + str(to_id) + line[m.end():]


def _clone_block_id(block: str, id_key: str, from_id: int, to_id: int) -> str | None:
    """Sklonuj blok: pierwsza linia z kluczem id dostaje nowe id (praca linia po linii).

    None, gdy id nie znaleziono - dzięki temu nie dopiszemy milcząco niezmienionego
    duplikatu (stary kod robił fallback i kopiował blok 1:1).
    """
    lines = block.split("\n")
    for i, ln in enumerate(lines):
        new = _clone_key_line(ln, id_key, from_id, to_id)
        if new is not None:
            lines[i] = new
            return "\n".join(lines)
    return None


def _clone_section_block(block_text: str, id_key: str, from_id: int, to_id: int) -> str | None:
    """Sklonuj blok sekcji: zamień `id_key <from_id>` na `id_key <to_id>` (None = brak id)."""
    return _clone_block_id(block_text, id_key, from_id, to_id)


def _clone_gfxhouse_block(block_text: str, from_id: int, to_id: int) -> str | None:
    """[GfxHouse]: LogicType 0 <from> -> LogicType 0 <to> (None = brak id)."""
    return _clone_block_id(block_text, "LogicType 0", from_id, to_id)


# --------------------------------------------------------------------------
# Pomocnicze: limity z logicdefines.inc
# --------------------------------------------------------------------------

_DEFINE_RE = re.compile(r"^\s*#define\s+([A-Za-z0-9_]+)\s+(\d+)", re.M)


def load_defines(root: Path) -> dict[str, int]:
    """Wczytaj #define X N z logicdefines.inc (root lub Data\GameSourceIncludes)."""
    out: dict[str, int] = {}
    candidates = [root / LIMITS_FILE, root / "Data" / "GameSourceIncludes" / LIMITS_FILE]
    for p in candidates:
        if p.is_file():
            try:
                txt = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for m in _DEFINE_RE.finditer(txt):
                out[m.group(1)] = int(m.group(2))
            break
    return out


# twarde wartości z exe (potwierdzone disasemblacją) jako fallback
_FALLBACK_LIMITS = {
    "HOUSE_TYPE_MAXIMUM": 55, "GOOD_TYPE_MAXIMUM": 66, "WEAPON_TYPE_MAXIMUM": 22,
    "VEHICLE_TYPE_MAXIMUM": 7, "JOB_TYPE_MAXIMUM": 56, "ARMOR_TYPE_MAXIMUM": 5,
    "TRIBE_TYPE_MAXIMUM": 42, "LANDSCAPE_TYPE_MAXIMUM": 88,
    "HOUSE_MAIN_TYPE_MAXIMUM": 8,
}


def limit_of(defines: dict[str, int], name: str) -> int:
    return defines.get(name, _FALLBACK_LIMITS[name])


def valid_range(maximum: int) -> tuple[int, int]:
    """Walidowane przez exe: 1..MAX-1 (slot 0 = 'none')."""
    return (1, maximum - 1)


# --------------------------------------------------------------------------
# Parser INI/CIF
# --------------------------------------------------------------------------


class Section:
    __slots__ = ("name", "entries")

    def __init__(self, name: str):
        self.name = name
        self.entries: list[tuple[str, list[str]]] = []

    def add(self, key: str, rest: str):
        try:
            toks = shlex.split(rest)
        except ValueError:
            toks = rest.split()
        self.entries.append((key, toks))

    def items(self) -> dict[str, list[list[str]]]:
        d: dict[str, list[list[str]]] = {}
        for k, t in self.entries:
            d.setdefault(k, []).append(t)
        return d


def decode_bytes(data: bytes) -> str:
    enc = sniff_encoding(data)
    try:
        return data.decode(enc)
    except UnicodeDecodeError:
        return data.decode(enc, errors="replace")


def parse_text(text: str) -> list[Section]:
    """Parsuje formaty: [sekcja] oraz %01%sekcja / %02%klucz reszta (CIF-text)."""
    sections: list[Section] = []
    cur: Section | None = None
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("//") or line.startswith("<"):
            continue
        if line.startswith("[") and "]" in line:
            cur = Section(line[1:line.index("]")].strip())
            sections.append(cur)
            continue
        if line.startswith("%01%"):
            cur = Section(line[4:].strip())
            sections.append(cur)
            continue
        m = re.match(r"%02%(\S+)(?:\s+(.*))?$", line)
        if m:
            if cur is None:
                cur = Section("")
                sections.append(cur)
            cur.add(m.group(1), m.group(2) or "")
            continue
        mm = re.match(r"(\S+)(?:\s+(.*))?$", line)
        if mm:
            if cur is None:
                cur = Section("")
                sections.append(cur)
            cur.add(mm.group(1), mm.group(2) or "")

    # scal sekcje [""] poprzedzające [text]... nie: zostawiamy, patrz name_map
    return sections


def read_text(path: Path) -> str:
    return decode_bytes(path.read_bytes())


# --------------------------------------------------------------------------
# cif2txt (także cache)
# --------------------------------------------------------------------------


def decode_cif(root: Path, src: Path, dst: Path | None = None, cif2txt: Path | None = None) -> str:
    """Dekoduje .cif do tekstu przez cif2txt.exe; cache w .ai/.modkit_cache."""
    exe = cif2txt or (root / CIF2TXT_REL)
    if not exe.is_file():
        raise FileNotFoundError(f"brak cif2txt: {exe}")
    if dst is None:
        cache = root / CACHE_REL
        cache.mkdir(parents=True, exist_ok=True)
        h = hashlib.md5(str(src).encode("utf-8", "replace")).hexdigest()[:8]
        dst = cache / (src.stem + f"_{h}.txt")
    if not dst.is_file() or src.stat().st_mtime > dst.stat().st_mtime:
        r = subprocess.run([str(exe), "C", str(src), str(dst)], capture_output=True)
        if r.returncode != 0:
            raise RuntimeError(f"cif2txt nie powiodło się dla {src}: {r.stdout} {r.stderr}")
    return read_text(dst)


def first_existing(root: Path, paths: list[str]) -> Path | None:
    for rel in paths:
        p = root / rel
        if p.is_file():
            return p
    return None


def load_table_text(root: Path, table: str, cif2txt: Path | None = None) -> str:
    """Wczytuje treść pliku tabeli (ini lub cif) z priorytetem jak w exe."""
    cfg = TABLES[table]
    p = first_existing(root, cfg["paths"])
    if p is None:
        raise FileNotFoundError(f"brak plików tabeli '{table}': {cfg['paths']}")
    if p.suffix.lower() == ".cif":
        return decode_cif(root, p, cif2txt=cif2txt)
    return read_text(p)


def load_table_records(root: Path, table: str, cif2txt: Path | None = None) -> list[dict[str, list[list[str]]]]:
    cfg = TABLES[table]
    text = load_table_text(root, table, cif2txt)
    recs: list[dict[str, list[list[str]]]] = []
    for s in parse_text(text):
        if s.name in cfg["sections"]:
            recs.append(s.items())
    return recs


def int0(toks: list[str], idx: int = 0, default: int | None = None) -> int | None:
    if idx < len(toks):
        try:
            return int(toks[idx])
        except (TypeError, ValueError):
            return default
    return default


# --------------------------------------------------------------------------
# Nazwy (stringstext / gameobjects)
# --------------------------------------------------------------------------


def load_names(root: Path, table: str, lang: str, cif2txt: Path | None = None) -> dict[int, str]:
    """stringn <id> \"<nazwa>\" (oraz %02%stringn w wersji CIF-text)."""
    out: dict[int, str] = {}
    seen: set[int] = set()
    for rel in NAME_PATHS.get(table, []):
        p = root / (rel % lang if "%s" in rel else rel)
        if not p.is_file():
            continue
        if p.suffix.lower() == ".cif":
            text = decode_cif(root, p, cif2txt=cif2txt)
        else:
            text = read_text(p)
        for s in parse_text(text):
            if s.name not in ("text", ""):
                continue
            for key, toks in s.entries:
                if key not in ("stringn", "string"):
                    continue
                if toks and toks[0].isdigit():
                    i = int(toks[0])
                    if i in seen:
                        continue
                    name = " ".join(toks[1:])
                    if key == "stringn":
                        out[i] = name
                        seen.add(i)
    return out


# --------------------------------------------------------------------------
# Inwentarz (inspect)
# --------------------------------------------------------------------------


def rng_str(ids: set[int]) -> str:
    if not ids:
        return "-"
    return ",".join(str(i) for i in sorted(ids))


def compact(ids: set[int]) -> str:
    """1-3,5,7-9"""
    if not ids:
        return "-"
    prev = last = None
    parts = []
    for i in sorted(ids):
        if last is None:
            prev = last = i
        elif i == last + 1:
            last = i
        else:
            parts.append(str(prev) if prev == last else f"{prev}-{last}")
            prev = last = i
    parts.append(str(prev) if prev == last else f"{prev}-{last}")
    return " ".join(parts)


def inspect(root: Path, cif2txt: Path | None, args) -> int:
    defines = load_defines(root)
    print(f"root : {root}")
    print(f"limits: z {LIMITS_FILE}")
    for table, cfg in TABLES.items():
        maximum = limit_of(defines, cfg["maxdef"])
        lo, hi = valid_range(maximum)
        try:
            recs = load_table_records(root, table, cif2txt)
        except (FileNotFoundError, RuntimeError) as e:
            print(f"\n== {table:11s} BŁĄD: {e}")
            continue
        used: set[int] = set()
        dead: set[int] = set()
        missing: list[int] = []
        for i, rec in enumerate(recs):
            id_toks = rec.get(cfg["id_key"])
            idv = int0(id_toks[0]) if id_toks else None
            if idv is None:
                missing.append(i)
                continue
            if lo <= idv <= hi:
                used.add(idv)
            else:
                dead.add(idv)
        free = set(range(lo, hi + 1)) - used
        print(f"\n== {table:11s} limit {maximum} (akceptowane {lo}..{hi}), sekcje {cfg['sections']}")
        print(f"   użyte  : {compact(used)}  ({len(used)}/{hi - lo + 1})")
        print(f"   wolne  : {compact(free)}" + ("" if free else "  (brak!)"))
        if dead:
            print(f"   odsiane: {compact(dead)}  <- exe NIE wczyta tych wpisów")
        if missing:
            print(f"   sekcje bez id: {missing}")
        if table == "tribes":
            # ciekawe: wieś 42 w tribetypes.ini? TRIBE_MAX=42 -> wolne 42? sprawdzamy poniżej
            pass
    return 0


# --------------------------------------------------------------------------
# Walidacja krzyżowa
# --------------------------------------------------------------------------


class Report:
    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.infos: list[str] = []

    def e(self, code: str, msg: str):
        self.errors.append(f"[E] {code}: {msg}")

    def w(self, code: str, msg: str):
        self.warnings.append(f"[W] {code}: {msg}")

    def i(self, code: str, msg: str):
        self.infos.append(f"[I] {code}: {msg}")

    def emit(self):
        for line in self.errors + self.warnings + self.infos:
            print(line)
        print(f"\npodsumowanie: {len(self.errors)} błędów, {len(self.warnings)} ostrzeżeń, {len(self.infos)} info")
        return 1 if self.errors else 0


def used_ids(recs: list[dict[str, list[list[str]]]], id_key: str) -> dict[int, list[int]]:
    """id -> indeksy sekcji w recs (wykrywanie duplikatów)."""
    out: dict[int, list[int]] = {}
    for i, rec in enumerate(recs):
        toks = rec.get(id_key)
        idv = int0(toks[0]) if toks else None
        if idv is not None:
            out.setdefault(idv, []).append(i)
    return out


def validate(root: Path, cif2txt: Path | None, args) -> int:
    rep = Report()
    defines = load_defines(root)
    lang = args.lang

    def lim_of(name: str) -> int:
        return limit_of(defines, name)

    # --- wczytaj wszystkie tabele -------------------------------------------------
    data: dict[str, list[dict[str, list[list[str]]]]] = {}
    for table in TABLES:
        try:
            data[table] = load_table_records(root, table, cif2txt)
        except (FileNotFoundError, RuntimeError) as e:
            rep.e("LOAD", f"tabela '{table}': {e}")
            data[table] = []

    # zakresy dostępnych typów
    ranges = {
        t: valid_range(lim_of(TABLES[t]["maxdef"])) for t in TABLES
    }

    def rng_set(table: str) -> set[int]:
        lo, hi = ranges[table]
        return set(range(lo, hi + 1))

    # --- HOMES: logika ------------------------------------------------------------
    houses = data["houses"]
    h_ids = used_ids(houses, "logictype")
    h_lo, h_hi = ranges["houses"]
    for idv, idxs in sorted(h_ids.items()):
        src = f"houses.ini #{idxs[0]}"
        if not (h_lo <= idv <= h_hi):
            rep.e("H-DEAD", f"logictype {idv} poza {h_lo}..{h_hi} -> exe odsiewa (martwy wpis) [{src}]")  # test akceptacyjny: 55
    for idv, idxs in h_ids.items():
        if len(idxs) > 1:
            rep.e("H-DUP", f"logictype {idv} zdefiniowany {len(idxs)} razy: sekcje {idxs}")

    # refs z houses
    jobs_ok = rng_set("jobs")
    goods_ok = rng_set("goods")
    veh_ok = rng_set("vehicles")
    main_hi = lim_of("HOUSE_MAIN_TYPE_MAXIMUM") - 1
    for i, rec in enumerate(houses):
        idv = int0(rec.get("logictype", [[]])[0]) if rec.get("logictype") else None
        tag = f"house#{idv}" if idv is not None else f"house section #{i}"
        try:
            for key in ("logicworker",):
                for toks in rec.get(key, []):
                    job = int0(toks, 0)
                    if job is not None and job not in jobs_ok:
                        rep.e("H-JOB", f"{tag}: {key} {job} -> brak zawodu {job} (poza {ranges['jobs']})")
        except Exception:
            pass
        for key in ("logicstock", "logicproduction"):
            for toks in rec.get(key, []):
                g = int0(toks, 0)
                if g is not None and g not in goods_ok:
                    rep.e("H-GOOD", f"{tag}: {key} {g} -> brak surowca {g} (poza {ranges['goods']})")
        for key in ("logicvehicletype",):
            for toks in rec.get(key, []):
                v = int0(toks, 0)
                if v is not None and v not in veh_ok:
                    rep.e("H-VEH", f"{tag}: {key} {v} -> brak pojazdu {v} (poza {ranges['vehicles']})")
        for toks in rec.get("logicmaintype", []):
            mt = int0(toks, 0)
            if mt is not None and not (1 <= mt <= main_hi):
                rep.e("H-MAIN", f"{tag}: logicmaintype {mt} poza 1..{main_hi}")

    # --- GFXHOUSE ------------------------------------------------------------
    gfx_path = root / GFX_HOUSES_PATH
    gfx_house_ids: dict[int, list[int]] = {}
    gfx_recs: list[str] = []
    if gfx_path.is_file():
        for s in parse_text(read_text(gfx_path)):
            if s.name != "GfxHouse":
                continue
            d = s.items()
            lt = d.get("LogicType")
            if not lt:
                continue
            # Format: LogicType <0> <id_budynku>  (patrz .ai/docs/typy-budynkow-surowcow.md)
            hid = int0(lt[0], 1)
            if hid is None:
                gfx_recs.append("?")
                continue
            gfx_house_ids.setdefault(hid, []).append(len(gfx_recs))
            gfx_recs.append(f"GfxHouse #{hid}")
            # koszty budowy: <0> <good> [qty] ... (pomijamy nagłówek)
            for toks in d.get("LogicConstructionGoods", []):
                for g in (int0(toks, i) for i in range(1, len(toks))):
                    if g is not None and g != 0 and g not in goods_ok:
                        rep.e("GFX-GOOD", f"GfxHouse#{hid}: LogicConstructionGoods {g} -> brak surowca")
            for toks in d.get("gfxoverlaylandscape", []):
                ls = int0(toks, 0)
                if ls is None or ls == 0:
                    continue
                lo, hi = ranges["landscapes"]
                if not (lo <= ls <= hi):
                    rep.e("GFX-LS", f"GfxHouse#{hid}: gfxoverlaylandscape {ls} poza {lo}..{hi}")
            # LogicTribeType to warstwa/wariant grafiki (1,2,3,4,7), NIE id plemienia
            for toks in d.get("LogicTribeType", []):
                ttv = int0(toks, 0)
                if ttv is not None and ttv not in (1, 2, 3, 4, 7):
                    rep.w("GFX-TRIBE", f"GfxHouse#{hid}: LogicTribeType {ttv} poza znanymi warstwami {{1,2,3,4,7}}")
    else:
        rep.e("GFX-NO", f"brak pliku {GFX_HOUSES_PATH}")

    house_set = set(h_ids)
    for hid, idxs in sorted(gfx_house_ids.items()):
        if hid not in house_set:
            rep.w("GFX-ORPHAN", f"GfxHouse#{hid} bez sekcji logiki w houses.ini (osierocona grafika)")
    for hid in sorted(house_set):
        if hid < h_lo or hid > h_hi:
            continue  # martwy wpis — już zgłoszony przez H-DEAD
        if hid not in gfx_house_ids:
            rep.w("H-NOGFX", f"logictype {hid} nie ma żadnego [GfxHouse] -> nie ma grafiki/wizualizacji")

    # --- NAZWY (stringstext/objects) ------------------------------------------
    names = {t: load_names(root, t, lang, cif2txt) for t in NAME_PATHS}
    for t in ("houses", "goods", "jobs", "tribes", "vehicles"):
        nm = names[t]
        if t == "houses":
            used = {idv for idv in h_ids if (h_lo <= idv <= h_hi)}
        else:
            cfg = TABLES[t]
            used = {u for rec in data[t] if rec.get(cfg["id_key"])
                    for u in (int0(rec.get(cfg["id_key"], [[]])[0]),) if u is not None}
        for idv in sorted(used):
            if idv not in nm:
                rep.w("NAME", f"{t}: brak nazwy (stringn) dla typu {idv}")
    for idv in sorted(set(names["houses"]) - house_set):
        if idv != 0:
            rep.i("NAME-UNUSED", f"houses: nazwa dla typu {idv}, którego nie ma w logice (stringstext)")

    # --- Tabele pozostałe: zakresy + duplikaty ---------------------------------
    for t in ("goods", "weapons", "vehicles", "jobs", "armor", "tribes", "landscapes"):
        cfg = TABLES[t]
        lo, hi = ranges[t]
        used = used_ids(data[t], cfg["id_key"])
        for idv, idxs in sorted(used.items()):
            if not (lo <= idv <= hi):
                rep.e(f"{t.upper()}-RANGE", f"{t}: id {idv} poza {lo}..{hi}")
            if len(idxs) > 1 and t != "weapons":
                rep.e(f"{t.upper()}-DUP", f"{t}: id {idv} zdefiniowany {len(idxs)} razy")
        missing = [i for i, rec in enumerate(data[t]) if not rec.get(cfg["id_key"])]
        if missing:
            rep.e(f"{t.upper()}-NOKEY", f"{t}: sekcje bez klucza '{cfg['id_key']}': {missing}")

    # --- BROŃ: (tribetype,type) + refs -----------------------------------------
    wpn_combo: dict[tuple[int, int], int] = {}
    tribe_range = ranges["tribes"]
    for rec in data["weapons"]:
        tr = int0(rec.get("tribetype", [[]])[0]) if rec.get("tribetype") else None
        ty = int0(rec.get("type", [[]])[0]) if rec.get("type") else None
        if tr is not None and not (tribe_range[0] <= tr <= tribe_range[1]):
            rep.e("WPN-TRIBE", f"broń: tribetype {tr} poza {tribe_range}")
        if ty is not None and not (ranges["weapons"][0] <= ty <= ranges["weapons"][1]):
            rep.e("WPN-RANGE", f"broń: type {ty} poza {ranges['weapons']}")
        if ty is not None and tr is not None:
            key = (tr, ty)
            if key in wpn_combo:
                rep.e("WPN-DUP", f"broń: tribetype {tr} type {ty} zdefiniowany 2x")
            wpn_combo[key] = 1
        for key, rng in (("goodtype", goods_ok), ("jobtype", rng_set("jobs"))):
            toks = rec.get(key)
            if not toks:
                continue
            v = int0(toks[0], 0)
            if v is None:
                continue
            if key == "goodtype" and v == 0:
                continue
            if isinstance(rng, set):
                ok = v in rng
            else:
                ok = rng[0] <= v <= rng[1]
            if not ok:
                rep.e("WPN-REF", f"broń: {key} {v} -> brak obiektu (poza zakresem)")

    # --- GOODS: refs do krajobrazów --------------------------------------------
    ls_range = ranges["landscapes"]
    ls_used = used_ids(data["landscapes"], "type")
    ls_set = set(ls_used)
    for i, rec in enumerate(data["goods"]):
        g = int0(rec.get("type", [[]])[0]) if rec.get("type") else None
        tag = f"good#{g}" if g else f"good sec#{i}"
        for key in ("landscapetype", "landscapeToHarvest", "landscapeToPickup", "landscapeToStore"):
            for toks in rec.get(key, []):
                ls = int0(toks, 0)
                if ls is None:
                    continue
                if ls == 0:
                    continue  # 0 = brak (wolno)
                if not (ls_range[0] <= ls <= ls_range[1]):
                    rep.e("GOOD-LS", f"{tag}: {key} {ls} poza {ls_range}")
                elif ls not in ls_set:
                    rep.w("GOOD-LS-UNDEF", f"{tag}: {key} {ls} nie zdefiniowany w landscapetypes")

    return rep.emit()


# --------------------------------------------------------------------------
# decode / limits
# --------------------------------------------------------------------------


def cmd_decode(root: Path, cif2txt: Path | None, args) -> int:
    src = Path(args.file)
    if not src.is_absolute():
        src = root / src
    dst = Path(args.out) if args.out else None
    text = decode_cif(root, src, dst=dst, cif2txt=cif2txt)
    if args.out:
        print(f"zapisano: {dst}")
    else:
        sys.stdout.write(text)
    return 0


def cmd_limits(root: Path, cif2txt: Path | None, args) -> int:
    defines = load_defines(root)
    for t, cfg in TABLES.items():
        mx = limit_of(defines, cfg["maxdef"])
        lo, hi = valid_range(mx)
        print(f"{t:12s} {cfg['maxdef']:28s} {mx:4d}  akceptowane {lo}..{hi}")
    for aux in AUX_DEFINES:
        mx = limit_of(defines, AUX_DEFINES[aux])
        print(f"{aux:12s} {AUX_DEFINES[aux]:28s} {mx:4d}")
    return 0


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------




def use_free_slots(root: Path, cif2txt: Path | None, args) -> int:
    defines = load_defines(root)
    print("wolne sloty (wg inspect):")
    for table, cfg in TABLES.items():
        maximum = limit_of(defines, cfg["maxdef"])
        lo, hi = valid_range(maximum)
        try:
            recs = load_table_records(root, table, cif2txt)
        except Exception as e:
            print(f"  {table}: błąd {e}")
            continue
        used = set()
        for rec in recs:
            toks = rec.get(cfg["id_key"])
            idv = int0(toks[0]) if toks else None
            if idv is not None and lo <= idv <= hi:
                used.add(idv)
        free = sorted(set(range(lo, hi+1)) - used)
        if free:
            print(f"  {table:9s}: {compact(set(free))}")
        else:
            print(f"  {table:9s}: brak")
    return 0


def _find_house_section_by_id(root: Path, idv: int, cif2txt: Path | None) -> tuple[Path, str, int, int, str] | None:
    """Zwróć (path, text, s,e,block) dla houses.ini/cif zawierającego logictype idv."""
    cfg = TABLES["houses"]
    p = first_existing(root, cfg["paths"])
    if p is None:
        return None
    if p.suffix.lower() == ".cif":
        text = decode_cif(root, p, cif2txt=cif2txt)
    else:
        text = _read_raw(p)
    res = _find_section_containing(text, cfg["sections"][0], lambda b: re.search(r"(^|\n|\r)\s*(?:%02%)?logictype\s+" + str(idv) + r"\b", b, re.M))
    if res is None:
        return None
    s,e,b = res
    return (p,text,s,e,b)


def _find_gfxhouse_by_id(root: Path, idv: int) -> tuple[Path, str, int, int, str] | None:
    p = root / GFX_HOUSES_PATH
    if not p.is_file():
        return None
    text = _read_raw(p)
    res = _find_section_containing(text, "GfxHouse", lambda b: re.search(r"(^|\n|\r)\s*LogicType\s+0\s+" + str(idv) + r"\b", b, re.M))
    if res is None:
        return None
    s,e,b = res
    return (p,text,s,e,b)


def _has_table_id(text: str, section: str, id_key: str, idv: int) -> bool:
    """Czy w tabeli (blokach sekcji) jest już wpis o podanym id?"""
    return _find_section_containing(
        text, section,
        lambda b: re.search(r"(^|\n|\r)\s*(?:%02%)?" + re.escape(id_key) + r"\s+" + str(idv) + r"\b",
                            b, re.M),
    ) is not None


def _clone_names_pair(p: Path, from_id: int, to_id: int, name: str | None = None) -> str:
    """Sklonuj w pliku nazw parę wpisów: `stringn <id> "..."` + kolejna linia `string "..."` (lm.).

    Idempotentne: gdy `stringn <to_id>` już jest - nic nie zmieniamy.
    Wstawia przed <CULTURES_CIF_END>, jeśli plik ma taki trailer (jak goods.ini).
    """
    data = p.read_bytes()
    text = decode_bytes(data)
    if re.search(r"(^|\n|\r)\s*stringn\s+" + str(to_id) + r"\b", text):
        return f"[=] stringn {to_id} już istnieje w {p} -> pomijam"
    m = re.search(r"(^|\n|\r)([^\S\n]*stringn\s+" + str(from_id) + r"\b[^\n]*)", text)
    if not m:
        return f"[W] brak stringn {from_id} w {p} -> pomijam nazwy"
    singular = _clone_key_line(m.group(2).strip(), "stringn", from_id, to_id)
    plural = None
    m2 = re.match(r"\r?\n([^\S\n]*string\s+\"[^\r\n]*)", text[m.end():])
    if m2:
        plural = m2.group(1).strip()
    if name:
        singular = re.sub(r'"[^"]*"', '"' + name + '"', singular, count=1)
        if plural:
            plural = re.sub(r'"[^"]*"', '"' + name + '"', plural, count=1)
    chunk = singular + (("\n" + plural) if plural else "")
    before = b"<CULTURES_CIF_END>" if b"<CULTURES_CIF_END>" in data else None
    bak = _append_raw(p, chunk, before=before)
    lm = " + lm" if plural else ""
    return f"[OK] Dodano stringn {to_id}{lm} do {p} (bak {bak})"


def clone_house(root: Path, cif2txt: Path | None, args: argparse.Namespace) -> int:
    try:
        from_id = int(args.from_id)
        to_id = int(args.to_id)
    except (TypeError, ValueError):
        print("[E] --from/--to muszą być liczbami")
        return 2
    if from_id == to_id:
        print("[E] --from i --to muszą się różnić")
        return 2
    name = (getattr(args, "name", None) or "").strip() or None
    cfg = TABLES["houses"]
    section = cfg["sections"][0]
    p = first_existing(root, cfg["paths"])
    if p is None:
        print("[E] Brak houses.ini/cif")
        return 1
    if p.suffix.lower() == ".cif":
        text = decode_cif(root, p, cif2txt=cif2txt)
    else:
        text = _read_raw(p)
    res = _find_section_containing(
        text, section,
        lambda b: re.search(r"(^|\n|\r)\s*logictype\s+" + str(from_id) + r"\b", b, re.M))
    if res is None:
        print(f"[E] Nie znalazłem [logichousetype] z logictype {from_id}")
        return 1
    s, e, b = res

    # 1) typ logiki -----------------------------------------------------------
    if _has_table_id(text, section, "logictype", to_id):
        print(f"[=] logictype {to_id} już istnieje w {p} -> pomijam")
    else:
        bnew = _clone_block_id(b, "logictype", from_id, to_id)
        if bnew is None:
            print(f"[E] Nie udało się podmienić logictype {from_id} -> {to_id}")
            return 1
        # unikalny debugname - mapy odwołują się do niego (np. goal "BuildHouses" "...")
        dbg = (name or f"dom test {to_id}").lower()
        if re.search(r'(^|\n|\r)\s*debugname\s+"' + re.escape(dbg) + r'"', text, re.M):
            dbg = f"{dbg} {to_id}"
        bnew = re.sub(r'(^|\n)([^\S\n]*debugname\s+")[^"]*(")',
                      lambda m: m.group(1) + m.group(2) + dbg + m.group(3), bnew, count=1)
        bak = _append_raw(p, bnew)
        print(f"[OK] Dodano [logichousetype] logictype {from_id} -> {to_id} "
              f"(debugname \"{dbg}\") do {p} (bak {bak})")

    # 2) nazwy PL (stringn + liczba mnoga) ------------------------------------
    for rel in NAME_PATHS["houses"]:
        p2 = root / rel
        if p2.is_file():
            print(_clone_names_pair(p2, from_id, to_id, name))
            break

    # 3) [GfxHouse] -----------------------------------------------------------
    gfx = _find_gfxhouse_by_id(root, from_id)
    if gfx is None:
        print(f"[W] brak [GfxHouse] dla LogicType 0 {from_id} -> nowy typ bez grafiki")
    else:
        gp, gtext, gs, ge, gblock = gfx
        if _find_gfxhouse_by_id(root, to_id) is not None:
            print(f"[=] [GfxHouse] dla LogicType 0 {to_id} już istnieje -> pomijam")
        else:
            gnew = _clone_block_id(gblock, "LogicType 0", from_id, to_id)
            if gnew is None:
                print(f"[W] nie udało się podmienić LogicType 0 {from_id} -> {to_id}")
            else:
                editname = name or f"Dom TEST {to_id}"
                gnew = re.sub(r'(^|\n)([^\S\n]*EditName\s+")[^"]*(")',
                              lambda m: m.group(1) + m.group(2) + editname + m.group(3),
                              gnew, count=1)
                bakg = _append_raw(gp, gnew)
                print(f"[OK] Dodano [GfxHouse] dla LogicType 0 {to_id} "
                      f"(EditName \"{editname}\") do {gp} (bak {bakg})")
    return 0


def clone_good(root: Path, cif2txt: Path | None, args) -> int:
    try:
        from_id = int(args.from_id)
        to_id = int(args.to_id)
    except Exception:
        print("--from/--to wymagają liczby")
        return 2
    if from_id == to_id:
        print("[E] --from i --to muszą się różnić")
        return 2
    cfg = TABLES["goods"]
    src = first_existing(root, cfg["paths"])
    if src is None:
        print("brak pliku goodtypes")
        return 1
    # zawsze piszemy do .ini (loader: ini > cif); .cif jest binarny i nie go nie ruszamy
    dst = root / cfg["paths"][0] if src.suffix.lower() == ".cif" else src
    p = dst
    if dst.is_file():
        text = _read_raw(dst)
    else:
        text = decode_cif(root, src, cif2txt=cif2txt)
        print(f"[i] {dst.name} nie istnieje - tworzę na podstawie {src.name}")
    res = _find_section_containing(text, cfg["sections"][0], lambda b: re.search(r"(^|\n|\r)\s*(?:%02%)?type\s+" + str(from_id) + r"\b", b, re.M))
    if res is None:
        print(f"nie znaleziono goodtype {from_id}")
        return 1
    s,e,b = res
    if _find_section_containing(text, cfg["sections"][0], lambda b2: re.search(r"(^|\n|\r)\s*(?:%02%)?type\s+" + str(to_id) + r"\b", b2, re.M)) is not None:
        print(f"[=] goodtype {to_id} już istnieje w {p} -> pomijam")
        return 0
    bnew = _clone_section_block(b, "type", from_id, to_id)
    if bnew is None:
        print(f"[E] nie udało się podmienić type {from_id} -> {to_id} w bloku [goodtype]")
        return 1
    tnew = _append_block(text, bnew)
    _write_raw(p, tnew)
    print(f"goods: dodano type {to_id} (sklon z {from_id}) -> {p}")
    # nazwy (stringn + liczba mnoga)
    name = (getattr(args, "name", None) or "").strip() or None
    lang = getattr(args, "lang", "pol") or "pol"
    for rel in NAME_PATHS["goods"]:
        cand = root / (rel % lang)
        if cand.suffix.lower() == ".cif":
            # .cif jest binarny; loader ma priorytet ini > cif, więc celujemy w .ini
            cand = cand.with_suffix(".ini")
        if cand.is_file():
            print(_clone_names_pair(cand, from_id, to_id, name))
            break
    else:
        print(f"[W] nie znaleziono pliku nazw surowców - dopisz ręcznie stringn {to_id}")
    return 0



def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    ap = argparse.ArgumentParser(prog="modkit", description="Narzędzia moderskie Cultures (CN.PLMOD) — Etap A")
    ap.add_argument("--root", default=str(ROOT_DEFAULT), help="katalog gry (domyślnie: dwie poziomy w górę od skryptu)")
    ap.add_argument("--cif2txt", default=None, help="ścieżka do cif2txt.exe (domyślnie: mapper tools\\cif2txt.exe)")
    ap.add_argument("--lang", default="pol", help="język tekstów (domyślnie pol)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("inspect", help="inwentarz tabel: użyte/wolne/odsiane typy")
    sub.add_parser("validate", help="walidacja krzyżowa (błędy/ostrzeżenia)")
    sub.add_parser("limits", help="limity z logicdefines.inc")
    sub.add_parser("use-free-slots", help="pokaż wolne sloty wg bieżących tabel")

    p_d = sub.add_parser("decode", help="dekoduj .cif do tekstu")
    p_d.add_argument("file", help="plik .cif (względnie do roota gry albo ścieżka bezwzględna)")
    p_d.add_argument("--out", default=None, help="plik wyjściowy (domyślnie stdout)")

    p_ch = sub.add_parser("clone-house", help="sklonuj budynek (houses + gfx + nazwy)")
    p_ch.add_argument("--from", dest="from_id", required=True)
    p_ch.add_argument("--to", dest="to_id", required=True)
    p_ch.add_argument("--name", default=None,
                      help="nazwa nowego typu (stringn/EditName); domyślnie 'Dom TEST <to>'")

    p_cg = sub.add_parser("clone-good", help="sklonuj surowiec (goodtypes + nazwy)")
    p_cg.add_argument("--from", dest="from_id", required=True)
    p_cg.add_argument("--to", dest="to_id", required=True)
    p_cg.add_argument("--name", default=None, help="nazwa nowego surowca (domyślnie kopiowana)")

    p_th = sub.add_parser("template-house", help="szablon domu")
    p_th.add_argument("--id", dest="id", required=True)
    p_th.add_argument("--name", default=None, help="nazwa budynku (domyślnie 'Nowy budynek')")
    p_tg = sub.add_parser("template-good", help="szablon surowca")
    p_tg.add_argument("--id", dest="id", required=True)
    p_tg.add_argument("--name", default=None, help="nazwa surowca (domyślnie 'Nowy surowiec')")

    args = ap.parse_args(argv)
    root = Path(args.root)
    cif2txt = Path(args.cif2txt) if args.cif2txt else None

    if args.cmd == "inspect":
        return inspect(root, cif2txt, args)
    if args.cmd == "validate":
        return validate(root, cif2txt, args)
    if args.cmd == "limits":
        return cmd_limits(root, cif2txt, args)
    if args.cmd == "use-free-slots":
        return use_free_slots(root, cif2txt, args)
    if args.cmd == "decode":
        return cmd_decode(root, cif2txt, args)
    if args.cmd == "clone-house":
        return clone_house(root, cif2txt, args)
    if args.cmd == "clone-good":
        return clone_good(root, cif2txt, args)
    if args.cmd == "template-house":
        return cmd_template_house(root, cif2txt, args)
    if args.cmd == "template-good":
        return cmd_template_good(root, cif2txt, args)
    return 2


# ---------------------------------------------------------------------------
# Etap E: szablony (template-house / template-good)
# UWaga: ten blok musi znajdować SIĘ PRZED `if __name__ == "__main__"` na końcu
# pliku - wcześniej definicje template-* stały po punkcie wejścia, więc komendy
# template-* kończyły się NameError.
# ---------------------------------------------------------------------------

# Szablony w stylu gry: linie W BLOKU ciągłe (bez pustych linii wewnątrz) -
# pusta linia oddziela wyłącznie bloki. Wcześniejsze wersje miały \n\n między
# polami i po dopisaniu powstawał blok rozstrzelony pustymi liniami.
TEMPLATE_HOUSE = """[logichousetype]
debugname "{dbg}"
logictype {to_id}
logicmaintype 3
debugcolor 0 128 0
"""

TEMPLATE_GFX = """[GfxHouse]
EditName "{name}"
EditGroups "none"
LogicMaximumSize 1
LogicType 0 {to_id}
LogicTribeType 1
logichitpoints 0 100000
"""

TEMPLATE_GOOD = """[goodtype]
type {to_id}
name "{name}"
category 1
isresource 1
debugcolor 0 128 0
"""

# para wpisów w plikach nazw: stringn (lm. r.) + string (liczba mnoga)
TPL_NAMES_H = '''stringn {to_id} "{name}"
string "{name}"
'''

TPL_NAMES_G = '''stringn {to_id} "{name}"
string "{name}"
'''


def _append_file(p: Path, s: str):
    """Zachowane dla kompatybilności - teraz przez _append_raw (bez podwójnych CR)."""
    _append_raw(p, s)


def _add_names_pair(p: Path, to_id: int, name: str) -> str:
    """Dopisz w pliku nazw parę `stringn <id> "..."` + `string "..."` (idempotentnie)."""
    data = p.read_bytes() if p.is_file() else b""
    text = decode_bytes(data)
    if re.search(r"(^|\n|\r)\s*stringn\s+" + str(to_id) + r"\b", text):
        return f"[=] stringn {to_id} już istnieje w {p} -> pomijam"
    chunk = TPL_NAMES_H.format(to_id=to_id, name=name).strip("\n")
    before = b"<CULTURES_CIF_END>" if b"<CULTURES_CIF_END>" in data else None
    return f"[OK] Dodano stringn {to_id} do {p} (bak {_append_raw(p, chunk, before=before)})"


def cmd_template_house(root: Path, _cif, args) -> int:
    to_id = int(args.id)
    name = (getattr(args, "name", None) or "").strip() or "Nowy budynek"
    dbg = name.lower()

    # 1) typ logiki
    p = root / "CN.PLMOD" / "types" / "houses.ini"
    text = _read_raw(p) if p.is_file() else ""
    if _has_table_id(text, "logichousetype", "logictype", to_id):
        print(f"[=] logictype {to_id} już istnieje w {p} -> pomijam")
    else:
        if text and re.search(r'(^|\n|\r)\s*debugname\s+"' + re.escape(dbg) + r'"', text, re.M):
            dbg = f"{dbg} {to_id}"  # debugname musi być unikalne (odwołują się do niego mapy)
        bak = _append_raw(p, TEMPLATE_HOUSE.format(to_id=to_id, dbg=dbg))
        print(f"[OK] Dodano szablon logictype {to_id} (debugname \"{dbg}\") do {p} (bak {bak})")

    # 2) grafika
    pg = root / "CN.PLMOD" / "budynki12" / "houses" / "houses.ini"
    if _find_gfxhouse_by_id(root, to_id) is not None:
        print(f"[=] [GfxHouse] dla LogicType 0 {to_id} już istnieje -> pomijam")
    else:
        bak = _append_raw(pg, TEMPLATE_GFX.format(to_id=to_id, name=name))
        print(f"[OK] Dodano szablon [GfxHouse] dla LogicType 0 {to_id} do {pg} (bak {bak})")

    # 3) nazwy
    pn = root / "CN.PLMOD" / "stringstext" / "gameobjects" / "houses.ini"
    print(_add_names_pair(pn, to_id, name))
    print(f"[i] szablon domu {to_id} gotowy (bez overlayu exe odsieje id > 54)")
    return 0


def cmd_template_good(root: Path, _cif, args) -> int:
    to_id = int(args.id)
    name = (getattr(args, "name", None) or "").strip() or "Nowy surowiec"
    cfg = TABLES["goods"]
    src = first_existing(root, cfg["paths"])
    dst = root / cfg["paths"][0] if (src is None or src.suffix.lower() == ".cif") else src
    text = _read_raw(dst) if dst.is_file() else (decode_cif(root, src, cif2txt=_cif) if src else "")
    if dst.is_file() and re.search(r"(^|\n|\r)\s*type\s+" + str(to_id) + r"\b", text, re.M):
        print(f"[=] goodtype {to_id} już istnieje w {dst} -> pomijam")
    else:
        if not dst.is_file() and src:
            print(f"[i] {dst.name} nie istnieje - szablon na podstawie {src.name}")
        bak = _append_raw(dst, TEMPLATE_GOOD.format(to_id=to_id, name=name))
        print(f"[OK] Dodano szablon [goodtype] type {to_id} do {dst} (bak {bak})")

    lang = getattr(args, "lang", "pol") or "pol"
    cand = [
        root / "CN.PLMOD" / "stringstext" / "gameobjects" / "goods_pol.ini",
        root / "CN.PLMOD" / "stringstext" / "gameobjects" / "goods.ini",
        root / f"Data\\text\\{lang}\\strings\\gameobjects\\goods.ini",
    ]
    pn = next((c for c in cand if c.is_file()), cand[-1])
    print(_add_names_pair(pn, to_id, name))
    return 0


if __name__ == "__main__":
    sys.exit(main())
