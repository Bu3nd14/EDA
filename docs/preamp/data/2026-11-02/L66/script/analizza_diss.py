#!/usr/bin/env python3
"""L66: analizza.py coi finali COL DISSIPATORE (ADR-099): R_thJA di Q132 / Q133 24,5 C/W = 2,5
(giunzione-case, onsemi) + 2 (interfaccia, IPOTESI di ADR-099) + 20 (WA-T220-101E a 1 W), invece dei
62,5 del TO-220 nudo che analizza.py usa (le cifre di dissipatore.py di L45d2b3b2b2). E' lo stato del
progetto: la Tj massima di ogni riga e' quella che va nella FMEA. Solo stdlib, /usr/bin/python3 -I.

Uso: analizza_diss.py dopo    -> calore_dopo.csv, analisi_jack_dopo.csv
     (solo la variante «dopo», il sorgente dopo ADR-111: le altre restano a 62,5, come i loro casi noti)
"""
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
DATA = os.path.abspath(os.path.join(L, "..", ".."))
sys.path.insert(0, os.path.join(DATA, "2026-10-22", "L45d2b3b1", "script"))
import analizza_calore as ac   # noqa: E402

ac.L = L
ac.a62.RTH.update({"q193": 403, "q132": 24.5, "q133": 24.5})

if __name__ == "__main__":
    if sys.argv[1:] != ["dopo"]:
        sys.exit(__doc__)
    ac.main(["analizza", "dopo"])
