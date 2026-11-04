#!/usr/bin/env python3
"""L70: the fuses of T1's secondary and the resistors before the regulators, from the waveforms.

    /usr/bin/python3 -I script/fusibili.py <out.csv> <seq_dir>/<caso> [...]

Per run (the _g1_out.txt of corri_an.sh), TE = 3.0 s:
  - per fuse leg (i(vff502s), i(vff503s)): peak |i|, the I2t from 0 to TE (the power-up / the inrush,
    for the runs that start from standby or cold) and over the whole run, the RMS over the last
    0.2 s (ten mains cycles: the regime the run ends in), and the instant the model melted
    (v(ff50x_m) > 0.5), if it did;
  - R550 / R551: P = (V(raw_p) - V(raw_pr))^2 / 4.7 and (V(raw_mr) - V(raw_m))^2 / 4.7: the peak, the
    energy from TE to the end, the mean power over the last 0.2 s (what it keeps receiving if
    nothing opens: the toroid stays on with S1).
A run without the fuse columns (today's circuit) gives only R550 / R551.
Solo stdlib.
"""
import csv
import math
import os
import sys

TE = 3.0
R55 = 4.7


def leggi(path):
    with open(path) as f:
        nomi = f.readline().split()
        dati = [list(map(float, r.split())) for r in f if r.strip()]
    return {n: [r[k] for r in dati] for k, n in enumerate(nomi)}


def integra(t, y, da, a):
    s = 0.0
    for k in range(1, len(t)):
        if t[k] <= da or t[k - 1] >= a:
            continue
        s += 0.5 * (y[k] + y[k - 1]) * (t[k] - t[k - 1])
    return s


def caso(d):
    fs = [f for f in os.listdir(d) if f.endswith("_g1_out.txt")]
    if len(fs) != 1 or not os.path.exists(os.path.join(d, "ok.txt")):
        return None
    w = leggi(os.path.join(d, fs[0]))
    t = w["time"]
    tf = t[-1]
    r = {"caso": "/".join(d.rstrip("/").split("/")[-2:]), "tf_s": "%.3f" % tf}
    for f in ("f502", "f503", "f504", "f505"):
        k = "i(vf%ss)" % f
        if k not in w:
            continue
        i = w[k]
        i2 = [x * x for x in i]
        r[f + "_pk_A"] = "%.2f" % max(abs(x) for x in i)
        r[f + "_i2t_avvio"] = "%.2f" % integra(t, i2, 0.0, TE)
        r[f + "_i2t_tutto"] = "%.2f" % integra(t, i2, 0.0, tf)
        r[f + "_rms_fine_A"] = "%.3f" % math.sqrt(integra(t, i2, tf - 0.2, tf) / 0.2)
        m = w.get("v(%s_m)" % f.replace("f", "ff"))
        fuso = next((t[j] for j, x in enumerate(m) if x > 0.5), None) if m else None
        r[f + "_fuso_ms"] = "" if fuso is None else "%.1f" % ((fuso - TE) * 1e3)
    # s1s2dc: R550 sits between RAW_PF and RAW_PR, R551 between RAW_MR and RAW_MF
    rp = "v(raw_pf)" if "v(raw_pf)" in w else "v(raw_p)"
    rm = "v(raw_mf)" if "v(raw_mf)" in w else "v(raw_m)"
    for nome, a, b in (("r550", rp, "v(raw_pr)"), ("r551", "v(raw_mr)", rm)):
        if a not in w or b not in w:
            continue
        p = [(x - y) ** 2 / R55 for x, y in zip(w[a], w[b])]
        r[nome + "_pk_W"] = "%.1f" % max(p[j] for j in range(len(t)) if t[j] >= TE) if tf > TE else ""
        r[nome + "_E_J"] = "%.2f" % integra(t, p, TE, tf)
        r[nome + "_P_fine_W"] = "%.2f" % (integra(t, p, tf - 0.2, tf) / 0.2)
    return r


out = []
for d in sys.argv[2:]:
    x = caso(d)
    if x:
        out.append(x)
campi = []
for x in out:
    for k in x:
        if k not in campi:
            campi.append(k)
with open(sys.argv[1], "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=campi)
    w.writeheader()
    w.writerows(out)
print("%s: %d corse" % (sys.argv[1], len(out)))
