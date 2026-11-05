#!/usr/bin/env python3
"""
L73, step 1 of 3: the audio board, from TODAY's netlist to an unplaced .kicad_pcb.

Copied from L49a (layout/preamp/audio/make_board.py) and changed in three places
(the third: the SMD transistors' pins mapped to their pads, ../pinmap.py):
- the netlist is today's circuits/preamp/preamp_audio.net (653 parts), read,
  never written: the trial copy with the swapped footprints goes in <out_dir>;
- the signal film caps take the footprint of the BIGGEST part of their
  window in the admitted list (REQUIREMENTS P6, ADR-122), and the Stax its
  own (NC-080, footprints/L73.pretty). Trial footprints: the source takes
  them only by decision (G2).

A TRIAL board (NC-048): it proves the audio circuit fits and routes inside the
candidate chassis, it is not the G2 layout. The circuit is not touched here.

Run with KiCad's bundled Python 3.9 (limitations #1):

  .../python3.9 make_board.py <out_dir>

Writes <out_dir>/audio_trial.net, <out_dir>/audio_raw.kicad_pcb,
<out_dir>/footprint_swaps.json.
"""
import json
import os
import re
import sys

import kinet2pcb
import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import pinmap  # noqa: E402
L73 = os.path.abspath(os.path.join(HERE, "..", ".."))
REPO = os.path.abspath(os.path.join(L73, "..", "..", "..", "..", ".."))
NETLIST = os.path.join(REPO, "circuits", "preamp", "preamp_audio.net")
FP_DIR = "/Users/roberto/Applications/KiCad.app/Contents/SharedSupport/footprints"
# library/preamp.pretty (the heatsink, ADR-099) and the lot's trial footprints
FP_DIRS = [FP_DIR, os.path.join(REPO, "library"), os.path.join(L73, "footprints")]

# The biggest part of each window, REQUIREMENTS P6 (ADR-122):
#  - input 1.0-2.2 uF: the 2.2 uF WIMA MKP4 is 26.5 x 11 x 21 mm at 22.5
#    (bigger than the 1 uF's 26.5 x 7); KiCad's next size up is W11.5;
#  - main 2.2-10 uF... its admitted types stop at 4.7 uF: WIMA 31.5 x 15 x 26 at 27.5;
#  - C_T 6.8-10 uF and the Singxer 4.7-10 uF: WIMA 10 uF / 250 V 41.5 x 19 x 32 at 37.5;
#  - the Stax: 1.0 uF +/-5 % only, WIMA 26.5 x 7 x 16.5 at 22.5, its own footprint.
BIG_IN = "Capacitor_THT:C_Rect_L26.5mm_W11.5mm_P22.50mm_MKS4"
BIG_MAIN = "Capacitor_THT:C_Rect_L31.5mm_W15.0mm_P27.50mm_MKS4"
BIG_10U = "Capacitor_THT:C_Rect_L41.5mm_W19.0mm_P37.50mm_MKS4"
STAX = "L73:C_Rect_L26.5mm_W7.0mm_P22.50mm_STAX_1uF"
SWAPS = {}
for r in ("C171", "C172", "C173", "C174", "C371", "C372", "C373", "C374"):
    SWAPS[r] = BIG_IN
for r in ("C262", "C462"):
    SWAPS[r] = BIG_MAIN
for r in ("C265", "C465", "C162", "C362"):
    SWAPS[r] = BIG_10U
for r in ("C165", "C365"):
    SWAPS[r] = STAX

TRACK_MM = 0.25
CLEAR_MM = 0.25
VIA_MM, VIA_DRILL_MM = 0.8, 0.4
POWER_TRACK_MM = 0.6
POWER_NETS = ("GND", "VPLUS", "VMINUS", "VRELAY", "RLY_RET")


def trial_netlist(out_dir):
    t = open(NETLIST).read()
    parts = t.split("(comp\n")
    done = {}
    for i in range(1, len(parts)):
        m = re.search(r'\(ref "([^"]+)"\)', parts[i])
        ref = m.group(1)
        if ref in SWAPS:
            old = re.search(r'\(footprint "([^"]+)"\)', parts[i]).group(1)
            parts[i] = parts[i].replace(f'"{old}"', f'"{SWAPS[ref]}"')
            done[ref] = [old, SWAPS[ref]]
    missing = sorted(set(SWAPS) - set(done))
    assert not missing, missing
    # L73: the SMD transistors' pins B / C / E onto the pads 1 / 2 / 3
    # (pinmap.py: the finding, and the pin-outs read from the datasheets)
    text, mapped = pinmap.remap("(comp\n".join(parts))
    path = os.path.join(out_dir, "audio_trial.net")
    open(path, "w").write(text)
    with open(os.path.join(out_dir, "footprint_swaps.json"), "w") as fh:
        json.dump({"footprints": done, "transistor_pins": mapped}, fh, indent=1)
    print("transistors remapped:", len(mapped))
    return path


def main():
    out_dir = sys.argv[1]
    os.makedirs(out_dir, exist_ok=True)
    net = trial_netlist(out_dir)
    pcb = os.path.join(out_dir, "audio_raw.kicad_pcb")
    kinet2pcb.kinet2pcb(net, pcb, fp_lib_dirs=FP_DIRS)

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

    fps = board.GetFootprints()
    by = {f.GetReference(): f for f in fps}
    wrong = [r for r, fp in SWAPS.items()
             if str(by[r].GetFPID().GetLibItemName()) != fp.split(":")[1]]
    names = {str(x) for x in board.GetNetsByName().keys()}
    print("footprints:", len(fps))
    print("nets:", board.GetNetCount())
    print("power nets missing from the board:", [n for n in POWER_NETS if n not in names])
    print("swaps not applied:", wrong)
    hs = [f.GetReference() for f in fps
          if "WA-T220" in str(f.GetFPID().GetLibItemName())]
    print("heatsinks:", len(hs))
    # every pad of a transistor must now carry a net
    q_empty = [f.GetReference() for f in fps if f.GetReference().startswith("Q")
               and str(f.GetFPID().GetLibItemName()).startswith("SOT-2")
               and any(not p.GetNetname() for p in f.Pads())]
    print("SOT-23 / SOT-223 transistors with an empty pad:", q_empty)
    assert not wrong and len(fps) == 653 and len(hs) == 16 and not q_empty
    board.Save(pcb)
    print("saved:", pcb)


if __name__ == "__main__":
    main()
