"""traccia.py - il livello, d e gli stati delle due celle ogni 100 ms, per un profilo e una curva.

    /usr/bin/python3 traccia.py <curva> <cima_A> [v4|v5]
"""
import math
import sys

import rapido as R
import profili as P

curva = sys.argv[1]
ion = float(sys.argv[2])
nome = sys.argv[3] if len(sys.argv) > 3 else "v4"
fs, fp = R.profilo_v4(ion) if nome == "v4" else P.PROFILI[nome](ion)
r = R.sfumatura(fs, fp, 3.0, (curva, curva))
print("S ins %.2f  S rel %.2f  mute %.1f" % (r["S_ins_dB"], r["S_rel_dB"], r["liv_mute_dB"]))
for k, t in enumerate(r["tt"]):
    if abs((t * 1000) % 100) < 0.5 or abs((t * 1000) % 100 - 100) < 0.5:
        d = min(max((t - R.T_INS) / 3.0, 0), 1) if t < 4.3 else min(max(1 - (t - 4.3) / 3.0, 0), 1)
        print("t %.2f d %.3f  L %7.2f dB  serie %.2f  deriv %.2f" % (
            t, d, 20 * math.log10(r["ll"][k] / r["a_pieno"]), r["xs"][k], r["xp"][k]))
