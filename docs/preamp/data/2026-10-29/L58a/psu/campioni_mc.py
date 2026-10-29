#!/usr/bin/env python3
"""L54b3b: the Monte Carlo samples of the timer's tolerances, as --toll files for genera_tb_psu.py.

Every parameter is UNIFORM over its tolerance (the edges as likely as the middle: a uniform
sample reaches the corners more often than a Gaussian, and a datasheet maximum is not a sigma).
Each sample is written twice: as toll_<n>.json (the absolute values the deck uses) and as a row of
campioni.csv with each parameter NORMALISED to u in [-1, 1] (for the regression, regressione.py).

The tolerances (README, "Le tolleranze"), at the temperature T (--temp, 25 by default):
  R    +-1 % and +-100 ppm/C x |T - 25| (thick film, declared)
  C    by its dielectric (--x7r REF,REF: those X7R, the others C0G):
       C0G +-5 % (+-30 ppm/C: under 0.2 % between 0 and 60 C, inside the 5 %);
       X7R from 0.8 x (1 - bias) x 0.93 (ageing) x 0.97 (temperature) to 1.2: +-20 % as the prompt,
       the DC bias at <= 5 V on a 25 V 1206 (1 uF -15 %, 330 nF -10 %, <= 100 nF -5 %, declared from
       the makers' curves), the ageing -7 % (10^5 h at -2.5 %/decade), the temperature -3 % at 0 / 60 C
  VREF LM4040A: 2.5 V +-0.1 % and +-100 ppm/C x |T - 25| (the A grade's maximum)
  VOS  per channel, +-3.5 mV (SBOS589D 7.6 at 2.2 V: the larger of 2.2 / 36 V) + 20 uV/C x |T - 25|
  IB   one for every input, +-15 nA at 25 C, +-20 nA otherwise (SBOS589D 7.6; the sign unknown)
Solo stdlib. /usr/bin/python3 -I campioni_mc.py --n 100 --seme 54 --uscita <dir> [--temp T]
       [--x7r C548,...]
"""
import argparse
import csv
import json
import os
import random

R = ["R504", "R505", "R506", "R507", "R508", "R509", "R512", "R522", "R523", "R534", "R536", "R555",
     "R569", "R570", "R571", "R572", "R574", "R578", "R580", "R581", "R582", "R583", "R585"]
C = {"C518": 100e-9, "C527": 22e-9, "C528": 100e-9, "C529": 100e-9, "C548": 1e-6, "C549": 100e-9,
     "C550": 10e-9, "C551": 100e-9, "C552": 1e-6, "C553": 330e-9}
CANALI = ["U505a", "U505b", "U506a", "U506b", "U508a", "U508b"] + [
    "U51%d%s" % (n, x) for n in (3, 4, 5) for x in "abcd"]


def intervallo_c(ref, x7r, temp):
    if ref not in x7r:
        return 0.95, 1.05
    bias = 0.15 if C[ref] >= 1e-6 else 0.10 if C[ref] >= 330e-9 else 0.05
    t = 0.97 if temp != 25 else 1.0
    return 0.8 * (1 - bias) * 0.93 * t, 1.2


def intervalli(temp, x7r):
    """name -> (low, high, kind): the parameter's range at temp."""
    dt = abs(temp - 25)
    out = {}
    for r in R:
        e = 0.01 + 100e-6 * dt
        out[r] = (1 - e, 1 + e, "fattore")
    for c in C:
        lo, hi = intervallo_c(c, x7r, temp)
        out[c] = (lo, hi, "fattore")
    e = 2.5 * (0.001 + 100e-6 * dt)
    out["vref"] = (2.5 - e, 2.5 + e, "vref")
    e = 3.5e-3 + 20e-6 * dt
    for ch in CANALI:
        out["vos_" + ch] = (-e, e, "vos")
    e = 15e-9 if dt == 0 else 20e-9
    out["ib"] = (-e, e, "ib")
    return out


def toll(valori, nota):
    t = {"nota": nota, "fattori": {}, "vos": {}}
    for k, v in valori.items():
        if k == "vref":
            t["vref"] = v
        elif k == "ib":
            t["ib"] = v
        elif k.startswith("vos_"):
            t["vos"][k[4:]] = v
        else:
            t["fattori"][k] = v
    return t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--seme", type=int, required=True)
    ap.add_argument("--uscita", required=True)
    ap.add_argument("--temp", type=float, default=25.0)
    ap.add_argument("--x7r", default="")
    a = ap.parse_args()
    x7r = set(a.x7r.split(",")) - {""}
    assert x7r <= set(C), x7r
    iv = intervalli(a.temp, x7r)
    nomi = sorted(iv)
    rng = random.Random(a.seme)
    os.makedirs(a.uscita, exist_ok=True)
    with open(os.path.join(a.uscita, "campioni.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["campione"] + nomi)
        for i in range(a.n):
            u = {k: rng.uniform(-1, 1) for k in nomi}
            v = {k: (iv[k][0] + iv[k][1]) / 2 + u[k] * (iv[k][1] - iv[k][0]) / 2 for k in nomi}
            w.writerow(["mc%03d" % i] + ["%.6f" % u[k] for k in nomi])
            nota = "L54b3b MC seme %d campione %d temp %g x7r %s" % (a.seme, i, a.temp, ",".join(sorted(x7r)) or "-")
            json.dump(toll(v, nota), open(os.path.join(a.uscita, "toll_mc%03d.json" % i), "w"),
                      sort_keys=True, indent=0)
    json.dump({k: list(iv[k][:2]) for k in nomi}, open(os.path.join(a.uscita, "intervalli.json"), "w"),
              sort_keys=True, indent=0)
    print("%d campioni, %d parametri in %s" % (a.n, len(nomi), a.uscita))


if __name__ == "__main__":
    main()
