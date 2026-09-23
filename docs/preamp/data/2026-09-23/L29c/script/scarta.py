#!/usr/bin/env python3
"""L29c: scarta da una directory di corse quelle il cui nome soddisfa il regex (i .dat, i log e
la loro riga in tempi.txt), perche' corri.sh le rifaccia col deck rigenerato.

Uso: scarta.py DIR REGEX"""
import glob
import os
import re
import sys

d, rx = sys.argv[1:3]
R = re.compile(rx)
n = 0
for p in glob.glob(os.path.join(d, "*.dat")) + glob.glob(os.path.join(d, "corsa_*.log")):
    b = os.path.basename(p)
    nome = b[6:-4] if b.startswith("corsa_") else b[:-4].replace("_stati", "")
    if R.search(nome):
        os.remove(p)
        n += 1
t = os.path.join(d, "tempi.txt")
righe = open(t).read().splitlines()
tenute = [r for r in righe if not R.search(r.split()[0])]
open(t, "w").write("\n".join(tenute) + "\n")
print("%d file tolti, %d righe di tempi tolte" % (n, len(righe) - len(tenute)))
