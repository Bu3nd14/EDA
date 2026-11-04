#!/usr/bin/env python3
"""L58a2: the arming of the latch at a cold power-up, read as a crossing.

analizza_mc.py takes t_arm as the first sample after TE with v(at_t2s) > 2.5 V (no VREF probe in these
decks). If AT_T2S is already above 2.5 V at TE, that first sample counts as armed (arm_pg_ms ~ -t_pg).
Here: AT_T2S at TE, and t_arm as the first UPWARD crossing of 2.5 V after TE (from below).

Solo stdlib. /usr/bin/python3 -I armo.py <seq_dir>/<caso> [...]
"""
import os
import sys

TE = 3.0


def leggi(path):
    with open(path) as f:
        nomi = f.readline().split()
        righe = [list(map(float, r.split())) for r in f if r.strip()]
    return {n: [r[k] for r in righe] for k, n in enumerate(nomi)}


for d in sys.argv[1:]:
    fs = [f for f in os.listdir(d) if f.endswith("_g1_out.txt")]
    w = leggi(os.path.join(d, fs[0]))
    t, a, pg = w["time"], w["v(at_t2s)"], w["v(at_pg)"]
    kte = min(range(len(t)), key=lambda k: abs(t[k] - TE))
    tpg = next((x for k, x in enumerate(t) if x >= TE and pg[k] > 2.5), None)
    tarm = next((x for k, x in enumerate(t) if x >= TE and k > 0 and a[k - 1] <= 2.5 < a[k]), None)
    nome = os.path.basename(os.path.dirname(d.rstrip("/"))) + "/" + os.path.basename(d.rstrip("/"))
    print("%-34s AT_T2S a TE %.3f V, max prima di TE %.3f V; t_pg %s ms; salita oltre 2,5 V %s ms; "
          "arm-pg %s ms" % (
              nome, a[kte], max(a[:kte + 1]),
              "-" if tpg is None else "%.1f" % ((tpg - TE) * 1e3),
              "-" if tarm is None else "%.1f" % ((tarm - TE) * 1e3),
              "-" if (tpg is None or tarm is None) else "%.1f" % ((tarm - tpg) * 1e3)))
