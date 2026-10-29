#!/usr/bin/env python3
"""L55 (NC-056): la giunzione dei finali, a calcolo, sulle potenze del banco di QUESTA cartella; le
regole di dissipatore.py di L45d2b3b2b2 (ADR-099), con le cifre termiche di ciascun contenitore.

Le potenze: calore_<v>.csv (guasti_finali.py + analizza.py: i corti dei finali e il riposo, il
peggiore sulle cinque posizioni) e run/p7/<v>/tb_mute_corto_regime.csv (P7: il corto all'uscita, il
peggiore sui casi del deck). Aria a 60 C (P7, ADR-021). Solo stdlib, /usr/bin/python3 -I.

  MJE15032 / MJE15033 (TO-220): R_thJC 2,5, nudo 62,5 C/W, Tj max 150 C (onsemi MJE15032/D); Ohmite
    WA-T220-101E 20 C/W a 1 W (la curva del costruttore), 2 C/W d'interfaccia (IPOTESI): 24,5 C/W.
  MJE243G / MJE253G (TO-225): R_thJC 8,34, nudo 83,4 C/W (massimi), Tj max 150 C (onsemi MJE243/D
    Rev. 17); Boyd TV4 21 C/W (la cifra dell'elenco del distributore: la curva del costruttore NON e'
    stata letta, modelli/README.md), 2 C/W d'interfaccia (IPOTESI): 31,34 C/W. La R_thSA che tiene la
    giunzione a 125 C (P7) e a 150 C (massimo assoluto) si stampa accanto.

Uso: dissipatore_l55.py fmje c243 c243m    -> dissipatore.csv
"""
import csv
import os
import sys

L = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TA, P7, TJMAX, RCS = 60.0, 125.0, 150.0, 2.0
TERMICO = {  # variante -> (contenitore, R_thJC, nudo, R_thSA del dissipatore, nome del dissipatore)
    "fmje": ("TO-220 MJE15032/33", 2.5, 62.5, 20.0, "Ohmite WA-T220-101E"),
    "c243": ("TO-225 MJE243G/253G", 8.34, 83.4, 21.0, "Boyd TV4"),
    "c243m": ("TO-225 MJE243G/253G", 8.34, 83.4, 21.0, "Boyd TV4"),
}


def peggiore(v, modo, col):
    p, dove = 0.0, ""
    for r in csv.DictReader(open(os.path.join(L, "calore_%s.csv" % v))):
        if r["modo"] == modo and r.get(col):
            if float(r[col]) > p:
                p, dove = float(r[col]), r["posizione"]
    return p, dove


def p7(v, col):
    f = os.path.join(L, "run", "p7", v, "tb_mute_corto_regime.csv")
    p, dove = 0.0, ""
    for r in csv.DictReader(open(f)):
        x = abs(float(r[col]))
        if x > p:
            p, dove = x, "%s %s dB %s Hz caso %s" % (r["blk"], r["modo_db"], r["f_hz"], r["caso"])
    return p, dove


out = []
print("%-6s %-44s %7s %7s %7s %8s %8s  %s" % ("var", "caso", "P W", "nudo C", "diss. C", "RSA@125", "RSA@150", "dove"))
for v in sys.argv[1:]:
    cont, rjc, nudo_r, rsa, nome_d = TERMICO[v]
    casi = [("NPN Q132 col PNP Q133 in corto",) + peggiore(v, "Q133_ce", "P_q132_W"),
            ("PNP Q133 con l'NPN Q132 in corto",) + peggiore(v, "Q132_ce", "P_q133_W"),
            ("NPN Q132 a riposo",) + peggiore(v, "rif", "P_q132_W"),
            ("PNP Q133 a riposo",) + peggiore(v, "rif", "P_q133_W"),
            ("P7 Q132 (mute o uscita in corto)",) + p7(v, "p_q132"),
            ("P7 Q133 (mute o uscita in corto)",) + p7(v, "p_q133")]
    for caso, p, dove in casi:
        nudo = TA + p * nudo_r
        con = TA + p * (rjc + RCS + rsa)
        r125 = (P7 - TA) / p - rjc - RCS if p else float("inf")
        r150 = (TJMAX - TA) / p - rjc - RCS if p else float("inf")
        out.append({"variante": v, "contenitore": cont, "dissipatore": nome_d, "caso": caso,
                    "P_W": "%.3f" % p, "Tj_senza_C": "%.0f" % nudo, "Tj_con_C": "%.0f" % con,
                    "RthSA_max_a_125C": "%.1f" % r125, "RthSA_max_a_150C": "%.1f" % r150,
                    "limite_P7_C": "%.0f" % P7, "Tj_max_C": "%.0f" % TJMAX, "dove": dove})
        print("%-6s %-44s %7.3f %7.0f %7.0f %8.1f %8.1f  %s" % (v, caso, p, nudo, con, r125, r150, dove))
with open(os.path.join(L, "dissipatore.csv"), "w", newline="") as fo:
    w = csv.DictWriter(fo, fieldnames=list(out[0]))
    w.writeheader()
    w.writerows(out)
