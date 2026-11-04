#!/usr/bin/env python3
"""L69: the runs on the NEW source (ADR-116; seq/oggi, seq/sano) against two references.

  1. the healthy run of the same event (L64b, an_l64b.csv: oggi/<sequence>), with the criteria of L54b3b
     (difetti() of confronta_l69.py, the same as confronta_l68.py's): `difetti`
  2. the run of the SAME case in L68 (L68/an_l68.csv: oggi/<caso>), on the source before ADR-116: the
     verdicts (VERD) equal, the times (TEMPI) within 5 ms, else listed: `vs_l68`. A case L68 did not
     have (R588 / R589) is «nuovo»
  The healthy runs (seq/sano/<sequence>) only against 1.

Writes <out.csv>: caso, ref, modo, evento, difetti, vs_l68.  Solo stdlib.
    /usr/bin/python3 -I psu/confronta_sorgente.py an_sorgente.csv confronto_sorgente.csv
"""
import csv
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
import modi  # noqa: E402
from confronta_l69 import AN_B, TEMPI, VERD, difetti, num  # noqa: E402

AN_68 = os.path.join(QUI, "..", "..", "L68", "an_l68.csv")
EV = dict(modi.EVENTI_L58B)


def vs(r, p):
    out = []
    for c in VERD:
        if r.get(c, "") != p.get(c, ""):
            out.append("%s %s -> %s" % (c, p.get(c, ""), r.get(c, "")))
    for c in TEMPI:
        x, y = num(r.get(c)), num(p.get(c))
        if (x is None) != (y is None):
            out.append("%s %s -> %s" % (c, p.get(c, "") or "-", r.get(c, "") or "-"))
        elif x is not None and abs(x - y) > 5:
            out.append("%s %.1f -> %.1f" % (c, y, x))
    return out


def main():
    an = {r["caso"]: r for r in csv.DictReader(open(sys.argv[1], newline=""))}
    b64 = {r["caso"]: r for r in csv.DictReader(open(AN_B, newline=""))}
    a68 = {r["caso"]: r for r in csv.DictReader(open(AN_68, newline=""))}
    guasti = {c[0]: c for c in modi.SIMULATI}
    out = []
    for k, r in sorted(an.items()):
        etich, caso = k.split("/")[-2:]
        if etich == "sano":
            d = difetti(r, b64["oggi/" + caso], caso)
            out.append(dict(caso=k, ref="-", modo="sano", evento=caso, difetti="; ".join(d), vs_l68=""))
            continue
        e = caso.rsplit("_", 1)[1]
        d = difetti(r, b64["oggi/" + EV[e]], EV[e])
        p = a68.get("oggi/" + caso)
        v = "nuovo" if p is None else "; ".join(vs(r, p))
        g = guasti[caso]
        out.append(dict(caso=k, ref=g[1], modo=g[2], evento=EV[e], difetti="; ".join(d), vs_l68=v))
    with open(sys.argv[2], "w", newline="") as f:
        w = csv.DictWriter(f, ["caso", "ref", "modo", "evento", "difetti", "vs_l68"], lineterminator="\n")
        w.writeheader()
        w.writerows(out)
    for x in out:
        print("%-30s %-16s | %s | L68: %s" % (x["caso"], x["evento"], x["difetti"] or "ok", x["vs_l68"] or "uguale"))


if __name__ == "__main__":
    main()
