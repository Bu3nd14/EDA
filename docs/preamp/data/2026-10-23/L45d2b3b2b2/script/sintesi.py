#!/usr/bin/env python3
"""L45d2b3b2b2: sintesi.py di L45d2b3b2a puntato a QUESTA cartella. La corrente in eccesso sui rail si
misura contro il riferimento sano del blocco di prima di ADR-099 (calore_oggi.csv di L45d2b3b2a), come
per rv2: i numeri restano confrontabili. Solo stdlib, /usr/bin/python3 -I.

Uso: sintesi.py <variante> [...]    -> sintesi_<v>.csv
"""
import csv
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
DATA = os.path.abspath(os.path.join(L, "..", ".."))
A = os.path.join(DATA, "2026-10-22", "L45d2b3b2a")
sys.path.insert(0, os.path.join(A, "script"))
import sintesi as s2a   # noqa: E402

s2a.L = L


def rif_oggi():
    out = {}
    for r in csv.DictReader(open(os.path.join(A, "calore_oggi.csv"))):
        if r["modo"] == "rif":
            out[r["posizione"]] = (s2a.f(r["I_rail_piu_mA"]), s2a.f(r["I_rail_meno_mA"]))
    return out


s2a.rif_oggi = rif_oggi

if __name__ == "__main__":
    for v in sys.argv[1:]:
        out = s2a.sintesi(v)
        n = [o for o in out if o["verdetto"] != "entro" and o["modo"] != "rif"]
        print("%s: %d modi, %d oltre i limiti" % (v, len(out) - 1, len(n)))
        for o in out:
            print("  %-10s %5s C %-16s dI+ %7s dI- %7s mA  %s %s  [%s]" % (
                o["modo"], o["Tj_max_60_C"], o["Tj_max_disp"], o["dI_rail_piu_mA"], o["dI_rail_meno_mA"],
                o["oltre_i_limiti_60C"], o["diodi_oltre_60C"], o["verdetto"]))
