#!/usr/bin/env python3
"""L45d2b3b2b1: le parti di una netlist KiCad che non sono in un'altra, e quelle che hanno cambiato
impronta. Solo stdlib, /usr/bin/python3 -I.

Uso: parti_nuove.py <prima.net> <dopo.net>
Stampa il conteggio, le sigle nuove separate da virgole (l'argomento di nomi_reti.py), le sparite e le
impronte cambiate.
"""
import re
import sys


def parti(p):
    t = open(p).read().split("(nets", 1)[0]
    out = {}
    for blocco in re.split(r"\(comp\s", t)[1:]:
        ref = re.search(r'\(ref\s+"([^"]+)"\)', blocco).group(1)
        fp = re.search(r'\(footprint\s+"([^"]*)"\)', blocco)
        val = re.search(r'\(value\s+"([^"]*)"\)', blocco)
        out[ref] = (val.group(1) if val else "", fp.group(1) if fp else "")
    return out


a, b = parti(sys.argv[1]), parti(sys.argv[2])
nuove = sorted(set(b) - set(a), key=lambda r: (r[0], int(re.sub(r"\D", "", r) or 0)))
sparite = sorted(set(a) - set(b))
print("parti prima %d, dopo %d, nuove %d, sparite %d" % (len(a), len(b), len(nuove), len(sparite)))
print("nuove: " + ",".join(nuove))
print("sparite: " + ",".join(sparite))
for r in sorted(set(a) & set(b)):
    if a[r] != b[r]:
        print("cambiata %s: %s %s -> %s %s" % (r, a[r][0], a[r][1], b[r][0], b[r][1]))
