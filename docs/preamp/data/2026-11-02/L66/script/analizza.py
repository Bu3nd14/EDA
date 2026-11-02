#!/usr/bin/env python3
"""L45d2b3b2b2: analizza_calore.py di L45d2b3b1 puntato a QUESTA cartella, con la R_thJA di Q193 (il
limite del VAS, MMBT5401 in SOT-23, 403 C/W: Q168 sul banco di L45d2b3b2a). Solo stdlib,
/usr/bin/python3 -I.

Uso: analizza.py <variante> [...]    -> calore_<v>.csv, analisi_jack_<v>.csv
"""
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
DATA = os.path.abspath(os.path.join(L, "..", ".."))
sys.path.insert(0, os.path.join(DATA, "2026-10-22", "L45d2b3b1", "script"))
import analizza_calore as ac   # noqa: E402

ac.L = L
ac.a62.RTH.update({"q193": 403})

if __name__ == "__main__":
    for v in sys.argv[1:]:
        ac.main(["analizza", v])
