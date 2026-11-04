#!/usr/bin/env python3
"""L45d2b2b1: the rete deck of each option of ADR-074 (corri_rete_074.sh) - regime and mains loss at
-10 % / nominal / +10 %. COPIED from L45d2b2a's riassunto_rpre.py, the label from the folder's name,
plus the series diode of --variante uscita. Stdlib.

Uso: riassunto_rete_074.py <out.csv> RETEDIR...      (RETEDIR = rete/<etichetta>)

Per regime case: each regulator's mean power (at its PIN with --variante uscita), its Tj = 60 C +
P x 32.5 C/W (ADR-021, SBVS204G's R_thJA; the TPS7A3301 assumed the same, as L45d2b2a), R550 / R551's
power, the least headroom IN - |OUT pin| (ADR-020 assumes >= 1 V); with the series diode its mean
power and the headroom IN - |rail|. Per mains loss (analizza.py): the rails' hold and P9's
trip_after_135 (negative is good), and the hold of VRELAY (vr_hold_ms, P9 (b) >= 25 ms).
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
        an = {r["file"]: r for r in csv.DictReader(open(os.path.join(d, "analisi.csv")))}
        caso, mis = None, {}
        for linea in log.splitlines():
            m = re.match(r"\s*CASO (\S+)", linea)
            if m:
                caso = m.group(1)
                continue
            m = re.match(r"\s*((?:p|pr|pd)_u50[12]_avg|(?:h|hr)_u50[12]_min)\s*=\s*([-0-9.eE+]+)", linea)
            if m and caso:
                mis.setdefault(caso, {})[m.group(1)] = float(m.group(2))
        for f in ("m10", "nom", "p10"):
            x = mis["regime_%s" % f]
            a = an["perdita_rete_%s" % f]
            r = {"opzione": os.path.basename(d.rstrip("/")), "rete": f}
            for u in ("u501", "u502"):
                p = x["p_%s_avg" % u]
                r["%s_W" % u] = "%.3f" % p
                r["%s_tj_C" % u] = "%.1f" % (60 + p * RJA)
                r["%s_res_W" % u] = "%.3f" % x.get("pr_%s_avg" % u, 0.0)
                r["%s_riserva_V" % u] = "%.3f" % x["h_%s_min" % u]
                r["%s_diodo_W" % u] = "%.3f" % x["pd_%s_avg" % u] if "pd_%s_avg" % u in x else ""
                r["%s_al_rail_V" % u] = "%.3f" % x["hr_%s_min" % u] if "hr_%s_min" % u in x else ""
            for k in ("t_off_ms", "vr_hold_ms", "t_p135_ms", "t_m135_ms", "t_p106_ms", "t_m106_ms",
                      "trip_after_135_ms"):
                r[k] = a.get(k, "")
            righe.append(r)
            print(" ".join("%s=%s" % kv for kv in r.items()))
    with open(out, "w", newline="") as fo:
        w = csv.DictWriter(fo, fieldnames=list(righe[0].keys()))
        w.writeheader()
        w.writerows(righe)


if __name__ == "__main__":
    main()
