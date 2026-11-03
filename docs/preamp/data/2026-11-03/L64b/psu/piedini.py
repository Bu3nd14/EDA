#!/usr/bin/env python3
"""L54a: i piedini di una o piu' parti di psu.net e le loro reti, con le altre parti su ciascuna rete.

Uso: /usr/bin/python3 piedini.py U509 [U505 ...]
"""
import os
import re
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(QUI, "..", "..", "..", "..", "..", ".."))
net = open(os.path.join(REPO, "circuits", "preamp", "psu.net")).read()
val = {m.group(1): m.group(2) for m in
       re.finditer(r'\(comp\s*\(ref "([^"]+)"\)\s*\(value "([^"]*)"\)', net)}
pin, membri = {}, {}
for blk in re.split(r"\(net\s*\(code", net.split("(nets", 1)[1])[1:]:
    nome = re.search(r'\(name "([^"]*)"\)', blk).group(1)
    for m in re.finditer(r'\(ref "([^"]+)"\)\s*\(pin "([^"]+)"\)', blk):
        pin[(m.group(1), m.group(2))] = nome
        membri.setdefault(nome, []).append("%s.%s" % (m.group(1), m.group(2)))
for ref in sys.argv[1:]:
    print("== %s (%s)" % (ref, val.get(ref)))
    for (r, p), n in sorted(pin.items(), key=lambda x: (x[0][0], int(x[0][1]) if x[0][1].isdigit() else 0)):
        if r == ref:
            altri = [x for x in membri[n] if not x.startswith(ref + ".")]
            print("  %-3s %-14s %s" % (p, n, " ".join(altri[:10]) + (" ..." if len(altri) > 10 else "")))
