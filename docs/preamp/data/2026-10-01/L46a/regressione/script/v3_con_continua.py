#!/usr/bin/env python3
"""L46a: V3 come v3.py di L39/L40, ma col guadagno lineare stimato INSIEME alla
continua (minimi quadrati di v(OUT) su [v(SRCN), 1] fra 12 e 20 ms).

Perche': v3.py misura il recupero come |v(OUT) - G v(SRCN)| < 5 % dell'inviluppo
(G x 0,5 V = 78,7 mV a +10 dB) senza togliere la continua. Il nodo OUT a +10 dB e'
accoppiato in continua con guadagno 3,15, e la continua d'uscita del blocco e'
passata da -15,45 a -26,1 mV con ADR-054: x3,15 fa ~-82 mV, sopra la soglia per
tutta la corsa. v3.py stampa allora «recupero 14000 us», che non e' un recupero
mancato ma la continua (prima stava a ~-49 mV, sotto la soglia). Qui la si toglie,
e il recupero torna a dire quello che vuole dire. Entrambe le cifre vanno nel report.

Uso: env/venv/bin/python3 v3_con_continua.py
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
    a = np.vstack([src[lin], np.ones(lin.sum())]).T
    (g, c), *_ = np.linalg.lstsq(a, out[lin], rcond=None)
    err = np.abs(out - (g * src + c))
    lim = 0.05 * g * 0.5
    dopo6 = t > 6e-3
    fuori = np.where(dopo6 & (err >= lim))[0]
    rec = (t[fuori[-1]] - 6e-3) if len(fuori) else 0.0
    m = (t >= 19e-3) & (t <= 20e-3)
    print("%-5s clip %+.3f / %+.3f V  G %.4f  continua a OUT %+.1f mV  recupero %.2f us  "
          "residuo 12-20 ms %.2f mV  DC jack %+.2f mV" % (
              fase, out[ov].max(), out[ov].min(), g, c * 1e3, rec * 1e6,
              err[lin].max() * 1e3, jack[m].mean() * 1e3))
