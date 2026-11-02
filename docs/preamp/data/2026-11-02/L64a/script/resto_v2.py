#!/usr/bin/env python3
"""L64a: la regex delle corse di V2 ancora da fare. resto_v2.py <cartella> <cella in corsa> ...
Tutte le corse di corse_sel.txt tranne: quelle con una riga rc=0 in tempi.txt, quelle ancora in
corsa (gli argomenti), e quelle con rc=OPT (vanno coi .nodeset del blocco, nodeset_v2.py).
Stampa la regex per corri.sh di L29c (vuota se non resta niente)."""
import os
import sys

d = sys.argv[1]
in_corsa = set(sys.argv[2:])
tutte = [c.strip() for c in open(os.path.join(d, "corse_sel.txt")) if c.strip()]
fatte, opt = set(), set()
for ln in open(os.path.join(d, "tempi.txt")):
    p = ln.split()
    if len(p) >= 2 and p[1] == "rc=0":
        fatte.add(p[0])
    elif len(p) >= 2 and p[1] == "rc=OPT":
        opt.add(p[0])
resto = [c for c in tutte if c not in fatte | opt | in_corsa]
# seleziona.py di L29c rifiuta una selezione che non nomina i riferimenti delle celle tenute, e
# allora corri.sh resta con la lista di prima (tutta la matrice, celle rc=OPT comprese). I
# riferimenti si aggiungono: quelli gia' corsi con rc=0 corri.sh li salta.
import csv  # noqa: E402
rif = set()
for r in csv.DictReader(open(os.path.join(d, "manifest.csv"))):
    if r["file"][:-4] in resto:
        rif |= {r["rif_ins"], r["rif_rel"]} - {"-", ""}
resto += sorted(rif - set(resto))
print("^(" + "|".join(resto) + ")$" if resto else "")
