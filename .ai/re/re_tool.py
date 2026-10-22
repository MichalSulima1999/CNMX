# -*- coding: utf-8 -*-
"""RE toolkit for CN.PLMOD.exe (The Nations / Cultures engine, x86-32, image base 0x400000).

Run from repo root.  Commands:
    dis <va> [end_va]        disassemble from va
    func <va>                heuristic function start + first bytes
    refs <va>                all .text refs (imm or absolute mem) to <va>
    refsimm <hex>            all .text refs to a raw immediate value (e.g. d0, 35a0)
    callers <va>             refs that are call/jmp targets of <va>
    strings <substr>         find strings containing substr (bytes, latin1)
    hexdump <va> [n]
    secs                     list sections
"""
import sys, io, re, struct
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='backslashreplace')
import pefile
from capstone import Cs, CS_ARCH_X86, CS_MODE_32
from capstone.x86 import X86_OP_IMM, X86_OP_MEM

EXE = r'G:\Games\CnMod 1.2\CN.PLMOD.exe'
pe = pefile.PE(EXE, fast_load=True)
BASE = pe.OPTIONAL_HEADER.ImageBase
DATA = open(EXE, 'rb').read()
md = Cs(CS_ARCH_X86, CS_MODE_32)
md.detail = True

SECS = [(s.Name.rstrip(b'\x00').decode('latin1'), s.VirtualAddress, s.Misc_VirtualSize,
         s.PointerToRawData, s.SizeOfRawData, s.Characteristics) for s in pe.sections]
TEXT = next(s for s in SECS if s[0] == '.text')
T0, T1, TVA = TEXT[3], TEXT[3] + TEXT[4], BASE + TEXT[1]
TVA_END = BASE + TEXT[1] + max(TEXT[2], TEXT[4])

_cache_insns = None


def rva_off(rva):
    for name, va, vsz, raw, rsz, ch in pe.sections and _secs_tuple():
        if va <= rva < va + max(vsz, rsz):
            return raw + (rva - va)
    return None


def _sections():
    return [(s.Name.rstrip(b'\x00').decode(), s.VirtualAddress, s.Misc_VirtualSize,
             s.PointerToRawData, s.SizeOfRawData) for s in pe.sections]

_S = _sections()
_TXT = [x for x in _S if x[0] == '.text'][0]
_TVA = _TXT[1]
_TRAW = _TXT[3]
_TRSZ = _TXT[4]


def va_off(va):
    r = va - BASE
    for name, sva, vsz, raw, rsz in _S:
        if sva <= r < sva + max(vsz, rsz):
            return raw + (r - sva)
    return None


def rd(va, n):
    o = va_off(va)
    return None if o is None else DATA[o:o + n]


def sec_of(va):
    r = va - BASE
    for name, sva, vsz, raw, rsz in _S:
        if sva <= r < sva + max(vsz, rsz):
            return name
    return None


def insn_abs_targets(i):
    """Return list of (kind, value) absolute references in instruction i."""
    res = []
    for op in i.operands:
        if op.type == X86_OP_IMM:
            res.append(('imm', op.imm & 0xFFFFFFFF))
        elif op.type == X86_OP_MEM and op.mem.base == 0 and op.mem.index == 0:
            res.append(('mem', op.mem.disp & 0xFFFFFFFF))
    return res


def all_insns():
    global _CACHE
    if _CACHE is None:
        _CACHE = list(md.disasm(DATA[_TRAW:_TRAW + _TRSZ], BASE + _TVA))
    return _CACHE

_CACHE = None


def dis(va, n=0x80, end=None):
    if end is not None:
        n = end - va
    o = va_off(va)
    if o is None:
        print('!! no section for 0x%X' % va)
        return
    for i in md.disasm(DATA[o:o + n], va):
        print('%08X  %-22s %s %s' % (i.address, i.bytes.hex(), i.mnemonic, i.op_str))


def refs(val, want=None):
    val &= 0xFFFFFFFF
    out = []
    for i in all_insns():
        for k, v in insn_abs_targets(i):
            if v == val:
                if want and i.mnemonic not in want:
                    break
                out.append((i.address, i))
                break
    return out


def cmd_refs(hexva):
    va = int(hexva, 16)
    r = refs(va)
    print('=== %d refs to 0x%X ===' % (len(r), va))
    for a, i in r:
        print('%08X  %-20s %s %s' % (a, i.bytes.hex(), i.mnemonic, i.op_str))


def cmd_refsimm(hexv):
    v = int(hexv, 16)
    r = refs(v)
    print('=== %d refs to imm 0x%X ===' % (len(r), v))
    for a, i in r:
        print('%08X  %-20s %s %s' % (a, i.bytes.hex(), i.mnemonic, i.op_str))


def cmd_callers(hexva):
    va = int(hexva, 16)
    r = refs(va, want=('call', 'jmp', 'jz', 'jnz', 'je', 'jne', 'jle', 'jg', 'jl', 'jge', 'jbe', 'ja', 'jb', 'jae', 'js', 'jns', 'jp', 'jnp', 'jo', 'jno', 'jcxz'))
    print('=== %d branch refs to 0x%X ===' % (len(r), va))
    for a, i in r:
        print('%08X  %-20s %s %s' % (a, i.bytes.hex(), i.mnemonic, i.op_str))


def cmd_func(hexva):
    va = int(hexva, 16)
    o = va_off(va)
    st = o
    while st > _TRAW and not (DATA[st - 1] in (0xCC, 0x90) and DATA[st - 2] in (0xCC, 0x90)):
        st -= 1
        if o - st > 0x8000:
            break
    sva = BASE + _TVA + (st - _TRAW)
    print('func start ~0x%X (va 0x%X)' % (sva, va))
    dis(sva, 0x40)


def cmd_strings(sub):
    b = sub.encode('latin1')
    for m in re.finditer(re.escape(b), DATA):
        s = m.start()
        # expand printable
        a = s
        while a > 0 and 32 <= DATA[a - 1] < 127:
            a -= 1
        z = s
        while z < len(DATA) and 32 <= DATA[z] < 127:
            z += 1
        print('0x%X: %s' % (a, DATA[a:z].decode('latin1')))


def cmd_hexdump(hexva, hexn='40'):
    va = int(hexva, 16)
    n = int(hexn, 16)
    d = rd(va, n)
    if d is None:
        print('no data'); return
    for i in range(0, len(d), 16):
        c = d[i:i + 16]
        print('%08X  %-47s  %s' % (va + i, c.hex(), ''.join(chr(x) if 32 <= x < 127 else '.' for x in c)))


def main():
    if len(sys.argv) < 2:
        print(__doc__); return
    c = sys.argv[1]; a = sys.argv[2:]
    if c == 'dis':
        dis(int(a[0], 16), end=(int(a[1], 16) if len(a) > 1 else None))
    elif c == 'func':
        cmd_func(a[0])
    elif c == 'refs':
        cmd_refs(a[0])
    elif c == 'refsimm':
        cmd_refsimm(a[0])
    elif c == 'callers':
        cmd_callers(a[0])
    elif c == 'strings':
        cmd_strings(a[0])
    elif c == 'hexdump':
        cmd_hexdump(*a)
    elif c == 'secs':
        for name, sva, vsz, raw, rsz in _S:
            print('%-8s VA=0x%08X VSize=0x%X Raw=0x%X RawSize=0x%X  VAend=0x%08X' % (
                name, BASE + sva, vsz, raw, rsz, BASE + sva + vsz))
    else:
        print('unknown', c)

if __name__ == '__main__':
    main()
