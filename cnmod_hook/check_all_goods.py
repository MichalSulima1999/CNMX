import re

with open(r'G:\Games\CnMod 1.2\Data\logic\goodtypes.ini', 'r', encoding='cp1250') as f:
    data = f.read()

blocks = re.split(r'\[goodtype\]', data)

for i, block in enumerate(blocks):
    if 'name "drewno' in block or 'name "wegiel' in block or 'name "ceg' in block:
        print(f'=== Block {i} ===')
        print(block[:500])
        print()