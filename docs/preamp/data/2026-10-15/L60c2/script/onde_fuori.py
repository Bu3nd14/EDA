#!/usr/bin/env python3
"""L60c2: come sono fatti i guasti fuori da 125 ms sulla Stax. Solo stdlib, /usr/bin/python3 -I.

Uso: onde_fuori.py MODO...      (es. G0_F2_R109_ap)  scrive onde_fuori.txt

Per ogni corsa: l'uscita del buffer F2 (outf2) e il jack della Stax (fix2jack) a istanti fissi dopo
il guasto (0,3 s), e su finestre di 20 ms il minimo e il massimo dei due: un'oscillazione si vede
come max - min grande a parita' di media, una rampa lenta come una media che si muove.
Le colonne del .dat sono quelle di genera_canale.deck_tr (analizza_p10.py di L45b).
"""
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L60C2 = os.path.dirname(QUI)
COL = ["mainjack", "fix1jack", "fix2jack", "outa", "outf1", "outf2"]
T_F = 0.3
ISTANTI = (0.0, 0.005, 0.02, 0.05, 0.1, 0.15, 0.2, 0.4, 0.8, 1.2, 1.6, 1.95)

out = []
for modo in sys.argv[1:]:
    p = os.path.join(L60C2, "run", "guasti", modo, modo + ".dat")
    t, v = [], {c: [] for c in COL}
    for riga in open(p):
        x = riga.split()
        if not x or not x[0][0].isdigit() and x[0][0] != "-":
            continue
        # wrdata ripete la colonna del tempo davanti a ogni vettore
        t.append(float(x[0]))
        for j, c in enumerate(COL):
            v[c].append(float(x[2 * j + 1]))
    out.append("== %s (%d punti, fine %.3f s)" % (modo, len(t), t[-1]))
    out.append("   t-tf ms     outa      outf2   fix2jack | finestra 20 ms: outf2 min/max, jack min/max")
    for dt in ISTANTI:
        tt = T_F + dt
        if tt > t[-1]:
            break
        i = min(range(len(t)), key=lambda k: abs(t[k] - tt))
        w = [k for k in range(len(t)) if tt <= t[k] < tt + 0.02]
        f2 = [v["outf2"][k] for k in w] or [0]
        jk = [v["fix2jack"][k] for k in w] or [0]
        out.append("   %7.1f %9.3f %9.3f %9.3f | %8.3f %8.3f %8.3f %8.3f"
                   % (dt * 1e3, v["outa"][i], v["outf2"][i], v["fix2jack"][i],
                      min(f2), max(f2), min(jk), max(jk)))
open(os.path.join(L60C2, "onde_fuori.txt"), "w").write("\n".join(out) + "\n")
print("\n".join(out))
