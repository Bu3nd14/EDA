#!/usr/bin/env python3
"""L46a: punto di lavoro per variante da run/<v>/tb_op/tb_op.log.

Corrente di riposo d'uscita (Q132/Q133), VAS (Q122), corrente del rail +, continua
all'uscita. Una riga `nome = <cifre>Note: ...` (#37) si ricuce col primo rigo di
sole cifre dopo le Note. -> run/punto_di_lavoro.csv

Uso: /usr/bin/python3 riassumi_op.py <variante>...
"""
import csv
import os
import re
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L46A = os.path.dirname(QUI)
CHIAVI = ["@q132[ic]", "@q133[ic]", "@q122[ic]", "i(vpp)", "i(vmm)", "v(out)", "v(nx)", "v(ny)"]


def valori(log):
    righe = open(log, errors="replace").read().split("\n")
    if any("Error" in r for r in righe):
        sys.exit("%s: righe Error" % log)
    out = {}
    for k, r in enumerate(righe):
        for c in CHIAVI:
            m = re.match(re.escape(c) + r" = ([-+0-9.eE]+)(Note:)?", r)
            if m and c not in out:
                testo = m.group(1)
                if m.group(2):
                    j = k + 1
                    while not re.match(r"^[-+0-9.eE]+$", righe[j].strip()):
                        j += 1
                    testo += righe[j].strip()
                out[c] = float(testo)
    return out


tab = []
for v in sys.argv[1:]:
    x = valori(os.path.join(L46A, "run", v, "tb_op", "tb_op.log"))
    tab.append([v, "%.2f" % (x["@q132[ic]"] * 1e3), "%.2f" % (-x["@q133[ic]"] * 1e3),
                "%.2f" % (-x["@q122[ic]"] * 1e3), "%.2f" % (-x["i(vpp)"] * 1e3),
                "%.2f" % (x["i(vmm)"] * 1e3), "%.2f" % (x["v(out)"] * 1e3)])
with open(os.path.join(L46A, "run", "punto_di_lavoro.csv"), "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["variante", "iq_n_ma", "iq_p_ma", "vas_ma", "i_vpp_ma", "i_vmm_ma", "vout_mv"])
    w.writerows(tab)
for r in tab:
    print("%-22s Iq %s / %s mA  VAS %s mA  rail+ %s mA  rail- %s mA  out %s mV" % tuple(r))
