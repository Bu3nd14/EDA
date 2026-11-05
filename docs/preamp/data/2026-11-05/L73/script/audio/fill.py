#!/usr/bin/env python3
"""
L73: how full each group's rectangle is - the sum of its parts' courtyards
against the rectangle the packer gave it. Says how much a better packing could
win before the board's size is blamed on the circuit.

  .../python3.9 fill.py <out_dir>      (reads audio_placed.kicad_pcb, placement.json)
"""
import collections
import json
import os
import sys

import pcbnew

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from place import crt_box, group_of, source_files  # noqa: E402


def main():
    out_dir = sys.argv[1]
    b = pcbnew.LoadBoard(os.path.join(out_dir, "audio_placed.kicad_pcb"))
    place = json.load(open(os.path.join(out_dir, "placement.json")))
    src = source_files()
    area = collections.Counter()
    tallest = collections.defaultdict(list)
    for f in b.GetFootprints():
        r = f.GetReference()
        if r.startswith("H"):
            continue
        bb = crt_box(f)
        a = pcbnew.ToMM(bb.GetWidth()) * pcbnew.ToMM(bb.GetHeight())
        g = group_of(r, src.get(r, ""))
        area[g] += a
        tallest[g].append((round(a, 1), r, f.GetValue()))
    W, H = place["board_mm"]
    out = {"board_mm": [W, H], "board_cm2": round(W * H / 100, 1),
           "courtyard_cm2": round(sum(area.values()) / 100, 1),
           "fill_board": round(sum(area.values()) / (W * H), 3), "groups": {}}
    for g, rect in place["groups"].items():
        ra = rect[2] * rect[3]
        out["groups"][g] = {"rect_mm": rect[2:], "courtyard_cm2": round(area[g] / 100, 1),
                            "fill": round(area[g] / ra, 3) if ra else None,
                            "biggest": sorted(tallest[g], reverse=True)[:4]}
    out["EDGE_courtyard_cm2"] = round(area["EDGE"] / 100, 1)
    with open(os.path.join(out_dir, "fill.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
