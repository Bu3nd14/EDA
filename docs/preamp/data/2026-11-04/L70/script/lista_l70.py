#!/usr/bin/env python3
"""L70: the runs of the two simplifications, one list (lista_l70.txt).

  1. The 32 lines of L69b's lista_l64b.txt without a fault (the healthy events of the source, at the
     mains of each line) on each variant s2 / s1 / s1s2 (varianti/psu_<v>.net): 96 runs. The label
     is the variant + L69b's mains suffix (oggi_m10 -> s2_m10). The options are L69b's plus
     --net; on s1 / s1s2 without --ritenuta costruttore (no Q513 / Q514 to give the maker's model).
     The base is L69b's an_l64b.csv, read, not rerun.
  2. The shorts on the raw side (modi.py, ADR-074's rows: C501 / C502 the reservoirs, C509 / C510 the
     regulators' pins, the four diodes of D501), at mains -10 / 0 / +10 % (musm10 / mus / musp10),
     on oggi and on s1, with --sonda-t2 (T1's secondary currents = the fuse in position A): 48 runs,
     labels guasti_oggi / guasti_s1. These rows were last run in L45d2b2b1, on another circuit:
     oggi is today's base for them.

    /usr/bin/python3 -I script/lista_l70.py
"""
import os

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
VAR = os.path.join(L, "varianti")
righe = []
for r in open(os.path.join(L, "lista_l64b.txt")):
    p = r.split()
    if not p or p[0].startswith("f_"):
        continue
    caso, etich, timer, opz = p[0], p[1], p[2], p[3:]
    assert etich.startswith("oggi"), r
    for v in ("s2", "s1", "s1s2"):
        o = list(opz)
        if v.startswith("s1"):
            i = o.index("--ritenuta")
            assert o[i + 1] == "costruttore", r
            del o[i:i + 2]
        righe.append(" ".join([caso, v + etich[4:], timer] + o
                              + ["--net", os.path.join(VAR, "psu_%s.net" % v)]))
assert len(righe) == 96, len(righe)
BASE = ["--n2n7002", "ds", "--tss", "3.0", "--comparatore", "tarato", "--bat54", "costruttore",
        "--sonde-piu", "--sonda-t2"]
for v in ("oggi", "s1"):
    for ref in ("c501", "c502", "c509", "c510", "d501a", "d501b", "d501c", "d501d"):
        for ev in ("musm10", "mus", "musp10"):
            o = (["--ritenuta", "costruttore"] if v == "oggi" else []) + BASE
            righe.append(" ".join(["f_%s_corto_%s" % (ref, ev), "guasti_" + v, "sorgente"] + o
                                  + ["--net", os.path.join(VAR, "psu_%s.net" % v)]))
assert len(righe) == 144, len(righe)
open(os.path.join(L, "lista_l70.txt"), "w").write("\n".join(righe) + "\n")
print("lista_l70.txt: %d righe" % len(righe))
