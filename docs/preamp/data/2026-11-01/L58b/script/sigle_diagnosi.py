#!/usr/bin/env python3
"""L58b: the references the diagnosis procedure needs, read off the audio board's netlist: for each
block output net (<tag>_OUT, and the nets SKiDL may rename it to - limitations #74), the two 22 ohm
emitter resistors that feed it (the finals' quiescent, ADR-042) and its output test point (ADR-107).
Solo stdlib. /usr/bin/python3 -I sigle_diagnosi.py <preamp_audio.net> -> a table on stdout
"""
import re
import sys

t = open(sys.argv[1]).read()
comps = {}
for m in re.finditer(r'\(comp\s*\(ref "([^"]+)"\)\s*\(value "([^"]*)"\)', t):
    comps[m.group(1)] = m.group(2)
pn = {}
for blocco in t.split("\n    (net")[1:]:
    nome = re.search(r'\(name "([^"]+)"\)', blocco).group(1)
    for r, p in re.findall(r'\(ref "([^"]+)"\)\s*\(pin "([^"]+)"\)', blocco):
        pn[(r, p)] = nome
by_net = {}
for (r, p), n in pn.items():
    by_net.setdefault(n, set()).add(r)
righe = []
for n, refs in sorted(by_net.items()):
    r22 = sorted(r for r in refs if r.startswith("R") and comps.get(r) in ("22", "22R"))
    if len(r22) != 2:
        continue
    tps = sorted(r for r in refs if r.startswith("TP"))
    righe.append((n, r22, tps))
for n, r22, tps in righe:
    print("%-14s 22 ohm: %-12s test point: %s" % (n, " ".join(r22), " ".join(tps) or "-"))
print("%d blocchi" % len(righe))
