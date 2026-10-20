#!/usr/bin/env python3
"""L45d2b2a: the rails each V2 power-up run actually simulated, against the bench's - so that a
refused alter (limitations #66) cannot pass for the bench's ramp. Stdlib.

Uso: controlla_rampe.py RUNDIR    -> ../controllo_rampe.txt, exit 1 on a mismatch

For each on_ss* run: v(vplus) and v(vminus) from <run>_stati (wrdata pairs), at 0.1 + 0.35 s and
0.1 + 0.55 s in the deck, against the bench's rails at the same instant from their start, scaled as
genera_v2_accensione.py scales them; within 0.3 V (the 30 ms linear segments). on_r300s_iii must
NOT match (L29c's 300 ms ramp): the check's own sabotage.
"""
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
SEQ = os.path.join(L, "seq", "sorgente", "accensione")
K = {"nom": (1.0, 1.0), "ps": (1 / 1.2, 1.2), "pf": (1.2, 1 / 1.2)}


def leggi(path):
    f = open(path)
    nomi = f.readline().split()
    col = {n: [] for n in nomi}
    for r in f:
        p = r.split()
        if len(p) == len(nomi):
            for n, x in zip(nomi, p):
                col[n].append(float(x))
    return col


def valore(t, v, x):
    i = min(range(len(t)), key=lambda j: abs(t[j] - x))
    return v[i]


g = open(os.path.join(SEQ, "punto_fisso.txt")).read().strip()
b = leggi(os.path.join(SEQ, "tb_psu_seq_accensione_g%s_out.txt" % g))
t0 = next(b["time"][k] for k in range(len(b["time"])) if b["v(mains_req)"][k] > 2.5)
ts = next(b["time"][k] for k in range(len(b["time"]))
          if b["time"][k] > t0 and (b["v(vplus)"][k] > 0.01 or b["v(vminus)"][k] < -0.01))
d = sys.argv[1]
out, ko = [], 0
for nome in sorted(x for x in os.listdir(d) if x.startswith("on_") and x.endswith("_stati.dat")):
    corsa = nome[:-len("_stati.dat")]
    righe = [r.split() for r in open(os.path.join(d, nome)) if r.strip()]
    # wrdata pairs: (t, v(ina)), (t, v(vplus)), (t, v(vminus)), ...
    righe = [list(map(float, r)) for r in righe if len(r) >= 6 and r[0][0] in "0123456789-."]
    t = [r[0] for r in righe]
    vp, vm = [r[3] for r in righe], [r[5] for r in righe]
    var = corsa.split("_")[-2] if corsa.startswith("on_ss") else None
    kp, km = K.get(var, (1.0, 1.0))
    ok_tutti = True
    for tt in (0.35, 0.55):
        ap = valore(b["time"], b["v(vplus)"], ts + tt / kp)
        am = valore(b["time"], b["v(vminus)"], ts + tt / km)
        sp, sm = valore(t, vp, 0.1 + tt), valore(t, vm, 0.1 + tt)
        ok = abs(sp - ap) < 0.3 and abs(sm - am) < 0.3
        ok_tutti &= ok
        out.append("%-16s t=%.2f  + %7.3f (banco %7.3f)  - %8.3f (banco %8.3f)  %s"
                   % (corsa, tt, sp, ap, sm, am, "uguale" if ok else "DIVERSO"))
    atteso = corsa.startswith("on_ss")
    if ok_tutti != atteso:
        ko += 1
        out.append("  -> FUORI: %s" % ("le rampe non sono quelle del banco" if atteso
                                       else "il controllo non distingue la rampa di L29c"))
out.append("fuori: %d" % ko)
open(os.path.join(L, "controllo_rampe.txt"), "w").write("\n".join(out) + "\n")
print("\n".join(out))
sys.exit(1 if ko else 0)
