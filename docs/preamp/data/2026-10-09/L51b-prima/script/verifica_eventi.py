#!/usr/bin/env python3
"""L41c: a small figure must be proven to contain its event. For each case and
its reference, from <caso>_l41c_stati.dat (wrdata: time, value pairs):
the largest |case - reference| on MAIN_A (the block's output, BEFORE the jack
relay) and on MAINC (the capacitor side of the jack contact), after t_ins.
If the gain moved, MAIN_A must show it even when the jack reads nothing.

L47c2b2: COPIED from L41c's (data/2026-09-26/L41c/script/), which stays as it
was. The state columns changed in L47c2b1 (the cells are gone: no xls.xs,
xlp.xs, dep). L41c's copy would skip EVERY row of today's files (its width
test) and print 0 for every case - a small figure with no event, silently.
This copy has today's columns and REFUSES a file with no row of that width.

Solo stdlib. /usr/bin/python3 verifica_eventi.py <corse_dir> <ponte_dir> <caso> [...]
"""
import bisect
import json
import os
import sys

COLS = ["ina", "vplus", "vminus", "main_a", "mainc", "fixc1", "fixc2"]


def leggi(path, nomi):
    t, cols = [], {n: [] for n in nomi}
    for r in open(path):
        v = r.split()
        if len(v) != 2 * len(COLS):
            continue
        t.append(float(v[0]))
        for n in nomi:
            cols[n].append(float(v[2 * COLS.index(n) + 1]))
    if not t:
        raise SystemExit("%s: nessuna riga da %d colonne - le colonne degli stati non sono queste"
                         % (path, 2 * len(COLS)))
    return t, cols


def main(argv):
    corse, ponte = argv[1], argv[2]
    for caso in argv[3:]:
        j = json.load(open(os.path.join(ponte, caso + ".json")))
        ti = j["t_ins"]
        te, ce = leggi(os.path.join(corse, "%s_l41c_stati.dat" % caso), ("main_a", "mainc"))
        tr, cr = leggi(os.path.join(corse, "rif_%s_l41c_stati.dat" % caso), ("main_a", "mainc"))
        out = []
        for n in ("main_a", "mainc"):
            best, tb = 0.0, None
            for k in range(len(te)):
                if te[k] < ti:
                    continue
                i = min(bisect.bisect_left(tr, te[k]), len(tr) - 1)
                d = abs(ce[n][k] - cr[n][i])
                if d > best:
                    best, tb = d, te[k]
            out.append("%s max|ev-rif| %.4g V a %.5f s" % (n, best, tb if tb else -1))
        print("%-16s t_jack %s t_gain %s | %s" % (caso, j["t_jack"], j["t_gain"], " | ".join(out)))


if __name__ == "__main__":
    main(sys.argv)
