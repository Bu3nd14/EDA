#!/usr/bin/env python3
"""L69b: why t_arm_ms moves by -0.6 / -0.7 ms against L64b (and L58b). AT_T2S charges from AT_ON through
R580 2.7M / C552 1u (psu.py, ADR-102); AT_ON high is V5 minus the drop on its pull-up, 10k before ADR-116
and 9.98k (R576 + R589) now. From today's accensione run: V5 and AT_ON while AT_T2S charges, the pull-up's
current, the rise of AT_ON a 10k -> 9.98k pull-up gives (I x 20 ohm), and the arming time that rise moves
(the RC charge to VREF: t = RC ln(V / (V - Vref)), dt/dV = -RC Vref / (V (V - Vref))).

    /usr/bin/python3 -I script/armo.py [out.txt]     -> armo.txt on stdout
"""
import math
import os
import sys

L = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = sys.argv[1] if len(sys.argv) > 1 else os.path.join(L, "seq", "oggi", "accensione",
                                                       "tb_psu_seq_accensione_g1_out.txt")
# the wrdata vectors of the deck (one time + value pair per vector), in order
VEC = ("front_in mute_sw_in mute_cmd permit_cmd vrelay vrelay_reg vplus vminus k501_f mute_g permit_g env "
       "mute_req permit_req mains_req vrelay_en vr_g mains_g raw_p raw_m isns1 isns2 raw_pr raw_mr at_pg "
       "at_pgt at_mrq at_mt at_t2s at_f at_md at_prt permit_t vr_t at_bn at_bp v5 raw_v rect_v").split()
TE, RC = 3.0, 2.7e6 * 1e-6
# one time column, then one column per vector (the header line names them)
cols = {n: i + 1 for i, n in enumerate(VEC)}
punti = []
with open(F) as f:
    for ln in f:
        p = ln.split()
        if len(p) != 1 + len(VEC) or p[0] == "time":
            continue
        t = float(p[0])
        von, v5 = float(p[cols["vrelay_en"]]), float(p[cols["v5"]])
        if TE + 0.5 <= t <= TE + 2.0:
            punti.append((von, v5))
von = sum(a for a, _ in punti) / len(punti)
v5 = sum(b for _, b in punti) / len(punti)
i_pu = (v5 - von) / 9.98e3
dv = i_pu * 20.0
# VREF from the deck's arming: t_arm = 2.1730 s after TE (an_l64b.csv); the charge starts near TE + 0
# with AT_T2S ~0 (D541 holds it to AT_ON while AT_ON is low); Vref solved from the charge itself
t_arm = 2.1730
vref = von * (1 - math.exp(-t_arm / RC))
dtdv = -RC * vref / (von * (von - vref))
print("AT_ON alto (media %.1f-%.1f s dall'evento): %.4f V; V5 %.4f V" % (0.5, 2.0, von, v5))
print("corrente nel pull-up: %.1f uA; 20 ohm in meno alzano AT_ON di %.3f mV" % (i_pu * 1e6, dv * 1e3))
print("VREF dalla carica (t_arm 2173,0 ms, RC 2,7 s): %.4f V; dt/dV %.1f ms/mV" % (vref, dtdv))
print("lo spostamento atteso dell'armo: %.2f ms (misurato: -0,6 / -0,7 ms contro L64b)" % (dtdv * dv * 1e3))
