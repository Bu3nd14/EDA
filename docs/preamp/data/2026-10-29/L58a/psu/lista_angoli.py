#!/usr/bin/env python3
"""L54b3b: the run list of the worst corners (prepara_angoli.sh's toll files) at their cases.

/usr/bin/python3 -I lista_angoli.py <cartella mc25> <ipotesi c0g|x7r> [temperature, default 0,25,60]
Each corner on the case its criterion is measured on (README, "I criteri"); the ones where the
mains matter at the three mains (--rete 0.9 / 1.1: suffix _m10 / _p10); the cold start's latch base
also with the comparators alive only from 2.2 V (tarato22, suffix _22); the mains loss at -10 % with
the corner that makes the jack latest. The diodes' maximum leakage at the temperature (--perdita).
"""
import os
import sys

PERDITE = {
    0: "D538:5.5e-9,D535:2.9e-9,D536:2.9e-9,D541:2.9e-9,D533:0.4e-6,D534:2.9e-9,D537:0.4e-6",
    25: "D538:25e-9,D535:5e-9,D536:5e-9,D541:5e-9,D533:2e-6,D534:5e-9,D537:2e-6",
    60: "D538:210e-9,D535:11e-9,D536:11e-9,D541:11e-9,D533:19e-6,D534:11e-9,D537:19e-6",
}
BASE = "--n2n7002 ds --tss 3.0 --ritenuta costruttore --bat54 costruttore --sonde-piu"
# corner name -> [(case, mains factors, comparator)]
TRE = (None, 0.9, 1.1)
CASI = {
    "dmus": [("buco20", TRE, "tarato")],
    "dperm_sp": [("spegnimento_l", (None,), "tarato")],
    "dperm_gu": [("guasto", (None,), "tarato")],
    "kperm_sp": [("spegnimento_l", (None,), "tarato")],
    "kperm_gu": [("guasto", (None,), "tarato")],
    "arm_acc": [("accensione", TRE, "tarato")],
    "arm_fr": [("fredda", TRE, "tarato")],
    "bn_fr": [("fredda", TRE, "tarato"), ("fredda", TRE, "tarato22")],
    "arm_tardi": [("accensione_u501", (None,), "tarato"), ("accensione", (None,), "tarato")],
    "jack_tardi": [("perdita", (None, 0.9), "tarato")],
}
m, ip = sys.argv[1], sys.argv[2]
temps = [int(x) for x in (sys.argv[3] if len(sys.argv) > 3 else "0,25,60").split(",")]
# [prefisso]: before the label (v_: the runs on the source after ADR-105)
pre = sys.argv[4] if len(sys.argv) > 4 else ""
for t in temps:
    for nome, usi in CASI.items():
        f = os.path.join(m, "toll_%s_t%d_%s.json" % (ip, t, nome))
        assert os.path.exists(f), f
        for caso, reti, cmp_ in usi:
            for r in reti:
                et = "%s%s_t%d_%s%s%s" % (pre, ip, t, nome, "" if r is None else "_m10" if r < 1 else "_p10",
                                        "_22" if cmp_ == "tarato22" else "")
                print("%s %s sorgente %s --comparatore %s --temp %d --perdita %s%s --toll %s"
                      % (caso, et, BASE, cmp_, t, PERDITE[t],
                         "" if r is None else " --rete %g" % r, f))
