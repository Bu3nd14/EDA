#!/usr/bin/env python3
"""
L49a, step 3 of 3: the Specctra round trip for Freerouting.

Run with KiCad's bundled Python 3.9 (limitations #1), as in
smoke/route_board.py:

  .../python3.9 layout/preamp/audio/route.py export <out_dir>
  /opt/homebrew/opt/openjdk/bin/java -jar scripts/tools/freerouting.jar \
      -de <out_dir>/audio.dsn -do <out_dir>/audio.ses -mp <passes>
  .../python3.9 layout/preamp/audio/route.py import <out_dir>

export: audio_placed.kicad_pcb -> audio.dsn
import: audio_placed.kicad_pcb + audio.ses -> audio_routed.kicad_pcb.
ImportSpecctraSES only answers True/False (limitations #9), so the import
counts what actually arrived and refuses to save a board with no tracks.
"""
import collections
import os
import sys

import pcbnew


def export_dsn(out_dir):
    board = pcbnew.LoadBoard(os.path.join(out_dir, "audio_placed.kicad_pcb"))
    dsn = os.path.join(out_dir, "audio.dsn")
    ok = pcbnew.ExportSpecctraDSN(board, dsn)
    print("ExportSpecctraDSN:", ok, dsn, os.path.getsize(dsn) if os.path.exists(dsn) else 0)
    return 0 if ok else 1


def import_ses(out_dir):
    board = pcbnew.LoadBoard(os.path.join(out_dir, "audio_placed.kicad_pcb"))
    ok = pcbnew.ImportSpecctraSES(board, os.path.join(out_dir, "audio.ses"))
    print("ImportSpecctraSES:", ok)
    kinds = collections.Counter(type(t).__name__ for t in board.Tracks())
    print("items imported:", dict(kinds))
    if not ok or not kinds:
        print("REFUSED: nothing imported, board not saved")
        return 1
    length = sum(pcbnew.ToMM(t.GetLength()) for t in board.Tracks()
                 if type(t).__name__ == "PCB_TRACK")
    print("track length mm:", round(length))
    # Freerouting 2.4.1 necks tracks down to 0.1874 mm at some SOIC-8 pins
    # (L49a: 32 short segments, 0.8-2 mm) even with
    # FREEROUTING__ROUTER__AUTOMATIC_NECKDOWN=false. The technology chosen
    # by the user is >= 0.25 mm, so they are widened back here and the DRC
    # that follows judges the clearances: nothing is hidden.
    min_w = board.GetDesignSettings().m_TrackMinWidth
    widened = 0
    for t in board.Tracks():
        if type(t).__name__ == "PCB_TRACK" and t.GetWidth() < min_w:
            t.SetWidth(min_w)
            widened += 1
    print("tracks widened to the minimum width:", widened)
    out = os.path.join(out_dir, "audio_routed.kicad_pcb")
    board.Save(out)
    print("saved:", out)
    return 0


if __name__ == "__main__":
    mode, out_dir = sys.argv[1], sys.argv[2]
    sys.exit(export_dsn(out_dir) if mode == "export" else import_ses(out_dir))
