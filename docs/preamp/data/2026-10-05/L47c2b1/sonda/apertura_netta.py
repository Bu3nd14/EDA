"""apertura_netta.py - L47c2b1, terza prova della sonda: il contatto in serie (BKSR) che si APRE
senza richiudersi (il deviatore: il COM lascia il NO e va verso il NC; i rimbalzi sono degli
urti, cioe' della chiusura del NC all'inserimento e del NO al rilascio). Si tocca solo il primo
pwl di BKSR (l'apertura); la chiusura del rilascio resta coi rimbalzi di MAKE. Variante «nb».

    /usr/bin/python3 apertura_netta.py
"""
import os

QUI = os.path.dirname(os.path.abspath(__file__))
MATRICE = os.path.join(QUI, "..", "matrice_interruttore")
VECCHIO = "pwl(time - V(NKSA), -1e4,1, 0,1, 1u,0, 400u,0, 401u,1, 600u,1, 601u,0, 1e4,0)"
NUOVO = "pwl(time - V(NKSA), -1e4,1, 0,1, 1u,0, 1e4,0)"
d = os.path.join(QUI, "nb")
os.makedirs(d, exist_ok=True)
for c in ("mev_20_iii", "mev_1k_iii"):
    r = open(os.path.join(MATRICE, "corsa_%s.cir" % c)).read()
    if r.count(VECCHIO) != 1:
        raise SystemExit("%s: il pwl d'apertura di BKSR non c'e' una volta sola" % c)
    r = r.replace(VECCHIO, NUOVO)
    open(os.path.join(d, "corsa_%s.cir" % c), "w").write(r)
    print("nb:", c)
