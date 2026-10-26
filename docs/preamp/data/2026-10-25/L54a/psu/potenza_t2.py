#!/usr/bin/env python3
"""L54a: the power out of T2's secondary and of T1's two windings in a window of a sequence run
made with --sonda-t2 (the mean of EMF x sense current over whole mains periods), as L41b1's timer
deck read the standby.
/usr/bin/python3 -I potenza_t2.py <out.txt> <t0> <t1>   (t1 - t0 a multiple of 20 ms)"""
import sys

path, t0, t1 = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
coppie = {"T2": ("v(t2_sec_a_e,t2_sec_b)", "i(vt2_sns)"),
          "T1a": ("v(t1_sec_aa_e)", "i(vt1a_sns)"), "T1b": ("v(t1_sec_ab_e)", "i(vt1b_sns)")}
with open(path) as f:
    nomi = f.readline().split()
    k = {n: (nomi.index(v), nomi.index(i)) for n, (v, i) in coppie.items()}
    s = dict.fromkeys(coppie, 0.0)
    n = 0
    for r in f:
        x = r.split()
        if x and t0 <= float(x[0]) < t1:
            for c, (kv, ki) in k.items():
                s[c] += float(x[kv]) * float(x[ki])
            n += 1
p = {c: 1e3 * v / n for c, v in s.items()}
print("%s %.3f-%.3f s: T2 %.2f mW, T1 %.1f mW (%.1f + %.1f), %d campioni"
      % (path.split("/")[-1], t0, t1, p["T2"], p["T1a"] + p["T1b"], p["T1a"], p["T1b"], n))
