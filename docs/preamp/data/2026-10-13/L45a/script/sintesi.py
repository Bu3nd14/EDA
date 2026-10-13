#!/usr/bin/env python3
"""L45a: la sintesi della FMEA del blocco (NC-042). Solo stdlib, /usr/bin/python3.

Uso: sintesi.py OUT.csv ANALISI.csv...

Da ogni riga di analizza_tr.py:
  classe dell'uscita del blocco guasto, negli ultimi 10 ms della corsa (t = 2,29-2,30 s):
    rail+ / rail-   |media| > 10 V
    oscilla         max - min > 0,1 V
    continua        0,05 V < |media - riposo| <= 10 V
    nessuna         altrimenti (il blocco resta a meno di 50 mV dal riposo, -2,9 mV)
  calore            Tj > 150 C su un dispositivo del blocco (27 C d'aria; R_thJA come caldo.py), o una
                    delle resistenze che contano sopra la sua potenza: 22 ohm 0,30 W (gain_block.py
                    :625), 56 ohm del VAS e del carico 0,25 W, 10 ohm della cella 0,25 W (assunta)
  verdetto al jack (il metodo di PR-23):
    SOPRA IL TETTO  A > 0,87 V (112,2 dB SPL)
    sopra l'obiettivo  2 mV < A <= 0,87 V
    entro           A <= 2 mV
Il verdetto si da' sul jack che il blocco serve: B -> principale; F2 -> fissa 2; F1 -> fissa 1;
A -> tutti e tre (le fisse in continua, la principale attraverso C_T e il blocco B).
"""
import csv
import sys

RIPOSO = -2.874e-3
P_MAX = {"p_r134_W": 0.30, "p_r135_W": 0.30, "p_r123_W": 0.25, "p_r126_W": 0.25,
         "p_r144_W": 0.25}


def f(r, k):
    try:
        return float(r.get(k, "nan"))
    except ValueError:
        return float("nan")


def classe(r):
    m, hi, lo = f(r, "out_avg"), f(r, "out_max"), f(r, "out_min")
    if m != m:
        return "?"
    if m > 10:
        return "rail+"
    if m < -10:
        return "rail-"
    if hi - lo > 0.1:
        return "oscilla"
    if abs(m - RIPOSO) > 0.05:
        return "continua %.2f V" % m
    return "nessuna"


def verdetto(v):
    if v != v:
        return "?"
    if v > 0.87:
        return "SOPRA IL TETTO"
    if v > 2e-3:
        return "sopra l'obiettivo"
    return "entro"


def main(argv):
    righe = []
    for p in argv[2:]:
        righe += list(csv.DictReader(open(p)))
    out = []
    for r in righe:
        var = r["variante"].replace("tr_", "")
        pos = var.split("_")[0]
        cal = []
        if f(r, "tj_max_C") > 150:
            cal.append("%s %s C" % (r.get("tj_max_disp"), r.get("tj_max_C")))
        for k, lim in P_MAX.items():
            if f(r, k) > lim:
                cal.append("%s %.2f W" % (k[2:6].upper(), f(r, k)))
        jack = {"B": ("main",), "F2": ("fix2",), "F1": ("fix1",), "A": ("main", "fix1", "fix2"),
                "ctrl": ("main", "fix1", "fix2")}.get(pos, ("main", "fix1", "fix2"))
        peggiore = max(jack, key=lambda j: f(r, j + "_A_V"))
        out.append({
            "posizione": var, "modo": r["modo"], "classe": classe(r),
            "out_V": r.get("out_avg", ""), "i_rail_piu_A": "%.3f" % -f(r, "ipp_avg"),
            "i_rail_meno_A": "%.3f" % f(r, "imm_avg"),
            "main_A_V": r.get("main_A_V"), "main_grezzo_V": r.get("main_grezzo_V"),
            "main_dB_SPL": r.get("main_dB_SPL"),
            "fix1_A_V": r.get("fix1_A_V"), "fix2_A_V": r.get("fix2_A_V"),
            "stax_dB_SPL": r.get("stax_dB_SPL"),
            "jack_peggiore": peggiore, "verdetto": verdetto(f(r, peggiore + "_A_V")),
            "calore": "; ".join(cal), "stato": r.get("stato"),
        })
    with open(argv[1], "w", newline="") as fo:
        w = csv.DictWriter(fo, fieldnames=list(out[0]))
        w.writeheader()
        for r in out:
            w.writerow(r)
    from collections import Counter
    c = Counter((r["posizione"], r["verdetto"]) for r in out)
    for k in sorted(c):
        print("%-8s %-18s %d" % (k[0], k[1], c[k]))
    print("stato non ok: %d" % sum(1 for r in out if r["stato"] != "ok"))


if __name__ == "__main__":
    main(sys.argv)
