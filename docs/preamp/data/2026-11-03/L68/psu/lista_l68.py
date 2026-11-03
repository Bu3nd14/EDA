#!/usr/bin/env python3
"""L68: the list of the FMEA runs of the comparator timer's parts, its connectors and its test points
(NC-078), for corri_lista_an.sh. Every line: <caso> oggi <options>, the options of lista_l58a.py (BASE).

  guasti     f_<...>_<evento> from modi.RIGHE_L68 (x the eight events of EVENTI_L58B), RIGHE_L68C
             (x EVENTI_L68C), RIGHE_L68T (muss)
  prova      one case per new primitive use, before the long list

The healthy runs to compare against are L64b's (an_l64b.csv: oggi/<sequence>); the two bases run here
(seq/base/accensione, seq/base/fredda) give them back column for column.

Usage: lista_l68.py [prova] > lista.txt
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modi  # noqa: E402

BASE = ("sorgente --n2n7002 ds --tss 3.0 --comparatore tarato --ritenuta costruttore "
        "--bat54 costruttore --sonde-piu")
casi = []
for b, _r, _m, _p, _w in modi.RIGHE_L68:
    casi += ["%s_%s" % (b, e) for e in modi.EVENTI_L58B]
for b, _r, _m, _p, _w in modi.RIGHE_L68C:
    casi += ["%s_%s" % (b, e) for e in modi.EVENTI_L68C]
casi += ["%s_muss" % b for b, _r, _m, _p, _w in modi.RIGHE_L68T]
PROVA = ["f_u513a_cieco_accs", "f_u513_alim_accs", "f_q513_aperto_accs", "f_j4sw_aperto_muss",
         "f_tp502_corto_muss", "f_d533_aperto_freds"]
if sys.argv[1:] == ["prova"]:
    assert all(c in casi for c in PROVA)
    casi = PROVA
elif sys.argv[1:] == ["resto"]:
    casi = [c for c in casi if c not in PROVA]
print("\n".join("%s oggi %s" % (c, BASE) for c in casi))
