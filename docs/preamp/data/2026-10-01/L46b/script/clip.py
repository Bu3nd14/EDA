#!/usr/bin/env python3
"""L46b: il clip e il recupero per variante (la cella costa la caduta sulla sua R).

  dc     tb_dc_headroom, +10 dB: massimo e minimo di v(OUT) nello sweep in continua
  v3     tb_v3_overload: clip nel sovraccarico (1-6 ms) e recupero con la continua
         tolta, metodo di L46a/regressione/script/v3_con_continua.py (guadagno e
         continua stimati insieme fra 12 e 20 ms, soglia 5 % dell'inviluppo)

Uso: env/venv/bin/python3 clip.py <variante>...   -> clip.csv
"""
import csv
import os
import sys
import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
LOTTO = os.path.dirname(QUI)

righe = []
for v in sys.argv[1:]:
    run = os.path.join(LOTTO, "run", v)
    dc = np.loadtxt(os.path.join(run, "tb_dc_headroom", "tb_dc_headroom_10db.csv"),
                    delimiter=",", skiprows=1)
    d = np.loadtxt(os.path.join(run, "tb_v3_overload", "tb_v3_overload.csv"),
                   delimiter=",", skiprows=1)
    t, src, out = d[:, 0], d[:, 1], d[:, 3]
    ov = (t >= 1e-3) & (t <= 6e-3)
    lin = (t >= 12e-3) & (t <= 20e-3)
    a = np.vstack([src[lin], np.ones(lin.sum())]).T
    (g, c), *_ = np.linalg.lstsq(a, out[lin], rcond=None)
    err = np.abs(out - (g * src + c))
    fuori = np.where((t > 6e-3) & (err >= 0.05 * g * 0.5))[0]
    rec = (t[fuori[-1]] - 6e-3) if len(fuori) else 0.0
    r = {"variante": v,
         "dc_max_V": "%.3f" % dc[:, 1].max(), "dc_min_V": "%.3f" % dc[:, 1].min(),
         "v3_max_V": "%.3f" % out[ov].max(), "v3_min_V": "%.3f" % out[ov].min(),
         "recupero_us": "%.2f" % (rec * 1e6)}
    righe.append(r)
    print("  ".join("%s=%s" % kv for kv in r.items()))
with open(os.path.join(LOTTO, "clip.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, list(righe[0]))
    w.writeheader()
    w.writerows(righe)
