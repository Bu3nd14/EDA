#!/usr/bin/env python3
"""L29c, sonda: la stessa corsa con una tran di 1 ms, e opzioni di convergenza diverse: da quale
punto di lavoro parte la tran? L'op puro converge (source stepping) a OUTA -15,45 mV; la tran
della prova di fumo e' ripiegata sul 'transient op' e partiva da OUTA +12,97 V.

Uso: tran_breve.py corsa_X.cir [variante ...]"""
import os
import subprocess
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
src = sys.argv[1]
L = open(src).read().splitlines()
it = next(i for i, r in enumerate(L) if r.startswith("tran "))
V = {
    "tale": [],
    "srcsteps": ["option srcsteps=40"],
    "gminsteps": ["option gminsteps=40"],
    "noopiter": ["option noopiter"],
    "gmin80": ["option gminsteps=80"],
    "src200": ["option srcsteps=200"],
    "trim_neutro": ["alter rl1 = 1e12", "alter cwire = 1e-18"],
    "solo_rl1": ["alter rl1 = 1e12"],
    "solo_cwire": ["alter cwire = 1e-18"],
    "g10": ["alter vk1i dc = 1", "alter vk5i dc = 1"],
    "rl1_1m": ["alter rl1 = 1e6"],
    # la via di main pezzo per pezzo (controfattuale neutro)
    "rrg_plain": ["alter vk1i dc = 0", "alter vk5i dc = 0", "alter rrgb = 0.1", "alter rrg10b = 0.1"],
    "rattt_plain": ["alter rattt = 1m", "alter vt1ri dc = 0"],
    "entrambi": ["alter vk1i dc = 0", "alter vk5i dc = 0", "alter rrgb = 0.1", "alter rrg10b = 0.1",
                 "alter rattt = 1m", "alter vt1ri dc = 0"],
    "senza_prb": ["alter vprbd dc = 0"],
}
TOGLI = {"nogmin": "option gminsteps"}
# righe di netlist aggiunte prima del .control
NETLIST = {
    "nodeset": [".nodeset V(OUTA)=0 V(W)=0 V(ATOP)=0 V(OUTB)=0 V(MAIN_A)=0 V(OUTF1)=0 V(OUTF2)=0"],
    "nodeset_a": [".nodeset V(OUTA)=0"],
}
for n in sys.argv[2:] or list(V):
    base = [r for r in L[:it] if not (n in TOGLI and r.startswith(TOGLI[n]))]
    if n in NETLIST:
        ic = base.index(".control")
        base = base[:ic] + NETLIST[n] + base[ic:]
    out = (base + V.get(n, []) + ["save all", "tran 1e-05 1e-3 0 1e-05",
                           "print v(outa)[0] v(main_a)[0] v(mainjack)[0]", ".endc", ".end"])
    p = os.path.join(QUI, "tr_%s.cir" % n)
    open(p, "w").write("\n".join(out) + "\n")
    r = subprocess.run(["/opt/homebrew/bin/ngspice", "-b", p], capture_output=True, text=True,
                       timeout=900)
    txt = r.stdout + r.stderr
    open(p[:-4] + ".log", "w").write(txt)
    vals = [l.strip() for l in txt.splitlines() if " = " in l and l.strip().startswith("v(")]
    steps = [l.strip() for l in txt.splitlines() if "stepping" in l or "Transient op" in l]
    print(n, "|", "; ".join(vals), "|", "; ".join(steps), flush=True)
