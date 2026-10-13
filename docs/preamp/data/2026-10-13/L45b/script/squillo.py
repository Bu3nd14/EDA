#!/usr/bin/env python3
"""L45b: la 47 ohm in corto col cavo sullo stadio - c'e' oscillazione o squillo? Solo stdlib.

Uso: squillo.py RUNDIR...   (corse *_gradino di genera_controlli.py: gradino 0,2 V a 0,35 s, 20 ms)

Legge il .dat grezzo di wrdata (colonne t, v a coppie: mainjack fix1jack fix2jack outa outf1 outf2
outb ...), SENZA ricampionare (un'oscillazione di MHz il ricampionamento a 96 kHz la perderebbe), e
per l'uscita del blocco B (outb) e il jack principale stampa, nella finestra 0,35-0,369 s:
  - il valore finale (media 0,365-0,369 s) e la sovraelongazione massima oltre di esso, in % del
    gradino;
  - l'ampiezza picco-picco residua in 0,360-0,369 s (un'oscillazione mantenuta resta qui);
  - il passo minimo che ngspice ha preso dopo il fronte (un'oscillazione lo stringe).
"""
import os
import sys


def leggi(path):
    t, cols = [], []
    for riga in open(path):
        p = riga.split()
        if len(p) < 14:
            continue
        try:
            v = [float(x) for x in p]
        except ValueError:
            continue
        t.append(v[0])
        cols.append(v[1::2])
    return t, cols


for d in sys.argv[1:]:
    m = os.path.basename(d.rstrip("/"))
    t, cols = leggi(os.path.join(d, m + ".dat"))
    print(m)
    for nome, k in (("outb", 6), ("mainjack", 0)):
        x = [c[k] for c in cols]
        prima = [x[i] for i in range(len(t)) if 0.345 <= t[i] < 0.35]
        v0 = sum(prima) / len(prima)
        fin = [x[i] for i in range(len(t)) if 0.365 <= t[i] < 0.369]
        vf = sum(fin) / len(fin)
        fin_res = [x[i] for i in range(len(t)) if 0.360 <= t[i] < 0.369]
        fin_res = max(fin_res) - min(fin_res)
        fin_win = [x[i] for i in range(len(t)) if 0.35 <= t[i] < 0.369]
        gr = vf - v0
        ov = (max(fin_win) - vf) / gr * 100 if gr > 0 else (min(fin_win) - vf) / gr * 100
        print("  %-8s gradino %.4g V, sovraelongazione %.2f %%, residuo p-p 0,360-0,369 s %.3g V" % (
            nome, gr, ov, fin_res))
    passi = [t[i + 1] - t[i] for i in range(len(t) - 1) if 0.3501 <= t[i] < 0.369]
    print("  passo minimo dopo il fronte %.3g s, punti in 0,350-0,369 s: %d" % (min(passi), len(passi)))
