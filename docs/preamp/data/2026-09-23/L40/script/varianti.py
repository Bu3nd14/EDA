#!/usr/bin/env python3
"""L40, ESPLORAZIONE - nessun valore del sorgente cambia.

Copia un deck di spice/preamp/tb/ in <fase>/<deck>__<etichetta>.cir con alcune
righe `alter` messe in testa al .control, e il resto del deck IDENTICO: stessa
matrice, stesse tabelle, stesso criterio. I `wrdata` delle curve diventano
un `let` innocuo (servono solo le tabelle echo, e le curve sono ~6 MB a deck).

Uso: /usr/bin/python3 varianti.py <fase> <deck> <etichetta> "<alter 1>" ["<alter 2>" ...]
  es. varianti.py strada_a tb_loop cm820p_r169 "alter c124 = 820p"
Un argomento che comincia con "+" e' una RIGA DI NETLIST in piu', messa prima del
.control (es. "+RG0L40 FB 0 7.87k": la gamba fissa della strada (b), sul nodo FB
del blocco flat - e' voluto che il nome del nodo sia quello del blocco, #24).
"--curve" tiene i wrdata del deck (serve a v3.py, che rilegge la forma d'onda).

Le alter colpiscono i dispositivi del blocco FLAT: nel deck del blocco A i due
buffer sono il .subckt e restano coi valori generati (sono solo carico
d'ingresso, un gate JFET). Ogni deck generato mostra (show) i valori alterati prima delle analisi,
cosi' il log prova che l'alter ha colpito (limitations #22).
"""
import os
import re
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L40 = os.path.dirname(QUI)
ROOT = os.path.abspath(os.path.join(L40, *[".."] * 5))

fase, deck, etich = sys.argv[1:4]
curve = "--curve" in sys.argv[4:]   # tiene i wrdata (es. per v3.py)
arg = [a for a in sys.argv[4:] if a != "--curve"]
alters = [a for a in arg if not a.startswith("+")]
righe_extra = [a[1:] for a in arg if a.startswith("+")]
src = os.path.join(ROOT, "spice", "preamp", "tb", deck + ".cir")
righe = open(src).read().split("\n")
i = righe.index(".control")
righe[0] = "%s__%s.cir - L40 ESPLORAZIONE da %s.cir, %s" % (
    deck, etich, deck, "; ".join(righe_extra + alters))
if righe_extra:
    righe[i:i] = ["* L40: righe di netlist in piu' (varianti.py)"] + righe_extra
    i += 1 + len(righe_extra)
out = []
for k, r in enumerate(righe):
    if k > i and not curve and re.match(r"\s*wrdata\b", r):
        # un corpo di `if` lasciato vuoto fa uscire ngspice con 139 alla fine
        # della corsa (tabelle complete): al posto del wrdata un'istruzione innocua
        r = r[:len(r) - len(r.lstrip())] + "let l40_nessuna_curva = 0"
    out.append(r)
    if k == i:
        out += ["* L40: variante"] + alters + ["@@STAMPA@@"]
# subito dopo le alter: la prova che sono arrivate (una `print` in coda, dopo
# l'ultimo `destroy all`, fa uscire ngspice con 139)
stampa = []
for a in alters:
    m = re.match(r"alter\s+(\S+)\s*=", a)
    if m:
        dev = m.group(1)
        par = "capacitance" if dev.lower().startswith("c") else "resistance"
        stampa.append("show %s : %s" % (dev, par))
for x in righe_extra:
    stampa.append("show %s : resistance" % x.split()[0].lower())
j = out.index("@@STAMPA@@")
out = out[:j] + stampa + out[j + 1:]
d = os.path.join(L40, fase)
os.makedirs(d, exist_ok=True)
p = os.path.join(d, "%s__%s.cir" % (deck, etich))
open(p, "w").write("\n".join(out))
print(p)
