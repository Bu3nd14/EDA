#!/usr/bin/env python3
"""L45d2b3b3: the rules of ADR-070 / ADR-071 for the columns AFTER the remedy. Solo stdlib.

Everything that can be is L45d1's (data/2026-10-14/L45d1/script/motore.py and tipi.py), imported, not
copied: the matrix (motore.priorita), the probability classes (motore.classe_p), the thresholds of the
severity (motore.TETTO, motore.OBIETTIVO, motore.db) and the rates (tipi.TIPI). What is new here:
  - g_blocco: L45d1's severity of a block fault (riporto_l45a.py) with today's criterion: since
    ADR-081 P10 has a duration only on the Stax (fixed 2, its load, 150 ms after ADR-086 / ADR-089 /
    ADR-098); the main and fixed 1 have none (they count on the protection downstream). 5 if a part is
    beyond its limits, 4 if the Stax is over 150 ms, then the peak thresholds of ADR-070;
  - priorita_dopo: the matrix, with ADR-071's first exception (the mute relays' coil-to-contact
    insulation at high priority) only where it still applies, at severity 4;
  - p_modo: the mode's FIT from tipi.TIPI, the fraction and the instances, as riporto_l45a.py does;
  - r_proxy: the detectability of a NEW block row, which has no L45a output class: 2 if the jack
    sees more than the ceiling (0,87 V; the block is at a rail and the music breaks), 3 otherwise
    (latent). verifica.py measures how well it reproduces L45a's rule on L45a's own rows.
SABOTA (verifica.py --sabota): the matrix with G4 P1 at high, the objective at 10 mV, the rates x 3.
"""
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L45D1 = os.path.abspath(os.path.join(QUI, "..", "..", "..", "2026-10-14", "L45d1", "script"))
sys.path.insert(0, L45D1)
import motore  # noqa: E402
import tipi  # noqa: E402

TIPI = tipi.TIPI
TETTO_STAX_MS = 150.0          # ADR-086 (L60c2), confirmed by ADR-089 / ADR-098
SABOTA = False


def g_picco(v):
    """ADR-070 on a peak in V: <= 100 uV 1, <= 2 mV 2 (the objective of ADR-046), else 3."""
    ob = 10e-3 if SABOTA else motore.OBIETTIVO
    v = v or 0.0
    return 1 if v <= 100e-6 else 2 if v <= ob else 3


def g_blocco(oltre, stax_ms, picco):
    if oltre:
        return 5
    if stax_ms is not None and stax_ms > TETTO_STAX_MS:
        return 4
    g = g_picco(picco)
    if stax_ms:                # above 0,87 V on the Stax for some ms: audible, inside the criterion
        g = max(g, 3)
    return g


def priorita_dopo(G, P, R, isolamento_mute=False):
    if G == "" or P == "" or R == "":
        return ""
    G, P, R = int(G), int(P), int(R)
    if isolamento_mute and G == 4:
        return "alta"           # ADR-071, 1
    if SABOTA and G == 4 and P == 1:
        return "alta"
    return motore.priorita(G, P, R)


def p_modo(tipo, chiave, n):
    fit, fonte, dist = TIPI[tipo]
    fm = fit * motore.fr(dist, chiave) * n * (3 if SABOTA else 1)
    return fm, motore.classe_p(fm), fonte, fit


def r_proxy(picco):
    return 2 if (picco or 0.0) > motore.TETTO else 3


db = motore.db
num = motore.num
