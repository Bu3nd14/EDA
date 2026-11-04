#!/usr/bin/env python3
"""L54b3a: the dirty-mains list (README, «I criteri»), one line per run for corri_lista_an.sh:
<caso> <etichetta> sorgente <options>. From buco20 (in music at TE) with --rete-forma, at the three
mains factors; buco:20:zero and buco:200:zero at 0 % are L54b2's fint_sorgente buco20 / buco200
(not redone). Two sags during the power-up, at 0 %.
/usr/bin/python3 -I lista_rete.py > ../lista_rete.txt"""
BASE = "--n2n7002 ds --tss 3.0 --comparatore tarato --sonde-piu"
RETI = (("m10", " --rete 0.9"), ("nom", ""), ("p10", " --rete 1.1"))
forme = []
for f in (0.85, 0.80, 0.70):
    for d in (0.1, 0.5, 2.0):
        forme.append(("calo%d_%g" % (round(f * 100), d), "calo:%g:0:%g:0.02" % (f, d), d + 1.4))
for ms, fase in ((10, "zero"), (10, "cresta"), (20, "zero"), (20, "cresta"), (30, "zero"),
                 (60, "zero"), (100, "zero"), (150, "zero"), (200, "zero"), (300, "zero")):
    forme.append(("buco%d_%s" % (ms, fase), "buco:%d:%s" % (ms, fase), 1.3 + ms * 1e-3))
forme.append(("sovra115", "sovra:1.15:0:0.5", 1.0))
for tag, rete in RETI:
    for nome, spec, dur in forme:
        if tag == "nom" and nome in ("buco20_zero", "buco200_zero"):
            continue
        print("buco20 r_%s_%s sorgente %s --rete-forma %s --durata %g%s" % (nome, tag, BASE, spec, dur, rete))
for f in (0.8, 0.7):
    print("accensione r_acc_calo%d_nom sorgente %s --rete-forma calo:%g:0.3:0.5:0.02 --durata 2.5"
          % (round(f * 100), BASE, f))
