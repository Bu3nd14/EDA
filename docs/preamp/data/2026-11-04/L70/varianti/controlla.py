#!/usr/bin/env python3
"""L70: what each variant netlist removes and adds against the source's (psu_oggi.net), by part and
by pin; and psu_oggi.net against circuits/preamp/psu.net (must be equal but the date).

    /usr/bin/python3 -I controlla.py  > controllo.txt
"""
import os
import re

QUI = os.path.dirname(os.path.abspath(__file__))
REPO = QUI
for _ in range(6):
    REPO = os.path.dirname(REPO)


def parse(path):
    text = open(path).read()
    comps = {m.group(1): m.group(2) for m in re.finditer(
        r'\(comp\b.*?\(ref "([^"]+)"\).*?\(value "([^"]*)"\)', text, re.S)}
    pins = {}
    for chunk in re.split(r"\(net\s*\(code", text.split("(nets", 1)[-1])[1:]:
        m = re.search(r'\(name "([^"]*)"\)', chunk)
        for n in re.finditer(r'\(ref "([^"]+)"\)\s*\(pin "([^"]+)"\)', chunk):
            pins[(n.group(1), n.group(2))] = m.group(1)
    return comps, pins


def senza_data(path):
    return [ln for ln in open(path) if "(date" not in ln and "(source" not in ln]


ok = senza_data(os.path.join(QUI, "psu_oggi.net")) == senza_data(os.path.join(REPO, "circuits", "preamp", "psu.net"))
print("psu_oggi.net = circuits/preamp/psu.net (ma la data):", ok)
c0, p0 = parse(os.path.join(QUI, "psu_oggi.net"))
print("oggi: %d parti" % len(c0))
for v in ("s2", "s1", "s1s2", "s1s2dc"):
    c, p = parse(os.path.join(QUI, "psu_%s.net" % v))
    print("\n== %s: %d parti" % (v, len(c)))
    print("  tolte:", " ".join(sorted(set(c0) - set(c))))
    print("  nuove:", " ".join(sorted(set(c) - set(c0))))
    diff = sorted(k for k in set(p0) | set(p) if p0.get(k) != p.get(k) and k[0] in c0 and k[0] in c)
    for k in diff:
        print("  piedino %s.%s: %s -> %s" % (k[0], k[1], p0.get(k), p.get(k)))
