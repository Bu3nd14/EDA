#!/usr/bin/env python3
"""L45d2b3b1: l'energia nella resistenza della cella RC col condensatore in corto (scelta 10, «R144
contro la sua parte»), dall'ultimo giro di un caso f_c145_corto_* del banco dell'alimentatore. Solo
stdlib, /usr/bin/python3 -I.

Uso: energia_cella.py <seq/etichetta> <caso> [<caso> ...]

Dall'istante del guasto tg (la riga VGF_c del deck) i 10 ohm (R144 || R152, due 20 ohm, ADR-086)
stanno fra VPLUS e massa: la potenza totale e' V(vplus)^2 / 10, ciascuna delle due ne prende meta'
(i(vfc) non e' fra i vettori scritti di questo caso). Le misure di L45d2b1 (energia, picco, tempo
sopra 1 W) per il totale, e per la singola resistenza. Integrazione a trapezi sui campioni.
"""
import glob
import os
import re
import sys

R = 10.0


def ultimo_cir(d, caso):
    return sorted(glob.glob(os.path.join(d, caso, "tb_psu_seq_%s_g*.cir" % caso)),
                  key=lambda p: int(re.search(r"_g(\d+)\.cir$", p).group(1)))[-1]


for caso in sys.argv[2:]:
    cir = ultimo_cir(sys.argv[1], caso)
    vg = [r for r in open(cir) if r.startswith("VGF_c ")]
    assert len(vg) == 1, vg
    tg = float(vg[0].split("pwl(")[1].split()[2])
    f = open(cir.replace(".cir", "_out.txt"))
    nomi = f.readline().split()
    ivp = nomi.index("v(vplus)")
    t, p, vp = [], [], []
    for r in f:
        x = [float(a) for a in r.split()]
        t.append(x[0])
        p.append(x[ivp] ** 2 / R if x[0] > tg else 0.0)
        vp.append(x[ivp])
    e = sum(0.5 * (p[k] + p[k - 1]) * (t[k] - t[k - 1]) for k in range(1, len(t)))
    sopra = sum(t[k] - t[k - 1] for k in range(1, len(t)) if p[k] > 1.0)
    sopra_1 = sum(t[k] - t[k - 1] for k in range(1, len(t)) if p[k] / 2 > 1.0)
    k0 = next(k for k, x in enumerate(p) if x > 1e-3)
    print("%s: dal guasto a %.4f s; totale %.3f J, picco %.2f W, sopra 1 W %.1f ms; "
          "ciascuna 20 ohm %.3f J, picco %.2f W, sopra 1 W %.1f ms; VPLUS alla fine %.3f V"
          % (caso, t[k0], e, max(p), 1e3 * sopra, e / 2, max(p) / 2, 1e3 * sopra_1, vp[-1]))
