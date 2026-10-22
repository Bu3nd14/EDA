#!/usr/bin/env python3
"""L45d2b3b1: V5 contro RLY_RET (la massa della logica) e contro la massa del banco, nell'ultimo giro
di un caso dell'alimentatore. Solo stdlib, /usr/bin/python3 -I.

Uso: v5_relativa.py <seq/etichetta/caso>
analizza_075.py legge v5_max / v5_min contro il nodo 0; il micro vede V(v5) - V(rly_ret).
"""
import glob
import os
import re
import sys

d = sys.argv[1]
caso = os.path.basename(d.rstrip("/"))
cir = sorted(glob.glob(os.path.join(d, "tb_psu_seq_%s_g*.cir" % caso)),
             key=lambda p: int(re.search(r"_g(\d+)\.cir$", p).group(1)))[-1]
out = cir.replace(".cir", "_out.txt")
f = open(out)
# wr_singlescale + wr_vecnames: una colonna del tempo, i nomi nella prima riga
nomi = f.readline().split()
iv5, irr, ivp = nomi.index("v(v5)"), nomi.index("v(rly_ret)"), nomi.index("v(vplus)")
v5 = []
for r in f:
    x = [float(a) for a in r.split()]
    v5.append((x[0], x[iv5], x[irr], x[ivp]))
mn = min(v5, key=lambda a: a[1] - a[2])
ma = min(v5, key=lambda a: a[1])
print("%s (%s): V5-RLY_RET min %.3f V a %.4f s; V5 min %.3f V (RLY_RET %.3f) a %.4f s; fine: V5 %.3f, RLY_RET %.3f, VPLUS %.3f"
      % (caso, os.path.basename(cir), mn[1] - mn[2], mn[0], ma[1], ma[2], ma[0], v5[-1][1], v5[-1][2], v5[-1][3]))
