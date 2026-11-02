#!/usr/bin/env python3
"""L66: le misure dei deck di meccanismo.py (run/meccanismo/<nome>/<nome>.log) in una tabella,
una colonna per corsa. Solo stdlib, /usr/bin/python3 -I.

Uso: leggi_meccanismo.py <out.csv> <nome> [<nome> ...]
"""
import os
import re
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
RE = re.compile(r"^\s*([a-z0-9_]+)\s*=\s*([-+0-9.eE]+)", re.M)


def misure(n):
    t = open(os.path.join(L, "run", "meccanismo", n, n + ".log"), errors="replace").read()
    return dict(RE.findall(t))


def main(out, nomi):
    m = {n: misure(n) for n in nomi}
    chiavi = []
    for n in nomi:
        for k in m[n]:
            if k not in chiavi:
                chiavi.append(k)
    righe = ["misura," + ",".join(nomi)]
    for k in chiavi:
        righe.append(k + "," + ",".join("%.5g" % float(m[n][k]) if k in m[n] else "" for n in nomi))
    open(out, "w").write("\n".join(righe) + "\n")
    print("\n".join(righe))


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2:])
