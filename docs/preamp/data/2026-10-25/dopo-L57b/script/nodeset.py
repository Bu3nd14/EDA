#!/usr/bin/env python3
"""L57a: il punto di lavoro vivo del banco del costo, come nodeset per tutti i deck di dist.py.

Corre dist.py op (senza protezione: converge senza ripieghi), legge `print all` dal log e scrive
costo/nodeset.inc con una riga .nodeset per nodo. Esclusi: le correnti di ramo, i nodi delle
sorgenti (vplus, vminus, vsn) e jin (non c'e' nel banco della THD, che pilota SEL). Rifiuta un log
con un ripiego («Transient op started») o col blocco spento (v(xa.d1n) sotto 5 V: vivo e' ~9,2 V).

Uso: /usr/bin/python3 nodeset.py
"""
import os
import re
import subprocess
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(os.path.dirname(QUI), "costo")
REPO = os.path.abspath(os.path.join(QUI, "..", "..", "..", "..", "..", ".."))
deck = os.path.join(D, "op_senza.cir")
out = os.path.join(D, "out_op_senza")
os.makedirs(D, exist_ok=True)
# il primo giro gira senza nodeset: il file non deve esistere ancora (l'include lo cercherebbe)
inc = os.path.join(D, "nodeset.inc")
open(inc, "w").write("* vuoto: nodeset.py lo riscrive dal punto di lavoro di op_senza\n")
subprocess.run(["/usr/bin/python3", os.path.join(QUI, "dist.py"), "op", deck], check=True)
subprocess.run(["/bin/zsh", os.path.join(REPO, "scripts", "run_simulation.sh"), deck, out], check=True)
log = open(os.path.join(out, "op_senza.log")).read()
if "Transient op started" in log:
    sys.exit("op_senza: ripiego sul transient op")
v = {}
for r in log.split("\n"):
    m = re.match(r"\s*(?:v\()?([a-z0-9_.]+)\)?\s*=\s*([-+0-9.eE]+)\s*$", r.strip().lower())
    if m and "#" not in r:
        v[m.group(1)] = float(m.group(2))
if v.get("xa.d1n", 0) < 5:
    sys.exit("op_senza: v(xa.d1n) = %s, il blocco non e' vivo" % v.get("xa.d1n"))
fuori = {"vplus", "vminus", "vsn", "jin"}
righe = ["* L57a: il punto di lavoro vivo del banco senza protezione (nodeset.py, da op_senza)"]
for n in sorted(v):
    if n not in fuori:
        righe.append(".nodeset v(%s)=%.6g" % (n, v[n]))
open(inc, "w").write("\n".join(righe) + "\n")
print("nodeset.inc: %d nodi, v(xa.d1n) = %.4g V" % (len(righe) - 1, v["xa.d1n"]))
