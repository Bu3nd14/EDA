#!/usr/bin/env python3
"""L54b3a: the bounce list (README, «I criteri»): the four switch transitions clean, then with a
bounce train of 1 / 3 / 5 ms, three seeds each, at mains 0 %.
/usr/bin/python3 -I lista_rimbalzi.py > ../lista_rimbalzi.txt"""
BASE = "--n2n7002 ds --tss 3.0 --comparatore tarato --sonde-piu"
CASI = (("accensione", "front"), ("spegnimento", "front"), ("rilascio", "sw3"),
        ("inserimento", "sw3"))
for caso, q in CASI:
    print("%s b_pulito sorgente %s" % (caso, BASE))
for caso, q in CASI:
    for ms in (1, 3, 5):
        for seme in (1, 2, 3):
            print("%s b_%dms_s%d sorgente %s --rimbalzo %s:%d:%d" % (caso, ms, seme, BASE, q, ms, seme))
