import re

with open(r'G:\Games\CnMod 1.2\Data\logic\goodtypes.ini', 'r', encoding='cp1250') as f:
    data = f.read()

print('Total goodtypes:', len(re.findall(r'goodtype \d+', data)))

# Check what landscape types exist
blocks = re.split(r'\[goodtype\]', data)
landscape_types = set()
for block in blocks:
    lt_match = re.search(r'landscapetype\s+(\d+)', block)
    if lt_match:
        landscape_types.add(int(lt_match.group(1)))

print('Landscape types used:', sorted(landscape_types))

# Check goodtype 5 (drewno/wood) and 24 (cegła/brick)
for i, block in enumerate(blocks):
    gt_match = re.search(r'goodtype\s+(\d+)', block)
    name_match = re.search(r'name\s+"([^"]+)"', block)
    lt_match = re.search(r'landscapetype\s+(\d+)', block)
    if gt_match and lt_match:
        gt = gt_match.group(1)
        if gt in ['5', '24', '2', '6']:
            name = name_match.group(1) if name_match else 'unknown'
            print(f'Good {gt}: {name}, landscape={lt_match.group(1)}')