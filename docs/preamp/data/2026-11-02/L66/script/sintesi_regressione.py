#!/usr/bin/env python3
"""L66: la sintesi della regressione del blocco sano per variante (regressione/misure_<v>.csv di
confronta_regressione.py). Solo stdlib, /usr/bin/python3 -I.

Uso: sintesi_regressione.py <v> [...]   -> sintesi_regressione.csv, e stampa

Per ogni variante: il margine di fase minimo (le misure pmarg*), la variazione relativa massima delle
misure con |oggi| >= 1e-6 (fuori dalle correnti di dispersione e dai residui numerici), e le tre misure
che cambiano di piu' in relativo, ciascuna col suo deck.
"""
import csv
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def main(vv):
    out = []
    for v in vv:
        rr = list(csv.DictReader(open(os.path.join(L, "regressione", "misure_%s.csv" % v))))
        pm = [(num(r["oggi"]), num(r[v]), r["deck"], r["misura"]) for r in rr
              if r["misura"].startswith("pmarg") and num(r["oggi"]) is not None and num(r[v]) is not None]
        m0 = min(p[0] for p in pm)
        m1 = min(p[1] for p in pm)
        dpm = max(abs(p[1] - p[0]) for p in pm)
        grandi = [(abs(num(r[v]) - num(r["oggi"])) / abs(num(r["oggi"])), r["deck"], r["misura"], r["oggi"], r[v])
                  for r in rr if num(r["oggi"]) is not None and num(r[v]) is not None and abs(num(r["oggi"])) >= 1e-6]
        grandi.sort(reverse=True)
        riga = {"variante": v, "misure": len(rr), "pmarg_min_oggi": "%.2f" % m0, "pmarg_min_var": "%.2f" % m1,
                "pmarg_delta_max": "%.3f" % dpm, "rel_max": "%.3g" % grandi[0][0],
                "top3": " | ".join("%s %s %s->%s (%.2g)" % (d, m, a, b, x) for x, d, m, a, b in grandi[:3])}
        out.append(riga)
        print(riga)
    with open(os.path.join(L, "sintesi_regressione.csv"), "w", newline="") as fo:
        w = csv.DictWriter(fo, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)


if __name__ == "__main__":
    main(sys.argv[1:])
