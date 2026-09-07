#!/usr/bin/env python3
"""
KiCad pcbnew scripting capability test.
Run with the BUNDLED kicad python interpreter:
  /Users/roberto/Applications/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3.9 \
      /Users/roberto/EDA/scripts/pcbnew_test.py

Exercises Task B items 1-9 and 11 (DRC and gerber export are done via kicad-cli
in separate shell steps, see pcbnew_report.txt).
"""
import pcbnew
import os

BOARD_PATH = "/Users/roberto/EDA/pcb/test_board.kicad_pcb"
FP_LIB_BASE = "/Users/roberto/Applications/KiCad.app/Contents/SharedSupport/footprints"

def section(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)

# ---------------------------------------------------------------------
section("B1: Create board from scratch")
# ---------------------------------------------------------------------
board = pcbnew.CreateEmptyBoard()
print("Created board object:", board)
print("Type:", type(board))

# ---------------------------------------------------------------------
section("B2: Add footprints from standard libraries")
# ---------------------------------------------------------------------
def load_fp(lib_name, fp_name):
    lib_path = os.path.join(FP_LIB_BASE, lib_name + ".pretty")
    fp = pcbnew.FootprintLoad(lib_path, fp_name)
    if fp is None:
        raise RuntimeError(f"Failed to load {fp_name} from {lib_path}")
    return fp

r1 = load_fp("Resistor_SMD", "R_0805_2012Metric")
c1 = load_fp("Capacitor_SMD", "C_0805_2012Metric")
print("Loaded R_0805_2012Metric:", r1)
print("Loaded C_0805_2012Metric:", c1)

r1.SetReference("R1")
r1.SetValue("10k")
r1.SetPosition(pcbnew.VECTOR2I_MM(50, 50))
board.Add(r1)

c1.SetReference("C1")
c1.SetValue("100nF")
c1.SetPosition(pcbnew.VECTOR2I_MM(60, 50))
board.Add(c1)

print("Footprints added. Board footprint count:", len(board.GetFootprints()))

# save now so pos units function is confirmed available
pcbnew.SaveBoard(BOARD_PATH, board)
print("Saved board to:", BOARD_PATH, "exists:", os.path.exists(BOARD_PATH), "size:", os.path.getsize(BOARD_PATH))

# ---------------------------------------------------------------------
section("B3: Inspect footprints - enumerate ref/value/pos/orientation")
# ---------------------------------------------------------------------
for fp in board.GetFootprints():
    pos = fp.GetPosition()
    print(f"  ref={fp.GetReference()} value={fp.GetValue()} "
          f"pos=({pcbnew.ToMM(pos.x)}, {pcbnew.ToMM(pos.y)})mm "
          f"orientation={fp.GetOrientationDegrees()}deg "
          f"layer={fp.GetLayerName()}")

# ---------------------------------------------------------------------
section("B4: Move and rotate a footprint, verify persistence via reload")
# ---------------------------------------------------------------------
r1 = board.FindFootprintByReference("R1")
print("Before: pos=", r1.GetPosition(), "orient=", r1.GetOrientationDegrees())
r1.SetPosition(pcbnew.VECTOR2I_MM(45, 42))
r1.SetOrientationDegrees(90)
print("After (in-memory): pos=", r1.GetPosition(), "orient=", r1.GetOrientationDegrees())
pcbnew.SaveBoard(BOARD_PATH, board)

board2 = pcbnew.LoadBoard(BOARD_PATH)
r1_reloaded = board2.FindFootprintByReference("R1")
pos = r1_reloaded.GetPosition()
print(f"Reloaded from disk: pos=({pcbnew.ToMM(pos.x)}, {pcbnew.ToMM(pos.y)})mm "
      f"orient={r1_reloaded.GetOrientationDegrees()}deg")
assert abs(pcbnew.ToMM(pos.x) - 45) < 0.001
assert abs(pcbnew.ToMM(pos.y) - 42) < 0.001
assert abs(float(r1_reloaded.GetOrientationDegrees()) - 90.0) < 0.001
print("VERIFIED: move+rotate persisted correctly across save/reload")

# continue working on board2 from here on (freshly reloaded, most faithful)
board = board2

# ---------------------------------------------------------------------
section("B5: Query geometry - pads, bbox, courtyard")
# ---------------------------------------------------------------------
r1 = board.FindFootprintByReference("R1")
for pad in r1.Pads():
    ppos = pad.GetPosition()
    print(f"  R1 pad '{pad.GetPadName()}' pos=({pcbnew.ToMM(ppos.x)},{pcbnew.ToMM(ppos.y)})mm "
          f"net={pad.GetNetname()!r} size={pad.GetSize()}")

bbox = board.GetBoardEdgesBoundingBox()
print("Board edges bbox (no edge cuts drawn yet):", bbox.GetWidth(), bbox.GetHeight())

fp_bbox = r1.GetBoundingBox()
print(f"R1 bounding box: w={pcbnew.ToMM(fp_bbox.GetWidth())}mm h={pcbnew.ToMM(fp_bbox.GetHeight())}mm")

# courtyard
try:
    cy_polyset = r1.GetCourtyard(pcbnew.F_CrtYd)
    print("R1 F_CrtYd polygon outline count:", cy_polyset.OutlineCount())
    if cy_polyset.OutlineCount() > 0:
        outline = cy_polyset.Outline(0)
        print("  courtyard outline point count:", outline.PointCount())
except Exception as e:
    print("Courtyard query failed:", repr(e))

# ---------------------------------------------------------------------
section("B6/B7: Nets - enumerate, assign nets to pads")
# ---------------------------------------------------------------------
netinfo = board.GetNetInfo()
print("Existing net count (before assignment):", netinfo.GetNetCount())
for i in range(netinfo.GetNetCount()):
    ni = netinfo.GetNetItem(i)
    print(f"  net[{i}] code={ni.GetNetCode()} name={ni.GetNetname()!r}")

# Create a new net and assign it to pads of R1 and C1 to form a connection
new_net = pcbnew.NETINFO_ITEM(board, "NET_R1_C1")
board.Add(new_net)
print("Added net:", new_net.GetNetname(), "code:", new_net.GetNetCode())

r1 = board.FindFootprintByReference("R1")
c1 = board.FindFootprintByReference("C1")

r1_pad2 = r1.Pads()[1]  # pad "2"
c1_pad1 = c1.Pads()[0]  # pad "1"
r1_pad2.SetNet(new_net)
c1_pad1.SetNet(new_net)
print(f"Assigned net '{new_net.GetNetname()}' to R1 pad {r1_pad2.GetPadName()} and C1 pad {c1_pad1.GetPadName()}")

# also net for the other two pads for completeness (GND-like)
gnd_net = pcbnew.NETINFO_ITEM(board, "GND")
board.Add(gnd_net)
r1_pad1 = r1.Pads()[0]
c1_pad2 = c1.Pads()[1]
r1_pad1.SetNet(gnd_net)
c1_pad2.SetNet(gnd_net)
print(f"Assigned net 'GND' to R1 pad {r1_pad1.GetPadName()} and C1 pad {c1_pad2.GetPadName()}")

board.BuildConnectivity()
netinfo = board.GetNetInfo()
print("Net count after assignment:", netinfo.GetNetCount())
for i in range(netinfo.GetNetCount()):
    ni = netinfo.GetNetItem(i)
    print(f"  net[{i}] code={ni.GetNetCode()} name={ni.GetNetname()!r}")

pcbnew.SaveBoard(BOARD_PATH, board)
print("Saved board with net assignments.")

# ---------------------------------------------------------------------
section("B8: Create tracks (segments) between pads on a net, and a via")
# ---------------------------------------------------------------------
board = pcbnew.LoadBoard(BOARD_PATH)  # reload to work from clean persisted state
r1 = board.FindFootprintByReference("R1")
c1 = board.FindFootprintByReference("C1")

r1_pad2 = r1.Pads()[1]
c1_pad1 = c1.Pads()[0]
print("Connecting pad", r1_pad2.GetPadName(), "net=", r1_pad2.GetNetname(),
      "to pad", c1_pad1.GetPadName(), "net=", c1_pad1.GetNetname())

start = r1_pad2.GetPosition()
end = c1_pad1.GetPosition()

track = pcbnew.PCB_TRACK(board)
track.SetStart(start)
track.SetEnd(end)
track.SetWidth(pcbnew.FromMM(0.25))
track.SetLayer(pcbnew.F_Cu)
track.SetNet(r1_pad2.GetNet())
board.Add(track)
print(f"Added track from ({pcbnew.ToMM(start.x)},{pcbnew.ToMM(start.y)}) to "
      f"({pcbnew.ToMM(end.x)},{pcbnew.ToMM(end.y)}) on net {track.GetNetname()!r}")

# via attempt
try:
    via = pcbnew.PCB_VIA(board)
    via.SetPosition(pcbnew.VECTOR2I_MM(55, 50))
    via.SetWidth(pcbnew.FromMM(0.6))
    via.SetDrill(pcbnew.FromMM(0.3))
    via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    via.SetNet(r1_pad2.GetNet())
    board.Add(via)
    print("Added via at (55,50)mm, net:", via.GetNetname())
    via_ok = True
except Exception as e:
    print("Via creation failed:", repr(e))
    via_ok = False

pcbnew.SaveBoard(BOARD_PATH, board)
print("Saved board with track" + (" and via" if via_ok else " (no via)") + ".")

# ---------------------------------------------------------------------
section("B9: Create a copper zone (pour) and assign it a net")
# ---------------------------------------------------------------------
board = pcbnew.LoadBoard(BOARD_PATH)
gnd_net = board.FindNet("GND")
print("GND net found:", gnd_net, "code:", gnd_net.GetNetCode() if gnd_net else None)

zone = pcbnew.ZONE(board)
board.Add(zone)
zone.SetLayer(pcbnew.B_Cu)
zone.SetNet(gnd_net)
zone.SetIsFilled(False)

outline = pcbnew.SHAPE_POLY_SET()
pts = [(40, 40), (80, 40), (80, 70), (40, 70)]
chain = pcbnew.SHAPE_LINE_CHAIN()
for (x, y) in pts:
    chain.Append(pcbnew.VECTOR2I_MM(x, y))
chain.SetClosed(True)
outline.AddOutline(chain)
zone.SetOutline(outline)

print("Zone added: layer=", zone.GetLayerName(), "net=", zone.GetNetname())

# Fill zones
filler = pcbnew.ZONE_FILLER(board)
filled_zones = pcbnew.ZONES()
filled_zones.append(zone)
fill_ok = filler.Fill(filled_zones)
print("Zone fill executed, success:", fill_ok, "IsFilled after fill:", zone.IsFilled())

pcbnew.SaveBoard(BOARD_PATH, board)
print("Saved board with zone.")

# ---------------------------------------------------------------------
section("B5 (cont): board bbox now that footprints exist")
# ---------------------------------------------------------------------
board = pcbnew.LoadBoard(BOARD_PATH)
# Add board edge (Edge.Cuts) rectangle so bbox / gerber board outline is meaningful
edge_pts = [(30, 30), (90, 30), (90, 80), (30, 80)]
for i in range(len(edge_pts)):
    seg = pcbnew.PCB_SHAPE(board)
    seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
    seg.SetLayer(pcbnew.Edge_Cuts)
    x1, y1 = edge_pts[i]
    x2, y2 = edge_pts[(i + 1) % len(edge_pts)]
    seg.SetStart(pcbnew.VECTOR2I_MM(x1, y1))
    seg.SetEnd(pcbnew.VECTOR2I_MM(x2, y2))
    seg.SetWidth(pcbnew.FromMM(0.15))
    board.Add(seg)
pcbnew.SaveBoard(BOARD_PATH, board)

board = pcbnew.LoadBoard(BOARD_PATH)
bbox = board.GetBoardEdgesBoundingBox()
print(f"Board edge bbox after adding Edge.Cuts rect: "
      f"w={pcbnew.ToMM(bbox.GetWidth())}mm h={pcbnew.ToMM(bbox.GetHeight())}mm")

# ---------------------------------------------------------------------
section("B11: Full round-trip fidelity check")
# ---------------------------------------------------------------------
board_final = pcbnew.LoadBoard(BOARD_PATH)
print("Footprints:", [f"{f.GetReference()}={f.GetValue()}" for f in board_final.GetFootprints()])
print("Nets:", [board_final.GetNetInfo().GetNetItem(i).GetNetname()
                for i in range(board_final.GetNetInfo().GetNetCount())])
tracks = list(board_final.GetTracks())
print("Track/Via items count:", len(tracks))
for t in tracks:
    print("  ", type(t).__name__, "net=", t.GetNetname())
zones = list(board_final.Zones())
print("Zone count:", len(zones))
for z in zones:
    print("  zone layer=", z.GetLayerName(), "net=", z.GetNetname(), "filled=", z.IsFilled())
drawings = [d for d in board_final.GetDrawings()]
print("Drawing/edge items count:", len(drawings))

print("\nDONE. Final board file:", BOARD_PATH)
