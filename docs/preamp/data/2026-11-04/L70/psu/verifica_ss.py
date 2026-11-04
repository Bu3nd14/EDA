#!/usr/bin/env python3
"""L45d2b2a: the soft-start of the bench against the datasheets' formulas, before its numbers are
used. Stdlib.

Uso: verifica_ss.py            -> prints, writes ../verifica_ss.txt, exits 1 on a failure

The ramps of misura_ss.py (ss_p_ms, ss_m_ms: from the regulator's IN past its UVLO to 99.9 % of the
final value) on the runs whose C_NR is known, against
  - TPS7A4701: t_SS = 100 kOhm x C_NR x ln((15 + 5) / 5)   (SBVS204G eq. 5)
  - TPS7A3301: t_SS = 1.2 ms per nF x C_NR                  (SBVS169D eq. 1)
within 2 %. The run with U501 at 1 uF is NOT a check of eq. 5: U501 is in current limit there
(1.0 A), and the ramp is set by the limit - it is printed, and must be SLOWER than eq. 5.
Two sabotages must make the check fail: C_NR 10 % off, and eq. 5 without its 5 V (ln(15 / 5)).
"""
import csv
import math
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
# run -> (U501's C_NR, U502's C_NR)
CNR = {"oggi/accensione": (10e-6, 10e-6), "oggi/accensione_m10": (10e-6, 10e-6), "n1u/accensione": (10e-6, 1e-6),
       "n1u/accensione_m10": (10e-6, 1e-6), "p4u7_n470n/accensione": (4.7e-6, 470e-9),
       "p4u7_n470n/accensione_m10": (4.7e-6, 470e-9), "p1u_n1u/accensione": (1e-6, 1e-6),
       "p1u_n1u/accensione_m10": (1e-6, 1e-6), "sorgente/accensione": (4.7e-6, 470e-9),
       "sorgente/accensione_m10": (4.7e-6, 470e-9)}


def eq5(c, k=1.0, cinque=5.0):
    return 1e5 * c * k * math.log((15 + cinque) / 5.0) if cinque else 1e5 * c * k * math.log(15 / 5.0)


def eq1(c, k=1.0):
    return 1.2e-3 * c * k / 1e-9


def controlla(righe, k=1.0, cinque=5.0, scrivi=None):
    ko = 0
    for r in righe:
        cp, cm = CNR[r["corsa"]]
        for nome, mis, att in (("U501", r["ss_p_ms"], eq5(cp, k, cinque)), ("U502", r["ss_m_ms"], eq1(cm, k))):
            if not mis:
                continue          # the rail never got to 99.9 % (oggi: 12 s)
            m = float(mis) / 1e3
            limite = nome == "U501" and float(r["u501_imax_A"]) > 0.95
            if limite:
                ok = m > att
                esito = "in limite di corrente: %.4f s > %.4f s dell'eq. 5" % (m, att)
            else:
                ok = abs(m / att - 1) <= 0.02
                esito = "%.4f s contro %.4f s, %+.2f %%" % (m, att, (m / att - 1) * 100)
            ko += not ok
            if scrivi:
                scrivi("%-28s %s %s  %s" % (r["corsa"], nome, "ok" if ok else "FUORI", esito))
    return ko


def main():
    righe = []
    for f in ("accensione.csv", "accensione_sorgente.csv"):
        righe += list(csv.DictReader(open(os.path.join(L, f))))
    out = []
    ko = controlla(righe, scrivi=out.append)
    sab1 = controlla(righe, k=1.1)
    sab2 = controlla(righe, cinque=0)
    out.append("controlli fuori: %d" % ko)
    out.append("sabotaggio C_NR +10 %%: %d fuori (deve essere > 0)" % sab1)
    out.append("sabotaggio eq. 5 senza i 5 V: %d fuori (deve essere > 0)" % sab2)
    testo = "\n".join(out) + "\n"
    open(os.path.join(L, "verifica_ss.txt"), "w").write(testo)
    print(testo, end="")
    sys.exit(1 if ko or not sab1 or not sab2 else 0)


if __name__ == "__main__":
    main()
