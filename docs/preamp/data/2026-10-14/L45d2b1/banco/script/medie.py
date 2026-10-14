#!/usr/bin/env python3
"""L45d2b1: le medie a finestre delle uscite dei blocchi in una corsa del banco (stdlib).

Uso: medie.py RUN.dat [FINESTRA_MS] [DA_S] [A_S]
Il .dat e' quello di genera_canale.py (wrdata con la x ripetuta): mainjack fix1jack fix2jack outa
outf1 outf2 outb ipp imm. Stampa per finestra: t, media di outf1, outf2, outb, e min / max di outb.
"""
import sys


def leggi(path):
    righe = []
    for r in open(path):
        p = r.split()
        if len(p) < 18:
            continue
        try:
            v = [float(x) for x in p]
        except ValueError:
            continue
        righe.append((v[0], v[9], v[11], v[13]))     # t, outf1, outf2, outb
    return righe


def main():
    path = sys.argv[1]
    w = float(sys.argv[2]) / 1e3 if len(sys.argv) > 2 else 0.01
    da = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
    a = float(sys.argv[4]) if len(sys.argv) > 4 else 1e9
    r = [x for x in leggi(path) if da <= x[0] <= a]
    i = 0
    while i < len(r):
        t0 = r[i][0]
        blocco = []
        while i < len(r) and r[i][0] < t0 + w:
            blocco.append(r[i])
            i += 1
        if len(blocco) < 2:
            continue
        # media pesata sul tempo (il passo varia)
        s = [0.0, 0.0, 0.0]
        T = 0.0
        for k in range(1, len(blocco)):
            dt = blocco[k][0] - blocco[k - 1][0]
            T += dt
            for j in range(3):
                s[j] += blocco[k][j + 1] * dt
        ob = [x[3] for x in blocco]
        print("%.4f  f1 %+8.3f  f2 %+8.3f  b %+8.3f   b min %+7.2f max %+7.2f" % (
            t0, s[0] / T, s[1] / T, s[2] / T, min(ob), max(ob)))


if __name__ == "__main__":
    main()
