#!/usr/bin/env python3
"""L45d2b2a: the audio board's capacitance on the two rails, from preamp_audio.net. Stdlib.

The supply bench models the audio board as two resistors (carico.txt): at a power-up the
board's capacitors are charged by the regulators too, and the soft-start sets that current.
Printed per rail:
  - the capacitors between the rail and GND (direct);
  - the capacitors between a cell node (<X>_VPF) and GND, and the resistance from VPLUS to
    that node (the RC cell of ADR-056, two 20 ohm in parallel since ADR-086).
Electrolytics are listed with their nominal value; genera_tb_psu.py derates them as it derates
C505 / C506 (0.8, ADR-046).

Uso: capacita_rail.py [preamp_audio.net]
"""
import os
import re
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(QUI, "..", "..", "..", "..", "..", ".."))
NET = sys.argv[1] if len(sys.argv) > 1 else os.path.join(REPO, "circuits", "preamp", "preamp_audio.net")


def parse(path):
    """(components, pin_net) - the parser of genera_tb_psu.py."""
    text = open(path).read()
    comps = {}
    for m in re.finditer(
            r'\(comp\b.*?\(ref "([^"]+)"\).*?\(value "([^"]*)"\)'
            r'.*?\(libsource\s*\(lib "([^"]*)"\)\s*\(part "([^"]*)"\)', text, re.S):
        comps[m.group(1)] = {"value": m.group(2), "lib": m.group(3), "part": m.group(4)}
    pin_net = {}
    for chunk in re.split(r"\(net\s*\(code", text.split("(nets", 1)[-1])[1:]:
        m = re.search(r'\(name "([^"]*)"\)', chunk)
        if m:
            for n in re.finditer(r'\(ref "([^"]+)"\)\s*\(pin "([^"]+)"\)', chunk):
                pin_net[(n.group(1), n.group(2))] = m.group(1)
    return comps, pin_net


def farad(v):
    m = re.match(r"^\s*([0-9]*\.?[0-9]+)\s*([munp]?)", v)
    return float(m.group(1)) * {"m": 1e-3, "u": 1e-6, "n": 1e-9, "p": 1e-12, "": 1.0}[m.group(2)]


def ohm(v):
    m = re.match(r"^\s*([0-9]*\.?[0-9]+)\s*([kKM]?)", v)
    return float(m.group(1)) * {"k": 1e3, "K": 1e3, "M": 1e6, "": 1.0}[m.group(2)]


COMPS, PN = parse(NET)


def nets(ref):
    return sorted(n for (r, p), n in PN.items() if r == ref)


def caps_between(a, b):
    out = []
    for ref, c in sorted(COMPS.items()):
        if c["part"].startswith("C") and sorted(nets(ref)) == sorted([a, b]):
            out.append((ref, farad(c["value"]), c["part"]))
    return out


for rail in ("VPLUS", "VMINUS"):
    cs = caps_between(rail, "GND")
    tot = sum(x[1] for x in cs)
    el = sum(x[1] for x in cs if x[2] == "C_Polarized")
    print("%s: %d condensatori diretti, %.1f uF (elettrolitici %.1f uF)" % (rail, len(cs), tot * 1e6, el * 1e6))
    if rail == "VPLUS":
        cel = sorted(set(n for n in PN.values() if n.endswith("_VPF")))
        for n in cel:
            cc = caps_between(n, "GND")
            rs = [ohm(COMPS[r]["value"]) for r, c in COMPS.items()
                  if c["part"] == "R" and sorted(nets(r)) == sorted(["VPLUS", n])]
            rpar = 1.0 / sum(1.0 / x for x in rs) if rs else float("inf")
            print("  cella %s: %.1f uF, %d resistenze da VPLUS, %.2f ohm in parallelo" % (
                n, sum(x[1] for x in cc) * 1e6, len(rs), rpar))
