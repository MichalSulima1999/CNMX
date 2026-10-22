import pefile, re, struct, sys
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

path = r'CN.PLMOD.exe'
pe = pefile.PE(path)
data = open(path, 'rb').read()
IB = pe.OPTIONAL_HEADER.ImageBase

def off2va(off):
    for s in pe.sections:
        if s.PointerToRawData <= off < s.PointerToRawData + s.SizeOfRawData:
            return IB + s.VirtualAddress + (off - s.PointerToRawData)
    return None

def va2off(va):
    rva = va - IB
    for s in pe.sections:
        if s.VirtualAddress <= rva < s.VirtualAddress + s.Misc_VirtualSize:
            return s.PointerToRawData + (rva - s.VirtualAddress)
    return None

text = [s for s in pe.sections if s.Name.startswith(b'.text')][0]
toff, tsz = text.PointerToRawData, text.SizeOfRawData
tva = IB + text.VirtualAddress
tdata = data[toff:toff+tsz]

md = Cs(CS_ARCH_X86, CS_MODE_32)

needles = {
 'houses_logic': b'cn.plmod\\types\\houses.ini\x00',
 'houses_gfx':   b'cn.plmod\\budynki12\\houses\\houses.ini\x00',
 'houses_text':  b'cn.plmod\\stringstext\\gameobjects\\houses.ini\x00',
 'goodtypes':    b'data\\logic\\goodtypes.ini\x00',
 'weapons':      b'cn.plmod\\types\\weapons.ini\x00',
 'tribes':       b'cn.plmod\\tribetypes12\\tribetypes.ini\x00',
 'houses_orig':  b'data\\logic\\housetypes.ini\x00',
 'goodtypes_cif':b'goodtypes.cif\x00',
 'cif_ext':      b'.cif\x00',
}
for name, n in needles.items():
    off = data.find(n)
    if off < 0:
        print('BRAK', name); continue
    va = off2va(off)
    print('%-14s off=0x%06X VA=0x%08X' % (name, off, va or 0))
    # xrefs
    pat = struct.pack('<I', va)
    start = 0; xrs = []
    while True:
        i = tdata.find(pat, start)
        if i < 0: break
        xrs.append(tva + i); start = i+1
    for x in xrs:
        print('   xref @ 0x%08X' % x)
        s = max(tva, x-80)
        insns = list(md.disasm(tdata[s-tva:s-tva+200], s))
        for ins in insns:
            if s <= ins.address <= x+160:
                mark = ' <==' if ins.address == x else ''
                print('      0x%08X: %-8s %s%s' % (ins.address, ins.mnemonic, ins.op_str, mark))
        print('      ---')
