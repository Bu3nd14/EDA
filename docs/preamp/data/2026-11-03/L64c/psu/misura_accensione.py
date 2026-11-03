#!/usr/bin/env python3
"""L45d2b1: i rail all'accensione sul banco dell'alimentatore - quando ciascuno passa 1 V, 5 V,
13,5 V e 13,8 V, lo scarto fra i due, e quando i jack si chiudono (MUTE_CMD a RLY_RET). Stdlib.
Serve a dimensionare l'inibizione all'accensione del rivelatore (circuits/preamp/dc_detector.py).

Uso: misura_accensione.py SEQDIR/accensione
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analizza_riv import leggi  # noqa: E402


def primo(t, v, cond):
    for i in range(len(t)):
        if cond(v[i]):
            return t[i]
    return None


def main(d):
    g = open(os.path.join(d, "punto_fisso.txt")).read().strip()
    c = leggi(os.path.join(d, "tb_psu_seq_accensione_g%s_out.txt" % g))
    t = c["time"]
    vp, vm = c["v(vplus)"], c["v(vminus)"]
    t0 = primo(t, c["v(mains_req)"], lambda x: x > 2.5)
    print("MAINS_REQ alto a %.4f s: i tempi sotto sono da li'" % t0)
    for s in (1.0, 5.0, 13.5, 13.8):
        a = primo(t, vp, lambda x: x > s)
        b = primo(t, vm, lambda x: x < -s)
        print("|rail| > %5.1f V:  + %7.1f ms   - %7.1f ms   scarto %+6.1f ms" % (
            s, (a - t0) * 1e3, (b - t0) * 1e3, (b - a) * 1e3))
    tj = None
    for i in range(len(t)):
        if t[i] > t0 and c["v(vrelay)"][i] - c["v(mute_cmd)"][i] > 6.0:
            tj = t[i]
            break
    print("jack: MUTE_CMD eccitato a %.1f ms" % ((tj - t0) * 1e3) if tj else "jack: mai")
    a1 = primo(t, vp, lambda x: x > 1.0)
    print("dal + a 1 V (il rivelatore comincia a vivere) ai jack: %.1f ms" % ((tj - a1) * 1e3) if tj else "")


if __name__ == "__main__":
    main(sys.argv[1])
