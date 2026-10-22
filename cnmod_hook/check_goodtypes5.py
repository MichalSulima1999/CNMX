import re

with open(r'G:\Games\CnMod 1.2\Data\logic\goodtypes.ini', 'r', encoding='cp1250') as f:
    content = f.read()

# Remove CIF header
if '<CULTURES_CIF_BEGIN>' in content:
    content = content.split('<CULTURES_CIF_BEGIN>')[1]

blocks = re.split(r'\[goodtype\]', content)

print(f'Total goodtypes: {len(blocks)-1}')

for i, block in enumerate(blocks):
    if not block.strip():
        continue
    gt_match = re.search(r'goodtype\s+(\d+)', block)
    name_match = re.search(r'name\s+"([^"]+)"', block)
    lt_match = re.search(r'landscapetype\s+(\d+)', block)
    if gt_match and name_match and lt_match:
        gt = gt_match.group(1)
        name = name_match.group(1)
        lt = lt_match.group(1)
        if gt in ['5', '24', '66', '67']:
            print(f'Good {gt}: {name}, landscape={lt}')