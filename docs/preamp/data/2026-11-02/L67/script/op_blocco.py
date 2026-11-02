#!/usr/bin/env python3
"""L67: il punto di lavoro di un blocco da solo, per i `.nodeset` della catena.

Perche' (README, «Il punto di lavoro della catena»): col blocco di oggi a 27 gradi l'op della catena
a quattro istanze non converge in nessuno dei 68 casi (gmin e source stepping falliti); ngspice
ripiega sul «Transient op», ne esce coi condensatori grossi scarichi (C145 1000 uF dietro 10 Ohm,
tau 10 ms) e la corsa di 4 ms misura una catena non ancora accesa: VPF a 4,9 V, 4 A dal +15 V, la
principale a pochi uV. Il blocco da solo converge sempre. I suoi nodi interni diventano `.nodeset`
per ogni istanza: guidano solo la ricerca dell'op, e se l'op converge la soluzione e' la stessa
(provato: il caso noto l56 coi nodeset ridà L56 cella per cella).

  op_blocco.py genera  -> ../op/op_oggi.cir (il blocco di oggi, il banco della sorgente, `op`)
  op_blocco.py leggi   -> ../op_oggi.csv (nodo interno, tensione), dal log della corsa

La corsa: /bin/zsh <R>/scripts/run_simulation.sh ../op/op_oggi.cir ../op/run
"""
import csv
import os
import re
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
LOTTO = os.path.dirname(QUI)
OP = os.path.join(LOTTO, "op")
ESTERNI = {"in", "out", "fb", "rg", "rg10", "vplus", "vminus", "0"}
DECK = """op_oggi - L67: il punto di lavoro del blocco di oggi, da solo (per i nodeset della catena)
.include @REPO@/models/jfet/lsk489.lib
.include @REPO@/models/bjt_npn/mmbt5551.lib
.include @REPO@/models/bjt_pnp/mmbt5401.lib
.include @REPO@/models/bjt_npn/mje15032.lib
.include @REPO@/models/bjt_pnp/mje15033.lib
.include @REPO@/models/diodes/1n4148.lib
.include @REPO@/models/bjt_pnp/ls350.lib
.include @REPO@/spice/preamp/gain_block_flat.inc
VPP VPLUS 0 DC 15
VMM VMINUS 0 DC -15
RSRC IN 0 2500
RRG RG 0 1G
RRG10 RG10 0 1G
RISO OUT OUTA 47
COUT OUTA JACK 4.7u
RBLEED JACK 0 220k
RLOAD JACK 0 10k
.options reltol=1e-6 abstol=1e-15 vntol=1e-9
.control
option itl1=1000
set numdgt=10
op
print all
.endc
.end
"""

if sys.argv[1:] == ["genera"]:
    os.makedirs(OP, exist_ok=True)
    open(os.path.join(OP, "op_oggi.cir"), "w").write(DECK)
    print("-> %s" % os.path.join(OP, "op_oggi.cir"))
elif sys.argv[1:] == ["leggi"]:
    log = os.path.join(OP, "run", "op_oggi.log")
    testo = open(log, errors="replace").read()
    if "stepping failed" in testo and "source stepping failed" in testo:
        raise SystemExit("%s: l'op del blocco da solo non converge" % log)
    nodi = {}
    for m in re.finditer(r"^([a-z0-9_]+) = ([-+0-9.eE]+)$", testo, re.M):
        n = m.group(1)
        if n not in ESTERNI and not n.endswith("#branch"):
            nodi[n] = m.group(2)
    if float(nodi.get("vpf", 0)) < 14:
        raise SystemExit("%s: VPF %s, punto di lavoro spento" % (log, nodi.get("vpf")))
    p = os.path.join(LOTTO, "op_oggi.csv")
    with open(p, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["nodo", "v"])
        for n in sorted(nodi):
            w.writerow([n, nodi[n]])
    print("%d nodi interni, vpf %s, nx %s, ny %s -> %s" % (len(nodi), nodi["vpf"], nodi.get("nx"), nodi.get("ny"), p))
else:
    raise SystemExit("uso: op_blocco.py genera|leggi")
