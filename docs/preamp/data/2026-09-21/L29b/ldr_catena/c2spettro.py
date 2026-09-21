"""c2spettro.py - spettro della differenza C2 (DFT a frequenze scelte) su [T0, T1].
Diagnostica di L29b: il residuo stazionario dopo il rilascio non e' un tono (rms 1,6 mV,
picco 6,7 mV, nessuna riga a 1 kHz): e' rumore numerico.

Uso:  /usr/bin/python3 c2spettro.py DIR EV.dat RIF.dat T0 T1
"""
import os, sys, math, cmath
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."] * 6, "scripts")))
import v2_metodo as v
d, ev, rif, t0, t1 = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]), float(sys.argv[5])
xe, _ = v.leggi_wrdata(d + "/" + ev, 2e-6, 1e9)
xr, _ = v.leggi_wrdata(d + "/" + rif, 2e-6, 1e9)
re_, i0, i1, _ = v.residuo_c(xe[0], 1000.0)
rr, j0, j1, _ = v.residuo_c(xr[0], 1000.0)
n = min(len(re_), len(rr))
diff = [re_[k] - rr[k] for k in range(n)]
y = v.filtra(diff, max(i0, j0))
a, b = int(t0 * v.FS), int(t1 * v.FS)
seg = y[a:b]
N = len(seg)
print("rms %.3g V, picco %.3g V, media %.3g V" % (math.sqrt(sum(s*s for s in seg)/N), max(abs(s) for s in seg), sum(seg)/N))
# DFT a frequenze scelte (risoluzione 1/(t1-t0))
for f in [20, 50, 100, 200, 500, 900, 990, 1000, 1010, 1100, 2000, 3000, 5000, 10000, 15000, 19000, 24000, 47000, 48000]:
    s = sum(seg[k] * cmath.exp(-2j * math.pi * f * k / v.FS) for k in range(0, N))
    print("%6d Hz  %.3g V" % (f, 2 * abs(s) / N))
# anche lo spettro grezzo della differenza delle corse (senza fit): e' il tono?
