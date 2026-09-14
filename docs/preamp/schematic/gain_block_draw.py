#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gain_block_draw.py - readable schematic of the preamplifier gain block.

DERIVED DOCUMENTATION, NOT A SOURCE OF TRUTH.
The topology lives in circuits/preamp/gain_block.py. This file only draws it.
If the two disagree, fix this drawing (or the topology at its source) - never
scripts/check_schematic.py.

Run:
  /Users/roberto/EDA/env/venv/bin/python3 docs/preamp/schematic/gain_block_draw.py

Emits, FROM ONE EXECUTION so they cannot diverge:
  gain_block.svg
  gain_block.manifest.json

HOW THIS FILE AVOIDS LYING
--------------------------
Three links, each mechanically checked:

  1. DEVICES (below) is transcribed BY HAND from the netlist. It is the only
     place a net name is written against a device pin.
     -> checked by scripts/check_schematic.py against the netlist, in both
        directions. That check is the acceptance criterion.

  2. The manifest is emitted FROM DEVICES, in the same run as the SVG. It
     cannot describe a different circuit from the one this file draws.

  3. Every wire goes through wire(), which takes two NODE NAMES and asserts
     they were registered on the same net. A device terminal's net is read
     from DEVICES, never typed at the call site. So a mis-drawn wire raises
     AssertionError at build time instead of producing a convincing picture
     of the wrong circuit.

  Plus a closing check that no device terminal was left both unwired and
  unlabelled - nothing dangles silently.

SCHEMDRAW TRAPS FOUND THE HARD WAY
----------------------------------
Both of these produced a plausible-looking but WRONG drawing, with no error:

  * Elements INHERIT THE DRAWING'S CURRENT DIRECTION. After any element
    placed with .to() pointing downwards, the next transistor comes out
    rotated 90 degrees - collector and emitter side by side, base pointing
    down - and the wires to it come out diagonal. Every transistor here
    therefore carries an explicit .right(), which pins the canonical
    vertical orientation regardless of what was drawn before it.
  * .reverse() on a transistor mirrors the BASE to the other side while
    leaving collector and emitter where they are. That is exactly what a
    current mirror and a Vbe multiplier need, and it is used deliberately at
    three places, each commented.

READABILITY CHOICES, and what they cost
---------------------------------------
 * FOUR PANELS, not one. 44 devices in a single frame is a wiring diagram.
   Panels 1-2-3 run left to right along the signal path; panel 4 holds the
   housekeeping that would otherwise clutter all three; the green box states
   the one property the feedback arrangement exists to guarantee.
 * V+ at the top of every panel, V- at the bottom, ground pointing down,
   signal left to right. No diagonal wires anywhere: wire() inserts an
   orthogonal elbow automatically so the caller cannot forget.
 * GLOBAL nets (V+, V-, GND, NREF, NCASC) travel BY NAME, not by wire.
   Drawing the cascode bias line as a wire would cross the very branch it
   biases. A named bias rail is what a real schematic does - and it is why
   panel 4 exists: every named rail is drawn once, in full, where it is
   generated.
 * The current mirror is drawn AS a mirror: emitters up to V+, bases facing
   each other across the gap, the diode connection visible as a loop. That
   shape is the whole point, and no auto-placer can know to draw it that way
   (docs/limitations.md #16).
 * Component designators are placed by hand with txt(), not with schemdraw's
   .label(): element labels rotate with the element and collide with
   neighbours, and this drawing exists to be read.
 * Operating currents are annotated from the SIMULATED .op in
   spice/preamp/tb/tb_op.cir - not from design intent.
"""
import json
import os

import matplotlib
matplotlib.use("Agg")             # headless: must precede the schemdraw import

import schemdraw                      # noqa: E402
import schemdraw.elements as elm      # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SVG = os.path.join(HERE, "gain_block.svg")
MANIFEST = os.path.join(HERE, "gain_block.manifest.json")
SOURCE_NETLIST = "spice/preamp/gain_block_flat.inc"

# =============================================================================
# DEVICES - transcribed BY HAND from spice/preamp/gain_block_flat.inc
# Pin keys follow scripts/check_schematic.py PINOUTS:
#   R,C -> 1,2    D -> A,K    Q -> C,B,E    J -> D,G,S
# Order matters: pin 1 is the FIRST node on the SPICE line.
# =============================================================================
DEVICES = {
    # ---- panel 1: cascoded differential pair --------------------------------
    "R108":  {"1": "IN",     "2": "G1"},
    "R113":  {"1": "IN",     "2": "0"},
    "R109":  {"1": "FB",     "2": "G2"},
    "JQ110A": {"D": "D1N",    "G": "G1",    "S": "S1"},
    "JQ110B": {"D": "D2N",    "G": "G2",    "S": "S2"},
    "R111":  {"1": "S1",     "2": "SRC"},
    "R112":  {"1": "S2",     "2": "SRC"},
    "Q106":  {"C": "SRC",    "B": "NREF",  "E": "NTE"},
    "R107":  {"1": "NTE",    "2": "VMINUS"},
    "Q117":  {"C": "NHI",    "B": "NCASC", "E": "D1N"},
    "Q118":  {"C": "NMIRI",  "B": "NCASC", "E": "D2N"},
    # ---- panel 2: current mirror + VAS --------------------------------------
    "R119":  {"1": "VPLUS",  "2": "NME1"},
    "R120":  {"1": "VPLUS",  "2": "NME2"},
    "Q121A":  {"C": "NMIRI",  "B": "NMIRI", "E": "NME1"},
    "Q121B":  {"C": "NHI",    "B": "NMIRI", "E": "NME2"},
    "R123":  {"1": "VPLUS",  "2": "NVE"},
    "Q122":  {"C": "NX",     "B": "NHI",   "E": "NVE"},
    "C124":  {"1": "NX",     "2": "NHI"},
    "Q125":  {"C": "NY",     "B": "NREF",  "E": "NVLE"},
    "R126":  {"1": "NVLE",   "2": "VMINUS"},
    # ---- panel 3: Class A complementary follower + feedback -----------------
    "Q127":  {"C": "NX",     "B": "NBB",   "E": "NY"},
    "R128":  {"1": "NX",     "2": "NBB"},
    "R129":  {"1": "NBB",    "2": "NY"},
    "R130":  {"1": "NX",     "2": "NBN"},
    "R131":  {"1": "NY",     "2": "NBP"},
    "Q132":  {"C": "VPLUS",  "B": "NBN",   "E": "NEN"},
    "Q133":  {"C": "VMINUS", "B": "NBP",   "E": "NEP"},
    "R134":  {"1": "NEN",    "2": "OUT"},
    "R135":  {"1": "NEP",    "2": "OUT"},
    "R136":  {"1": "OUT",    "2": "FB"},
    "C137":  {"1": "OUT",    "2": "FB"},
    "R138":  {"1": "FB",     "2": "RG"},
    "R143":  {"1": "FB",     "2": "RG10"},
    # ---- panel 4: bias references and rail decoupling -----------------------
    "R101":  {"1": "0",      "2": "NREF"},
    "D102":  {"A": "NREF",   "K": "NREFM"},
    "D103":  {"A": "NREFM",  "K": "VMINUS"},
    "C104":  {"1": "NREF",   "2": "VMINUS"},
    "C105":  {"1": "NREF",   "2": "VMINUS"},
    "R114":  {"1": "VPLUS",  "2": "NCASC"},
    "R115":  {"1": "NCASC",  "2": "0"},
    "C116":  {"1": "NCASC",  "2": "0"},
    "C139":  {"1": "VPLUS",  "2": "0"},
    "C140":  {"1": "VMINUS", "2": "0"},
    "C141":  {"1": "VPLUS",  "2": "0"},
    "C142":  {"1": "VMINUS", "2": "0"},
}

# =============================================================================
# Infrastructure
# =============================================================================
NODE_XY, NODE_NET, TOUCHED = {}, {}, set()

RED, BLUE, GREEN, GREY = "#c00000", "#00449e", "#1a7a1a", "#8c8c8c"
NETCOL, DIM = "#0b5394", "#555555"

d = schemdraw.Drawing(show=False)
d.config(fontsize=9)


def node(name, net, xy):
    assert name not in NODE_XY, f"node {name} declared twice"
    NODE_XY[name] = (float(xy[0]), float(xy[1]))
    NODE_NET[name] = net.upper()
    return NODE_XY[name]


def term(ref, pin, xy, alias=None):
    """Register a DEVICE TERMINAL. Its net comes from DEVICES, never a literal."""
    return node(alias or f"{ref}.{pin}", DEVICES[ref][pin], xy)


def _touch(n):
    if "." in n and n.split(".")[0] in DEVICES:
        TOUCHED.add(n)


def wire(a, b, via=(), dots=(), first="v", color="black"):
    """Wire two registered nodes; assert same net; never draw a diagonal."""
    assert NODE_NET[a] == NODE_NET[b], \
        f"wire {a}({NODE_NET[a]}) -> {b}({NODE_NET[b]}): reti diverse"
    _touch(a)
    _touch(b)
    pts = [NODE_XY[a]] + [tuple(map(float, p)) for p in via] + [NODE_XY[b]]
    ortho = [pts[0]]
    for q in pts[1:]:
        px, py = ortho[-1]
        if abs(px - q[0]) > 1e-9 and abs(py - q[1]) > 1e-9:
            ortho.append((px, q[1]) if first == "v" else (q[0], py))
        ortho.append(q)
    for p, q in zip(ortho, ortho[1:]):
        if p != q:
            d.add(elm.Line().at(p).to(q).color(color))
    for p in dots:
        d.add(elm.Dot().at(tuple(map(float, p))))


def txt(xy, s, size=9, color="black", halign="center"):
    d.add(elm.Label().at(tuple(map(float, xy)))
          .label(s, loc="center", halign=halign, fontsize=size, color=color))


def flag(n, text=None, direction="right", length=1.5, size=8.5, color=NETCOL):
    """Terminate a node in a named flag. A named rail IS a connection."""
    x, y = NODE_XY[n]
    dx, dy = {"right": (length, 0), "left": (-length, 0),
              "up": (0, length), "down": (0, -length)}[direction]
    end = (x + dx, y + dy)
    d.add(elm.Line().at((x, y)).to(end).color(color))
    d.add(elm.Dot().at(end).color(color).fill(color))
    ha = {"right": "left", "left": "right", "up": "center",
          "down": "center"}[direction]
    off = {"right": (0.25, 0.0), "left": (-0.25, 0.0),
           "up": (0.0, 0.30), "down": (0.0, -0.36)}[direction]
    txt((end[0] + off[0], end[1] + off[1]), text or NODE_NET[n],
        size=size, color=color, halign=ha)
    _touch(n)


def frame(x0, y0, x1, y1, title=None, subtitle=None, color="#9a9a9a"):
    for p, q in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)),
                 ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
        d.add(elm.Line().at(p).to(q).color(color).linewidth(0.9))
    if title:
        txt(((x0 + x1) / 2, y1 - 0.75), title, size=13)
    if subtitle:
        txt(((x0 + x1) / 2, y1 - 1.6), subtitle, size=8.5, color=DIM)


def rail(x0, x1, y, label, color):
    d.add(elm.Line().at((x0, y)).to((x1, y)).color(color).linewidth(1.8))
    txt((x0 - 0.35, y), label, size=10, color=color, halign="right")


# --- placement helpers: orientation pinned, terminals registered -------------
def _place(ref, e, mapping):
    d.add(e)
    for pin, anch in mapping.items():
        term(ref, pin, tuple(e.absanchors[anch]))
    return e


def npn(ref, anchor, xy, rev=False):
    e = elm.BjtNpn().right()          # .right() pins the vertical orientation
    if rev:                           # base to the RIGHT instead of the left
        e = e.reverse()
    return _place(ref, e.anchor(anchor).at(tuple(map(float, xy))),
                  {"C": "collector", "B": "base", "E": "emitter"})


def pnp(ref, anchor, xy, rev=False):
    e = elm.BjtPnp().right()
    if rev:
        e = e.reverse()
    return _place(ref, e.anchor(anchor).at(tuple(map(float, xy))),
                  {"C": "collector", "B": "base", "E": "emitter"})


def jfet(ref, xy, gate_left=False):
    e = elm.JFetN().right()
    if gate_left:
        e = e.reverse()
    return _place(ref, e.anchor("drain").at(tuple(map(float, xy))),
                  {"D": "drain", "G": "gate", "S": "source"})


def res(ref, p1, p2, value=None, lbl=None, color="black"):
    a, b = term(ref, "1", p1), term(ref, "2", p2)
    d.add(elm.Resistor().at(a).to(b).color(color))
    if lbl:
        txt(lbl[0], ref, size=8.5, color=color, halign=lbl[1])
        if value:
            txt((lbl[0][0], lbl[0][1] - 0.46), value, size=8, color=color,
                halign=lbl[1])
    return a, b


def cap(ref, p1, p2, value=None, lbl=None, color="black"):
    a, b = term(ref, "1", p1), term(ref, "2", p2)
    d.add(elm.Capacitor().at(a).to(b).color(color))
    if lbl:
        txt(lbl[0], ref, size=8.5, color=color, halign=lbl[1])
        if value:
            txt((lbl[0][0], lbl[0][1] - 0.46), value, size=8, color=color,
                halign=lbl[1])
    return a, b


def dio(ref, pa, pk, lbl=None):
    a, b = term(ref, "A", pa), term(ref, "K", pk)
    d.add(elm.Diode().at(a).to(b))
    if lbl:
        txt(lbl[0], ref, size=8.5, halign=lbl[1])
    return a, b


def gnd(xy):
    d.add(elm.Ground().at(tuple(map(float, xy))))


# =============================================================================
# PANEL 1 - cascoded differential pair
# =============================================================================
frame(-2.0, -6.0, 20.0, 17.0,
      "1.   COPPIA DIFFERENZIALE CASCODATA",
      "LSK489 duale monolitico (ADR-013), cascodata (ADR-014)")
rail(-1.2, 19.2, -3.4, "V-", BLUE)

# --- the pair. gate_left mirrors the left device so the gates face outwards --
jfet("JQ110A", (5.0, 6.0), gate_left=True)
jfet("JQ110B", (13.0, 6.0))
txt((5.8, 5.8), "JQ110A", size=8.5, halign="left")
txt((5.8, 5.34), "LSK489  1/2", size=8, color=DIM, halign="left")
txt((12.2, 5.8), "JQ110B", size=8.5, halign="right")
txt((12.2, 5.34), "LSK489  2/2", size=8, color=DIM, halign="right")

# --- input network ----------------------------------------------------------
gy = NODE_XY["JQ110A.G"][1]
res("R108", (1.2, gy), NODE_XY["JQ110A.G"], value="100",
    lbl=((2.6, 6.08), "center"))
wire("R108.2", "JQ110A.G")
res("R113", (1.2, gy), (1.2, 2.1), value="1M", lbl=((0.72, 3.95), "right"))
gnd(NODE_XY["R113.2"])
TOUCHED.add("R113.2")
wire("R108.1", "R113.1", dots=[NODE_XY["R108.1"]])
flag("R108.1", "IN", direction="left", length=1.4)

res("R109", (17.4, NODE_XY["JQ110B.G"][1]), NODE_XY["JQ110B.G"], value="100",
    lbl=((15.7, 6.08), "center"))
wire("R109.2", "JQ110B.G")
flag("R109.1", "FB", direction="right", length=1.0)
txt((18.75, 4.35), "dal riquadro 3", size=7.5, color=NETCOL)

# --- source degeneration and tail -------------------------------------------
res("R111", NODE_XY["JQ110A.S"], (5.0, 2.2), value="100",
    lbl=((4.52, 3.7), "right"))
res("R112", NODE_XY["JQ110B.S"], (13.0, 2.2), value="100",
    lbl=((13.48, 3.7), "left"))
npn("Q106", "collector", (9.0, 2.2))
wire("R111.2", "Q106.C", dots=[NODE_XY["R111.2"]])
wire("Q106.C", "R112.2", dots=[NODE_XY["R112.2"], NODE_XY["Q106.C"]])
txt((10.05, 1.78), "Q106   2N5551", size=8.5, halign="left")
txt((10.05, 1.32), "coda  4,41 mA", size=8, color=RED, halign="left")
flag("Q106.B", "NREF", direction="left", length=1.6)
res("R107", NODE_XY["Q106.E"], (9.0, -2.0), value="137",
    lbl=((9.48, -0.35), "left"))
node("P1.vm", "VMINUS", (9.0, -3.4))
wire("R107.2", "P1.vm", dots=[NODE_XY["P1.vm"]])

# --- cascode ----------------------------------------------------------------
npn("Q117", "emitter", (5.0, 8.7))
npn("Q118", "emitter", (13.0, 8.7))
wire("Q117.E", "JQ110A.D")
wire("Q118.E", "JQ110B.D")
txt((5.8, 10.75), "Q117", size=8.5, halign="left")
txt((5.8, 10.29), "2N5551", size=8, color=DIM, halign="left")
txt((13.8, 10.75), "Q118", size=8.5, halign="left")
txt((13.8, 10.29), "2N5551", size=8, color=DIM, halign="left")
flag("Q117.B", "NCASC", direction="left", length=1.5)
flag("Q118.B", "NCASC", direction="left", length=1.5)

node("P1.nhi", "NHI", (5.0, 12.9))
wire("Q117.C", "P1.nhi")
flag("P1.nhi", "NHI", direction="up", length=0.9)
node("P1.nmiri", "NMIRI", (13.0, 12.9))
wire("Q118.C", "P1.nmiri")
flag("P1.nmiri", "NMIRI", direction="up", length=0.9)

txt((5.45, 12.25), "2,20 mA", size=8, color=RED, halign="left")
txt((13.45, 12.25), "2,17 mA", size=8, color=RED, halign="left")
txt((9.0, -4.1),
    "il cascode tiene i drain fermi a 9,21 V: niente moltiplicazione di "
    "Miller,", size=8, color=DIM)
txt((9.0, -4.6),
    "quindi la risposta HF non segue la posizione del volume  (ADR-014)",
    size=8, color=DIM)
txt((9.0, -5.3), "V_ds = 8,75 V su entrambi i JFET      g_m = 4,38 mS",
    size=8, color=DIM)

# =============================================================================
# PANEL 2 - current mirror + VAS
# =============================================================================
frame(21.0, -6.0, 42.0, 17.0,
      "2.   SPECCHIO DI CORRENTE  +  VAS",
      "carico attivo LS352 appaiato; VAS PNP compensato a Miller")
rail(22.0, 41.0, 13.6, "V+", RED)
rail(22.0, 41.0, -3.4, "V-", BLUE)

# --- the mirror. rev=True mirrors Q121A's base so the two bases face each -----
# --- other across the gap: that is what makes it READ as a mirror. -----------
res("R119", (26.0, 13.6), (26.0, 10.6), value="220",
    lbl=((25.52, 12.35), "right"))
res("R120", (31.0, 13.6), (31.0, 10.6), value="220",
    lbl=((31.48, 12.35), "left"))
d.add(elm.Dot().at(NODE_XY["R119.1"]))
d.add(elm.Dot().at(NODE_XY["R120.1"]))
TOUCHED.update({"R119.1", "R120.1"})

pnp("Q121A", "emitter", (26.0, 10.6), rev=True)
pnp("Q121B", "emitter", (31.0, 10.6))
wire("R119.2", "Q121A.E")
wire("R120.2", "Q121B.E")
wire("Q121A.B", "Q121B.B")                       # the mirror's base bus
txt((25.52, 10.8), "Q121A", size=8.5, halign="right")
txt((25.52, 10.34), "LS352 1/2", size=8, color=DIM, halign="right")
txt((31.48, 10.8), "Q121B", size=8.5, halign="left")
txt((31.48, 10.34), "LS352 2/2", size=8, color=DIM, halign="left")
txt((28.5, 12.75), "2,13 mA specchiati", size=8, color=RED)

# diode connection, drawn as a visible loop back onto the base bus
node("P2.diode", "NMIRI", (28.5, NODE_XY["Q121A.B"][1]))
wire("Q121A.C", "P2.diode", via=[(26.0, 8.35), (28.5, 8.35)],
     dots=[NODE_XY["P2.diode"], (26.0, 8.35)])
txt((28.5, 7.9), "connessione a diodo", size=7.5, color=DIM)

node("P2.nmiri_in", "NMIRI", (26.0, 6.5))
wire("Q121A.C", "P2.nmiri_in")
flag("P2.nmiri_in", "NMIRI", direction="down", length=0.8)
txt((26.0, 5.05), "dal cascode Q118", size=7.5, color=NETCOL)

node("P2.nhi_vas", "NHI", (31.0, 8.3))
node("P2.nhi_c126", "NHI", (31.0, 7.4))
node("P2.nhi_in", "NHI", (31.0, 6.5))
wire("Q121B.C", "P2.nhi_in",
     dots=[NODE_XY["P2.nhi_vas"], NODE_XY["P2.nhi_c126"]])
flag("P2.nhi_in", "NHI", direction="down", length=0.8)
txt((31.0, 5.05), "dal cascode Q117", size=7.5, color=NETCOL)

# --- VAS --------------------------------------------------------------------
res("R123", (36.5, 13.6), (36.5, 10.6), value="91",
    lbl=((36.98, 12.35), "left"))
d.add(elm.Dot().at(NODE_XY["R123.1"]))
TOUCHED.add("R123.1")
pnp("Q122", "emitter", (36.5, 9.0))
wire("R123.2", "Q122.E")
wire("P2.nhi_vas", "Q122.B", first="h")
txt((37.65, 9.2), "Q122   2N5401", size=8.5, halign="left")
txt((37.65, 8.74), "VAS,  6,44 mA", size=8, color=RED, halign="left")

node("P2.nx_c126", "NX", (36.5, 5.6))
node("P2.nx_out", "NX", (39.8, 4.2))
wire("Q122.C", "P2.nx_out", via=[(36.5, 4.2)], dots=[NODE_XY["P2.nx_c126"]])
flag("P2.nx_out", "NX", direction="right", length=0.9)

# Miller compensation: bridges collector back to base, routed clear of R123
node("P2.c126_bot", "NX", (33.4, 5.6))
wire("P2.nx_c126", "P2.c126_bot", first="h")
cap("C124", NODE_XY["P2.c126_bot"], (33.4, 7.4), value="470p C0G",
    lbl=((32.92, 6.8), "right"))
wire("C124.2", "P2.nhi_c126", first="h")
txt((33.0, 3.5), "compensazione Miller: il polo dominante", size=7.5,
    color=DIM, halign="left")

# --- VAS load current sink --------------------------------------------------
npn("Q125", "collector", (31.0, 1.6))
node("P2.ny_out", "NY", (39.8, 2.6))
wire("Q125.C", "P2.ny_out", via=[(31.0, 2.6)])
flag("P2.ny_out", "NY", direction="right", length=0.9)
flag("Q125.B", "NREF", direction="left", length=1.6)
txt((32.05, 1.5), "Q125   2N5551", size=8.5, halign="left")
txt((32.05, 1.04), "carico VAS,  6,44 mA", size=8, color=RED, halign="left")
res("R126", NODE_XY["Q125.E"], (31.0, -3.4), value="91",
    lbl=((31.48, -1.65), "left"))
d.add(elm.Dot().at(NODE_XY["R126.2"]))
TOUCHED.add("R126.2")

txt((31.5, -4.7),
    "V+ e' il rail debole per il PSRR (59,5 dB a 1 kHz):", size=8, color=DIM)
txt((31.5, -5.2),
    "specchio e VAS poggiano entrambi su V+", size=8, color=DIM)

# =============================================================================
# PANEL 3 - Class A complementary follower + feedback
# =============================================================================
frame(43.0, -6.0, 71.0, 17.0,
      "3.   INSEGUITORE COMPLEMENTARE CLASSE A   +   CONTROREAZIONE",
      "MJE15032/33 a 14,7 mA, e la rete che il rele' commuta")
rail(44.0, 62.5, 13.6, "V+", RED)
rail(44.0, 62.5, -3.4, "V-", BLUE)

node("P3.nx_in", "NX", (45.4, 10.5))
node("P3.nx_q129", "NX", (50.0, 10.5))
node("P3.nx_r130", "NX", (53.0, 10.5))
node("P3.nx_r132", "NX", (56.0, 10.5))
flag("P3.nx_in", "NX", direction="left", length=0.9)
node("P3.ny_in", "NY", (45.4, 0.5))
node("P3.ny_q129", "NY", (50.0, 0.5))
node("P3.ny_r131", "NY", (53.0, 0.5))
node("P3.ny_r133", "NY", (56.0, 0.5))
flag("P3.ny_in", "NY", direction="left", length=0.9)

# --- Vbe multiplier. rev=True puts the base on the right, facing the ---------
# --- divider it taps: the textbook shape. -----------------------------------
npn("Q127", "collector", (50.0, 6.9), rev=True)
wire("P3.nx_in", "P3.nx_q129")
wire("P3.nx_q129", "Q127.C", dots=[NODE_XY["P3.nx_q129"]])
wire("Q127.E", "P3.ny_q129", dots=[NODE_XY["P3.ny_q129"]])
wire("P3.ny_in", "P3.ny_q129")
txt((48.85, 6.65), "Q127", size=8.5, halign="right")
txt((48.85, 6.19), "2N5551", size=8, color=DIM, halign="right")
txt((48.85, 5.58), "moltiplicatore", size=7.5, color=DIM, halign="right")
txt((48.85, 5.12), "di V_be:  1,96 V", size=7.5, color=DIM, halign="right")

res("R128", NODE_XY["P3.nx_r130"], (53.0, 7.4), value="1.69k",
    lbl=((53.48, 9.3), "left"))
res("R129", NODE_XY["R128.2"], (53.0, 4.3), value="1.00k",
    lbl=((53.48, 6.2), "left"))
wire("P3.nx_q129", "P3.nx_r130", dots=[NODE_XY["P3.nx_r130"]])
wire("R128.2", "R129.1")
wire("R129.2", "P3.ny_r131", dots=[NODE_XY["P3.ny_r131"]])
wire("P3.ny_q129", "P3.ny_r131")
wire("Q127.B", "R128.2", dots=[NODE_XY["R128.2"]])

# --- output devices ---------------------------------------------------------
wire("P3.nx_r130", "P3.nx_r132")
wire("P3.ny_r131", "P3.ny_r133")
res("R130", NODE_XY["P3.nx_r132"], (59.5, 10.5), value="10",
    lbl=((57.75, 11.65), "center"))
npn("Q132", "base", (59.5, 10.5))
wire("R130.2", "Q132.B")
node("P3.vp", "VPLUS", (NODE_XY["Q132.C"][0], 13.6))
wire("Q132.C", "P3.vp", dots=[NODE_XY["P3.vp"]])
txt((61.25, 11.6), "Q132   MJE15032", size=8.5, halign="left")

res("R131", NODE_XY["P3.ny_r133"], (59.5, 0.5), value="10",
    lbl=((57.75, 1.65), "center"))
pnp("Q133", "base", (59.5, 0.5))
wire("R131.2", "Q133.B")
node("P3.vm", "VMINUS", (NODE_XY["Q133.C"][0], -3.4))
wire("Q133.C", "P3.vm", dots=[NODE_XY["P3.vm"]])
txt((61.25, -0.6), "Q133   MJE15033", size=8.5, halign="left")

res("R134", NODE_XY["Q132.E"], (NODE_XY["Q132.E"][0], 6.8), value="22",
    lbl=((60.75, 8.4), "left"))
res("R135", NODE_XY["Q133.E"], (NODE_XY["Q133.E"][0], 4.2), value="22",
    lbl=((60.75, 2.8), "left"))
node("P3.out", "OUT", (NODE_XY["R134.2"][0], 5.5))
wire("R134.2", "P3.out")
wire("P3.out", "R135.2", dots=[NODE_XY["P3.out"]])
txt((44.4, 4.0), "14,71 mA di riposo:", size=8, color=RED, halign="left")
txt((44.4, 3.5), "Classe A coi carichi V1 -", size=8, color=RED, halign="left")
txt((44.4, 3.0), "il carico piu' pesante", size=8, color=RED,
    halign="left")
txt((44.4, 2.5), "chiede 3,9 mA di picco.", size=8, color=RED,
    halign="left")
# L11: the old claim was "Classe A garantita". It is false with the mute
# engaged or a short at a connector (NC-001); ADR-021 admits class B there.
txt((44.4, 2.0), "A mute o in corto: classe B", size=8, color=RED,
    halign="left")
txt((44.4, 1.5), "(ADR-021, termica verificata)", size=8, color=RED,
    halign="left")

# --- feedback network: the point of the whole design ------------------------
res("R136", (64.0, 5.5), (64.0, 2.0), value="1.50k",
    lbl=((63.52, 4.1), "right"), color=GREEN)
cap("C137", (66.8, 5.5), (66.8, 2.0), value="330p",
    lbl=((67.28, 4.1), "left"))
node("P3.out_end", "OUT", (68.5, 5.5))
wire("P3.out", "R136.1")
wire("R136.1", "C137.1", dots=[NODE_XY["R136.1"]])
wire("C137.1", "P3.out_end", dots=[NODE_XY["C137.1"]])
flag("P3.out_end", "OUT", direction="right", length=0.8)
wire("R136.2", "C137.2", dots=[NODE_XY["C137.2"]])
node("P3.fb_tag", "FB", (62.4, 2.0))
wire("R136.2", "P3.fb_tag", dots=[NODE_XY["R136.2"]])
flag("P3.fb_tag", "FB", direction="left", length=0.5)
txt((65.4, 1.3), "FB  ->  gate di JQ110B (riq. 1)", size=7.5, color=NETCOL,
    halign="left")

res("R138", NODE_XY["R136.2"], (64.0, -1.0), value="3.57k",
    lbl=((63.52, 0.65), "right"), color=GREEN)
flag("R138.2", "RG", direction="down", length=0.8)

# L27 / ADR-026: the second R_g leg, in PARALLEL with R138 from the same FB
# node - never in series with it, and never in series with R136.
node("P3.fb_r143", "FB", (69.3, 2.0))
wire("C137.2", "P3.fb_r143", dots=[NODE_XY["C137.2"]])
res("R143", NODE_XY["P3.fb_r143"], (69.3, -1.0), value="866",
    lbl=((68.82, 0.65), "right"), color=GREEN)
flag("R143.2", "RG10", direction="down", length=0.8)

# The relay contacts are NOT devices of this netlist - they live in
# preamp_audio.py. Drawn grey and dashed so they cannot be mistaken for one.
for _x, _k in ((64.0, "K1a"), (69.3, "K5a")):
    d.add(elm.Line().at((_x, -2.6)).to((_x, -3.1)).color(GREY)
          .linestyle("--"))
    d.add(elm.Switch().at((_x, -3.1)).down().color(GREY).linestyle("--"))
    d.add(elm.Ground().at((_x, -5.0)).color(GREY))
    txt((_x + 0.95, -3.55), _k, size=8, color=GREY, halign="left")
txt((66.65, -5.25), "contatti NO dei rele', in preamp_audio.py:",
    size=7.0, color=GREY)
txt((66.65, -5.7), "NON sono dispositivi di questa netlist",
    size=7.0, color=GREY)

# =============================================================================
# PANEL 4 - bias references and rail decoupling
# =============================================================================
frame(-2.0, -19.2, 42.0, -7.5,
      "4.   RIFERIMENTI DI POLARIZZAZIONE E DISACCOPPIAMENTO",
      "ogni rail nominato nei riquadri 1-3 e' generato qui, una volta sola")

# --- negative reference string. GND at the top, V- at the bottom: that is ----
# --- the real order of these potentials (0 > -13,7 > -15 V). ----------------
node("P4.gnd", "0", (2.2, -9.7))
node("P4.r101", "0", (4.0, -9.7))
gnd(NODE_XY["P4.gnd"])
d.add(elm.Line().at(NODE_XY["P4.gnd"]).to(NODE_XY["P4.r101"]))
res("R101", NODE_XY["P4.r101"], (4.0, -12.4), value="6.81k",
    lbl=((3.52, -10.85), "right"))
TOUCHED.add("R101.1")
dio("D102", NODE_XY["R101.2"], (4.0, -14.2), lbl=((3.52, -13.3), "right"))
wire("R101.2", "D102.A")
dio("D103", NODE_XY["D102.K"], (4.0, -16.0), lbl=((3.52, -15.1), "right"))
wire("D102.K", "D103.A")

cap("C104", (7.5, -12.4), (7.5, -16.0), value="100u",
    lbl=((7.98, -13.95), "left"))
cap("C105", (10.5, -12.4), (10.5, -16.0), value="100n",
    lbl=((10.98, -13.95), "left"))
node("P4.nref_tag", "NREF", (13.6, -12.4))
wire("R101.2", "C104.1", dots=[NODE_XY["R101.2"]])
wire("C104.1", "C105.1", dots=[NODE_XY["C104.1"]])
wire("C105.1", "P4.nref_tag", dots=[NODE_XY["C105.1"]])
flag("P4.nref_tag", "NREF   ->  basi di Q106 e Q125", direction="right",
     length=0.7)
wire("D103.K", "C104.2", dots=[NODE_XY["D103.K"]])
wire("C104.2", "C105.2", dots=[NODE_XY["C104.2"]])
txt((8.5, -17.2),
    "bypass verso V-, NON verso massa: un generatore di corrente deve tenere",
    size=7.5, color=DIM)
txt((8.5, -17.7),
    "ferma la propria corrente rispetto al rail su cui poggia  ->  PSRR",
    size=7.5, color=DIM)

# --- cascode divider --------------------------------------------------------
node("P4.vp1", "VPLUS", (21.0, -9.7))
d.add(elm.Line().at((19.4, -9.7)).to(NODE_XY["P4.vp1"]).color(RED)
      .linewidth(1.8))
txt((19.05, -9.7), "V+", size=10, color=RED, halign="right")
res("R114", NODE_XY["P4.vp1"], (21.0, -12.4), value="4.99k",
    lbl=((20.52, -10.85), "right"))
TOUCHED.add("R114.1")
res("R115", NODE_XY["R114.2"], (21.0, -15.4), value="10.0k",
    lbl=((20.52, -13.7), "right"))
wire("R114.2", "R115.1")
gnd(NODE_XY["R115.2"])
TOUCHED.add("R115.2")
cap("C116", (24.5, -12.4), (24.5, -15.4), value="47u",
    lbl=((24.98, -13.7), "left"))
gnd(NODE_XY["C116.2"])
TOUCHED.add("C116.2")
node("P4.ncasc_tag", "NCASC", (27.6, -12.4))
wire("R114.2", "C116.1", dots=[NODE_XY["R114.2"]])
wire("C116.1", "P4.ncasc_tag", dots=[NODE_XY["C116.1"]])
flag("P4.ncasc_tag", "NCASC  ->  basi di Q117 e Q118", direction="right",
     length=0.7)
txt((22.6, -11.9), "9,89 V", size=8, color=RED, halign="left")

# --- rail decoupling --------------------------------------------------------
rail(33.0, 40.5, -9.7, "V+", RED)
rail(33.0, 40.5, -16.0, "V-", BLUE)
node("P4.dg", "0", (39.8, -12.85))
d.add(elm.Line().at((34.0, -12.85)).to(NODE_XY["P4.dg"]))
gnd(NODE_XY["P4.dg"])
for ref, x, val, top in (("C139", 35.0, "100n", True),
                         ("C141", 37.5, "100u", True),
                         ("C140", 35.0, "100n", False),
                         ("C142", 37.5, "100u", False)):
    if top:
        cap(ref, (x, -9.7), (x, -12.85), value=val,
            lbl=((x - 0.48, -11.0), "right"))
    else:
        cap(ref, (x, -16.0), (x, -12.85), value=val,
            lbl=((x - 0.48, -14.5), "right"))
    d.add(elm.Dot().at(NODE_XY[f"{ref}.1"]))
    d.add(elm.Dot().at(NODE_XY[f"{ref}.2"]))
    TOUCHED.update({f"{ref}.1", f"{ref}.2"})
txt((36.5, -17.2), "disaccoppiamento locale dei rail", size=7.5, color=DIM)

# =============================================================================
# CALLOUT - the property the whole feedback arrangement exists to guarantee
# =============================================================================
frame(43.0, -19.2, 71.0, -7.5, color=GREEN)
txt((57.0, -8.35),
    "PERCHE' L'ANELLO NON SI APRE MAI   (ADR-004 / requisito V2)",
    size=11.5, color=GREEN)
_callout = [
    ("R136 (1.50k) e' CABLATA FISSA fra OUT e FB: l'anello di controreazione "
     "passa sempre di li'.", GREEN),
    ("I rele' commutano soltanto R138 (3.57k, K1) e R143 (866, K5) verso massa: "
     "rami IN PARALLELO, mai in serie all'anello.", GREEN),
    ("K1, K5 APERTI     ->   guadagno = 1                            "
     "(0 dB)", GREEN),
    ("K1 CHIUSO         ->   guadagno = 1 + Rf/R138 = 1,420            "
     "(+3,05 dB)", GREEN),
    ("K1 e K5 CHIUSI    ->   guadagno = 1 + Rf/(R138 || R143) = 3,152  "
     "(+9,97 dB)", GREEN),
    ("IN RIMBALZO o SALDATI  ->  il guadagno resta fra 1 e 3,152, mai sopra: "
     "l'anello resta chiuso (ADR-026)", GREEN),
    ("", GREEN),
    ("Simulato con due contatti reali (R_on 50 mohm, R_off 1e12 ohm, rimbalzi), "
     "0 -> +3 -> +10 -> +3 -> 0 e 0 <-> +10:", "#333333"),
    ("l'uscita resta entro +1,52 / -1,63 V, cioe' l'inviluppo del +10 dB. "
     "Non esce mai da quella banda.", "#333333"),
    ("", "#333333"),
    ("CONTROFATTUALE - la disposizione che ADR-004 ha scartato, rele' in "
     "serie a R136:  uscita a -13,77 V,", "#333333"),
    ("1,2 V dal rail. E' il numero contro cui ADR-004 stava proteggendo.",
     "#333333"),
]
for i, (line, col) in enumerate(_callout):
    if line:
        txt((44.0, -9.65 - i * 0.76), line, size=8, color=col, halign="left")

# =============================================================================
# Header / footer
# =============================================================================
txt((34.0, 20.8), "PREAMPLIFICATORE DI LINEA  -  BLOCCO DI GUADAGNO", size=16)
txt((34.0, 19.65),
    "ADR-006: un solo blocco, progettato una volta, usato due volte per "
    "canale.     Classe A a discreti, nessun operazionale, nessun servo di "
    "continua (ADR-003, ADR-007).     Rail +/-15 V.",
    size=9.5, color="#333333")
txt((34.0, 18.75),
    "BLOCCO A e BUFFER (guadagno 1): R138, R143 e i rele' NON montati.     "
    "BLOCCO B (stadio d'uscita): come disegnato, "
    "0 / +3 / +10 dB commutabile.", size=9.5, color="#333333")
txt((34.0, -20.5),
    "Disegno derivato da circuits/preamp/gain_block.py e verificato contro "
    "spice/preamp/gain_block_flat.inc da scripts/check_schematic.py.      "
    "Punti di lavoro: simulati in spice/preamp/tb/tb_op.cir.",
    size=8, color="#333333")
txt((34.0, -21.2),
    "I modelli SPICE usati per quei punti di lavoro sono SEGNAPOSTO scritti "
    "a mano: nessuna cifra di distorsione e' ricavabile da essi.",
    size=8, color="#333333")

# =============================================================================
# Closing check, then emit BOTH artefacts from this one run
# =============================================================================
# Two nodes registered at the SAME point are connected - no wire needed, and
# schemdraw would draw a zero-length line anyway. Formalising that here buys a
# check I could not otherwise make: if two DIFFERENT nets ever land on the same
# coordinate, that is a short circuit in the drawing, and it now fails loudly
# instead of looking tidy.
_by_point = {}
for _n, _xy in NODE_XY.items():
    _by_point.setdefault((round(_xy[0], 6), round(_xy[1], 6)), []).append(_n)
for _pt, _group in sorted(_by_point.items()):
    _nets = {NODE_NET[g] for g in _group}
    assert len(_nets) == 1, (
        f"CORTOCIRCUITO nel disegno: in {_pt} coincidono reti diverse "
        f"{sorted(_nets)} ({', '.join(sorted(_group))})")
    if len(_group) > 1:
        for g in _group:
            _touch(g)

missing = sorted(f"{ref}.{pin}" for ref, pins in DEVICES.items()
                 for pin in pins if f"{ref}.{pin}" not in TOUCHED)
if missing:
    raise AssertionError(
        "terminali ne' cablati ne' etichettati: " + ", ".join(missing))

d.save(SVG)
with open(MANIFEST, "w") as f:
    json.dump({"source_netlist": SOURCE_NETLIST, "devices": DEVICES},
              f, indent=2, sort_keys=True)
    f.write("\n")

print(f"SVG      -> {SVG}")
print(f"manifest -> {MANIFEST}")
print(f"dispositivi disegnati: {len(DEVICES)}")
print(f"terminali cablati o etichettati: {len(TOUCHED)} / "
      f"{sum(len(p) for p in DEVICES.values())}")
if os.environ.get("PREVIEW_PNG"):
    d.save(os.environ["PREVIEW_PNG"], dpi=110)
    print("anteprima PNG ->", os.environ["PREVIEW_PNG"])
