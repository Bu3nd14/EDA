#!/usr/bin/env python3
"""
L49b, step 3 of 3: the Specctra round trip for Freerouting, as L49a's
layout/preamp/audio/route.py, for the supply board.

  .../python3.9 layout/preamp/psu/route.py export <out_dir>
  /opt/homebrew/opt/openjdk/bin/java -jar scripts/tools/freerouting.jar \
      -de <out_dir>/psu.dsn -do <out_dir>/psu.ses -mp <passes>
  .../python3.9 layout/preamp/psu/route.py import <out_dir>

export: psu_placed.kicad_pcb -> psu.dsn
import: psu_placed.kicad_pcb + psu.ses -> psu_routed.kicad_pcb, plus
psu_routed.kicad_dru (the custom rules, psu.kicad_dru) next to it, which the
DRC that follows reads. ImportSpecctraSES only answers True/False
(limitations #9): the import counts what arrived and refuses an empty board.
"""
import collections
import json
import math
import os
import shutil
import sys

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))


# Mains to every other class, in the DSN's units (um): the trial reinforced
# creepage of make_board.py. KiCad's exporter writes one clearance per class,
# and the MAINS class carries the L-to-N figure; without this the router laid
# AC_N 2.40 mm from K501's coil pad (L49b, iteration 3: 7 DRC violations of
# psu.kicad_dru's "mains_to_low_voltage"). Specctra's class_class rule gives
# the pair its own clearance.
MAINS_TO_OTHERS_UM = 6400
OTHER_CLASSES = ("kicad_default", "POWER", "POWER_WIDE")


def add_mains_class_rules(dsn):
    text = open(dsn).read()
    cut = text.index("\n  (wiring")
    close = text.rindex(")", 0, cut)          # the end of (network ...)
    rules = "".join(
        f"\n    (class_class (classes MAINS {c})\n"
        f"      (rule (clearance {MAINS_TO_OTHERS_UM})))" for c in OTHER_CLASSES)
    with open(dsn, "w") as fh:
        fh.write(text[:close] + rules + "\n  " + text[close:])
    print("class_class rules added:", len(OTHER_CLASSES))


def export_dsn(out_dir):
    board = pcbnew.LoadBoard(os.path.join(out_dir, "psu_placed.kicad_pcb"))
    dsn = os.path.join(out_dir, "psu.dsn")
    ok = pcbnew.ExportSpecctraDSN(board, dsn)
    print("ExportSpecctraDSN:", ok, dsn, os.path.getsize(dsn) if os.path.exists(dsn) else 0)
    if ok:
        add_mains_class_rules(dsn)
    return 0 if ok else 1


def drop_unused_anchors(board, out_dir):
    """escape.py lays an anchor via per rail group; where the router landed
    elsewhere, or on the via's own layer only, the via joins nothing (a DRC
    warning, iterations 16 and 18). Such a via goes, and its stub with it
    unless a track lands on the stub. Found by geometry (escape.json), not by
    the locked flag, which the SES import may not keep. Everything is
    collected first and removed after: board.Tracks() is not iterable again
    once an item has been removed (iteration 19)."""
    path = os.path.join(out_dir, "escape.json")
    if not os.path.exists(path):
        return 0
    tol = pcbnew.FromMM(0.01)

    def near(p, q):
        return abs(p.x - q.x) <= tol and abs(p.y - q.y) <= tol

    tracks = [t for t in board.Tracks() if type(t).__name__ == "PCB_TRACK"]
    all_vias = [t for t in board.Tracks() if type(t).__name__ == "PCB_VIA"]
    doomed, added = [], []
    for e in json.load(open(path)):
        if e["kind"] != "anchor via":
            continue
        at = pcbnew.VECTOR2I(pcbnew.FromMM(e["at_mm"][0]), pcbnew.FromMM(e["at_mm"][1]))
        frm = pcbnew.VECTOR2I(pcbnew.FromMM(e["from_mm"][0]), pcbnew.FromMM(e["from_mm"][1]))
        vias = [v for v in all_vias if near(v.GetPosition(), at)]
        stub = [t for t in tracks
                if (near(t.GetStart(), at) and near(t.GetEnd(), frm))
                or (near(t.GetEnd(), at) and near(t.GetStart(), frm))]
        # A track touches the via when its end cap does: centre within the
        # via's radius plus the track's half width (iterations 22-24: tests on
        # the centre, then on the radius alone, removed vias in use).
        r = max((v.GetWidth(pcbnew.F_Cu) for v in vias), default=0) // 2
        others = [t for t in tracks if t not in stub and t.GetNetname() == e["net"]
                  and any(math.hypot(p.x - at.x, p.y - at.y) <= r + t.GetWidth() // 2
                          for p in (t.GetStart(), t.GetEnd()))]
        layers = {t.GetLayer() for t in stub + others}
        if not vias or len(layers) > 1:
            continue                  # the via joins two layers: it is used
        # A via whose copper touches a pad of its net is a joint too: in
        # iteration 24 an anchor overlapped D510's through-hole pad and was
        # the only link between U501's input group and the rest of RAW_P. On
        # one layer it is still a "dangling" via for the DRC, so it becomes
        # what it is: a track from its centre to the pad's, inside copper
        # that already touches.
        touching = [p for v in vias for f in board.GetFootprints() for p in f.Pads()
                    if p.GetNetname() == e["net"] and p.IsOnLayer(pcbnew.F_Cu)
                    and v.GetEffectiveShape(pcbnew.F_Cu).Collide(
                        p.GetEffectiveShape(pcbnew.F_Cu), 0)]
        if touching:
            for p in touching[:1]:
                t = pcbnew.PCB_TRACK(board)
                t.SetStart(at)
                t.SetEnd(p.GetPosition())
                t.SetWidth(stub[0].GetWidth() if stub else pcbnew.FromMM(0.35))
                t.SetLayer(pcbnew.F_Cu)
                t.SetNet(p.GetNet())
                added.append(t)
            doomed += vias
            continue
        # The via does nothing (iteration 18: "connected on only one layer").
        # Its stub goes too, unless the router landed on the stub or the via.
        on_stub = others or [t for t in tracks if t not in stub
                             and t.GetNetname() == e["net"]
                             and any(s.HitTest(t.GetStart()) or s.HitTest(t.GetEnd())
                                     for s in stub)
                             and not (near(t.GetStart(), frm) or near(t.GetEnd(), frm))]
        doomed += vias + ([] if on_stub else stub)
    for t in doomed:
        board.Remove(t)
    for t in added:
        board.Add(t)
    return len([t for t in doomed if type(t).__name__ == "PCB_VIA"])


def import_ses(out_dir):
    board = pcbnew.LoadBoard(os.path.join(out_dir, "psu_placed.kicad_pcb"))
    ok = pcbnew.ImportSpecctraSES(board, os.path.join(out_dir, "psu.ses"))
    print("ImportSpecctraSES:", ok)
    kinds = collections.Counter(type(t).__name__ for t in board.Tracks())
    print("items imported:", dict(kinds))
    if not ok or not kinds:
        print("REFUSED: nothing imported, board not saved")
        return 1
    length = sum(pcbnew.ToMM(t.GetLength()) for t in board.Tracks()
                 if type(t).__name__ == "PCB_TRACK")
    print("track length mm:", round(length))
    # Nothing is widened here (L49a's import did, for the fan-out necks of
    # limitations #50): with the fan-out off a narrow track is a finding, and
    # the DRC reports it.
    narrow = [t for t in board.Tracks() if type(t).__name__ == "PCB_TRACK"
              and t.GetWidth() < board.GetDesignSettings().m_TrackMinWidth]
    print("tracks below the minimum width:", len(narrow))
    if "keep" not in sys.argv[3:]:   # "keep": no cleanup, for comparing the DRC
        print("unused anchor vias removed:", drop_unused_anchors(board, out_dir))
    out = os.path.join(out_dir, "psu_routed.kicad_pcb")
    board.Save(out)
    shutil.copyfile(os.path.join(HERE, "psu.kicad_dru"),
                    os.path.join(out_dir, "psu_routed.kicad_dru"))
    print("saved:", out)
    return 0


if __name__ == "__main__":
    mode, out_dir = sys.argv[1], sys.argv[2]
    sys.exit(export_dsn(out_dir) if mode == "export" else import_ses(out_dir))
