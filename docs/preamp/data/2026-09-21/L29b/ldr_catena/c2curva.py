"""c2curva.py - C2(t) a intervalli di 0,1 s, con la pipeline di scripts/v2_metodo.py
(leggi_wrdata, residuo_c, differenza, filtra). Diagnostica di L29b, non un verdetto.

Uso:  /usr/bin/python3 c2curva.py DIR EV.dat RIF.dat T0 T1 COLONNA   (0 principale, 1 e 2 fisse)

Serve a vedere DOVE sta il picco che `analizza` riporta. In L29b ha mostrato che dopo il
rilascio C2 resta a ~6,5 mV sulla principale a livello pieno, e che e' NUMERICO: contro la
stessa corsa senza rele' (stato fisico identico) e contro la stessa corsa con TMAX 7 us.
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."] * 6, "scripts")))
import v2_metodo as v
d, ev, rif, t0, t1, col = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]), float(sys.argv[5]), int(sys.argv[6])
xe, te = v.leggi_wrdata(d + "/" + ev, 2e-6, 1e9)
xr, tr = v.leggi_wrdata(d + "/" + rif, 2e-6, 1e9)
re_, i0, i1, _ = v.residuo_c(xe[col], 1000.0)
rr, j0, j1, _ = v.residuo_c(xr[col], 1000.0)
n = min(len(re_), len(rr))
i0, i1 = max(i0, j0), min(i1, j1, n)
diff = [re_[k] - rr[k] for k in range(n)]
y = v.filtra(diff, i0)
b = 0.1
t = t0
while t < t1:
    a, z = int(t * v.FS), int((t + b) * v.FS)
    m = max(range(a, z), key=lambda k: abs(y[k]))
    print("%6.2f-%6.2f  C2 max %.3g V a %.4f" % (t, t + b, abs(y[m]), m / v.FS))
    t += b
