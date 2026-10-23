#!/usr/bin/env python3
"""L45d2b3b2b2: caldo.py di L45d2b3b2a puntato a QUESTA cartella: i deck della variante con tutto il
circuito a <temp> (una riga `.temp`, un valore). Solo stdlib, /usr/bin/python3 -I.

Uso: caldo.py <variante> <temp> <modo> [...]   -> deck/<v>t<temp>_<pos>/*.cir, deck/lista_<v>t<temp>.txt
"""
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
DATA = os.path.abspath(os.path.join(L, "..", ".."))
sys.path.insert(0, os.path.join(DATA, "2026-10-22", "L45d2b3b2a", "script"))
import caldo as c2a   # noqa: E402

c2a.L = L

if __name__ == "__main__":
    c2a.main(sys.argv[1], sys.argv[2], sys.argv[3:])
