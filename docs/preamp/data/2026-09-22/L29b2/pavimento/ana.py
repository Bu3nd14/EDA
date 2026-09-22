#!/usr/bin/env python3
"""L29b2, diagnostica del pavimento: C2(t) di una coppia di corse di diag.py, su piu' nodi,
e la griglia dei passi. Pipeline di scripts/v2_metodo.py (leggi_wrdata, residuo_c, filtra).

Uso:  /usr/bin/python3 ana.py A.dat B.dat [BLOCCO=0.5] [T0=0.5]
Colonne di diag.py: 0 mainjack, 1 fixjack1, 2 ina, 3 outa, 4 src, 5 xls.xs, 6 xlp.xs, 7 dep.
Per ina e outa (guadagno 1) la cifra e' riportata anche x 3,15 (il blocco B a +10 dB), per
confrontarla con la principale. Non e' C2 di V2 su un nodo interno: e' un localizzatore.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."] * 6, "scripts")))
import v2_metodo as v  # noqa: E402

A, B = sys.argv[1], sys.argv[2]
BL = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5
T0 = float(sys.argv[4]) if len(sys.argv) > 4 else 0.5
NOMI = ("main", "fix1", "ina", "outa", "src")


def tempi(path):
    t = []
    with open(path) as f:
        for line in f:
            p = line.split()
            if not p:
                continue
            try:
                t.append(float(p[0]))
            except ValueError:
                pass
    return t


def c2(xa, xb, col):
    ra, i0, i1, _ = v.residuo_c(xa[col], 1000.0)
    rb, j0, j1, _ = v.residuo_c(xb[col], 1000.0)
    n = min(len(ra), len(rb))
    i0 = max(i0, j0)
    return v.filtra([ra[k] - rb[k] for k in range(n)], i0), i0, min(i1, j1, n)


xa, _ = v.leggi_wrdata(A, 2e-6, 1e9)
xb, _ = v.leggi_wrdata(B, 2e-6, 1e9)
ys = {}
for col, nome in enumerate(NOMI):
    ys[nome] = c2(xa, xb, col)
ta, tb = tempi(A), tempi(B)


def passo(t, a, b):
    d = [t[k + 1] - t[k] for k in range(len(t) - 1) if a <= t[k] < b and t[k + 1] > t[k]]
    if not d:
        return "-"
    d.sort()
    return "%5.2f/%5.2f/%5.2f" % (d[0] * 1e6, d[len(d) // 2] * 1e6, d[-1] * 1e6)


print("C2 max per finestra [mV]; ina/outa anche x3,15; passo min/med/max [us] di A e B")
print("%-11s %8s %8s %8s %8s %8s %8s   %-17s %-17s" % ("finestra", "main", "fix1", "ina*3.15",
      "outa*3.15", "src", "dep", "passo A", "passo B"))
t = T0
tend = min(ys["main"][2], ys["src"][2]) / v.FS
while t + BL <= tend:
    a, z = int(t * v.FS), int((t + BL) * v.FS)
    riga = []
    for nome in NOMI:
        y = ys[nome][0]
        m = max(abs(y[k]) for k in range(a, z))
        riga.append(m * 1e3 * (3.15 if nome in ("ina", "outa") else 1.0))
    dep = xa[7][a]
    print("%5.2f-%5.2f %8.3f %8.3f %8.3f %8.3f %8.4f %8.3f   %-17s %-17s" % (
        t, t + BL, riga[0], riga[1], riga[2], riga[3], riga[4], dep,
        passo(ta, t, t + BL), passo(tb, t, t + BL)))
    t += BL
