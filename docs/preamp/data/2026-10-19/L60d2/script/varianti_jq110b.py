#!/usr/bin/env python3
"""L60d2: JQ110B aperta sul blocco A, condensatore nominale, si ferma a 0,304 s ("Timestep too small",
4,26 ms dopo il guasto) col metodo normale e col gear. Tre varianti numeriche del deck gear, il
circuito uguale: rshunt 1e12 su ogni nodo, reltol 3e-4, il fronte del guasto in 100 us invece di
10 us. Se finiscono e danno la stessa durata, la durata regge. Solo stdlib.

Uso: varianti_jq110b.py   -> deck/diagnosi/A_JQ110B_as_{rshunt,reltol,fronte}.cir, deck/lista_jq110b.txt
"""
import os

L = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(L, "deck", "diagnosi")
base = open(os.path.join(D, "A_JQ110B_as_gear.cir")).read()
VAR = {
    "rshunt": ("option itl1=1000\n", "option itl1=1000\noption rshunt=1e12\n"),
    "reltol": ("option itl1=1000\n", "option itl1=1000\noption reltol=3e-4\n"),
    "fronte": ("VCTL CTL 0 PWL(0 0 0.3 0 0.30001 1)", "VCTL CTL 0 PWL(0 0 0.3 0 0.3001 1)"),
}
lista = []
for v, (a, b) in VAR.items():
    assert base.count(a) == 1, v
    t = base.replace(a, b).replace("A_JQ110B_as_gear", "A_JQ110B_as_" + v)
    p = os.path.join(D, "A_JQ110B_as_%s.cir" % v)
    open(p, "w").write(t)
    lista.append(p)
open(os.path.join(L, "deck", "lista_jq110b.txt"), "w").write("\n".join(lista) + "\n")
print(len(lista), "deck")
