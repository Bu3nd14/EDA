#!/usr/bin/env python3
"""L51b: the peak at the jack of the supply's faults, three ways side by side.

  L47c2b2       the load before, the audio board before (L47c2b2/tabella.csv);
  L51b-prima    the load before, TODAY's audio board (L48a's selector, L48b's C_T):
                its bridge is L47c2b2's byte for byte (confronta_prima.py), so the step
                from L47c2b2 is the audio board alone;
  L51b          today's load and today's audio board: the step from L51b-prima is the
                load alone (the rails of today, the selector's coil, gear for U503).

    /usr/bin/python3 scomposizione.py      # -> ../scomposizione.csv, and on stdout
"""
import csv
import math
import os

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
DATA = os.path.dirname(os.path.dirname(L))
FONTI = (("l47c2b2", os.path.join(DATA, "2026-10-06", "L47c2b2", "tabella.csv")),
         ("prima", os.path.join(DATA, "2026-10-09", "L51b-prima", "tabella.csv")),
         ("oggi", os.path.join(L, "tabella.csv")))

tab = {}
for k, p in FONTI:
    with open(p) as f:
        tab[k] = {r["caso"]: r for r in csv.DictReader(f)}
casi = list(tab["oggi"])
if any(list(tab[k]) != casi for k, _ in FONTI):
    raise SystemExit("RIFIUTATO: le tre tabelle non hanno gli stessi casi nello stesso ordine")
righe = []
for c in casi:
    v = {k: float(tab[k][c]["picco_V"]) for k, _ in FONTI}
    righe.append({"caso": c, "criterio": tab["oggi"][c]["criterio"],
                  "picco_V_l47c2b2": tab["l47c2b2"][c]["picco_V"],
                  "picco_V_prima": tab["prima"][c]["picco_V"],
                  "picco_V_oggi": tab["oggi"][c]["picco_V"],
                  "scheda_audio_dB": "%.2f" % (20 * math.log10(v["prima"] / v["l47c2b2"])),
                  "carico_dB": "%.2f" % (20 * math.log10(v["oggi"] / v["prima"])),
                  "esito_oggi": tab["oggi"][c]["esito"]})
out = os.path.join(L, "scomposizione.csv")
with open(out, "w", newline="") as f:
    w = csv.DictWriter(f, list(righe[0]))
    w.writeheader()
    w.writerows(righe)
print(open(out).read(), end="")
