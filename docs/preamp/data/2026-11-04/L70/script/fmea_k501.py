#!/usr/bin/env python3
"""L70: the rows of today's FMEA (data/2026-11-03/L69/fmea_oggi.csv, 692 rows) that the two
simplifications touch:
  - the rows of the parts each variant removes (they leave the FMEA);
  - the rows whose effect relies on K501 opening / the latch / the toroid going off (with S1 the
    toroid stays on until the front switch: these must be re-read at thermal steady state).
Prints counts by priorita_dopo and writes righe_toccate.csv.

    /usr/bin/python3 -I script/fmea_k501.py
"""
import collections
import csv
import os
import re

L = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = os.path.join(os.path.dirname(os.path.dirname(L)), "2026-11-03", "L69", "fmea_oggi.csv")
TOLTE = {
    "s2": "C518 D533 D534 D535 Q504 R510 R511 R512 R554 R555 R569".split(),
    "s1": "C552 C553 C554 C555 D534 D535 D541 Q513 Q514 R580 R581 R582 R583 R584 R585".split(),
}
TOLTE["s1s2"] = sorted(set(TOLTE["s1"]) | set(TOLTE["s2"]))
# U506 channel A (S2), U513 channel D (S2), U515 channels C / D (S1): rows by mode text
CANALI = {"s2": [("U506", r"\b(A|ch ?A|canale A|1)\b"), ("U513", r"\b(D|canale D|4)\b")],
          "s1": [("U515", r"\b(C|D|canale C|canale D)\b")]}
CANALI["s1s2"] = CANALI["s1"] + CANALI["s2"]
K501 = re.compile(r"K501|ritenuta|toroidale|MAINS_REQ", re.I)

righe = list(csv.DictReader(open(F)))
print("FMEA di oggi: %d righe, %s" % (len(righe), dict(collections.Counter(r["priorita_dopo"] for r in righe))))
out = []
for v in ("s2", "s1", "s1s2"):
    via = [r for r in righe if r["ref"] in TOLTE[v]]
    ch = [r for r in righe if any(r["ref"] == u and re.search(p, r["modo"] + " " + r["funzione"])
                                  for u, p in CANALI[v])]
    print("\n== %s: righe delle parti tolte %d %s" % (v, len(via), dict(collections.Counter(r["priorita_dopo"] for r in via))))
    print("   righe dei canali tolti (da rileggere a mano) %d %s" % (len(ch), dict(collections.Counter(r["priorita_dopo"] for r in ch))))
    for r in ch:
        print("     %s | %s | %s | %s" % (r["ref"], r["funzione"][:40], r["modo"][:40], r["priorita_dopo"]))
    for r in via + ch:
        out.append(dict(variante=v, motivo="parte tolta" if r in via else "canale tolto", **r))
tocca = [r for r in righe if K501.search(" ".join(r[k] for k in ("effetto_dopo", "rimedio", "decisione", "stato")))
         and r["ref"] not in TOLTE["s1s2"]]
print("\nrighe (parti che restano) il cui effetto passa da K501 / la ritenuta / il toroidale: %d %s"
      % (len(tocca), dict(collections.Counter(r["priorita_dopo"] for r in tocca))))
for r in tocca:
    out.append(dict(variante="s1", motivo="effetto da K501", **r))
    if r["priorita_dopo"] == "alta":
        print("   ALTA %s | %s | %s" % (r["ref"], r["modo"][:40], r["effetto_dopo"][:90]))
with open(os.path.join(L, "righe_toccate.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["variante", "motivo"] + list(righe[0].keys()))
    w.writeheader()
    w.writerows(out)
