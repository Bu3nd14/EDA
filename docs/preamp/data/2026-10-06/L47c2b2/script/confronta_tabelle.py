#!/usr/bin/env python3
"""L47c2b2: la tabella dei guasti accanto a quelle di L41c e di L46b (l'ultima ricorsa).

Solo stdlib. /usr/bin/python3 confronta_tabelle.py  -> ../confronto.csv e a schermo

Le tre tabelle hanno gli stessi criteri (script/tabella.py di L41c) ma non lo stesso banco:
  L41c   l'alimentatore col pilota delle LDR e la sfumatura; la scheda audio con le celle; il
         blocco di L40; il contatto in serie del banco = interruttore ideale;
  L46b   come L41c, col blocco di ADR-054 e R120 226 ohm (ADR-056), ponte di L41c riusato;
  L47c2b2 l'alimentatore e il firmware di L47c2a (ADR-062, il mute che taglia); la scheda senza
         celle; il contatto in serie BSERx col fronte di 4,55 us (ADR-063, che vale anche per
         --matrice l41c); il ponte rifatto. Lo spegnimento lungo finisce a TE + 1,1 s.
"""
import csv
import os

QUI = os.path.dirname(os.path.abspath(__file__))
LOTTO = os.path.dirname(QUI)
DATA = os.path.dirname(os.path.dirname(LOTTO))
T = [("L41c", os.path.join(DATA, "2026-09-26", "L41c", "tabella.csv")),
     ("L46b", os.path.join(DATA, "2026-10-01", "L46b", "l41c", "tabella.csv")),
     ("L47c2b2", os.path.join(LOTTO, "tabella.csv"))]
val = {}
casi = []
for nome, p in T:
    for r in csv.DictReader(open(p)):
        if r["caso"] not in casi:
            casi.append(r["caso"])
        val[(nome, r["caso"])] = (r["picco_V"], r["dB_SPL_picco_1m"], r["esito"])
out = os.path.join(LOTTO, "confronto.csv")
with open(out, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["caso"] + ["%s_%s" % (n, k) for n, _ in T for k in ("picco_V", "dB_SPL")]
               + ["L47c2b2_esito"])
    for c in casi:
        w.writerow([c] + [x for n, _ in T for x in val.get((n, c), ("-", "-", "-"))[:2]]
                   + [val[("L47c2b2", c)][2]])
print(open(out).read())
