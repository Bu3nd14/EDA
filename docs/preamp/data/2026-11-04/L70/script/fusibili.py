#!/usr/bin/env python3
"""L70, S1: the fuse and R550 / R551 in the shorts on the raw side (seq/guasti_oggi, seq/guasti_s1).

For each run (the fault at TE = 3.0 s during music, to TE + 1 s):
  - position A, the two ends of T1's secondary: i(vt1a_sns), i(vt1b_sns) (--sonda-t2). Each leg
    carries both rails on alternate half-waves;
  - position B, in series with R550 / R551 after the reservoirs: (v(raw_p) - v(raw_pr)) / 4.7 and
    (v(raw_mr) - v(raw_m)) / 4.7;
  - healthy (the 200 ms before TE, music, regime): RMS per leg / per resistor;
  - after the fault: the RMS of the last 200 ms (the regime the fault settles on, with K501 closed
    or open), the I2t from TE, the peak; R550 / R551: peak power, energy from TE to the end and to
    K501's opening;
  - K501: the first instant after TE with v(k501_f) < 0.5 (open), if any.
The fuse's opening is judged against SCHURTER FST 5x20 (vendor/fuse/schurter/FST_5x20, 21.07.2026):
pre-arcing 10 In 20-300 ms, 4 In 150 ms-3 s, 2.75 In 600 ms-10 s, 2.1 In <= 120 s, 1.5 In >= 60 min;
melting I2t at 10 In (typ.) 1.6 A 10.5, 2 A 16, 2.5 A 21.9, 3.15 A 47 A2s.

    /usr/bin/python3 -I script/fusibili.py      -> fusibili.csv
"""
import csv
import glob
import math
import os

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
TE = 3.0
R = 4.7


def leggi(path):
    with open(path) as f:
        nomi = f.readline().split()
        righe = [list(map(float, r.split())) for r in f if r.strip()]
    return {n: [r[k] for r in righe] for k, n in enumerate(nomi)}


def integra(t, y, a, b):
    s = 0.0
    for k in range(1, len(t)):
        t0, t1 = max(t[k - 1], a), min(t[k], b)
        if t1 > t0:
            s += 0.5 * (y[k - 1] + y[k]) * (t1 - t0)
    return s


def rms(t, i, a, b):
    return math.sqrt(integra(t, [x * x for x in i], a, b) / (b - a))


righe = []
for d in sorted(glob.glob(os.path.join(L, "seq", "guasti_*", "f_*"))):
    if not os.path.exists(os.path.join(d, "ok.txt")):
        righe.append(dict(variante=d.split(os.sep)[-2], caso=os.path.basename(d), esito="CORSA RIFIUTATA"))
        continue
    f = glob.glob(os.path.join(d, "*_g1_out.txt"))
    assert len(f) == 1, d
    w = leggi(f[0])
    t = w["time"]
    tf = t[-1]
    ia, ib = w["i(vt1a_sns)"], w["i(vt1b_sns)"]
    i550 = [(p - q) / R for p, q in zip(w["v(raw_p)"], w["v(raw_pr)"])]
    i551 = [(q - m) / R for q, m in zip(w["v(raw_mr)"], w["v(raw_m)"])]
    k = w["v(k501_f)"]
    t_k = next((x for x, y in zip(t, k) if x > TE and y < 0.5), None)
    r = dict(variante=d.split(os.sep)[-2], caso=os.path.basename(d),
             k501_aperto_ms=None if t_k is None else round((t_k - TE) * 1e3, 1))
    for nome, i in (("A_t1a", ia), ("A_t1b", ib), ("B_r550", i550), ("B_r551", i551)):
        r[nome + "_sano_rms_A"] = round(rms(t, i, TE - 0.2, TE), 3)
        r[nome + "_regime_rms_A"] = round(rms(t, i, tf - 0.2, tf), 3)
        r[nome + "_picco_A"] = round(max(abs(x) for x, y in zip(i, t) if y >= TE), 2)
        r[nome + "_i2t_A2s"] = round(integra(t, [x * x for x in i], TE, tf), 2)
        r[nome + "_i2t_100ms_A2s"] = round(integra(t, [x * x for x in i], TE, TE + 0.1), 2)
        # the power-up (K501 closing on empty reservoirs): what the fuse takes at every switch-on,
        # the peak before the fault and the I2t of the first 100 ms from the first 50 mA
        t_on = next(y for x, y in zip(i, t) if abs(x) > 0.05)
        r[nome + "_acc_t_on_s"] = round(t_on, 4)
        r[nome + "_acc_picco_A"] = round(max(abs(x) for x, y in zip(i, t) if y < TE - 0.5), 2)
        r[nome + "_acc_i2t_100ms_A2s"] = round(integra(t, [x * x for x in i], t_on, t_on + 0.1), 3)
    for nome, i in (("r550", i550), ("r551", i551)):
        p = [x * x * R for x in i]
        r[nome + "_ppk_W"] = round(max(x for x, y in zip(p, t) if y >= TE), 1)
        r[nome + "_E_J"] = round(integra(t, p, TE, tf), 2)
        r[nome + "_E_100ms_J"] = round(integra(t, p, TE, TE + 0.1), 2)
        r[nome + "_regime_W"] = round(integra(t, p, tf - 0.2, tf) / 0.2, 2)
    r["esito"] = "ok"
    righe.append(r)
campi = []
for r in righe:
    campi += [c for c in r if c not in campi]
with open(os.path.join(L, "fusibili.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, campi)
    w.writeheader()
    w.writerows(righe)
print("fusibili.csv: %d righe" % len(righe))
