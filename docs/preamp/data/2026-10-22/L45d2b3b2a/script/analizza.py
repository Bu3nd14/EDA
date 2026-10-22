#!/usr/bin/env python3
"""L45d2b3b2a: il jack e il calore delle corse di una variante. Solo stdlib, /usr/bin/python3 -I.

Uso: analizza.py <variante> [<variante> ...]
     legge run/<variante>_<pos>/<modo>/, scrive analisi_jack_<variante>.csv e calore_<variante>.csv

E' analizza_calore.py di L45d2b3b1 com'e' (che a sua volta chiama analizza_tr.py di L45a e le regole
di analizza_L62b.py), con la cartella puntata qui. Le R_thJA delle parti nuove delle varianti:
i PNP / NPN in SOT-23 sono 417 K/W come q160 / q163 di L62b (R_TH_NUOVI sotto); le resistenze nuove
contro 0,25 W come ogni 0207.
"""
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
DATA = os.path.abspath(os.path.join(L, "..", ".."))
sys.path.insert(0, os.path.join(DATA, "2026-10-22", "L45d2b3b1", "script"))
import analizza_calore as ac   # noqa: E402

ac.L = L
# le parti nuove delle varianti (genera.py, RIMEDI): Q168 il limite del VAS, MMBT5401 in SOT-23
R_TH_NUOVI = {"q168": 403}
ac.a62.RTH.update(R_TH_NUOVI)

if __name__ == "__main__":
    for v in sys.argv[1:]:
        ac.main(["analizza", v])
