#!/usr/bin/env python3
"""
Place the 3 footprints of the RC smoke-test board on a simple grid layout.
Must be run with the KiCad BUNDLED python3.9 interpreter (pcbnew only lives
there):

  /Users/roberto/Applications/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3.9 \
      /Users/roberto/EDA/smoke/place_components.py
"""
import pcbnew

BOARD_PATH = "/Users/roberto/EDA/smoke/rc_circuit.kicad_pcb"

# Simple left-to-right placement mirroring circuit topology: V1 -> R1 -> C1
POSITIONS_MM = {
    "V1": (30.0, 40.0),
    "R1": (45.0, 40.0),
    "C1": (60.0, 40.0),
}
ROTATIONS_DEG = {
    "V1": 0,
    "R1": 90,
    "C1": 90,
}

board = pcbnew.LoadBoard(BOARD_PATH)
for fp in board.GetFootprints():
    ref = fp.GetReference()
    if ref in POSITIONS_MM:
        x_mm, y_mm = POSITIONS_MM[ref]
        fp.SetPosition(pcbnew.VECTOR2I_MM(x_mm, y_mm))
        fp.SetOrientationDegrees(ROTATIONS_DEG[ref])
        print(f"Placed {ref} at ({x_mm}, {y_mm}) mm, rot={ROTATIONS_DEG[ref]} deg")
    else:
        print(f"WARNING: no placement rule for {ref}, leaving as-is")

# Draw a simple board outline on Edge.Cuts so the board has a defined shape.
outline_pts_mm = [(10, 20), (80, 20), (80, 60), (10, 60)]
for i in range(len(outline_pts_mm)):
    x1, y1 = outline_pts_mm[i]
    x2, y2 = outline_pts_mm[(i + 1) % len(outline_pts_mm)]
    seg = pcbnew.PCB_SHAPE(board)
    seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
    seg.SetStart(pcbnew.VECTOR2I_MM(x1, y1))
    seg.SetEnd(pcbnew.VECTOR2I_MM(x2, y2))
    seg.SetLayer(pcbnew.Edge_Cuts)
    seg.SetWidth(pcbnew.FromMM(0.15))
    board.Add(seg)

pcbnew.Refresh = getattr(pcbnew, "Refresh", None)
board.Save(BOARD_PATH)
print("Saved:", BOARD_PATH)
