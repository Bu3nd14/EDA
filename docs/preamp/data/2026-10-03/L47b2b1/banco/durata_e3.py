"""durata_e3.py - per un'accoppiata di asimmetrico.json: |Zin| al connettore a 20 Hz e a 20 kHz
lungo la sequenza, il minimo di ciascuna e per quanto tempo quella a 20 kHz sta sotto 100 kohm.

Y_RESTO a 20 Hz: la parte resistiva uguale (G 1,456 uS) e la capacitiva scalata con la frequenza
(rapido.Y_RESTO e' a 20 kHz). La cella con i suoi 5 pF e R_IN come in rapido.zin_e3.

    /usr/bin/python3 durata_e3.py <asimmetrico.json> <criterio> [td_s]
"""
import json
import math
import sys

import famiglia as F
import rapido as R

if len(sys.argv) > 3:
    F.TD = float(sys.argv[3])
acc = json.load(open(sys.argv[1]))[sys.argv[2]]


def zin(rs, rp, f):
    w = 2 * math.pi * f
    y_resto = complex(R.Y_RESTO.real, R.Y_RESTO.imag * f / R.F_E3)
    zs = 1 / (1 / rs + 1j * w * R.CCELL)
    zp = 1 / (1 / rp + 1j * w * R.CCELL + 1 / R.RIN)
    return 1 / abs(y_resto + 1 / (zs + zp))


pi, pr = acc["inserimento"], acc["rilascio"]
si, di = F.funzioni(*F.tabelle(pi["a"], pi["b"], pi["i0"], pi["g"]))
sr, dr = F.funzioni(*F.tabelle(pr["a"], pr["b"], pr["i0"], pr["g"]))
t_ins, td = R.T_INS, F.TD
t_rel = t_ins + td + 1.0


def d(t):
    if t < t_rel:
        return min(max((t - t_ins) / td, 0.0), 1.0)
    return min(max(1 - (t - t_rel) / td, 0.0), 1.0)


for c in "ABCDE":
    tt, ll, xs, xp = R.corsa(lambda t: si(d(t)) if t < t_rel else sr(d(t)),
                             lambda t: di(d(t)) if t < t_rel else dr(d(t)), t_rel + td + 0.5, (c, c))
    z20 = [zin(10 ** a, 10 ** b, 20.0) for a, b in zip(xs, xp)]
    z20k = [zin(10 ** a, 10 ** b, 20e3) for a, b in zip(xs, xp)]
    sotto_i = sum(1 for t, z in zip(tt, z20k) if z < 100e3 and t < t_rel) * 1e-3
    sotto_r = sum(1 for t, z in zip(tt, z20k) if z < 100e3 and t >= t_rel) * 1e-3
    print("%s  20 Hz min %.1f k   20 kHz min %.1f k   sotto 100 k a 20 kHz: %.2f s all'inserimento, "
          "%.2f s al rilascio" % (c, min(z20) / 1e3, min(z20k) / 1e3, sotto_i, sotto_r))
