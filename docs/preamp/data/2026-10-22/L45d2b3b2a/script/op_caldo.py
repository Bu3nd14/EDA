#!/usr/bin/env python3
"""L45d2b3b2a: il limite del VAS a riposo, a caldo. tb_op (il blocco piatto) della variante, con
`.temp` a un valore e in piu' le correnti di Q168 (il limitatore) e del VAS. Solo stdlib,
/usr/bin/python3 -I.

Uso: op_caldo.py           -> deck/op_caldo/<v>_t<T>.cir, deck/lista_op_caldo.txt
     op_caldo.py leggi     stampa e scrive op_caldo.csv dalle corse in run/op_caldo/

Quanto ruba Q168 alla base del VAS: a riposo su R123 (33 ohm) cadono ~0,35 V; a caldo la Vbe di Q168
scende (~2 mV/K) e la sua corrente di collettore sale. La base del VAS e' ~83 uA (gain_block.py).
"""
import csv
import os
import re
import sys

L = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VARIANTI = ("oggi", "rv2")
TEMPI = (27, 60, 90)
STAMPA = "print @q168[ic] @q168[vbe]\n"


def genera():
    lista = []
    for v in VARIANTI:
        t0 = open(os.path.join(L, "regressione", "deck_" + v, "tb_op.cir")).read()
        for T in TEMPI:
            t = t0
            if t.count("\n.control\n") != 1:
                sys.exit("RIFIUTATO: .control")
            t = t.replace("\n.control\n", "\n.temp %d\n.control\n" % T)
            agg = "print i(VPP) i(VMM)\n" + (STAMPA if v != "oggi" else "")
            if t.count("print i(VPP) i(VMM)\n") != 1:
                sys.exit("RIFIUTATO: print i(VPP)")
            t = t.replace("print i(VPP) i(VMM)\n", agg)
            p = os.path.join(L, "deck", "op_caldo", "%s_t%d.cir" % (v, T))
            os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, "w").write(t)
            lista.append(p)
    open(os.path.join(L, "deck", "lista_op_caldo.txt"), "w").write("\n".join(lista) + "\n")
    print("%d deck" % len(lista))


def valore(log, nome):
    m = re.search(r"^%s\s+=\s+([-+0-9.eE]+)" % re.escape(nome), log, re.M | re.I)
    return float(m.group(1)) if m else float("nan")


def leggi():
    righe = []
    for v in VARIANTI:
        for T in TEMPI:
            b = "%s_t%d" % (v, T)
            log = open(os.path.join(L, "run", "op_caldo", b, b + ".log")).read()
            r = {"variante": v, "T_C": T}
            for k in ("@q122[ic]", "@q122[ib]", "@q168[ic]", "@q168[vbe]", "@q132[ic]", "v(out)", "i(vpp)"):
                r[k] = valore(log, k)
            righe.append(r)
            print("%-5s %3d C  VAS %.3f mA (base %.1f uA)  Q168 %.3g uA (Vbe %.3f)  finale %.2f mA  uscita %.2f mV" % (
                v, T, -r["@q122[ic]"] * 1e3, -r["@q122[ib]"] * 1e6, -r["@q168[ic]"] * 1e6, r["@q168[vbe]"],
                r["@q132[ic]"] * 1e3, r["v(out)"] * 1e3))
    with open(os.path.join(L, "op_caldo.csv"), "w", newline="") as fo:
        w = csv.DictWriter(fo, fieldnames=list(righe[0]))
        w.writeheader()
        w.writerows(righe)


if __name__ == "__main__":
    leggi() if sys.argv[1:] == ["leggi"] else genera()
