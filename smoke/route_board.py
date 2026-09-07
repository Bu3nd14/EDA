#!/usr/bin/env python3
"""
DSN export / Freerouting / SES import round trip for the RC smoke-test board.
Run with the KiCad-bundled python3.9 (see specctra_roundtrip_test.py for the
pattern this was copied from).

Usage:
  # 1) export DSN
  .../python3.9 route_board.py export

  # 2) externally run freerouting (not scriptable from inside pcbnew):
  PATH="/opt/homebrew/opt/openjdk/bin:$PATH" java -jar \
      /Users/roberto/EDA/scripts/tools/freerouting.jar \
      -de /Users/roberto/EDA/smoke/rc_circuit.dsn \
      -do /Users/roberto/EDA/smoke/rc_circuit.ses -mp 1 -l en

  # 3) import SES
  .../python3.9 route_board.py import
"""
import pcbnew
import os
import sys

PCB_IN = "/Users/roberto/EDA/smoke/rc_circuit.kicad_pcb"
DSN_OUT = "/Users/roberto/EDA/smoke/rc_circuit.dsn"
SES_IN = "/Users/roberto/EDA/smoke/rc_circuit.ses"
PCB_ROUTED_OUT = "/Users/roberto/EDA/smoke/rc_circuit_routed.kicad_pcb"


def export_dsn():
    board = pcbnew.LoadBoard(PCB_IN)
    ok = pcbnew.ExportSpecctraDSN(board, DSN_OUT)
    print("ExportSpecctraDSN:", ok, "->", DSN_OUT, "exists:", os.path.exists(DSN_OUT))
    return ok


def import_ses():
    board = pcbnew.LoadBoard(PCB_IN)
    print("Tracks before import:", len(list(board.Tracks())))
    ok = pcbnew.ImportSpecctraSES(board, SES_IN)
    print("ImportSpecctraSES:", ok)
    tracks = list(board.Tracks())
    print("Tracks after import:", len(tracks))
    for t in tracks:
        print(" ", type(t).__name__, "net=", t.GetNetname(), "layer=", board.GetLayerName(t.GetLayer()))
    board.Save(PCB_ROUTED_OUT)
    print("Saved routed board to:", PCB_ROUTED_OUT)
    return ok


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "export"
    if mode == "export":
        export_dsn()
    elif mode == "import":
        import_ses()
    else:
        print("usage: route_board.py [export|import]")
