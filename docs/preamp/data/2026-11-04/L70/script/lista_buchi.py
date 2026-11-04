#!/usr/bin/env python3
"""L70: the mains holes between 20 and 200 ms, on today's circuit and on the variants: the case
buco200 (from MUSICA, tf = TE + 1.6 s) with --rete-forma buco:<ms>:zero, at the three mains.
Without the detector the mute comes only when a rail or VRELAY_REG crosses its threshold: the
question is which holes mute, and whether the latch (S2 alone) then holds the toroid off.

    /usr/bin/python3 -I script/lista_buchi.py <variante> [--fusibile I2T:ITH:RC]
writes lista_buchi_<variante>.txt; labels <variante>_b<ms>[_m10|_p10].
"""
import os
import sys

L = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
v = sys.argv[1]
fus = sys.argv[sys.argv.index("--fusibile") + 1] if "--fusibile" in sys.argv else None
if ("1" in v) != bool(fus):
    raise SystemExit("RIFIUTATO: --fusibile va con s1 / s1s2, e solo con loro")
BASE = ("sorgente --n2n7002 ds --tss 3.0 --comparatore tarato --ritenuta costruttore "
        "--bat54 costruttore --sonde-piu")
out = []
for ms in (40, 60, 80, 100, 150):
    for suff, rete in (("", None), ("_m10", "0.9"), ("_p10", "1.1")):
        r = ["buco200", "%s_b%d%s" % (v, ms, suff), BASE, "--rete-forma", "buco:%d:zero" % ms]
        if rete:
            r += ["--rete", rete]
        if v != "oggi":
            r += ["--net", os.path.join(L, "varianti", "psu_%s.net" % v)]
        if fus:
            r += ["--fusibile", fus]
        out.append(" ".join(r))
nome = os.path.join(L, "lista_buchi_%s.txt" % v)
with open(nome, "w") as f:
    f.write("\n".join(out) + "\n")
print(nome, len(out), "corse")
