#!/usr/bin/env python3
"""L62a: il jack e il calore delle corse di guasto. Solo stdlib, /usr/bin/python3 -I.

Uso: analizza_L62a.py       legge run/<v>_<pos>/<modo>/ e scrive analisi_jack.csv, calore.csv

IL JACK: analizza_tr.py di L45a importato e chiamato com'e' (il metodo di PR-23, v2_metodo; i
volt «A» al jack, i dB SPL della principale e della Stax), su ogni cartella di run/.

IL CALORE, dai <modo>_fine.csv (media degli ultimi 10 ms): Tj = Ta + P * R_thJA a Ta = 27 e 60 C
(P7, ADR-021). Le R_thJA sono quelle di analizza_tr.RTH, salvo:
  q127  125 C/W: DZT5551 in SOT-223 sulla piazzola minima (ADR-082), non piu' i 417 del SOT-23
  q160, q163  417 C/W: le parti nuove dei rimedi, MMBT in SOT-23 (il caso peggiore dichiarato)
Le resistenze sono assiali 0207 (FP_R di gain_block.py): oltre 0,25 W si segnala. Per le due
22 ohm d'emettitore il vincolo di BOM e' >= 0,34 W a 60 C (ADR-021, gain_block.py).
La corrente dei rail (limitations #59): ipp_avg / imm_avg, il canale intero (quattro blocchi).
"""
import csv
import glob
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L62A = os.path.dirname(QUI)
DATA = os.path.abspath(os.path.join(L62A, "..", ".."))
sys.path.insert(0, os.path.join(DATA, "2026-10-13", "L45a", "script"))
import analizza_tr as at  # noqa: E402

RTH = dict(at.RTH)
RTH.update({"q127": 125, "q160": 417, "q163": 417})
TJMAX = {"q132": 150, "q133": 150}       # MJE15032/33; tutti gli altri 150 come le MMBT/DZT
P7_TJ = 125.0
R_LIM = 0.25
R22_LIM = 0.34
TA = (27.0, 60.0)


def main():
    dirs = sorted(d for d in glob.glob(os.path.join(L62A, "run", "*", "*"))
                  if os.path.isdir(d) and os.path.basename(os.path.dirname(d)).startswith("base_"))
    # L62b: solo le cartelle dei guasti (base_<pos>); run/ contiene anche tb_base, temperatura e
    # quelle di V4 a caldo
    at.main(["analizza_tr", os.path.join(L62A, "analisi_jack.csv")] + dirs)
    righe = []
    for d in dirs:
        cart, modo = d.split(os.sep)[-2:]
        f = at.leggi_fine(os.path.join(d, modo + "_fine.csv"))
        v, pos = cart.split("_", 1)
        r = {"variante": v, "posizione": pos, "modo": modo, "fine": "si" if f else "MANCA"}
        if not f:
            righe.append(r)
            continue
        r["I_rail_piu_mA"] = "%.1f" % (-f.get("ipp_avg", float("nan")) * 1e3)
        r["I_rail_meno_mA"] = "%.1f" % (f.get("imm_avg", float("nan")) * 1e3)
        for k in ("q132", "q133", "q127", "q122", "q125", "q146", "q160", "q163"):
            if "p_" + k in f:
                r["P_%s_W" % k] = "%.3f" % abs(f["p_" + k])
        oltre = []
        for ta in TA:
            tj = {k: ta + abs(f["p_" + k]) * rt for k, rt in RTH.items() if "p_" + k in f}
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
                oltre += ["%s %.0f C" % (k, t) for k, t in sorted(tj.items()) if t > P7_TJ]
        pr = {k[2:]: abs(x) for k, x in f.items() if k.startswith("p_r")}
        for k in ("r134", "r135", "r128", "r129", "r161", "r162", "r164", "r165"):
            if k in pr:
                r["P_%s_W" % k] = "%.3f" % pr[k]
        for k, p in sorted(pr.items()):
            lim = R22_LIM if k in ("r134", "r135") else R_LIM
            if p > lim:
                oltre.append("%s %.2f W" % (k, p))
        r["oltre_i_limiti_60C"] = "; ".join(oltre)
        righe.append(r)
    campi = []
    for r in righe:
        campi += [k for k in r if k not in campi]
    with open(os.path.join(L62A, "calore.csv"), "w", newline="") as fo:
        w = csv.DictWriter(fo, fieldnames=campi)
        w.writeheader()
        w.writerows(righe)
    print("calore: %d righe -> calore.csv" % len(righe))


if __name__ == "__main__":
    main()
