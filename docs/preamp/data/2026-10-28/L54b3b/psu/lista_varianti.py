#!/usr/bin/env python3
"""L54b3a: the two remedies' variants before the questions to the user.
  qv_: --qualifica v:12.7 (the relays' raw only): L54b2's safety list (fint_ lines) and the sags of
       lista_rete.txt, as lista_qualifica.py;
  lp_: the low-leakage diodes on the three megohm nodes (D535, D541, D536 with the BAV199 model) and
       R571 1 MEG, with the makers' BAT54 and transistors: the cases that set the timings
       (accensione, buco20, buco200, accensione_u501, guasto, fredda, spegnimento_l, perdita).
/usr/bin/python3 -I lista_varianti.py <L54b2/lista_finale.txt> <lista_rete.txt> > ../lista_varianti.txt"""
import sys

fin, rete = sys.argv[1:3]
for r in open(fin):
    p = r.split()
    if p and p[1].startswith("fint_"):
        p[1] = "qv_" + p[1][len("fint_"):]
        print(" ".join(p) + " --qualifica v:12.7")
for r in open(rete):
    p = r.split()
    if p and p[1].startswith(("r_calo", "r_acc")):
        p[1] = "qv" + p[1]
        print(" ".join(p) + " --qualifica v:12.7")
LP = ("--n2n7002 ds --tss 3.0 --comparatore tarato --sonde-piu --ritenuta costruttore --bat54 costruttore"
      " --bassa-perdita D535,D541,D536 --valore R571=1MEG")
for caso in ("accensione", "buco20", "buco200", "accensione_u501", "guasto", "fredda", "spegnimento_l",
             "perdita"):
    print("%s lp_sorgente sorgente %s" % (caso, LP))
