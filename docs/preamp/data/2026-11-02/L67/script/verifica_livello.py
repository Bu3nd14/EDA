#!/usr/bin/env python3
"""L67 (NC-055, ADR-112): la catena giudicata con la regola «ogni blocco al suo livello».

ADR-112 (decisione dell'utente in L67): sulla catena la THD a 20 kHz si giudica al livello a cui
ogni istanza lavora. Il tetto scala col livello fra 0,2 e 2 V RMS,
    tetto(L) = 0,001 % x L / 0,2 V,
che ridà i due punti di ADR-055 (0,001 % a 0,2 V, 0,01 % a 2 V): la seconda armonica, che domina,
cresce col livello. Alla principale la cifra della catena (la somma di A e B) si confronta col
tetto del livello piu' alto lungo il percorso: max(livello del blocco A, livello alla principale).
Le fisse escono al livello del blocco A, quindi la regola per loro non cambia niente. La h5 in su
resta a -140 dB (gia' <= -149,7 ovunque).

Uso: /usr/bin/python3 -I verifica_livello.py <blocco>... -> ../verifica_livello.csv
"""
import csv
import math
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
LOTTO = os.path.dirname(QUI)
LIV_MAIN = {"lo": 0.2, "hi": 2.0}
out = []
for b in sys.argv[1:]:
    for r in csv.DictReader(open(os.path.join(LOTTO, "catena_%s.csv" % b))):
        if r["freq"] != "20000":
            continue
        L = max(float(r["livello_A_V"]), LIV_MAIN[r["livello"]])
        if L > 2.0 * 1.001:
            raise SystemExit("%s: livello %.3g V oltre i 2 V di ADR-055 (%s)" % (b, L, r))
        tetto = 0.001 * L / 0.2
        thd = float(r["thd_pct"])
        m = 20 * math.log10(tetto / thd)
        out.append({"blocco": b, "griglia": r["griglia"], "uscita": r["uscita"], "livello": r["livello"],
                    "modo": r["modo"], "vol": r["vol"], "rs": r["rs"], "livello_giudizio_V": "%.3g" % L,
                    "thd_pct": r["thd_pct"], "tetto_livello_pct": "%.4g" % tetto, "margine_dB": "%.1f" % m,
                    "verdetto_v4": r["verdetto"], "verdetto_adr112": "dentro" if m >= 0 else "FUORI"})
p = os.path.join(LOTTO, "verifica_livello.csv")
with open(p, "w", newline="") as fh:
    w = csv.DictWriter(fh, list(out[0]))
    w.writeheader()
    w.writerows(out)
for b in sys.argv[1:]:
    for g in ("l56", "volbasso"):
        rr = [r for r in out if r["blocco"] == b and r["griglia"] == g]
        peg = min(rr, key=lambda r: float(r["margine_dB"]))
        print("%-17s %-8s %2d fuori su %2d (prima %2d); margine minimo %5s dB: %s %s modo=%s vol=%s rs=%s THD %s %% contro %s %%"
              % (b, g, sum(r["verdetto_adr112"] != "dentro" for r in rr), len(rr),
                 sum(r["verdetto_v4"] != "dentro" for r in rr), peg["margine_dB"], peg["uscita"], peg["livello"],
                 peg["modo"], peg["vol"], peg["rs"], peg["thd_pct"], peg["tetto_livello_pct"]))
print("-> %s" % p)
