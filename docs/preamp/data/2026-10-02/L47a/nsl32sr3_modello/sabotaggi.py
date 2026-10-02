#!/usr/bin/env python3
"""sabotaggi.py - le due verifiche vedono un modello sbagliato? (L47a)

Quattro copie alterate del .lib in una cartella temporanea; ognuna deve far fallire la verifica
indicata (exit != 0). Esce col numero di sabotaggi NON rilevati.
"""
import math, os, re, subprocess, sys, tempfile

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
import genera_modello as G

PY = "/usr/bin/python3"
orig = open(G.OUT).read()
tau = "%.6g" % G.TAU_ON
r1 = "%.4f" % math.log10(G.R1)
r2 = "%.4f" % math.log10(G.R2)
blk_b = re.search(r"\.subckt NSL32SR3_B.*?\.ends", orig, re.S).group(0)
nodo = re.search(r"-2\.0000,(\d\.\d{4})", blk_b).group(0)
nodo_mosso = "-2.0000,%.4f" % (float(nodo.split(",")[1]) + 0.1)

SABOTAGGI = [
    ("curva B: il nodo a 10 uA spostato di +0,1 decadi", "verifica_statica.py",
     lambda s: s.replace(blk_b, blk_b.replace(nodo, nodo_mosso))),
    ("tau di accensione +30 %", "verifica_dinamica.py",
     lambda s: s.replace(tau, "%.6g" % (G.TAU_ON * 1.3))),
    ("tasso di discesa fino a 100 kohm -20 %", "verifica_dinamica.py",
     lambda s: s.replace("," + r1, ",%.4f" % math.log10(G.R1 * 0.8))),
    ("tasso di coda verso il buio -20 %", "verifica_dinamica.py",
     lambda s: s.replace("," + r2, ",%.4f" % math.log10(G.R2 * 0.8))),
]

mancati = 0
cartella = tempfile.mkdtemp()
for titolo, script, f in SABOTAGGI:
    s = f(orig)
    assert s != orig, "sabotaggio senza effetto sul testo: " + titolo
    p = os.path.join(cartella, "sab.lib")
    open(p, "w").write(s)
    rc = subprocess.run([PY, os.path.join(QUI, script), p], capture_output=True, text=True).returncode
    rilevato = rc != 0
    mancati += not rilevato
    print("%-50s %-22s exit %d  %s" % (titolo, script, rc, "rilevato" if rilevato else "<-- NON RILEVATO"))
print("\nsabotaggi non rilevati:", mancati)
sys.exit(mancati)
