#!/usr/bin/env python3
"""L60c2: la sonda delle corse di V2 che si fermano («Timestep too small» su lsk489a nel blocco A,
sempre a x,024 s: l'istante in cui si muovono i contatti del jack). Solo stdlib, /usr/bin/python3 -I.

Uso: sonda_v2.py CORSA...      (es. mh01_1k_iii) scrive run/sonda_v2/<variante>/corsa_<CORSA>.cir

Varianti, ciascuna dalla corsa fallita in run/v2/ (la prima prova di corri.sh):
  ck01   il contatto aperto di K3 a 0,1 pF, quello del G6K: se passa, il guasto numerico viene dal
         contatto da 1 pF;
  gear   il contatto da 1 pF col metodo gear (option method=gear prima di tran).
"""
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L60C2 = os.path.dirname(QUI)
for corsa in sys.argv[1:]:
    src = open(os.path.join(L60C2, "run", "v2", "corsa_%s.cir" % corsa)).read()
    assert src.count("alter cks2 = 1p\n") == 1 and src.count("\ntran ") == 1
    for var in ("ck01", "gear"):
        t = src
        if var == "ck01":
            t = t.replace("alter cks2 = 1p\n", "alter cks2 = 0.1p\n")
        else:
            t = t.replace("\ntran ", "\noption method=gear\ntran ")
        d = os.path.join(L60C2, "run", "sonda_v2", var)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "corsa_%s.cir" % corsa), "w").write(t)
        print(os.path.join(d, "corsa_%s.cir" % corsa))
