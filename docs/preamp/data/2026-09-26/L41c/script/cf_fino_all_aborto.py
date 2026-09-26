#!/usr/bin/env python3
"""L41c: the counterfactual without D up to its abort.

cf_nodelta_l41c stops with "Timestep too small" in the input JFET (xa.jq110a)
at the jack contact's opening, 3 ms after the gain changed with the jack still
connected - and so it does with method=gear, a 1 us maximum step, or reltol
1e-5 (L41c). After the abort the .dat is all zeros (limitations #35), so
v2_metodo cannot read it. Up to the abort the samples are true. This reads
the RAW |case - reference| at the three jacks from the gain's change to the
last sample before the abort (the time is in the log), with no filter: it is
the figure's form, not V2's A_ins, and a LOWER bound of what the full run
would show (the contact's opening, when the run stops, is not in it).

Solo stdlib. /usr/bin/python3 cf_fino_all_aborto.py <corse_dir> <ponte_dir>
"""
import bisect
import json
import math
import os
import re
import sys


def leggi(path):
    t, y = [], []
    for r in open(path):
        v = r.split()
        if len(v) != 6:
            continue
        t.append(float(v[0]))
        y.append((float(v[1]), float(v[3]), float(v[5])))
    return t, y


def main(argv):
    corse, ponte = argv[1], argv[2]
    j = json.load(open(os.path.join(ponte, "cf_nodelta.json")))
    log = open(os.path.join(corse, "corsa_cf_nodelta_l41c.log")).read()
    m = re.search(r"Timestep too small; time = ([0-9.eE+-]+)", log)
    t_ab = float(m.group(1)) if m else None
    te, ye = leggi(os.path.join(corse, "cf_nodelta_l41c.dat"))
    tr, yr = leggi(os.path.join(corse, "rif_cf_nodelta_l41c.dat"))
    t0 = j["t_gain"]
    t1 = t_ab if t_ab is not None else te[-1]
    best = (0.0, None, None)
    for k in range(len(te)):
        if not (t0 <= te[k] < t1):
            continue
        i = min(bisect.bisect_left(tr, te[k]), len(tr) - 1)
        for u, nome in enumerate(("MAINJACK", "FIXJACK1", "FIXJACK2")):
            d = abs(ye[k][u] - yr[i][u])
            if d > best[0]:
                best = (d, te[k], nome)
    v, tb, u = best
    dbspl = 33.45 + 20 * math.log10(v / 100e-6) if v > 0 else float("-inf")
    print("cf_nodelta: aborto a %s s; guadagno a %.5f s, jack (tardi) a %.5f s"
          % (t_ab, j["t_gain"], j["t_jack"]))
    print("picco grezzo |ev - rif| fra il guadagno e l'aborto: %.4g V su %s a %.5f s (~%.1f dB SPL di picco a 1 m)"
          % (v, u, tb if tb else -1, dbspl))


if __name__ == "__main__":
    main(sys.argv)
