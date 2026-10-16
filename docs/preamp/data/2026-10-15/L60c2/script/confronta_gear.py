#!/usr/bin/env python3
"""L60c2: lo stesso deck di V2 col metodo di default (trapezoidale) e col gear, sulla stessa cella che
col default finisce: se il gear cambia i jack, le corse rifatte col gear non si possono mescolare
alle altre. Solo stdlib, /usr/bin/python3 -I.

Uso: confronta_gear.py CORSA [T_FINE]   (es. g10mai_1k_iii 24)  scrive confronto_gear_<CORSA>.txt

Ricampiona i tre jack (wrdata: mainjack fixjack1 fixjack2) a 96 kHz con scripts/v2_metodo.py e stampa,
per ciascuno, il massimo di |gear - default| e il massimo di |default|.
"""
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L60C2 = os.path.dirname(QUI)
ROOT = os.path.abspath(os.path.join(L60C2, "..", "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import v2_metodo as vm  # noqa: E402

corsa = sys.argv[1]
tf = float(sys.argv[2]) if len(sys.argv) > 2 else None
a, _ = vm.leggi_wrdata(os.path.join(L60C2, "run", "v2", corsa + ".dat"), 1e-9, tf)
b, _ = vm.leggi_wrdata(os.path.join(L60C2, "run", "sonda_v2", "gear", corsa + ".dat"), 1e-9, tf)
out = ["%s: default contro gear, %d / %d campioni a %d Hz" % (corsa, len(a[0]), len(b[0]), vm.FS)]
for j, nome in enumerate(("mainjack", "fixjack1", "fixjack2")):
    n = min(len(a[j]), len(b[j]))
    d = max(abs(a[j][k] - b[j][k]) for k in range(n))
    m = max(abs(a[j][k]) for k in range(n))
    out.append("  %-9s max|gear - default| = %.4g uV   max|default| = %.4g V" % (nome, d * 1e6, m))
open(os.path.join(L60C2, "confronto_gear_%s.txt" % corsa), "w").write("\n".join(out) + "\n")
print("\n".join(out))
