#!/usr/bin/env python3
"""L60d2: il peggiore di ogni uscita sulle grandezze di V2 col tetto di 100 uV, letto da analisi.csv
e non dal verdetto (che tiene solo l'uscita peggiore di ogni cella: limitations #63). Le grandezze:
A senza segnale (A_ins, A_rel), B1, B2 senza segnale, B2g; col metodo (picco_V) e, se c'e', col
metodo di prima (picco_puntuale_V). Solo stdlib.

Uso: peggiore_per_uscita.py ANALISI.csv MANIFESTO.csv
"""
import csv
import sys

righe = list(csv.DictReader(open(sys.argv[1])))
# Come verdetto.py di L47c2b1: le corse di spegnimento (off_*) sono escluse (lo spegnimento vero e'
# quello morbido dell'alimentatore, L30 / L41c), e di ogni evento contano le grandezze della colonna
# `conta` del manifesto; B1 viene dai riferimenti «sempre in mute» e conta sempre.
man = {r["cella"]: r for r in csv.DictReader(open(sys.argv[2]))}


def conta(r):
    g, amp = r["grandezza"], float(r["amp"] or 0)
    m = man.get(r["cella"])
    if m is None or m["file"].startswith("off_"):
        return False
    if g == "B1":
        return True
    if g not in [x for x in m.get("conta", "").split(";") if x]:
        return False
    if g in ("A_ins", "A_rel", "B2"):
        return amp == 0
    return g == "B2g"


for u in ("MAINJACK", "FIXJACK1", "FIXJACK2"):
    sub = [r for r in righe if r["uscita"] == u and conta(r) and r["picco_V"]]
    sopra = [r for r in sub if float(r["picco_V"]) > 100e-6]
    print("%s: %d righe col tetto, %d sopra 100 uV" % (u, len(sub), len(sopra)))
    for g in ("A_ins", "A_rel", "B1", "B2", "B2g"):
        gg = [r for r in sub if r["grandezza"] == g]
        if not gg:
            continue
        w = max(gg, key=lambda r: float(r["picco_V"]))
        p = w.get("picco_puntuale_V") or ""
        print("   %-6s %10.4g uV  %-26s  (metodo di prima %s)"
              % (g, float(w["picco_V"]) * 1e6, w["cella"],
                 "%.4g uV" % (float(p) * 1e6) if p else "-"))
