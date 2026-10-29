#!/usr/bin/env python3
"""L55, diagnosi: il potenziale di giunzione VJ dei modelli alla temperatura, con le formule di SPICE3
(ngspice, bjttemp.c: pbo, pbfact, fact1/fact2, egfet), TNOM 27 C.

Il modello onsemi del MJE253 ha VJC = 0,0328604 V. ngspice scala VJ con la temperatura:
VJ(T) = (T/Tref) * pbo + pbfact(T); con un VJ cosi' piccolo, sopra TNOM la tensione scende a zero e
sotto, e la capacita' di giunzione CJ / (1 - V/VJ)^MJ non e' piu' definita: la `tran` si ferma al primo
punto. L'op non usa le capacita', e converge. Solo stdlib, /usr/bin/python3 -I.
"""
import math

K = 1.3806226e-23
Q = 1.6021918e-19
REF = 300.15
TNOM = 300.15


def egfet(t):
    return 1.16 - (7.02e-4 * t * t) / (t + 1108)


def pbfact(t):
    vt = K * t / Q
    arg = -egfet(t) / (2 * K * t) + 1.1150877 / (K * (REF + REF))
    return -2 * vt * (1.5 * math.log(t / REF) + Q * arg)


def vj_t(vj, tc):
    t = tc + 273.15
    fact1 = TNOM / REF
    pbo = (vj - pbfact(TNOM)) / fact1
    return (t / REF) * pbo + pbfact(t)


MODELLI = (("MJE15032 VJC", 0.600021), ("MJE15032 VJE", 0.648491), ("MJE243 VJC", 0.4),
           ("MJE243 VJE", 0.99), ("MJE253 VJC", 0.0328604), ("MJE253 VJE", 0.99))
TEMP = (0, 27, 30, 36.5, 45, 60, 66.2, 100, 125)
print("%-14s" % "" + "".join("%9.1f" % t for t in TEMP))
for nome, vj in MODELLI:
    print("%-14s" % nome + "".join("%9.4f" % vj_t(vj, t) for t in TEMP))
