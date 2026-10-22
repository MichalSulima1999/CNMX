from capstone import Cs, CS_ARCH_X86, CS_MODE_32
import pefile
exe = r'G:\\Games\\CnMod 1.2\\CN.PLMOD.exe'
out = r'G:\\Games\\CnMod 1.2\\.ai\\docs\\cmp_full.txt'
pe = pefile.PE(exe)
data=None; rva=None
for sec in pe.sections:
    if b'.text' in sec.Name:
        data=sec.get_data(); rva=sec.VirtualAddress; break
md = Cs(CS_ARCH_X86, CS_MODE_32); md.detail=True
img = pe.OPTIONAL_HEADER.ImageBase
cnt=0
with open(out,'w',encoding='utf-8') as f:
    for insn in md.disasm(data, img+rva):
        if insn.mnemonic == 'cmp' and len(insn.operands)>=2:
            op = insn.operands[1]
            if op.type == 1:  # IMM
                imm = op.imm & 0xFFFFFFFF
                if imm <= 0x400:  # rozszerz trochę
                    rva_i = insn.address - img
                    f.write(f'{rva_i:08X} {insn.address:08X} 0x{imm:02X} ({imm})\n')
                    cnt+=1
print(cnt)
