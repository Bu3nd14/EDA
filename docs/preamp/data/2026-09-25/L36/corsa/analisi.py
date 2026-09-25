#!/usr/bin/env python3
"""L36: riassume corsa.csv. Uso: analisi.py <corsa.csv> <sintesi.txt>"""
import csv
import sys
from collections import defaultdict


def main(argv):
    rows = list(csv.DictReader(open(argv[1])))
    out = []
    p = out.append
    for r in rows:
        for k in ("L_mH", "gap_ms", "fraz", "irel_mA", "imin_rilascio_mA",
                  "imin_inserimento_mA", "i0_mA", "tcaduta_dopo_NO_K6_us", "R", "vrelay"):
            r[k] = float(r[k])
        for k in ("tiene_al_rilascio", "tiene_all_inserimento"):
            r[k] = r[k] == "True"
    p(f"corse: {len(rows)}; esiti: " +
      ", ".join(f"{e} {sum(r['corsa'] == e for r in rows)}" for e in ("ok", "OPT", "ERR")))
    by = defaultdict(list)
    for r in rows:
        by[r["variante"]].append(r)

    for v in ("ingenua", "progetto"):
        rs = by[v]
        p(f"\n== {v}: {len(rs)} celle")
        p(f"   cade al rilascio del mute:    {sum(not r['tiene_al_rilascio'] for r in rs)}")
        p(f"   cade all'inserimento del mute: {sum(not r['tiene_all_inserimento'] for r in rs)}")
        marg = min(min(r["imin_rilascio_mA"], r["imin_inserimento_mA"]) / r["i0_mA"] for r in rs)
        p(f"   corrente minima / corrente a regime, nel peggiore: {marg:.6f}")
    rs = by["ingenua"]
    p("\n== ingenua: celle che cadono al rilascio, per L (righe) e buco di K6 (colonne),"
      " su 24 (3 R x 4 soglie x 2 VRELAY)")
    gaps = sorted({r["gap_ms"] for r in rs})
    p("   L mH  " + "".join(f"{g:>8g} ms" for g in gaps))
    for L in sorted({r["L_mH"] for r in rs}):
        p(f"   {L:5g} " + "".join(
            f"{sum(not r['tiene_al_rilascio'] for r in rs if r['L_mH'] == L and r['gap_ms'] == g):>11d}"
            for g in gaps))
    p("   per soglia di rilascio (frazione di 5 V / R), su 120 (5 L x 4 buchi x 3 R x 2 VRELAY):")
    for f in sorted({r["fraz"] for r in rs}):
        p(f"   {f:4g}: {sum(not r['tiene_al_rilascio'] for r in rs if r['fraz'] == f)}")

    rs = by["residuo"]
    p("\n== residuo (manopola a 0 dB fuori mute, poi mute inserito): K1 cade dopo"
      " l'apertura del NO di K6 di (solo elettrico, nessun ritardo meccanico accreditato):")
    p(f"   tenuta fuori mute prima dell'inserimento: {sum(r['tiene_al_rilascio'] for r in rs)} su {len(rs)}")
    p("   L mH   min us   max us")
    for L in sorted({r["L_mH"] for r in rs}):
        ts = [r["tcaduta_dopo_NO_K6_us"] for r in rs if r["L_mH"] == L]
        p(f"   {L:5g} {min(ts):8.1f} {max(ts):8.1f}")
    open(argv[2], "w").write("\n".join(out) + "\n")
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
