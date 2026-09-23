#!/usr/bin/env python3
"""L29c, sonda: una corsa divisa fermata a TSTOP, con varianti di solutore o di modello del
contatto, per i 'Timestep too small' del cambio a caldo e dello spegnimento a 10 ms.

Uso: prova_tran.py corsa_X.cir TSTOP variante [variante ...]"""
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

QUI = os.path.dirname(os.path.abspath(__file__))
src, tstop = sys.argv[1], sys.argv[2]
L = open(src).read().splitlines()
it = next(i for i, r in enumerate(L) if r.startswith("tran "))
tmax = L[it].split()[1]
V = {
    "tale": ([], None, None),
    "gear": (["option method=gear"], None, None),
    "tmax1u": ([], "1e-06", None),
    "roff1g": ([], None, (r"SW\(RON=0.1 ROFF=1e12", "SW(RON=0.1 ROFF=1e9")),
    "rail1m": ([], None, ("RAIL", "1m")),
    "gear_tmax1u": (["option method=gear"], "1e-06", None),
}


def uno(n):
    pre, tm, sub = V[n]
    base = list(L[:it])
    if sub and sub[0] != "RAIL":
        base = [re.sub(sub[0], sub[1], r) for r in base]
    if sub and sub[0] == "RAIL":
        # la discesa si ferma a 1 mV invece che a 0 V esatti
        base = [r.replace(" 0 1000 0 ]", " 1m 1000 1m ]") if "@vpp[pwl]" in r else r for r in base]
        base = [r.replace(" 0 1000 0 ]", " -1m 1000 -1m ]") if "@vmm[pwl]" in r else r for r in base]
    out = base + pre + ["tran %s %s 0 %s" % (tm or tmax, tstop, tm or tmax),
                        "print v(mainjack)[length(v(mainjack))-1]", ".endc", ".end"]
    p = os.path.join(QUI, "pt_%s_%s.cir" % (os.path.basename(src)[6:-4], n))
    open(p, "w").write("\n".join(out) + "\n")
    r = subprocess.run(["/opt/homebrew/bin/ngspice", "-b", p], capture_output=True, text=True, timeout=3600)
    txt = r.stdout + r.stderr
    open(p[:-4] + ".log", "w").write(txt)
    ts = [l for l in txt.splitlines() if "Timestep too small" in l]
    return "%s %s: rc %d, %s" % (os.path.basename(src), n, r.returncode,
                                ts[0][-90:] if ts else "completa")


with ThreadPoolExecutor(len(sys.argv) - 3) as ex:
    for x in ex.map(uno, sys.argv[3:]):
        print(x, flush=True)
