"""b2_rele.py - L47b2b1: B2 a 20 Hz e la profondita' del mute quando chiude il rele' al jack.

Il verdetto V2 (v2/sorgente, v2/curve_*) da' B2 a 20 Hz SOPRA 100 uV su ogni curva, col picco
26 ms dopo la chiusura del rele' (t_ins + Td + RIT): il passa-alto a 20 Hz del metodo (filtrato da
t = 0) porta dentro la finestra di B2 la memoria del residuo di musica che c'era PRIMA del rele'.
B2 dovrebbe quindi scalare col residuo a 20 Hz all'istante del rele'. Qui:
  1. il residuo a 20 Hz all'istante del rele' (rapido.py, |H| a 20 Hz) per le curve A-E col v5;
  2. il rapporto B2 / residuo sui quattro verdetti V2 (A, B, C, D): se e' costante, il meccanismo
     e' quello;
  3. B2 previsto per ritardi del rele' (RIT) da 0,5 a 3 s.

    /usr/bin/python3 b2_rele.py
"""
import math

import rapido as R

PIENO = 3.818 * 3.1623            # il tono al jack principale, +10 dB (picco)
TD, TI = 3.0, R.T_INS
B2_V2 = {"A": 106.9e-6, "B": 202.9e-6, "C": 225.7e-6, "D": 100.5e-6}   # verdetto.csv di v2/


def h20(rs, rp):
    w = 2 * math.pi * 20.0
    zs = 1 / (1 / rs + 1j * w * R.CCELL)
    zp = 1 / (1 / rp + 1j * w * R.CCELL + 1 / R.RIN)
    return abs(zp / (R.RSRC + zs + zp))


fs, fp = R.profilo_v5(7e-3)
ris = {}
for c in "ABCDE":
    t_rel = TI + TD + 4.0                  # rilascio lontano: si guarda solo il mute fermo
    tt, ll, xs, xp = R.corsa(lambda t: fs(min(max((t - TI) / TD, 0), 1)),
                             lambda t: fp(min(max((t - TI) / TD, 0), 1)), t_rel, (c, c))
    ris[c] = {}
    for rit in (0.5, 1.0, 1.5, 2.0, 2.5, 3.0):
        t = TI + TD + rit
        k = min(range(len(tt)), key=lambda j: abs(tt[j] - t))
        ris[c][rit] = PIENO * h20(10 ** xs[k], 10 ** xp[k])
k = [B2_V2[c] / ris[c][0.5] for c in B2_V2]
kk = sum(k) / len(k)
print("rapporto B2 / residuo a 20 Hz all'istante del rele' (RIT 0,5 s): %s  media %.4f" % (
    ", ".join("%s %.4f" % (c, B2_V2[c] / ris[c][0.5]) for c in B2_V2), kk))
print("curva  " + "  ".join("RIT %.1f s" % r for r in ris["A"]))
for c in "ABCDE":
    print("%s  res " % c + "  ".join("%7.2f mV" % (ris[c][r] * 1e3) for r in ris[c]))
    print("   B2~ " + "  ".join("%7.1f uV" % (kk * ris[c][r] * 1e6) for r in ris[c]))
