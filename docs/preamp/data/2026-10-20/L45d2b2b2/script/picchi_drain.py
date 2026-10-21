#!/usr/bin/env python3
"""L45d2b2b2: the drains' highest voltage over a whole run (the clamps at the coils' release) against
the 2N7002's 60 V, for each label given. Solo stdlib.

    picchi_drain.py <seq/etichetta> [...]          (every case with a punto_fisso.txt)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analizza_075 import A  # noqa: E402

for seq in sys.argv[1:]:
    for c in sorted(os.listdir(seq)):
        d = os.path.join(seq, c)
        if not os.path.exists(os.path.join(d, "punto_fisso.txt")):
            continue
        g = int(open(os.path.join(d, "punto_fisso.txt")).read())
        S = A.leggi(os.path.join(d, "tb_psu_seq_%s_g%d_out.txt" % (c, g)))
        mx = {n: max(S[n]) for n in ("v(mute_cmd)", "v(permit_cmd)", "v(mains_coil)", "v(q503_rk)") if n in S}
        print("%-12s %-22s %s" % (os.path.basename(seq), c, "  ".join("%s %.2f V" % kv for kv in mx.items())))
