#!/usr/bin/env python3
"""L46b: le celle RC di ADR-056 lette dalla netlist della scheda audio.

Per ogni rete *_VPF: i membri, e che ci siano esattamente la R da 10 Ohm verso il
rail +, il 1000 uF verso GND, le 220 / 226 Ohm dello specchio e la 56 Ohm del VAS.
Esce 1 se una rete non torna.

Uso: /usr/bin/python3 celle_netlist.py <file.net>
"""
import re
import sys

t = open(sys.argv[1]).read()
val = dict(re.findall(r'\(comp\s*\(ref "([^"]+)"\)\s*\(value "([^"]+)"\)', t))
reti = {}
for blocco in re.split(r"\(net\s*\(code", t)[1:]:
    m = re.search(r'\(name "([^"]+)"\)', blocco)
    if m:
        reti[m.group(1)] = re.findall(r'\(node\s*\(ref "([^"]+)"\)', blocco)
male = 0
for nome in sorted(n for n in reti if n.endswith("VPF")):
    membri = sorted(reti[nome])
    valori = sorted(val.get(r, "?") for r in membri)
    ok = valori == sorted(["10", "1000u", "220", "226", "56"])
    r10 = [r for r in membri if val.get(r) == "10"]
    c = [r for r in membri if val.get(r) == "1000u"]
    rail = [n for n, mm in reti.items() if r10 and r10[0] in mm and n != nome]
    cg = [n for n, mm in reti.items() if c and c[0] in mm and n != nome]
    ok = ok and rail == ["VPLUS"] and cg == ["GND"]
    male += not ok
    print("%-9s %s  cella %s -> %s, %s -> %s  %s" % (
        nome, " ".join("%s=%s" % (r, val.get(r)) for r in membri),
        r10, rail, c, cg, "OK" if ok else "NON TORNA"))
print("%d reti VPF, %d non tornano" % (sum(n.endswith("VPF") for n in reti), male))
sys.exit(1 if male else 0)
