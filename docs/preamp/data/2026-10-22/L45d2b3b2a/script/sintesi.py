#!/usr/bin/env python3
"""L45d2b3b2a: la sintesi del banco del calore per una variante, per modo, il peggiore sulle cinque
posizioni. Le regole sono quelle di sintesi_calore.py di L45d2b3b1 (P7 di ADR-021: Tj oltre 125 C a
60 C d'aria, resistenze 0207 oltre 0,25 W, le 22 ohm oltre 0,34 W; i diodi 1N4148 a 350 K/W).
Solo stdlib, /usr/bin/python3 -I.

Uso: sintesi.py <variante> [...]    legge analisi_jack_<v>.csv e calore_<v>.csv, scrive sintesi_<v>.csv
     e stampa, per ogni modo, la Tj piu' alta, la parte e cio' che e' oltre i limiti.

In piu' di b1: la corrente del rail + e del rail - del canale in eccesso sul riferimento sano di oggi
(il guasto la aggiunge tutta al blocco guasto), e il massimo assoluto (150 C) passato o no.
"""
import csv
import os
import sys

L = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TJ_ASS = 150.0


def f(x, d=float("nan")):
    try:
        return float(x)
    except (TypeError, ValueError):
        return d


def rif_oggi():
    out = {}
    for r in csv.DictReader(open(os.path.join(L, "calore_oggi.csv"))):
        if r["modo"] == "rif":
            out[r["posizione"]] = (f(r["I_rail_piu_mA"]), f(r["I_rail_meno_mA"]))
    return out


def sintesi(v):
    jack = {(r["variante"], r["modo"]): r for r in csv.DictReader(open(os.path.join(L, "analisi_jack_%s.csv" % v)))}
    cal = list(csv.DictReader(open(os.path.join(L, "calore_%s.csv" % v))))
    rif = rif_oggi()
    righe = {}
    for r in cal:
        if r["modo"] == "CTRL_OUT_VP":
            continue
        # analizza_calore.py di b1 divide la cartella al primo «_»: per d_Q148ap_A la «variante» e'
        # «d» e la «posizione» «Q148ap_A». La cartella intera e' la loro unione.
        cart = r["variante"] + "_" + r["posizione"]
        if not cart.startswith(v + "_"):
            sys.exit("RIFIUTATO: %s non e' della variante %s" % (cart, v))
        r = dict(r, posizione=cart[len(v) + 1:])
        j = jack[(cart, r["modo"])]
        s = righe.setdefault(r["modo"], {"stati": set(), "pos": [], "main": 0.0, "fix1": 0.0, "dB": -999.0,
                                         "tj": 0.0, "tjd": "", "oltre": {}, "diodi": {}, "dip": 0.0, "dim": 0.0})
        s["pos"].append(r["posizione"])
        s["stati"].add(j["stato"] if r["fine"] == "si" else "MANCA")
        s["main"] = max(s["main"], f(j["main_A_V"], 0))
        s["fix1"] = max(s["fix1"], f(j["fix1_A_V"], 0))
        s["dB"] = max(s["dB"], f(j["main_dB_SPL"], -999))
        if f(r.get("Tj_max_60"), 0) > s["tj"]:
            s["tj"], s["tjd"] = f(r["Tj_max_60"]), "%s (%s)" % (r["Tj_max_disp_60"], r["posizione"])
        ip, im = rif[r["posizione"]]
        s["dip"] = max(s["dip"], f(r.get("I_rail_piu_mA"), 0) - ip)
        s["dim"] = max(s["dim"], f(r.get("I_rail_meno_mA"), 0) - im)
        for o in filter(None, (x.strip() for x in r.get("oltre_i_limiti_60C", "").split(";"))):
            s["oltre"].setdefault(o.split()[0], []).append(o.split(" ", 1)[1])
        for o in filter(None, (x.strip() for x in r.get("oltre_diodi_60C", "").split(";"))):
            s["diodi"].setdefault(o.split()[0], []).append(o.split(" ", 1)[1])
    out = []
    for m in sorted(righe):
        s = righe[m]
        n = len(s["pos"])
        stato = "ok" if s["stati"] == {"ok"} else "/".join(sorted(s["stati"]))
        oltre = "; ".join("%s %s" % (p, max(x, key=lambda y: f(y.split()[0]))) +
                          ("" if len(x) == n else " (%d/%d)" % (len(x), n)) for p, x in sorted(s["oltre"].items()))
        diodi = "; ".join("%s %s" % (p, max(x, key=lambda y: f(y.split()[0]))) for p, x in sorted(s["diodi"].items()))
        tjd = max([s["tj"]] + [f(max(x, key=lambda y: f(y.split()[0])).split()[0]) for x in s["diodi"].values()])
        out.append({"variante": v, "modo": m, "posizioni": n, "stato": stato,
                    "main_A_V": "%.4g" % s["main"], "main_dB_SPL": "%.1f" % s["dB"], "fix1_A_V": "%.4g" % s["fix1"],
                    "Tj_max_60_C": "%.0f" % s["tj"], "Tj_max_disp": s["tjd"],
                    "dI_rail_piu_mA": "%.1f" % s["dip"], "dI_rail_meno_mA": "%.1f" % s["dim"],
                    "oltre_i_limiti_60C": oltre, "diodi_oltre_60C": diodi,
                    "verdetto": "entro" if not (oltre or diodi) else
                                ("oltre P7, sotto 150 C" if tjd <= TJ_ASS and not any(
                                    o.split()[0][0] == "r" for o in oltre.split("; ") if o) else "oltre")})
    with open(os.path.join(L, "sintesi_%s.csv" % v), "w", newline="") as fo:
        w = csv.DictWriter(fo, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    return out


if __name__ == "__main__":
    for v in sys.argv[1:]:
        out = sintesi(v)
        if "rif" in {o["modo"] for o in out}:
            r = [o for o in out if o["modo"] == "rif"][0]
            print("%s rif: Tj %s %s, %s" % (v, r["Tj_max_60_C"], r["Tj_max_disp"], r["verdetto"]))
        n = [o for o in out if o["verdetto"] != "entro" and o["modo"] != "rif"]
        print("%s: %d modi, %d oltre i limiti" % (v, len(out) - ("rif" in {o["modo"] for o in out}), len(n)))
        for o in out:
            if o["modo"] == "rif":
                continue
            print("  %-10s %5s C %-16s dI+ %7s mA  main %6s dB  %s %s  [%s]" % (
                o["modo"], o["Tj_max_60_C"], o["Tj_max_disp"], o["dI_rail_piu_mA"], o["main_dB_SPL"],
                o["oltre_i_limiti_60C"], o["diodi_oltre_60C"], o["verdetto"]))
