import re
from collections import Counter
sentences = set()
for line in open('/tmp/all_prose.txt'):
    line = line.strip()
    parts = re.split(r'(?<=[.])\s+', line)
    for p in parts:
        if p: sentences.add(p)
def skel(s):
    s = re.sub(r'\b\d+\b', '#', s)
    s = re.sub(r'\b([A-Z][a-z]+)(\s+[A-Z][a-z]+)*\b', 'X', s)
    return s
ctr = Counter(skel(s) for s in sentences)
print("Distinct skeletons:", len(ctr))
for sk, c in sorted(ctr.items(), key=lambda x: -x[1]):
    print(c, '|', sk)
