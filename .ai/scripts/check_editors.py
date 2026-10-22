import pefile
for fn in ['Edytor podstawowy.exe', "Remik's Editor.exe"]:
    try:
        pe = pefile.PE(rf'G:\\Games\\CnMod 1.2\\{fn}')
        print(fn, hex(pe.OPTIONAL_HEADER.ImageBase), pe.FILE_HEADER.TimeDateStamp)
    except Exception as e:
        print(e)
