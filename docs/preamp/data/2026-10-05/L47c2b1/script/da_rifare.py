#!/usr/bin/env python3
"""L47c2b1: dopo una modifica del generatore, quali corse della matrice cambiano davvero. Divide
il deck nuovo in una cartella temporanea (dividi.py di L29b2), confronta ogni corsa_*.cir con
quella gia' corsa nella matrice, e con --togli sposta in DIR/superate/ i .dat delle corse cambiate
(corri.sh rifa' solo le corse senza .dat). Le corse nuove, che la matrice non ha, si elencano.

Uso: da_rifare.py DECK MATRICE TMPDIR [--togli]
"""
import filecmp
import glob
import os
import subprocess
import sys

deck, mat, tmp = sys.argv[1:4]
togli = "--togli" in sys.argv
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 6))
os.makedirs(tmp, exist_ok=True)
testo = open(deck).read().replace("@REPO@", REPO)
open(os.path.join(tmp, "deck.cir"), "w").write(testo)
subprocess.run([sys.executable, os.path.join(REPO, "docs/preamp/data/2026-09-22/L29b2/pavimento/dividi.py"),
                os.path.join(tmp, "deck.cir")], check=True, capture_output=True)
cambiate, nuove, uguali = [], [], 0
for p in sorted(glob.glob(os.path.join(tmp, "corsa_*.cir"))):
    q = os.path.join(mat, os.path.basename(p))
    if not os.path.exists(q):
        nuove.append(os.path.basename(p))
    elif filecmp.cmp(p, q, shallow=False):
        uguali += 1
    else:
        cambiate.append(os.path.basename(p)[6:-4])
print("uguali %d, cambiate %d, nuove %d" % (uguali, len(cambiate), len(nuove)))
for c in cambiate:
    print("  cambiata:", c)
for c in nuove:
    print("  nuova:", c)
if togli:
    sup = os.path.join(mat, "superate")
    os.makedirs(sup, exist_ok=True)
    n = 0
    for c in cambiate:
        for suf in (".dat", "_stati.dat"):
            p = os.path.join(mat, c + suf)
            if os.path.exists(p):
                os.rename(p, os.path.join(sup, c + suf))
                n += 1
    print("spostati %d .dat in %s" % (n, sup))
