#!/usr/bin/env python3
"""L29e: le celle peggiori di L29d2 rifatte sul deck versionato dal sorgente, contro il banco.

Uso: tabella_sorgente.py <verdetto.csv di L29e> <verdetto.csv di L29d2 (matrice)> <uscita.csv>

Per ogni riga di verdetto di L29e (cella, grandezza) cerca la stessa riga nel banco. Criterio,
dichiarato prima di leggere i numeri: stesso esito, e scarto relativo <= 1 % sulle grandezze
sopra 1 nV (A, B2) o sopra 0,01 dB (S); sotto quelle soglie lo scarto e' rumore numerico (il
controfattuale di L29d2 dava gli scarti del 13 % solo sotto 1 nV). Esce col numero di righe che
non lo rispettano, piu' le righe senza corrispondente.
"""
import csv
import sys

TOLL = 0.01


def leggi(p):
    with open(p) as f:
        return {(r["cella"], r["grandezza"]): r for r in csv.DictReader(f)}


src, banco = leggi(sys.argv[1]), leggi(sys.argv[2])
righe, bad = [], 0
for k in sorted(src):
    s = src[k]
    b = banco.get(k)
    if b is None:
        righe.append([k[0], k[1], s["uscita"], s["picco"], "-", "-", s["esito"], "-", "SENZA BANCO"])
        bad += 1
        continue
    ps, pb = float(s["picco"]), float(b["picco"])
    piccolo = 0.01 if k[1].startswith("S") else 1e-9
    rel = abs(ps - pb) / abs(pb) if pb else (0.0 if ps == 0 else float("inf"))
    ok = s["esito"] == b["esito"] and (rel <= TOLL or max(abs(ps), abs(pb)) < piccolo)
    bad += not ok
    righe.append([k[0], k[1], s["uscita"], s["picco"], b["picco"], "%.3g" % rel,
                  s["esito"], b["esito"], "ok" if ok else "DIVERSO"])
with open(sys.argv[3], "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["cella", "grandezza", "uscita", "sorgente", "banco_L29d2", "scarto_rel",
                "esito_sorgente", "esito_banco", "confronto"])
    w.writerows(righe)
for r in righe:
    print("%-26s %-6s %-9s %12s %12s %9s %-6s %-6s %s" % tuple(r))
print("righe: %d, fuori criterio: %d" % (len(righe), bad))
sys.exit(bad)
