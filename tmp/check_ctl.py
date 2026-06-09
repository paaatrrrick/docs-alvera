import os
for f in sorted(os.listdir(os.path.expanduser('~/workspace/fr/misc/chronicles'))):
    p = os.path.expanduser('~/workspace/fr/misc/chronicles/' + f)
    data = open(p, 'rb').read()
    bad = []
    for i, b in enumerate(data):
        if b < 9 or (10 < b < 32 and b != 13):
            bad.append((i, b))
    if bad:
        print(f, bad[:5])
print('done')
