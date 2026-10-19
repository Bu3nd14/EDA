#!/usr/bin/env python3
"""L62a: il gradino al jack nell'istante del guasto del moltiplicatore. Con il blocco di oggi
Q127_ae da' 74 mV «A» alla principale (B, 0 dB); in L45a 0,42 mV. Quale parte nuova lo porta?
Il deck deck/base_B/<modo>.cir di genera_L62a.py, con la sola copia guasta cambiata:

  l45a     la copia di L45a/inc/ (il blocco di L45a: niente R150..R153, R112 / R144 100 / 10 ohm)
  r153     la copia di oggi con R153 a 1 ohm (l'inseguitore senza il limite di ADR-087)
  r150     la copia di oggi senza R150 (la resistenza in parallelo a R109, ADR-086)
  r151     la copia di oggi senza R151 / R152, e R112 / R144 ai valori di L45a (100 / 10 ohm)

Uso: diagnosi_scatto.py   -> deck/diagnosi/<modo>__<prova>.cir, inc/diagnosi/, deck/lista_diagnosi.txt
"""
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L62A = os.path.dirname(QUI)
sys.path.insert(0, QUI)
import genera_L62a as g  # noqa: E402

MODI = ("Q127_ae", "R128_ap")


def cambia(t, prova):
    righe = t.splitlines()
    if prova == "r153":
        righe = [r.replace("R153 NFC VMINUS 4.7k", "R153 NFC VMINUS 1") for r in righe]
    elif prova == "r150":
        righe = [r for r in righe if not r.startswith("R150 ")]
    elif prova == "r151":
        righe = [r for r in righe if not r.startswith(("R151 ", "R152 "))]
        righe = [r.replace("R112 S2 SRC 200", "R112 S2 SRC 100").replace("R144 VPLUS VPF 20", "R144 VPLUS VPF 10")
                 for r in righe]
    out = "\n".join(righe) + "\n"
    if out == t:
        sys.exit("RIFIUTATO: %s non cambia la copia" % prova)
    return out


def main():
    lista = []
    for m in MODI:
        deck = open(os.path.join(L62A, "deck", "base_B", m + ".cir")).read()
        oggi = "@REPO@/%s/inc/base/%s.subckt" % (g.REL, m)
        if deck.count(oggi) != 1:
            sys.exit("RIFIUTATO: il deck di %s non include la copia di oggi" % m)
        for prova in ("l45a", "r153", "r150", "r151"):
            if prova == "l45a":
                inc = "@REPO@/%s/inc/%s.subckt" % (g.gc.REL, m)
            else:
                t = open(os.path.join(L62A, "inc", "base", m + ".subckt")).read()
                g.scrivi(os.path.join(L62A, "inc", "diagnosi", "%s__%s.subckt" % (m, prova)), cambia(t, prova))
                inc = "@REPO@/%s/inc/diagnosi/%s__%s.subckt" % (g.REL, m, prova)
            # il nome della cartella di run deve essere il modo (il .dat si chiama <modo>.dat)
            p = os.path.join(L62A, "deck", "diagnosi_%s" % prova, m + ".cir")
            lista.append(g.scrivi(p, deck.replace(oggi, inc).replace("L62a base ", "L62a diagnosi %s " % prova, 1)))
    g.scrivi(os.path.join(L62A, "deck", "lista_diagnosi.txt"), "\n".join(lista) + "\n")
    print("diagnosi: %d deck" % len(lista))


if __name__ == "__main__":
    main()
