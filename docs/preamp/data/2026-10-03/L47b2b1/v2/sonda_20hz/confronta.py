"""confronta.py - #38: due corse dello stesso deck con e senza un'opzione di convergenza devono
dare le stesse cifre. Confronta l'ampiezza del tono a 20 Hz (fit di v2_metodo, finestra di un
periodo) sulle tre uscite, istante per istante, e la differenza massima in dB e in V.

    /usr/bin/python3 confronta.py <a.dat> <b.dat> <t_fine>
"""
import math
import os
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 7))
sys.path.insert(0, os.path.join(REPO, "scripts"))
import v2_metodo as V2  # noqa: E402

a, b, tf = sys.argv[1], sys.argv[2], float(sys.argv[3])
ca, ta = V2.leggi_wrdata(a, 1e-5, tf)
cb, tb = V2.leggi_wrdata(b, 1e-5, tf)
print("fine letta: %.4f / %.4f s" % (ta, tb))
for k, nome in enumerate(("MAINJACK", "FIXJACK1", "FIXJACK2")):
    ia, aa = V2.ampiezza(ca[k], 20.0, 0.2, tf - 0.1)
    ib, ab = V2.ampiezza(cb[k], 20.0, 0.2, tf - 0.1)
    n = min(len(aa), len(ab))
    dv = max(abs(x - y) for x, y in zip(aa[:n], ab[:n]))
    ddb = max(abs(20 * math.log10(max(x, 1e-30) / max(y, 1e-30))) for x, y in zip(aa[:n], ab[:n])
              if x > 1e-6 and y > 1e-6)
    print("%-9s ampiezza max %.6g V; differenza max %.3g V, %.4f dB" % (nome, max(aa), dv, ddb))
