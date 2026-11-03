#!/usr/bin/env python3
"""L58a2: print chosen columns of an analizza_mc.py CSV, one row per case, aligned.

Solo stdlib. /usr/bin/python3 -I colonne.py <an.csv> [col,col,...]
"""
import csv
import sys

COL = ("caso,t_mus_ms,n_giu,n_su,dmus_ms,mus_end,k501_end,vplus_end,ritenuta,bn_max0,bn_max,on_min,"
       "t_pg_ms,t_arm_ms,d_perm_ms,k_perm_ms,x_max,esito")
cols = (sys.argv[2] if len(sys.argv) > 2 else COL).split(",")
with open(sys.argv[1]) as f:
    righe = list(csv.DictReader(f))
larg = {c: max([len(c)] + [len(r.get(c, "")) for r in righe]) for c in cols}
print(" ".join(c.ljust(larg[c]) for c in cols))
for r in righe:
    print(" ".join(r.get(c, "").ljust(larg[c]) for c in cols))
