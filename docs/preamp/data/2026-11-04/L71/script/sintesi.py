#!/usr/bin/env python3
"""L71: the figures of the report, from an_l71.csv, stato_l71.csv and the chain's tables, by family
and lot of runs (nominal values / tolerance corners). Prints sintesi_l71.txt's content.
    /usr/bin/python3 -I script/sintesi.py > sintesi_l71.txt"""
import csv
import glob
import os
import re

L = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
an = {r["caso"]: r for r in csv.DictReader(open(os.path.join(L, "an_l71.csv")))}
st = {r["caso"]: r for r in csv.DictReader(open(os.path.join(L, "stato_l71.csv")))}
assert set(an) == set(st)
print("corse lette: %d (con ok.txt: tutte; ripieghi numerici: %d)" % (
    len(an), len(glob.glob(os.path.join(L, "seq", "*", "*", "ripiego.txt")))))
for lab, sel in (("valori nominali", lambda e: "ang" not in e), ("angoli di ADR-105", lambda e: "ang" in e)):
    print("\n== %s" % lab)
    fams = {}
    for c in an:
        e, n = c.split("/")
        if sel(e):
            fams.setdefault(re.sub(r"_[0-9p]+$", "", n), []).append(c)
    for f, cs in sorted(fams.items()):
        num = lambda col, src=st: [float(src[c][col]) for c in cs if src[c].get(col, "") != ""]  # noqa: E731
        dp, r41, mm = num("d_perm_ms", an), num("r41_min_ms"), num("mus_min_ms")
        print("%-14s %3d corse | C2 fuori %d, C3 fuori %d | stato diverso dall'atteso %d | ritenuta %d | "
              "Delta min %s ms | r41 min %s ms | musica min %s ms | perm. dopo il jack %d" % (
                  f, len(cs), sum(an[c]["C2"] != "1" for c in cs), sum(an[c]["C3"] != "1" for c in cs),
                  sum(st[c]["esito"] != "atteso" for c in cs), sum(st[c]["ritenuta"] == "1" for c in cs),
                  "-" if not dp else "%.1f" % min(dp), "-" if not r41 else "%.1f" % min(r41),
                  "-" if not mm else "%.1f" % min(mm), sum(int(st[c]["perm_dopo"] or 0) for c in cs)))
    c3 = sorted((float(an[c]["d_perm_ms"]), c) for c in an if sel(c.split("/")[0]) and an[c]["C3"] != "1")
    print("C3 fuori (%d): %s" % (len(c3), "; ".join("%s %.1f" % (c, v) for v, c in c3)))
    r = sorted((float(st[c]["r41_min_ms"]), c) for c in st if sel(c.split("/")[0]) and st[c]["r41_min_ms"])
    print("r41 piu' piccoli: %s" % "; ".join("%s %.1f" % (c, v) for v, c in r[:4]))
print("\n== al jack (V2, <= 100 uV = 33,45 dB SPL)")
tab = []
for p in sorted(glob.glob(os.path.join(L, "tabella_*.csv"))):
    g = os.path.basename(p)[len("tabella_"):-4]
    for r in csv.DictReader(open(p)):
        tab.append((float(r["picco_V"]), r["dB_SPL_picco_1m"], g, r["caso"], r["esito"]))
for nome, filt in (("aperture del jack", lambda x: x[2] != "rientro"), ("rientri", lambda x: x[2] == "rientro")):
    xs = sorted(filter(filt, tab), reverse=True)
    print("%s: %d righe, sopra la soglia %d, peggiore %.3g V = %s dB SPL (%s %s)" % (
        nome, len(xs), sum(x[4] != "sotto" for x in xs), xs[0][0], xs[0][1], xs[0][2], xs[0][3]))
