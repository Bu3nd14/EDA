#!/usr/bin/env python3
"""L67 (NC-055): la sintesi della catena, da catena_<blocco>.csv.

Per blocco, griglia (l56 / volbasso) e uscita (bout = la principale, f1out / f2out = le fisse):
casi giudicati, casi fuori, margine minimo in dB contro il tetto di THD a 20 kHz (0,2 / 2 V), h5 in
su peggiore dove giudicata, e il caso del margine minimo.

Uso: /usr/bin/python3 -I sintesi_catena.py <blocco>...  -> ../sintesi_catena.csv
"""
import csv
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
LOTTO = os.path.dirname(QUI)
out = []
for b in sys.argv[1:]:
    righe = list(csv.DictReader(open(os.path.join(LOTTO, "catena_%s.csv" % b))))
    for g in ("l56", "volbasso"):
        for u in ("bout", "f1out", "f2out"):
            sel = [r for r in righe if r["griglia"] == g and r["uscita"] == u]
            if not sel:
                continue
            conm = [r for r in sel if r["margine_dB"]]
            peg = min(conm, key=lambda r: float(r["margine_dB"])) if conm else None
            h5 = [float(r["h5su_db"]) for r in sel if r["livello"] == "lo" and r["freq"] != "1000"]
            out.append({"blocco": b, "griglia": g, "uscita": u, "casi": len(sel),
                        "fuori": sum(r["verdetto"] != "dentro" for r in sel),
                        "margine_min_dB": peg["margine_dB"] if peg else "",
                        "h5su_peggiore_dB": "%.1f" % max(h5) if h5 else "",
                        "caso_peggiore": ("%s %s modo=%s vol=%s rs=%s THD=%s %%" % (
                            peg["freq"], peg["livello"], peg["modo"], peg["vol"], peg["rs"], peg["thd_pct"])) if peg else ""})
p = os.path.join(LOTTO, "sintesi_catena.csv")
with open(p, "w", newline="") as fh:
    w = csv.DictWriter(fh, list(out[0]))
    w.writeheader()
    w.writerows(out)
for r in out:
    print("%(blocco)-17s %(griglia)-8s %(uscita)-6s %(fuori)2s/%(casi)-2s margine %(margine_min_dB)6s dB  h5+ %(h5su_peggiore_dB)s  %(caso_peggiore)s" % r)
print("-> %s" % p)
