#!/usr/bin/env python3
"""L45d2b2a: the regulators' heat at regime with a resistor before each (corri_rpre.sh). Stdlib.

Uso: riassunto_rpre.py <out.csv> RETEDIR...      (RETEDIR = rete/rpre_<ohm>)

From each deck's log, per regime case (m10 / nom / p10): the mean power of U501 and U502 and of
their resistors, the least headroom IN - |OUT|; and the project's rule for actives (REQUIREMENTS
under P7, ADR-021): Tj = 60 C + P x R_thJA <= 125 C, with SBVS204G's 32.5 C/W (the JEDEC board;
TPS7A3301 assumed the same, the same RGW package). From analizza.py's analisi.csv, per mains loss:
the rails' hold (t_p135 / t_m135, t_p106 / t_m106) and trip_after_135 (P9: the jack opens before
the rail leaves 13.5 V, negative is good). A log with an error refuses the directory.
"""
import csv
import os
import re
import sys

RJA = 32.5


def main():
    out, dirs = sys.argv[1], sys.argv[2:]
    righe = []
    for d in dirs:
        log = open(os.path.join(d, "tb_psu_rete.log")).read()
        if re.search(r"error|singular|timestep too small", log, re.I):
            raise SystemExit("RIFIUTATO: %s ha un errore nel log" % d)
        r_ohm = d.rstrip("/").split("rpre_")[-1]
        an = {r["file"]: r for r in csv.DictReader(open(os.path.join(d, "analisi.csv")))}
        caso = None
        mis = {}
        for linea in log.splitlines():
            m = re.match(r"\s*CASO (\S+)", linea)
            if m:
                caso = m.group(1)
                continue
            m = re.match(r"\s*(p_u50[12]_avg|pr_u50[12]_avg|h_u50[12]_min)\s*=\s*([-0-9.eE+]+)", linea)
            if m and caso:
                mis.setdefault(caso, {})[m.group(1)] = float(m.group(2))
        for f in ("m10", "nom", "p10"):
            x = mis["regime_%s" % f]
            a = an["perdita_rete_%s" % f]
            r = {"rpre_ohm": r_ohm, "rete": f}
            for u in ("u501", "u502"):
                p = x["p_%s_avg" % u]
                r["%s_W" % u] = "%.3f" % p
                r["%s_tj_C" % u] = "%.1f" % (60 + p * RJA)
                r["%s_res_W" % u] = "%.3f" % x.get("pr_%s_avg" % u, 0.0)
                r["%s_riserva_V" % u] = "%.3f" % x["h_%s_min" % u]
            for k in ("t_off_ms", "t_p135_ms", "t_m135_ms", "t_p106_ms", "t_m106_ms", "trip_after_135_ms"):
                r[k] = a[k]
            righe.append(r)
            print(" ".join("%s=%s" % kv for kv in r.items()))
    with open(out, "w", newline="") as fo:
        w = csv.DictWriter(fo, fieldnames=list(righe[0].keys()))
        w.writeheader()
        w.writerows(righe)


if __name__ == "__main__":
    main()
