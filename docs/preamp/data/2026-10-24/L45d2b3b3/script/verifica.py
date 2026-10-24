#!/usr/bin/env python3
"""L45d2b3b3: the rules of regole.py on a KNOWN CASE, before any new number. Solo stdlib.

    verifica.py [--sabota]

From the published rows of L45d1 / L45d2a, with their own G, P, R, the rules must give back the
published columns:
  1. the priority of the 469 rows of L45d1/fmea_sintesi.csv (the matrix of ADR-070);
  2. the priority after ADR-071 of the 173 rows of L45d2a/decisioni.csv;
  3. the severity of L45a's 112 block rows (fmea_blocco_adr070.csv) from the peak, the verdict and
     the heat, through g_blocco (an old P10 verdict 'FUORI' passed as a Stax over the ceiling);
  4. the FIT and the probability class of every row of the four tables that has a type and a
     fraction (L45a, L45b, L45c1 adr070 and L45c2's fmea_comando.csv).
Then it prints, without judging, how often r_proxy gives L45a's detectability on L45a's rows.
--sabota: the matrix and the objective changed (regole.SABOTA): the same checks must FAIL (exit 1).
"""
import csv
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
import regole  # noqa: E402

DATA = os.path.abspath(os.path.join(QUI, "..", "..", ".."))
D1 = os.path.join(DATA, "2026-10-14", "L45d1")
regole.SABOTA = "--sabota" in sys.argv


def rd(*p):
    return list(csv.DictReader(open(os.path.join(DATA, *p))))


diverse = {}


def conta(nome, ok):
    diverse.setdefault(nome, [0, 0])
    diverse[nome][0] += 1
    if not ok:
        diverse[nome][1] += 1


# 1
for r in rd("2026-10-14", "L45d1", "fmea_sintesi.csv"):
    conta("1 priorita' (fmea_sintesi)", regole.priorita_dopo(r["G"], r["P"], r["R"]) == r["priorita"])
# 2
for r in rd("2026-10-14", "L45d2a", "decisioni.csv"):
    iso = r["scelta"] == "6" and r["ref"].startswith(("K2", "K3"))
    conta("2 priorita' dopo ADR-071 (decisioni)",
          regole.priorita_dopo(r["G"], r["P"], r["R"], iso) == r["priorita_adr071"])
# 3
blocco = rd("2026-10-14", "L45d1", "fmea_blocco_adr070.csv")
for r in blocco:
    stax = 151.0 if r["verdetto"].startswith("FUORI") else None
    conta("3 gravita' del blocco (L45a)",
          regole.g_blocco(r["calore"].strip(), stax, float(r["picco_V"])) == int(r["G"]))
# 4
TAB = [("2026-10-14", "L45d1", "fmea_blocco_adr070.csv"), ("2026-10-14", "L45d1", "fmea_controlli_adr070.csv"),
       ("2026-10-14", "L45d1", "fmea_rail_adr070.csv"), ("2026-10-14", "L45c2", "fmea_comando.csv")]
def fit_di(r):
    """'chiave f [x n]', L45b's 'TIPO chiave f [x n]', terms summed with ' + '."""
    fm = 0.0
    for termine in r["frazione"].split(" + "):
        tok = termine.split()
        tipo = tok.pop(0) if tok[0] in regole.TIPI else r["tipo"]
        n = int(tok[-1]) if len(tok) >= 4 and tok[-2] == "x" else 1
        fm += regole.p_modo(tipo, tok[0], n)[0]
    return fm


for t in TAB:
    for r in rd(*t):
        if not r.get("frazione") or not r.get("P"):
            continue
        fm = fit_di(r)
        conta("4 FIT e probabilita' (%s)" % t[-1],
              "%.3g" % fm == r["fit_modo"] and regole.motore.classe_p(fm) == int(r["P"]))

for k in sorted(diverse):
    print("%-48s %4d righe, %3d diverse" % (k, diverse[k][0], diverse[k][1]))
acc = sum(1 for r in blocco if regole.r_proxy(float(r["picco_V"])) == int(r["R"]))
print("r_proxy contro la rilevabilita' di L45a: %d su %d uguali (informativo)" % (acc, len(blocco)))
tot = sum(v[1] for v in diverse.values())
if regole.SABOTA:
    print("SABOTATO: %d diverse (devono essere > 0)" % tot)
    sys.exit(1 if tot else 0)
if tot:
    sys.exit("RIFIUTATO: %d righe diverse dal pubblicato" % tot)
print("tutte uguali")
