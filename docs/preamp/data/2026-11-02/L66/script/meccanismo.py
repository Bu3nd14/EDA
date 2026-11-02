#!/usr/bin/env python3
"""L66: il meccanismo di Q132 in corto base-emettitore (NC-076), misurato. Solo stdlib,
/usr/bin/python3 -I.

Uso: meccanismo.py <pos> <modo> [<modo> ...]  -> meccanismo/<pos>_<modo>.cir per ciascuno

Prende i deck del banco (deck/sorg_<pos>/<modo>.cir, gli stessi della lista) e sostituisce il blocco
.control con: la stessa tran (1u 2.3 0 50u), e le medie su 2.29..2.3 s delle tensioni dei nodi del
blocco guasto XA e delle correnti di collettore e di base dei suoi transistor. Il circuito non cambia.
"""
import os
import re
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)

NODI = ("vplus vminus vpf nx nhi nvb nve nvs ny nbb nbn nen nbp nep nvle nref outa "
        "nme1 nme2 nmirc nmiri d1n d2n src").split()
QT = ("q122 q193 q125 q127 q132 q133 q146 q121a q121b q148 q106").split()


def nome(n):
    return "v(outa)" if n == "outa" else ("v(%s)" % n if n in ("vplus", "vminus") else "v(xa.%s)" % n)


def controllo(base):
    r = [".control", "set noaskquit", "option itl1=1000",
         "save " + " ".join([nome(n) for n in NODI] +
                            ["@q.xa.%s[ic]" % q for q in QT] + ["@q.xa.%s[ib]" % q for q in QT] +
                            ["@q.xa.%s[p]" % q for q in QT]),
         "tran 1u 2.3 0 50u"]
    for n in NODI:
        r.append("meas tran v_%s AVG %s from=2.29 to=2.3" % (n, nome(n)))
    for q in QT:
        for k in ("ic", "ib", "p"):
            r.append("meas tran %s_%s AVG @q.xa.%s[%s] from=2.29 to=2.3" % (k, q, q, k))
    r += [".endc"]
    return "\n".join(r)


def main(pos, modi):
    os.makedirs(os.path.join(L, "meccanismo"), exist_ok=True)
    for m in modi:
        t = open(os.path.join(L, "deck", "sorg_" + pos, m + ".cir")).read()
        t2, n = re.subn(r"\.control.*?\.endc", lambda _: controllo(m), t, flags=re.S)
        if n != 1:
            sys.exit("RIFIUTATO: %s/%s ha %d blocchi .control" % (pos, m, n))
        p = os.path.join(L, "meccanismo", "%s_%s.cir" % (pos, m))
        open(p, "w").write(t2)
        print(p)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2:])
