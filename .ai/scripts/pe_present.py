# -*- coding: utf-8 -*-
"""pe_present.py — Etap 0 (P4): sciezka prezentacji + timing w CN.PLMOD.exe.

- stringi DDraw/D3D8 wokol znanych offsetow,
- xref-y do LoadLibraryA/GetProcAddress/timeGetTime/Sleep (wywolania call rel32),
- dezasemblacja okolic flip 0x479195 / draw 0x4787B3 i wywolan timeGetTime.
"""
import sys, struct
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pefile
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

PE = r"G:\Games\CnMod 1.2\CN.PLMOD.exe"
pe = pefile.PE(PE)
base = pe.OPTIONAL_HEADER.ImageBase
data = pe.__data__

def va2off(va):
    return pe.get_offset_from_rva(va - base)

def off2va(off):
    rva = pe.get_rva_from_offset(off)
    return pe.OPTIONAL_HEADER.ImageBase + rva if rva is not None else None

def cstr(off, maxlen=80):
    end = data.find(b"\x00", off, off + maxlen)
    if end < 0: end = off + maxlen
    return data[off:end]

# --- 1. stringi w okolicy znanych offsetow ---
print("=== STRINGI W OKOLICY ===")
for off in (0x104fb8, 0x10503b, 0x1059ac, 0x1059c8, 0x1059e5, 0x1059f0, 0x105b52):
    # szukaj poczatku stringu
    s = off
    while s > 0 and data[s - 1] != 0:
        s -= 1
    print("  0x%06x (va 0x%06x): %r" % (off, off2va(off), cstr(s)))

# case-insensitive d3d8 / directdrawcreate
low = bytes(data).lower()
for n in (b"d3d8.dll", b"directdrawcreate", b"directdrawcreateex", b"ddraw.dll",
          b"acquire", b"waitscanline", b"waitforverticalblank", b"ctl",
          b"gfx_fullscreen", b"window mode", b"x2dddd"):
    p = low.find(n)
    if p >= 0:
        s = p
        while s > 0 and data[s - 1] != 0:
            s -= 1
        print("  %-24s @ 0x%06x (va 0x%06x): %r" % (n.decode(), p, off2va(p), cstr(s, 100)))

# --- 2. importy LoadLibraryA/GetProcAddress/timeGetTime/Sleep -> IAT VA ---
iat = {}
for e in pe.DIRECTORY_ENTRY_IMPORT:
    for imp in e.imports:
        if imp.name:
            iat[imp.name.decode()] = imp.address
print("\n=== IAT ===")
for k in ("LoadLibraryA", "GetProcAddress", "timeGetTime", "Sleep", "PeekMessageA", "GetVersionExA"):
    print("  %-18s 0x%08x" % (k, iat.get(k, 0)))

# --- 3. skan .text: thunke (FF25) + bezposrednie call [IAT] (FF15) ---

text = None
for s in pe.sections:
    if s.Name.rstrip(b"\x00") == b".text":
        text = s
tv = text.VirtualAddress
ts = text.PointerToRawData
tn = text.Misc_VirtualSize
blob = data[ts:ts + tn]

# thunke importowe: FF 25 <IAT-VA> (jmp dword ptr [xxx]) w .text
thunks = {}
iamap = {k: v for k, v in iat.items()}
by_addr = {}
for k, a in iamap.items():
    by_addr.setdefault(a, []).append(k)
for i in range(len(blob) - 6):
    if blob[i] == 0xFF and blob[i + 1] == 0x25:
        mem = struct.unpack_from("<I", blob, i + 2)[0]
        if mem in by_addr:
            thunks[base + tv + i] = by_addr[mem][0]
print("\n=== THUNKI importow ===")
for va, nm in sorted(thunks.items()):
    print("  0x%08x -> %s" % (va, nm))

def find_calls(target):
    out = []
    for i in range(len(blob) - 5):
        if blob[i] == 0xE8:
            rel = struct.unpack_from("<i", blob, i + 1)[0]
            src = tv + i
            if base + src + 5 + rel == target:
                out.append(base + src)
    return out

print("\n=== CALLS (thunke + bezposrednie FF15) ===")
thunk_by_name = {}
for va, nm in sorted(thunks.items()):
    thunk_by_name.setdefault(nm, []).append(va)
# bezposrednie call dword ptr [IAT] (FF 15)
direct = {}
for i in range(len(blob) - 6):
    if blob[i] == 0xFF and blob[i + 1] == 0x15:
        mem = struct.unpack_from("<I", blob, i + 2)[0]
        if mem in by_addr:
            direct.setdefault(by_addr[mem][0], []).append(base + tv + i)
sites = {}
names = ["timeGetTime", "Sleep", "LoadLibraryA", "GetProcAddress", "PeekMessageA"]
for k in names:
    s = []
    for tva in thunk_by_name.get(k, []):
        s += find_calls(tva)
    s += direct.get(k, [])
    sites[k] = sorted(set(s))
    print("  %-16s %3d wywolan: %s" % (k, len(sites[k]), ["0x%x" % x for x in sites[k][:14]]))

# --- 4. dezasemblacja ---
md = Cs(CS_ARCH_X86, CS_MODE_32)
md.detail = False

def disasm(va, before=0, after=140, head=""):
    try:
        off = va2off(va)
    except Exception:
        off = None
    if off is None:
        print("\n--- 0x%08x: poza sekcjami mapowanymi (%s) ---" % (va, head))
        return
    start = max(0, off - before)
    print("\n--- okno 0x%08x [-%d B, +%d B] %s ---" % (va, before, after, head))
    for ins in md.disasm(bytes(data[start:off + after]), base + start):
        mark = ">>" if ins.address == va else "  "
        print("%s 0x%08x: %-7s %s" % (mark, ins.address, ins.mnemonic, ins.op_str))

# referencje push do stringow (DDRAW.DLL, D3D8.DLL, DirectDrawCreate(Ex))
print("\n=== PUSH do stringow DDraw/D3D8 ===")
for label, sva in (("DDRAW.DLL", 0x504fcc), ("D3D8.DLL", 0x50592c),
                   ("DirectDrawCreateEx", 0x504fb8), ("DirectDrawCreate", 0x5059f0)):
    refs = []
    for i in range(len(blob) - 5):
        if blob[i] == 0x68:
            imm = struct.unpack_from("<I", blob, i + 1)[0]
            if imm == sva:
                refs.append(base + tv + i)
    print("  %-20s xrefy: %s" % (label, ["0x%x" % x for x in refs]))

print("\n=== INICJALIZACJA DDraw (LoadLibrary/GetProcAddress/init) ===")
for va, bf, af in ((0x478520, 8, 60), (0x4786b3, 2, 140)):
    disasm(va, bf, af)

print("\n=== PRESENT 0x40567e (retry flip) — cale cialo ===")
disasm(0x405540, 0, 380)

print("\n=== RAMKA 0x4027a0 (petla z Sleep 0xa) + kontekst ===")
disasm(0x402740, 0, 120)

# wzorce call [reg+off] w .text — mapowanie vtable DDraw  (poprawnie: FF 50-57 = call [reg+disp8])
print("\n=== CALLS [vtable+disp8] (FF 50-57) — potencjalne metody DDraw ===")
vt = {0x18: "CreateSurface", 0x2c: "Flip", 0x34: "GetFlipStatus",
      0x40: "SetCooperativeLevel", 0x44: "SetDisplayMode", 0x48: "WaitForVerticalBlank",
      0x50: "Flip(X2D-wrap)"}
for offs, label in sorted(vt.items()):
    hits = []
    for i in range(len(blob) - 3):
        if blob[i] == 0xFF:
            modrm = blob[i + 1]
            if 0x50 <= modrm <= 0x57:
                if blob[i + 2] == offs:
                    # weryfikacja: dezasembluj od i, pierwsza instr ma byc call [reg+disp8]
                    try:
                        ins0 = next(md.disasm(bytes(blob[i:i + 6]), 0))
                    except Exception:
                        ins0 = None
                    if ins0 is not None and ins0.mnemonic == "call":
                        hits.append(base + tv + i)
    print("  [reg+0x%02x] %-22s %2d: %s" % (offs, label, len(hits), ["0x%x" % x for x in hits[:14]]))

print("\n=== PUBLIKA: konteksty SetCooperativeLevel / SetDisplayMode / CreateSurface / DRAW ===")
for va, bf, af in ((0x4819e4, 8, 60), (0x4f0c19, 8, 60), (0x4f0e90, 8, 60),
                   (0x432ce1, 8, 70), (0x49443a, 8, 80), (0x4787b3, 0, 420)):
    disasm(va, bf, af)
