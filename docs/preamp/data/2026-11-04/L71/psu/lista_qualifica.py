#!/usr/bin/env python3
"""L54b3a: the remedy on the bench (--qualifica): L54b2's safety list with the calibrated
comparator (lista_finale.txt, the fint_ lines: twelve channels), labels fint_ -> q_, and the sags,
the swell and the power-up sags of lista_rete.txt, labels r_ -> qr_, each with --qualifica.
/usr/bin/python3 -I lista_qualifica.py <L54b2/lista_finale.txt> <lista_rete.txt> <soglie> > ../lista_qualifica.txt"""
import sys

fin, rete, soglie = sys.argv[1:4]
for r in open(fin):
    p = r.split()
    if p and p[1].startswith("fint_"):
        p[1] = "q_" + p[1][len("fint_"):]
        print(" ".join(p) + " --qualifica " + soglie)
for r in open(rete):
    p = r.split()
    if p and p[1].startswith(("r_calo", "r_sovra", "r_acc")):
        p[1] = "q" + p[1]
        print(" ".join(p) + " --qualifica " + soglie)
