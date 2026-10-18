#!/usr/bin/env python3
"""L60d1, NC-070: B1 e B2g sul jack principale di una corsa «sempre in mute», in due modi.

  v2      il metodo di scripts/v2_metodo.py com'e': diradamento a dtmin = tmax/5 = 2 us,
          ricampionamento cubico a 96 kHz, filtro 20 Hz - 20 kHz (B1), o grezzo (B2g)
  media   ogni campione a 96 kHz e' la MEDIA del segnale vero (lineare a tratti fra i punti di
          ngspice, senza diradamento) sull'intervallo di 10,4 us centrato su di lui: cio' che
          vedrebbe un convertitore col suo filtro anti-aliasing. Poi lo stesso filtro e lo
          stesso picco

Il jack in mute porta un treno di impulsi di ~134 ns a fase fissa (due per periodo, L60d1): il
primo modo prende un punto qualunque dell'impulso, il secondo la sua area. Solo stdlib (importa
le funzioni di v2_metodo.py, che non esegue niente all'import).

Uso: b1_confronto.py <file .dat> [t_da=0.5] [colonna=0]
"""
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
R = os.path.abspath(os.path.join(QUI, "..", "..", "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(R, "scripts"))
import v2_metodo as V  # noqa: E402

path = sys.argv[1]
t_da = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
col = int(sys.argv[3]) if len(sys.argv) > 3 else 0

# --- il metodo di V2
cols, t_fine = V.leggi_wrdata(path, 1e-5 / 5, 1e9)
x = cols[col]
b1, i1 = V.b_picco(x, t_da, t_fine)
b2g, i2 = V.picco(x, int(round(t_da * V.FS)), len(x))

# --- la media su ogni intervallo
T, Y = [], []
for riga in open(path):
    p = riga.split()
    if not p:
        continue
    try:
        t, y = float(p[0]), float(p[1 + 2 * col])
    except ValueError:
        continue
    if T and t <= T[-1]:
        Y[-1] = y
        continue
    T.append(t)
    Y.append(y)
# integrale cumulativo (trapezi) e media su [tk - h/2, tk + h/2]
C = [0.0]
for i in range(1, len(T)):
    C.append(C[-1] + 0.5 * (Y[i] + Y[i - 1]) * (T[i] - T[i - 1]))


def integrale(tt, j):
    while j < len(T) - 2 and T[j + 1] <= tt:
        j += 1
    u = tt - T[j]
    h = T[j + 1] - T[j]
    yy = Y[j] + (Y[j + 1] - Y[j]) * u / h if h > 0 else Y[j]
    return C[j] + 0.5 * (Y[j] + yy) * u, j


h = 1.0 / V.FS
n = int(T[-1] * V.FS) + 1
m = [0.0] * n
j = 0
a, j = integrale(0.0, 0)
for k in range(n):
    b, j = integrale(min((k + 0.5) * h, T[-1]), j)
    m[k] = (b - a) / h
    a = b
b1m, _ = V.b_picco(m, t_da, T[-1])
b2gm, _ = V.picco(m, int(round(t_da * V.FS)), len(m))
print("%s  colonna %d, da %.2f s a %.3f s" % (os.path.basename(os.path.dirname(path)), col, t_da,
                                             T[-1]))
print("  v2    B1 filtrato %8.3f uV   B2g grezzo %8.3f uV" % (b1 * 1e6, b2g * 1e6))
print("  media B1 filtrato %8.3f uV   B2g grezzo %8.3f uV" % (b1m * 1e6, b2gm * 1e6))
