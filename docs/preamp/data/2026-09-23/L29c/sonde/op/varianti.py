#!/usr/bin/env python3
"""L29c, sonda: da dove viene il punto di lavoro sbagliato del banco nuovo (OUTA a +13 V nella
prova di fumo). Prende una corsa divisa, sostituisce la tran con un op, e aggiunge
un'alterazione per variante.

Uso: varianti.py corsa_X.cir [variante ...]"""
import os
import subprocess
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
src = sys.argv[1]
L = open(src).read().splitlines()
it = next(i for i, r in enumerate(L) if r.startswith("tran "))
V = {
    "tale": [],
    "trim_neutro": ["alter rl1 = 1e12", "alter cwire = 1e-18"],
    "g10": ["alter vk1i dc = 1", "alter vk5i dc = 1"],
    "trim_neutro_g10": ["alter rl1 = 1e12", "alter cwire = 1e-18", "alter vk1i dc = 1",
                        "alter vk5i dc = 1"],
}
scelte = sys.argv[2:] or list(V)
for n in scelte:
    extra = V[n]
    out = L[:it] + extra + ["save all", "op", "print v(outa) v(w) v(main_a) v(mainjack) v(st1r) v(st2r) v(sk1)",
                            ".endc", ".end"]
    p = os.path.join(QUI, "op_%s.cir" % n)
    open(p, "w").write("\n".join(out) + "\n")
    r = subprocess.run(["/opt/homebrew/bin/ngspice", "-b", p], capture_output=True, text=True,
                       timeout=900)
    txt = r.stdout + r.stderr
    open(p[:-4] + ".log", "w").write(txt)
    vals = [l.strip() for l in txt.splitlines() if " = " in l and l.strip().startswith(("v(", "st", "sk"))]
    steps = [l.strip() for l in txt.splitlines() if "stepping" in l or "Transient op" in l]
    print(n, "|", "; ".join(vals), "|", "; ".join(steps), flush=True)
