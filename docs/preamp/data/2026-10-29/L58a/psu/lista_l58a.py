#!/usr/bin/env python3
"""L58a: the list of the FMEA rows of the timer's new parts (R585, D534 / D535 / D536 / D541), for
corri_lista_an.sh. Every line: <caso> <etichetta> sorgente <options>, the options of L54b3b's
lista_verifica.txt plus --sonde-piu (the base of Q513).

  base     the seven events, no fault (the reference of every row)
  guasti   f_<ref>_<aperto|corto>_<evento>, from modi.RIGHE_TIMER (latent, from t = 0)
  perdita  each BAS416 with 1 uA of reverse leakage on top of its model (--perdita): the ASSUMPTION
           of the row, a damaged junction ~12 x the datasheet's 80 nA at 150 C (ADR-070, «Da
           riaprire se»: no table gives a leakage mode)
  deriva   R585 at 2 x (66k): the drift of FMD-2016 taken at its worst direction (AT_F held less)

Usage: lista_l58a.py [prova] > lista.txt
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modi  # noqa: E402

BASE = ("sorgente --n2n7002 ds --tss 3.0 --comparatore tarato --ritenuta costruttore "
        "--bat54 costruttore --sonde-piu")
EV = modi.EVENTI_TIMER
righe = []
if sys.argv[1:] == ["prova"]:
    # the known answers: the base power-up as L54b3b's v_sorgente, and R585 open (ADR-103)
    righe = ["accensione l58a_base %s" % BASE, "fredda l58a_base %s" % BASE,
             "f_r585_aperto_accs l58a %s" % BASE, "f_r585_aperto_freds l58a %s" % BASE]
else:
    for e, s in EV.items():
        righe.append("%s l58a_base %s" % (s, BASE))
    for b, _r, _m, _p, _w in modi.RIGHE_TIMER:
        for e in EV:
            righe.append("%s_%s l58a %s" % (b, e, BASE))
    for d in ("D534", "D535", "D536", "D541"):
        for e, s in EV.items():
            righe.append("%s l58a_perdita_%s %s --perdita %s:1e-6" % (s, d.lower(), BASE, d))
    for e, s in EV.items():
        righe.append("%s l58a_r585x2 %s --valore R585=66k" % (s, BASE))
print("\n".join(righe))
