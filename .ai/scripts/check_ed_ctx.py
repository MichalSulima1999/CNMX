from capstone import Cs, CS_ARCH_X86, CS_MODE_32
import pefile

fn = 'Edytor podstawowy.exe'
pe = pefile.PE(rf'G:\\Games\\CnMod 1.2\\{fn}')
for sec in pe.sections:
    if b'.text' in sec.Name:
        data = sec.get_data()
        rva = sec.VirtualAddress
        break
md = Cs(CS_ARCH_X86, CS_MODE_32)
img = pe.OPTIONAL_HEADER.ImageBase
ts = img + rva
for va in [0x41DF9C,0x41EDF4,0x40A648]:
    off = va - ts
    print(f'=== {va:08X}')
    for insn in md.disasm(data[off-12:off+8], va-12):
        print(f'{insn.address:08X}: {insn.mnemonic} {insn.op_str}')
    print()
