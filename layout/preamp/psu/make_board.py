#!/usr/bin/env python3
"""
L49b, step 1 of 3: the supply board, from the netlist to an unplaced .kicad_pcb.

A TRIAL board (NC-048), the sister of layout/preamp/audio/: it proves the
supply (circuits/preamp/psu.py, the second PCB of P4) fits and routes with its
mains section kept apart. The circuit is not touched here.

Run with KiCad's bundled Python 3.9 (limitations #1):

  /Users/roberto/Applications/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3.9 \
      layout/preamp/psu/make_board.py <out_dir>

Writes <out_dir>/psu_raw.kicad_pcb.
"""
import json
import os
import sys

import kinet2pcb
import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
NETLIST = os.path.join(REPO, "circuits", "preamp", "psu.net")
FP_DIR = "/Users/roberto/Applications/KiCad.app/Contents/SharedSupport/footprints"

# Technology chosen by the user on 2026-10-09 (L49a): two layers, the source's
# footprints, tracks and clearances >= 0.25 mm. Wider than L49a's 0.25 / 0.6
# by the user's preference after L49a ("piste più larghe compatibilmente con
# gli altri vincoli"): narrowed only where a measured constraint says so.
TRACK_MM = 0.4
CLEAR_MM = 0.25
VIA_MM, VIA_DRILL_MM = 0.8, 0.4
# Explicit names, never merged (limitations #23). Two power classes:
# - POWER_WIDE, 1.0 mm: the transformer secondaries (the reservoirs' charging
#   peaks), the small bridge's output and VRELAY - none touches a fine pitch.
# - POWER, 1.0 mm too: the nets on the regulators' VQFN-20 pins. The
#   footprint's pads are 0.35 mm wide at 0.65 mm pitch: the neighbour pad's
#   edge is 0.475 mm from a pin's centre, so a track ENTERING a pin is at most
#   2 x (0.475 - 0.25) = 0.45 mm wide, with 2 or 4 layers alike. Without a
#   neck the router had to run the whole net narrow (L49b: 1.0 mm left 44
#   connections open, 0.5 mm 26, 0.44 mm 5, all at VQFN pins). The user chose
#   (2026-10-09, L49b) "2 strati, stretta solo al piedino": the class stays
#   wide and Freerouting's automatic neckdown narrows the last stretch into
#   the pin only (run.sh); measure.py lists every narrowed segment.
POWER_WIDE_TRACK_MM = 1.0
POWER_WIDE_NETS = ("T1_SEC_A", "T1_SEC_B", "T2_SEC_A", "T2_SEC_B", "RECT_V",
                   "VRELAY")
POWER_TRACK_MM = 1.0
POWER_NETS = ("GND", "VPLUS", "VMINUS", "RLY_RET", "VRELAY_REG",
              "RAW_P", "RAW_M", "RAW_V")
# The mains side (SAFETY.md, "Le parti che toccano la rete"). Its distance to
# everything else is the TRIAL reinforced creepage, 6.4 mm = 2 x 3.2 mm (IEC
# 60664-1, PD2, group IIIb, 250 V: the most severe reading found; IEC 62368-1
# Table 17 read by secondary sources gives 2.5 / 5.0 mm). The norm is not
# confirmed yet (SAFETY.md): a trial figure, L49b's report gives the sources.
# It is held by the placement (an empty band, place.py), judged by the DRC
# (psu.kicad_dru, rule "mains_to_low_voltage") and measured on the copper
# (measure.py). The netclass itself carries the L-to-N figure: Specctra has
# one clearance per class, and 6.4 mm there made the source's own footprints
# (MKDS 5.08 mm pitch: 2.48 mm pad to pad; K501's poles: 5.5 mm) violations
# before any track was laid (L49b, iteration 1).
MAINS_NETS = ("AC_L", "AC_N", "T1_PRI_L", "T1_PRI_N", "T2_PRI_L")
MAINS_TRACK_MM = 1.0
MAINS_CLEAR_MM = 2.4


def netclass(name, track, clear):
    nc = pcbnew.NETCLASS(name)
    nc.SetTrackWidth(pcbnew.FromMM(track))
    nc.SetClearance(pcbnew.FromMM(clear))
    nc.SetViaDiameter(pcbnew.FromMM(VIA_MM))
    nc.SetViaDrill(pcbnew.FromMM(VIA_DRILL_MM))
    return nc


def main():
    global POWER_TRACK_MM, POWER_WIDE_TRACK_MM
    out_dir = sys.argv[1]
    # optional: the rails' width, for the width sweep of L49b's report
    if len(sys.argv) > 2:
        POWER_TRACK_MM = POWER_WIDE_TRACK_MM = float(sys.argv[2])
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "classes.json"), "w") as fh:
        json.dump({"Default": TRACK_MM, "POWER": POWER_TRACK_MM,
                   "POWER_WIDE": POWER_WIDE_TRACK_MM, "MAINS": MAINS_TRACK_MM,
                   "clearance": CLEAR_MM, "mains_class_clearance": MAINS_CLEAR_MM}, fh,
                  indent=1)
    pcb = os.path.join(out_dir, "psu_raw.kicad_pcb")
    kinet2pcb.kinet2pcb(NETLIST, pcb, fp_lib_dirs=[FP_DIR])

    board = pcbnew.LoadBoard(pcb)
    ds = board.GetDesignSettings()
    ds.m_TrackMinWidth = pcbnew.FromMM(0.25)
    ds.m_MinClearance = pcbnew.FromMM(CLEAR_MM)
    # The source's regulator footprint (Texas_RGW0020A_..._ThermalVias) drills
    # 0.2 mm vias in the exposed pad, under KiCad's 0.3 mm default: the board
    # takes the footprint's figure, and the report writes it as a constraint
    # on the fab (or on G2's footprint), instead of a DRC exclusion.
    ds.m_MinThroughDrill = pcbnew.FromMM(0.2)
    ns = ds.m_NetSettings
    default = ns.GetDefaultNetclass()
    default.SetTrackWidth(pcbnew.FromMM(TRACK_MM))
    default.SetClearance(pcbnew.FromMM(CLEAR_MM))
    default.SetViaDiameter(pcbnew.FromMM(VIA_MM))
    default.SetViaDrill(pcbnew.FromMM(VIA_DRILL_MM))
    ns.SetNetclass("POWER", netclass("POWER", POWER_TRACK_MM, CLEAR_MM))
    ns.SetNetclass("POWER_WIDE", netclass("POWER_WIDE", POWER_WIDE_TRACK_MM, CLEAR_MM))
    ns.SetNetclass("MAINS", netclass("MAINS", MAINS_TRACK_MM, MAINS_CLEAR_MM))
    for name in POWER_NETS:
        ns.SetNetclassPatternAssignment(name, "POWER")
    for name in POWER_WIDE_NETS:
        ns.SetNetclassPatternAssignment(name, "POWER_WIDE")
    for name in MAINS_NETS:
        ns.SetNetclassPatternAssignment(name, "MAINS")
    ns.RecomputeEffectiveNetclasses()

    names = {str(x) for x in board.GetNetsByName().keys()}
    print("footprints:", len(board.GetFootprints()))
    print("nets:", board.GetNetCount())
    print("power / mains nets missing from the board:",
          [n for n in POWER_NETS + POWER_WIDE_NETS + MAINS_NETS if n not in names])
    board.Save(pcb)
    print("saved:", pcb)


if __name__ == "__main__":
    main()
