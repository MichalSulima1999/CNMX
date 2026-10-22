import re

with open(r'G:\Games\CnMod 1.2\Data\logic\goodtypes.ini', 'r', encoding='cp1250') as f:
    content = f.read()

content = content.split('<CULTURES_CIF_BEGIN>')[1]
blocks = content.split('[goodtype]')

for b in blocks:
    if not b.strip():
        continue
    if 'type 5' in b or 'type 66' in b or 'type 24' in b or 'type 67' in b:
        nm = re.search(r'name "([^"]+)"', b)
        tp = re.search(r'type\s+(\d+)', b)
        lt = re.search(r'landscapetype\s+(\d+)', b)
        if tp and nm and lt:
            print(f'Type {tp.group(1)}: {nm.group(1)}, landscape={lt.group(1)}')