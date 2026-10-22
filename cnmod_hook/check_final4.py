with open(r'G:\Games\CnMod 1.2\Data\logic\goodtypes.ini', 'r', encoding='cp1250') as f:
    content = f.read()

# Find all occurrences of 'goodtype 66'
import re
for m in re.finditer(r'goodtype 66', content):
    start = max(0, m.start() - 200)
    end = min(len(content), m.end() + 300)
    print(f'Found at {m.start()}:')
    print(content[start:end])
    print('---')

# Also check for 'goodtype 5'
for m in re.finditer(r'goodtype 5\b', content):
    start = max(0, m.start() - 200)
    end = min(len(content), m.end() + 300)
    print(f'Found goodtype 5 at {m.start()}:')
    print(content[start:end])
    print('---')