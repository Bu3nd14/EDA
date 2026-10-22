#!/usr/bin/env python3
"""L45d2b3b1: COPIED from L45d2b2c's; added, the two halves of the follower's collector resistor
(ADR-097): every net named ...NFCR must carry exactly two resistors (R153's half and R160's).

L45d2b2c: the parts of a KiCad netlist (the (comp (ref ...)) entries), how many, duplicates, and
the 1N4148 whose pins sit on an output pair's base / emitter nets (NBN / NEN / NBP / NEP of an
instance). Solo stdlib. /usr/bin/python3 -I conta_parti.py <file.net>
"""
import re
import sys
from collections import Counter

t = open(sys.argv[1]).read()
comp = t.split("(nets", 1)[0]
refs = re.findall(r'\(comp\s+\(ref\s+"([^"]+)"\)', comp)
dup = [r for r, n in Counter(refs).items() if n > 1]
print("parti %d, duplicate %s" % (len(refs), dup or "nessuna"))
nets = t.split("(nets", 1)[1]
uscita = {}
nfcr = {}
for blocco in re.split(r"\(net\s", nets)[1:]:
    nome = re.search(r'\(name\s+"([^"]*)"\)', blocco).group(1)
    nodi = re.findall(r'\(node\s+\(ref\s+"([^"]+)"\)\s+\(pin\s+"([^"]+)"\)', blocco)
    if nome.endswith("NFCR"):
        nfcr[nome] = sorted(r for r, _ in nodi)
    for ref, pin in nodi:
        if re.search(r"(NBN|NEN|NBP|NEP)$", nome) and ref.startswith("D"):
            uscita.setdefault(ref, []).append("%s:%s" % (pin, nome))
for ref in sorted(uscita, key=lambda r: int(r[1:])):
    print("  %s %s" % (ref, " ".join(sorted(uscita[ref]))))
print("diodi sui finali: %d" % len(uscita))
for k in sorted(nfcr):
    print("  %s %s" % (k, " ".join(nfcr[k])))
male = [k for k, v in nfcr.items() if len(v) != 2 or not all(r.startswith("R") for r in v)]
print("nodi NFCR: %d, con due resistenze %d%s" % (len(nfcr), len(nfcr) - len(male),
                                                  ", SBAGLIATI %s" % male if male else ""))
