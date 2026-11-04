#!/usr/bin/env python3
"""L70, S1: the RC cell of a block shorted (f_c145_corto_*, 10 ohm = two 20 ohm 0207 from VPLUS to
ground) without the latch: the steady state of the last 200 ms. U501's dissipation is
(v(raw_pr) - v(vplus_reg)) x its current i(v.xu501.vsns); R550 from its two nodes; each 20 ohm from
v(vplus)^2 / 20. Tj of U501 with SBVS204G's 32.5 C/W (the figure ADR-092 used) at 60 C of air.

    /usr/bin/python3 -I script/cella_s1.py   -> cella_s1.csv
"""
import csv
import glob
import os

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)


def leggi(path):
    with open(path) as f:
        nomi = f.readline().split()
        righe = [list(map(float, r.split())) for r in f if r.strip()]
    return {n: [r[k] for r in righe] for k, n in enumerate(nomi)}


out = []
for d in sorted(glob.glob(os.path.join(L, "seq", "guasti_*", "f_c145_corto_*"))):
    w = leggi(glob.glob(os.path.join(d, "*_g1_out.txt"))[0])
    t = w["time"]
    k = [i for i, x in enumerate(t) if x >= t[-1] - 0.2]
    m = lambda xs: sum(xs[i] for i in k) / len(k)   # noqa: E731
    vpr, vp = m(w["v(raw_pr)"]), m(w["v(vplus)"])
    vreg = m(w["v(vplus_reg)"]) if "v(vplus_reg)" in w else vp
    iu = abs(m(w["i(v.xu501.vsns)"]))
    i550 = [(a - b) / 4.7 for a, b in zip(w["v(raw_p)"], w["v(raw_pr)"])]
    p550 = sum(i550[i] ** 2 * 4.7 for i in k) / len(k)
    pu = (vpr - vreg) * iu
    out.append(dict(variante=d.split(os.sep)[-2], caso=os.path.basename(d), v_raw_pr=round(vpr, 2),
                    v_vplus=round(vp, 3), i_u501_A=round(iu, 3), P_u501_W=round(pu, 2),
                    Tj_u501_60C=round(60 + 32.5 * pu), P_r550_W=round(p550, 2),
                    P_20ohm_ciascuna_W=round(vp * vp / 20, 2)))
with open(os.path.join(L, "cella_s1.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, list(out[0]))
    w.writeheader()
    w.writerows(out)
for r in out:
    print(r)
