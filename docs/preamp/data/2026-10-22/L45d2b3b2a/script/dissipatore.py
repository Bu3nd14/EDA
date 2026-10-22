#!/usr/bin/env python3
"""L45d2b3b2a: i finali MJE15032 / MJE15033 col dissipatore Ohmite WA-T220-101E, a calcolo sulle
potenze simulate. Solo stdlib, /usr/bin/python3 -I.

Uso: dissipatore.py        stampa e scrive dissipatore.csv

Le cifre:
- R_thJC 2,5 C/W, Tj max 150 C, R_thJA senza dissipatore 62,5 C/W: onsemi MJE15032/D
  (vendor/bjt_npn/onsemi/MJE15032/mje15032-d.pdf);
- dissipatore: Ohmite W Series (WA-T220-101E), Rs-a 12 C/W in convezione naturale a 10 W; 1,0 W per
  20 C di salita (scheda DigiKey): a 1-2 W si usa 20 C/W, la cifra peggiore della curva;
- interfaccia case-dissipatore 2 C/W: IPOTESI dichiarata (clip a molla, a secco, senza isolante;
  con un grasso ~0,5-1 C/W). Il dissipatore e' al potenziale del collettore (il tab).
Le potenze: i due corti dei finali sul banco del calore con la variante rv2 (calore_rv2.csv,
calore_rv2t60.csv), P7 (p7_rv2.csv), il riposo (calore_rv2.csv, rif). Aria a 60 C (P7, ADR-021).
"""
import csv
import os

L = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RJC, RCS, RSA, RJA_NUDO, TA, P7, TJMAX = 2.5, 2.0, 20.0, 62.5, 60.0, 125.0, 150.0


def peggiore(f, modo, col):
    p, dove = 0.0, ""
    for r in csv.DictReader(open(os.path.join(L, f))):
        if r["modo"] == modo and r.get(col):
            if float(r[col]) > p:
                p, dove = float(r[col]), r["posizione"]
    return p, dove


casi = [("NPN Q132 col PNP Q133 in corto", "calore_rv2.csv", "Q133_ce", "P_q132_W"),
        ("NPN Q132 col PNP Q133 in corto, dispositivi a 60 C", "calore_rv2t60.csv", "Q133_ce", "P_q132_W"),
        ("PNP Q133 con l'NPN Q132 in corto", "calore_rv2.csv", "Q132_ce", "P_q133_W"),
        ("NPN Q132 a riposo", "calore_rv2.csv", "rif", "P_q132_W"),
        ("PNP Q133 a riposo", "calore_rv2.csv", "rif", "P_q133_W")]
righe = []
for nome, f, modo, col in casi:
    p, dove = peggiore(f, modo, col)
    righe.append((nome, p, dove))
for r in csv.DictReader(open(os.path.join(L, "p7_rv2.csv"))):
    if r["colonna"] in ("p_q132", "p_q133"):
        righe.append(("P7 %s (mute o uscita in corto)" % r["colonna"][2:].upper(), float(r["max_W"]), r["dove"]))

out = []
print("%-52s %7s %9s %9s  %s" % ("caso", "P W", "nudo C", "dissip. C", "dove"))
for nome, p, dove in righe:
    nudo = TA + p * RJA_NUDO
    con = TA + p * (RJC + RCS + RSA)
    out.append({"caso": nome, "P_W": "%.3f" % p, "Tj_senza_C": "%.0f" % nudo, "Tj_con_C": "%.0f" % con,
                "limite_P7_C": "%.0f" % P7, "Tj_max_C": "%.0f" % TJMAX, "dove": dove})
    print("%-52s %7.3f %9.0f %9.0f  %s" % (nome, p, nudo, con, dove))
with open(os.path.join(L, "dissipatore.csv"), "w", newline="") as fo:
    w = csv.DictWriter(fo, fieldnames=list(out[0]))
    w.writeheader()
    w.writerows(out)
