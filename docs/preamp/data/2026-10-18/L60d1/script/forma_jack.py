#!/usr/bin/env python3
"""L60d1, NC-070: com'e' fatto il segnale sul jack principale in una corsa «sempre in mute»:
media (continua), RMS senza la media, ampiezza a 1 kHz (proiezione su seno e coseno), su una
finestra [t0, t1]. Lo stesso per i nodi del file _stati (main_a, mainc). Solo stdlib.

Uso: forma_jack.py <cartella della corsa> [t0=1.5] [t1=2.0] [f=1000]
"""
import math
import os
import sys

d = sys.argv[1]
t0 = float(sys.argv[2]) if len(sys.argv) > 2 else 1.5
t1 = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0
f = float(sys.argv[4]) if len(sys.argv) > 4 else 1000.0


def leggi(path, nomi):
    t, cols = [], [[] for _ in nomi]
    for riga in open(path):
        x = riga.split()
        if not x:
            continue
        tt = float(x[0])
        if tt < t0:
            continue
        if tt > t1:
            break
        t.append(tt)
        for j in range(len(nomi)):
            cols[j].append(float(x[2 * j + 1]))
    return t, dict(zip(nomi, cols))


def descrivi(t, y):
    # integrazione a trapezi: il passo di ngspice non e' uniforme
    T = t[-1] - t[0]
    m = s = c = q = 0.0
    for i in range(1, len(t)):
        dt = t[i] - t[i - 1]
        ym = 0.5 * (y[i] + y[i - 1])
        tm = 0.5 * (t[i] + t[i - 1])
        m += ym * dt
        s += ym * math.sin(2 * math.pi * f * tm) * dt
        c += ym * math.cos(2 * math.pi * f * tm) * dt
        q += ym * ym * dt
    m /= T
    a = 2 * math.hypot(s, c) / T
    rms = math.sqrt(max(q / T - m * m, 0.0))
    return m, rms, a


fn = [n for n in os.listdir(d) if n.endswith(".dat") and "_stati" not in n][0]
t, v = leggi(os.path.join(d, fn), ["mainjack", "fixjack1", "fixjack2"])
print("finestra %.3f-%.3f s, %d punti, f = %g Hz" % (t0, t1, len(t), f))
for k in v:
    m, r, a = descrivi(t, v[k])
    print("%-9s media %+.4g V  rms(ac) %.4g V  picco a f %.4g V" % (k, m, r, a))
ts, vs = leggi(os.path.join(d, fn.replace(".dat", "_stati.dat")),
               ["ina", "vplus", "vminus", "main_a", "mainc", "fixc1", "fixc2"])
for k in ("ina", "main_a", "mainc", "vplus", "vminus"):
    m, r, a = descrivi(ts, vs[k])
    print("%-9s media %+.4g V  rms(ac) %.4g V  picco a f %.4g V" % (k, m, r, a))
