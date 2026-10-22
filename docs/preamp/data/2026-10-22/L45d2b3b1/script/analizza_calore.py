#!/usr/bin/env python3
"""L45d2b3b1: il jack e il calore delle corse del banco del calore. Solo stdlib, /usr/bin/python3 -I.

Uso: analizza_calore.py <variante>    legge run/<variante>_<pos>/<modo>/ e scrive
                                      analisi_jack_<variante>.csv, calore_<variante>.csv

IL JACK: analizza_tr.py di L45a importato e chiamato com'e' (come L62b).
IL CALORE: le stesse regole di analizza_L62b.py (Tj = Ta + P * R_thJA a 27 e 60 C, Q127 in
SOT-223, le resistenze 0207 oltre 0,25 W, le 22 ohm oltre 0,34 W, Tj oltre 125 C a 60 C, P7 di
ADR-021), cifra per cifra: la variante l62b deve ridare calore.csv di L62b (confronta_l62b.py).
In piu', solo dove il deck li misura (la variante oggi), i diodi: 1N4148, R_thJA 350 K/W (Vishay
81857, limiti_blocco.csv di L45d2b2c), Tj oltre 125 C a 60 C d'aria come le altre parti.
"""
import csv
import glob
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
DATA = os.path.abspath(os.path.join(L, "..", ".."))
sys.path.insert(0, os.path.join(DATA, "2026-10-19", "L62b", "script"))
sys.path.insert(0, os.path.join(DATA, "2026-10-13", "L45a", "script"))
import analizza_tr as at      # noqa: E402
import analizza_L62b as a62   # noqa: E402

RTH_DIODO = 350.0


def main(argv):
    v = argv[1]
    dirs = sorted(d for d in glob.glob(os.path.join(L, "run", v + "_*", "*")) if os.path.isdir(d))
    at.main(["analizza_tr", os.path.join(L, "analisi_jack_%s.csv" % v)] + dirs)
    righe = []
    for d in dirs:
        cart, modo = d.split(os.sep)[-2:]
        f = at.leggi_fine(os.path.join(d, modo + "_fine.csv"))
        vv, pos = cart.split("_", 1)
        r = {"variante": vv, "posizione": pos, "modo": modo, "fine": "si" if f else "MANCA"}
        if not f:
            righe.append(r)
            continue
        r["I_rail_piu_mA"] = "%.1f" % (-f.get("ipp_avg", float("nan")) * 1e3)
        r["I_rail_meno_mA"] = "%.1f" % (f.get("imm_avg", float("nan")) * 1e3)
        for k in ("q132", "q133", "q127", "q122", "q125", "q146", "q160", "q163"):
            if "p_" + k in f:
                r["P_%s_W" % k] = "%.3f" % abs(f["p_" + k])
        oltre = []
        for ta in a62.TA:
            tj = {k: ta + abs(f["p_" + k]) * rt for k, rt in a62.RTH.items() if "p_" + k in f}
            if "p_q121a" in f:
                tj["q121"] = ta + (abs(f["p_q121a"]) + abs(f["p_q121b"])) * 233
            if "p_jq110a" in f:
                tj["jq110"] = ta + (abs(f["p_jq110a"]) + abs(f["p_jq110b"])) * 250
            c = max(tj, key=tj.get)
            r["Tj_max_%d" % ta] = "%.0f" % tj[c]
            r["Tj_max_disp_%d" % ta] = c
            for k in ("q132", "q133", "q127", "q160", "q163"):
                if k in tj:
                    r["Tj_%s_%d" % (k, ta)] = "%.0f" % tj[k]
            if ta == 60.0:
                oltre += ["%s %.0f C" % (k, t) for k, t in sorted(tj.items()) if t > a62.P7_TJ]
        pr = {k[2:]: abs(x) for k, x in f.items() if k.startswith("p_r")}
        for k in ("r134", "r135", "r128", "r129", "r161", "r162", "r164", "r165"):
            if k in pr:
                r["P_%s_W" % k] = "%.3f" % pr[k]
        for k, p in sorted(pr.items()):
            lim = a62.R22_LIM if k in ("r134", "r135") else a62.R_LIM
            if p > lim:
                oltre.append("%s %.2f W" % (k, p))
        r["oltre_i_limiti_60C"] = "; ".join(oltre)
        # i diodi (solo oggi): la potenza del piu' caldo e la sua Tj a 60 C
        pd = {k[2:]: abs(x) for k, x in f.items() if k.startswith("p_d")}
        if pd:
            c = max(pd, key=pd.get)
            r["P_diodo_max_W"] = "%.4f" % pd[c]
            r["diodo_max"] = c
            r["P_d158_W"] = "%.4f" % pd.get("d158", float("nan"))
            r["P_d159_W"] = "%.4f" % pd.get("d159", float("nan"))
            dio = ["%s %.0f C" % (k, 60.0 + p * RTH_DIODO) for k, p in sorted(pd.items())
                   if 60.0 + p * RTH_DIODO > a62.P7_TJ]
            r["oltre_diodi_60C"] = "; ".join(dio)
        righe.append(r)
    campi = []
    for r in righe:
        campi += [k for k in r if k not in campi]
    with open(os.path.join(L, "calore_%s.csv" % v), "w", newline="") as fo:
        w = csv.DictWriter(fo, fieldnames=campi)
        w.writeheader()
        w.writerows(righe)
    print("calore %s: %d righe -> calore_%s.csv" % (v, len(righe), v))


if __name__ == "__main__":
    main(sys.argv)
