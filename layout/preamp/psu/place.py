#!/usr/bin/env python3
"""
L49b, step 2 of 3: placement of the supply trial board, by functional group.

Run with KiCad's bundled Python 3.9 (limitations #1):

  .../python3.9 layout/preamp/psu/place.py <out_dir> [height_mm] [gap_mm] [sep_mm] [logic_gap_mm]

Reads <out_dir>/psu_raw.kicad_pcb, writes <out_dir>/psu_placed.kicad_pcb and
<out_dir>/placement.json (group rectangles, board size, the checks).

The floorplan, left to right:
- MAINS: the mains section (SAFETY.md, P2) in its own column on the left
  edge - J510 from the IEC module, F501 and J511 to the small toroid T2, the
  mains relay K501 and J512 to the big toroid T1. K501 is turned so its COIL
  pins face the low-voltage side: the coil is the relay's low-voltage end
  (G2RL footprint: coil pads 18 mm edge to edge from the contact pads).
- a SEPARATION band of sep_mm, courtyard to courtyard, with nothing in it:
  the router keeps the MAINS class clearance (make_board.py) and measure.py
  measures the copper distance that results;
- RAIL: T1's secondary, the bridge, the reservoirs, the two regulators, the
  hold-up after them and the star tie NT501;
- VRELAY: T2's secondary, its bridge, the 12 V and 5 V regulators;
- LOGIC: the supervisor, the timer, the micro, the switches, and the headers
  to the audio board (J1, J2, J4) and to the panel (J508), UPDI (J515).
Each group is packed (shelf, connectivity order) to the narrowest width that
keeps it within height_mm. Board geometry is an OUTPUT.
"""
import collections
import json
import os
import sys

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "audio"))
# The packing helpers are L49a's, unchanged.
from place import (add_hole, connectivity_order, crt_box, move_box_to,  # noqa: E402
                   outline, size_mm)

MARGIN = 8.0          # clears the M3 holes in the corners (L49a's 4 mm landed on parts)
HOLE_INSET = 4.0
# Top -> bottom, then the next column: K501 last, so it lands in the column
# next to the separation band with its coil facing it.
MAINS = ["J510", "F501", "J511", "J512", "K501"]
MAINS_NETS = {"AC_L", "AC_N", "T1_PRI_L", "T1_PRI_N", "T2_PRI_L"}
# In PACKING order, not sorted by height: the tall parts first, then each
# regulator followed by its own satellites (input / NR / output caps, the
# protection diode, the feedback divider), so they land next to it. Sorted by
# height they scattered over the rows and 2-3 connections stayed open at any
# rail width from 0.6 to 1.0 mm (L49b, iterations 24-27).
RAIL = ["J513", "D501", "C501", "C502", "C505", "C506",
        "U501", "C509", "C507", "C511", "D510",
        "U502", "C510", "C508", "C512", "C513", "R501", "R502", "D511"]
# The star tie (GND to RLY_RET, psu.py) sits in the corridor between RAIL and
# VRELAY, its GND pad towards the rails: packed inside RAIL, RLY_RET had to
# cross the whole rail block to reach it and stayed unrouted (L49b, it. 16-19).
STAR = "NT501"
VRELAY = ["J514", "D503", "C520", "C523",
          "U503", "C522", "C521", "C524", "D512",
          "D504", "U504", "C525"]


def group_of(ref):
    if ref == STAR:
        return "STAR"
    if ref in MAINS:
        return "MAINS"
    if ref in RAIL:
        return "RAIL"
    if ref in VRELAY:
        return "VRELAY"
    return "LOGIC"


# Room of their own round the three VQFN regulators, on every side: each takes
# up to six 1.0 mm rail tracks plus its escapes and anchors (escape.py). At the
# group's gap alone the router left 3-4 connections open round U501 (L49b,
# iterations 28-29) while half the board was empty.
PAD = {"U501": 3.0, "U502": 3.0, "U503": 3.0}


def pack(fps, width, gap, x0, y0, place=True):
    """L49a's shelf packing, with PAD mm of extra room round some parts."""
    x, y, row_h, used_w = 0.0, 0.0, 0.0, 0.0
    for f in fps:
        p = PAD.get(f.GetReference(), 0.0)
        w, h = size_mm(f)
        w, h = w + 2 * p, h + 2 * p
        if x > 0 and x + w > width:
            y += row_h + gap
            x, row_h = 0.0, 0.0
        if place:
            move_box_to(f, x0 + x + p, y0 + y + p)
        x += w + gap
        used_w = max(used_w, x - gap)
        row_h = max(row_h, h)
    return used_w, y + row_h


def width_for_height(fps, height, gap, w_min):
    """Narrowest packing width (1 mm steps) whose height fits."""
    w = w_min
    while True:
        pw, ph = pack(fps, w, gap, 0.0, 0.0, place=False)
        if ph <= height or w > 400:
            return w, pw, ph
        w += 1.0


def turn_coil_right(k):
    """Orient K501 so its coil pads (A1, A2) are right of its contacts."""
    best = None
    for deg in (0, 90, 180, 270):
        k.SetOrientationDegrees(deg)
        pads = {p.GetNumber(): p.GetPosition() for p in k.Pads()}
        dx = pads["A1"].x - pads["13"].x
        if best is None or dx > best[1]:
            best = (deg, dx)
    k.SetOrientationDegrees(best[0])
    return best[0]


def main():
    out_dir = sys.argv[1]
    height = float(sys.argv[2]) if len(sys.argv) > 2 else 100.0
    gap = float(sys.argv[3]) if len(sys.argv) > 3 else 1.5
    sep = float(sys.argv[4]) if len(sys.argv) > 4 else 8.0
    # The logic block gets its own gap: the 12 V and its return reach some
    # forty 0805 / SOT-23 / SOIC pins there at 1.0 mm (the user's wide rails),
    # and at the rails' gap 2 connections stayed open (L49b, it. 20-21).
    logic_gap = float(sys.argv[5]) if len(sys.argv) > 5 else gap
    board = pcbnew.LoadBoard(os.path.join(out_dir, "psu_raw.kicad_pcb"))

    groups = collections.defaultdict(list)
    for f in board.GetFootprints():
        f.SetOrientationDegrees(0)
        groups[group_of(f.GetReference())].append(f)
    by_ref = {f.GetReference(): f for f in board.GetFootprints()}
    groups["RAIL"] = [by_ref[r] for r in RAIL]
    groups["VRELAY"] = [by_ref[r] for r in VRELAY]
    groups["LOGIC"] = connectivity_order(groups["LOGIC"])
    # tallest first: the SOICs and the diodes set the rows
    groups["LOGIC"].sort(key=lambda f: -size_mm(f)[1])
    k501_deg = turn_coil_right(by_ref["K501"])
    # Terminal blocks of the mains column: pins in a column, wire entry to
    # the left edge (outside), so the mains wiring never crosses the board.
    for r in ("J510", "J511", "J512"):
        by_ref[r].SetOrientationDegrees(90)
    groups["MAINS"] = [by_ref[r] for r in MAINS]

    cg = 3.0 * gap   # corridor between groups, for the router
    # MAINS: columns of one part per row, as many as height_mm asks for.
    inner_h = max(height - 2 * MARGIN, max(size_mm(f)[1] for f in groups["MAINS"]))
    mcols, col, used = [], [], 0.0
    for f in groups["MAINS"]:
        h = size_mm(f)[1]
        if col and used + 2 * gap + h > inner_h:
            mcols.append(col)
            col, used = [], 0.0
        used += (2 * gap if col else 0.0) + h
        col.append(f)
    mcols.append(col)
    mcol_w = [max(size_mm(f)[0] for f in c) for c in mcols]
    mw = sum(mcol_w) + 2 * gap * (len(mcols) - 1)
    packs = {}
    gaps = {"RAIL": gap, "VRELAY": gap, "LOGIC": logic_gap}
    for g in ("RAIL", "VRELAY", "LOGIC"):
        w_min = max(size_mm(f)[0] for f in groups[g])
        packs[g] = width_for_height(groups[g], inner_h, gaps[g], w_min)
    W = (2 * MARGIN + mw + sep + packs["RAIL"][1] + cg + packs["VRELAY"][1]
         + cg + packs["LOGIC"][1])
    H = 2 * MARGIN + max([inner_h] + [p[2] for p in packs.values()])

    rects = {}
    x, y_max = MARGIN, 0.0
    for c, cw in zip(mcols, mcol_w):
        y = MARGIN
        for f in c:
            w, h = size_mm(f)
            # K501 flush right, its coil towards the band; the terminal blocks
            # flush left, away from it: with J512 flush right the primary
            # K501 -> J512 had to pass 6.4 mm from the coil (L49b, it. 11).
            move_box_to(f, x + cw - w if f.GetReference() == "K501" else x, y)
            y += h + 2 * gap
        y_max = max(y_max, y - 2 * gap)
        x += cw + 2 * gap
    rects["MAINS"] = [MARGIN, MARGIN, round(mw, 2), round(y_max - MARGIN, 2)]
    x = MARGIN + mw + sep
    rects["SEPARATION"] = [round(MARGIN + mw, 2), 0.0, sep, round(H, 2)]
    for g in ("RAIL", "VRELAY", "LOGIC"):
        w, h = pack(groups[g], packs[g][0], gaps[g], x, MARGIN)
        rects[g] = [round(x, 2), MARGIN, round(w, 2), round(h, 2)]
        if g == "RAIL":
            # the star tie in the RAIL | VRELAY corridor, half way down, its
            # GND pad (2) towards the rails
            star = by_ref[STAR]
            for deg in (0, 90, 180, 270):
                star.SetOrientationDegrees(deg)
                pads = {p.GetNumber(): p.GetPosition().x for p in star.Pads()}
                if pads["2"] < pads["1"]:
                    break
            sw, sh = size_mm(star)
            move_box_to(star, x + w + (cg - sw) / 2, MARGIN + (inner_h - sh) / 2)
            rects["STAR"] = [round(x + w + (cg - sw) / 2, 2),
                             round(MARGIN + (inner_h - sh) / 2, 2), round(sw, 2), round(sh, 2)]
        x += w + cg

    for hx, hy in ((HOLE_INSET, HOLE_INSET), (W - HOLE_INSET, HOLE_INSET),
                   (HOLE_INSET, H - HOLE_INSET), (W - HOLE_INSET, H - HOLE_INSET)):
        add_hole(board, hx, hy)
    outline(board, W, H)

    boxes = [(f.GetReference(), crt_box(f)) for f in board.GetFootprints()
             if not f.GetReference().startswith("H")]
    overlaps = []
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            if boxes[i][1].Intersects(boxes[j][1]):
                overlaps.append([boxes[i][0], boxes[j][0]])
    # A mounting hole must not land on a part either (the corners are free in
    # L49a's floorplan, not necessarily here).
    holes = [f for f in board.GetFootprints() if f.GetReference().startswith("H")]
    hole_hits = [[h.GetReference(), r] for h in holes for r, b in boxes
                 if crt_box(h).Intersects(b)]

    moved_refs = []
    for f in board.GetFootprints():
        ref = f.Reference()
        if f.GetReference().startswith("H"):
            ref.SetVisible(False)
            continue
        rb = ref.GetBoundingBox()
        for ref_other, box in boxes:
            if ref_other != f.GetReference() and rb.Intersects(box):
                ref.SetLayer(pcbnew.F_Fab)
                moved_refs.append(f.GetReference())
                break

    out = os.path.join(out_dir, "psu_placed.kicad_pcb")
    board.Save(out)
    info = {"height_target_mm": height, "gap_mm": gap, "logic_gap_mm": logic_gap,
            "separation_mm": sep,
            "k501_orientation_deg": k501_deg,
            "board_mm": [round(W, 1), round(H, 1)],
            "area_cm2": round(W * H / 100, 1),
            "groups": rects, "group_counts": {g: len(v) for g, v in groups.items()},
            "courtyard_overlaps": overlaps, "hole_overlaps": hole_hits,
            "refs_moved_to_fab": moved_refs}
    with open(os.path.join(out_dir, "placement.json"), "w") as fh:
        json.dump(info, fh, indent=1)
    print(json.dumps({k: info[k] for k in ("board_mm", "area_cm2", "group_counts",
                                           "k501_orientation_deg")}))
    print("courtyard overlaps:", len(overlaps), overlaps[:5])
    print("hole overlaps:", hole_hits)
    print("saved:", out)


if __name__ == "__main__":
    main()
