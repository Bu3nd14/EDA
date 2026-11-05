#!/usr/bin/env python3
"""Summarise a kicad-cli DRC JSON: violations by type and severity, with the
first items of each. Stdlib only (/usr/bin/python3).

  /usr/bin/python3 layout/preamp/audio/drc_summary.py <drc.json>
"""
import collections
import json
import sys

d = json.load(open(sys.argv[1]))
v = d.get("violations", [])
u = d.get("unconnected_items", [])
p = d.get("schematic_parity", [])
print("violations:", len(v), "unconnected:", len(u), "parity:", len(p))
by = collections.defaultdict(list)
for x in v:
    by[(x["type"], x["severity"])].append(x)
for (t, s), xs in sorted(by.items(), key=lambda kv: -len(kv[1])):
    print(f"{len(xs):4d}  {s:8s} {t}")
    for x in xs[:3]:
        print("        ", x["description"], "|",
              " ; ".join(i["description"] for i in x.get("items", []))[:160])
