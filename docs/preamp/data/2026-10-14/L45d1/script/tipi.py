#!/usr/bin/env python3
"""L45d1: the failure rates by part type for the carry-over of L45a, L45b and L45c1 to ADR-070.
Data only (solo stdlib).

L45c2's types are READ from L45c2 (script/classi_l45c2.py), not copied: the same rule, the same
numbers. The new types follow the same rule, the user's choice of 2026-10-14 («Stima dichiarata»,
confirmed at the start of L45d1, «No, stima dichiarata»):
  - integrated circuits: the SN 29500-2 reference rate the maker's functional-safety report gives
    for the part or its nearest sibling;
  - passive and discrete parts: an ORDER OF MAGNITUDE declared as an estimate (STIMA), at the hot
    chassis (60 C air, ADR-021);
  - the split among the modes: MIL-HDBK-338B Table 7.8-1 (../../L45c2/tassi/), or an IPOTESI where
    the table has no row for the mode, declared here and in tassi/fonti.md.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "L45c2", "script"))
import classi_l45c2  # noqa: E402

TIPI = dict(classi_l45c2.TIPI)

# Bipolar (338B): short .73, open .27. IPOTESI: the short split evenly between C-E and B-E (338B
# does not say which junction); the open is the emitter open of L45a's bench (ae)
_BJT = {"ce": 0.365, "be": 0.365, "ae": 0.27}
TIPI.update({
    "BJT_S":  (2.0, "STIMA (bipolare di segnale, SOT-23 o mezzo SOIC doppio)", _BJT),
    "BJT_V":  (5.0, "STIMA (bipolare SOT-223 del VAS e del suo carico, ~84 C di giunzione, L56)", _BJT),
    "BJT_P":  (10.0, "STIMA (finale in classe A, MJE15032 / MJE15033, il piu' caldo del blocco)", _BJT),
    # FET (338B), as L45c2's FET: the D-S short (.51 less the gate's .10) and output low .22 = ds;
    # open .05 and output high .05 = the source open (as); G-S .05 (IPOTESI, as L45c2)
    "JFET":   (3.0, "STIMA (meta' dell'LSK489)",
               {"ds": 0.41 + 0.22, "as": 0.05 + 0.05, "gs": 0.05, "gd": 0.05, "deriva": 0.17}),
    "C_film": (1.0, "STIMA (condensatore a film plastico)",
               {"aperto": 0.42, "corto": 0.40, "valore": 0.18}),
    # Relay (338B): fails to trip .55, spurious trip .26, short .19. IPOTESI: fails to trip split as
    # K501's (coil open .25, a pole welded .27, both .03); spurious trip = a contact that opens by
    # itself (an open pole, a bounce, a bistable that changes over); the short split into the coil
    # .14 and the coil-to-contact insulation .05
    "RELE_S": (10.0, "STIMA (rele' di segnale G6K, poche manovre al giorno)",
               {"bobina_aperta": 0.25, "un_polo_saldato": 0.27, "due_poli_saldati": 0.03,
                "spurio": 0.26, "bobina_corto": 0.14, "isolamento": 0.05}),
    "LED":    (1.0, "STIMA (LED di segnalazione)", {"aperto": 0.70, "corto": 0.30}),
    "ROT":    (10.0, "STIMA (commutatore rotativo o a levetta del frontale)",
               {"uscita_errata": 0.53, "contatto": 0.47}),
    # TI SFFS612 (TPS748A-Q1): SN 29500-2 table 4, "LDO > 1 W", 100 FIT at 90 C. U501 / U502 drop
    # ~5 V at ~0,3 A, 1,5 W: the full figure (U503 / U504 of L45c2 were halved for < 1 W). U501 is
    # the TPS7A4701 of U503 (SBVS204G); U502 the TPS7A3301 (SBVS169D), its negative sibling
    "LDO_P":  (100.0, "TI SFFS612 (SN 29500-2 tab. 4: LDO > 1 W, 100 FIT a 90 C)",
               dict(classi_l45c2.TIPI["LDO"][2])),
})
