#!/usr/bin/env python3
"""L60d1, NC-070: dove nasce il fronte che fa i picchi sul jack principale in mute. La corsa
«sempre in mute» di prepara_diagnosi.py (run/diagnosi/<variante>/corsa.cir) fermata a 30 ms,
salvando anche i nodi interni e le correnti dei transistor del blocco B (XB).

Uso: sonda_blocco.py <variante> [tstop=30m]-> run/sonda/<variante>/corsa.cir (wrdata sonda.dat)
Colonne di sonda.dat (dopo il tempo, a coppie t/valore come ogni wrdata): COLONNE sotto.
"""
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
var = sys.argv[1]
TSTOP = sys.argv[2] if len(sys.argv) > 2 else "30m"
c = open(os.path.join(L, "run", "diagnosi", var, "corsa.cir")).read()

COLONNE = ["v(mainjack)", "v(mainc)", "v(main_a)", "v(outb)", "v(xb.nhi)", "v(xb.nvb)",
           "v(xb.nx)", "v(xb.ny)", "v(xb.nbn)", "v(xb.nbp)", "v(fbb)",
           "@q.xb.q132[ic]", "@q.xb.q133[ic]", "@q.xb.q122[ic]", "@q.xb.q125[ic]",
           "@q.xb.q146[ic]", "@q.xb.q127[ic]", "@q.xb.q121b[ic]", "@q.xb.q117[ic]"]
# il blocco di prima di L56 non ha l'inseguitore Q146 (ADR-067)
inc = [r for r in c.split("\n") if r.startswith(".include") and "gain_block" in r][0]
if "Q146 " not in open(inc.split()[1]).read():
    COLONNE.remove("@q.xb.q146[ic]")
righe = c.split("\n")
out = []
for r in righe:
    if r.startswith("save "):
        r = "save " + " ".join(COLONNE)
    elif r.startswith("tran "):
        p = r.split()
        p[2] = TSTOP
        r = " ".join(p)
    elif r.startswith("wrdata "):
        continue
    out.append(r)
i = out.index([r for r in out if r.startswith("tran ")][0])
out.insert(i + 1, "wrdata sonda.dat " + " ".join(COLONNE))
d = os.path.join(L, "run", "sonda", var)
os.makedirs(d, exist_ok=True)
open(os.path.join(d, "corsa.cir"), "w").write("\n".join(out))
open(os.path.join(d, "colonne.txt"), "w").write("\n".join(COLONNE) + "\n")
print("->", d)
