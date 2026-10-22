import pefile, sys
from capstone import Cs, CS_ARCH_X86, CS_MODE_32
path = r'CN.PLMOD.exe'
pe = pefile.PE(path); data = open(path,'rb').read(); IB = pe.OPTIONAL_HEADER.ImageBase
text = [s for s in pe.sections if s.Name.startswith(b'.text')][0]
toff = text.PointerToRawData; tva = IB + text.VirtualAddress
tdata = data[toff:toff+text.SizeOfRawData]
md = Cs(CS_ARCH_X86, CS_MODE_32)
start = int(sys.argv[1],16); end = int(sys.argv[2],16)
if len(sys.argv) > 3 and sys.argv[3] == 'align':
    # find nearest prologue backwards
    i = start - tva
    while i > 0:
        if tdata[i] == 0x55 and tdata[i+1] == 0x8B and tdata[i+2] == 0xEC:
            start = tva + i; break
        i -= 1
off = start - tva
for i in md.disasm(tdata[off:end-tva], start):
    print('0x%08X: %-8s %s' % (i.address, i.mnemonic, i.op_str))
