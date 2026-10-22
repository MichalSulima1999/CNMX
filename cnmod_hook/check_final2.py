import re

with open(r'G:\Games\CnMod 1.2\Data\logic\goodtypes.ini', 'r', encoding='cp1250') as f:
    content = f.read()

content = content.split('<CULTURES_CIF_BEGIN>')[1]
blocks = content.split('[goodtype]')

print(f'Total blocks: {len(blocks)}')

for i, block in enumerate(blocks):
    if not block.strip():
        continue
    # Check if block contains our target goodtypes
    if 'goodtype 5' in block or 'goodtype 24' in block or 'goodtype 66' in block or 'goodtype 67' in block:
        print(f'=== Block {i} ===')
        print(block[:300])
        print('---')