#!/usr/bin/env python3
"""L60c2: A Q122_ce, la corsa che si ferma 6 ms dopo il guasto (anche in L45b, 0,306 s), rifatta col
metodo gear e, in una seconda variante, col passo massimo a 5 us. Solo stdlib, /usr/bin/python3 -I.

Uso: ricorsa_q122.py        scrive deck/ricorse/G0_A_Q122_ce_{gear,gear5u}{,_k105}.cir e deck/ricorse/lista.txt
"""
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
import genera_L60c2 as g2   # noqa: E402

g1, gc = g2.g1, g2.gc
lista = []
for var in ("gear", "gear5u"):
    for k in (1.0, 1.05):
        sk = "" if k == 1.0 else "_k105"
        t = gc.deck_tr("A", 0, "Q122_ce", False, False, tfine=g2.T_FINE, gear=True)
        t = g1.applica(t, "G0", k)
        if var == "gear5u":
            righe = t.split("\n")
            tr = [i for i, r in enumerate(righe) if r.startswith("tran ")]
            if len(tr) != 1:
                sys.exit("RIFIUTATO: tran")
            p = righe[tr[0]].split()
            # tran passo tfine [tstart [tmax]]: il passo massimo a 5 us
            righe[tr[0]] = " ".join(p[:3] + ["0", "5u"] + [x for x in p[5:] if x.lower() == "uic"])
            t = "\n".join(righe)
        nome = "G0_A_Q122_ce_%s%s" % (var, sk)
        t = g1.rinomina(t, nome)
        p = os.path.join(g2.L60C2, "deck", "ricorse", nome + ".cir")
        gc.scrivi(p, "L60c2 ricorse %s - " % nome + t)
        lista.append(p)
gc.scrivi(os.path.join(g2.L60C2, "deck", "ricorse", "lista.txt"), "\n".join(lista) + "\n")
print("\n".join(lista))
