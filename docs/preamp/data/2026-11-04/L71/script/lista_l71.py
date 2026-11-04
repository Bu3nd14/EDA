#!/usr/bin/env python3
"""L71 (NC-083): the sequences with the front switch / SW3 moved during a sequence, on today's
circuit (circuits/preamp/psu.net), with L69b's options, at mains -10 / 0 / +10 %.
The cases are psu/genera_tb_psu.py's L71 families (acc_spento_, spl_riacceso_, ins_ritorno_,
ril_ritorno_, spl_sw3_), read from the generator itself so that the list cannot drift from it.

    /usr/bin/python3 -I script/lista_l71.py
writes lista_l71.txt; labels l71, l71_m10, l71_p10.
"""
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
    if not m:
        raise SystemExit("RIFIUTATO: %s non trovato nel generatore" % var)
    casi += [pre + x.strip().strip('"') for x in m.group(1).split(",") if x.strip()]
out = []
for suff, rete in (("", None), ("_m10", "0.9"), ("_p10", "1.1")):
    for c in casi:
        r = "%s l71%s %s" % (c, suff, BASE)
        out.append(r + (" --rete %s" % rete if rete else ""))
nome = os.path.join(L, "lista_l71.txt")
with open(nome, "w") as f:
    f.write("\n".join(out) + "\n")
print(nome, len(casi), "casi,", len(out), "corse")
