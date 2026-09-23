#!/usr/bin/env python3
"""L40: V1 per variante e istanza, col criterio di L39/script/margini.py
(ADR-024): blocco B e buffer pos 1 (cavo al jack, 1 fF - 4,7 nF), tutte le
sorgenti e i carichi; blocco A cablaggio <= 1 nF, entrambi i carichi, e il trim
di L16 col cablaggio <= 1 nF. Crossover della cella a vuoto accanto.

Uso: /usr/bin/python3 sintesi_v1.py <fase>   -> <fase>/sintesi_v1.csv
"""
import csv
import glob
import os
import sys

L40 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fase = sys.argv[1]
D = os.path.join(L40, fase)
CAB1N = ("1f", "47p", "100p", "220p", "470p", "1n")


def leggi(deck, var, f):
    p = os.path.join(D, "%s__%s" % (deck, var), f)
    return list(csv.DictReader(open(p))) if os.path.exists(p) else []


def minimo(r, filtro):
    r = [x for x in r if filtro(x)]
    return min(r, key=lambda x: float(x["pm_deg"])) if r else None


def fc(r, filtro):
    r = [x for x in r if filtro(x)]
    return float(r[0]["fcross_hz"]) / 1e3 if r else float("nan")


var = sorted({os.path.basename(p).split("__", 1)[1] for p in glob.glob(os.path.join(D, "*__*"))
              if os.path.isdir(p)})
COL = ["B0", "B3", "B10", "A", "Atrim", "buf"]
out = []
for v in var:
    lb = leggi("tb_loop", v, "tb_loop_margini.csv")
    la = leggi("tb_loop_blockA", v, "tb_loop_blockA.csv")
    lt = leggi("tb_loop_blockA", v, "tb_loop_blockA_trim.csv")
    lf = leggi("tb_loop_bufferfissa", v, "tb_loop_bufferfissa.csv")
    cel = {
        "B0": (lb, lambda x: x["mode"] == "0db" and x["pos"] == "1",
               lambda x: x["mode"] == "0db" and x["rsrc"] == "1m" and x["pos"] == "1"
               and x["cprobe"] == "1f" and x["rload"] == "100k"),
        "B3": (lb, lambda x: x["mode"] == "3db" and x["pos"] == "1",
               lambda x: x["mode"] == "3db" and x["rsrc"] == "1m" and x["pos"] == "1"
               and x["cprobe"] == "1f" and x["rload"] == "100k"),
        "B10": (lb, lambda x: x["mode"] == "10db" and x["pos"] == "1",
                lambda x: x["mode"] == "10db" and x["rsrc"] == "1m" and x["pos"] == "1"
                and x["cprobe"] == "1f" and x["rload"] == "100k"),
        "A": (la, lambda x: x["cwire"] in CAB1N,
              lambda x: x["carico"] == "1" and x["rsrc"] == "1m" and x["cwire"] == "1f"),
        "Atrim": (lt, lambda x: x["cwire"] in CAB1N,
                  lambda x: x["cand"] == "1" and x["pos"] == "6" and x["rsrc"] == "1m"
                  and x["cwire"] == "1f"),
        "buf": (lf, lambda x: x["pos"] == "1",
                lambda x: x["pos"] == "1" and x["rld"] == "10k" and x["cprobe"] == "1f"),
    }
    riga = [v]
    for c in COL:
        r, f, fv = cel[c]
        m = minimo(r, f)
        riga += [float(m["pm_deg"]) if m else float("nan"), fc(r, fv),
                 float(m["tdb_10hz"]) if m else float("nan")]
    out.append(riga)
with open(os.path.join(D, "sintesi_v1.csv"), "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["variante"] + ["%s_%s" % (c, q) for c in COL for q in ("pm_min", "fc_khz", "t10_db")])
    w.writerows(out)
print("%-18s" % "variante" + "".join("%15s" % c for c in COL) + "   min")
for r in out:
    pm = r[1::3]
    print("%-18s" % r[0] + "".join("%7.2f/%6.0fk" % (r[1 + 3 * i], r[2 + 3 * i]) for i in range(len(COL)))
          + "  %6.2f %s" % (min(pm), "OK" if min(pm) >= 60 else "sotto"))
