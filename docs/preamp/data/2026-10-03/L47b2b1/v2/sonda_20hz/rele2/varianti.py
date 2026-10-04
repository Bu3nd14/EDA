"""varianti.py (rele2) - L47b2b1: la terza sonda sul collasso del passo di E cev_20 / ch2_20 alla
chiusura del rele' al jack (t = 4,5 s), che nessuna opzione della seconda sonda ripara: rshunt
(#38: regge, ma aggiunge una conduttanza a ogni nodo) e il passo massimo piu' corto (7 e 5 us,
come le corse «pav» di V2). Il deck ha gia' trtol=1 (aggiungi_trtol.py).

    /usr/bin/python3 varianti.py <corsa.cir>   -> <qui>/<cartella>_<nome>__<variante>.cir
"""
import os
import re
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
VARIANTI = {
    "rshunt": ("option rshunt=1e12", None),
    "tmax7": (None, 7e-6),
    "tmax5": (None, 5e-6),
    "rshunt_tmax7": ("option rshunt=1e12", 7e-6),
}

for p in sys.argv[1:]:
    righe = open(p).read().splitlines()
    k = next(i for i, r in enumerate(righe) if r.startswith("tran "))
    nome = "%s_%s" % (os.path.basename(os.path.dirname(os.path.abspath(p))),
                      os.path.splitext(os.path.basename(p))[0])
    for v, (opz, tmax) in VARIANTI.items():
        r = list(righe)
        if tmax:
            parti = r[k].split()                      # tran tstep tstop tstart tmax
            parti[1], parti[4] = "%g" % tmax, "%g" % tmax
            r[k] = " ".join(parti)
        if opz:
            r.insert(k, opz)
        r = [x.replace("wrdata ", "wrdata %s__%s_" % (nome, v), 1) if x.startswith("wrdata ") else x
             for x in r]
        out = os.path.join(QUI, "%s__%s.cir" % (nome, v))
        open(out, "w").write("\n".join(r) + "\n")
        print(out)
