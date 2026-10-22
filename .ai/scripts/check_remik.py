import pefile
fn = r"G:\\Games\\CnMod 1.2\\Remik's Editor.exe"
pe = pefile.PE(fn)
for sec in pe.sections:
    if b'.text' in sec.Name:
        data = sec.get_data()
        rva = sec.VirtualAddress
        break
img = pe.OPTIONAL_HEADER.ImageBase
ts = img + rva
for va in [0x41DF9C,0x41EDF4,0x40A648]:
    off = va-ts
    print(hex(va), data[off:off+3].hex())
