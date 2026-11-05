#!/usr/bin/env python3
"""
L73: the height of the audio board's parts, in bands of depth.

  .../python3.9 heights.py <out_dir> [band_mm]

Reads <out_dir>/audio_placed.kicad_pcb (or audio_routed), writes
<out_dir>/heights.json: for every band of depth (y from the board's rear edge,
the RCA side) the tallest body above the board and the part that sets it.
floorplan.py uses it instead of one "tallest part" for the whole board: the
rear band sits under the RCA jacks, the front band under the panel controls.

The heights, above the board's top face, each with its source. Where no
datasheet in the repo gives it, the figure is an ASSUMPTION of this trial,
marked so, and the biggest common size is taken.
"""
import json
import os
import sys

import pcbnew

# footprint name prefix -> (height mm, source)
HEIGHTS = [
    ("TO-220-3_Vertical_Ohmite_WA-T220-101E", 35.6,
     "Ohmite sink-w.pdf: 32.0 +/- 0.3 mm body, 3.6 mm REF to the board"),
    ("C_Rect_L41.5mm_W19.0mm", 32.0, "WIMA MKP4 10 uF / 250 V, 41.5 x 19 x 32 (ADR-122)"),
    ("C_Rect_L31.5mm_W15.0mm", 26.0, "WIMA MKP4 4.7 uF, 31.5 x 15 x 26 (ADR-122)"),
    ("C_Rect_L26.5mm_W11.5mm", 21.0, "WIMA MKP4 2.2 uF, 26.5 x 11 x 21 (ADR-122)"),
    ("C_Rect_L26.5mm_W7.0mm", 16.5, "WIMA MKP4 1 uF, 26.5 x 7 x 16.5 (ADR-122)"),
    ("CP_Radial_D10.0mm", 20.0, "ASSUMED: 1000 uF in D10, 20 mm the common length"),
    ("CP_Radial_D8.0mm", 11.5, "ASSUMED: 100 uF in D8, 11.5 mm"),
    ("Relay_DPDT_Omron_G6K", 10.0, "ASSUMED: G6K 10 mm max (Omron G6K, ~9.5)"),
    ("Relay_DPDT_AXICOM", 10.0, "ASSUMED: IM series ~9.6 mm"),
    ("PinHeader_", 15.0, "ASSUMED: header 8.5 mm plus the mating housing"),
    ("C_Disc_D5.0mm", 10.0, "ASSUMED: disc ceramic"),
    ("R_Axial_DIN0207", 3.5, "horizontal, D2.5 plus lead bend"),
    ("D_DO-35", 3.0, "horizontal"),
    ("D_DO-41", 4.0, "horizontal"),
    ("TestPoint_Keystone", 9.0, "ASSUMED: Keystone 5000-series loop"),
    ("SOT-", 1.8, "SMD"),
    ("SOIC-", 1.8, "SMD"),
    ("D_SMA", 2.4, "SMD"),
    ("MountingHole", 0.0, ""),
]


def height_of(name):
    for k, h, src in HEIGHTS:
        if name.startswith(k):
            return h, src
    return 12.0, "ASSUMED: unlisted footprint, 12 mm"


def main():
    out_dir = sys.argv[1]
    band = float(sys.argv[2]) if len(sys.argv) > 2 else 10.0
    path = os.path.join(out_dir, "audio_placed.kicad_pcb")
    b = pcbnew.LoadBoard(path)
    edge = b.GetBoardEdgesBoundingBox()
    y0, H = pcbnew.ToMM(edge.GetY()), pcbnew.ToMM(edge.GetHeight())
    n = int(H // band) + 1
    bands = [{"y_mm": [round(i * band, 1), round(min((i + 1) * band, H), 1)],
              "tall_mm": 0.0, "part": None} for i in range(n)]
    unlisted = set()
    for f in b.GetFootprints():
        name = str(f.GetFPID().GetLibItemName())
        h, src = height_of(name)
        if src.startswith("ASSUMED: unlisted"):
            unlisted.add(name)
        bb = f.GetCourtyard(pcbnew.F_CrtYd).BBox() if not f.GetReference().startswith("H") \
            else f.GetBoundingBox(False)
        a = pcbnew.ToMM(bb.GetY()) - y0
        z = pcbnew.ToMM(bb.GetBottom()) - y0
        for i in range(max(0, int(a // band)), min(n, int(z // band) + 1)):
            if h > bands[i]["tall_mm"]:
                bands[i]["tall_mm"] = h
                bands[i]["part"] = f"{f.GetReference()} {f.GetValue()}"
    info = {"board_depth_mm": round(H, 1), "band_mm": band, "bands": bands,
            "tallest_mm": max(x["tall_mm"] for x in bands),
            "table": [[k, h, s] for k, h, s in HEIGHTS], "unlisted_footprints": sorted(unlisted)}
    with open(os.path.join(out_dir, "heights.json"), "w") as fh:
        json.dump(info, fh, indent=1)
    for x in bands:
        print(x)
    print("unlisted:", sorted(unlisted))


if __name__ == "__main__":
    main()
