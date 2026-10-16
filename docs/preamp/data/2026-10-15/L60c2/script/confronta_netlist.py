#!/usr/bin/env python3
"""L60c2: compare two KiCad netlists by MEANING, not by text.

SKiDL renames merged nets and reshuffles the file from run to run
(limitations #23), so a text diff of preamp_audio.net says nothing. This
compares: the components (ref -> value, lib:part, footprint) and the
connectivity as a set of pin groups (each net = the frozenset of its
ref.pin), so a net that only changed name does not show up.

  /usr/bin/python3 confronta_netlist.py OLD.net NEW.net
"""
import re
import sys
sys.path.insert(0, __import__("pathlib").Path(__file__).resolve().parents[6].joinpath("scripts").as_posix())
from check_relay_safe_state import parse_netlist  # noqa: E402
from pathlib import Path  # noqa: E402


def footprints(path):
    text = Path(path).read_text()
    out = {}
    for m in re.finditer(r'\(comp\b.*?\(ref "([^"]+)"\).*?\(footprint "([^"]*)"\)',
                         text, re.S):
        out[m.group(1)] = m.group(2)
    return out


def groups(pin_net):
    nets = {}
    for (ref, pin), name in pin_net.items():
        nets.setdefault(name, set()).add(f"{ref}.{pin}")
    return {frozenset(v): k for k, v in nets.items()}


old_c, old_p = parse_netlist(Path(sys.argv[1]))
new_c, new_p = parse_netlist(Path(sys.argv[2]))
old_f, new_f = footprints(sys.argv[1]), footprints(sys.argv[2])
print(f"componenti: {len(old_c)} -> {len(new_c)}")
for ref in sorted(set(old_c) | set(new_c)):
    a, b = old_c.get(ref), new_c.get(ref)
    fa, fb = old_f.get(ref), new_f.get(ref)
    if a != b or fa != fb:
        print(f"  {ref}: {a} [{fa}] -> {b} [{fb}]")
go, gn = groups(old_p), groups(new_p)
print(f"reti: {len(go)} -> {len(gn)}")
for g in sorted(set(go) - set(gn), key=lambda s: sorted(s)):
    print(f"  solo prima: {go[g]}: {sorted(g)}")
for g in sorted(set(gn) - set(go), key=lambda s: sorted(s)):
    print(f"  solo dopo:  {gn[g]}: {sorted(g)}")
renamed = sorted((go[g], gn[g]) for g in set(go) & set(gn) if go[g] != gn[g])
print(f"reti uguali con nome diverso: {len(renamed)}")
for a, b in renamed:
    print(f"  {a} -> {b}")
