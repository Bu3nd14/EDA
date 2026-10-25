#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
input_limiter.py - the protection of block A's input: 1 kOhm in series and a
diode pair to two shunt references at +/-5 V (ADR-101, L57b).

Fase 2 DRAFT, L57b. Source of truth for the topology (AGENTS.md rule 2).
preamp_audio.py calls references() once for the board and limiter() once per
channel. Run on its own, it writes spice/preamp/input_limiter.subckt, the SAME
parts as SPICE subcircuits for the testbenches (the way gain_block.py writes
gain_block.subckt), so no deck writes the protection by hand.

WHY (NC-059, L57a). A source with a two-pole plug (class II) has its ground
at half the mains through its Y capacitors. Plugged in while selected, the
hot pin touching before the shield, block A's input saw tens of volts of
50 Hz: the LSK489's gate-gate reached 32.2 V at mains +10 % against a 30 V
minimum breakdown (datasheet p. 2). The user chose the limiter at ~+/-5.6 V
("Limitatore +/-5,6 V", ADR-101): gate-gate 4.3 V, the main jack at the
listening position 99.8 / 109.8 dB SPL (0 / +10 dB) under PR-23's 112.2, the
fixed outputs +3.4 dB over the K11's full-scale peak.

   relay COM (SELCOM) --R 1k--+-- block A IN (R_IN 1M inside the block)
                              |
                VLIM_M --|>|--+--|>|-- VLIM_P          (one diode pair per channel)

   VPLUS --R_FEED--+-- VLIM_P          VLIM_M --+--R_FEED-- VMINUS
                   |                            |
            LM4040 5.0 K, A to GND       LM4040 5.0 A, K to GND
                   |                            |
                 C_BYP                        C_BYP

WHY SHUNTS. A clamping diode pushes current INTO its reference: the + diode
into VLIM_P, and the - diode pulls it out of VLIM_M towards the input, which
the - shunt (cathode on ground) supplies. On both sides the clamp current
ADDS to the shunt's own bias, so no clamp current can starve a reference.
A series regulator could not sink it.

The protection belongs to the channel, not to the block (ADR-006: one
topology for all eight blocks); the fixed outputs and block B have no input
from outside. It sits after the selector's contact, so E3 (R_SEL || R_IN at
the jack) is unchanged but for the diodes' leakage and capacitance.

Refs explicit (limitations #22): R<base+79> and D<base+79> per channel
(R179 / D179 left, R379 / D379 right: free between the channel's R178 and
block A's section 14 at base + 90); U1, U2, R4, R5, C1, C2 on the board,
after R1-R3 and before J1.

Run (writes spice/preamp/input_limiter.subckt):
  /Users/roberto/EDA/env/venv/bin/python3 <this file>
"""
import os
import sys

if __name__ == "__main__":
    for _ver in ("6", "7", "8", "9", "10"):
        os.environ.setdefault(
            f"KICAD{_ver}_SYMBOL_DIR",
            "/Users/roberto/Applications/KiCad.app/Contents/SharedSupport/symbols",
        )
        os.environ.setdefault(
            f"KICAD{_ver}_FOOTPRINT_DIR",
            "/Users/roberto/Applications/KiCad.app/Contents/SharedSupport/footprints",
        )
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from skidl import Part, Net  # noqa: E402

import spice_export as sx  # noqa: E402
from gain_block import FP_R, FP_SOT23, FP_CERAMIC, REPO  # noqa: E402

# ADR-101: 1k is AN-015's minimum ("at least 1k, better 1.5k"); 4.7k leaves
# V4 (0.00105 % at 20 kHz) by NC-055's mechanism, and 1k-2.2k changes the
# part's protection little (gate-gate 4.3 -> 3.3 V).
R_SER = "1k"
# The diode pair (L57b): Nexperia BAV199, two low-leakage diodes in series in
# one SOT-23 - 3 pA typ / 5 nA max reverse at 75 V and 25 C, ~1.1 pF per
# diode at 5 V reverse (vendor/diodes/nexperia/BAV199/BAV199.pdf p. 3, fig. 5)
# - against the BAV99's 30 nA max at 25 V. The pins READ FROM THE DATASHEET
# (p. 1, table 2): 1 = A1, 2 = K2, 3 = K1/A2, the common node, on the input.
# The KiCad symbol Diode:BAV99 has the same pin NUMBERS, but names pin 1 "K"
# and pin 2 "A" against its own drawing: wire by number, never by name.
# SPICE: no Nexperia model could be obtained (nexperia.com 403), so BAV199 is
# models/diodes/bav199_fit.lib, a declared fit of the datasheet's figure.
DIODE_VALUE = "BAV199"
DIODE_MODEL = "BAV199"
D_PIN_A, D_PIN_COM, D_PIN_K = "1", "3", "2"
# The shunts: LM4040 5.0 V (the family of the supervisor's U507, psu.py),
# grade B: the threshold's +/-10 mV does not matter for a limiter, and B is
# TI's tightest unencrypted 5.0 V model (models/voltage_reference/
# lm4040_5v0_ngspice.lib, LM4040_NB5P0). SNOS633N p. 3: pin 1 cathode, pin 2
# anode, pin 3 to float or to the anode.
REF_VALUE = "LM4040B-5.0"
REF_SUBCKT = "LM4040_NB5P0 TOL=0"
REF_K, REF_A = "1", "2"      # Reference_Voltage:LM4040DBZ-5, as U507
# R_FEED 10k: ~1.0 mA of bias from the 15 V rails, 13x the datasheet's
# 74 uA IRMIN (p. 26; the model's knee is at ~34 uA, optimistic). A clamping
# diode only ADDS to it (see WHY SHUNTS): <= 1.1 mA per channel (L57a),
# 3.7 mA with both channels clamping and a rail at ~20 V (a rail regulator
# shorted, L45d2b2c) - against 15 mA recommended; 18.5 mW against 306 mW in
# SOT-23. R_FEED dissipates 10 mW, 22.5 mW at 20 V.
R_FEED = "10k"
# The datasheet equivalent of each shunt, for the decks (INREF_EQ, below): TI's model's voltage
# at 100 uA, 4.992 V, inside grade B's 5 V +/-10 mV; ZR 1.1 ohm max at 1 mA (SNOS633N p. 26).
REF_EQ_V, REF_EQ_ZR = "4.992", "1.1"
# C_BYP: TI says the LM4040 is stable with any capacitive load (p. 1, p. 40);
# 100 nF keeps the clamp's sub-microsecond edges off the shunt's own loop.
C_BYP = "100n"


def references(vp, vm, gnd):
    """The two references, shared by both channels. Returns (VLIM_P, VLIM_M)."""
    vlp, vlm = Net("VLIM_P"), Net("VLIM_M")
    up = Part("Reference_Voltage", "LM4040DBZ-5", value=REF_VALUE,
              footprint=FP_SOT23, ref="U1")
    up[REF_K] += vlp
    up[REF_A] += gnd
    um = Part("Reference_Voltage", "LM4040DBZ-5", value=REF_VALUE,
              footprint=FP_SOT23, ref="U2")
    um[REF_K] += gnd
    um[REF_A] += vlm
    sx.spice_dev(up, "X", [REF_K, REF_A], REF_SUBCKT)
    sx.spice_dev(um, "X", [REF_K, REF_A], REF_SUBCKT)
    for ref, a, b, val, fp, pre in (("R4", vp, vlp, R_FEED, FP_R, "R"),
                                    ("R5", vlm, vm, R_FEED, FP_R, "R"),
                                    ("C1", vlp, gnd, C_BYP, FP_CERAMIC, "C"),
                                    ("C2", vlm, gnd, C_BYP, FP_CERAMIC, "C")):
        p = Part("Device", pre, value=val, footprint=fp, ref=ref)
        p[1] += a
        p[2] += b
        sx.spice_dev(p, pre, ["1", "2"], sx.spice_value(val))
    return vlp, vlm


def limiter(base, selcom, ain, vlp, vlm):
    """One channel: R_SER from the selector's common to block A's input, the
    diode pair from the input to the references."""
    r = Part("Device", "R", value=R_SER, footprint=FP_R, ref=f"R{base + 79}")
    r[1] += selcom
    r[2] += ain
    sx.spice_dev(r, "R", ["1", "2"], sx.spice_value(R_SER))
    d = Part("Diode", "BAV99", value=DIODE_VALUE, footprint=FP_SOT23,
             ref=f"D{base + 79}")
    d[D_PIN_A] += vlm
    d[D_PIN_COM] += ain
    d[D_PIN_K] += vlp
    sx.spice_dev(d, "D", [D_PIN_A, D_PIN_COM], DIODE_MODEL, suffix="A")
    sx.spice_dev(d, "D", [D_PIN_COM, D_PIN_K], DIODE_MODEL, suffix="B")
    return r, d


if __name__ == "__main__":
    head = ("GENERATED by circuits/preamp/input_limiter.py - DO NOT HAND-EDIT.\n"
            "ADR-101 (L57b): block A's input protection, the parts of\n"
            "preamp_audio.py. Models: %s (models/diodes/bav199_fit.lib) and\n"
            "%s (models/voltage_reference/lm4040_5v0_ngspice.lib); include them.\n"
            % (DIODE_MODEL, REF_SUBCKT.split()[0]))
    VP, VM, GND = Net("VPLUS"), Net("VMINUS"), Net("GND")
    sx.reset()
    vlp, vlm = references(VP, VM, GND)
    ref_sub = sx.subckt("INREF", ["VLIM_P", "VLIM_M", "VPLUS", "VMINUS"],
                        header=head + "Ports: VLIM_P VLIM_M VPLUS VMINUS "
                        "(node 0 = signal ground). Once per board.")
    # INREF_EQ: the same board parts, each LM4040 replaced by its datasheet figure - 5.0 V
    # (TI's model sits at 4.992 V at 100 uA) behind ZR 1.1 ohm max (SNOS633N p. 26). TI's
    # transistor-level model finds no operating point in ngspice when fed through R_FEED (gmin
    # and source stepping fail; it has a start-up capacitor, Cstart 400 nF): limitations #76.
    # With <= 1.1 mA in a clamping diode ZR moves the threshold by ~1 mV out of 5.6 V.
    eq = []
    for ln in ref_sub.splitlines():
        t = ln.split()
        if ln.startswith(".subckt INREF"):
            eq.append(ln.replace("INREF", "INREF_EQ"))
        elif ln.startswith(".ends"):
            eq.append(".ends INREF_EQ")
        elif t and t[0] in ("XU1", "XU2"):
            k, a = t[1], t[2]
            u = t[0][1:]
            eq.append(f"V{u} N_{u} {a} DC {REF_EQ_V}")
            eq.append(f"RZ{u} {k} N_{u} {REF_EQ_ZR}")
        elif ln.startswith("* Ports"):
            eq.append(ln)
            eq.append("* EQUIVALENT: each LM4040 as its datasheet figure, a source behind ZR max "
                      "(limitations #76).")
        else:
            eq.append(ln)
    ref_sub += "\n" + "\n".join(eq) + "\n"
    sx.reset()
    limiter(100, Net("SELCOM"), Net("AIN"), vlp, vlm)
    lim_sub = sx.subckt("INLIM", ["SELCOM", "AIN", "VLIM_P", "VLIM_M"],
                        header=head + "Ports: SELCOM AIN VLIM_P VLIM_M. "
                        "Once per channel (refs of the left one).")
    path = os.path.join(REPO, "spice", "preamp", "input_limiter.subckt")
    with open(path, "w") as f:
        f.write(ref_sub + "\n" + lim_sub)
    print("SPICE subcircuits ->", path)
