#!/usr/bin/env python3
"""L54b3b: L54b3a's safety list on today's source (the n_ lines of L54b3a/lista_nuovo.txt) at a
temperature, with the diodes' maximum leakage at that temperature (README, "Le perdite massime").

/usr/bin/python3 -I lista_temp.py <lista_nuovo.txt> <0|60> [opzioni in piu']
The label n_... becomes t<T>_...; --temp, --perdita and --sonde-piu are appended.
"""
import sys

PERDITE = {
    0: "D538:5.5e-9,D535:2.9e-9,D536:2.9e-9,D541:2.9e-9,D533:0.4e-6,D534:2.9e-9,D537:0.4e-6",
    60: "D538:210e-9,D535:11e-9,D536:11e-9,D541:11e-9,D533:19e-6,D534:11e-9,D537:19e-6",
}
f, t = sys.argv[1], int(sys.argv[2])
PRE = sys.argv[3] if len(sys.argv) > 3 else ""  # v_: after ADR-105
piu = " ".join(sys.argv[4:])
for r in open(f):
    p = r.split()
    if len(p) < 3 or not p[1].startswith("n_"):
        continue
    p[1] = "%st%d_%s" % (PRE, t, p[1][2:])
    extra = " --temp %d --perdita %s" % (t, PERDITE[t])
    if "--sonde-piu" not in p:
        extra += " --sonde-piu"
    print(" ".join(p) + extra + (" " + piu if piu else ""))
