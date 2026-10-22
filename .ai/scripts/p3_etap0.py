# -*- coding: utf-8 -*-
"""p3_etap0.py — Etap 0 Planu 3: katalogizacja stałych layoutu GUI + pipeline prezentacji.
Wyniki zapisywane do .ai\docs\layout-constants.md i .ai\docs\pipeline-prezentacji.md
(analiza statyczna; brak modyfikacji)."""
import sys, struct, collections, os
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pefile
from capstone import Cs, CS_ARCH_X86, CS_MODE_32, x86

PE = r"G:\Games\CnMod 1.2\CN.PLMOD.exe"
pe = pefile.PE(PE)
base = pe.OPTIONAL_HEADER.ImageBase
data = pe.__data__

ttext = [s for s in pe.sections if s.Name.rstrip(b"\x00") == b".text"][0]
tv, ts, tn = ttext.VirtualAddress, ttext.PointerToRawData, ttext.Misc_VirtualSize
blob = data[ts:ts + tn]
md = Cs(CS_ARCH_X86, CS_MODE_32)
md.detail = True

OUT = r"G:\Games\CnMod 1.2\.ai\docs"
os.makedirs(OUT, exist_ok=True)

def disasm_lines(va, before, after, mark=None):
    off = pe.get_offset_from_rva(va - base)
    if off is None:
        return ["  (poza mapowaniem; off=%r)" % off]
    start = max(0, off - before)
    lines = []
    for ins in md.disasm(bytes(data[start:off + after]), base + start):
        m = ">>" if (mark is not None and ins.address == mark) else "  "
        lines.append("%s 0x%08x: %-7s %s" % (m, ins.address, ins.mnemonic, ins.op_str))
    return lines

# ---------------------------------------------------------------- 1. odwołania do globals GUI
GUIW, GUIH = 0x569264, 0x569268
refs_w, refs_h = [], []
for i in range(len(blob) - 6):
    try:
        ins = next(md.disasm(bytes(blob[i:i + 8]), 0))
    except Exception:
        continue
    if ins.mnemonic == "invalid":
        continue
    for op in ins.operands:
        if op.type == x86.X86_OP_MEM:
            d = op.mem.disp
            if op.mem.base == 0 and op.mem.index == 0 and d == GUIW:
                refs_w.append((base + tv + i, ins.mnemonic, ins.op_str))
            elif op.mem.base == 0 and op.mem.index == 0 and d == GUIH:
                refs_h.append((base + tv + i, ins.mnemonic, ins.op_str))
            elif d == GUIW or d == GUIH:
                refs_w.append((base + tv + i, ins.mnemonic + "(b/i)", ins.op_str)) if d == GUIW else refs_h.append((base + tv + i, ins.mnemonic + "(b/i)", ins.op_str))

# ---------------------------------------------------------------- 2. callerzy (E8)
def callers(target):
    out = []
    for i in range(len(blob) - 5):
        if blob[i] == 0xE8:
            rel = struct.unpack_from("<i", blob, i + 1)[0]
            if base + tv + i + 5 + rel == target:
                out.append(base + tv + i)
    return out

getters = {
    0x4A8845: "GetGUIWidth", 0x4A884B: "GetGUIHeight",
    0x478479: "GetWidth(display)", 0x47848A: "GetHeight(display)",
    0x40D507: "stretch(0x40D507)", 0x40C634: "ctor powierzchni(0x40C634)",
    0x476643: "root widget(0x476643)", 0x47B0D7: "blit HUD(0x47B0D7)",
    0x411327: "memcpy wierszowe(0x411327)", 0x4787B3: "draw(0x4787B3)",
}

# ---------------------------------------------------------------- 3. push-imm histogram + znane stałe
K = {0x1f4: "500", 0x1a4: "420", 0x258: "600", 0x8c: "140", 0x104: "260",
     0x154: "340", 0x190: "400", 0x12c: "300", 0xc8: "200", 0x96: "150",
     0x64: "100", 0xfa: "250", 0x1e0: "480", 0x226: "550"}

hist = collections.Counter()
push_sites = collections.defaultdict(list)
for i in range(len(blob) - 5):
    if blob[i] == 0x68:
        imm = struct.unpack_from("<I", blob, i + 1)[0]
        if 0x20 <= imm <= 0x900:
            hist[imm] += 1
        if imm in K:
            push_sites[imm].append(base + tv + i)

# ---------------------------------------------------------------- 4. fonty — xrefy stringów
def cstr(off):
    s = off
    while s > 0 and data[s - 1] != 0: s -= 1
    e = data.find(b"\x00", off, off + 64)
    return bytes(data[s:e]).decode("cp1250", "replace")

fstr = {}
for pat in (b"font08", b"font_08", b"font10", b"font_10", b"font12", b"font_12",
            b"fonthead16bld", b"fonthead_16bld", b".fnt"):
    p = 0
    while True:
        o = bytes(data).find(pat, p)
        if o < 0: break
        # tylko zaczyn klucza (nie w środku innego); dopasuj do .fnt
        mm = bytes(data).find(b"\x00", o, o + 0x200)
        st = bytes(data).find(b"\x00", 0, o)  # nie: szukaj początku łańcucha
        # szukaj początku: cofnij do poprzedniego NUL
        s = o
        while s > 0 and data[s - 1] != 0: s -= 1
        nm = bytes(data[s:mm]).decode("cp1250", "replace")
        if nm.lower().endswith(".fnt"):
            fstr.setdefault(nm, pe.get_rva_from_offset(s) + base)
        p = o + 1

def pushrefs(sva):
    refs = []
    for i in range(len(blob) - 5):
        if blob[i] == 0x68 and struct.unpack_from("<I", blob, i + 1)[0] == sva:
            refs.append(base + tv + i)
    return refs

# ---------------------------------------------------------------- zapis layout-constants.md
L = ["# Katalog stałych layoutu GUI (Plan 3, Etap 0)",
     "",
     "Wygenerowano: 2026-10-06 (skrypt `p3_etap0.py`, analiza statyczna CN.PLMOD.exe)",
     "",
     "Konwencja: `push 0x…` w .text z wartościami stałych; odwołania do `[0x569264]`=GUIW / `[0x569268]`=GUIH",
     "oraz wywołania getterów. Część trafień bywa mid-instruction — zweryfikowane capstone (granice instrukcji).",
     ""]
L.append("## 1. Odwołania do globalsów GUI (GUIW=0x569264, GUIH=0x569268)")
L.append("")
L.append("### GUIW (0x569264) — %d odwołań" % len(refs_w))
for va, mn, ops in sorted(refs_w):
    L.append("- `0x%08x`  %s %s" % (va, mn, ops))
L.append("")
L.append("### GUIH (0x569268) — %d odwołań" % len(refs_h))
for va, mn, ops in sorted(refs_h):
    L.append("- `0x%08x`  %s %s" % (va, mn, ops))
L.append("")

L.append("## 2. Wywołania getterów / funkcji pipeline'u (%d wierszy)" % len(getters))
for t, nm in sorted(getters.items(), key=lambda kv: kv[1]):
    cs = callers(t)
    L.append("- **%s** — %d wywołań: %s" % (nm, len(cs), ", ".join("0x%x" % x for x in cs[:20])))
    if len(cs) > 20:
        L.append("  (+%d więcej)" % (len(cs) - 20))
L.append("")

L.append("## 3. Push-imm z kluczowymi stałymi layoutu")
for imm in sorted(K, key=lambda x: K[x]):
    sites = push_sites[imm]
    L.append("- `0x%x` (%s) — %d miejsc: %s" % (imm, K[imm], len(sites),
             ", ".join("0x%x" % x for x in sites[:24])))
L.append("")

L.append("## 4. Histogram push-imm (0x20..0x900) — wzorce stałych")
top = sorted(hist.items(), key=lambda kv: -kv[1])
L.append("")
L.append("| imm | dec | ile razy | | imm | dec | ile razy |")
L.append("|---|---|---|---|---|---|---|")
pairs = [top[i:i + 3] for i in range(0, len(top), 3)]
for row in pairs[:30]:
    cells = []
    for imm, c in row:
        cells.append("`0x%x` | %d | %d" % (imm, imm, c))
    while len(cells) < 3:
        cells.append(" | | ")
    L.append("| " + " | ".join(cells) + " |")
L.append("")

L.append("## 5. Tablice fontów (xrefy stringów .fnt)")
for nm, sva in sorted(fstr.items()):
    r = pushrefs(sva)
    L.append("- `%s` @ 0x%08x — %d xrefy push: %s" % (nm, sva, len(r), ", ".join("0x%x" % x for x in r[:10])))
open(os.path.join(OUT, "layout-constants.md"), "w", encoding="utf-8").write("\n".join(L))
print("layout-constants.md: GUIW refs=%d, GUIH refs=%d, fonty=%d" % (len(refs_w), len(refs_h), len(fstr)))

# ---------------------------------------------------------------- pipeline-prezentacji.md
P = ["# Pipeline prezentacji: UI vs tła (Plan 3, Etap 0 — decyzja C vs B)",
     "",
     "Badanie: czy HUD/UI rysowane jest na osobnej powierzchni od teł (→ wariant C możliwy)",
     "czy na wspólnej (→ wariant C wymaga rozdzielenia, co faworyzuje B). Uzupełnij xrefami z layout-constants.md.",
     ""]
P.append("## Kontekst globalny (aktualizacja po P4)")
P.append("- `0x479195` to **dyspozytor wiadomości**, nie flip. Prezentacja: draw `0x4787B3` → blit `0x47B0D7` → flip `0x405658` (retry WASSTILLDRAWING+Sleep(10), vsync załatwione przez dgVoodoo2).")
P.append("- Blity HUD 1:1: `0x47B0D7` + memcpy `0x411327`. Stretch teł: `0x40D507`.")
P.append("")
P.append("## 6. Callerzy stretcha (0x40D507) i blitu HUD (0x47B0D7)")
for t, nm in ((0x40D507, "stretch teł 0x40D507"), (0x47B0D7, "blit HUD 0x47B0D7")):
    cs = callers(t)
    P.append("- **%s** — %d wywołań: %s" % (nm, len(cs), ", ".join("0x%x" % x for x in cs[:24])))
P.append("")

P.append("## 7. Kontekst lubianych miejsc (auto-disasm)")
show = sorted(set([c for t in (0x40D507, 0x47B0D7) for c in callers(t)[:3]] +
                  [r[0] for r in refs_w[:8]] + [r[0] for r in refs_h[:8]]))
for va in show[:14]:
    P += ["", "### 0x%08x" % va, ""] + ["    " + ln for ln in disasm_lines(va, 10, 26, va)]
open(os.path.join(OUT, "pipeline-prezentacji.md"), "w", encoding="utf-8").write("\n".join(P))
print("pipeline-prezentacji.md ok")

# ---------------------------------------------------------------- podsumowanie konsolowe
print("\n=== PUSH stałych (top po katalogu) ===")
for imm in sorted(K, key=lambda x: -len(push_sites[x])):
    print("  0x%x (%s): %d" % (imm, K[imm], len(push_sites[imm])))
print("\n=== Histogram top 15 ===")
for imm, c in top[:15]:
    print("  0x%x (%-4d) x%d" % (imm, imm, c))