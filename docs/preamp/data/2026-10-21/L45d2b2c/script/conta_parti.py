#!/usr/bin/env python3
"""L45d2b2c: the parts of a KiCad netlist (the (comp (ref ...)) entries), how many, duplicates, and
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
for blocco in re.split(r"\(net\s", nets)[1:]:
    nome = re.search(r'\(name\s+"([^"]*)"\)', blocco).group(1)
    for ref, pin in re.findall(r'\(node\s+\(ref\s+"([^"]+)"\)\s+\(pin\s+"([^"]+)"\)', blocco):
        if re.search(r"(NBN|NEN|NBP|NEP)$", nome) and ref.startswith("D"):
            uscita.setdefault(ref, []).append("%s:%s" % (pin, nome))
for ref in sorted(uscita, key=lambda r: int(r[1:])):
    print("  %s %s" % (ref, " ".join(sorted(uscita[ref]))))
print("diodi sui finali: %d" % len(uscita))
