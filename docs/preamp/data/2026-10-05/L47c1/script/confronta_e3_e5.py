#!/usr/bin/env python3
"""L47c1: tb_e3_e5 (senza celle, ADR-062) contro tb_e3_e5_ldr di L47b2b1 (con le celle).

E5: ogni riga di tb_e3_e5_e5.csv contro la riga "nessuna" (serie a 1 mohm, la derivazione
spenta a 25 M) e contro le righe con la serie a 99,9 / 115,5 ohm del deck vecchio, stessa
posizione / modo / attenuatore / sorgente. E3: il minimo vero, cioe' z20k (limitations #45:
lo zmin di allora saltava i 20 kHz), contro lo stato di gioco del deck vecchio.
Uso: /usr/bin/python3 confronta_e3_e5.py
"""
import csv
import os

QUI = os.path.dirname(os.path.abspath(__file__))
LOTTO = os.path.dirname(QUI)
NUOVO = os.path.join(LOTTO, "regressione", "dopo", "tb_e3_e5")
VECCHIO = os.path.join(LOTTO, "..", "..", "2026-10-03", "L47b2b1", "regressione", "dopo",
                       "tb_e3_e5_ldr")

e5n = list(csv.DictReader(open(os.path.join(NUOVO, "tb_e3_e5_e5.csv"))))
e5v = list(csv.DictReader(open(os.path.join(VECCHIO, "tb_e3_e5_ldr_e5.csv"))))
old = {(r["ldr"], r["pos"], r["mode"], r["att"], r["rsrc"]): float(r["onoise_uv"]) for r in e5v}
mx_nessuna, peggiore = 0.0, (0.0, None)
for r in e5n:
    k = (r["pos"], r["mode"], r["att"], r["rsrc"])
    v = float(r["onoise_uv"])
    mx_nessuna = max(mx_nessuna, abs(v - old[("nessuna",) + k]) / old[("nessuna",) + k])
    if v > peggiore[0]:
        peggiore = (v, k)
peggiore_old = max(old.values())
print("E5 senza celle: peggiore %.4f uV a %s (limite 9,90)" % peggiore)
print("E5 contro la riga 'nessuna' di L47b2b1: massima differenza relativa %.2e" % mx_nessuna)
print("E5 con le celle (L47b2b1, la serie a 115,5 ohm): peggiore %.4f uV" % peggiore_old)

e3n = list(csv.DictReader(open(os.path.join(NUOVO, "tb_e3_e5_e3.csv"))))
e3v = [r for r in csv.DictReader(open(os.path.join(VECCHIO, "tb_e3_e5_ldr_e3.csv")))
       if r["stato"] == "gioco"]
print("E3 senza celle: minimo vero %.1f kOhm (zmin %.1f)"
      % (min(float(r["z20k_ohm"]) for r in e3n) / 1e3,
         min(float(r["zmin_ohm"]) for r in e3n) / 1e3))
print("E3 con le celle, stato di gioco (L47b2b1): zmin riportato %.1f kOhm, minimo vero "
      "(z20k) %.1f kOhm" % (min(float(r["zmin_ohm"]) for r in e3v) / 1e3,
                            min(float(r["z20k_ohm"]) for r in e3v) / 1e3))
