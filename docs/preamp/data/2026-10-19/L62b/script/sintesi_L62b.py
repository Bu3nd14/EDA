#!/usr/bin/env python3
"""L62a: la sintesi delle corse di guasto, per variante e modo, il peggiore sulle cinque posizioni
(A, F1, F2, B, B a +10 dB). Legge analisi_jack.csv e calore.csv, scrive sintesi.csv e stampa.

Colonne: lo stato peggiore delle corse; il jack (il massimo di main / fix1 / fix2 «A», in mV);
la corrente del rail + del canale; la Tj del finale piu' caldo a 27 e 60 C d'aria; la 22 ohm piu'
calda; le parti oltre i limiti a 60 C (in quante posizioni). I controlli prima: il riferimento sano
della base (uscita del blocco -2,9 mV, ~38 mA per blocco) e CTRL_OUT_VP sopra 0,87 V.
"""
import csv
import os

L62A = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
jack = {(r["variante"], r["modo"]): r for r in csv.DictReader(open(os.path.join(L62A, "analisi_jack.csv")))}
cal = list(csv.DictReader(open(os.path.join(L62A, "calore.csv"))))


def f(x, d=float("nan")):
    try:
        return float(x)
    except (TypeError, ValueError):
        return d


print("CONTROLLI")
for r in cal:
    if r["modo"] == "rif" and r["variante"] == "base":
        j = jack[("base_" + r["posizione"], "rif")]
        print("  base %-5s rif: uscita blocco %s V, rail + %s mA, Tj finale 27 C %s, stato %s"
              % (r["posizione"], j.get("out_avg"), r["I_rail_piu_mA"], r.get("Tj_q132_27"), j["stato"]))
    if r["modo"] == "CTRL_OUT_VP":
        j = jack[("base_" + r["posizione"], "CTRL_OUT_VP")]
        print("  CTRL_OUT_VP %s: main %s V, sopra il tetto %s" % (r["posizione"], j["main_A_V"], j["sopra_tetto_main"]))

righe = {}
for r in cal:
    if r["modo"] == "CTRL_OUT_VP":
        continue
    j = jack[("%s_%s" % (r["variante"], r["posizione"]), r["modo"])]
    k = (r["variante"], r["modo"])
    s = righe.setdefault(k, {"variante": k[0], "modo": k[1], "stati": set(), "jack_mV": 0.0,
                             "I_rail_mA": 0.0, "Tj_finale_27": 0.0, "Tj_finale_60": 0.0,
                             "P_22_W": 0.0, "oltre": {}, "n": 0})
    s["n"] += 1
    s["stati"].add(j["stato"])
    s["jack_mV"] = max(s["jack_mV"], 1e3 * max(f(j["main_A_V"], 0), f(j["fix1_A_V"], 0), f(j["fix2_A_V"], 0)))
    s["I_rail_mA"] = max(s["I_rail_mA"], f(r.get("I_rail_piu_mA"), 0))
    for ta in (27, 60):
        s["Tj_finale_%d" % ta] = max(s["Tj_finale_%d" % ta], f(r.get("Tj_q132_%d" % ta), 0), f(r.get("Tj_q133_%d" % ta), 0))
    s["P_22_W"] = max(s["P_22_W"], f(r.get("P_r134_W"), 0), f(r.get("P_r135_W"), 0))
    for o in filter(None, (x.strip() for x in r.get("oltre_i_limiti_60C", "").split(";"))):
        p = o.split()[0]
        s["oltre"].setdefault(p, []).append(o.split(" ", 1)[1])

out = []
print("\n%-8s %-10s %-4s %-10s %9s %8s %7s %7s %7s  oltre i limiti a 60 C" % (
    "variante", "modo", "pos", "stato", "jack mV", "rail+mA", "Tj27", "Tj60", "P22 W"))
for k in sorted(righe):
    s = righe[k]
    stato = "ok" if s["stati"] == {"ok"} else "/".join(sorted(s["stati"]))
    oltre = "; ".join("%s %s" % (p, max(v, key=lambda x: f(x.split()[0]))) + ("" if len(v) == s["n"] else " (%d/%d)" % (len(v), s["n"]))
                      for p, v in sorted(s["oltre"].items()))
    print("%-8s %-10s %-4d %-10s %9.3f %8.1f %7.0f %7.0f %7.3f  %s" % (
        k[0], k[1], s["n"], stato, s["jack_mV"], s["I_rail_mA"], s["Tj_finale_27"], s["Tj_finale_60"], s["P_22_W"], oltre))
    out.append({"variante": k[0], "modo": k[1], "posizioni": s["n"], "stato": stato,
                "jack_max_mV": "%.3f" % s["jack_mV"], "I_rail_piu_max_mA": "%.1f" % s["I_rail_mA"],
                "Tj_finale_27_C": "%.0f" % s["Tj_finale_27"], "Tj_finale_60_C": "%.0f" % s["Tj_finale_60"],
                "P_22ohm_max_W": "%.3f" % s["P_22_W"], "oltre_i_limiti_60C": oltre})
with open(os.path.join(L62A, "sintesi.csv"), "w", newline="") as fo:
    w = csv.DictWriter(fo, fieldnames=list(out[0]))
    w.writeheader()
    w.writerows(out)
