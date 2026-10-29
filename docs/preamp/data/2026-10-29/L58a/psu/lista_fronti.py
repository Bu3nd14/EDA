#!/usr/bin/env python3
"""L54b3a: the fast edges injected at the parts' terminals (--disturbo nodo:...), after the first
form (in series with the regulator) did not reach the node (README, «I fronti veloci»):
  V5:          every pull-up of the timer and the supervisors on V5 (R503 ... R581), R576 (the
               latch's anode, VRELAY_EN) and R581 (its trigger, AT_F) among them;
  VRELAY_REG:  R522 (the supervisor's divider), K501's coil, R540, C531 (not the bulk C523 / C524).
A pulse 10 us wide, +-1 / +-5 V, 10 ns edges, C554 = C555 = 1 fF / 100p / 330p / 1n / 2.2n; 1 us edges
at 1 nF; in music (rilascio, at TE + 0.3 s). Makers' transistors and BAT54.
/usr/bin/python3 -I lista_fronti.py > ../lista_fronti.txt"""
BASE = ("--n2n7002 ds --tss 3.0 --comparatore tarato --sonde-piu --ritenuta costruttore"
        " --bat54 costruttore")
V5 = "+".join("RR%d" % r for r in (503, 512, 517, 518, 524, 537, 569, 570, 571, 572, 573, 575, 576,
                                     579, 581))
VR = "RR522+RK501_coil+RR540+CC531"
CBE = (("0", "1f"), ("100p", "100p"), ("330p", "330p"), ("1n", "1n"), ("2n2", "2.2n"))
for nodo, net, els in (("v5", "v5", V5), ("vr", "vrelay_reg", VR)):
    for amp in (1, -1, 5, -5):
        for tag, c in CBE:
            print("rilascio g_%s_%+d_c%s sorgente %s --disturbo nodo:%s:%s:%g:1e-8:1e-5:0.3 "
                  "--valore C554=%s,C555=%s" % (nodo, amp, tag, BASE, net, els, amp, c, c))
        print("rilascio g_%s_%+d_c1n_1us sorgente %s --disturbo nodo:%s:%s:%g:1e-6:1e-5:0.3"
              % (nodo, amp, BASE, net, els, amp))
print("rilascio num_fronte2 sorgente %s --disturbo nodo:v5:%s:5:1e-8:1e-5:0.3 --valore C554=1f,C555=1f"
      " --passo-max 5u" % (BASE, V5))
