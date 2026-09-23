#!/usr/bin/env python3
"""L40: risposta dei candidati (tb_ac): guadagno a 1 kHz (E2), a 20 kHz, banda
-3 dB (nel deck si chiama `flo`: `fhi`/`flo` di tb_ac.cir sono scambiati,
fhi e' l'angolo BASSO) e picco sopra il guadagno a 1 kHz (dalle curve), per modo e sorgente.
Uso: /usr/bin/python3 cand_ac.py [fase]   (default candidati)
"""
import glob
import os
import re
import sys

L40 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fase = sys.argv[1] if len(sys.argv) > 1 else "candidati"
D = os.path.join(L40, fase)


def picco(p, g1k):
    m = -1e9
    for r in open(p):
        c = r.split()
        if len(c) >= 2:
            try:
                m = max(m, float(c[1]))
            except ValueError:
                pass
    return m - g1k


print("%-9s %-5s %-5s %8s %8s %9s %7s" % ("cand", "modo", "rsrc", "g1k_dB", "g20k_dB", "f-3dB_kHz", "picco"))
for d in sorted(glob.glob(os.path.join(D, "tb_ac__*"))):
    if not os.path.isdir(d):
        continue
    cand = os.path.basename(d).split("__")[1]
    log = open(glob.glob(os.path.join(d, "*.log"))[0]).read()
    for blk in re.split(r"\nMODE=", log)[1:]:
        m = re.match(r"(\S+)\s+RSRC=(\S+)", blk)
        blk = blk.split("Doing analysis")[0]   # solo la print di questo blocco
        v = dict(re.findall(r"^(\w+)\s*=\s*(\S+)", blk, re.M))
        gm, rs = m.group(1), m.group(2)
        if rs not in ("1.5", "2500"):
            continue
        g1k = float(v["g1k"])
        cur = os.path.join(d, "tb_ac_%s_%s.txt" % (gm, rs))
        pk = picco(cur, g1k) if os.path.exists(cur) else float("nan")
        print("%-9s %-5s %-5s %8.4f %8.4f %9.1f %7.3f" % (
            cand, gm, rs, g1k, float(v["g20k"]), float(v["flo"]) / 1e3, pk))
