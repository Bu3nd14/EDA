#!/usr/bin/env python3
"""L70: the runs of the variants, from L69b's list (lista_l64b.txt, copied here).

    /usr/bin/python3 -I script/lista_varianti.py <variante> <eventi|tutte> [--fusibile I2T:ITH:RC] [--tag x]

Each line of lista_l64b.txt (<caso> oggi[_m10|_p10] sorgente <opzioni>) becomes
<caso> <variante><tag>[_m10|_p10] sorgente <opzioni> --net varianti/psu_<variante>.net [--fusibile ...]
'eventi' keeps the lines that are not f_* (the events of the sequence); 'tutte' every line.
Writes lista_<variante><tag>_<scelta>.txt.
"""
import os
import sys

L = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
v, scelta = sys.argv[1], sys.argv[2]
assert v in ("s1", "s2", "s1s2", "s1s2dc", "oggi") and scelta in ("eventi", "tutte")
fus = sys.argv[sys.argv.index("--fusibile") + 1] if "--fusibile" in sys.argv else None
tag = sys.argv[sys.argv.index("--tag") + 1] if "--tag" in sys.argv else ""
if ("1" in v) != bool(fus):
    raise SystemExit("RIFIUTATO: --fusibile va con s1 / s1s2, e solo con loro")
net = os.path.join(L, "varianti", "psu_%s.net" % v)
out = []
for ln in open(os.path.join(L, "lista_l64b.txt")):
    x = ln.split()
    if not x or (scelta == "eventi" and x[0].startswith("f_")):
        continue
    assert x[1].startswith("oggi") and x[2] == "sorgente", ln
    etich = v + tag + x[1][4:]
    extra = [] if v == "oggi" else ["--net", net] + (["--fusibile", fus] if fus else [])
    out.append(" ".join([x[0], etich] + x[2:] + extra))
nome = os.path.join(L, "lista_%s%s_%s.txt" % (v, tag, scelta))
with open(nome, "w") as f:
    f.write("\n".join(out) + "\n")
print(nome, len(out), "corse")
