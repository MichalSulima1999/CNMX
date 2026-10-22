import re

with open(r'G:\Games\CnMod 1.2\Data\logic\goodtypes.ini', 'r', encoding='cp1250') as f:
    data = f.read()

blocks = re.split(r'\[goodtype\]', data)

for i, block in enumerate(blocks):
    gt_match = re.search(r'goodtype\s+(\d+)', block)
    name_match = re.search(r'name\s+"([^"]+)"', block)
    lt_match = re.search(r'landscapetype\s+(\d+)', block)
    produced_house = 'isProducedInHouseFlag 1' in block
    produced_map = 'isProducedOnMapFlag 1' in block
    
    if gt_match and name_match and lt_match:
        gt = gt_match.group(1)
        name = name_match.group(1)
        lt = lt_match.group(1)
        print(f'Good {gt:>3}: {name:<15} landscape={lt:>2} house={produced_house} map={produced_map}')