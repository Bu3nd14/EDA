import bisect
import sys


def leggi(p):
    f = open(p)
    head = f.readline().split()
    cols = {h: [] for h in head}
    for r in f:
        v = r.split()
        if len(v) == len(head):
            for h, x in zip(head, v):
                cols[h].append(float(x))
    return head, cols


ha, A = leggi(sys.argv[1])
hb, B = leggi(sys.argv[2])
t1 = float(sys.argv[3])
ta, tb = A["time"], B["time"]
for h in ha[1:]:
    mx, tm = 0.0, None
    for k in range(len(ta)):
        if ta[k] > t1:
            break
        i = min(bisect.bisect_left(tb, ta[k]), len(tb) - 1)
        d = abs(A[h][k] - B[h][i])
        if d > mx:
            mx, tm = d, ta[k]
    print("%-14s max|gear-trap| %.4g V a %s" % (h, mx, tm))


def primo(t, c, cond, dopo=2.0):
    for k in range(len(t)):
        if t[k] >= dopo and cond(k):
            return t[k]


for nome, X in (("gear", A), ("trap", B)):
    t = X["time"]
    vr = X["v(vrelay)"]
    jack = primo(t, X, lambda k: vr[k] - X["v(mute_cmd)"][k] < 1.2)
    gain = primo(t, X, lambda k: vr[k] - X["v(permit_cmd)"][k] < 9.6 or vr[k] < 9.6)
    v106 = primo(t, X, lambda k: X["v(vplus)"][k] < 10.6)
    print("%s: jack %.5f guadagno %.5f V+<10,6 %.5f" % (nome, jack, gain, v106))
