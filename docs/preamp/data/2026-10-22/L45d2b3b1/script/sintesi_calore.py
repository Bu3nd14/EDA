#!/usr/bin/env python3
"""L45d2b3b1: la sintesi del banco del calore sul blocco di oggi, per modo, il peggiore sulle cinque
posizioni (A, F1, F2, B, B a +10 dB). Solo stdlib, /usr/bin/python3 -I.

Uso: sintesi_calore.py     legge analisi_jack_oggi.csv e calore_oggi.csv, scrive sintesi_calore.csv

Le colonne: lo stato peggiore; il jack (V «A» col metodo di PR-23) sulla principale, la fissa 1 e la
fissa 2 (questa col condensatore di L45a, 4,7 uF: la Stax si giudica sul banco della Stax), e i dB
SPL della principale; la Tj piu' alta a 60 C d'aria e il suo dispositivo; le parti oltre i limiti a
60 C (P7 di ADR-021: Tj oltre 125 C, resistenze 0207 oltre 0,25 W, le 22 ohm oltre 0,34 W) con in
quante posizioni; i diodi (la potenza del piu' caldo, D158 / D159). Accanto, la colonna «calore» di
L45a (fmea_blocco.csv: il blocco di allora, a 27 C d'aria). I controlli prima: il riferimento sano
(uscita del blocco, corrente del rail +) e CTRL_OUT_VP sopra 0,87 V alla principale.
"""
import csv
import os
import sys

L = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.abspath(os.path.join(L, "..", ".."))
# sintesi_calore.py [variante]: oggi (default, -> sintesi_calore.csv) o dopo097 (il blocco di ADR-097,
# -> sintesi_calore_dopo097.csv)
V = sys.argv[1] if len(sys.argv) > 1 else "oggi"
USCITA = "sintesi_calore.csv" if V == "oggi" else "sintesi_calore_%s.csv" % V
jack = {(r["variante"], r["modo"]): r for r in csv.DictReader(open(os.path.join(L, "analisi_jack_%s.csv" % V)))}
cal = list(csv.DictReader(open(os.path.join(L, "calore_%s.csv" % V))))
l45a = {r["modo"]: r for r in csv.DictReader(open(os.path.join(DATA, "2026-10-13", "L45a", "fmea_blocco.csv")))}


def f(x, d=float("nan")):
    try:
        return float(x)
    except (TypeError, ValueError):
        return d


print("CONTROLLI")
for r in cal:
    j = jack[(V + "_" + r["posizione"], r["modo"])]
    if r["modo"] == "rif":
        print("  %-5s rif: uscita blocco %s V, rail + %s mA, Tj finale 27 C %s, stato %s"
              % (r["posizione"], j.get("out_avg"), r.get("I_rail_piu_mA"), r.get("Tj_q132_27"), j["stato"]))
    if r["modo"] == "CTRL_OUT_VP":
        print("  CTRL_OUT_VP %s: main %s V, sopra il tetto %s" % (r["posizione"], j["main_A_V"], j["sopra_tetto_main"]))

righe = {}
for r in cal:
    if r["modo"] in ("rif", "CTRL_OUT_VP"):
        continue
    j = jack[(V + "_" + r["posizione"], r["modo"])]
    s = righe.setdefault(r["modo"], {"stati": set(), "pos": [], "main": 0.0, "fix1": 0.0, "fix2": 0.0,
                                     "dB": -999.0, "tj": 0.0, "tjd": "", "oltre": {}, "pd": 0.0,
                                     "pdd": "", "p158": 0.0, "p159": 0.0, "diodi": {}, "manca": 0})
    s["pos"].append(r["posizione"])
    s["stati"].add(j["stato"] if r["fine"] == "si" else "MANCA")
    if r["fine"] != "si":
        s["manca"] += 1
    s["main"] = max(s["main"], f(j["main_A_V"], 0))
    s["fix1"] = max(s["fix1"], f(j["fix1_A_V"], 0))
    s["fix2"] = max(s["fix2"], f(j["fix2_A_V"], 0))
    s["dB"] = max(s["dB"], f(j["main_dB_SPL"], -999))
    if f(r.get("Tj_max_60"), 0) > s["tj"]:
        s["tj"], s["tjd"] = f(r["Tj_max_60"]), "%s (%s)" % (r["Tj_max_disp_60"], r["posizione"])
    for o in filter(None, (x.strip() for x in r.get("oltre_i_limiti_60C", "").split(";"))):
        s["oltre"].setdefault(o.split()[0], []).append(o.split(" ", 1)[1])
    for o in filter(None, (x.strip() for x in r.get("oltre_diodi_60C", "").split(";"))):
        s["diodi"].setdefault(o.split()[0], []).append(o.split(" ", 1)[1])
    if f(r.get("P_diodo_max_W"), 0) > s["pd"]:
        s["pd"], s["pdd"] = f(r["P_diodo_max_W"]), r["diodo_max"]
    s["p158"] = max(s["p158"], f(r.get("P_d158_W"), 0))
    s["p159"] = max(s["p159"], f(r.get("P_d159_W"), 0))

out = []
for m in sorted(righe):
    s = righe[m]
    n = len(s["pos"])
    stato = "ok" if s["stati"] == {"ok"} else "/".join(sorted(s["stati"]))
    oltre = "; ".join("%s %s" % (p, max(v, key=lambda x: f(x.split()[0]))) +
                      ("" if len(v) == n else " (%d/%d)" % (len(v), n)) for p, v in sorted(s["oltre"].items()))
    diodi = "; ".join("%s %s" % (p, max(v, key=lambda x: f(x.split()[0]))) for p, v in sorted(s["diodi"].items()))
    out.append({"modo": m, "posizioni": n, "stato": stato,
                "main_A_V": "%.4g" % s["main"], "main_dB_SPL": "%.1f" % s["dB"],
                "fix1_A_V": "%.4g" % s["fix1"], "fix2_4u7_A_V": "%.4g" % s["fix2"],
                "Tj_max_60_C": "%.0f" % s["tj"], "Tj_max_disp": s["tjd"],
                "oltre_i_limiti_60C": oltre, "P_diodo_max_W": "%.4f" % s["pd"], "diodo_max": s["pdd"],
                "P_d158_max_W": "%.4f" % s["p158"], "P_d159_max_W": "%.4f" % s["p159"],
                "diodi_oltre_60C": diodi,
                "L45a_calore_27C": l45a[m]["calore"] if m in l45a else "(modo nuovo)"})
with open(os.path.join(L, USCITA), "w", newline="") as fo:
    w = csv.DictWriter(fo, fieldnames=list(out[0]))
    w.writeheader()
    w.writerows(out)
n_oltre = [o for o in out if o["oltre_i_limiti_60C"] or o["diodi_oltre_60C"]]
print("\n%d modi, %d con parti oltre i limiti a 60 C, %d con corse non ok" %
      (len(out), len(n_oltre), len([o for o in out if o["stato"] != "ok"])))
for o in n_oltre:
    print("  %-12s Tj %s %-14s %s %s   [L45a: %s]" % (o["modo"], o["Tj_max_60_C"], o["Tj_max_disp"],
                                                  o["oltre_i_limiti_60C"], o["diodi_oltre_60C"], o["L45a_calore_27C"]))
for o in out:
    if o["stato"] != "ok":
        print("  NON OK %-12s %s" % (o["modo"], o["stato"]))
