#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Normalizacja i naprawa plikow .ini CNMX.

Co robi:
  1. Odtwarza utracone litery (U+FFFD) przez dopasowanie slowa do oryginalu
     (per-id ze zrodla: .orig lub skonwertowany .cif) - bez zmiany tresci.
  2. Odwraca podwojne kodowanie (mojibake latin1 -> cp1250).
  3. Normalizuje format: cp1250, CRLF, bez BOM, koncowy CRLF.

Uzycie:
    python ini_normalize.py            # dry-run
    python ini_normalize.py --apply    # zapis z backupem .bak_format_<stamp>
"""
import os
import re
import shutil
import subprocess
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
CIF2TXT = os.path.join(ROOT, 'mapper tools', 'cif2txt.exe')
TMP = os.path.join(os.environ['TEMP'], 'cnmx_fmt')
STAMP = time.strftime('%Y%m%d_%H%M%S')
SKIP = ('.bak', '.orig', '.broken', '.NIEUZYWANY', '.etapc')
TOKEN = re.compile(r'[0-9A-Za-z\u00a0-\uffff]+')
QUOTED = re.compile(r'"([^"\r\n]*)"')

GLOBAL = {}          # szkielet -> set(slowo), z calego korpusu
REPORT = {'files': 0, 'chars': 0, 'mojibake': 0, 'left': [], 'skipped': []}


def skeleton(tok):
    return ''.join(c if ord(c) < 128 else '?' for c in tok)


def add_token(tok):
    if all(ord(c) < 128 for c in tok) or '\ufffd' in tok:
        return
    sk = skeleton(tok)
    if '?' in sk:
        GLOBAL.setdefault(sk, set()).add(tok)


def feed(t):
    for m in QUOTED.finditer(t):
        for tok in TOKEN.findall(m.group(1)):
            add_token(tok)


def decode_any(b):
    if b'\xef\xbf\xbd' in b:
        return b.decode('utf-8', 'replace'), 'utf-8-utrata'
    if b[:3] == b'\xef\xbb\xbf':
        return b.decode('utf-8-sig'), 'utf-8-bom'
    try:
        t = b.decode('utf-8')
        if any(x > 127 for x in b):
            return t, 'utf-8'
        return t, 'ascii'
    except UnicodeDecodeError:
        return b.decode('cp1250'), 'cp1250'


# ---------------------------------------------------------------- corpus
def build_corpus():
    os.makedirs(TMP, exist_ok=True)
    n_cif = n_ini = 0
    for dp, dn, fn in os.walk(os.path.join(ROOT, 'Data', 'text')):
        for f in fn:
            if not f.lower().endswith('.cif'):
                continue
            dst = os.path.join(TMP, f + '.txt')
            if not os.path.exists(dst):
                subprocess.run([CIF2TXT, 'C', os.path.join(dp, f), dst], capture_output=True)
            if os.path.exists(dst):
                feed(open(dst, 'rb').read().decode('cp1250', 'replace'))
                n_cif += 1
    for sub in ('Data', 'CN.PLMOD'):
        for dp, dn, fn in os.walk(os.path.join(ROOT, sub)):
            for f in fn:
                if not f.lower().endswith('.ini') or any(s in f for s in SKIP):
                    continue
                t, _ = decode_any(open(os.path.join(dp, f), 'rb').read())
                if '\ufffd' not in t:
                    feed(t)
                    n_ini += 1
    print(f'Korpus: {n_cif} .cif + {n_ini} .ini, slow: {len(GLOBAL)}')


# --------------------------------------------------- id -> tekst (zrodla)
def parse_strings(t):
    """id -> {'sing':..., 'plur':...} z formatu CIF/TXT/INI (ignoruje %01%/%02%)."""
    out = {}
    cur = None
    for line in t.splitlines():
        s = re.sub(r'^%0[12]%?', '', line.strip())
        m = re.match(r'stringn\s+(\d+)\s+"(.*)"\s*$', s)
        if m:
            cur = int(m.group(1))
            out.setdefault(cur, {})['sing'] = m.group(2)
            continue
        m = re.match(r'string\s+"(.*)"\s*$', s)
        if m and cur is not None:
            out.setdefault(cur, {}).setdefault('plur', m.group(1))
    return out


def convert_cif(cif_path):
    dst = os.path.join(TMP, os.path.basename(cif_path) + '.txt')
    if not os.path.exists(dst):
        subprocess.run([CIF2TXT, 'C', cif_path, dst], capture_output=True)
    if os.path.exists(dst):
        return parse_strings(open(dst, 'rb').read().decode('cp1250', 'replace'))
    return {}


def find_cif(basename):
    for dp, dn, fn in os.walk(os.path.join(ROOT, 'Data', 'text')):
        for f in fn:
            if f.lower() == basename.lower():
                return os.path.join(dp, f)
    return None


def sources_for(path, text):
    """Zwraca (per_id, opis_zrodla) dla pliku z U+FFFD."""
    alt = []
    orig = path + '.orig'
    if os.path.exists(orig):
        t, _ = decode_any(open(orig, 'rb').read())
        if '\ufffd' not in t:
            alt.append(parse_strings(t))
    base = os.path.basename(path)
    cif = find_cif(base[:-4] + '.cif')
    if cif:
        alt.append(convert_cif(cif))
    if not alt:
        return None, None
    merged = {}
    for src in alt:
        for sid, vals in src.items():
            for slot, v in vals.items():
                merged.setdefault(sid, {}).setdefault(slot, v)
    return merged, [os.path.basename(a) for a in ([orig] if os.path.exists(orig) else [])] + ([os.path.basename(cif)] if cif else [])


# ------------------------------------------------------------- naprawa
def repair_value(val, sid, slot, per_id, fname=''):
    changes = []

    def fix(m):
        tok = m.group(0)
        if '\ufffd' not in tok:
            return tok
        sk = skeleton(tok)
        cands = set()
        src = ''
        if per_id and sid in per_id:
            src = per_id[sid].get(slot) or per_id[sid].get('sing') or ''
            cands = {w for w in TOKEN.findall(src) if skeleton(w) == sk}
            if not cands and src:
                # fallback: seria U+FFFD moze odpowiadac roznej liczbie liter (np. "Wol" -> "Wol")
                parts = re.split(r'\ufffd+', tok)
                pat = '^' + '.+'.join(re.escape(x) for x in parts) + '$'
                rx = re.compile(pat)
                cands = {w for w in TOKEN.findall(src) if rx.match(w)}
        if not cands:
            cands = {w for w in GLOBAL.get(sk, set()) if '\ufffd' not in w}
        if len(cands) == 1:
            good = cands.pop()
            changes.append((tok, good))
            return good
        REPORT['left'].append((fname, sid, tok, sorted(cands)[:4]))
        return tok

    return TOKEN.sub(fix, val), changes


def repair_text(text, per_id, fname=''):
    out = []
    cur = None
    slot = 'sing'
    n = 0
    for line in text.splitlines():
        s = line.strip()
        mv = QUOTED.search(s)
        m = re.match(r'stringn\s+(\d+)\s+"', s)
        if m:
            cur, slot = int(m.group(1)), 'sing'
        elif re.match(r'string\s+"', s):
            slot = 'plur'
        if mv and '\ufffd' in mv.group(1):
            newval, ch = repair_value(mv.group(1), cur, slot, per_id, fname)
            n += len(ch)
            line = line[:mv.start(1)] + newval + line[mv.end(1):]
        out.append(line)
    return '\n'.join(out), n


MOJIBAKE_SPECIAL = {
    '[GfxHouse] - Kwatera G': '[GfxHouse] - Kwatera g\u0142\u00f3wna',
}

SUSPICIOUS = set('ÂÃÄÅ³¶¼¹œŒ¿¯§¬«')


def susp_count(s):
    return sum(1 for c in s if c in SUSPICIOUS)


def encodable(s):
    try:
        s.encode('cp1250')
        return True
    except UnicodeEncodeError:
        return False


def strip_unencodable(s):
    out = []
    for c in s:
        try:
            c.encode('cp1250')
            out.append(c)
        except UnicodeEncodeError:
            pass
    return ''.join(out)


def fix_mojibake(text):
    out, n = [], 0
    for line in text.splitlines():
        susp = susp_count(line)
        if not susp and encodable(line):
            out.append(line)
            continue

        # 1. nazwa assetu (gfxoverlaylandscape) - usuwamy tylko znaki niekodowalne
        if line.lstrip().startswith('gfxoverlaylandscape'):
            cleaned = strip_unencodable(line)
            if cleaned != line:
                n += 1
                REPORT['skipped'].append(('asset-oczyszczony', line + ' -> ' + cleaned))
            out.append(cleaned)
            continue

        # 2. komentarz z nazwa budynku
        if line.startswith('[GfxHouse] - '):
            fixed = None
            try:
                fixed = line.encode('latin1').decode('cp1250')
            except UnicodeEncodeError:
                for k, v in MOJIBAKE_SPECIAL.items():
                    if line.startswith(k):
                        fixed = v
                        break
            if fixed is None:
                cleaned = strip_unencodable(line)
                if cleaned != line:
                    n += 1
                    REPORT['skipped'].append(('komentarz-oczyszczony', line + ' -> ' + cleaned))
                out.append(cleaned)
                continue
            if fixed != line:
                n += 1
            out.append(fixed)
            continue

        # 3. zwykle odwrocenie podwojnego kodowania (tylko jesli poprawia sytuacje)
        if susp:
            try:
                fixed = line.encode('latin1').decode('cp1250')
            except UnicodeEncodeError:
                out.append(line)
                REPORT['skipped'].append(('mojibake-nieodwracalny', line))
                continue
            if susp_count(fixed) < susp:
                n += 1
                line = fixed
        out.append(strip_unencodable(line) if not encodable(line) else line)
    return '\n'.join(out), n


def normalize(text):
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    if not text.endswith('\n'):
        text += '\n'
    return text.replace('\n', '\r\n')


def main():
    apply = '--apply' in sys.argv
    build_corpus()
    files = []
    for sub in ('Data', 'CN.PLMOD'):
        for dp, dn, fn in os.walk(os.path.join(ROOT, sub)):
            for f in fn:
                if f.lower().endswith('.ini') and not any(s in f for s in SKIP):
                    files.append(os.path.join(dp, f))

    for p in sorted(files):
        b = open(p, 'rb').read()
        t, enc = decode_any(b)
        rel = os.path.relpath(p, ROOT)
        orig_t = t
        notes = []

        if '\ufffd' in t:
            per_id, srcs = sources_for(p, t)
            if per_id is None:
                REPORT['skipped'].append((rel, 'brak zrodla dla U+FFFD'))
                continue
            t, n = repair_text(t, per_id, os.path.basename(p))
            REPORT['chars'] += n
            notes.append(f'odtworzone znaki: {n} (zrodlo: {",".join(srcs)})')

        # mojibake: tylko gdy w pliku sa charakterystyczne znaki podwojnego kodowania
        if susp_count(t):
            t, n = fix_mojibake(t)
            REPORT['mojibake'] += n
            notes.append(f'mojibake naprawiony w liniach: {n}')

        out = normalize(t)
        try:
            data = out.encode('cp1250')
        except UnicodeEncodeError as e:
            REPORT['skipped'].append((rel, f'cp1250: {e}'))
            print(f'!! {rel}: POMINIETY ({e})')
            continue

        if data == b:
            continue

        REPORT['files'] += 1
        print(f'== {rel} [{enc} -> cp1250] {len(b)} -> {len(data)} B')
        for n in notes:
            print(f'   {n}')

        if apply:
            bak = p + f'.bak_format_{STAMP}'
            shutil.copy2(p, bak)
            tmp = p + '.tmpfmt'
            open(tmp, 'wb').write(data)
            os.replace(tmp, p)

    print(f'\nRAZEM: plikow zmienionych {REPORT["files"]}, odtworzonych znakow {REPORT["chars"]}, '
          f'linii mojibake {REPORT["mojibake"]}')
    if REPORT['left']:
        print(f'\nNIEROZWIAZANE tokeny: {len(REPORT["left"])}')
        for x in REPORT['left'][:40]:
            print('  ', x)
    if REPORT['skipped']:
        print(f'\nPOMINIETE / DO RECENZJI: {len(REPORT["skipped"])}')
        for x in REPORT['skipped'][:40]:
            print('  ', x)
    if not apply:
        print('\nDRY-RUN — nic nie zapisano. Uzyj --apply.')


if __name__ == '__main__':
    main()
