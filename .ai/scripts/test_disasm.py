from capstone import Cs, CS_ARCH_X86, CS_MODE_32
import pefile
exe = r'G:\\Games\\CnMod 1.2\\CN.PLMOD.exe'
pe = pefile.PE(exe)
for sec in pe.sections:
    if b'.text' in sec.Name:
        data = sec.get_data()
        rva = sec.VirtualAddress
        print('found', len(data), hex(rva))
        break
else:
    print('no')