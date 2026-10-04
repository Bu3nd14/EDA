"""varianti.py - L47b2b1: il collasso del passo a 20 Hz con le curve C ed E (limitations #42, #38).

Le corse a 20 Hz della matrice «curve» con la serie in curva C o E si fermano a t = 21,4 ms su
«Timestep too small ... trouble with lsk489a-instance j.xa.jq110a», anche il riferimento «mai»
(cella in gioco, ferma). Regola di #38: un'opzione di convergenza si sceglie PROVANDOLA, sul deck
che fallisce e su uno che passava, contando i fallimenti e confrontando le cifre.

Scrive, per ogni deck dato, le varianti con una riga `option ...` subito prima della `tran`:
    /usr/bin/python3 varianti.py <corsa.cir> [<corsa.cir> ...]
-> <qui>/<nome>__<variante>.cir
"""
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
VARIANTI = {
    "base": None,
    "gear": "option method=gear",
    "itl4": "option itl4=100",
    "trtol1": "option trtol=1",
    "gmin": "option gmin=1e-13",
    # seconda sonda: E cev_20 e ch2_20 si fermano alla chiusura del rele' (t = 4,5 s) anche con
    # trtol=1 (il deck ha gia' la riga di aggiungi_trtol.py: queste si sommano)
    "trtol05": "option trtol=0.5",
    "trtol02": "option trtol=0.2",
}

for p in sys.argv[1:]:
    righe = open(p).read().splitlines()
    k = next(i for i, r in enumerate(righe) if r.startswith("tran "))
    # la cartella nel nome: corsa_cmai_20 esiste in curve_CC e in curve_DD
    nome = "%s_%s" % (os.path.basename(os.path.dirname(os.path.abspath(p))),
                      os.path.splitext(os.path.basename(p))[0])
    for v, opz in VARIANTI.items():
        r = list(righe)
        if opz:
            r.insert(k, opz)
        # il .dat nella cartella della sonda, con il nome della variante
        r = [x.replace("wrdata ", "wrdata %s__%s_" % (nome, v), 1) if x.startswith("wrdata ") else x
             for x in r]
        out = os.path.join(QUI, "%s__%s.cir" % (nome, v))
        open(out, "w").write("\n".join(r) + "\n")
        print(out)
