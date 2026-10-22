import re
d = open(r'CN.PLMOD\types\houses.ini', 'rb').read().decode('cp1250', errors='replace')
secs = re.split(r'(?m)^(?=\[)', d)
n = 0
for s in secs:
    if 'logichousetype' not in s.split('\n')[0]:
        continue
    n += 1
    def g(k):
        m = re.search(r'(?mi)^%s\s+(.*)$' % k, s)
        return m.group(1).strip() if m else '-'
    keys = re.findall(r'(?mi)^(\w+)', s)
    print('%2d | name=%-28s logictype=%-3s maintype=%-3s workers=%d stock=%d | keys=%s' % (
        n, g('debugname').strip('"'), g('logictype'), g('logicmaintype'),
        len(re.findall(r'(?mi)^logicworker', s)),
        len(re.findall(r'(?mi)^logicstock', s)),
        ','.join(sorted(set(keys)))))
