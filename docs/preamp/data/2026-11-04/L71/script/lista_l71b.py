#!/usr/bin/env python3
"""L71, the second list: the instants added after the first 135 runs, where the permissive's delay
after the mute (Delta) shortens with a short MUSICA (an_l71.csv d_perm_ms: 17.5 ms at ril_ritorno_12,
20.8 at acc_spento_1205): ril_ritorno_9 / 10 / 11 and acc_spento_1201 ... 1204, at the three mains.
The cases of the generator's families that are NOT in lista_l71.txt (which stays the list that ran).
    /usr/bin/python3 -I script/lista_l71b.py      -> lista_l71b.txt"""
import os
import re

L = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = ("sorgente --n2n7002 ds --tss 3.0 --comparatore tarato --ritenuta costruttore "
        "--bat54 costruttore --sonde-piu")
src = open(os.path.join(L, "psu", "genera_tb_psu.py")).read()
fam = {"L71_ACC": "acc_spento_", "L71_SPL": "spl_riacceso_", "L71_INS": "ins_ritorno_",
       "L71_RIL": "ril_ritorno_", "L71_SPLSW3": "spl_sw3_"}
casi = []
for var, pre in fam.items():
    m = re.search(r"^%s = \(([^)]*)\)" % var, src, re.M)
    casi += [pre + x.strip().strip('"') for x in m.group(1).split(",") if x.strip()]
prima = set(tuple(l.split()[:2]) for l in open(os.path.join(L, "lista_l71.txt")) if l.strip())
out = []
for suff, rete in (("", None), ("_m10", "0.9"), ("_p10", "1.1")):
    for c in casi:
        if (c, "l71" + suff) in prima:
            continue
        out.append("%s l71%s %s" % (c, suff, BASE) + (" --rete %s" % rete if rete else ""))
open(os.path.join(L, "lista_l71b.txt"), "w").write("\n".join(out) + "\n")
print("lista_l71b.txt", len(out), "corse")
