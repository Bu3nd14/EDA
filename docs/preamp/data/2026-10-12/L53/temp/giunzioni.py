#!/usr/bin/env python3
"""L53: le tensioni di giunzione di ogni dispositivo del blocco nelle quattro condizioni di op_cliff.

Legge i nodi dal log (print all) e i piedini da spice/preamp/gain_block_flat.inc. Per i BJT
Vbe e Vbc (NPN; per i PNP col segno girato, cosi' Vbc > ~0,4 V vuol dire saturazione per tutti),
per i JFET Vgs e Vgd. Stampa la tabella e segna le grandezze che cambiano piu' di 50 mV fra una
condizione buona e una cattiva.

Uso: /usr/bin/python3 giunzioni.py
"""
import os
import re

QUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(QUI, *[".."] * 6))
LOG = os.path.join(QUI, "run_cliff", "op_cliff.log")
INC = os.path.join(REPO, "spice", "preamp", "gain_block_flat.inc")

PNP = {"Q121A", "Q121B", "Q122", "Q133"}
dev = {}
for r in open(INC):
    p = r.split()
    if p and p[0][0] in "QJ":
        dev[p[0]] = p[1:4]        # Q: C B E ; J: D G S

blocchi = re.split(r"L53_COND ", open(LOG, errors="replace").read())[1:]
cond = []
for b in blocchi:
    nome = b.split("\n")[0].strip()
    v = {"0": 0.0}
    for m in re.finditer(r"^(\S+) = ([-+0-9.eE]+)", b, re.M):
        k = m.group(1).lower()
        k = re.sub(r"^v\((.*)\)$", r"\1", k)
        v[k] = float(m.group(2))
    cond.append((nome, v))

def nodo(v, n):
    return v[n.lower()]

righe = []
for d, pins in sorted(dev.items()):
    for nome_g, a, b in (("Vbe" if d[0] == "Q" else "Vgs", 1, 2), ("Vbc" if d[0] == "Q" else "Vgd", 1, 0)):
        vals = []
        for nome, v in cond:
            x = nodo(v, pins[a]) - nodo(v, pins[b])
            if d in PNP:
                x = -x
            vals.append(x)
        righe.append((d, nome_g, vals))

print("%-8s %-4s " % ("disp", "") + " ".join("%22s" % n[:22] for n, _ in cond))
for d, g, vals in righe:
    salto = max(abs(vals[1] - vals[0]), abs(vals[2] - vals[3]))
    print("%-8s %-4s " % (d, g) + " ".join("%22.4f" % x for x in vals) + ("   <--" if salto > 0.05 else ""))
for nome, v in cond:
    print("%s: %s" % (nome, " ".join("%s=%.4g" % (k, v[k]) for k in sorted(v) if k.startswith("@"))))
