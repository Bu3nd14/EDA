#!/usr/bin/env python3
"""
L49a: the numbers the trial board gives back to the project.

  .../python3.9 layout/preamp/audio/measure.py <out_dir>

Reads <out_dir>/audio_routed.kicad_pcb and placement.json, writes
<out_dir>/measure.json and prints it:
- board size, courtyard area and fill;
- routed length per net, the longest signal nets, the input nets
  (RCA header -> selector relay) and the main outputs;
- how many signal nets have copper on both channel halves (cross the spine);
- tracks and vias.
"""
import collections
import json
import os
import sys

import pcbnew

POWER = {"GND", "VPLUS", "VMINUS", "VRELAY", "RLY_RET", "VTRIM", "VHOLD"}


def main():
    out_dir = sys.argv[1]
    b = pcbnew.LoadBoard(os.path.join(out_dir, "audio_routed.kicad_pcb"))
    place = json.load(open(os.path.join(out_dir, "placement.json")))
    W, H = place["board_mm"]
    spine = place["groups"]["SPINE"]
    x_lo, x_hi = spine[0], spine[0] + spine[2]

    length = collections.Counter()
    xs = collections.defaultdict(list)
    vias = 0
    for t in b.Tracks():
        if type(t).__name__ == "PCB_VIA":
            vias += 1
            continue
        n = t.GetNetname()
        length[n] += pcbnew.ToMM(t.GetLength())
        for p in (t.GetStart(), t.GetEnd()):
            xs[n].append(pcbnew.ToMM(p.x))
    crt = 0.0
    for f in b.GetFootprints():
        if f.GetReference().startswith("H"):
            continue
        bb = f.GetCourtyard(pcbnew.F_CrtYd).BBox()
        crt += pcbnew.ToMM(bb.GetWidth()) * pcbnew.ToMM(bb.GetHeight())

    signal = {n: l for n, l in length.items() if n not in POWER}
    longest = sorted(signal.items(), key=lambda kv: -kv[1])[:12]
    # Nets with copper left of the spine AND right of it: L and R meet there.
    both = sorted(n for n in signal
                  if min(xs[n]) < x_lo and max(xs[n]) > x_hi)
    # Input nets: those carrying an IN header pin.
    inputs = {}
    outputs = {}
    for f in b.GetFootprints():
        v = f.GetValue()
        for p in f.Pads():
            n = p.GetNetname()
            if v.startswith("IN") and n and n not in POWER:
                inputs[f"{f.GetReference()} {v}"] = round(length[n], 1)
            if v.startswith("MAIN") and n and n not in POWER:
                outputs[f"{f.GetReference()} {v}"] = round(length[n], 1)

    info = {"board_mm": [W, H], "area_cm2": round(W * H / 100, 1),
            "courtyard_cm2": round(crt / 100, 1),
            "fill": round(crt / (W * H), 3),
            "tracks_m": round(sum(length.values()) / 1000, 2), "vias": vias,
            "longest_signal_nets_mm": [[n, round(l, 1)] for n, l in longest],
            "input_nets_mm": inputs, "main_output_nets_mm": outputs,
            "nets_crossing_spine": both, "n_nets_crossing_spine": len(both),
            "power_nets_mm": {n: round(length[n], 1) for n in sorted(POWER) if n in length}}
    with open(os.path.join(out_dir, "measure.json"), "w") as fh:
        json.dump(info, fh, indent=1)
    print(json.dumps(info, indent=1))


if __name__ == "__main__":
    main()
