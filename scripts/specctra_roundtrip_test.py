#!/usr/bin/env python3
"""
Tests the Specctra DSN export / SES import round trip using KiCad's bundled
pcbnew module + the external Freerouting autorouter (not bundled with KiCad;
downloaded separately as a plain jar, requires a JRE).

Run with the KiCad-bundled python3.9:
  /Users/roberto/Applications/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3.9 \
      /Users/roberto/EDA/scripts/specctra_roundtrip_test.py

Prerequisites established during testing (2026-09-07):
  - Freerouting jar downloaded to /Users/roberto/EDA/scripts/tools/freerouting.jar
    (https://github.com/freerouting/freerouting/releases/download/v2.4.1/freerouting-2.4.1.jar)
  - A JRE was NOT present out of the box (macOS java stub only prompts to
    install). Installed via `brew install openjdk` (no sudo needed for basic
    CLI use; only the system-wide symlink step in the brew caveats needs sudo,
    which was NOT done/needed for this test).
  - Invoke freerouting with:
      PATH="/opt/homebrew/opt/openjdk/bin:$PATH" java -jar freerouting.jar \
          -de <in>.dsn -do <out>.ses -mp 1 -l en
"""
import pcbnew
import os

PCB_UNROUTED = "/Users/roberto/EDA/pcb/test_board_unrouted.kicad_pcb"
DSN_OUT = "/Users/roberto/EDA/pcb/test_board_unrouted.dsn"
SES_IN = "/Users/roberto/EDA/pcb/test_board_freerouted.ses"  # produced by freerouting, external step
PCB_ROUTED_OUT = "/Users/roberto/EDA/pcb/test_board_ses_imported.kicad_pcb"


def export_dsn():
    board = pcbnew.LoadBoard(PCB_UNROUTED)
    ok = pcbnew.ExportSpecctraDSN(board, DSN_OUT)
    print("ExportSpecctraDSN:", ok, "->", DSN_OUT, "exists:", os.path.exists(DSN_OUT))
    return ok


def import_ses():
    board = pcbnew.LoadBoard(PCB_UNROUTED)
    print("Tracks before import:", len(list(board.Tracks())))
    ok = pcbnew.ImportSpecctraSES(board, SES_IN)
    print("ImportSpecctraSES:", ok)
    print("Tracks after import:", len(list(board.Tracks())))
    for t in board.Tracks():
        print(" ", type(t).__name__, "net=", t.GetNetname())
    pcbnew.SaveBoard(PCB_ROUTED_OUT, board)
    print("Saved routed board to:", PCB_ROUTED_OUT)
    return ok


if __name__ == "__main__":
    export_dsn()
    # -- external step (not run from this script) --
    #   PATH="/opt/homebrew/opt/openjdk/bin:$PATH" java -jar \
    #     /Users/roberto/EDA/scripts/tools/freerouting.jar \
    #     -de /Users/roberto/EDA/pcb/test_board_unrouted.dsn \
    #     -do /Users/roberto/EDA/pcb/test_board_freerouted.ses -mp 1 -l en
    if os.path.exists(SES_IN):
        import_ses()
    else:
        print(f"NOTE: {SES_IN} not found - run freerouting (see comment above) first.")
