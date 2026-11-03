#!/usr/bin/env python3
"""L54b3a: the runs on the source with ADR-104 (D535 / D536 / D541 BAS416, R571 1M), all with the
makers' latch transistors and BAT54 (--ritenuta / --bat54 costruttore):
  n_     L54b2's safety list (lista_finale.txt's fint_ lines, labels fint_ -> n_);
  b2_    the bounces (lista_rimbalzi.py's cases, clean and with the trains);
  f_     the fast edges: a pulse 10 us wide in series with U512 (V5) or U503 (VRELAY_REG), +-1 and
         +-5 V, 10 ns edges, C554 = C555 = 1 fF / 100p / 330p / 1n / 2.2n; 1 us edges at 1 nF; in
         music (rilascio, the pulse at TE + 0.3 s);
  num_   the numeric check: one case per family with --passo-max 5u.
/usr/bin/python3 -I lista_nuovo.py <L54b2/lista_finale.txt> > ../lista_nuovo.txt"""
import sys

MAKER = "--ritenuta costruttore --bat54 costruttore"
BASE = "--n2n7002 ds --tss 3.0 --comparatore tarato --sonde-piu " + MAKER
for r in open(sys.argv[1]):
    p = r.split()
    if p and p[1].startswith("fint_"):
        p[1] = "n_" + p[1][len("fint_"):]
        print(" ".join(p) + " " + MAKER)
CASI = (("accensione", "front"), ("spegnimento", "front"), ("rilascio", "sw3"),
        ("inserimento", "sw3"))
for caso, q in CASI:
    print("%s b2_pulito sorgente %s" % (caso, BASE))
    for ms in (1, 3, 5):
        for seme in (1, 2, 3):
            print("%s b2_%dms_s%d sorgente %s --rimbalzo %s:%d:%d" % (caso, ms, seme, BASE, q, ms, seme))
CBE = (("0", "1f"), ("100p", "100p"), ("330p", "330p"), ("1n", "1n"), ("2n2", "2.2n"))
for ref, nodo in (("U512", "v5"), ("U503", "vr")):
    for amp in (1, -1, 5, -5):
        for tag, c in CBE:
            print("rilascio f_%s_%+d_c%s sorgente %s --disturbo %s:%g:1e-8:1e-5:0.3 --valore C554=%s,C555=%s"
                  % (nodo, amp, tag, BASE, ref, amp, c, c))
        print("rilascio f_%s_%+d_c1n_1us sorgente %s --disturbo %s:%g:1e-6:1e-5:0.3"
              % (nodo, amp, BASE, ref, amp))
print("buco20 num_calo85 sorgente %s --rete-forma calo:0.85:0:0.1:0.02 --durata 1.5 --rete 0.9 --passo-max 5u" % BASE)
print("spegnimento num_rimb sorgente %s --rimbalzo front:5:1 --passo-max 5u" % BASE)
print("rilascio num_fronte sorgente %s --disturbo U512:5:1e-8:1e-5:0.3 --passo-max 5u" % BASE)
