#!/usr/bin/env python3
"""L39: V3 da tb_v3_overload (prima e dopo). Dalla forma d'onda della prima tran
(colonne: t,v(SRCN), t,v(OUT), t,v(JACK), t,v(NX)):
  - clip +/-: massimo e minimo di v(OUT) nel sovraccarico, 1-6 ms;
  - guadagno lineare G: minimi quadrati di v(OUT) su v(SRCN) fra 12 e 20 ms;
  - recupero: il primo istante dopo 6 ms da cui |v(OUT) - G v(SRCN)| resta per
    sempre sotto il 5 % dell'inviluppo lineare (G x 0,5 V);
  - DC al jack: media di v(JACK) sull'ultimo periodo (19-20 ms).
Uso: env/venv/bin/python3 v3.py
"""
import os
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for fase in ("prima", "dopo"):
    d = np.loadtxt(os.path.join(BASE, fase, "tb_v3_overload", "tb_v3_overload.csv"),
                   delimiter=",", skiprows=1)
    t, src, out, jack = d[:, 0], d[:, 1], d[:, 3], d[:, 5]
    ov = (t >= 1e-3) & (t <= 6e-3)
    lin = (t >= 12e-3) & (t <= 20e-3)
    g = float(np.dot(src[lin], out[lin]) / np.dot(src[lin], src[lin]))
    err = np.abs(out - g * src)
    lim = 0.05 * g * 0.5
    dopo6 = np.where(t > 6e-3)[0]
    fuori = dopo6[err[dopo6] >= lim]
    t_rec = (t[fuori[-1]] - 6e-3) if len(fuori) else 0.0
    dc = float(np.mean(jack[t >= 19e-3]))
    print("%-5s clip %+.3f / %+.3f V  G %.4f  recupero %.2f us  DC jack %+.2f mV"
          % (fase, out[ov].max(), out[ov].min(), g, t_rec * 1e6, dc * 1e3))
