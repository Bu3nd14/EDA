#!/usr/bin/env python3
"""
L49a, step 2 of 3: placement of the audio trial board, by functional group.

Run with KiCad's bundled Python 3.9 (limitations #1):

  .../python3.9 layout/preamp/audio/place.py <out_dir> [gap_mm] [block_w_mm]

Reads <out_dir>/audio_raw.kicad_pcb, writes <out_dir>/audio_placed.kicad_pcb
and <out_dir>/placement.json (group rectangles, board size, the checks).

The floorplan follows the circuit, not a grid:
- the 16 relays are SHARED by the two channels (one pole each: K13-K16 the
  selector, ADR-064; K7-K10 the trim; K1/K5/K11/K12 the gain; K2-K4 the mute;
  K6 the permit), so they form a spine in the middle, left channel on the
  left, right channel mirrored on the right;
- the RCA harness headers (inputs, fixed outputs, main) sit on the REAR edge,
  the panel harness headers (volume, the three rotary switches, mute switch,
  LEDs, the timer, the supply) on the FRONT edge;
- per channel, block A and block B next to the spine (they go through it:
  selector -> A -> trim -> volume -> B -> mute), the two fixed-output
  buffers outside them, the channel parts (output and DC-blocking film caps,
  C_T, R_G) outermost;
- each bias sensor packed right after its MJE15032 (gain_block.py,
  "thermally coupled to the NPN output device ... the coupling is PCB copper",
  ADR-034 / NC-019); the distance is measured and written to placement.json.

Board geometry is an OUTPUT: the outline is the packed groups plus a margin.

L73 (copied from L49a, layout/preamp/audio/place.py), on today's circuit:
- the bias sensor is the DZT5551 of the Vbe multiplier (SOT-223, ADR-082), the
  one wired to the 1.58k of section 4: a block has three MMBT5551 and L49a's
  "first MMBT5551" is no longer the sensor;
- the block test points TPn01 / TPn02 go to block n (L49a's rule put
  TP501-TP802 in the right channel strip), TP1-TP9 to the spine;
- the input limiter (input_limiter.py): D179 / R179 and D379 / R379 to their
  channel, U1 / U2 / C1 / C2 / R4 / R5 (shared) to the spine;
- the sixteen WA-T220-101E heatsinks sit at collector potential (MJE15032 on
  VPLUS, MJE15033 on VMINUS, ADR-099): their courtyard holds the whole
  heatsink, so no courtyard overlap means no contact, and the smallest
  heatsink-to-heatsink gap is measured and written to placement.json.
"""
import collections
import json
import math
import os
import re
import sys

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))   # docs/preamp/data/<date>/L73/script/audio
NETLIST = os.path.join(REPO, "circuits", "preamp", "preamp_audio.net")
FP_DIR = "/Users/roberto/Applications/KiCad.app/Contents/SharedSupport/footprints"

PACK = os.environ.get("L73_PACK", "connectivity")   # L73: "height" = tallest first
MARGIN = 4.0          # board edge to the nearest courtyard, mm
HOLE_INSET = 4.0      # M3 hole centre from the corner, mm
STRIP = 6.0           # extra depth of the rear / front connector strips, mm
POWER_NETS = {"GND", "VPLUS", "VMINUS", "VRELAY", "RLY_RET", "VTRIM", "VHOLD"}

REAR_L = ["J230", "J110", "J111", "J104", "J103", "J102", "J101"]   # outer -> spine
REAR_R = ["J430", "J310", "J311", "J304", "J303", "J302", "J301"]
FRONT = ["J120", "SW1", "SW2", "SW4", "SW3", "J4", "J5", "J6", "J7", "J2", "J1", "J320"]


def source_files():
    """ref -> source file of the part, read from the netlist's SKiDL Line."""
    t = open(NETLIST).read()
    out = {}
    for ref, line in re.findall(
            r'\(comp\s+\(ref "([^"]+)"\).*?SKiDL Line"\) "([^"]+)"', t, re.S):
        out[ref] = line.split(":")[0]
    return out


def num(ref):
    m = re.search(r"(\d+)$", ref)
    return int(m.group(1)) if m else -1


def group_of(ref, src):
    """The functional group of a part."""
    n = num(ref)
    if src == "gain_block.py":
        return {1: "A_L", 2: "B_L", 3: "A_R", 4: "B_R",
                5: "F1_L", 6: "F2_L", 7: "F1_R", 8: "F2_R"}[n // 100]
    if ref in REAR_L or ref in REAR_R or ref in FRONT:
        return "EDGE"
    if ref.startswith("TP") and n >= 100:     # L73: the block's own test points
        return {1: "A_L", 2: "B_L", 3: "A_R", 4: "B_R",
                5: "F1_L", 6: "F2_L", 7: "F1_R", 8: "F2_R"}[n // 100]
    if src == "input_limiter.py" and n >= 100:  # L73: D179/R179 left, D379/R379 right
        return "CH_L" if n // 100 == 1 else "CH_R"
    if src == "preamp_audio.py" and n >= 100:
        return "CH_L" if n // 100 in (1, 2) else "CH_R"
    if src == "trim.py" and n >= 900:
        # R901-R903 the left trim divider, R911-R913 the right (trim.py).
        return "CH_L" if n < 910 else "CH_R"
    return "SPINE"


def crt_box(fp):
    """Courtyard bounding box in board units, falling back to the body."""
    try:
        bb = fp.GetCourtyard(pcbnew.F_CrtYd).BBox()
        if bb.GetWidth() > 0:
            return bb
    except Exception:  # noqa: BLE001
        pass
    return fp.GetBoundingBox(False)


def move_box_to(fp, x_mm, y_mm):
    """Move fp so its courtyard's top-left corner lands on (x_mm, y_mm)."""
    bb = crt_box(fp)
    pos = fp.GetPosition()
    dx = pcbnew.FromMM(x_mm) - bb.GetX()
    dy = pcbnew.FromMM(y_mm) - bb.GetY()
    fp.SetPosition(pcbnew.VECTOR2I(pos.x + dx, pos.y + dy))


def size_mm(fp):
    bb = crt_box(fp)
    return pcbnew.ToMM(bb.GetWidth()), pcbnew.ToMM(bb.GetHeight())


def connectivity_order(fps):
    """Order a group's footprints so that parts sharing a signal net sit
    next to each other in the packing (BFS over signal nets)."""
    by_ref = {f.GetReference(): f for f in fps}
    nets = collections.defaultdict(set)
    for f in fps:
        for p in f.Pads():
            nn = p.GetNetname()
            if nn and nn not in POWER_NETS:
                nets[nn].add(f.GetReference())
    adj = collections.defaultdict(set)
    for members in nets.values():
        if len(members) > 12:
            continue
        for a in members:
            adj[a] |= members - {a}
    order, seen = [], set()
    for seed in sorted(by_ref, key=lambda r: (-len(adj[r]), r)):
        if seed in seen:
            continue
        queue = collections.deque([seed])
        seen.add(seed)
        while queue:
            r = queue.popleft()
            order.append(r)
            for nb in sorted(adj[r], key=lambda x: (-len(adj[x]), x)):
                if nb not in seen:
                    seen.add(nb)
                    queue.append(nb)
    # The bias sensor goes right after the NPN output device it senses.
    vals = {r: by_ref[r].GetValue() for r in order}
    sensor = bias_sensor(fps)
    npn = [r for r in order if vals[r] == "MJE15032"]
    if sensor and npn:
        order.remove(sensor)
        order.insert(order.index(npn[0]) + 1, sensor)
    return [by_ref[r] for r in order]


def bias_sensor(fps):
    """L73: the DZT5551 of the Vbe multiplier - the one sharing a net with the
    block's 1.58k (gain_block.py section 4, ADR-054 / ADR-082)."""
    r158 = [f for f in fps if f.GetValue() == "1.58k"]
    if not r158:
        return None
    nets = {p.GetNetname() for p in r158[0].Pads()}
    for f in fps:
        if f.GetValue() == "DZT5551" and nets & {p.GetNetname() for p in f.Pads()}:
            return f.GetReference()
    return None


def shelf_pack(fps, width, gap, x0, y0):
    """Pack footprints in rows of at most `width` mm. Returns (w, h)."""
    x, y, row_h, used_w = 0.0, 0.0, 0.0, 0.0
    for f in fps:
        w, h = size_mm(f)
        if x > 0 and x + w > width:
            y += row_h + gap
            x, row_h = 0.0, 0.0
        move_box_to(f, x0 + x, y0 + y)
        x += w + gap
        used_w = max(used_w, x - gap)
        row_h = max(row_h, h)
    return used_w, y + row_h


def trial_pack(fps, width, gap):
    """Size of a packing without keeping it (positions are overwritten later)."""
    return shelf_pack(fps, width, gap, 0.0, 0.0)


def add_hole(board, x_mm, y_mm):
    fp = pcbnew.FootprintLoad(os.path.join(FP_DIR, "MountingHole.pretty"),
                              "MountingHole_3.2mm_M3")
    fp.SetReference(f"H{len([f for f in board.GetFootprints() if f.GetReference().startswith('H')]) + 1}")
    fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x_mm), pcbnew.FromMM(y_mm)))
    board.Add(fp)


def outline(board, w, h):
    pts = [(0, 0), (w, 0), (w, h), (0, h)]
    for i in range(4):
        seg = pcbnew.PCB_SHAPE(board)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(pts[i][0]), pcbnew.FromMM(pts[i][1])))
        seg.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(pts[(i + 1) % 4][0]),
                                   pcbnew.FromMM(pts[(i + 1) % 4][1])))
        seg.SetLayer(pcbnew.Edge_Cuts)
        seg.SetWidth(pcbnew.FromMM(0.1))
        board.Add(seg)


def main():
    out_dir = sys.argv[1]
    gap = float(sys.argv[2]) if len(sys.argv) > 2 else 1.5
    block_w = float(sys.argv[3]) if len(sys.argv) > 3 else 75.0
    # The relay spine needs more room than the blocks: its SMD relays must
    # escape on their own (L49a: with 1.5 mm Freerouting left K1 pin 6
    # unrouted unless its fan-out stage necked tracks to 0.187 mm).
    spine_gap = float(sys.argv[4]) if len(sys.argv) > 4 else 2 * gap
    board = pcbnew.LoadBoard(os.path.join(out_dir, "audio_raw.kicad_pcb"))
    src = source_files()

    groups = collections.defaultdict(list)
    for f in board.GetFootprints():
        f.SetOrientationDegrees(0)
        groups[group_of(f.GetReference(), src.get(f.GetReference(), ""))].append(f)
    for g in groups:
        groups[g] = connectivity_order(groups[g])
    # The channel strip is mostly big film caps of mixed height: tallest
    # first packs it into far fewer rows than connectivity order does.
    for g in ("CH_L", "CH_R"):
        groups[g].sort(key=lambda f: -size_mm(f)[1])
    # L73: the same for the gain blocks and the spine when PACK=height. With
    # the sixteen heatsinks (16.5 mm deep) in connectivity order, each block's
    # rectangle was 37-39 % parts (fill.py): every row as tall as its tallest
    # part. The sort is stable, so parts of one height keep their
    # connectivity order; the bias sensor goes back right after its NPN.
    if PACK == "height":
        for g in groups:
            if g in ("EDGE", "CH_L", "CH_R"):
                continue
            s = bias_sensor(groups[g])
            groups[g].sort(key=lambda f: -round(size_mm(f)[1], 1))
            if s:
                fs = [f for f in groups[g] if f.GetReference() == s][0]
                npn = [f for f in groups[g] if f.GetValue() == "MJE15032"][0]
                groups[g].remove(fs)
                groups[g].insert(groups[g].index(npn) + 1, fs)

    # Edge headers lie along their edge: pins in a row parallel to it.
    for f in groups["EDGE"]:
        w, h = size_mm(f)
        if h > w:
            f.SetOrientationDegrees(90)

    # Sizes of every group at its packing width.
    cg = 3.0 * gap   # corridor between columns, for the router
    widths = {"SPINE": 2 * 9.6 + 3 * spine_gap + 2 * 13.0}   # two relay columns + diodes
    for g in groups:
        if g in ("SPINE", "EDGE") or g.startswith("CH"):
            continue
        widths[g] = block_w
    gaps = {g: gap for g in groups}
    gaps["SPINE"] = spine_gap
    sizes = {g: trial_pack(groups[g], widths[g], gaps[g])
             for g in groups if g not in ("EDGE", "CH_L", "CH_R")}
    # The channel strip spans the two block columns as actually packed (the
    # packer may use less than block_w): sized from block_w it ran into the
    # relay spine (L49a, gap 1.0 / block_w 85: K1 over R261, K11 over C174).
    half_w = (max(sizes[g][0] for g in ("A_L", "B_L", "A_R", "B_R"))
              + max(sizes[g][0] for g in ("F1_L", "F2_L", "F1_R", "F2_R")) + cg)
    widths["CH_L"] = widths["CH_R"] = half_w
    for g in ("CH_L", "CH_R"):
        sizes[g] = trial_pack(groups[g], widths[g], gaps[g])

    rear_h = max(size_mm(f)[1] for f in groups["EDGE"]
                 if f.GetReference() in REAR_L + REAR_R) + STRIP
    front_h = max(size_mm(f)[1] for f in groups["EDGE"]
                  if f.GetReference() in FRONT) + STRIP
    col1 = max(sizes["A_L"][0], sizes["B_L"][0], sizes["A_R"][0], sizes["B_R"][0])
    col2 = max(sizes["F1_L"][0], sizes["F2_L"][0], sizes["F1_R"][0], sizes["F2_R"][0])
    ch_h = max(sizes["CH_L"][1], sizes["CH_R"][1])
    spine_w = sizes["SPINE"][0]
    row1 = max(sizes[g][1] for g in ("A_L", "A_R", "F1_L", "F1_R"))
    row2 = max(sizes[g][1] for g in ("B_L", "B_R", "F2_L", "F2_R"))
    body_h = max(ch_h + cg + row1 + gap + row2, sizes["SPINE"][1])
    W = 2 * MARGIN + 2 * (col1 + col2) + spine_w + 4 * cg
    H = 2 * MARGIN + rear_h + body_h + front_h + 2 * cg
    y_ch = MARGIN + rear_h + cg          # channel strip, right behind the RCAs
    y_r1 = y_ch + ch_h + cg              # blocks A and F1
    y_r2 = y_r1 + row1 + gap             # blocks B and F2

    # Columns, x of the left edge. Left half: F | A/B | SPINE, right mirrored.
    xl2 = MARGIN
    xl1 = xl2 + col2 + cg
    xs = xl1 + col1 + cg
    xr1 = xs + spine_w + cg
    xr2 = xr1 + col1 + cg
    rects = {}

    def put(g, x, y):
        w, h = shelf_pack(groups[g], widths[g], gaps[g], x, y)
        rects[g] = [round(x, 2), round(y, 2), round(w, 2), round(h, 2)]

    put("CH_L", xl2, y_ch)
    put("F1_L", xl2, y_r1)
    put("F2_L", xl2, y_r2)
    put("A_L", xl1 + col1 - sizes["A_L"][0], y_r1)
    put("B_L", xl1 + col1 - sizes["B_L"][0], y_r2)
    put("SPINE", xs, MARGIN + rear_h + cg)
    put("A_R", xr1, y_r1)
    put("B_R", xr1, y_r2)
    put("F1_R", xr2 + col2 - sizes["F1_R"][0], y_r1)
    put("F2_R", xr2 + col2 - sizes["F2_R"][0], y_r2)
    put("CH_R", xr1, y_ch)

    # Edge headers: rear strip, left half outer -> spine, right mirrored.
    edge = {f.GetReference(): f for f in groups["EDGE"]}
    pitch_l = (xs - MARGIN - 2 * HOLE_INSET) / len(REAR_L)
    for i, r in enumerate(REAR_L):
        move_box_to(edge[r], MARGIN + 2 * HOLE_INSET + i * pitch_l, MARGIN)
    for i, r in enumerate(REAR_R):
        w, _ = size_mm(edge[r])
        move_box_to(edge[r], W - MARGIN - 2 * HOLE_INSET - i * pitch_l - w, MARGIN)
    # Front strip: centred row, the two volume headers at the ends of it.
    fw = sum(size_mm(edge[r])[0] for r in FRONT) + gap * 4 * (len(FRONT) - 1)
    x = (W - fw) / 2
    for r in FRONT:
        w, h = size_mm(edge[r])
        move_box_to(edge[r], x, H - MARGIN - h)
        x += w + 4 * gap

    for hx, hy in ((HOLE_INSET, HOLE_INSET), (W - HOLE_INSET, HOLE_INSET),
                   (HOLE_INSET, H - HOLE_INSET), (W - HOLE_INSET, H - HOLE_INSET)):
        add_hole(board, hx, hy)
    outline(board, W, H)

    # The thermal pair: MJE15032 to its MMBT5551, per block, centre to centre.
    pairs = {}
    for g in groups:
        if g in ("SPINE", "EDGE") or g.startswith("CH"):
            continue
        q = {f.GetValue(): f for f in groups[g]}
        s = bias_sensor(groups[g])
        if "MJE15032" in q and s:
            sf = board.FindFootprintByReference(s)
            a, b = q["MJE15032"].GetPosition(), sf.GetPosition()
            # centre to centre (L49a's figure) and courtyard edge to edge
            ca, cb = crt_box(q["MJE15032"]), crt_box(sf)
            ex = max(0, max(ca.GetX(), cb.GetX()) - min(ca.GetRight(), cb.GetRight()))
            ey = max(0, max(ca.GetY(), cb.GetY()) - min(ca.GetBottom(), cb.GetBottom()))
            pairs[g] = {"npn": q["MJE15032"].GetReference(), "sensor": s,
                        "mm": round(pcbnew.ToMM(int(math.hypot(a.x - b.x, a.y - b.y))), 2),
                        "courtyard_gap_mm": round(pcbnew.ToMM(int(math.hypot(ex, ey))), 2)}

    # L73: the heatsinks at collector potential must not touch. Gap between
    # their courtyards (which enclose the heatsink, footprint in
    # library/preamp.pretty), every pair, and the smallest NPN-PNP gap (VPLUS
    # against VMINUS: a contact there shorts the rails).
    hs = [f for f in board.GetFootprints() if "WA-T220" in str(f.GetFPID().GetLibItemName())]

    def box_gap(a, b):
        ex = max(0, max(a.GetX(), b.GetX()) - min(a.GetRight(), b.GetRight()))
        ey = max(0, max(a.GetY(), b.GetY()) - min(a.GetBottom(), b.GetBottom()))
        return pcbnew.ToMM(int(math.hypot(ex, ey)))

    hs_pairs = []
    for i in range(len(hs)):
        for j in range(i + 1, len(hs)):
            hs_pairs.append((round(box_gap(crt_box(hs[i]), crt_box(hs[j])), 2),
                             hs[i].GetReference(), hs[j].GetReference(),
                             hs[i].GetValue() != hs[j].GetValue()))
    hs_pairs.sort()
    heatsinks = {"count": len(hs),
                 "min_gap_mm": hs_pairs[0] if hs_pairs else None,
                 "min_gap_npn_pnp_mm": next((p for p in hs_pairs if p[3]), None),
                 "closest_five": hs_pairs[:5]}

    # Overlap check between courtyards (the packer must not produce any).
    boxes = [(f.GetReference(), crt_box(f)) for f in board.GetFootprints()
             if not f.GetReference().startswith("H")]
    overlaps = []
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            if boxes[i][1].Intersects(boxes[j][1]):
                overlaps.append([boxes[i][0], boxes[j][0]])

    # Silkscreen: a reference that would land on a neighbour's courtyard is
    # moved to F.Fab (still on the assembly drawing), and the mounting holes
    # carry none. Cosmetic, but it keeps the DRC at zero without exclusions.
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

    out = os.path.join(out_dir, "audio_placed.kicad_pcb")
    board.Save(out)
    info = {"gap_mm": gap, "spine_gap_mm": spine_gap, "block_w_mm": block_w, "pack": PACK,
            "board_mm": [round(W, 1), round(H, 1)],
            "area_cm2": round(W * H / 100, 1),
            "groups": rects, "group_counts": {g: len(v) for g, v in groups.items()},
            "thermal_pairs": pairs, "heatsinks": heatsinks,
            "courtyard_overlaps": overlaps,
            "refs_moved_to_fab": moved_refs}
    with open(os.path.join(out_dir, "placement.json"), "w") as fh:
        json.dump(info, fh, indent=1)
    print(json.dumps({k: info[k] for k in ("board_mm", "area_cm2", "group_counts")}))
    print("thermal pairs:", pairs)
    print("heatsinks:", heatsinks)
    print("courtyard overlaps:", len(overlaps), overlaps[:5])
    print("saved:", out)


if __name__ == "__main__":
    main()
