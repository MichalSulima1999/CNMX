import re

with open(r'G:\Games\CnMod 1.2\Data\logic\goodtypes.ini', 'r', encoding='cp1250') as f:
    content = f.read()

print("First 500 chars:")
print(content[:500])
print("...")

# Check for [goodtype] pattern
print("\n[goodtype] count:", content.count('[goodtype]'))

# Try different split
blocks = content.split('[goodtype]')
print(f"Split by [goodtype]: {len(blocks)} blocks")

# Check first few blocks
for i, block in enumerate(blocks[:5]):
    if block.strip():
        print(f"\nBlock {i}: {block[:200]}")
        print("---")