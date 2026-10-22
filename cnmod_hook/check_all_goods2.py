import re

with open(r'G:\Games\CnMod 1.2\Data\logic\goodtypes.ini', 'r', encoding='cp1250') as f:
    data = f.read()

blocks = re.split(r'\[goodtype\]', data)

for i, block in enumerate(blocks):
    if 'landscapetype' in block:
        # Extract goodtype and landscape type
        gt_match = re.search(r'goodtype\s+(\d+)', block)
        lt_match = re.search(r'landscapetype\s+(\d+)', block)
        name_match = re.search(r'name\s+"([^"]+)"', block)
        if gt_match and lt_match:
            gt = gt_match.group(1)
            lt = lt_match.group(1)
            name = name_match.group(1) if name_match else 'unknown'
            print(f'Good {gt}: {name}, landscape={lt}')