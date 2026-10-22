import re

with open(r'G:\Games\CnMod 1.2\Data\logic\goodtypes.ini', 'r', encoding='cp1250') as f:
    content = f.read()

content = content.split('<CULTURES_CIF_BEGIN>')[1]
blocks = content.split('[goodtype]')

for i, block in enumerate(blocks):
    if not block.strip():
        continue
    # Search for any of our target goodtype numbers
    for target in ['5', '24', '66', '67']:
        if f'goodtype {target}' in block:
            gt = re.search(r'goodtype\s+(\d+)', block)
            nm = re.search(r'name\s+"([^"]+)"', block)
            lt = re.search(r'landscapetype\s+(\d+)', block)
            if gt and nm and lt:
                print(f'Good {gt.group(1)}: {nm.group(1)}, landscape={lt.group(1)}')
            break