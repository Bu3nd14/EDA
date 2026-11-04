#!/usr/bin/env python3
"""L58b: the second list of the series pair at 1M:10k (lista_s1m.txt was the first):
  rete   the pair without faults, Q501's gate-drain short and Q509's short, at mains -10 / +10 %
         (--rete 0.9 / 1.1), against accensione, spegnimento_l, perdita, inserimento
  R      the two gate resistors open (modi.RIGHE_SERIE_R) against the eight events, mains nominal
Usage: lista_serie2.py > lista_s1m2.txt
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modi  # noqa: E402

BASE = ("sorgente --n2n7002 ds --tss 3.0 --comparatore tarato --ritenuta costruttore "
        "--bat54 costruttore --sonde-piu --q501serie 1e6:10000")
righe = []
for f, et in ((0.9, "m10"), (1.1, "p10")):
    for e, s in (("accs", "accensione"), ("spls", "spegnimento_l"), ("perds", "perdita"),
                 ("inss", "inserimento")):
        righe.append("%s l58b_s1m_base_%s %s --rete %g" % (s, et, BASE, f))
        for b in ("f_q501a_gd", "f_q509_corto"):
            righe.append("%s_%s l58b_s1m_%s %s --rete %g" % (b, e, et, BASE, f))
for b, _r, _m, _p, _w in modi.RIGHE_SERIE_R:
    for e in modi.EVENTI_L58B:
        righe.append("%s_%s l58b_s1m %s" % (b, e, BASE))
print("\n".join(righe))
