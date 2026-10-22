with open(r'G:\Games\CnMod 1.2\Data\logic\goodtypes.ini', 'r', encoding='cp1250') as f:
    content = f.read()

print(f'File length: {len(content)}')
print(f'Contains "goodtype 66": {"goodtype 66" in content}')
print(f'Contains "goodtype 5": {"goodtype 5" in content}')
print(f'Contains "goodtype": {"goodtype" in content}')
print(f'Contains "[goodtype]": {"[goodtype]" in content}')

# Print first 2000 chars
print('\nFirst 1000 chars:')
print(content[:1000])

# Find all occurrences of "goodtype"
import re
matches = list(re.finditer(r'goodtype\s+\d+', content))
print(f'\nTotal "goodtype N" matches: {len(matches)}')
for m in matches[:10]:
    print(f'  At {m.start()}: {content[m.start():m.end()+50]}')