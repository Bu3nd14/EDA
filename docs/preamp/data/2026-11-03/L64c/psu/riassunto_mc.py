#!/usr/bin/env python3
"""L54b3b: the summary of a Monte Carlo analysis (analizza_mc.py's csv), per case.

For each case: the nominal row (<prefisso>nominale/<caso>, toll_nominale.json), and over the
samples the min / max of each margin, and the samples whose VERDICTS differ from the nominal's
(n_giu, n_su, n_k501, mus_end, k501_end, ritenuta, C2, C3).
/usr/bin/python3 -I riassunto_mc.py <an.csv> <prefisso>
"""
import csv
import sys

MARGINI = ["d_perm_ms", "dmus_ms", "k_perm_ms", "t_mus_ms", "t_k501_ms", "t_jack_ms", "t_gain_ms",
           "t_pg_ms", "t_arm_ms", "arm_pg_ms", "bn_max0", "bn_max", "dvp_mv", "dvm_mv", "t_fpgt_ms"]
VERDETTI = ["C2", "C3", "n_giu", "n_su", "n_k501", "mus_end", "k501_end", "ritenuta"]

fa, pre = sys.argv[1], sys.argv[2]
per = {}
for r in csv.DictReader(open(fa)):
    et, c = r["caso"].split("/")
    per.setdefault(c, {})[et[len(pre):]] = r
for c in sorted(per):
    rs = per[c]
    nom = rs.get("nominale")
    camp = {k: v for k, v in rs.items() if k != "nominale"}
    print("== %s: %d campioni%s" % (c, len(camp), "" if nom else " (MANCA il nominale)"))
    for m in MARGINI:
        xs = [(float(v[m]), k) for k, v in camp.items() if v.get(m, "") != ""]
        if not xs:
            continue
        lo, hi = min(xs), max(xs)
        print("  %-10s nominale %-9s min %-9g (%s) max %-9g (%s)  [%d]"
              % (m, nom.get(m, "") if nom else "", lo[0], lo[1], hi[0], hi[1], len(xs)))
    if nom:
        diversi = [(k, [x for x in VERDETTI if v.get(x) != nom.get(x)]) for k, v in sorted(camp.items())]
        diversi = [(k, d) for k, d in diversi if d]
        print("  verdetti diversi dal nominale: %d %s" % (len(diversi), diversi[:8]))
