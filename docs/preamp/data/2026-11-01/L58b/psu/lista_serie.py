#!/usr/bin/env python3
"""L58b: the list of the series pair (genera_tb_psu.py --q501serie 10000), for corri_lista_an.sh.
  base   the pair without faults against the seven events of the timer and inserimento: the
         regression against l58b_base / L58a's l58a_base (same verdicts, jack times within 0.1 ms)
  guasti each of the four modes of the pair (modi.RIGHE_SERIE) against the same eight events
Usage: lista_serie.py > lista_serie.txt
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modi  # noqa: E402

BASE = ("sorgente --n2n7002 ds --tss 3.0 --comparatore tarato --ritenuta costruttore "
        "--bat54 costruttore --sonde-piu --q501serie 10000")
righe = ["%s l58b_serie_base %s" % (s, BASE) for s in modi.EVENTI_L58B.values()]
for b, _r, _m, _p, _w in modi.RIGHE_SERIE:
    for e in modi.EVENTI_L58B:
        righe.append("%s_%s l58b_serie %s" % (b, e, BASE))
print("\n".join(righe))
