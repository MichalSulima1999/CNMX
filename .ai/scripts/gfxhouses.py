import re, collections
d = open(r'CN.PLMOD\budynki12\houses\houses.ini', 'rb').read().decode('cp1250', errors='replace')
secs = re.split(r'(?m)^\[', d)
rows = []
for s in secs:
    if not s.startswith('GfxHouse]'):
        continue
    lt = re.search(r'(?mi)^LogicType\s+(-?\d+)\s+(-?\d+)', s)
    nm = re.search(r'(?mi)^EditName\s+"([^"]*)"', s)
    tb = re.search(r'(?mi)^LogicTribeType\s+(-?\d+)', s)
    rows.append((
        nm.group(1) if nm else '?',
        int(lt.group(1)) if lt else None,
        int(lt.group(2)) if lt else None,
        int(tb.group(1)) if tb else None,
    ))
print('total GfxHouse:', len(rows))
c = collections.Counter((r[1], r[2]) for r in rows)
for k, v in sorted(c.items(), key=lambda x: (x[0][0] is None, x[0][0], x[0][1])):
    print('  LogicType %s -> %d entries' % (k, v))
print()
bytype = collections.defaultdict(list)
for r in rows:
    bytype[r[2]].append(r[0])
for t in sorted(bytype):
    print('type %-4s : %s' % (t, ', '.join(bytype[t][:8])))
