#!/usr/bin/env python3
"""post.py - quello che v2_metodo.py analizza non calcola, dalle corse di ldr1k.cir (L29b).

Uso:  /usr/bin/python3 post.py DIR      (DIR = cartella dei .dat di build.py)

1. CARICO SULLA SORGENTE durante la sequenza: R_s + (R_p || 1 M), dalle resistenze delle
   due celle (stato xs = log10 R, file <cella>_stati.dat). Resistivo: 5 pF della cella
   esclusi (a 20 kHz valgono 1,6 M, e contano solo quando la serie e' gia' alta). Il
   minimo si confronta con l'ipotesi di ADR-038 (>= 10 k) e con E3 (>= 100 k).
2. STATO DELLE LDR agli istanti del rele' (chiusura e apertura): serve a impostare la
   corsa a 20 kHz, che non puo' rifare tutta la sequenza col passo da 0,5 us.
3. RIPRESA DEL LIVELLO dopo il rilascio: ampiezza del tono al jack principale nella corsa
   con l'evento contro quella mai in mute, su finestre di 10 ms (10 periodi a 1 kHz),
   in dB. Il guadagno a valle e' lineare: il rapporto e' quello dell'attenuatore
   serie/derivazione all'ingresso del blocco A.
Solo stdlib. Ogni cifra: SIMULATA, modello comportamentale dal datasheet, con
estrapolazione dichiarata.
"""
import math
import os
import sys

D = sys.argv[1]
R_IN = 1e6


def leggi(nome, colonne):
    """wrdata: coppie (t, y) ripetute; restituisce t e le y."""
    t, ys = [], [[] for _ in range(colonne)]
    with open(os.path.join(D, nome)) as f:
        for riga in f:
            v = riga.split()
            if len(v) != 2 * colonne:
                continue
            t.append(float(v[0]))
            for k in range(colonne):
                ys[k].append(float(v[2 * k + 1]))
    return t, ys


def carico(rs, rp):
    return rs + rp * R_IN / (rp + R_IN)


def a_istante(t, y, t0):
    i = min(range(len(t)), key=lambda k: abs(t[k] - t0))
    return y[i]


print("=== 1. carico minimo sulla sorgente, R_s + (R_p || 1 M) ===")
for cella in ("ev", "norele", "inv", "lzev"):
    p = cella + "_stati.dat"
    if not os.path.exists(os.path.join(D, p)):
        continue
    t, (xs, xp, dep, ina) = leggi(p, 4)
    zl = [carico(10 ** a, 10 ** b) for a, b in zip(xs, xp)]
    # si guarda dove la derivazione conduce davvero: prima, il carico e' 1 M + R_s
    i = min(range(len(t)), key=lambda k: zl[k])
    print("%-7s min %.4g ohm a t = %.3f s (d = %.3f, R_s = %.4g, R_p = %.4g); "
          "ipotesi ADR-038 >= 10 k: %s; E3 >= 100 k: %s"
          % (cella, zl[i], t[i], dep[i], 10 ** xs[i], 10 ** xp[i],
             "si'" if zl[i] >= 1e4 else "NO", "si'" if zl[i] >= 1e5 else "NO"))
    for t0 in (1.0, 1.3, 1.6, 2.0, 2.5, 3.0, 3.5, 4.0, 4.05, 5.0, 5.5, 6.0, 7.0, 7.7, 8.0, 9.0, 10.0, 12.0):
        if t0 <= t[-1]:
            print("   t = %5.2f  d = %.3f  R_s = %9.4g  R_p = %9.4g  carico = %9.4g"
                  % (t0, a_istante(t, dep, t0), 10 ** a_istante(t, xs, t0),
                     10 ** a_istante(t, xp, t0), carico(10 ** a_istante(t, xs, t0), 10 ** a_istante(t, xp, t0))))

print("\n=== 3. ripresa del livello al jack principale dopo il rilascio (ev contro mai) ===")
te, (me, _, _) = leggi("ev.dat", 3)
tm, (mm, _, _) = leggi("mai.dat", 3)


def ampiezza(t, y, t0, T=0.010):
    """ampiezza del tono a 1 kHz su [t0, t0+T]: fit seno+coseno sui campioni del .dat."""
    s = c = ss = cc = sc = ys = yc = 0.0
    for tk, yk in zip(t, y):
        if t0 <= tk < t0 + T:
            a, b = math.sin(2 * math.pi * 1000 * tk), math.cos(2 * math.pi * 1000 * tk)
            ss += a * a; cc += b * b; sc += a * b; ys += yk * a; yc += yk * b
    det = ss * cc - sc * sc
    if det == 0:
        return float("nan")
    A = (ys * cc - yc * sc) / det
    B = (yc * ss - ys * sc) / det
    return math.hypot(A, B)


for t0 in (4.5, 5.2, 6.0, 7.0, 7.5, 7.7, 7.8, 7.9, 8.0, 8.1, 8.3, 8.6, 9.0, 9.5, 10.0, 10.5, 11.0, 11.9):
    ae, am = ampiezza(te, me, t0), ampiezza(tm, mm, t0)
    print("t = %5.2f  ev %.5g V  mai %.5g V  ->  %+.3f dB" % (t0, ae, am, 20 * math.log10(ae / am) if ae > 0 else float("-inf")))
