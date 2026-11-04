"""L54b2: i valori di alcune colonne di un *_out.txt (wrdata con wr_vecnames e wr_singlescale) a
certi istanti. Uso: sonda_nodi.py <out.txt> <t1,t2,...> <col1> [col2 ...]  (i nomi come nel file,
per esempio v(at_pg))."""
import sys

path, ts, cols = sys.argv[1], [float(x) for x in sys.argv[2].split(",")], sys.argv[3:]
with open(path) as f:
    head = f.readline().split()
    idx = [head.index(c) for c in cols]
    want = list(ts)
    print("%10s " % "t (s)" + " ".join("%12s" % c for c in cols))
    for line in f:
        p = line.split()
        t = float(p[0])
        while want and t >= want[0]:
            print("%10.4f " % t + " ".join("%12.4f" % float(p[i]) for i in idx))
            want.pop(0)
        if not want:
            break
