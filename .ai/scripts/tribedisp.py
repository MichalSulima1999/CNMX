import pefile, collections
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

path = r'CN.PLMOD.exe'
pe = pefile.PE(path); data = open(path, 'rb').read(); IB = pe.OPTIONAL_HEADER.ImageBase
text = [s for s in pe.sections if s.Name.startswith(b'.text')][0]
tva = IB + text.VirtualAddress
tdata = data[text.PointerToRawData:text.PointerToRawData + text.SizeOfRawData]
md = Cs(CS_ARCH_X86, CS_MODE_32); md.detail = True

lo, hi = 0x5193, 0x1AE08
disp = collections.Counter()
for ins in md.disasm(tdata, tva):
    for op in ins.operands:
        if op.type == 3 and lo <= op.mem.disp < hi:
            disp[op.mem.disp] += 1
print('distinct displacements in [0x%X, 0x%X): %d' % (lo, hi, len(disp)))
print('total mem operands:', sum(disp.values()))
top = disp.most_common(30)
for d, c in top:
    print('   0x%-8X  x%d' % (d, c))
