#!/usr/bin/env python3
"""L45d2b3b2a: i guasti del VAS sulla variante rv2 coi dispositivi a 60 C invece che a 27 C. Solo
stdlib, /usr/bin/python3 -I.

Uso: caldo.py <variante> <temp> <modo> [...]   -> deck/<variante>t<temp>_<pos>/<modo>.cir (piu' rif),
                                                  deck/lista_<variante>t<temp>.txt

Il banco del calore simula ogni dispositivo a 27 C e calcola la Tj dopo dalla potenza: la soglia del
limite del VAS (la Vbe di Q168) e' quella a 27 C. Qui tutto il circuito a <temp> (una riga `.temp`
con UN valore: limitations, «.temp con lista»), per vedere in che verso si muove la potenza del VAS
quando il limitatore e' caldo. E' un'indicazione, non la Tj di ciascun dispositivo alla sua temperatura.
"""
import os
import sys

L = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main(v, temp, modi):
    lista = []
    for cart in sorted(os.listdir(os.path.join(L, "deck"))):
        if not cart.startswith(v + "_"):
            continue
        pos = cart[len(v) + 1:]
        for m in ["rif"] + modi:
            src = os.path.join(L, "deck", cart, m + ".cir")
            if not os.path.isfile(src):
                continue
            t = open(src).read()
            if t.count("\n.control\n") != 1 or ".temp" in t:
                sys.exit("RIFIUTATO: %s" % src)
            t = t.replace("\n.control\n", "\n.temp %s\n.control\n" % temp)
            p = os.path.join(L, "deck", "%st%s_%s" % (v, temp, pos), m + ".cir")
            os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, "w").write(t)
            lista.append(p)
    open(os.path.join(L, "deck", "lista_%st%s.txt" % (v, temp)), "w").write("\n".join(lista) + "\n")
    print("%d deck" % len(lista))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3:])
