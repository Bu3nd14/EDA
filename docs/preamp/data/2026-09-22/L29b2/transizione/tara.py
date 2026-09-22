#!/usr/bin/env python3
"""L29b2: taratura del simulatore veloce (sur.py) contro le corse ngspice del profilo v3/v4.

Uso:  /usr/bin/python3 tara.py DIR_NGSPICE PROFILO     (DIR con ev_stati.dat e inv_stati.dat)

1. le traiettorie log10(R) delle due celle: Python contro ngspice, stesso profilo, stesso d(t);
2. C2 d'inserzione, rilascio e inversione: dal g(t) di ngspice e dal g(t) di Python.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sur  # noqa: E402

D, PROF = sys.argv[1], sys.argv[2]
FS = sur.FS
DT = 1.0 / FS
TI, TD = 1.0, 6.0
TR = TI + TD + 0.5 + 1.0
TINV = TI + 0.75 * TD
lg = math.log10
PROFILI = {
    "v3": [(0, 20e-3), (0.1, 0.2e-3), (0.45, 4.5e-6), (0.5, 10e-9), (1, 10e-9)],
    "v4": [(0, 20e-3), (0.1, 0.2e-3), (0.45, 4.5e-6), (0.75, 0.19e-6), (0.8, 10e-9), (1, 10e-9)],
}
SER = [(d, lg(i)) for d, i in PROFILI[PROF]]


def i_ser(d):
    return 10 ** sur.pwl(d, SER)


def i_par(d):
    return 10e-9 * 2e6 ** min(max((d - 0.5) / 0.5, 0), 1)


def leggi_stati(path, n):
    """ev_stati.dat: t xs_s t xs_p t dep t ina -> xs_s, xs_p ricampionati a FS."""
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
    xa, xb = [0.0] * n, [0.0] * n
    j = 0
    for k in range(n):
        tk = k * DT
        while j < len(t) - 2 and t[j + 1] <= tk:
            j += 1
        u = (tk - t[j]) / (t[j + 1] - t[j])
        u = min(max(u, 0.0), 1.0)
        xa[k] = a[j] + u * (a[j + 1] - a[j])
        xb[k] = b[j] + u * (b[j + 1] - b[j])
    return xa, xb


def corsa(t_rel, tf, nome):
    n = int(tf * FS)
    d = sur.profondita(n, DT, TI, t_rel, TD)
    xs_s = sur.evolvi(lambda k: i_ser(d[k]), n, DT, sur.xt_di(sur.i_led(i_ser(0), 1e7)), 1e7)
    xs_p = sur.evolvi(lambda k: i_par(d[k]), n, DT, sur.xt_di(sur.i_led(i_par(0), 1e7)), 1e7)
    ns_s, ns_p = leggi_stati(os.path.join(D, nome), n)
    es = max(abs(x - y) for x, y in zip(xs_s, ns_s))
    ep = max(abs(x - y) for x, y in zip(xs_p, ns_p))
    ks = max(range(n), key=lambda k: abs(xs_s[k] - ns_s[k]))
    kp = max(range(n), key=lambda k: abs(xs_p[k] - ns_p[k]))
    print("%s: |dlog10 R| max serie %.4f (a %.3f s), derivazione %.4f (a %.3f s)" % (
        nome, es, ks * DT, ep, kp * DT), flush=True)
    return sur.livello(xs_s, xs_p), sur.livello(ns_s, ns_p)


g_mai = sur.livello([sur.xt_di(sur.i_led(i_ser(0), 1e7))], [sur.xt_di(sur.i_led(i_par(0), 1e7))])[0]
gp, gn = corsa(TR, TR + TD + 3.0, "ev_stati.dat")
for nome, g in (("python", gp), ("ngspice", gn)):
    ci = sur.c2(g, TI, TD + 0.5, rif=0.0)[0]
    cr = sur.c2(g, TR, TD + 0.5, rif=g_mai)[0]
    print("C2 %-8s inserzione %.3f mV   rilascio %.3f mV" % (nome, ci * 1e3, cr * 1e3), flush=True)
gp, gn = corsa(TINV, TINV + 0.75 * TD + 3.0, "inv_stati.dat")
for nome, g in (("python", gp), ("ngspice", gn)):
    cv = sur.c2(g, TINV, 0.75 * TD, rif=g_mai)[0]
    print("C2 %-8s inversione %.3f mV" % (nome, cv * 1e3), flush=True)
