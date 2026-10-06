import sys
f = open(sys.argv[1])
head = f.readline().split()
rows = []
for r in f:
    v = r.split()
    if len(v) == len(head):
        rows.append([float(x) for x in v])
for tt in [float(x) for x in sys.argv[2:]]:
    r = min(rows, key=lambda x: abs(x[0] - tt))
    print("t=%.4f " % r[0] + " ".join("%s=%.4g" % (h, x) for h, x in zip(head[1:], r[1:])))
