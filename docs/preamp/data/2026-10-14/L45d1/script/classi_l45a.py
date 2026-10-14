#!/usr/bin/env python3
"""L45d1: the ADR-070 classes of L45a's table (the faults of the gain block), read by
riporto_l45a.py. Data only (solo stdlib). The rates are tipi.py's.

The part types come from circuits/preamp/gain_block.py: C104, C116, C141, C142, C145 electrolytic
(FP_ELCO / CP_Radial), C105, C139, C140 ceramic, C124 and C137 C0G (gain_block.py: "MUST be
C0G/NP0"), D102 / D103 1N4148, JQ110A/B the two halves of the LSK489, Q121A/B the two halves of the
LS352, Q122 / Q125 DZT5401 / DZT5551 (SOT-223, ADR-068), Q132 / Q133 MJE15032 / MJE15033.
"""
from tipi import TIPI  # noqa: F401  (riporto_l45a reads K.TIPI)

ELETTROLITICI = {"C104", "C116", "C141", "C142", "C145"}


def tipo_di(ref):
    if ref.startswith("JQ"):
        return "JFET"
    if ref in ("Q122", "Q125"):
        return "BJT_V"
    if ref in ("Q132", "Q133"):
        return "BJT_P"
    if ref.startswith("Q"):
        return "BJT_S"
    if ref.startswith("C"):
        return "C_el" if ref in ELETTROLITICI else "C_cer"
    if ref.startswith("D"):
        return "D_seg"
    if ref.startswith("R"):
        return "R"
    return None


# the mode's key in TIPI, from the suffix of L45a's mode name (modi.csv)
CHIAVE = {"ce": "ce", "be": "be", "ae": "ae",          # BJT: C-E short, B-E short, emitter open
          "ds": "ds", "gs": "gs", "as": "as",          # JFET: D-S short, G-S short, source open
          "cc": "corto", "ap": "aperto"}               # R, C, D

# the Vbe multiplier's parts: their heat is NC-062's (opened after L45a, blocking for G1)
VBE = {"Q127", "R128", "R129"}

RIMEDI = {
    "rivelatore": "un rivelatore di continua sulle uscite dei blocchi che apra il mute: col rivelatore "
                  "ideale (L45b) il tempo sopra 0,87 V scende a 0,2-10,1 ms, dentro P10; il picco non "
                  "cambia (14,8-14,9 V, L45a)",
    "calore": "il secondo guasto per calore: limitare la corrente del ramo o scegliere parti che la "
              "reggano (il dispositivo d'uscita e' di L55)",
    "calore_vbe": "il moltiplicatore di Vbe: NC-062, bloccante per G1, col suo lotto",
    "dentro": "nessuno: dentro P10 (il colpo, se c'e', dura meno di 100 ms)",
    "nessuno": "nessuno: il guasto non ha effetto al jack",
}
