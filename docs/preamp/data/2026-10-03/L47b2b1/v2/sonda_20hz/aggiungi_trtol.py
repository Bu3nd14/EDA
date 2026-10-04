"""aggiungi_trtol.py - L47b2b1 (#38, #42): mette `option trtol=1` prima della `tran` nelle corse
date (corsa_*.cir di una cartella di V2), con un commento che dice perche'. Sul posto: la corsa
si rifa' con lo stesso nome, e i suoi .dat restano dove analizza_par.py li cerca.

    /usr/bin/python3 aggiungi_trtol.py <corsa.cir> [...]
"""
import sys

RIGA = "option trtol=1"
NOTA = ("* L47b2b1: trtol=1 (sonda_20hz/: con la NSL-32SR3 in curva C o E ferma in gioco, a 20 Hz il "
        "passo collassa a 21,4 ms; trtol=1 corre, e su curva D ridà le stesse cifre, #38)")
for p in sys.argv[1:]:
    r = open(p).read().splitlines()
    if RIGA in r:
        print("gia' fatto:", p)
        continue
    k = next(i for i, x in enumerate(r) if x.startswith("tran "))
    r[k:k] = [NOTA, RIGA]
    open(p, "w").write("\n".join(r) + "\n")
    print("trtol=1 in", p)
