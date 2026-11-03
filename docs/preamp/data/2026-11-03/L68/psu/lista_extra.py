#!/usr/bin/env python3
"""L54b3b: the extra runs - the latch's hFE groups A / C (both transistors) at 25 and 60 C on the
cases that arm, trip or must not trip it, and the numeric check (the 60 C buco20 corner at 5 us).
/usr/bin/python3 -I lista_extra.py <cartella mc25>
"""
import os
import sys

PERDITE = {
    25: "D538:25e-9,D535:5e-9,D536:5e-9,D541:5e-9,D533:2e-6,D534:5e-9,D537:2e-6",
    60: "D538:210e-9,D535:11e-9,D536:11e-9,D541:11e-9,D533:19e-6,D534:11e-9,D537:19e-6",
}
m = sys.argv[1]
B = "--n2n7002 ds --tss 3.0 --comparatore tarato --bat54 costruttore --sonde-piu"
for g in ("A", "C"):
    for t in (25, 60):
        for caso in ("accensione", "fredda", "guasto", "ritenuta_frontale", "accensione_u501"):
            print("%s v_hfe%s_t%d sorgente %s --ritenuta costruttore%s --temp %d --perdita %s"
                  % (caso, g, t, B, g, t, PERDITE[t]))
# with tarato22: the cold start's latch base, hFE A / C at 60 C
for g in ("A", "C"):
    print("fredda v_hfe%s_t60_22 sorgente --n2n7002 ds --tss 3.0 --comparatore tarato22 --bat54 costruttore "
          "--sonde-piu --ritenuta costruttore%s --temp 60 --perdita %s" % (g, g, PERDITE[60]))
print("buco20 v_num_c0g_t60_dmus sorgente --n2n7002 ds --tss 3.0 --comparatore tarato --ritenuta costruttore "
      "--bat54 costruttore --sonde-piu --temp 60 --perdita %s --toll %s --passo-max 5u"
      % (PERDITE[60], os.path.join(m, "toll_c0g_t60_dmus.json")))
