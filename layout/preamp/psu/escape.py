#!/usr/bin/env python3
"""
L49b, step 2b: the regulators' pin escape, laid before the router.

  .../python3.9 layout/preamp/psu/escape.py <out_dir>

Edits <out_dir>/psu_placed.kicad_pcb in place and writes escape.json.

Why: on the three VQFN-20 regulators (U501 TPS7A4701, U502 TPS7A3301, U503
TPS7A4701) the source joins two pins of one net with ONE pin between them on
the same side - IN on 13 and 15 around NR on 14, OUT on 1 and 3 around the
unconnected 2. At 0.65 mm pitch Freerouting does not go round the middle pin:
seven connections stayed open in every run (L49b, iterations 4-7, gaps 2.5
and 3.0 mm, with and without neckdown). This lays what a designer would:
- middle pin WITHOUT a net: a bridge just past the pads' tips;
- middle pin WITH a net (NR): a via right past its tip, and the bridge round
  the via; NR then leaves from the via on the other layer.
Pad geometry from the footprint (Texas_RGW0020A_..._ThermalVias): pads
1.025 x 0.35 mm at 0.65 mm pitch. Every clearance below, worked by hand, is
>= 0.30 mm against 0.25; the DRC that follows checks them again. The tracks
are 0.35 mm (the neck the user accepted: "stretta solo al piedino") and
LOCKED, so the router keeps them.
"""
import json
import math
import os
import sys

import pcbnew

REGULATORS = ("U501", "U502", "U503")
NET_TIES = ("NT501",)
PAD_HALF_LEN = 1.025 / 2
W_NECK = 0.35
VIA_D, VIA_DRILL = 0.8, 0.4


def mm(v):
    return pcbnew.FromMM(v)


def vec(p):
    return (pcbnew.ToMM(p.x), pcbnew.ToMM(p.y))


def add(a, b, k=1.0):
    return (a[0] + k * b[0], a[1] + k * b[1])


def unit(a, b):
    d = (b[0] - a[0], b[1] - a[1])
    n = math.hypot(*d)
    return (d[0] / n, d[1] / n)


def outward(center, p):
    """Axis-aligned unit vector from the package centre through a side pad."""
    dx, dy = p[0] - center[0], p[1] - center[1]
    return (math.copysign(1, dx), 0.0) if abs(dx) > abs(dy) else (0.0, math.copysign(1, dy))


def track(board, net, pts, width):
    for a, b in zip(pts, pts[1:]):
        t = pcbnew.PCB_TRACK(board)
        t.SetStart(pcbnew.VECTOR2I(mm(a[0]), mm(a[1])))
        t.SetEnd(pcbnew.VECTOR2I(mm(b[0]), mm(b[1])))
        t.SetWidth(mm(width))
        t.SetLayer(pcbnew.F_Cu)
        t.SetNet(net)
        t.SetLocked(True)
        board.Add(t)


def via(board, net, p):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(pcbnew.VECTOR2I(mm(p[0]), mm(p[1])))
    v.SetWidth(mm(VIA_D))
    v.SetDrill(mm(VIA_DRILL))
    v.SetNet(net)
    v.SetLocked(True)
    board.Add(v)


def anchor(board, net, start, at, anchored, done, ref, width=None):
    """One ANCHOR via per net group of a regulator: the 1.0 mm rail tracks
    land on it, never on a 0.65 mm pitch pin. Without anchors the router had to
    neck down at the pins itself (Freerouting's automatic neckdown), and left
    2-8 connections open in a different place on every run (L49b, it. 5-13)."""
    # Up to two per net group (the corner's and the bridge's): with one only,
    # the corner's sat against a neighbour and U503's RAW_V group stayed
    # unrouted (iterations 22-23). The one the router does not use goes.
    key = (ref, net.GetNetname(), round(at[0], 2), round(at[1], 2))
    if key in anchored:
        return
    anchored.add(key)
    track(board, net, [start, at], width or W_NECK)
    via(board, net, at)
    # route.py import removes an anchor the router did not use (with its stub)
    done.append({"ref": ref, "net": net.GetNetname(), "kind": "anchor via",
                 "at_mm": [round(at[0], 4), round(at[1], 4)],
                 "from_mm": [round(start[0], 4), round(start[1], 4)]})


def main():
    out_dir = sys.argv[1]
    path = os.path.join(out_dir, "psu_placed.kicad_pcb")
    board = pcbnew.LoadBoard(path)
    done = []
    anchored = set()
    for ref in REGULATORS:
        fp = board.FindFootprintByReference(ref)
        center = vec(fp.GetPosition())
        pads = {p.GetNumber(): p for p in fp.Pads() if p.GetNumber() != "21"}
        num = {int(n): p for n, p in pads.items() if n.isdigit()}
        ep_net = [p for p in fp.Pads() if p.GetNumber() == "21"][0].GetNetname()
        # 1. Pins on the exposed pad's own net (ground / return) go INWARD into
        #    it: pad's inner end at 1.85 mm from the centre, the pad's edge at
        #    1.575, the stub ends inside it; 0.30 mm from the neighbours.
        for n, p in sorted(num.items()):
            if p.GetNetname() == ep_net:
                P = vec(p.GetPosition())
                o = outward(center, P)
                track(board, p.GetNet(), [add(P, o, -0.3), add(P, o, -0.9)], W_NECK)
                done.append({"ref": ref, "pins": [n, 21], "kind": "to exposed pad"})
        # 2. Corner pairs of one net (5-6, 10-11, 15-16, 20-1): an L outside
        #    the corner, 0.3 mm past both tips; 0.30 mm from the next pin's
        #    side, 0.30 mm past the next pin's tip at the leg's end cap.
        for a, b in ((5, 6), (10, 11), (15, 16), (20, 1)):
            pa, pb = num.get(a), num.get(b)
            if not pa or not pb or not pa.GetNetname() or pa.GetNetname() != pb.GetNetname():
                continue
            if pa.GetNetname() == ep_net:
                continue                      # both already in the exposed pad
            Pa, Pb = vec(pa.GetPosition()), vec(pb.GetPosition())
            oa, ob = outward(center, Pa), outward(center, Pb)
            ea = add(Pa, oa, PAD_HALF_LEN + 0.3)
            eb = add(Pb, ob, PAD_HALF_LEN + 0.3)
            # the corner: ea moved along ob to eb's outward line
            k = (eb[0] - ea[0]) * ob[0] + (eb[1] - ea[1]) * ob[1]
            q = add(ea, ob, k)
            track(board, pa.GetNet(), [add(Pa, oa, 0.3), ea, q, eb, add(Pb, ob, 0.3)], W_NECK)
            done.append({"ref": ref, "pins": [a, b], "kind": "corner"})
            # anchor 1.0 mm out of the corner, on the diagonal
            d = unit((0.0, 0.0), add(oa, ob))
            anchor(board, pa.GetNet(), q, add(q, d, 1.0), anchored, done, ref)
        # 3. Pairs of one net with one pin between them on the same side.
        for a in sorted(num):
            b, c = a + 2, a + 1
            if b not in num or (a - 1) // 5 != (b - 1) // 5:
                continue                      # not on the same side
            pa, pb, pc = num[a], num[b], num[c]
            if not pa.GetNetname() or pa.GetNetname() != pb.GetNetname():
                continue
            if pa.GetNetname() == ep_net:
                continue                      # both already in the exposed pad
            if pc.GetNetname() == pa.GetNetname():
                continue                      # three in a row: the router manages
            Pa, Pb, Pc = vec(pa.GetPosition()), vec(pb.GetPosition()), vec(pc.GetPosition())
            o = outward(center, Pc)
            tip = lambda P: add(P, o, PAD_HALF_LEN)          # noqa: E731
            s = unit(Pc, Pa)                  # along the side, from c towards a
            net = pa.GetNet()
            if not pc.GetNetname():
                # Bridge 0.5 mm past the tips: its edge is 0.325 mm from c's tip,
                # its legs 0.30 mm from c's sides.
                pts = [add(Pa, o, 0.3), add(tip(Pa), o, 0.5), add(tip(Pb), o, 0.5),
                       add(Pb, o, 0.3)]
                track(board, net, pts, W_NECK)
                done.append({"ref": ref, "pins": [a, b], "around": c, "kind": "bridge"})
                # anchor 1.5 mm past c's tip: 1.17 mm from a's and b's corners
                anchor(board, net, add(tip(Pc), o, 0.5), add(tip(Pc), o, 1.5), anchored,
                       done, ref)
            else:
                # c out through a via 0.9 mm past its tip (0.62 mm from the
                # corners of a and b). The bridge leaves a and b STRAIGHT out to
                # 0.3 mm past the tips (0.30 mm from c's and the outer
                # neighbour's sides, 0.31 mm from the via), steps out to 0.95 mm
                # from c's axis (0.375 mm from the via) and crosses 1.8 mm past
                # the tips (0.325 mm below the via). Iteration 8 stepped out
                # diagonally from inside the pad and passed 0.22 mm from pin 12.
                vpos = add(tip(Pc), o, 0.9)
                track(board, pc.GetNet(), [add(Pc, o, 0.3), vpos], W_NECK)
                via(board, pc.GetNet(), vpos)
                a1 = add(tip(Pa), o, 0.3)
                a2 = add(add(tip(Pc), o, 0.75), s, 0.95)
                a3 = add(add(tip(Pc), o, 1.8), s, 0.95)
                b3 = add(add(tip(Pc), o, 1.8), s, -0.95)
                b2 = add(add(tip(Pc), o, 0.75), s, -0.95)
                b1 = add(tip(Pb), o, 0.3)
                track(board, net, [add(Pa, o, 0.3), a1, a2, a3, b3, b2, b1, add(Pb, o, 0.3)],
                      W_NECK)
                done.append({"ref": ref, "pins": [a, b], "around": c, "kind": "via+bridge",
                             "middle_net": pc.GetNetname()})
                # anchor 2.9 mm past c's tip: 0.525 mm past the cross. The middle
                # pin's own net leaves its via on the other layer, sideways.
                anchor(board, net, add(tip(Pc), o, 1.8), add(tip(Pc), o, 2.9), anchored,
                       done, ref)
    # The star tie NT501 (GND to RLY_RET, psu.py): two 0.5 mm round pads 1.0 mm
    # apart, joined by the footprint's copper bar, each reachable from its outer
    # side only. It stayed unrouted in iterations 16 and 17: an anchor each,
    # 1.5 mm out along the tie's axis (0.5 mm stub, the pad's own width).
    for ref in NET_TIES:
        fp = board.FindFootprintByReference(ref)
        p1, p2 = list(fp.Pads())[:2]
        for p, other in ((p1, p2), (p2, p1)):
            P, Q = vec(p.GetPosition()), vec(other.GetPosition())
            u = unit(Q, P)
            anchor(board, p.GetNet(), P, add(P, u, 1.5), anchored, done, ref, width=0.5)
    board.Save(path)
    with open(os.path.join(out_dir, "escape.json"), "w") as fh:
        json.dump(done, fh, indent=1)
    for d in done:
        print(d)
    print("escapes laid:", len(done))


if __name__ == "__main__":
    main()
