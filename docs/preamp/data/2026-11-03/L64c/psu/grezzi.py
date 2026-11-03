#!/usr/bin/env python3
"""L54b3a: the raws (RAW_P, RAW_M, RAW_V) where the regulators hold and where they let go.
For each run: the raws' valley (min of RAW_P and RAW_V, max of RAW_M) over 2.8-3.0 s (steady, in
music, before TE), and their valley over the 20 ms before V+ first falls below 14.8 V after TE (V+ is 14.98 V in regulation, behind the RC cells)
(the + regulator out of regulation; empty if it never does).
Solo stdlib. /usr/bin/python3 -I grezzi.py <seq_dir>/<caso> [...]"""
import os
import sys


def leggi(path):
    with open(path) as f:
        nomi = f.readline().split()
        righe = [list(map(float, r.split())) for r in f if r.strip()]
    return {n: [r[k] for r in righe] for k, n in enumerate(nomi)}


print("caso,p_regime,m_regime,v_regime,t_uscita_ms,p_uscita,m_uscita,v_uscita")
for d in sys.argv[1:]:
    fs = [f for f in os.listdir(d) if f.endswith("_g1_out.txt")]
    w = leggi(os.path.join(d, fs[0]))
    t, p, m, v, vp = w["time"], w["v(raw_p)"], w["v(raw_m)"], w["v(raw_v)"], w["v(vplus)"]
    k0 = [k for k in range(len(t)) if 2.8 <= t[k] <= 3.0]
    reg = (min(p[k] for k in k0), max(m[k] for k in k0), min(v[k] for k in k0))
    ku = next((k for k in range(len(t)) if t[k] > 3.0 and vp[k] < 14.8), None)
    if ku is None:
        usc = ("", "", "", "")
    else:
        kk = [k for k in range(len(t)) if t[ku] - 0.02 <= t[k] <= t[ku]]
        usc = (round((t[ku] - 3.0) * 1e3, 1), round(min(p[k] for k in kk), 3),
               round(max(m[k] for k in kk), 3), round(min(v[k] for k in kk), 3))
    nome = os.path.basename(os.path.dirname(d.rstrip("/"))) + "/" + os.path.basename(d.rstrip("/"))
    print(",".join(str(x) for x in (nome,) + tuple(round(x, 3) for x in reg) + usc))
