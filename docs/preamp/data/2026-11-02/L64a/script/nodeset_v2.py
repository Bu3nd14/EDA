#!/usr/bin/env python3
"""L64a: i .nodeset del blocco da solo per le corse della matrice di V2 che non trovano l'op.

    /usr/bin/python3 -I nodeset_v2.py <cartella delle corse> <cella> [...]

Perche': sul blocco di oggi 22 celle della dispersione (dpminmax, dpmaxmax) non trovano il punto
di lavoro in nessuna delle tre prove di corri.sh di L29c (col .nodeset delle uscite, senza, col
.nodeset esteso a INA e SELA): ngspice ripiega sul «Transient op», che la guardia di L29c
rifiuta (rc=OPT). In L60d2, sul blocco di allora, le stesse celle finivano con rc=0. E' la
trappola di limitations #86: la regola e' un .nodeset per ogni nodo interno di ogni istanza del
blocco, preso dall'op del blocco da solo. Qui i 38 nodi di
docs/preamp/data/2026-11-02/L67/op_oggi.csv (il blocco di oggi da solo, L67), per XA, XF1, XF2 e
XB. Un .nodeset guida solo la ricerca dell'op: dove l'op converge, la soluzione resta la stessa
(lo prova prova_nodeset.sh su celle che convergono anche senza).

Per ogni cella scrive <cartella>/corsa_<cella>_nb.cir: corsa_<cella>.cir con le righe .nodeset
dei blocchi accodate a quella che c'e' (e il .dat scritto dove lo scrive la corsa).
"""
import csv
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
OP = os.path.join(os.path.dirname(L), "L67", "op_oggi.csv")
ISTANZE = ("xa", "xf1", "xf2", "xb")

REPO = os.path.abspath(os.path.join(L, "..", "..", "..", "..", ".."))
SUB = os.path.join(REPO, "spice", "preamp", "gain_block.subckt")
PORTE = {"in", "out", "fb", "rg", "rg10", "vplus", "vminus", "0"}
interni = set()
for ln in open(SUB):
    if ln.strip() and not ln.startswith(("*", ".", "+")):
        p = ln.split()
        n = {"r": 2, "c": 2, "l": 2, "d": 2, "q": 3, "j": 3, "v": 2, "x": 0}.get(p[0][0].lower(), 0)
        interni |= {x.lower() for x in p[1:1 + n]}
interni -= PORTE
# op_oggi.csv ha anche nodi del banco di L67 (jack, outa): restano solo quelli del blocco
tutti = [(r["nodo"], float(r["v"])) for r in csv.DictReader(open(OP))]
nodi = [(n, v) for n, v in tutti if n in interni]
fuori = [n for n, _ in tutti if n not in interni]
mancano = sorted(interni - {n for n, _ in nodi})
if mancano or len(nodi) < 30:
    sys.exit(f"RIFIUTATO: nodi del blocco senza valore in {OP}: {mancano}")
print(f"{len(nodi)} nodi interni del blocco; fuori dal blocco, lasciati: {fuori}")
righe = []
for x in ISTANZE:
    parti = ["v(%s.%s)=%.10g" % (x, n, v) for n, v in nodi]
    for i in range(0, len(parti), 8):
        righe.append(".nodeset " + " ".join(parti[i:i + 8]))
blocco = "* L64a (limitations #86): i nodi interni del blocco da solo, da L67/op_oggi.csv\n" + \
    "\n".join(righe) + "\n"
d = sys.argv[1]
for c in sys.argv[2:]:
    src = os.path.join(d, "corsa_%s.cir" % c)
    t = open(src).read()
    righe_t = t.split("\n")
    idx = [i for i, l in enumerate(righe_t) if l.startswith(".nodeset ")]
    if len(idx) != 1:
        sys.exit(f"RIFIUTATO: {src} ha {len(idx)} righe .nodeset, attesa 1")
    righe_t.insert(idx[0] + 1, blocco.rstrip("\n"))
    open(os.path.join(d, "corsa_%s_nb.cir" % c), "w").write("\n".join(righe_t))
    print("scritto corsa_%s_nb.cir" % c)
