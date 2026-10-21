#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
psu_draw.py - the COMPLETE schematic of the supply board, one A3 page (L63a).

DERIVED DOCUMENTATION, NOT A SOURCE OF TRUTH. The topology lives in
circuits/preamp/psu.py; this file only draws circuits/preamp/psu.net. If the two
disagree, fix this drawing (or the topology at its source) - never the checks.

Every one of the 133 parts is drawn, every pin the netlist connects is a
terminal, every unconnected pin of an integrated circuit carries its cross.
How the drawing is kept honest is in sheet_kit.py: wires only between nodes of
one net, no short in the picture, a name on every island of a net drawn in
pieces, the manifest emitted from the drawing and checked against psu.net in
both directions by scripts/check_schematic.py (block 2d of run_tests.sh).

Run:
  /Users/roberto/EDA/env/venv/bin/python3 docs/preamp/schematic/psu_draw.py

Writes psu.svg, psu.pdf, psu.manifest.json next to this file.
  PSU_SHEET_DIR=<dir>   writes the three files there instead (run_tests.sh:
                        matplotlib stamps ids and a date into the SVG and PDF; the
                        test then compares that manifest with the versioned one).
  PREVIEW_PNG=<file>    also writes a PNG preview (PREVIEW_DPI, default 150).

The page reads left to right as the energy flows (row 1: mains, the audio rails,
VRELAY and the 5 V) and then as the control flows (row 2: reference, supervisor
and mains detector; the micro; the hardware delays and the relay commands).
Nets that run between panels travel BY NAME: the same name is the same net,
and the kit refuses a name that is not the net's.
"""
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)

from sheet_kit import Sheet, DIM, RETCOL, GNDCOL, NETCOL   # noqa: E402

NETLIST = os.path.join(REPO, "circuits", "preamp", "psu.net")
OUT = os.environ.get("PSU_SHEET_DIR") or HERE
SVG = os.path.join(OUT, "psu.svg")
PDF = os.path.join(OUT, "psu.pdf")
MANIFEST = os.path.join(OUT, "psu.manifest.json")

if not os.path.exists(NETLIST):
    sys.exit(f"netlist assente: {NETLIST}\n"
             "rigenerala con: env/venv/bin/python3 circuits/preamp/psu.py")

S = Sheet(NETLIST, "circuits/preamp/psu.net", width=122.0)
two, N, W, to, at, node = S.two, S.N, S.wire, S.to, S.at, S.node
gnd, ret, lab, rail = S.gnd, S.ret, S.label, S.rail
T = S.T
P = S.P
FS = S.fs


def v(ref):
    return S.comp[ref][0]


def num(s):
    """'44.2k' -> 44200.0; 'M' is MEGA, the KiCad convention (limitations #13)."""
    m = re.fullmatch(r"([0-9.]+)\s*([pnumkM]?)", s)
    assert m, f"valore non interpretabile: {s!r}"
    return float(m.group(1)) * {"": 1, "p": 1e-12, "n": 1e-9, "u": 1e-6, "m": 1e-3,
                                "k": 1e3, "M": 1e6}[m.group(2)]


def it(x, nd=2):
    return f"{x:.{nd}f}".replace(".", ",")


def hang(ref, top_net, xy, length=2.0, side=None, sym=None):
    """A part hanging down from `xy` (on top_net) to a ground or return symbol."""
    nets = sorted({n for (r, _), n in S.pin.items() if r == ref})
    other = [n for n in nets if n != top_net]
    assert len(other) == 1, f"{ref}: {nets}"
    x, y = xy
    two(ref, {top_net: (x, y), other[0]: (x, y - length)}, side=side)
    bot = N(ref, other[0])
    if other[0] == "GND":
        gnd(bot)
    elif other[0] == "RLY_RET":
        ret(bot)
    elif sym:
        sym(bot)
    return N(ref, top_net), bot


def chain(*nodes):
    for a, b in zip(nodes, nodes[1:]):
        W(a, b)


# =============================================================================
# the page
# =============================================================================
S.text((61.0, 85.35), "ALIMENTATORE — schematico completo (seconda scheda)", size=11)
S.text((61.0, 84.25),
       f"disegnato da circuits/preamp/psu.net: {len(S.comp)} parti, tutte; ogni piedino "
       "collegato è un terminale, ogni piedino libero degli integrati ha la sua croce. "
       "Le reti con lo stesso nome sono la stessa rete. Verificato contro la netlist nei "
       "due sensi (scripts/check_schematic.py, run_tests.sh 2d).",
       size=FS - 0.3, color=DIM)

# =============================================================================
# 1  MAINS AND TRANSFORMERS
# =============================================================================
S.panel(0.8, 44.5, 24.2, 82.8, "1  Rete e trasformatori",
        "i trasformatori sono fuori scheda, sui loro morsetti")
j510 = S.conn("J510", 2.0, 76.0, ["1", "2"], side="r", sub="dal modulo IEC")
acl = to(j510["1"], 1.9, 0)                                  # (5.6, 75.45)
two("F501", {"AC_L": (6.4, 79.0), "T2_PRI_L": (9.4, 79.0)}, side="t", value="vedi nota")
W(acl, N("F501", "AC_L"), (5.6, 79.0))
j511 = S.conn("J511", 11.2, 79.55, ["1", "2"], side="l")
W(N("F501", "T2_PRI_L"), j511["1"])
S.relay_contact("K501", "13", "14", (7.0, 72.0), (9.6, 72.0))
S.relay_contact("K501", "23", "24", (7.0, 70.0), (9.6, 70.0))
W(acl, T("K501", "13"), (5.6, 72.0))
j512 = S.conn("J512", 11.2, 72.55, ["1", "2"], side="l")
W(T("K501", "14"), j512["1"])
W(T("K501", "24"), j512["2"], (10.1, 70.0))
acn = to(j510["2"], 0.9, 0)                                  # (4.6, 74.65)
W(acn, j511["2"], (4.6, 78.2))
W(acn, T("K501", "23"), (4.6, 70.0))
S.text((8.3, 68.9), "contatti di K501 (bobina: pannello 6)", size=FS - 1.0, color=DIM)
S.text((8.3, 68.35), "K501 a riposo = toroide spento (ADR-048)", size=FS - 1.0, color=DIM)
S.dashed_box(13.4, 76.6, 17.0, 80.6, "T2", "sempre acceso")
S.dashed_box(13.4, 66.4, 17.0, 73.0, "T1", "2 × 15 V, con K501")
j514 = S.conn("J514", 18.4, 79.55, ["1", "2"], side="r")
lab(j514["1"])
lab(j514["2"])
j513 = S.conn("J513", 18.4, 70.55, ["1", "2", "3"], side="r")
g513 = to(j513["2"], 0.7, 0)
g513b = to(g513, 0, -2.6)
gnd(g513b)
S.text((12.5, 63.6), "F501: valore da fissare sul datasheet di T2", size=FS - 1.0, color=DIM)
S.text((12.5, 63.05), f"(nella netlist: «{v('F501')}»)", size=FS - 1.4, color=DIM)

# =============================================================================
# 2  THE AUDIO RAILS
# =============================================================================
YP, YM = 73.0, 54.5
S.panel(24.2, 44.5, 80.0, 82.8, "2  Rail audio ±15,3 V",
        "ponte, serbatoi, R in serie, regolatori lineari a basso rumore; uno Schottky in serie "
        "dopo ciascuno e due sui piedini (ADR-093); tenute 2200 µF; verso la scheda audio da J1")
br = S.bridge("D501", (27.8, 63.5), label_side="r")
W(j513["1"], br["~1"], (25.6, 70.0), (25.6, 63.5))
W(j513["3"], br["~2"], (21.6, 68.4), (21.6, 61.2), (30.0, 61.2), (30.0, 63.5))

# ---- + rail ---------------------------------------------------------------
hang("C501", "RAW_P", (31.0, YP), 2.4)
W(br["+"], N("C501", "RAW_P"), (27.8, YP))
two("R550", {"RAW_P": (33.0, YP), "RAW_PR": (35.6, YP)})
W(N("C501", "RAW_P"), N("R550", "RAW_P"))
hang("C509", "RAW_PR", (37.2, YP))
W(N("R550", "RAW_PR"), N("C509", "RAW_PR"))
ANYPINS = {p: ("b", 0.6 + 0.9 * i) for i, p in
           enumerate(("4", "5", "6", "7", "8", "9", "10", "11", "12", "21"))}
U47_SIDES = {"15": ("l", 1.0), "16": ("l", 1.7), "13": ("l", 2.4), "14": ("l", 3.6),
             "1": ("r", 1.0), "20": ("r", 1.7), "3": ("r", 2.6)}


def tps7a47(ref, x0, y1, gnd_net, title):
    """TPS7A4701: the ANY-OUT pins that the netlist grounds are connected, the
    others carry a cross. Returns the pins and the voltage they program."""
    pins, nc = dict(U47_SIDES), {}
    for p, pos in ANYPINS.items():
        (pins if (ref, p) in S.pin else nc)[p] = pos
    u = S.ic(ref, x0, y1, 9.4, 5.4, pins, nc=nc, title=title)
    # the bus of the ground pins, under their stubs (the crosses stay above it)
    ybus = y1 - 5.4 - 1.4
    gp = sorted((p for p in pins if pins[p][0] == "b"), key=lambda p: pins[p][1])
    for p in gp:
        assert S.pin[(ref, p)] == gnd_net, f"{ref}.{p} non e' a {gnd_net}"
    first = node(f"{ref}_bus_a", gnd_net, (P(u[gp[0]])[0], ybus))
    last = node(f"{ref}_bus_b", gnd_net, (P(u[gp[-1]])[0], ybus))
    W(u[gp[0]], first)
    W(first, last)
    W(u[gp[-1]], last)
    for p in gp[1:-1]:
        W(u[p], node(f"{ref}_bus_{p}", gnd_net, (P(u[p])[0], ybus)))
    g = node(f"{ref}_bus_g", gnd_net, (x0 + 3.2, ybus))
    (gnd if gnd_net == "GND" else ret)(g)
    from sheet_kit import symbol_pins
    sym = symbol_pins(*S.comp[ref][1:])
    prog = sum(float(sym[p].rstrip("V")) for p in gp if sym[p].endswith("V"))
    return u, 1.4 + prog, [sym[p] for p in gp if sym[p].endswith("V")]


u1, VOUT1, PROG1 = tps7a47("U501", 41.0, YP + 1.0, "GND", f"U501  {v('U501')}")
assert abs(VOUT1 - float(v("U501").split()[-1].rstrip("V"))) < 1e-9, (VOUT1, v("U501"))
W(N("C509", "RAW_PR"), u1["15"])
j1in = node("u501_in", "RAW_PR", (39.8, YP))
W(j1in, u1["16"], (39.8, P(u1["16"])[1]))
W(j1in, u1["13"], (39.8, P(u1["13"])[1]))
hang("C507", "NR_P", (38.6, P(u1["14"])[1]), side="l")
W(u1["14"], N("C507", "NR_P"))
o1 = node("u501_out", "VPLUS_REG", (51.6, YP))
W(u1["1"], o1)
W(o1, u1["20"], (51.6, P(u1["20"])[1]))
W(o1, u1["3"], (51.6, P(u1["3"])[1]))
two("D513", {"VPLUS_REG": (53.0, YP + 5.4), "RAW_PR": (38.4, YP + 5.4)})
two("D510", {"VPLUS_REG": (53.0, YP + 3.6), "RAW_PR": (38.4, YP + 3.6)})
W(N("D513", "RAW_PR"), N("D510", "RAW_PR"))
W(N("D510", "RAW_PR"), node("u501_byp_in", "RAW_PR", (38.4, YP)))
W(N("D513", "VPLUS_REG"), N("D510", "VPLUS_REG"))
W(N("D510", "VPLUS_REG"), node("u501_byp_out", "VPLUS_REG", (53.0, YP)))
hang("C511", "VPLUS_REG", (54.2, YP))
W(o1, N("C511", "VPLUS_REG"))
two("D515", {"VPLUS_REG": (56.0, YP), "VPLUS": (58.4, YP)})
W(N("C511", "VPLUS_REG"), N("D515", "VPLUS_REG"))
hang("C505", "VPLUS", (60.4, YP), 2.4)
W(N("D515", "VPLUS"), N("C505", "VPLUS"))
lab(to(N("C505", "VPLUS"), 1.6, 0))
S.text((46.4, YP - 7.8), "ANY-OUT a massa: " + " + ".join(p.replace(".", ",") for p in PROG1)
       + f" + 1,4 V = {it(VOUT1, 1)} V", size=FS - 1.0, color=DIM)

# ---- - rail ---------------------------------------------------------------
hang("C502", "RAW_M", (31.0, YM), 2.4)
W(br["-"], N("C502", "RAW_M"), (27.8, YM))
two("R551", {"RAW_M": (33.0, YM), "RAW_MR": (35.6, YM)})
W(N("C502", "RAW_M"), N("R551", "RAW_M"))
hang("C510", "RAW_MR", (37.2, YM))
W(N("R551", "RAW_MR"), N("C510", "RAW_MR"))
u2 = S.ic("U502", 41.0, YM + 1.0, 5.4, 4.6,
          {"15": ("l", 1.0), "16": ("l", 1.7), "13": ("l", 2.4), "14": ("l", 3.6),
           "1": ("r", 1.0), "20": ("r", 1.7), "3": ("r", 3.6),
           "7": ("b", 2.4), "21": ("b", 4.2)},
          title=f"U502  {v('U502')}")
W(N("C510", "RAW_MR"), u2["15"])
j2in = node("u502_in", "RAW_MR", (39.8, YM))
W(j2in, u2["16"], (39.8, P(u2["16"])[1]))
W(j2in, u2["13"], (39.8, P(u2["13"])[1]))
hang("C508", "NR_M", (38.6, P(u2["14"])[1]), side="l")
W(u2["14"], N("C508", "NR_M"))
yb2 = YM + 1.0 - 4.6 - 1.4
b2a = node("u502_bus_a", "GND", (P(u2["7"])[0], yb2))
b2b = node("u502_bus_b", "GND", (P(u2["21"])[0], yb2))
W(u2["7"], b2a)
W(b2a, b2b)
W(u2["21"], b2b)
gnd(node("u502_bus_g", "GND", (43.6, yb2)))
o2 = node("u502_out", "VMINUS_REG", (47.6, YM))
W(u2["1"], o2)
W(o2, u2["20"], (47.6, P(u2["20"])[1]))
yfb = P(u2["3"])[1]
two("R501", {"VMINUS_REG": (49.0, YM), "FB_M": (49.0, yfb)})
two("C513", {"VMINUS_REG": (51.6, YM), "FB_M": (51.6, yfb)})
hang("R502", "FB_M", (50.3, yfb), 2.2)
chain(u2["3"], N("R501", "FB_M"), N("R502", "FB_M"), N("C513", "FB_M"))
two("D514", {"RAW_MR": (38.4, YM + 5.4), "VMINUS_REG": (53.4, YM + 5.4)})
two("D511", {"RAW_MR": (38.4, YM + 3.6), "VMINUS_REG": (53.4, YM + 3.6)})
W(N("D514", "RAW_MR"), N("D511", "RAW_MR"))
W(N("D511", "RAW_MR"), node("u502_byp_in", "RAW_MR", (38.4, YM)))
W(N("D514", "VMINUS_REG"), N("D511", "VMINUS_REG"))
byp2 = node("u502_byp_out", "VMINUS_REG", (53.4, YM))
W(N("D511", "VMINUS_REG"), byp2)
hang("C512", "VMINUS_REG", (54.8, YM))
chain(o2, N("R501", "VMINUS_REG"), N("C513", "VMINUS_REG"), byp2, N("C512", "VMINUS_REG"))
two("D516", {"VMINUS_REG": (56.4, YM), "VMINUS": (58.8, YM)})
W(N("C512", "VMINUS_REG"), N("D516", "VMINUS_REG"))
hang("C506", "VMINUS", (60.6, YM), 2.4)
W(N("D516", "VMINUS"), N("C506", "VMINUS"))
lab(to(N("C506", "VMINUS"), 1.6, 0))
V_FB = 1.176 * (1 + num(v("R501")) / num(v("R502")))
S.text((45.0, YM - 7.4), f"FB di U502: 1,176 V × (1 + R501 / R502) = {it(V_FB)} V "
       "(il valore «−15.3V» è il nome della parte)", size=FS - 1.0, color=DIM)

# ---- J1, the star, J2 -------------------------------------------------------
jj1 = S.conn("J1", 76.4, 70.0, ["1", "2", "3", "4", "5", "6", "7"], side="l",
             sub="verso la scheda audio")
W(jj1["1"], jj1["2"])
lab(jj1["1"], "left")
W(jj1["3"], jj1["4"])
lab(jj1["3"], "left")
W(jj1["5"], jj1["6"])
lab(jj1["5"], "left")
lab(jj1["7"], "left")
two("NT501", {"RLY_RET": (72.8, 57.6), "GND": (75.2, 57.6)}, side="t")
ret(to(N("NT501", "RLY_RET"), 0, -0.8))
gnd(to(N("NT501", "GND"), 0, -0.8))
S.text((74.0, 55.4), "il solo punto in cui", size=FS - 1.2, color=DIM)
S.text((74.0, 54.85), "GND e RLY_RET si toccano", size=FS - 1.2, color=DIM)
jj2 = S.conn("J2", 76.4, 61.2, ["1"], side="l", sub="ritorno dei relè")
ret(to(to(jj2["1"], -1.6, 0), 0, -0.6))

# =============================================================================
# 3  VRELAY AND THE 5 V
# =============================================================================
S.panel(80.0, 44.5, 121.2, 82.8, "3  VRELAY e i 5 V della logica",
        "da T2: ponte, Schottky, serbatoio proprio, U503 12 V; U504 + U512 in serie per V5 "
        "(ADR-094); Q505 stacca VRELAY in standby (NC-037)")
YR = 73.0
b3 = S.bridge("D503", (84.0, 66.0), label_side="r")
lab(to(b3["~1"], -1.2, 0), "up")
lab(to(b3["~2"], 1.4, 0), "down")
ret(to(b3["-"], 0, -0.5))
rv = node("rect_v_top", "RECT_V", (84.0, YR))
W(b3["+"], rv)
lab(rv, "up")
two("D504", {"RECT_V": (85.6, YR), "RAW_V": (88.0, YR)})
W(rv, N("D504", "RECT_V"))
hang("C520", "RAW_V", (89.6, YR), 2.4)
hang("C522", "RAW_V", (91.6, YR))
chain(N("D504", "RAW_V"), N("C520", "RAW_V"), N("C522", "RAW_V"))
u3, VOUT3, PROG3 = tps7a47("U503", 95.0, YR + 1.0, "RLY_RET", f"U503  {v('U503')}")
assert abs(VOUT3 - float(v("U503").split()[-1].rstrip("V"))) < 1e-9, (VOUT3, v("U503"))
W(N("C522", "RAW_V"), u3["15"])
j3in = node("u503_in", "RAW_V", (93.8, YR))
W(j3in, u3["16"], (93.8, P(u3["16"])[1]))
W(j3in, u3["13"], (93.8, P(u3["13"])[1]))
hang("C521", "NR_V", (92.6, P(u3["14"])[1]), side="l")
W(u3["14"], N("C521", "NR_V"))
o3 = node("u503_out", "VRELAY_REG", (105.6, YR))
W(u3["1"], o3)
W(o3, u3["20"], (105.6, P(u3["20"])[1]))
W(o3, u3["3"], (105.6, P(u3["3"])[1]))
two("D512", {"VRELAY_REG": (107.0, YR + 3.6), "RAW_V": (93.0, YR + 3.6)})
W(N("D512", "RAW_V"), node("u503_byp_in", "RAW_V", (93.0, YR)))
byp3 = node("u503_byp_out", "VRELAY_REG", (107.0, YR))
W(N("D512", "VRELAY_REG"), byp3)
hang("C523", "VRELAY_REG", (108.2, YR), 2.4)
hang("C524", "VRELAY_REG", (109.8, YR))
lab(N("C524", "VRELAY_REG"), "up")
# the gate of Q505: R540 and R539 in one column (pull-up and the drive from Q506)
two("C531", {"VRELAY_REG": (112.8, YR), "SW_G": (112.8, YR - 3.0)}, side="t")
two("R540", {"VRELAY_REG": (114.8, YR), "SW_G": (114.8, YR - 3.0)}, side="t")
q505 = S.pmos("Q505", (116.8, YR - 2.4), gate="left")
chain(o3, byp3, N("C523", "VRELAY_REG"), N("C524", "VRELAY_REG"),
      N("C531", "VRELAY_REG"), N("R540", "VRELAY_REG"))
W(N("R540", "VRELAY_REG"), q505["S"], (116.8, YR))
ysw = P(q505["G"])[1]
assert abs(ysw - (YR - 3.0)) < 1e-6, ysw
two("R539", {"SW_G": (114.8, ysw), "SW_D": (114.8, ysw - 2.6)}, side="l")
chain(N("C531", "SW_G"), N("R540", "SW_G"), N("R539", "SW_G"), q505["G"])
q506 = S.nmos("Q506", (114.8, ysw - 3.4), gate="left")
W(N("R539", "SW_D"), q506["D"])
lab(q506["G"], "left")
ret(q506["S"])
vrel = to(q505["D"], 0, -1.0)
lab(to(vrel, 1.2, 0))
# the 5 V: two LDOs in series (ADR-094)
YV = 60.0
vr2 = node("vrelay_reg_5v", "VRELAY_REG", (86.2, YV))
lab(vr2, "left")
u4 = S.ic("U504", 87.6, YV + 1.0, 3.6, 2.4, {"1": ("l", 1.0), "3": ("r", 1.0), "2": ("b", 1.8)},
          title=f"U504  {v('U504')}")
W(vr2, u4["1"])
ret(u4["2"])
hang("C536", "V5_PRE", (93.4, YV))
W(u4["3"], N("C536", "V5_PRE"))
u12 = S.ic("U512", 95.8, YV + 1.0, 3.6, 2.4, {"1": ("l", 1.0), "3": ("r", 1.0), "2": ("b", 1.8)},
           title=f"U512  {v('U512')}")
W(N("C536", "V5_PRE"), u12["1"])
ret(u12["2"])
hang("C525", "V5", (101.6, YV))
W(u12["3"], N("C525", "V5"))
lab(to(N("C525", "V5"), 1.6, 0))
S.text((94.6, YV - 3.6), "due regolatori in serie: un corto di U504 non porta 12 V al micro "
       "(ADR-094)", size=FS - 1.0, color=DIM)
S.text((100.4, YR - 7.8), "ANY-OUT a RLY_RET: " + " + ".join(p.replace(".", ",") for p in PROG3)
       + f" + 1,4 V = {it(VOUT3, 1)} V", size=FS - 1.0, color=DIM)

# =============================================================================
# 4  REFERENCE, SUPERVISOR, MAINS DETECTOR
# =============================================================================
S.panel(0.8, 0.8, 46.0, 44.0, "4  Riferimento, sorvegliante, rivelatore di rete",
        "quattro comparatori open-drain in OR su MUTE_G: il mute senza il firmware (ADR-048 p. 5)")
XO, XB = 40.0, 42.4                 # comparator outputs, MUTE_G bus
cA = S.comparator("U505", "A", {"-": "2", "+": "3", "out": "1"}, (XO, 37.0), power=("8", "4"),
                  note=v("U505").split()[0])
cB = S.comparator("U505", "B", {"-": "6", "+": "5", "out": "7"}, (XO, 29.0))
cC = S.comparator("U506", "B", {"-": "6", "+": "5", "out": "7"}, (XO, 21.0),
                  note=v("U506").split()[0])
cD = S.comparator("U506", "A", {"-": "2", "+": "3", "out": "1"}, (XO, 11.5), power=("8", "4"))
# power of the two duals, with their decoupling
for c, cref, ytop in ((cA, "C517", 40.4), (cD, "C519", 15.2)):
    vtop = node(f"{cref}_v5", "V5", (P(c["V+"])[0], ytop))
    W(c["V+"], vtop)
    rail(vtop)
    hang(cref, "V5", (P(c["V+"])[0] - 1.4, ytop), 1.6, side="l")
    W(vtop, N(cref, "V5"))
    ret(c["V-"])
# the MUTE_G bus
bus = [node(f"mg_{i}", "MUTE_G", (XB, P(c["out"])[1])) for i, c in enumerate((cA, cB, cC, cD))]
for c, b in zip((cA, cB, cC, cD), bus):
    W(c["out"], b)
chain(*bus)
lab(to(bus[-1], 0, -3.6), "down")


def divider(top_ref, bot_ref, mid_net, x, ymid, ytop, ybot, top_sym, bot_sym):
    """Two resistors in a column, their common node on the comparator's input row."""
    tnet = [n for (r, _), n in S.pin.items() if r == top_ref and n != mid_net][0]
    bnet = [n for (r, _), n in S.pin.items() if r == bot_ref and n != mid_net][0]
    two(top_ref, {tnet: (x, ytop), mid_net: (x, ymid)})
    two(bot_ref, {mid_net: (x, ymid), bnet: (x, ybot)})
    top_sym(N(top_ref, tnet))
    bot_sym(N(bot_ref, bnet))


def to_adc(ref, net, x, y):
    adc = [n for (r, _), n in S.pin.items() if r == ref and n != net][0]
    two(ref, {net: (x, y), adc: (x, y - 2.4)})
    lab(N(ref, adc), "down")


# row A - U505 A: VPLUS too low
yA = P(cA["+"])[1]
divider("R506", "R507", "SUP_P", 20.0, yA, yA + 3.0, yA - 2.2, rail, ret)
hang("C515", "SUP_P", (22.4, yA))
to_adc("R544", "SUP_P", 24.8, yA)
chain(N("R506", "SUP_P"), N("C515", "SUP_P"), N("R544", "SUP_P"), cA["+"])
lab(to(cA["-"], -0.8, 0), "left")
# row B - U505 B: VMINUS too low (its divider runs from VREF to VMINUS)
yB = P(cB["-"])[1]
two("R508", {"VREF": (20.0, yB + 2.4), "SUP_M": (20.0, yB)})
two("R509", {"SUP_M": (20.0, yB), "VMINUS": (20.0, yB - 2.8)})
rail(N("R508", "VREF"))
rail(N("R509", "VMINUS"), up=False)
hang("C516", "SUP_M", (22.4, yB))
to_adc("R545", "SUP_M", 24.8, yB)
chain(N("R508", "SUP_M"), N("C516", "SUP_M"), N("R545", "SUP_M"), cB["-"])
yBp = P(cB["+"])[1]
two("R504", {"VREF": (31.0, yBp), "VREF_HALF": (33.6, yBp)})
hang("R505", "VREF_HALF", (35.0, yBp), 2.2)
chain(N("R504", "VREF_HALF"), N("R505", "VREF_HALF"), cB["+"])
lab(N("R504", "VREF"), "left")
# row C - U506 B: VRELAY_REG too low
yC = P(cC["+"])[1]
divider("R522", "R523", "SUP_VR", 20.0, yC, yC + 3.0, yC - 2.8, rail, ret)
hang("C526", "SUP_VR", (22.4, yC))
to_adc("R546", "SUP_VR", 24.8, yC)
chain(N("R522", "SUP_VR"), N("C526", "SUP_VR"), N("R546", "SUP_VR"), cC["+"])
lab(to(cC["-"], -0.8, 0), "left")
# row D - U506 A: no half-wave of the mains (the detector on T2's rectified secondary)
yD = P(cD["-"])[1]
rvin = node("rect_v_det", "RECT_V", (3.0, yD + 1.6))
lab(rvin, "up")
two("R510", {"RECT_V": (3.8, yD + 1.6), "MD_B_R": (6.4, yD + 1.6)})
two("R554", {"MD_B_R": (6.4, yD + 1.6), "MD_B": (9.0, yD + 1.6)})
W(rvin, N("R510", "RECT_V"))
q504 = S.npn("Q504", (10.6 + 0.6, yD + 1.6 + 0.56), base="left")
hang("R511", "MD_B", (9.6, yD + 1.6), 2.2, side="l")
chain(N("R554", "MD_B"), N("R511", "MD_B"), q504["B"])
ret(q504["E"])
ymd = yD + 4.0
two("R512", {"V5": (13.6, ymd + 5.6), "MD_R": (13.6, ymd + 2.8)})
two("R555", {"MD_R": (13.6, ymd + 2.8), "MD": (13.6, ymd)})
rail(N("R512", "V5"))
mdn = node("md_c", "MD", (P(q504["C"])[0], ymd))
W(q504["C"], mdn)
hang("C518", "MD", (15.8, ymd))
to_adc("R547", "MD", 18.2, ymd)
chain(mdn, N("R555", "MD"), N("C518", "MD"), N("R547", "MD"))
W(N("R547", "MD"), cD["-"], (34.6, ymd), (34.6, yD))
lab(to(cD["+"], -0.8, 0), "left")
# the reference
two("R503", {"V5": (7.0, 40.0), "VREF_R": (7.0, 37.4)})
two("R553", {"VREF_R": (7.0, 37.4), "VREF": (7.0, 34.8)})
rail(N("R503", "V5"))
S.zref("U507", (7.0, 32.2), (7.0, 34.8), side="l")
ret(T("U507", "2"))
hang("C514", "VREF", (9.6, 34.8))
vref = node("vref_out", "VREF", (12.2, 34.8))
chain(N("R553", "VREF"), N("C514", "VREF"), vref)
lab(vref)
# the thresholds, from the values
V_REF = float(re.search(r"-(\d+(?:\.\d+)?)$", v("U507")).group(1))
TRIP_P = V_REF * (1 + num(v("R506")) / num(v("R507")))
V_HALF = V_REF * num(v("R505")) / (num(v("R504")) + num(v("R505")))
_k = num(v("R508")) / (num(v("R508")) + num(v("R509")))
TRIP_M = (V_HALF - V_REF * (1 - _k)) / _k
TRIP_V = V_REF * (1 + num(v("R522")) / num(v("R523")))
S.text((2.0, 29.4), "le soglie, dai valori:", size=FS - 0.8, color=DIM, halign="left")
S.text((2.0, 28.75), f"VPLUS < {it(TRIP_P)} V   VMINUS > {it(TRIP_M)} V", size=FS - 0.8,
       color=DIM, halign="left")
S.text((2.0, 28.1), f"VRELAY_REG < {it(TRIP_V)} V   (VREF {it(V_REF, 3)} V)", size=FS - 0.8,
       color=DIM, halign="left")
S.text((2.0, yD - 3.8), "Q504 conduce a ogni semionda di RECT_V e scarica C518; senza",
       size=FS - 0.8, color=DIM, halign="left")
S.text((2.0, yD - 4.35), "semionde MD sale verso V5 e U506 A tira giù MUTE_G",
       size=FS - 0.8, color=DIM, halign="left")

# =============================================================================
# 5  THE MICRO AND ITS INPUTS
# =============================================================================
S.panel(46.0, 0.8, 77.0, 44.0, "5  Il temporizzatore: il micro e i suoi ingressi",
        "la sequenza è del firmware (firmware/preamp_timer/), l'ordine è dell'hardware (pannello 6)")
u9 = S.ic("U509", 58.0, 38.0, 9.0, 24.0,
          {"1": ("t", 8.0), "20": ("b", 4.5),
           "3": ("l", 2.0), "4": ("l", 3.0), "5": ("l", 4.0), "6": ("l", 5.0),
           "14": ("l", 7.0), "12": ("l", 13.0), "13": ("l", 19.0),
           "11": ("r", 2.0), "10": ("r", 4.0), "8": ("r", 6.0), "9": ("r", 8.0),
           "16": ("r", 12.0)},
          nc={"2": ("l", 21.0), "7": ("l", 22.0), "15": ("l", 23.0),
              "17": ("r", 15.0), "18": ("r", 16.0), "19": ("r", 17.0)},
          title=f"U509  {v('U509')}")
v9 = to(u9["1"], 0, 1.4)
rail(v9)
hang("C534", "V5", (69.0, P(v9)[1]))
W(v9, N("C534", "V5"))
ret(u9["20"])
for p in ("3", "4", "5", "6", "11", "10", "8", "9"):
    lab(u9[p], "left" if p in ("3", "4", "5", "6") else "right")
ymg = P(u9["14"])[1]
two("R543", {"MUTE_G": (51.6, ymg), "MUTE_G_IN": (54.4, ymg)})
W(N("R543", "MUTE_G_IN"), u9["14"])
lab(N("R543", "MUTE_G"), "left")
yfr = P(u9["12"])[1]
j508 = S.conn("J508", 47.4, yfr + 0.55, ["1", "2"], side="r", title="interruttore frontale")
ret(to(to(j508["2"], 0.8, 0), 0, -0.6))
two("R518", {"V5": (50.2, yfr + 2.8), "FRONT_SW": (50.2, yfr)}, side="r")
rail(N("R518", "V5"))
two("R541", {"FRONT_SW": (51.4, yfr), "FRONT_IN": (53.8, yfr)}, side="b")
hang("C532", "FRONT_IN", (55.4, yfr))
chain(j508["1"], N("R518", "FRONT_SW"), N("R541", "FRONT_SW"))
chain(N("R541", "FRONT_IN"), N("C532", "FRONT_IN"), u9["12"])
ysw2 = P(u9["13"])[1]
msw = node("mute_sw_in_lbl", "MUTE_SW", (49.8, ysw2))
lab(msw, "left")
two("R517", {"V5": (50.8, ysw2 + 2.8), "MUTE_SW": (50.8, ysw2)}, side="l")
rail(N("R517", "V5"))
two("R542", {"MUTE_SW": (51.6, ysw2), "MUTE_SW_IN": (54.0, ysw2)})
hang("C533", "MUTE_SW_IN", (55.4, ysw2))
chain(msw, N("R517", "MUTE_SW"), N("R542", "MUTE_SW"))
chain(N("R542", "MUTE_SW_IN"), N("C533", "MUTE_SW_IN"), u9["13"])
j515 = S.conn("J515", 73.0, P(u9["16"])[1] + 0.55, ["1", "2", "3"], side="l",
              title="programmazione")
W(u9["16"], j515["1"])
u5v = to(j515["2"], -1.0, 0)
lab(to(u5v, 0, -2.4), "down")
ret(to(to(j515["3"], -0.5, 0), 0, -0.6))
# the legend
S.text((47.0, 9.6), "Legenda", size=FS + 0.5, halign="left")
S.d.add(__import__("schemdraw").elements.Ground(lead=False).theta(0).at((48.0, 8.4))
        .color(GNDCOL).scale(0.85))
S.text((49.0, 8.2), "GND — la massa audio (rail, serbatoi, J1)", halign="left")
S.d.add(__import__("schemdraw").elements.GroundSignal(lead=False).theta(0).at((48.0, 6.8))
        .color(RETCOL).scale(0.85))
S.text((49.0, 6.6), "RLY_RET — il ritorno delle bobine e della logica; tocca GND solo in NT501",
       halign="left")
S.text((48.0, 5.0), "NOME", color=NETCOL)
S.text((49.0, 5.0), "una rete per nome: la stessa scritta in due punti è un filo", halign="left")
S.text((47.4, 3.6), "×  piedino libero (nessuna rete nella netlist)", halign="left")
S.text((47.4, 2.4), "i punti di giunzione li mette il disegno dove si incontrano tre fili",
       halign="left", color=DIM, size=FS - 0.8)

# =============================================================================
# 6  THE HARDWARE DELAYS AND THE RELAY COMMANDS
# =============================================================================
S.panel(77.0, 0.8, 121.2, 44.0, "6  I ritardi in hardware e i comandi dei relè",
        "Δ: PERMIT_CMD non prima di Δ dopo la caduta di MUTE_REQ; Δ₂: VRELAY dopo PERMIT "
        "(ADR-049); i sink a bassa tensione e la bobina di K501")
# ---- MUTE_REQ -> MUTE_G --------------------------------------------------------
ymr = 39.6
mreq = node("mute_req_in", "MUTE_REQ", (82.4, ymr))
lab(mreq, "up")
hang("R525", "MUTE_REQ", (83.6, ymr), 2.2, side="r")
two("R513", {"MUTE_REQ": (85.0, ymr), "MUTE_G": (87.6, ymr)})
hang("R514", "MUTE_G", (88.8, ymr), 2.2)
hang("C527", "MUTE_G", (92.0, ymr))
two("D522", {"MUTE_G": (112.0, ymr), "PERMIT_G": (112.0, 32.6 + 0.5)})
mg6 = node("mute_g_lbl", "MUTE_G", (114.0, ymr))
chain(mreq, N("R525", "MUTE_REQ"), N("R513", "MUTE_REQ"))
chain(N("R513", "MUTE_G"), N("R514", "MUTE_G"), N("C527", "MUTE_G"), N("D522", "MUTE_G"), mg6)
lab(mg6)
# ---- PERMIT_T: the two requests through their diodes -------------------------------
ypa, ypt = 35.4, 32.6
mbr = node("mute_req_pt", "MUTE_REQ", (82.4, ypa))
W(mreq, mbr)
two("R532", {"MUTE_REQ": (83.6, ypa), "PT_A": (86.2, ypa)})
two("D520", {"PT_A": (86.8, ypa), "PERMIT_T": (89.2, ypa)})
chain(mbr, N("R532", "MUTE_REQ"))
W(N("R532", "PT_A"), N("D520", "PT_A"))
preq = node("permit_req_in", "PERMIT_REQ", (81.6, ypt))
lab(preq, "left")
hang("R526", "PERMIT_REQ", (82.8, ypt), 2.2, side="l")
two("R533", {"PERMIT_REQ": (83.6, ypt), "PT_B": (86.2, ypt)})
two("D521", {"PT_B": (86.8, ypt), "PERMIT_T": (89.2, ypt)})
chain(preq, N("R526", "PERMIT_REQ"), N("R533", "PERMIT_REQ"))
W(N("R533", "PT_B"), N("D521", "PT_B"))
ptj = node("permit_t_j", "PERMIT_T", (90.4, ypt))
W(N("D520", "PERMIT_T"), ptj, (90.4, ypa))
W(N("D521", "PERMIT_T"), ptj)
hang("C528", "PERMIT_T", (91.4, ypt))
hang("R534", "PERMIT_T", (94.0, ypt), 1.8)
cE = S.comparator("U508", "A", {"-": "2", "+": "3", "out": "1"}, (100.6, ypt + 0.5),
                  power=("8", "4"), note=v("U508").split()[0])
assert abs(P(cE["+"])[1] - ypt) < 1e-3
pt_in = node("permit_t_in", "PERMIT_T", (P(cE["+"])[0] - 0.6, P(cE["+"])[1]))
two("D523", {"PERMIT_T": (96.6, ypt), "VR_T": (96.6, ypt - 4.4)}, side="l")
chain(ptj, N("C528", "PERMIT_T"), N("R534", "PERMIT_T"), N("D523", "PERMIT_T"))
W(N("D523", "PERMIT_T"), cE["+"])
lab(to(cE["-"], -0.8, 0), "up")
v8 = node("u508_v5", "V5", (P(cE["V+"])[0], ypt + 4.2))
W(cE["V+"], v8)
rail(v8)
hang("C530", "V5", (P(cE["V+"])[0] + 1.6, ypt + 4.2), 1.6)
W(v8, N("C530", "V5"))
ret(cE["V-"])
ypg = P(cE["out"])[1]
two("R524", {"PERMIT_G": (103.4, ypg), "V5": (103.4, ypg + 2.6)}, side="r")
rail(N("R524", "V5"))
hang("R516", "PERMIT_G", (106.4, ypg), 2.2, side="l")
pgl = node("permit_g_lbl", "PERMIT_G", (114.0, ypg))
chain(cE["out"], N("R524", "PERMIT_G"), N("R516", "PERMIT_G"))
chain(N("R516", "PERMIT_G"), N("D522", "PERMIT_G"), pgl)
lab(pgl)
# ---- VR_T: Δ2 -------------------------------------------------------------------
yvt = ypt - 4.4
ven = node("vrelay_en_in", "VRELAY_EN", (81.6, yvt))
lab(ven, "left")
hang("R527", "VRELAY_EN", (82.8, yvt), 2.2, side="l")
two("R535", {"VRELAY_EN": (83.6, yvt), "VE_A": (86.2, yvt)})
two("D524", {"VE_A": (86.8, yvt), "VR_T": (89.2, yvt)})
chain(ven, N("R527", "VRELAY_EN"), N("R535", "VRELAY_EN"))
W(N("R535", "VE_A"), N("D524", "VE_A"))
hang("C529", "VR_T", (91.4, yvt))
hang("R536", "VR_T", (94.0, yvt), 2.2)
cF = S.comparator("U508", "B", {"-": "6", "+": "5", "out": "7"}, (100.6, yvt + 0.5))
chain(N("D524", "VR_T"), N("C529", "VR_T"), N("R536", "VR_T"), N("D523", "VR_T"), cF["+"])
lab(to(cF["-"], -0.8, 0), "up")
yvg = P(cF["out"])[1]
two("R537", {"VR_G": (108.6, yvg), "V5": (108.6, yvg + 2.6)}, side="l")
rail(N("R537", "V5"))
hang("R538", "VR_G", (110.4, yvg), 2.2)
vgl = node("vr_g_lbl", "VR_G", (112.4, yvg))
chain(cF["out"], N("R537", "VR_G"), N("R538", "VR_G"), vgl)
lab(vgl)
TAU_T = num(v("R534")) * num(v("C528"))
TAU_T2 = num(v("R536")) * num(v("C529"))
S.text((97.0, yvt - 3.4), f"τ di Δ = R534 · C528 = {it(TAU_T * 1e3, 1)} ms;   "
       f"τ di Δ₂ = R536 · C529 = {it(TAU_T2 * 1e3, 1)} ms", size=FS - 0.8, color=DIM)

# ---- the low-side sinks ------------------------------------------------------------
YQ = 12.6


def sink(qref, x, gate_net, drain_net, clamp=None):
    q = S.nmos(qref, (x, YQ), gate="left", label_side="r")
    lab(q["G"], "left")
    ret(q["S"])
    top = to(q["D"], 0, 2.2)
    if clamp:
        d1, d2, z = clamp
        y = P(top)[1]
        two(d1, {drain_net: (x, y), [n for (r, _), n in S.pin.items()
                                     if r == d1 and n != drain_net][0]: (x, y + 1.5)}, side="l")
        mid = [n for (r, _), n in S.pin.items() if r == d1 and n != drain_net][0]
        cl = [n for (r, _), n in S.pin.items() if r == d2 and n != mid][0]
        two(d2, {mid: (x, y + 1.5), cl: (x, y + 3.0)}, side="l")
        two(z, {cl: (x, y + 3.0), "VRELAY": (x, y + 4.6)}, side="l")
        lab(N(z, "VRELAY"), "up")
        W(top, N(d1, drain_net))
    lab(to(top, 0.0, 0.0) if False else top, "right")
    return q


sink("Q501", 86.0, "MUTE_G", "MUTE_CMD", clamp=("D506", "D530", "D507"))
sink("Q502", 95.0, "PERMIT_G", "PERMIT_CMD", clamp=("D508", "D531", "D509"))
# the mains relay: MAINS_REQ -> Q503 -> R552 -> the coil of K501
q503 = S.nmos("Q503", (110.4, YQ), gate="left", label_side="r")
ret(q503["S"])
yg = P(q503["G"])[1]
mrq = node("mains_req_in", "MAINS_REQ", (100.4, yg))
lab(mrq, "up")
hang("R528", "MAINS_REQ", (101.6, yg), 2.2, side="l")
two("R520", {"MAINS_REQ": (102.6, yg), "MAINS_G": (105.2, yg)})
hang("R521", "MAINS_G", (106.6, yg), 2.2)
chain(mrq, N("R528", "MAINS_REQ"), N("R520", "MAINS_REQ"))
chain(N("R520", "MAINS_G"), N("R521", "MAINS_G"), q503["G"])
two("R552", {"MAINS_SINK": (110.4, YQ + 0.8), "MAINS_COIL": (110.4, YQ + 3.2)})
W(q503["D"], N("R552", "MAINS_SINK"))
S.relay_coil("K501", (110.4, YQ + 7.6), (110.4, YQ + 4.4), side="l",
             note="contatti: pannello 1")
mc = node("mains_coil_j", "MAINS_COIL", (110.4, YQ + 3.8))
chain(N("R552", "MAINS_COIL"), mc, T("K501", "A2"))
two("D505", {"MAINS_COIL": (112.6, YQ + 3.8), "MAINS_COIL_D": (112.6, YQ + 5.8)})
two("D532", {"MAINS_COIL_D": (112.6, YQ + 5.8), "VRELAY_REG": (112.6, YQ + 7.8)})
W(mc, N("D505", "MAINS_COIL"))
vrk = node("vrelay_reg_k501", "VRELAY_REG", (110.4, YQ + 8.4))
W(T("K501", "A1"), vrk)
W(N("D532", "VRELAY_REG"), vrk, (112.6, YQ + 8.4))
lab(to(vrk, 0, 0.6), "up")
# J4, to the audio board
j4 = S.conn("J4", 118.4, 9.0, ["1", "2", "3"], side="l", sub="verso la scheda audio")
for p in ("1", "2", "3"):
    lab(j4[p], "left")
S.text((100.8, 2.4), "MUTE_CMD e PERMIT_CMD: sink verso RLY_RET; la bobina del relè è sulla "
       "scheda audio, tra VRELAY e il sink", size=FS - 0.8, color=DIM)

# =============================================================================
stats = S.finish(SVG, PDF, MANIFEST, png=os.environ.get("PREVIEW_PNG"),
                 png_dpi=int(os.environ.get("PREVIEW_DPI", "150")))
print(f"SVG      -> {SVG}")
print(f"PDF      -> {PDF}")
print(f"manifest -> {MANIFEST}")
print(f"parti disegnate: {stats['parts']} / {len(S.comp)}   terminali: {stats['terminals']}   "
      f"piedini liberi segnati: {stats['nc']}")
print(f"reti: {stats['nets']}   isole: {stats['islands']}   nomi: {stats['named']}   "
      f"giunzioni: {stats['dots']}")
print("testi: nessuno sopra un altro, un filo o una parte")
