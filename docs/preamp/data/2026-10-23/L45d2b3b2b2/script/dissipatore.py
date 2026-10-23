#!/usr/bin/env python3
"""L45d2b3b2b2: i finali MJE15032 / MJE15033 col dissipatore Ohmite WA-T220-101E (ADR-099), a calcolo
sulle potenze del blocco del SORGENTE. Le cifre e le regole sono quelle di dissipatore.py di
L45d2b3b2a; le potenze vengono da qui (calore_sorg.csv, calore_sorgt60.csv) e da P7 sul sorgente
(p7_sorgente.csv di L45d2b3b2b1). Solo stdlib, /usr/bin/python3 -I.

Uso: dissipatore.py        stampa e scrive dissipatore.csv (con la colonna del banco di L45d2b3b2a)

- R_thJC 2,5 C/W, Tj max 150 C, R_thJA senza dissipatore 62,5 C/W: onsemi MJE15032/D
  (vendor/bjt_npn/onsemi/MJE15032/mje15032-d.pdf);
- dissipatore 20 C/W (la curva del costruttore a 1 W, vendor/heatsink/ohmite/WA-T220-101E/);
- interfaccia case-dissipatore 2 C/W: IPOTESI dichiarata (clip a molla, a secco, senza isolante).
Aria a 60 C (P7, ADR-021).
"""
import csv
import os

L = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.dirname(os.path.dirname(L))
A = os.path.join(DATA, "2026-10-22", "L45d2b3b2a")
B1 = os.path.join(DATA, "2026-10-22", "L45d2b3b2b1")
RJC, RCS, RSA, RJA_NUDO, TA, P7, TJMAX = 2.5, 2.0, 20.0, 62.5, 60.0, 125.0, 150.0


def peggiore(f, modo, col):
    p, dove = 0.0, ""
    for r in csv.DictReader(open(f)):
        if r["modo"] == modo and r.get(col):
            if float(r[col]) > p:
                p, dove = float(r[col]), r["posizione"]
    return p, dove


banco = {r["caso"]: r for r in csv.DictReader(open(os.path.join(A, "dissipatore.csv")))}
casi = [("NPN Q132 col PNP Q133 in corto", "calore_sorg.csv", "Q133_ce", "P_q132_W"),
        ("NPN Q132 col PNP Q133 in corto, dispositivi a 60 C", "calore_sorgt60.csv", "Q133_ce", "P_q132_W"),
        ("PNP Q133 con l'NPN Q132 in corto", "calore_sorg.csv", "Q132_ce", "P_q133_W"),
        ("NPN Q132 a riposo", "calore_sorg.csv", "rif", "P_q132_W"),
        ("PNP Q133 a riposo", "calore_sorg.csv", "rif", "P_q133_W")]
righe = [(nome,) + peggiore(os.path.join(L, f), modo, col) for nome, f, modo, col in casi]
for r in csv.DictReader(open(os.path.join(B1, "p7_sorgente.csv"))):
    if r["colonna"] in ("p_q132", "p_q133"):
        righe.append(("P7 %s (mute o uscita in corto)" % r["colonna"][2:].upper(), float(r["max_W"]), r["dove"]))

out = []
print("%-52s %7s %7s %7s %9s  %s" % ("caso", "P W", "nudo C", "dissip.", "banco C", "dove"))
for nome, p, dove in righe:
    nudo = TA + p * RJA_NUDO
    con = TA + p * (RJC + RCS + RSA)
    b = banco.get(nome, {})
    out.append({"caso": nome, "P_W": "%.3f" % p, "Tj_senza_C": "%.0f" % nudo, "Tj_con_C": "%.0f" % con,
                "banco_P_W": b.get("P_W", ""), "banco_Tj_con_C": b.get("Tj_con_C", ""),
                "limite_P7_C": "%.0f" % P7, "Tj_max_C": "%.0f" % TJMAX, "dove": dove})
    print("%-52s %7.3f %7.0f %7.0f %9s  %s" % (nome, p, nudo, con, b.get("Tj_con_C", ""), dove))
with open(os.path.join(L, "dissipatore.csv"), "w", newline="") as fo:
    w = csv.DictWriter(fo, fieldnames=list(out[0]))
    w.writeheader()
    w.writerows(out)
