#!/usr/bin/env python3
"""L46b (copiato da L46a): V1 nel gruppo B di I_DSS (ADR-031) per variante e istanza.

Minimo di pm_deg sulle righe b_min / b_tip / b_max (gruppo B) e, accanto, sulle
righe a_come_e (il modello com'e' pubblicato: deve stare vicino al V1 della
stessa variante, #29). La riga `xa` di tb_idss_loop (il vecchio segnaposto) non
conta. Celle vuote: rifiuto (#26).

Uso: /usr/bin/python3 riassumi_idss.py <variante>...  -> idss.csv
"""
import csv
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L46A = os.path.dirname(QUI)
RUN = os.path.join(L46A, "run")
FILE = [("B", "tb_idss_loop", "tb_idss_loop_margini.csv"),
        ("A", "tb_idss_blockA", "tb_idss_blockA.csv"),
        ("buf", "tb_idss_buffer", "tb_idss_buffer.csv")]
GRUPPO_B = ("b_min", "b_tip", "b_max")

out = []
for v in sys.argv[1:]:
    riga = {"variante": v}
    for ist, deck, f in FILE:
        r = list(csv.DictReader(open(os.path.join(RUN, v, deck, f))))
        if not r or any(x["pm_deg"] == "" for x in r):
            sys.exit("%s %s: tabella vuota o celle vuote" % (v, deck))
        b = [float(x["pm_deg"]) for x in r if x["var"] in GRUPPO_B]
        a = [float(x["pm_deg"]) for x in r if x["var"] == "a_come_e"]
        if len({x["var"] for x in r if x["var"] in GRUPPO_B}) != 3:
            sys.exit("%s %s: manca una variante del gruppo B" % (v, deck))
        riga[ist + "_grB_min"] = "%.2f" % min(b)
        riga[ist + "_grB_max"] = "%.2f" % max(b)
        riga[ist + "_pubbl_min"] = "%.2f" % min(a)
    out.append(riga)
col = ["variante"] + ["%s_%s" % (i, q) for i, _, _ in FILE for q in ("grB_min", "grB_max", "pubbl_min")]
with open(os.path.join(L46A, "idss.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, col)
    w.writeheader()
    w.writerows(out)
for r in out:
    print(" ".join("%s=%s" % (k, r[k]) for k in col))
