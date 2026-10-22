from capstone import Cs, CS_ARCH_X86, CS_MODE_32
import pefile
exe = r'G:\\Games\\CnMod 1.2\\CN.PLMOD.exe'
out = r'G:\\Games\\CnMod 1.2\\.ai\\docs\\cmp_imm2.txt'
pe = pefile.PE(exe)
data=None; rva=None
for sec in pe.sections:
    if b'.text' in sec.Name:
        data=sec.get_data(); rva=sec.VirtualAddress; break
md = Cs(CS_ARCH_X86, CS_MODE_32)
md.skipdata = True
img = pe.OPTIONAL_HEADER.ImageBase
cnt=0
with open(out,'w',encoding='utf-8') as f:
    for insn in md.disasm(data, img+rva):
        if insn.mnemonic == 'cmp':
            try:
                if insn.operands:
                    op = insn.operands[1] if len(insn.operands)>1 else insn.operands[0]
            except:
                continue
            # check by reg/imm? capstone API varies
            try:
                # capstone 5: access via .type
                pass
            except:
                pass
print(cnt)
