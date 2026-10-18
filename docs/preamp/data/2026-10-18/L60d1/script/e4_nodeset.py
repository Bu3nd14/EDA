#!/usr/bin/env python3
"""L60d1: tb_e4_uscite risolto, con un .nodeset sui VPF dei quattro blocchi (14,85 V, il valore
del punto di lavoro vivo) prima di .control. Nella cella trim=0 att=25 +3 dB «dopo» il solutore
trovava, anche da zero, una soluzione spuria col canale spento (5,57 A sul rail positivo); il
transitorio d'accensione nella stessa cella arriva allo stato vivo (prova_e4.py).

Uso: e4_nodeset.py <tb_e4_uscite_resolved.cir> <cartella>  -> <cartella>/tb_e4_uscite.cir
"""
import os
import sys

src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
t = open(src).read()
ns = ".nodeset " + " ".join("v(%s.vpf)=14.85" % x for x in ("xa", "xf1", "xf2", "xb"))
assert t.count("\n.control") == 1
t = t.replace("\n.control", "\n" + ns + "\n.control")
open(os.path.join(out, "tb_e4_uscite.cir"), "w").write(t)
print(ns, "->", out)
