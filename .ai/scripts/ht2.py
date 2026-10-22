import pefile, struct, sys
path = r'CN.PLMOD.exe'
pe = pefile.PE(path); data = open(path,'rb').read(); IB = pe.OPTIONAL_HEADER.ImageBase
text = [s for s in pe.sections if s.Name.startswith(b'.text')][0]
toff, tsz = text.PointerToRawData, text.SizeOfRawData
tva = IB + text.VirtualAddress
tdata = data[toff:toff+tsz]

def va2off(va):
    rva = va - IB
    for s in pe.sections:
        if s.VirtualAddress <= rva < s.VirtualAddress + s.Misc_VirtualSize:
            return s.PointerToRawData + (rva - s.VirtualAddress)
    return None

def cstr(va):
    o = va2off(va)
    if o is None: return None
    e = data.index(b'\0', o)
    return data[o:min(e, o+80)].decode('latin1')

# indirect: push dword [X] -> value at X is the string ptr
for loc in [0x500470, 0x500474, 0x500578, 0x50057c, 0x4ff8d4, 0x500f48]:
    o = va2off(loc)
    v = struct.unpack_from('<I', data, o)[0]
    print(' [%s] -> ptr 0x%08X  %r' % (hex(loc), v, cstr(v)))

for pat, name in [(b'\x24\x06\x00\x00','imm 0x624'), (b'\xa0\x35\x00\x00','imm 0x35a0'), (b'\xbc\x51\x01\x00','imm 0x151bc')]:
    start=0; hits=[]
    while True:
        i = tdata.find(pat, start)
        if i<0: break
        hits.append(tva+i); start=i+1
    print(name, len(hits), [hex(h) for h in hits[:20]])
