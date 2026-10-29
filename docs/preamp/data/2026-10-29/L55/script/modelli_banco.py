#!/usr/bin/env python3
"""L55: le copie DI BANCO dei modelli dei finali con le capacita' di giunzione ferme a TNOM.

Perche' (vj_temperatura.py): il modello onsemi del MJE253 ha VJC = 0,0328604 V, e ngspice scala VJ con
la temperatura (SPICE3): sopra ~35 C VJC diventa negativo, la capacita' base-collettore non e' piu'
definita e la `tran` si ferma al primo punto («Timestep too small; initial timepoint»). L'op converge
perche' non usa le capacita'. Il banco a caldo del candidato non corre senza un rimedio.

Il rimedio, DICHIARATO: TLEVC=1 (le capacita' col modello lineare di ngspice) con CTE = CTC = CTS = 0 e
TVJE = TVJC = TVJS = 0: CJ e VJ restano quelli del costruttore a TNOM, a ogni temperatura. Il resto del
modello (IS, BF, le resistenze, XTI, XTB, EG) segue la temperatura come prima. Accodato in fondo alla
copia, fuori dal file del costruttore (l'ultimo valore vince, come KF/AF di ADR-057).

Le copie stanno in ../modelli_banco/, NON in models/: sono del banco, non del progetto. Si fanno anche
per i MJE15032 / MJE15033 (nomi Qmje15032F / Qmje15033F) per misurare sul caso noto quanto pesa il
congelamento: il blocco di oggi col congelamento contro il blocco di oggi senza.

Solo stdlib, /usr/bin/python3 -I.
"""
import os
import re

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
ROOT = os.path.abspath(os.path.join(L, *[".."] * 5))
OUT = os.path.join(L, "modelli_banco")
FERMO = "+ TLEVC=1 CTE=0 CTC=0 CTS=0 TVJE=0 TVJC=0 TVJS=0\n"
COPIE = (("bjt_npn/mje243.lib", "Qmje243", "Qmje243F"), ("bjt_pnp/mje253.lib", "Qmje253", "Qmje253F"),
         ("bjt_npn/mje15032.lib", "Qmje15032", "Qmje15032F"), ("bjt_pnp/mje15033.lib", "Qmje15033", "Qmje15033F"))

os.makedirs(OUT, exist_ok=True)
for rel, nome, nuovo in COPIE:
    t = open(os.path.join(ROOT, "models", rel), newline="").read()
    # solo la riga che COMINCIA con .MODEL (l'intestazione nostra cita il nome nei commenti)
    pat = re.compile(r"^\.MODEL %s " % nome, re.M | re.I)
    if len(pat.findall(t)) != 1:
        raise SystemExit("%s: .MODEL %s trovato %d volte" % (rel, nome, len(pat.findall(t))))
    t = pat.sub(".MODEL %s " % nuovo, t)
    testa = ("* L55 COPIA DI BANCO di models/%s: modello rinominato %s, e in fondo le capacita' di\n"
             "* giunzione ferme a TNOM (script/modelli_banco.py). NON e' un modello del progetto.\n" % (rel, nuovo))
    p = os.path.join(OUT, os.path.basename(rel).replace(".lib", "_fermo.lib"))
    open(p, "w", newline="").write(testa + t.rstrip("\r\n") + "\n" + FERMO)
    print(p)
