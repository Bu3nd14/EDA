#!/usr/bin/env python3
"""L45d2b3b3: fmea_dopo.md from fmea_dopo.csv (dopo.py). Solo stdlib, /usr/bin/python3 -I.

The count before / after by priority, the rows by destination (stato), then the high and medium rows
after the remedy, with the source of each figure. The CSV has every row and every column.
"""
import csv
import os
from collections import Counter, OrderedDict

L = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
righe = list(csv.DictReader(open(os.path.join(L, "fmea_dopo.csv"))))
PR = ["alta", "media", "bassa", "esclusa"]


def dest(r):
    s = r["stato"]
    for k in ("NC-072", "NC-073", "NC-075", "accettata", "alla diagnosi", "a G2", "escluso", "invariata"):
        if s.startswith(k):
            return {"alla diagnosi": "alla diagnosi (L58)", "a G2": "a G2", "invariata": "invariata (riga di L45)",
                    "escluso": "esclusa (ADR-085)"}.get(k, k)
    return "nel circuito (rimedio costruito, misurata)" if not r["effetto_dopo"].startswith("CALCOLO") \
        else "nel circuito (calcolo)"


def tab(rs, campi, titoli):
    o = ["| " + " | ".join(titoli) + " |", "|" + "---|" * len(titoli)]
    for r in rs:
        o.append("| " + " | ".join(str(r[c]).replace("|", "/") for c in campi) + " |")
    return o


md = ["# NC-042 — la FMEA della scheda audio dopo i rimedi (L45d2b3b3)", "",
      "Generata da `script/sintesi_dopo.py` da `fmea_dopo.csv` (`script/dopo.py`; le regole in "
      "`script/regole.py`, provate da `script/verifica.py` sulle colonne pubblicate di L45d1 e L45d2a). "
      "Le colonne «dopo» sono quelle di ADR-070 sul circuito di oggi; la fonte di ogni cifra e' in "
      "`fonte_dopo` nel CSV. Il picco e' al jack peggiore fra principale e fissa 1 (V e dB SPL di picco a 1 m); "
      "la Stax e' il tempo sopra 0,87 V col suo carico (P10, al piu' 150 ms: ADR-086 / ADR-089 / ADR-098).", ""]

md += ["## Quante righe, per priorita', prima e dopo il rimedio", ""]
gruppi = OrderedDict()
for r in righe:
    g = r["lotto"] if r["gruppo"] == "tabelle di L45" else "nuove: " + r["lotto"]
    gruppi.setdefault(g, []).append(r)
rows = []
for g, rs in gruppi.items():
    a, b = Counter(r["priorita_prima"] for r in rs), Counter(r["priorita_dopo"] for r in rs)
    rows.append(dict(g=g, n=len(rs), **{"a" + p: a.get(p, 0) for p in PR}, **{"b" + p: b.get(p, 0) for p in PR}))
a = Counter(r["priorita_prima"] for r in righe)
b = Counter(r["priorita_dopo"] for r in righe)
rows.append(dict(g="**tutte**", n=len(righe), **{"a" + p: a.get(p, 0) for p in PR}, **{"b" + p: b.get(p, 0) for p in PR}))
md += tab(rows, ["g", "n", "aalta", "amedia", "abassa", "balta", "bmedia", "bbassa", "besclusa"],
          ["Lotto", "righe", "alta prima", "media prima", "bassa prima", "**alta dopo**", "**media dopo**",
           "bassa dopo", "esclusa"])
md += ["", "Le righe nuove non hanno un «prima»: sono le parti aggiunte dopo L45 (il blocco: ADR-086, 087, 090, "
       "095, 097, 099; l'alimentatore: ADR-091…094), misurate, e i modi che nessun banco ha corso, a calcolo.", ""]

md += ["## Dove va ogni riga", ""]
dd = OrderedDict()
for r in righe:
    dd.setdefault(dest(r), []).append(r)
rows = []
for k, rs in sorted(dd.items(), key=lambda kv: -len([r for r in kv[1] if r["priorita_dopo"] == "alta"])):
    c = Counter(r["priorita_dopo"] for r in rs)
    rows.append(dict(k=k, n=len(rs), alta=c.get("alta", 0), media=c.get("media", 0), bassa=c.get("bassa", 0)))
md += tab(rows, ["k", "n", "alta", "media", "bassa"], ["Destinazione", "righe", "alta", "media", "bassa"])
md += [""]

CAMPI = ["lotto", "ref", "funzione", "modo", "G_prima", "priorita_prima", "G_dopo", "P_dopo", "R_dopo",
         "picco_dopo_dB", "stax_ms", "Tj_max_C", "stato", "effetto_dopo"]
TIT = ["Lotto", "Parte", "Funzione", "Modo", "G prima", "priorita' prima", "G", "P", "R", "dB SPL", "Stax ms",
       "Tj C", "Stato", "Effetto"]
ORD = {"alta": 0, "media": 1}
for p in ("alta", "media"):
    rs = sorted([r for r in righe if r["priorita_dopo"] == p],
                key=lambda r: (dest(r), -int(r["G_dopo"] or 0), r["lotto"], r["ref"]))
    md += ["## Priorita' %s dopo il rimedio (%d)" % (p, len(rs)), ""]
    md += tab(rs, CAMPI, TIT)
    md += [""]

open(os.path.join(L, "fmea_dopo.md"), "w").write("\n".join(md) + "\n")
print("fmea_dopo.md: %d righe; dopo %s" % (len(righe), dict(b)))
print("destinazioni:", {k: len(v) for k, v in dd.items()})
