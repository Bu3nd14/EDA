#!/usr/bin/env python3
"""L54a: the energy and the time over 1 W of R550 (4.7 ohm, raw_p - raw_pr) and R552 (47 ohm,
mains_coil - mains_sink) after the event of a fault case - what the firmware's K501 bounds today
(NC-073, ADR-094) and the analog timer must bound too. Solo stdlib.
/usr/bin/python3 -I energia.py <te> <out.txt> [...]"""
import sys

te = float(sys.argv[1])
for path in sys.argv[2:]:
    with open(path) as f:
        nomi = f.readline().split()
        col = {n: k for k, n in enumerate(nomi)}
        rr = [("R550", "v(raw_p)", "v(raw_pr)", 4.7), ("R552", "v(mains_coil)", "v(mains_sink)", 47.0)]
        rr = [x for x in rr if x[1] in col and x[2] in col]
        e = dict.fromkeys([x[0] for x in rr], 0.0)
        pmax = dict.fromkeys(e, 0.0)
        sopra = dict.fromkeys(e, 0.0)
        tp = None
        for r in f:
            x = [float(v) for v in r.split()]
            t = x[0]
            if tp is not None and t >= te:
                dt = t - tp
                for nome, a, b, ro in rr:
                    p = (x[col[a]] - x[col[b]]) ** 2 / ro
                    e[nome] += p * dt
                    pmax[nome] = max(pmax[nome], p)
                    if p > 1.0:
                        sopra[nome] += dt
            tp = t
    print(path.split("/")[-2], " ".join("%s %.3f J, picco %.1f W, oltre 1 W per %.0f ms"
                                        % (n, e[n], pmax[n], 1e3 * sopra[n]) for n in e))
