import pefile, re, sys
from capstone import Cs, CS_ARCH_X86, CS_MODE_32
path = r'CN.PLMOD.exe'
pe = pefile.PE(path); data = open(path,'rb').read(); IB = pe.OPTIONAL_HEADER.ImageBase
text = [s for s in pe.sections if s.Name.startswith(b'.text')][0]
tva = IB + text.VirtualAddress
tdata = data[text.PointerToRawData:text.PointerToRawData+text.SizeOfRawData]
md = Cs(CS_ARCH_X86, CS_MODE_32)
targets = [0x37, 0x42, 0x36, 0x41]
res = {t: [] for t in targets}
for ins in md.disasm(tdata, tva):
    if ins.mnemonic not in ('cmp','mov','push','sub','add','and','or','xor','imul','test','inc','dec'):
        continue
    op = ins.op_str
    if '[' in op:
        op = re.sub(r'\[[^\]]*\]', '', op)
    for imm in re.finditer(r'0x[0-9a-f]+', op):
        v = int(imm.group(), 16)
        if v in res:
            res[v].append((ins.address, ins.mnemonic, ins.op_str))
for t in targets:
    print('=== 0x%X : %d hits' % (t, len(res[t])))
    for a, m, o in res[t]:
        print('   0x%08X: %-6s %s' % (a, m, o))
