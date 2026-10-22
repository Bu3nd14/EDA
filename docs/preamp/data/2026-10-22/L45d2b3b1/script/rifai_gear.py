#!/usr/bin/env python3
"""L45d2b3b1: le corse della Stax fermate subito dopo il guasto («CORSA CORTA», il passo crollato)
rifatte col metodo gear, come le corse buone di L60c2 / L45a. Solo stdlib, /usr/bin/python3 -I.

Uso: rifai_gear.py <caso> [<caso> ...]    da deck/stax_guasti/<caso>.cir a deck/stax_gear/<caso>.cir,
                                          con `option method=gear` dopo `option itl1=1000`;
                                          scrive deck/lista_stax_gear.txt
"""
import os
import sys

L = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
lista = []
args = sys.argv[1:]
# --da <gruppo>: i deck d'origine in deck/<gruppo>/ (default stax_guasti); l'uscita in deck/<gruppo>_gear/
da = "stax_guasti"
if args[:1] == ["--da"]:
    da, args = args[1], args[2:]
dest = "stax_gear" if da == "stax_guasti" else da + "_gear"
for caso in args:
    t = open(os.path.join(L, "deck", da, caso + ".cir")).read()
    if "method=gear" in t:
        sys.exit("RIFIUTATO: %s e' gia' in gear" % caso)
    a = "option itl1=1000\n"
    if t.count(a) != 1:
        sys.exit("RIFIUTATO: %s ha %d righe %r" % (caso, t.count(a), a))
    t = t.replace(a, a + "option method=gear\n")
    p = os.path.join(L, "deck", dest, caso + ".cir")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w").write(t)
    lista.append(p)
open(os.path.join(L, "deck", "lista_%s.txt" % dest), "w").write("\n".join(lista) + "\n")
print("gear: %d deck" % len(lista))
