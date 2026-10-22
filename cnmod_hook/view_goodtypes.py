with open(r'G:\Games\CnMod 1.2\Data\logic\goodtypes.ini', 'r', encoding='cp1250') as f:
    content = f.read()
print(len(content), 'chars')
print(content[:2000])