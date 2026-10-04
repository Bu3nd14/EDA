"""componi.py - un'accoppiata con l'inserimento da una griglia e il rilascio da un'altra (tempi
diversi nei due versi), nello stesso formato di asimmetrico.json, per sfumatura.py.

    /usr/bin/python3 componi.py <asim_ins.json> <crit_ins> <asim_rel.json> <crit_rel> <nome> <uscita.json>
"""
import json
import os
import sys

a_i, c_i, a_r, c_r, nome, out = sys.argv[1:7]
ins = json.load(open(a_i))[c_i]["inserimento"]
rel = json.load(open(a_r))[c_r]["rilascio"]
d = json.load(open(out)) if os.path.exists(out) else {}
d[nome] = {"inserimento": ins, "rilascio": rel,
           "da": {"inserimento": [os.path.basename(a_i), c_i], "rilascio": [os.path.basename(a_r), c_r]}}
json.dump(d, open(out, "w"), indent=1)
print(nome, d[nome])
