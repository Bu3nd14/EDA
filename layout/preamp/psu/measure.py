#!/usr/bin/env python3
"""
L49b: the numbers the supply trial board gives back to the project.

  .../python3.9 layout/preamp/psu/measure.py <out_dir>

Reads <out_dir>/psu_routed.kicad_pcb and placement.json, writes
<out_dir>/measure.json and prints it:
- board size, courtyard area and fill; tracks and vias; length per class;
- THE MAINS DISTANCE: the smallest copper-to-copper distance, on the same
  layer, between a mains net (MAINS class) and any other net, from the real
  pad and track shapes (pcbnew's SHAPE.Collide, bisected to 0.01 mm). It is
  the creepage the board surface gives; the DRC judges the same thing
  (psu.kicad_dru), this measures it, independently of the rule file;
- the same between the two mains nets of a pair (L to N, functional).
"""
import collections
import json
import os
import sys

import pcbnew

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_board as mb  # noqa: E402  (the class widths, one source)

# The netclass object is not usable from Python here (GetEffectiveNetClass()
# returns a bare SwigPyObject): the widths come from make_board.py.
CLASS_MM = {"POWER": mb.POWER_TRACK_MM, "POWER_WIDE": mb.POWER_WIDE_TRACK_MM,
            "MAINS": mb.MAINS_TRACK_MM}
MAINS = set(mb.MAINS_NETS)
LAYERS = (pcbnew.F_Cu, pcbnew.B_Cu)
REACH_MM = 25.0     # pairs further apart than this are not bisected


def items(board):
    """(net, layer, shape, label) for every pad and track on copper."""
    out = []
    for f in board.GetFootprints():
        for p in f.Pads():
            for L in LAYERS:
                if p.IsOnLayer(L) and p.GetNetname():
                    out.append((p.GetNetname(), L, p.GetEffectiveShape(L),
                                f"{f.GetReference()}.{p.GetNumber()}"))
    for t in board.Tracks():
        for L in LAYERS:
            if t.IsOnLayer(L) and t.GetNetname():
                kind = "via" if type(t).__name__ == "PCB_VIA" else "track"
                out.append((t.GetNetname(), L, t.GetEffectiveShape(L), kind))
    return out


def distance(a, b):
    """Smallest gap between two shapes, mm, or None beyond REACH_MM."""
    if not a.Collide(b, pcbnew.FromMM(REACH_MM)):
        return None
    if a.Collide(b, 0):
        return 0.0
    lo, hi = 0.0, REACH_MM
    while hi - lo > 0.01:
        mid = (lo + hi) / 2
        if a.Collide(b, pcbnew.FromMM(mid)):
            hi = mid
        else:
            lo = mid
    return round(hi, 2)


def nearest(pairs):
    best = None
    for (na, L, sa, la), (nb, _, sb, lb) in pairs:
        d = distance(sa, sb)
        if d is not None and (best is None or d < best[0]):
            best = (d, f"{na} {la}", f"{nb} {lb}", "F.Cu" if L == pcbnew.F_Cu else "B.Cu")
    return best


def main():
    out_dir = sys.argv[1]
    b = pcbnew.LoadBoard(os.path.join(out_dir, "psu_routed.kicad_pcb"))
    place = json.load(open(os.path.join(out_dir, "placement.json")))
    W, H = place["board_mm"]

    cls_path = os.path.join(out_dir, "classes.json")
    if os.path.exists(cls_path):           # the widths this board was made with
        CLASS_MM.update({k: v for k, v in json.load(open(cls_path)).items()
                         if k in CLASS_MM})
    its = items(b)
    mains = [i for i in its if i[0] in MAINS]
    other = [i for i in its if i[0] not in MAINS]
    to_lv = nearest(((m, o) for m in mains for o in other if m[1] == o[1]))
    l_n = nearest(((m, o) for m in mains for o in mains
                   if m[1] == o[1] and m[0] < o[0]))

    length = collections.Counter()
    vias = 0
    widths = collections.defaultdict(set)
    for t in b.Tracks():
        if type(t).__name__ == "PCB_VIA":
            vias += 1
            continue
        length[t.GetNetClassName()] += pcbnew.ToMM(t.GetLength())
        widths[t.GetNetClassName()].add(round(pcbnew.ToMM(t.GetWidth()), 3))
    # Necks: segments narrower than their class (the user's choice: wide
    # rails, narrowed only into the regulators' pins). Each with the pad it
    # ends on, so "only at the pins" is a measured statement.
    pads = [(f.GetReference(), p) for f in b.GetFootprints() for p in f.Pads()]
    necks = []
    for t in b.Tracks():
        if type(t).__name__ == "PCB_VIA":
            continue
        cls_w = pcbnew.FromMM(CLASS_MM.get(t.GetNetClassName(), mb.TRACK_MM))
        if t.GetWidth() >= cls_w:
            continue
        ends = sorted({f"{r}.{p.GetNumber()}" for r, p in pads
                       if p.GetNetname() == t.GetNetname()
                       and (p.HitTest(t.GetStart()) or p.HitTest(t.GetEnd()))})
        necks.append({"net": t.GetNetname(), "width_mm": round(pcbnew.ToMM(t.GetWidth()), 3),
                      "class_mm": round(pcbnew.ToMM(cls_w), 3),
                      "length_mm": round(pcbnew.ToMM(t.GetLength()), 2), "pads": ends})
    crt = 0.0
    for f in b.GetFootprints():
        if f.GetReference().startswith("H"):
            continue
        bb = f.GetCourtyard(pcbnew.F_CrtYd).BBox()
        crt += pcbnew.ToMM(bb.GetWidth()) * pcbnew.ToMM(bb.GetHeight())

    info = {"board_mm": [W, H], "area_cm2": round(W * H / 100, 1),
            "courtyard_cm2": round(crt / 100, 1), "fill": round(crt / (W * H), 3),
            "tracks_m": round(sum(length.values()) / 1000, 2), "vias": vias,
            "length_mm_by_class": {k: round(v) for k, v in sorted(length.items())},
            "track_widths_mm_by_class": {k: sorted(v) for k, v in sorted(widths.items())},
            "necks": {"count": len(necks),
                      "min_width_mm": min((n["width_mm"] for n in necks), default=None),
                      "max_length_mm": max((n["length_mm"] for n in necks), default=None),
                      "not_on_a_pad": [n for n in necks if not n["pads"]],
                      "parts": sorted({p.split(".")[0] for n in necks for p in n["pads"]}),
                      "list": necks},
            "mains_to_low_voltage_mm": to_lv[0] if to_lv else None,
            "mains_to_low_voltage_between": list(to_lv[1:]) if to_lv else None,
            "mains_L_to_N_mm": l_n[0] if l_n else None,
            "mains_L_to_N_between": list(l_n[1:]) if l_n else None}
    with open(os.path.join(out_dir, "measure.json"), "w") as fh:
        json.dump(info, fh, indent=1)
    print(json.dumps(info, indent=1))


if __name__ == "__main__":
    main()
