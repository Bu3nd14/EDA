#!/usr/bin/env python3
"""L70: the fault cases of the raw side (modi.py, L45d2b2b1 / L58a rows), where a fuse on T1's
secondary or a fusing R550 / R551 would act: the reservoirs, the regulators' pins, the bridge's
diodes shorted, the pin Schottkys and the series Schottkys, at the mains of each row.

    /usr/bin/python3 -I script/lista_corti.py <variante> [--fusibile I2T:ITH:RC] [--tag x]
writes lista_corti_<variante><tag>.txt; label <variante><tag> (the mains is in the case's name).
"""
import os
import sys

L = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(L, "psu"))
import modi  # noqa: E402

v = sys.argv[1]
fus = sys.argv[sys.argv.index("--fusibile") + 1] if "--fusibile" in sys.argv else None
tag = sys.argv[sys.argv.index("--tag") + 1] if "--tag" in sys.argv else ""
if ("1" in v) != bool(fus):
    raise SystemExit("RIFIUTATO: --fusibile va con s1 / s1s2, e solo con loro")
CHIAVI = ("c501", "c502", "c509", "c510", "d501", "d510", "d511", "d515", "d516")
casi = [c[0] for c in modi.SIMULATI if any(c[0].startswith("f_" + k) for k in CHIAVI)]
BASE = ("sorgente --n2n7002 ds --tss 3.0 --comparatore tarato --ritenuta costruttore "
        "--bat54 costruttore --sonde-piu")
out = []
for c in casi:
    r = [c, v + tag, BASE]
    if v != "oggi":
        r += ["--net", os.path.join(L, "varianti", "psu_%s.net" % v)]
    if fus:
        r += ["--fusibile", fus]
    out.append(" ".join(r))
nome = os.path.join(L, "lista_corti_%s%s.txt" % (v, tag))
with open(nome, "w") as f:
    f.write("\n".join(out) + "\n")
print(nome, len(out), "corse")
