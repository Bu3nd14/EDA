#!/usr/bin/env python3
"""L29b2: il «salto» dell'inviluppo in dB: la variazione massima di livello (dB) in una
finestra di 100 ms, contata solo dove il livello sta sopra -70 dB (sotto e' inudibile e la
scala in dB esplode). Per le corse ngspice (ev_stati.dat, inv_stati.dat) e per un profilo
di cerca.py (json).

Uso:  venv/python3 salto.py ngspice DIR     |     venv/python3 salto.py json FILE.json
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

W = 0.100
SOGLIA = -70.0


def da_stati(path):
    t, a, b = [], [], []
    for line in open(path):
        p = line.split()
        if len(p) < 8:
            continue
        try:
            tt = float(p[0])
        except ValueError:
            continue
        if t and tt <= t[-1]:
            continue
        t.append(tt)
        a.append(float(p[1]))
        b.append(float(p[3]))
    tt = np.arange(0, t[-1], 1e-3)
    xa, xb = np.interp(tt, t, a), np.interp(tt, t, b)
    rs, rp = 10 ** xa, 10 ** xb
    par = rp * 1e6 / (rp + 1e6)
    return tt, par / (rs + 1.5 + par)


def salto(tt, g, t0, t1):
    dt = tt[1] - tt[0]
    db = 20 * np.log10(np.maximum(g, 1e-12))
    m = (tt >= t0) & (tt <= t1)
    idx = np.where(m)[0]
    k = int(round(W / dt))
    best = (0.0, 0.0, 0.0, 0.0)
    for i in idx[:-k]:
        a, b = db[i], db[i + k]
        if max(a, b) < SOGLIA:
            continue
        lo, hi = max(min(a, b), SOGLIA), max(a, b)
        if hi - lo > best[0]:
            best = (hi - lo, tt[i], a, b)
    return best


if __name__ == "__main__":
    if sys.argv[1] == "ngspice":
        d = sys.argv[2]
        for nome, t0, t1 in (("ev_stati.dat", 1.0, 8.4), ("ev_stati.dat", 8.5, 17.4),
                             ("inv_stati.dat", 1.0, 13.0)):
            tt, g = da_stati(os.path.join(d, nome))
            s, t, a, b = salto(tt, g, t0, t1)
            print("%-14s %5.1f-%5.1f s: salto max %5.1f dB in 100 ms a %.2f s (%.1f -> %.1f dB)" % (
                nome, t0, t1, s, t, a, b))
    else:
        import cerca
        p = json.load(open(sys.argv[2]))["profilo"]
        T = p["td"] + p["acc"]
        t_rele = 0.5 + T + 0.5
        d, g, _ = cerca.corsa(p, t_rele + 1.0, t_rele + 1.0 + T + 1.5)
        tt = np.arange(len(g)) * cerca.DT
        for nome, t0, t1 in (("inserzione", 0.4, t_rele), ("rilascio", t_rele + 1.0, tt[-1])):
            s, t, a, b = salto(tt, g, t0, t1)
            print("%-10s: salto max %5.1f dB in 100 ms a %.2f s (%.1f -> %.1f dB)" % (nome, s, t, a, b))
        dd, _, _ = cerca.corsa(p, 1e9, 0.5 + T + 0.5)
        ti = int(np.argmax(dd >= 0.75)) * cerca.DT
        d, g, _ = cerca.corsa(p, ti, ti + T + 1.5)
        s, t, a, b = salto(np.arange(len(g)) * cerca.DT, g, 0.4, ti + T + 1.5)
        print("inversione 0,75: salto max %5.1f dB in 100 ms a %.2f s (%.1f -> %.1f dB)" % (s, t, a, b))
