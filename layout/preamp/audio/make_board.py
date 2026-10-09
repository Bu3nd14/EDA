#!/usr/bin/env python3
"""
L49a, step 1 of 3: the audio board, from the netlist to an unplaced .kicad_pcb.

A TRIAL board (NC-048): it proves the audio circuit fits and routes inside the
candidate chassis, it is not the G2 layout. The circuit is not touched here:
the netlist comes straight from circuits/preamp/preamp_audio.py.

Run with KiCad's bundled Python 3.9 (pcbnew and kinet2pcb live only there,
docs/limitations.md #1):

  /Users/roberto/Applications/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3.9 \
      layout/preamp/audio/make_board.py <out_dir>

Writes <out_dir>/audio_raw.kicad_pcb.
"""
import os
import sys

import kinet2pcb
import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
NETLIST = os.path.join(REPO, "circuits", "preamp", "preamp_audio.net")
FP_DIR = "/Users/roberto/Applications/KiCad.app/Contents/SharedSupport/footprints"

# Board technology chosen by the user on 2026-10-09 (L49a): two layers, the
# footprints as the source has them (THT plus SMD relays, SOT-23, SOIC),
# tracks and clearances >= 0.25 mm. Power nets get a wider class.
TRACK_MM = 0.25
CLEAR_MM = 0.25
VIA_MM, VIA_DRILL_MM = 0.8, 0.4
POWER_TRACK_MM = 0.6
# Explicit names, never merged (limitations #23): stable across regenerations.
POWER_NETS = ("GND", "VPLUS", "VMINUS", "VRELAY", "RLY_RET")


def main():
    out_dir = sys.argv[1]
    os.makedirs(out_dir, exist_ok=True)
    pcb = os.path.join(out_dir, "audio_raw.kicad_pcb")
    kinet2pcb.kinet2pcb(NETLIST, pcb, fp_lib_dirs=[FP_DIR])

    board = pcbnew.LoadBoard(pcb)
    ds = board.GetDesignSettings()
    ds.m_TrackMinWidth = pcbnew.FromMM(TRACK_MM)
    ds.m_MinClearance = pcbnew.FromMM(CLEAR_MM)
    ns = ds.m_NetSettings
    default = ns.GetDefaultNetclass()
    default.SetTrackWidth(pcbnew.FromMM(TRACK_MM))
    default.SetClearance(pcbnew.FromMM(CLEAR_MM))
    default.SetViaDiameter(pcbnew.FromMM(VIA_MM))
    default.SetViaDrill(pcbnew.FromMM(VIA_DRILL_MM))
    power = pcbnew.NETCLASS("POWER")
    power.SetTrackWidth(pcbnew.FromMM(POWER_TRACK_MM))
    power.SetClearance(pcbnew.FromMM(CLEAR_MM))
    power.SetViaDiameter(pcbnew.FromMM(VIA_MM))
    power.SetViaDrill(pcbnew.FromMM(VIA_DRILL_MM))
    ns.SetNetclass("POWER", power)
    for name in POWER_NETS:
        ns.SetNetclassPatternAssignment(name, "POWER")
    ns.RecomputeEffectiveNetclasses()

    names = [n for n in board.GetNetsByName().keys()]
    missing = [n for n in POWER_NETS if str(n) not in {str(x) for x in names}]
    print("footprints:", len(board.GetFootprints()))
    print("nets:", board.GetNetCount())
    print("power nets missing from the board:", missing)
    board.Save(pcb)
    print("saved:", pcb)


if __name__ == "__main__":
    main()
