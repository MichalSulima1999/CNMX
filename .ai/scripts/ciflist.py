import re, sys
path = sys.argv[1]
key = sys.argv[2]
sec = sys.argv[3]
d = open(path, 'rb').read().decode('cp1250', errors='replace')
parts = re.split(r'(?m)^%01%', d)
out = []
for s in parts:
    if not s.startswith(sec):
        continue
    t = re.search(r'(?m)^%02%type\s+(\d+)', s)
    n = re.search(r'(?m)^%02%name\s+"([^"]*)"', s)
    out.append((int(t.group(1)) if t else None, n.group(1) if n else '?'))
print('count', len(out))
used = sorted(t for t, _ in out if t)
print('used indices:', used)
for t, n in out:
    print(' ', t, n)
