from capstone import Cs,CS_ARCH_X86,CS_MODE_32
import pefile

for fn in ['Edytor podstawowy.exe', "Remik's Editor.exe"]:
    pe = pefile.PE(rf'G:\\Games\\CnMod 1.2\\{fn}')
    for sec in pe.sections:
        if b'.text' in sec.Name:
            data = sec.get_data()
            rva = sec.VirtualAddress
            break
    img = pe.OPTIONAL_HEADER.ImageBase
    ts = img + rva
    print(fn)
    for va in [0x41DF9C,0x41EDF4,0x40A648,0x40A648+0x100]:  # skip
        pass
    # read bytes
    for va in [0x41DF9C,0x41EDF4,0x40A648]:
        off = va-ts
        if 0<=off<len(data):
            print(' ', hex(va), data[off:off+3].hex())
        else:
            print(' x', hex(va))
    break
