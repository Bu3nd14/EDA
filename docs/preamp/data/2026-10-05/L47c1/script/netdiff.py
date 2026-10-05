#!/usr/bin/env python3
"""Compare two KiCad netlists by connectivity (pin sets), not by net names."""
import re
import sys

COMP = re.compile(r'\(comp\s*\(ref "([^"]+)"\)\s*\(value "([^"]*)"\)')
NET = re.compile(r'\(net\s*\(code "?\d+"?\)\s*\(name "([^"]*)"\)(.*?)(?=\(net\s*\(code|\Z)', re.S)
NODE = re.compile(r'\(node\s*\(ref "([^"]+)"\)\s*\(pin "([^"]+)"\)')


def parse(path):
    t = open(path).read()
    comps = {m.group(1): m.group(2) for m in COMP.finditer(t)}
    nets = [(m.group(1), frozenset(NODE.findall(m.group(2)))) for m in NET.finditer(t)]
    return comps, nets


a_c, a_n = parse(sys.argv[1])
b_c, b_n = parse(sys.argv[2])
gone = set(a_c) - set(b_c)
print("components A", len(a_c), "B", len(b_c))
print("components only in A:", sorted(gone))
print("components only in B:", sorted(set(b_c) - set(a_c)))
for r in sorted(set(a_c) & set(b_c)):
    if a_c[r] != b_c[r]:
        print("value changed", r, a_c[r], "->", b_c[r])
a_sets = {}
for name, pins in a_n:
    p = frozenset(x for x in pins if x[0] not in gone)
    if p:
        a_sets.setdefault(p, []).append(name)
b_sets = {}
for name, pins in b_n:
    b_sets.setdefault(pins, []).append(name)
onlya = [(v, sorted(k)) for k, v in a_sets.items() if k not in b_sets]
onlyb = [(v, sorted(k)) for k, v in b_sets.items() if k not in a_sets]
print("nets of A (removed parts dropped) not in B:", len(onlya))
for v, k in onlya:
    print("   A", v, k)
print("nets of B not in A:", len(onlyb))
for v, k in onlyb:
    print("   B", v, k)
print("nets A", len(a_n), "B", len(b_n))
