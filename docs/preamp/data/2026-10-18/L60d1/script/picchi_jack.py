#!/usr/bin/env python3
"""L60d1, NC-070: i picchi del jack principale in una corsa «sempre in mute». Nella finestra
[t0, t1]: quanti campioni superano SOGLIA, quanti «eventi» (gruppi separati da > 10 us), la loro
durata sopra soglia, la fase dentro il periodo di 1 kHz, e attorno al picco massimo la forma del
jack e di mainc / main_a (dal file _stati, che ngspice scrive negli stessi istanti). Solo stdlib.

Uso: picchi_jack.py <cartella> [soglia_V=1e-4] [t0=1.5] [t1=2.0]
"""
import os
import sys

d = sys.argv[1]
soglia = float(sys.argv[2]) if len(sys.argv) > 2 else 1e-4
t0 = float(sys.argv[3]) if len(sys.argv) > 3 else 1.5
t1 = float(sys.argv[4]) if len(sys.argv) > 4 else 2.0
fn = [n for n in os.listdir(d) if n.endswith(".dat") and "_stati" not in n][0]

T, J = [], []
for riga in open(os.path.join(d, fn)):
    x = riga.split()
    if not x:
        continue
    t = float(x[0])
    if t < t0:
        continue
    if t > t1:
        break
    T.append(t)
    J.append(float(x[1]))

eventi = []
for i, (t, v) in enumerate(zip(T, J)):
    if abs(v) < soglia:
        continue
    if eventi and t - eventi[-1]["fine"] < 10e-6:
        e = eventi[-1]
        e["fine"] = t
        if abs(v) > abs(e["v"]):
            e["v"], e["t"], e["i"] = v, t, i
    else:
        eventi.append({"inizio": t, "fine": t, "v": v, "t": t, "i": i})
print("finestra %.3f-%.3f s: %d eventi sopra %.3g V" % (t0, t1, len(eventi), soglia))
fasi = {}
for e in eventi:
    k = round(((e["t"] * 1000.0) % 1.0) * 360.0 / 10.0) * 10
    fasi[k] = fasi.get(k, 0) + 1
print("fase (gradi a 1 kHz, a 10) -> eventi:", dict(sorted(fasi.items())))
for e in sorted(eventi, key=lambda e: -abs(e["v"]))[:5]:
    print("  t %.7f s  picco %+.4g V  sopra soglia %.3g us" %
          (e["t"], e["v"], (e["fine"] - e["inizio"]) * 1e6))
if not eventi:
    sys.exit()

m = max(eventi, key=lambda e: abs(e["v"]))
lo, hi = m["t"] - 20e-6, m["t"] + 20e-6
S = {}
for riga in open(os.path.join(d, fn.replace(".dat", "_stati.dat"))):
    x = riga.split()
    if not x:
        continue
    t = float(x[0])
    if t < lo:
        continue
    if t > hi:
        break
    S[t] = (float(x[7]), float(x[9]))  # main_a, mainc
print("attorno al picco massimo (t, jack, main_a, mainc):")
for i in range(max(m["i"] - 12, 0), min(m["i"] + 13, len(T))):
    s = S.get(T[i], (float("nan"), float("nan")))
    print("  %.9f  %+.4e  %+.5f  %+.4e" % (T[i], J[i], s[0], s[1]))
