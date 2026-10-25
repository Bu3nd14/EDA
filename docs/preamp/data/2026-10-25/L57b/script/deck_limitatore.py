#!/usr/bin/env python3
"""L57b: mette il limitatore d'ingresso generato (spice/preamp/input_limiter.subckt, ADR-101) nei
quattro deck canonici che modellano l'ingresso del blocco A, fra il contatto del selettore e AIN.

Ogni sostituzione deve cadere esattamente una volta (altrimenti AssertionError, nessun file scritto).
Il contatto del selettore e la sua capacita' (CSEL, i contatti e il cablaggio) vanno sul nodo dei COM,
SELCOM; il limitatore da SELCOM ad AIN; i due riferimenti dai rail.

Uso: /usr/bin/python3 deck_limitatore.py        (una volta: un deck gia' modificato fa AssertionError)
"""
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", "..", "..", "..", ".."))
TB = os.path.join(ROOT, "spice", "preamp", "tb")

INC_ANCHOR = ".include @REPO@/spice/preamp/gain_block.subckt\n"
INC = INC_ANCHOR + """* L57b (ADR-101, NC-059): block A's input limiter - 1 kOhm in series and a BAV199 diode pair
* to two LM4040 5.0 V shunts at +/-5 V - generated from the source by
* circuits/preamp/input_limiter.py (INLIM per channel, INREF once). The BAV199 is
* models/diodes/bav199_fit.lib, a DECLARED FIT of its datasheet (capacitance from fig. 5,
* leakage the 1N4148's, an upper bound): no Nexperia model could be obtained. The LM4040 is
* TI's model, adapted for ngspice (models/voltage_reference/lm4040_5v0_ngspice.lib).
.include @REPO@/models/diodes/bav199_fit.lib
.include @REPO@/models/voltage_reference/lm4040_5v0_ngspice.lib
.include @REPO@/spice/preamp/input_limiter.subckt
"""
LIM = ("* L57b (ADR-101): the limiter between the selector's COM node and block A's input\n"
       "XLIM SELCOM AIN VLIM_P VLIM_M INLIM\n"
       "XREF VLIM_P VLIM_M VPLUS VMINUS INREF\n")

DECK = {
    "tb_e3_e5.cir": [("RKSEL SEL AIN 0.1\nCSEL  AIN 0 1f\n",
                      "RKSEL SEL SELCOM 0.1\nCSEL  SELCOM 0 1f\n" + LIM)],
    "tb_trim.cir": [("RKSEL SEL AIN 0.1\nCSEL  AIN 0 1f\n",
                     "RKSEL SEL SELCOM 0.1\nCSEL  SELCOM 0 1f\n" + LIM)],
    "tb_f1_selettore.cir": [("SWA  SELA AIN CTLA 0 swk\nCKA  SELA AIN 15p\n",
                             "SWA  SELA SELCOM CTLA 0 swk\nCKA  SELA SELCOM 15p\n"),
                            ("SWB  SELB AIN CTLB 0 swk\nCKB  SELB AIN 15p\n",
                             "SWB  SELB SELCOM CTLB 0 swk\nCKB  SELB SELCOM 15p\n"),
                            ("CSEL AIN 0 68p\n", "CSEL SELCOM 0 68p\n" + LIM)],
    "tb_loop_blockA.cir": [("RSRCA VSRCN IN 1m\n",
                            "RSRCA VSRCN SELCOM 1m\n"
                            + LIM.replace("SELCOM AIN", "SELCOM IN"))],
}

out = {}
for name, subs in DECK.items():
    p = os.path.join(TB, name)
    t = open(p).read()
    for old, new in [(INC_ANCHOR, INC)] + subs:
        assert t.count(old) == 1, (name, old, t.count(old))
        t = t.replace(old, new)
    out[p] = t
for p, t in out.items():
    open(p, "w").write(t)
    print("modificato", os.path.relpath(p, ROOT))
