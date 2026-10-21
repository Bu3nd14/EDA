#!/usr/bin/env python3
"""L45d2b2c: P7 cell by cell, without and with D158 / D159 (run/tb_<rail>/ against run/tb_cbe_<rail>/):
the cells where Q133's power, the 47 ohm's and the output peak move most. Solo stdlib.
/usr/bin/python3 -I confronta_cbe.py <rail> [n]
"""
import csv
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
LOTTO = os.path.dirname(QUI)
CHIAVE = ("blk", "modo_db", "f_hz", "vin_pk", "k_att", "caso")
COL = ("p_q132", "p_q133", "p_r134", "p_r135", "p_rsep", "voutpk", "icmax_q132", "icmin_q133", "p_q122", "p_q125")


def leggi(d):
    p = os.path.join(LOTTO, "run", d, "tb_mute_corto", "tb_mute_corto_regime.csv")
    return dict((tuple(r[k] for k in CHIAVE), r) for r in csv.DictReader(open(p)))


def main():
    rail = sys.argv[1]
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    a, b = leggi("tb_" + rail), leggi("tb_cbe_" + rail)
    assert set(a) == set(b), "celle diverse"
    for col in ("p_q133", "p_rsep"):
        print("== le %d celle dove %s cambia di piu' (senza -> con i diodi)" % (n, col))
        d = sorted(a, key=lambda k: -abs(float(b[k][col]) - float(a[k][col])))
        for k in d[:n]:
            print("  " + ",".join(k) + "  " + "  ".join("%s %.4g->%.4g" % (c, float(a[k][c]), float(b[k][c]))
                                                      for c in COL))


if __name__ == "__main__":
    main()
