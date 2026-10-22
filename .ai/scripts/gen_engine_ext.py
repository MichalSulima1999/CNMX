#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_engine_ext.py — generator tabeli Patch[] dla ROZSZERZENIA silnika CN.PLMOD.exe
(Etap 1: relokacja 5 tablic per-plemienia aktora do ogona elementu, stride 0x7F;
 Etap 2: rekord plemienia — rozmiar, koniec tablicy, relokacja 4 baz flag,
 walidatory flag).

Architektura (decyzje z `.ai/docs/plan-rozszerzenie-silnika.md` + `etap0-*`):
  * GROUND TRUTH = SEKWENCYJNY disasm .text (skipdata). Wzorzec/brute-force służy
    tylko jako wskaźnik kandydatów (site'y zgubione przez desync -> RECONCILIATION).
  * RVA = tva(0x1000) + indeks tdata; patchy adresowane RVA (VA = 0x400000 + RVA).

Kategorie:
  A) element stride 0x4A80 -> NEW_ELEM_SIZE   (imul 208 + add 35 + mov 3 = 246)
  B) pula           0x5D200 -> NEW_POOL_SIZE   (37 imm + 7 kuratorowanych disp)
  C) stride surowców 0x42   -> 0x7F            (imul/add/mov, filtr 32-bit)
  D) stride domów    0x37   -> 0x7F            (jw.)
  E1) limity pętli kopiowania cmp 0x42/0x37 -> 0x7F (4 jawne adresy)
  H) Etap 2 — REKORD plemienia: rozmiar 0x1AE08 -> NEW_REC_SIZE, koniec tablicy
     0x468D50 -> NEW_REC_ARREND, relokacja 4 baz (0x50D8/0x511A/0x515C/0x5193)
     na ogon rekordu, 3 walidatory flag -> 0x7F.
  F) relokacja displacency 5 tablic per-plemienia (z mapy sekwencyjnej)
     nowy = NOWA_BAZA + plemię×0x7F + sub; ekskluzje: 0x1581 (inna tablica),
     blok dest goodsB (0x9E79 — code cave Etap 3).
  G) SPECJALNE: tylko raport (code cave / Etap 2 / Etap 4-6).

Uruchomienie:
    python .ai\\scripts\\gen_engine_ext.py [--exe CN.PLMOD.exe] [--out patches_ext.h]
"""
import argparse, struct, sys
from collections import Counter

try:
    import pefile
    from capstone import Cs, CS_ARCH_X86, CS_MODE_32
    from capstone.x86 import X86_OP_IMM, X86_OP_MEM
except ImportError as e:
    sys.exit("Brak zaleznosci: %s (pip install pefile capstone)" % e)

# ===================== nowe stałe ============================================
NEW_GOOD_MAX   = 0x7F
NEW_HOUSE_MAX  = 0x7F
OLD_GOOD_STRIDE  = 0x42
OLD_HOUSE_STRIDE = 0x37
OLD_GOODB_STRIDE = 0x38
NEW_STRIDE       = 0x7F
ARR_N            = 42

OLD_GOODS_A  = 0x1278
OLD_GOODS_A2 = 0x1D4C
OLD_HOUSES_A = 0x2820
OLD_HOUSES_B = 0x3126
OLD_GOODS_B  = 0x3C78
OLD_ELEM_END = 0x4A80

def arr_size(): return ARR_N * NEW_STRIDE          # 0x14D6
NEW_GOODS_A   = OLD_ELEM_END
NEW_GOODS_A2  = NEW_GOODS_A  + arr_size()
NEW_GOODS_B   = NEW_GOODS_A2 + arr_size()
NEW_HOUSES_A  = NEW_GOODS_B  + arr_size()
NEW_HOUSES_B  = NEW_HOUSES_A + arr_size()
NEW_ELEM_SIZE = (NEW_HOUSES_B + arr_size() + 15) & ~15    # 0xB2B0
NEW_POOL_SIZE = 20 * NEW_ELEM_SIZE                         # 0xDF5C0

ELEM_STRIDE_OLD = 0x4A80
POOL_SIZE_OLD   = 0x5D200
# Alokacja puli aktorów używa 0x5D204 = 0x5D200 + 4 (2 site'y zapisu [0x510BC4]
# + dalsze 4 alle: 0x70AC, 0x9B51, 0x9C10, 0x26203). Patchować na NEW_POOL_SIZE + 4.
POOL_ALLOC_OLD  = 0x5D204

# ---- Etap 2: rekord plemienia ---------------------------------------------
# Rekord ma 0x1AE08 B; pola (upakowane): +0x50A0 jobs(56), +0x50D8 surowce A(66),
# +0x511A surowce B(66), +0x515C flagi domów(55), +0x5193 pojazdy(8), od +0x519C dalej.
# Relokacja: 4 tablice flag (A/B/domy/pojazdy) na ogon rekordu; jobs i pola od
# +0x519C (w tym mapa produkcji 0x1492C) zostają na miejscu.
OLD_REC_SIZE  = 0x1AE08
OLD_REC_ARREND = 0x468D50          # baza + 42 × 0x1AE08 (koniec tablicy, offset)
NEW_REC_BASE   = OLD_REC_SIZE      # start ogona
NEW_REC_SUROW_A = NEW_REC_BASE
NEW_REC_SUROW_B = NEW_REC_SUROW_A + NEW_GOOD_MAX
NEW_REC_DOMY    = NEW_REC_SUROW_B + NEW_HOUSE_MAX
# pojazdy (8 B) NA KOŃCU ogona — po PEŁNEJ tablicy domów (0x7F B). Bez rozszerzania (7 szt.).
NEW_REC_VEH     = NEW_REC_DOMY     + NEW_HOUSE_MAX     # 0x1AF85
NEW_REC_SIZE    = (NEW_REC_VEH + 8 + 15) & ~15          # 0x1AF90
# Koniec tablicy rekordów: old 0x468D50 = 42 × 0x1AE08 (baza w obrazie traktowana
# jako 0 w pętli `cmp esi,0x468D50`). Nowy koniec = 42 × NEW_REC_SIZE.
NEW_REC_ARREND  = 42 * NEW_REC_SIZE                 # 0x46CDA0

# (rva, stara baza, nowa baza, opis) — relokacja displacency w rekordzie:
# read: pętla kopiowania; write: walidatory flag. Wszystkie disp32 off=3 (ModRM+..).
REC_DISP = [
    (0x0009E4D, 0x50D8, "surowce A read (copy)"),
    (0x0009E6C, 0x511A, "surowce B read (copy)"),
    (0x0009E89, 0x515C, "flagi domów read (copy)"),
    (0x0009EA8, 0x5193, "pojazdy read (copy)"),
    (0x000142BB, 0x5193, "pojazdy write (guard)"),
    (0x000142FD, 0x515C, "flagi domów write (guard)"),
    (0x0001431E, 0x50D8, "surowce A write (guard)"),
    (0x0001433F, 0x511A, "surowce B write (guard)"),
]
REC_DISP_NEW = {0x50D8: NEW_REC_SUROW_A, 0x511A: NEW_REC_SUROW_B,
                0x515C: NEW_REC_DOMY, 0x5193: NEW_REC_VEH}

# Walidatory flag w rekordzie — imm8 cmp: 0x37/0x42 -> 0x7F (bezpieczne po relokacji).
REC_LIMITS = [
    (0x000142F4, 0x37, NEW_HOUSE_MAX, "flagi domów guard"),
    (0x00014315, 0x42, NEW_GOOD_MAX,  "surowce A guard"),
    (0x00014336, 0x42, NEW_GOOD_MAX,  "surowce B guard"),
]

# 0x14289/0x14292 gateują mapę produkcji [esi + edi*8 + 0x1492C] (nie relokowaną).
# Podniesienie bez rozszerzania mapy = przepełnienie tablicy -> SPECJALNE, bez patchy.
REC_VALIDATOR_PROD = "0x14289/0x14292 gate mapy produkcji 0x1492C (good->house," \
                     " 66 wpisów × 8 B); po relokacji pól flag pozostaje na " \
                     "starym offsecie; podniesienie do 0x7F wymaga rozszerzenia mapy — Etap 4/6."

# E2 z CURATED_CMP_E2 — 0x14289/0x14292 to walidatory MAPY PRODUKCJI (0x1492C),
# NIE flag; podniesienie wymaga Etapu 4/6. Rozdzielamy listę:
#  - aktywne w Etapie 2: 0x142F4/0x14315/0x14336 (REC_LIMITS powyżej)
#  - wstrzymane w Etapie 2: 0x14289/0x14292 (SPECIAL)

ARR_TABLES = [  # nazwa, stara baza, stary stride, symbol nowej bazy
    ("GOODS_A",  OLD_GOODS_A,  OLD_GOOD_STRIDE,  "NEW_GOODS_A"),
    ("GOODS_A2", OLD_GOODS_A2, OLD_GOOD_STRIDE,  "NEW_GOODS_A2"),
    ("GOODS_B",  OLD_GOODS_B,  OLD_GOODB_STRIDE, "NEW_GOODS_B"),
    ("HOUSES_A", OLD_HOUSES_A, OLD_HOUSE_STRIDE, "NEW_HOUSES_A"),
    ("HOUSES_B", OLD_HOUSES_B, OLD_HOUSE_STRIDE, "NEW_HOUSES_B"),
]

# (rva, oczekiwana wartosc, nowa stale, opis) — E1: pętla kopiowania (bezpieczne)
CURATED_CMP_E1 = [
    (0x0009E65, 0x42, NEW_GOOD_MAX,  "copy goodsA loop limit eax"),
    (0x0009E82, 0x42, NEW_GOOD_MAX,  "copy goodsB loop limit eax"),
    (0x0009EA1, 0x37, NEW_HOUSE_MAX, "copy housesA loop limit eax"),
    (0x000A003, 0x37, NEW_HOUSE_MAX, "copy houses2 read loop limit edx"),
]

# E2: 2 walidatory MAPY PRODUKCJI (0x1492C) — wstrzymane do Etapu 4/6.
#     3 walidatory FLAG (0x142F4/0x14315/0x14336) przeniesione do REC_LIMITS
#     (generowane w Etapie 2).
CURATED_CMP_E2 = [
    (0x00014289, 0x37, NEW_HOUSE_MAX, "validator house < max (mapa produkcji 0x1492C)"),
    (0x00014292, 0x42, NEW_GOOD_MAX,  "validator good < max (mapa produkcji 0x1492C)"),
]

# zależne od danych gry (Etap 4/6) — WYŁĄCZONE nawet z raportu patchy; tylko nota.
EXCLUDED_ETAP46 = [
    (0x00014359, 0x37, "tabele 0x14B3C/0x14C08"),
    (0x0001436F, 0x42, "tabele 0x14B3C/0x14C08"),
    (0x000158D5, 0x37, "walker tablic domów 0x624"),
    (0x00015923, 0x37, "walker tablic domów 0x624"),
    (0x00015368, 0x37, "walker/alokacja tablicy domów 0x624 (0x151BC = 0x37*0x624)"),
]

# Fałszywe pozytywy kategorii C/D: imm 0x42/0x37 w imul/add/mov, które NIE są
# stridem — dane gry albo offset UI. Pomijane w generacji, raportowane.
C_D_EXCLUDE = {
    0x00015368: "alokator/walker tablicy domów 0x624 (0x151BC=0x37*0x624); patch bez skali alokacji = przepełnienie",
    0x00036ADD: "dane gry: limit per poziom — sekwencja zapisów 0x37..0x32 do [esi+0x1EC]",
    0x0004C231: "dane gry: limit per poziom — sekwencja zapisów 0x37..0x32 do [esi+0x1EC]",
    0x0005F6DE: "dane gry: inicjalizacja tablicy lokalnej wartościami 0xF/0x37/0x26",
    0x000BD62F: "UI lista: [ebp-8]=Y-offset (0x42, +0x16/iter); bound pętli to cmp @0xBD6C1 (niepatchowany)",
    0x000D89AF: "UI rysowanie: add eax,0x42 = offset pikselowy (kolory 0x64/0xFF, wsp. 0x400)",
    0x000D8AAE: "UI rysowanie: add eax,0x42 = offset pikselowy (kolory 0x64/0xFF, wsp. 0x400)",
}

# 7 zweryfikowanych RAFOWYCH site'ów puli w regionie UI (mapa sekwencyjna je gubi).
# Wszystkie to `cmp dword ptr [reg + 0x5D200], imm` — disp32 na off=2, stareb = 00 D2 05 00.
CURATED_POOL_DISP = [
    0x0003473B, 0x000385C7, 0x00042688, 0x00043DD5,
    0x00046257, 0x0004B1A2, 0x0005BA16,
]

# ===================== wczytywanie PE / sekwencyjny smap =====================
def load_binary(path):
    pe = pefile.PE(path)
    text = [s for s in pe.sections if s.Name.startswith(b'.text')][0]
    data = open(path, 'rb').read()
    toff, tva = text.PointerToRawData, text.VirtualAddress
    tdata = data[toff:toff+text.SizeOfRawData]
    md = Cs(CS_ARCH_X86, CS_MODE_32)
    md.detail = True
    md.skipdata = True
    return pe, data, tdata, toff, tva, md

def build_smap(md, tdata, tva):
    """Sekwencyjny disasm .text (skipdata); zwraca listę (rva, insn) prawdziwych insn."""
    smap = []
    for ins in md.disasm(tdata, tva):
        if ins.id == 0:                       # pseudo-instrukcja skipdata
            continue
        if ins.mnemonic.startswith('.'):      # '.byte' '.word' itp.
            continue
        smap.append((ins.address, ins))
    return smap

def rva2off(tva, toff, rva):
    return rva - tva + toff

def imm_pos(b, value):
    """Pozycja imm (value) w bajtach instrukcji. Zakłada prawą (ostatnią) zgodność."""
    v32 = value & 0xFFFFFFFF
    pat = struct.pack('<I', v32)
    for i in range(len(b)-3, -1, -1):
        if b[i:i+4] == pat:
            return i, 4
    v8 = value & 0xFF
    for i in range(len(b)-1, -1, -1):
        if b[i] == v8:
            return i, 1
    return None, None

def disp_pos(b, disp):
    pat = struct.pack('<I', disp & 0xFFFFFFFF)
    for i in range(len(b)-3, -1, -1):
        if b[i:i+4] == pat:
            return i
    return None

# ===================== agregacja =============================================
class Gen:
    def __init__(self):
        self.patches = []     # (rva, off, size, bytes, desc)
        self.review = []
        self.special = []
    def add(self, rva, off, size, nb, desc):
        key = (rva, off, size)
        if key in [ (p[0], p[1], p[2]) for p in self.patches ]:
            return
        self.patches.append((rva, off, size, nb, desc))
    def add_review(self, msg):
        self.review.append(msg)
    def add_special(self, msg):
        self.special.append(msg)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--exe', default=r'CN.PLMOD.exe')
    ap.add_argument('--out', default=r'patches_ext.h')
    ap.add_argument('--report', default=None)
    ap.add_argument('--filter', default=None,
                    help='podzbior patchy: slowo w opisie (np. "REC"), albo "!"+slowo = wyklucz')
    ap.add_argument('--f-context', action='store_true',
                    help='F: tylko site y w funkcjach dotykajacych [0x510BC4] lub stridu 0x4A80'
                         ' (+ dysp == dokladna baza tablicy). Odrzucone -> REVIEW.')
    ap.add_argument('--f-provenance', action='store_true',
                    help='F (filtr finalny): d==obase bezwarunkowo; deep tylko gdy byte-op,'
                         ' scale==1 ORAZ funkcja dotyka aktora (ref510/ref4A). ELOFF +0x18,'
                         ' lea, dword/word, scale>1, noctx -> REVIEW.')
    a = ap.parse_args()

    pe, data, tdata, toff, tva, md = load_binary(a.exe)
    g = Gen()
    smap = build_smap(md, tdata, tva)
    by_rva = {rva: ins for rva, ins in smap}
    g.add_special('Sekwencyjny disasm: %d instrukcji w .text (skipdata).' % len(smap))

    stats = Counter()

    # ---------- A) element stride 0x4A80 -> NEW_ELEM_SIZE --------------------
    for rva, ins in smap:
        if ins.mnemonic not in ('imul', 'add', 'mov'):
            continue
        hits = [op for op in ins.operands if op.type == X86_OP_IMM
                and (op.imm & 0xFFFFFFFF) == ELEM_STRIDE_OLD]
        if not hits:
            continue
        pos, size = imm_pos(ins.bytes, ELEM_STRIDE_OLD)
        if pos is None:
            g.add_review('A elem stride imm off @%08X: %s' % (rva, ins.mnemonic+' '+ins.op_str))
            continue
        nb = struct.pack('<I', NEW_ELEM_SIZE)[:size]
        g.add(rva, pos, size, nb, 'elem stride 0x4A80 %s' % ins.op_str)
        stats['A-elem'] += 1

    # ---------- B) pula 0x5D200 -> NEW_POOL_SIZE -----------------------------
    # Uwaga: 'push' jest konieczny — odczyt sentinela puli wystepuje jako
    # `push dword ptr [reg + 0x5D200]` (np. @1E3AE). Bez 'push' ten site
    # zostaje pominiety, a zapis sentinela trafia pod nowy offset -> odczyt smieci.
    for rva, ins in smap:
        if ins.mnemonic not in ('cmp', 'mov', 'imul', 'add', 'sub', 'push'):
            continue
        imm_hit = any(op.type == X86_OP_IMM and (op.imm & 0xFFFFFFFF) == POOL_SIZE_OLD
                      for op in ins.operands)
        if imm_hit:
            pos, size = imm_pos(ins.bytes, POOL_SIZE_OLD)
            if pos is None:
                g.add_review('B pool imm off @%08X: %s' % (rva, ins.mnemonic+' '+ins.op_str))
                continue
            nb = struct.pack('<I', NEW_POOL_SIZE)[:size]
            g.add(rva, pos, size, nb, 'pool size 0x5D200 %s' % ins.op_str)
            stats['B-pool'] += 1
            continue
        # disp32 == POOL_SIZE_OLD (np. cmp [reg+0x5D200], imm) — w normalnym smapie
        mem_hit = any(op.type == X86_OP_MEM and op.mem.base and
                      (op.mem.disp & 0xFFFFFFFF) == POOL_SIZE_OLD for op in ins.operands)
        if mem_hit:
            pos = disp_pos(ins.bytes, POOL_SIZE_OLD)
            if pos is None:
                g.add_review('B pool disp off @%08X: %s' % (rva, ins.mnemonic+' '+ins.op_str))
                continue
            if data[rva2off(tva, toff, rva) + pos: rva2off(tva, toff, rva) + pos + 4] != \
                    struct.pack('<I', POOL_SIZE_OLD):
                g.add_review('B pool disp bajty niezgadzajace @%08X' % rva)
                continue
            g.add(rva, pos, 4, struct.pack('<I', NEW_POOL_SIZE),
                  'pool sentinel %s' % ins.op_str)
            stats['B-pool-disp'] += 1

    # 7 kuratorowanych site'ów puli (region UI; smap je gubi przez desync)
    pool_pat = struct.pack('<I', POOL_SIZE_OLD)
    for rva in CURATED_POOL_DISP:
        off = rva2off(tva, toff, rva)
        if data[off+2:off+6] != pool_pat:
            g.add_review('B kuratorowany pool @%08X: brak starych bajtow 00 D2 05 00 @+2'
                         % rva)
            continue
        g.add(rva, 2, 4, struct.pack('<I', NEW_POOL_SIZE), 'pool sentinel (UI curated)')
        stats['B-pool-curated'] += 1

    # Alokacja puli aktorów: 0x5D204 (0x5D200 + 4). 6 site'ów (mov, push).
    for rva, ins in smap:
        if ins.mnemonic not in ('mov', 'push'):
            continue
        if not any(op.type == X86_OP_IMM and (op.imm & 0xFFFFFFFF) == POOL_ALLOC_OLD
                   for op in ins.operands):
            continue
        pos, size = imm_pos(ins.bytes, POOL_ALLOC_OLD)
        if pos is None:
            g.add_review('B pool alloc imm off @%08X: %s' % (rva, ins.mnemonic+' '+ins.op_str))
            continue
        nb = struct.pack('<I', NEW_POOL_SIZE + 4)[:size]
        g.add(rva, pos, size, nb, 'pool alloc 0x5D204 %s' % ins.op_str)
        stats['B-pool-alloc'] += 1

    # ---------- C) stride surowców 0x42 -> 0x7F ------------------------------
    seen_cd_exclude = set()
    def stride_scan(value, tag):
        n = 0
        for rva, ins in smap:
            if ins.mnemonic not in ('imul', 'add', 'mov'):
                continue
            if rva in C_D_EXCLUDE:
                # fałszywy pozytyw: dane gry / offset UI — nie stride; nie patchuj,
                # tylko raportuj (raz na RVA, niezależnie od kategorii wartości).
                if not (rva in seen_cd_exclude):
                    seen_cd_exclude.add(rva)
                    g.add_special('C/D wykluczony (dane/UI): 0x%08X %s — %s'
                                  % (rva, ins.mnemonic+' '+ins.op_str, C_D_EXCLUDE[rva]))
                continue
            # UWAGA: strictly equality całego imm (nie niskiego bajtu!). np.
            # `mov eax,0x5570042` zawiera 0x42 jako niski bajt — to stała
            # adresowa, a nie stride.
            if not any(op.type == X86_OP_IMM and
                       (op.imm & 0xFFFFFFFF) == value
                       for op in ins.operands):
                continue
            # odrzuć, gdy operand reg/mem ma size 1 (add al,0x42, mov byte [mem])
            if any(op.type != X86_OP_IMM and getattr(op, 'size', 0) == 1
                   for op in ins.operands):
                stats['%s-rejected8' % tag] += 1
                continue
            pos, size = imm_pos(ins.bytes, value)
            if pos is None:
                g.add_review('%s imm off @%08X: %s' % (tag, rva, ins.mnemonic+' '+ins.op_str))
                continue
            nb = bytes([NEW_HOUSE_MAX if value == 0x37 else NEW_GOOD_MAX])[:size]
            g.add(rva, pos, size, nb, '%s stride 0x%02X %s' % (tag, value, ins.op_str))
            n += 1
        return n

    stats['C-good']  = stride_scan(0x42, 'good-stride')
    stats['D-house'] = stride_scan(0x37, 'house-stride')

    # ---------- E1) limity cmp pętli kopiowania ------------------------------
    for rva, old, newv, desc in CURATED_CMP_E1:
        off = rva - tva
        if off < 0 or off >= len(tdata):
            g.add_review('E1 limit cmp poza .text @%08X' % rva)
            continue
        ins = by_rva.get(rva)
        if ins is None:
            g.add_review('E1 limit cmp nie dekoduje @%08X' % rva)
            continue
        pos, size = imm_pos(ins.bytes, old)
        if pos is None or size != 1:
            g.add_review('E1 limit cmp @%08X oczekiwano imm8=%02X, jest: %s (%s)'
                         % (rva, old, ins.mnemonic+' '+ins.op_str,
                            ' '.join('%02X' % b for b in ins.bytes)))
            continue
        g.add(rva, pos, 1, bytes([newv & 0xFF]), 'E1 limit %s' % desc)
        stats['E1-limits'] += 1

    # E2 — 2 walidatory mapy produkcji (0x1492C) ZOSTAJĄ wstrzymane (Etap 4/6).
    # 3 walidatory flag (0x142F4/0x14315/0x14336) generowane w kategorii REC poniżej.
    for rva, old, newv, desc in CURATED_CMP_E2:
        ins = by_rva.get(rva)
        ok = ins is not None and \
             any(op.type == X86_OP_IMM and (op.imm & 0xFF) == old for op in ins.operands)
        g.add_special('E2 (Etap 4/6): 0x%08X cmp imm=%02X -> %02X %s — mapa produkcji '
                      '0x1492C nie relokowana; POMINIĘTO. [%s]'
                      % (rva, old, newv, desc, 'OK' if ok else 'SPRAWDŹ'))

    # ===================== H) Etap 2: rekord plemienia ========================
    # P6a: rozmiar rekordu imm 0x1AE08 -> NEW_REC_SIZE (28 site'ów).
    for rva, ins in smap:
        if ins.mnemonic not in ('imul', 'add', 'mov'):
            continue
        if not any(op.type == X86_OP_IMM and (op.imm & 0xFFFFFFFF) == OLD_REC_SIZE
                   for op in ins.operands):
            continue
        pos, size = imm_pos(ins.bytes, OLD_REC_SIZE)
        if pos is None:
            g.add_review('REC size imm off @%08X: %s' % (rva, ins.mnemonic+' '+ins.op_str))
            continue
        nb = struct.pack('<I', NEW_REC_SIZE)[:size]
        g.add(rva, pos, size, nb, 'REC size 0x1AE08 %s' % ins.op_str)
        stats['REC-size'] += 1

    # P6b: koniec tablicy rekordów imm 0x468D50 -> NEW_REC_ARREND (2 site'y).
    for rva, ins in smap:
        if ins.mnemonic not in ('cmp', 'mov', 'add', 'sub', 'imul'):
            continue
        if not any(op.type == X86_OP_IMM and (op.imm & 0xFFFFFFFF) == OLD_REC_ARREND
                   for op in ins.operands):
            continue
        pos, size = imm_pos(ins.bytes, OLD_REC_ARREND)
        if pos is None:
            g.add_review('REC arrend imm off @%08X: %s' % (rva, ins.mnemonic+' '+ins.op_str))
            continue
        nb = struct.pack('<I', NEW_REC_ARREND)[:size]
        g.add(rva, pos, size, nb, 'REC array end 0x468D50 %s' % ins.op_str)
        stats['REC-arrend'] += 1

    # P7: relokacja displacency baz rekordu (8 site'ów; jobs 0x50A0 zostaje).
    for rva, old_d, desc in REC_DISP:
        ins = by_rva.get(rva)
        if ins is None:
            g.add_review('REC disp nie dekoduje @%08X' % rva)
            continue
        nd = REC_DISP_NEW[old_d]
        pos = disp_pos(ins.bytes, old_d)
        if pos is None:
            g.add_review('REC disp off @%08X (%s): %s' % (rva, desc, ins.op_str))
            continue
        fo = rva2off(tva, toff, rva) + pos
        if data[fo:fo+4] != struct.pack('<I', old_d):
            g.add_review('REC disp bajty niezgadzajace @%08X (0x%04X)' % (rva, old_d))
            continue
        g.add(rva, pos, 4, struct.pack('<I', nd),
              'REC disp 0x%04X->0x%04X %s %s' % (old_d, nd, desc, ins.op_str))
        stats['REC-disp'] += 1

    # P8: walidatory flag w rekordzie — imm8 cmp -> 0x7F (3 site'y).
    for rva, old, newv, desc in REC_LIMITS:
        ins = by_rva.get(rva)
        if ins is None:
            g.add_review('REC limit nie dekoduje @%08X' % rva)
            continue
        pos, size = imm_pos(ins.bytes, old)
        if pos is None or size != 1:
            g.add_review('REC limit @%08X oczekiwano imm8=%02X, jest: %s (%s)'
                         % (rva, old, ins.mnemonic+' '+ins.op_str,
                            ' '.join('%02X' % b for b in ins.bytes)))
            continue
        g.add(rva, pos, 1, bytes([newv & 0xFF]), 'REC limit %s' % desc)
        stats['REC-limits'] += 1

    g.add_special(REC_VALIDATOR_PROD)
    g.add_special('Rekord: jobs +0x50A0 i pola od +0x519C (w tym mapa 0x1492C) zostają '
                  'na swoich offsetach; nie patchowane.')
    g.add_special('Nowy rekord: size=0x%06X, arr_end=0x%06X, ogon: surowceA=0x%06X, '
                  'surowceB=0x%06X, domy=0x%06X, pojazdy=0x%06X.'
                  % (NEW_REC_SIZE, NEW_REC_ARREND, NEW_REC_SUROW_A, NEW_REC_SUROW_B,
                     NEW_REC_DOMY, NEW_REC_VEH))

    # ---------- F) relokacja displacency 5 tablic ----------------------------
    SAFE_DISP_MNEM = {
        'mov','lea','cmp','and','or','xor','add','sub','adc','sbb','inc','dec',
        'not','neg','test','push','movzx','movsx','sete','setne','setl','setle',
        'setg','setge','setb','seta','movsxd',
    }
    EXCLUDE_DISP = {
        0x1581,   # GOODS_A: inna tablica (array 5-bajtowych)
        0x201F,   # GOODS_A2: [esi+esi*2] — tablica 3-bajtowych, nie element
    }
    EXCLUDE_RVA  = {0x0009E79}   # goodsB copy dest (code cave Etap 3)
    # ELOFF: base rejestru = element+0x18 (funkcje 0x9ABC/0x3299A) — band o +0x18
    # bledny (np. 0x2808 -> GOODS_A2 zamiast realnego HOUSES_A). Korekta manualna Etap 3/4.
    EXCLUDE_ELOFF_RVA = {0x000329DE, 0x000329E7}

    # context F: funkcje "dotykajace" aktora — odnosza sie do [0x510BC4] albo
    # do stridu elementu 0x4A80. Takie funkcje realnie obsluguja strukture aktora;
    # site'y F wewnatrz funkcji bez tego kontekstu to najprawdopodobniej pola
    # innych obiektow gry (crash 0x24F2D = obiekt 0x1890 / pole 0x188C).
    f_ref510 = set()
    f_ref4A = set()
    if a.f_context or a.f_provenance:
        for r, ins in smap:
            for op in ins.operands:
                if op.type == X86_OP_MEM and (op.mem.disp & 0xFFFFFFFF) == 0x510BC4:
                    f_ref510.add(r)
            if ins.mnemonic in ('imul', 'mov', 'add', 'cmp', 'lea', 'sub'):
                for op in ins.operands:
                    if op.type == X86_OP_IMM and (op.imm & 0xFFFFFFFF) == 0x4A80:
                        f_ref4A.add(r)
        rv_lst = sorted(by_rva.keys())

        def func_bounds(hint):
            # granice funkcji: najblizsze 'ret' z lewej/prawej od hint
            start = 0
            for r in reversed(rv_lst):
                if r < hint and by_rva[r].mnemonic == 'ret':
                    start = r + len(by_rva[r].bytes)
                    break
            end = len(tdata)
            for r in rv_lst:
                if r > hint and by_rva[r].mnemonic == 'ret':
                    end = r
                    break
            return start, end

        def func_touches(hint):
            import bisect
            st, en = func_bounds(hint)
            for s in (f_ref510, f_ref4A):
                lst = sorted(s)
                i = bisect.bisect_left(lst, st)
                if i < len(lst) and lst[i] < en:
                    return True
            return False

    for name, obase, ostride, newbase_sym in ARR_TABLES:
        nbase = globals()[newbase_sym]
        band = (obase, obase + ARR_N * ostride)
        per_tab = Counter()
        for rva, ins in smap:
            if ins.mnemonic not in SAFE_DISP_MNEM:
                continue
            for op in ins.operands:
                if op.type != X86_OP_MEM:
                    continue
                d = op.mem.disp & 0xFFFFFFFF
                if not (band[0] <= d < band[1]):
                    continue
                if op.mem.base == 0 and op.mem.index == 0:
                    continue                    # absolutny adres — nie element
                if rva in EXCLUDE_RVA:
                    g.add_special('F pominięty EXCLUDE_RVA @%08X (%s, %s)' % (rva, name, ins.op_str))
                    continue
                if d in EXCLUDE_DISP:
                    g.add_review('F EXCLUDE_DISP 0x%04X @%08X (%s, %s)' % (d, rva, name, ins.op_str))
                    continue
                if a.f_context and d != obase and not func_touches(rva):
                    g.add_review('F bez-kontekstu aktora 0x%04X @%08X (%s, %s)'
                                 % (d, rva, name, ins.op_str))
                    continue
                if a.f_provenance and d != obase:
                    # filtr finalny F: deep tylko byte-op + scale==1 + kontekst aktora
                    if rva in EXCLUDE_ELOFF_RVA:
                        g.add_review('F ELOFF element+0x18 (band +0x18 bledny) 0x%04X @%08X (%s, %s)'
                                     % (d, rva, name, ins.op_str))
                        continue
                    if ins.mnemonic == 'lea':
                        g.add_review('F lea deep (REVIEW) 0x%04X @%08X (%s, %s)'
                                     % (d, rva, name, ins.op_str))
                        continue
                    if op.mem.index and op.mem.scale > 1:
                        g.add_review('F deep scale>1 (REVIEW) 0x%04X @%08X (%s, %s)'
                                     % (d, rva, name, ins.op_str))
                        continue
                    if 'byte ptr' not in ins.op_str.lower():
                        g.add_review('F deep dword/word (REVIEW) 0x%04X @%08X (%s, %s)'
                                     % (d, rva, name, ins.op_str))
                        continue
                    if not func_touches(rva):
                        g.add_review('F deep bez-kontekstu aktora 0x%04X @%08X (%s, %s)'
                                     % (d, rva, name, ins.op_str))
                        continue
                tribe = (d - obase) // ostride
                sub   = (d - obase) %  ostride
                nd = nbase + tribe * NEW_STRIDE + sub
                pos = disp_pos(ins.bytes, d)
                if pos is None:
                    g.add_review('F disp off @%08X (%s 0x%04X): %s' % (rva, name, d, ins.op_str))
                    continue
                # sanity: stary bajt zgadza się (przed patch'em)
                if data[rva2off(tva, toff, rva) + pos:
                        rva2off(tva, toff, rva) + pos + 4] != struct.pack('<I', d):
                    g.add_review('F bajty niezgadzajace @%08X (%s 0x%04X)' % (rva, name, d))
                    continue
                g.add(rva, pos, 4, struct.pack('<I', nd),
                      'F %s disp 0x%04X->0x%04X %s' % (name, d, nd, ins.op_str))
                per_tab['n'] += 1
        stats['F-%s' % name] = per_tab['n']

    # ---------- G) specjalne (raport) ----------------------------------------
    g.add_special(
        'POWTÓRKA KOPIOWANIA SUROWCÓW B (0x9E6C-0x9E82): blok używa esi=acc JOBS '
        '(stride 0x38) zamiast acc surowców dla dest +0x3C78. Po relokacji wymaga '
        'CODE CAVE (Etap 3): edx = [ebp-0x10](acc 0x7F) + ebx, disp -> NEW_GOODS_B.')
    g.add_special('0x9E00 mov [ebp-0x20],0x1AE08 = rozmiar rekordu plemienia — Etap 2.')
    g.add_special('0x9E15 mov [ebp-0xc],1 / liczba plemion w pętli — bez zmian (1..41).')
    for rva, old, note in EXCLUDED_ETAP46:
        g.add_special('EXCLUDED Etap 4/6: 0x%08X cmp imm=%02X (%s) — zależne od danych gry.' %
                      (rva, old, note))

    # filtr podzbioru (--filter REC / !REC / 'a,b' = OR; tokeny mogą być z '!':
    # np. 'F GOODS_A ,!0x1364,!0x1454' = patche F GOODS_A ale bez tych disp)
    if a.filter:
        f = a.filter
        toks = [w.strip() for w in f.split(',') if w.strip()]
        neg = [t[1:] for t in toks if t.startswith('!')]
        pos = [t for t in toks if not t.startswith('!')]
        def keep(desc):
            hit = any(w in desc for w in pos) if pos else True
            if neg and any(w in desc for w in neg):
                hit = False
            return hit
        g.patches = [p for p in g.patches if keep(p[4])]
        g.add_special('FILTER: %s -> %d patchy' % (a.filter, len(g.patches)))

    # ===================== walidacja + raport ================================
    bad = 0
    for (rva, off, size, nb, desc) in g.patches:
        fo = rva2off(tva, toff, rva) + off
        if fo + size > len(data):
            print('POZA PLIKIEM: %08X' % rva); bad += 1
    if bad:
        print('%d patchy poza plikiem — PRZERWANO' % bad)
        return 1

    print('PATCHE: %d' % len(g.patches))
    total_disp = sum(v for k, v in stats.items() if k.startswith('F-'))
    print('  A element stride   : %d' % stats['A-elem'])
    print('  B pula imm         : %d' % stats['B-pool'])
    print('  B pula disp (smap) : %d' % stats['B-pool-disp'])
    print('  B pula curated     : %d' % stats['B-pool-curated'])
    print('  B pula alloc 0x5D204: %d' % stats['B-pool-alloc'])
    print('  C stride surowce   : %d (odrzucone 8-bit: %d)' %
          (stats['C-good'], stats['good-stride-rejected8']))
    print('  D stride domy      : %d (odrzucone 8-bit: %d)' %
          (stats['D-house'], stats['house-stride-rejected8']))
    print('  E1 limity copy-loop: %d' % stats['E1-limits'])
    print('  H REC size (P6a)   : %d' % stats['REC-size'])
    print('  H REC arr end (P6b): %d' % stats['REC-arrend'])
    print('  H REC disp (P7)    : %d' % stats['REC-disp'])
    print('  H REC limits (P8)  : %d' % stats['REC-limits'])
    for k in sorted(k for k in stats if k.startswith('F-')):
        print('  F %-9s: %d' % (k[2:], stats[k]))
    print('  F RAZEM: %d' % total_disp)
    print('REVIEW: %d' % len(g.review))
    print('SPECIAL: %d' % len(g.special))

    # ===================== wyjście C ==========================================
    def emit_table(path):
        L = []
        L.append('/* Auto-generowane: gen_engine_ext.py — Etap 1+2 (aktor + rekord).')
        L.append('   Etap 1: relokacja 5 tablic per-plemienia do ogona elementu, stride -> 0x7F.')
        L.append('   Etap 2: rekord plemienia — rozmiar/koniec tablicy, 4 bazy flag -> ogon,')
        L.append('   walidatory flag -> 0x7F. */')
        L.append('#pragma once')
        L.append('#include <windows.h>')
        L.append('')
        L.append('#define NEW_GOOD_MAX   0x%02X' % NEW_GOOD_MAX)
        L.append('#define NEW_HOUSE_MAX  0x%02X' % NEW_HOUSE_MAX)
        L.append('#define NEW_STRIDE     0x%02X' % NEW_STRIDE)
        L.append('#define NEW_ELEM_SIZE  0x%04X' % NEW_ELEM_SIZE)
        L.append('#define NEW_POOL_SIZE  0x%06X' % NEW_POOL_SIZE)
        L.append('#define NEW_GOODS_A    0x%04X' % NEW_GOODS_A)
        L.append('#define NEW_GOODS_A2   0x%04X' % NEW_GOODS_A2)
        L.append('#define NEW_GOODS_B    0x%04X' % NEW_GOODS_B)
        L.append('#define NEW_HOUSES_A   0x%04X' % NEW_HOUSES_A)
        L.append('#define NEW_HOUSES_B   0x%04X' % NEW_HOUSES_B)
        L.append('#define NEW_REC_SIZE   0x%06X' % NEW_REC_SIZE)
        L.append('#define NEW_REC_ARREND 0x%06X' % NEW_REC_ARREND)
        L.append('#define NEW_REC_SUROW_A 0x%06X' % NEW_REC_SUROW_A)
        L.append('#define NEW_REC_SUROW_B 0x%06X' % NEW_REC_SUROW_B)
        L.append('#define NEW_REC_DOMY    0x%06X' % NEW_REC_DOMY)
        L.append('#define NEW_REC_VEH     0x%06X' % NEW_REC_VEH)
        L.append('')
        L.append('typedef struct { DWORD rva; BYTE off; BYTE size; BYTE bytes[8]; const char* desc; } Patch;')
        L.append('')
        L.append('static const Patch PATCHES[] = {')
        for (rva, off, size, nb, desc) in sorted(g.patches):
            pad = nb + b'\x00' * (8 - len(nb))
            hx = ', '.join('0x%02X' % b for b in pad)
            d = desc.replace('\\', '\\\\').replace('"', '\\"')
            L.append('    { 0x%07X, %2d, %d, { %s }, "%s" },' % (rva, off, size, hx, d))
        L.append('};')
        L.append('#define PATCH_COUNT (sizeof(PATCHES)/sizeof(PATCHES[0]))')
        L.append('')
        L.append('/* logi (zdefiniowane w osobnej jednostce log.cpp; stdout + plik logs/etapc.log) */')
        L.append('#ifdef __cplusplus')
        L.append('extern "C" {')
        L.append('#endif')
        L.append('void etapc_log(const char* fmt, ...);')
        L.append('#ifdef __cplusplus')
        L.append('}')
        L.append('#endif')
        L.append('')
        L.append('/* aplikuje patche do biezacego procesu; zwraca liczbe udanych. RVA od ImageBase. */')
        L.append('static int etapc_apply_patches(void)')
        L.append('{')
        L.append('    int ok = 0;')
        L.append('    HMODULE mod = GetModuleHandleW(L"CN.PLMOD.exe");')
        L.append('    if (!mod)')
        L.append('        mod = GetModuleHandleW(NULL);')
        L.append('    BYTE* base = (BYTE*)mod;')
        L.append('    DWORD prev = 0;')
        L.append('')
        L.append('    for (size_t i = 0; i < PATCH_COUNT; ++i) {')
        L.append('        Patch p = PATCHES[i];')
        L.append('        BYTE* addr = base + p.rva + p.off;')
        L.append('        if (!VirtualProtect(addr, p.size, PAGE_EXECUTE_READWRITE, &prev)) {')
        L.append('            etapc_log("patch %u (rva %08X) VirtualProtect FAILED\\n", (unsigned)i, p.rva);')
        L.append('            continue;')
        L.append('        }')
        L.append('        memcpy(addr, p.bytes, p.size);')
        L.append('        VirtualProtect(addr, p.size, prev, &prev);')
        L.append('        etapc_log("patch %u ok: %s (rva %08X off %u len %u)\\n",')
        L.append('                  (unsigned)i, p.desc, p.rva, p.off, p.size);')
        L.append('        ++ok;')
        L.append('    }')
        L.append('    return ok;')
        L.append('}')
        with open(path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(L) + '\n')
        print('Zapisano: %s' % path)

    emit_table(a.out)

    if a.report:
        with open(a.report, 'w', encoding='utf-8') as f:
            f.write('gen_engine_ext.py — raport pokrycia (Etap 1+2: aktor + rekord)\n')
            f.write('PATCHE ogółem: %d\n\n' % len(g.patches))
            f.write(' per kategoria:\n')
            f.write('  A element stride    : %d\n' % stats['A-elem'])
            f.write('  B pula imm          : %d\n' % stats['B-pool'])
            f.write('  B pula disp (smap)  : %d\n' % stats['B-pool-disp'])
            f.write('  B pula curated      : %d\n' % stats['B-pool-curated'])
            f.write('  C stride surowce    : %d (odrzucone 8-bit: %d)\n' %
                    (stats['C-good'], stats['good-stride-rejected8']))
            f.write('  D stride domy       : %d (odrzucone 8-bit: %d)\n' %
                    (stats['D-house'], stats['house-stride-rejected8']))
            f.write('  E1 limity copy-loop : %d\n' % stats['E1-limits'])
            f.write('  H REC size (P6a)    : %d\n' % stats['REC-size'])
            f.write('  H REC arr end (P6b) : %d\n' % stats['REC-arrend'])
            f.write('  H REC disp (P7)     : %d\n' % stats['REC-disp'])
            f.write('  H REC limits (P8)   : %d\n' % stats['REC-limits'])
            for k in sorted(k for k in stats if k.startswith('F-')):
                f.write('  F %-10s: %d\n' % (k[2:], stats[k]))
            f.write('  F RAZEM             : %d\n' % total_disp)
            f.write('\nSPECJALNE (Etap 2/3/4-6, nie generowane):\n')
            for s in g.special:
                f.write('  * %s\n' % s)
            f.write('\nREVIEW (%d):\n' % len(g.review))
            for r in g.review:
                f.write('  %s\n' % r)
        print('Raport: %s' % a.report)
    return 0

if __name__ == '__main__':
    sys.exit(main())