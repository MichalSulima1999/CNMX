import pefile, re, collections
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

path = r'CN.PLMOD.exe'
pe = pefile.PE(path); data = open(path,'rb').read(); IB = pe.OPTIONAL_HEADER.ImageBase
text = [s for s in pe.sections if s.Name.startswith(b'.text')][0]
tva = IB + text.VirtualAddress
tdata = data[text.PointerToRawData:text.PointerToRawData+text.SizeOfRawData]
md = Cs(CS_ARCH_X86, CS_MODE_32); md.detail = True

# tribe flag arrays offsets inside tribe record (base reg varies)
targets = {0x50a0: 'jobs56?', 0x50d8: 'goodA66', 0x511a: 'goodB66', 0x515c: 'house55',
           0x5193: 'veh8', 0x1492c: 'good->house pairs', 0x5ec: 'house name field'}
hits = collections.defaultdict(list)
for ins in md.disasm(tdata, tva):
    if not ins.operands:
        continue
    for op in ins.operands:
        if op.type == 3:  # mem
            d = op.mem.disp
            if d in targets:
                hits[d].append((ins.address, ins.mnemonic, ins.op_str))
for d, name in targets.items():
    print('=== disp 0x%X (%s): %d' % (d, name, len(hits[d])))
    for a, m, o in hits[d][:40]:
        print('    0x%08X: %-6s %s' % (a, m, o))
    if len(hits[d]) > 40:
        print('    ... %d more' % (len(hits[d]) - 40))
