#!/usr/bin/env python3
"""L70: the lines of a list whose seq/<etichetta>/<caso>/ok.txt does not exist yet.
    /usr/bin/python3 -I script/mancanti.py <lista> > <lista_mancanti>
"""
import os
import sys

L = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for ln in open(sys.argv[1]):
    x = ln.split()
    if x and not os.path.exists(os.path.join(L, "seq", x[1], x[0], "ok.txt")):
        sys.stdout.write(ln)
