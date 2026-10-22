#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
audio_draw.py - the COMPLETE schematic of the audio board, one A2 page (L63b).

DERIVED DOCUMENTATION, NOT A SOURCE OF TRUTH. The topology lives in
circuits/preamp/preamp_audio.py (and gain_block.py, trim.py, selector.py,
gain_interlock.py); this file only draws circuits/preamp/preamp_audio.net. If
the two disagree, fix this drawing (or the topology at its source) - never the
checks.

«Blocco una volta, un canale» (the user's reading of «senza blocchi ripetuti»,
L63a, 2026-10-21):
  - the gain block is drawn ONCE, complete, from circuits/preamp/gain_block.net
    (the block with every optional part fitted), with the table of its eight
    instances on the board: their refs, what is not fitted, their ports;
  - the LEFT channel is drawn, the right one is named: its refs (+200, the trim
    +10), its nets (L_ -> R_), and the right poles of the shared relays drawn
    with their own nets;
  - everything else part by part.
How the drawing is kept honest is in sheet_kit.py: Sheet.fold() derives the
table and the left -> right correspondence and asserts them on the netlist, and
finish() expands the drawing into a manifest of all the board's parts (578 since ADR-097), which
scripts/check_schematic.py compares with preamp_audio.net in both directions
(block 2d of run_tests.sh).

A3 or A2: the user's «A3 first, A2 if it won't fit» (L63b). At the supply page's
scale (5 pt, ~7 mm resistors) the supply page fills an A3 with 133 parts and 349
pins; this one draws 138 parts and ~420 pins plus a 59-row table: ~1.2 A3 before
the table. So A2, at the same scale: the two pages print alike.

Run:
  /Users/roberto/EDA/env/venv/bin/python3 docs/preamp/schematic/audio_draw.py

Writes audio.svg, audio.pdf, audio.manifest.json next to this file.
  AUDIO_SHEET_DIR=<dir>  writes the three files there instead (run_tests.sh 2f).
  PREVIEW_PNG=<file>     also writes a PNG preview (PREVIEW_DPI, default 150).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)

from sheet_kit import Sheet, DIM, RETCOL, GNDCOL, NETCOL   # noqa: E402

NETLIST = os.path.join(REPO, "circuits", "preamp", "preamp_audio.net")
BLOCK = os.path.join(REPO, "circuits", "preamp", "gain_block.net")
OUT = os.environ.get("AUDIO_SHEET_DIR") or HERE
SVG = os.path.join(OUT, "audio.svg")
PDF = os.path.join(OUT, "audio.pdf")
MANIFEST = os.path.join(OUT, "audio.manifest.json")

for f in (NETLIST, BLOCK):
    if not os.path.exists(f):
        sys.exit(f"netlist assente: {f}\nrigenerala con: env/venv/bin/python3 "
                 "circuits/preamp/preamp_audio.py (e gain_block.py)")

A2 = (594 / 25.4, 420 / 25.4)
S = Sheet(NETLIST, "circuits/preamp/preamp_audio.net", width=172.5, page=A2)
S.template(BLOCK, "BLK", "circuits/preamp/gain_block.net")
two, N, W, to, at, node = S.two, S.N, S.wire, S.to, S.at, S.node
gnd, ret, lab, rail = S.gnd, S.ret, S.label, S.rail
T, P, FS = S.T, S.P, S.fs


# L45d2b3b1: SKiDL keeps ONE name of two joined nets, and which one depends on the order of the
# parts: adding R160 (ADR-097) turned AL_OUT into F1L_IN and L_FIXOUT2 / R_FIXOUT2 into
# L_FIXJACK2 / R_FIXJACK2, with the same pins (data/2026-10-22/L45d2b3b1/script/nomi_reti.py;
# limitations #74). The page asks for a net by the name it was drawn with; if the netlist has
# the other name instead, that one is used. Never both, never neither.
SINONIMI = {"AL_OUT": "F1L_IN", "L_FIXOUT2": "L_FIXJACK2", "R_FIXOUT2": "R_FIXJACK2"}


def rete(n):
    """A net of the page by its drawn name, or by its declared synonym (exactly one exists)."""
    alt = SINONIMI.get(n)
    ci = [x for x in (n, alt) if x and x in S.nets]
    assert len(ci) == 1, f"rete {n}: nella netlist {ci or 'nessuna'} (sinonimi {SINONIMI})"
    return ci[0]


def b(x):
    """A net of the block drawn once (the template)."""
    return "BLK:" + x


def t(r):
    """A part of the block drawn once."""
    return "BLK:" + r


def nets(ref):
    return sorted({n for (r, _), n in S.pin.items() if r == ref})


def hang(ref, top_net, xy, length=2.2, side=None, sym=None):
    """A part hanging down from xy (on top_net); a ground or RLY_RET below it gets
    its symbol. Returns (top node, bottom node)."""
    other = [n for n in nets(ref) if n != top_net]
    assert len(other) == 1, f"{ref}: {nets(ref)}"
    x, y = xy
    two(ref, {top_net: (x, y), other[0]: (x, y - length)}, side=side)
    bot = N(ref, other[0])
    if S.show(other[0]) == "GND":
        gnd(bot)
    elif S.show(other[0]) == "RLY_RET":
        ret(bot)
    elif sym:
        sym(bot)
    return N(ref, top_net), bot


def chain(*nodes):
    for a, c in zip(nodes, nodes[1:]):
        W(a, c)


def notes(x, y, lines, size=None, color=DIM, step=0.62):
    for i, s in enumerate(lines):
        S.text((x, y - i * step), s, size=size or FS - 0.8, color=color, halign="left")


def ground_right(n, dx=0.5):
    """A ground symbol at the end of a short stub to the right of n."""
    gnd(to(n, dx, 0))


def ret_right(n, dx=0.5):
    ret(to(n, dx, 0))


# =============================================================================
# the fold: what the drawing stands for (sheet_kit.Sheet.fold derives and asserts)
# =============================================================================
def left(ref):
    """A part of the left channel outside the blocks: 1xx / 2xx above 60 (the
    channel's own numbering, preamp_audio.py `_n[0] = 60`), the connectors J1xx /
    J2xx, the trim ladder R90x (trim.py, base 900)."""
    letter, n = S._num(ref)
    return (100 <= n < 300 and (n % 100 > 60 or letter == "J")) or 900 <= n < 910


def ref_lr(ref):
    """The right twin: channel base 300 instead of 100 (preamp_audio.py), trim 910."""
    letter, n = S._num(ref)
    return f"{letter}{n + (10 if n >= 900 else 200)}"


PREFIX_LR = (("L_", "R_"), ("AL_", "AR_"), ("BL_", "BR_"), ("F1L_", "F1R_"), ("F2L_", "F2R_"))


def net_lr(n):
    for a, c in PREFIX_LR:
        if n.startswith(a):
            return c + n[len(a):]
    return n


INSTANCES = [("AL", 100), ("BL", 200), ("AR", 300), ("BR", 400),
             ("F1L", 500), ("F2L", 600), ("F1R", 700), ("F2R", 800)]
F = S.fold(INSTANCES,
           # gain_block.py fits these only with r_in / switchable: found by their nets
           {"R_IN": ("IN", "GND"), "R_g": ("FB", "RG"), "R_g10": ("FB", "RG10")},
           100,                       # gain_block.net: gain_block(tag="", base=100)
           left, ref_lr, net_lr,
           [("AL", "AR"), ("BL", "BR"), ("F1L", "F1R"), ("F2L", "F2R")],
           value_lr=lambda v: v.replace("_L", "_R"))
ONLY = {role: sorted(tag for tag in F["instances"] if role not in F["absent"][tag])
        for role in F["optional"]}

# =============================================================================
# the page
# =============================================================================
S.text((86.25, 121.0), "SCHEDA AUDIO — schematico completo (prima scheda)", size=11)
S.text((86.25, 119.95),
       f"disegnato da circuits/preamp/preamp_audio.net, {len(S.comp) - len(F['tparts'])} parti: "
       "il blocco di guadagno una volta (riquadro 7, da circuits/preamp/gain_block.net) con la "
       "tabella delle otto istanze (riquadro 8); il canale sinistro disegnato, il destro nominato; "
       "tutto il resto parte per parte.",
       size=FS - 0.3, color=DIM)
S.text((86.25, 119.3),
       "Le reti con lo stesso nome sono la stessa rete. Verificato contro la netlist nei due sensi "
       f"su tutte le {len(S.comp) - len(F['tparts'])} parti, il blocco espanso nelle otto istanze e il sinistro nel destro "
       "(scripts/check_schematic.py, run_tests.sh 2d).", size=FS - 0.3, color=DIM)

# =============================================================================
# 1  INPUTS AND SELECTOR (left channel; the right poles of K13-K16: panel 5)
# =============================================================================
S.panel(0.8, 80.4, 21.0, 118.6, "1  Ingressi e selettore",
        "canale sinistro; ogni ingresso a 0 V (ADR-064)")
YIN = [112.0, 105.0, 98.0, 91.0]
XBUS = 17.6
YA = 95.0
bus_in = []
for k, y in enumerate(YIN):
    n = k + 1
    j = S.conn(f"J10{n}", 1.4, y + 0.55, ["1", "2"], side="r")
    gnd(to(to(j["2"], 0.5, 0), 0, -0.4))
    hang(f"R{174 + n}", f"L_IN{n}", (5.0, y), 2.2)
    W(j["1"], N(f"R{174 + n}", f"L_IN{n}"))
    two(f"C{170 + n}", {f"L_IN{n}": (6.2, y), f"L_SEL{n}": (8.6, y)})
    W(N(f"R{174 + n}", f"L_IN{n}"), N(f"C{170 + n}", f"L_IN{n}"))
    hang(f"R{170 + n}", f"L_SEL{n}", (10.2, y), 2.2, side="l")
    W(N(f"C{170 + n}", f"L_SEL{n}"), N(f"R{170 + n}", f"L_SEL{n}"))
    kp = S.relay_pole(f"K{12 + n}", 1, (15.4, y - 0.5), rtl=True, note=f"IN{n}")
    W(N(f"R{170 + n}", f"L_SEL{n}"), kp["NO"])
    bn = node(f"alin_{n}", "AL_IN", (XBUS, y - 0.5))
    W(kp["COM"], bn)
    bus_in.append(bn)
chain(*bus_in)
ain = node("al_in_a", "AL_IN", (XBUS, YA))      # on the bus, between inputs 3 and 4
notes(1.2, 85.2, ["C171–C174 film; R171–R174 tengono a 0 V",
                  "il lato del preamp di ogni ingresso,",
                  "R175–R178 il jack vuoto (F1, PR-14)"])

# =============================================================================
# 2  BLOCK A, FIXED OUTPUTS, TRIM, VOLUME, BLOCK B, MAIN OUTPUT (left channel)
# =============================================================================
S.panel(21.0, 80.4, 86.0, 118.6, "2  Blocco A, uscite fisse, trim, volume, blocco B, uscita principale",
        "canale sinistro; i blocchi sono il riquadro 7, le loro sigle la tabella (riquadro 8)")
boxA = S.instance("AL", 22.8, YA + 2.4, 5.0, 4.8, {"IN": ("l", 2.4), "OUT": ("r", 2.4)},
                  title="blocco AL", sub=["guadagno 1", "R113 montata"])
W(ain, boxA["IN"])
AOUT = rete("AL_OUT")
aout = node("al_out_j", AOUT, (29.6, YA))
W(boxA["OUT"], aout)
# the fixed outputs: one buffer each (ADR-023), the mute changeover after the cap (ADR-044)
YF = {1: 110.0, 2: 103.6}
fins = []
for k, (riso, cap, rbc, rbl, jk, relay, name) in {
        1: ("R161", "C162", "R167", "R163", "J110", "K2", "SINGXER"),
        2: ("R164", "C165", "R168", "R166", "J111", "K3", "STAX")}.items():
    y = YF[k]
    tag = f"F{k}L"
    box = S.instance(tag, 31.2, y + 1.6, 5.0, 3.2, {"IN": ("l", 1.6), "OUT": ("r", 1.6)},
                     title=f"blocco {tag}", sub=["buffer, guadagno 1"])
    fin = node(f"f{k}_in", AOUT, (29.6, y))
    W(fin, box["IN"])
    fins.append(fin)
    two(riso, {f"{tag}_OUT": (37.8, y), f"L_FIX{k}": (40.2, y)})
    W(box["OUT"], N(riso, f"{tag}_OUT"))
    two(cap, {f"L_FIX{k}": (41.2, y), f"L_FIXC{k}": (43.6, y)})
    W(N(riso, f"L_FIX{k}"), N(cap, f"L_FIX{k}"))
    hang(rbc, f"L_FIXC{k}", (44.8, y), 2.2)
    W(N(cap, f"L_FIXC{k}"), N(rbc, f"L_FIXC{k}"))
    kp = S.relay_pole(relay, 1, (46.2, y), note="mute")
    W(N(rbc, f"L_FIXC{k}"), kp["COM"])
    ground_right(kp["NC"])
    jn = node(f"fixout_{k}", rete(f"L_FIXOUT{k}"), (49.8, y + 0.5))
    W(kp["NO"], jn)
    hang(rbl, rete(f"L_FIXOUT{k}"), (49.8, y + 0.5), 2.2)
    jj = S.conn(jk, 53.4, y + 1.05, ["1", "2"], side="l")
    W(jn, jj["1"])
    gnd(to(jj["2"], 0, -0.7))
chain(aout, fins[1], fins[0])
# the trim: the ladder and pole 1 of K7 / K8 (trim.py, ADR-027); K7 reset = 0 dB
two("R901", {AOUT: (31.6, YA), "L_TAP6": (31.6, YA - 2.4)}, side="l")
two("R902", {"L_TAP6": (31.6, YA - 2.4), "L_TAP12": (31.6, YA - 4.8)}, side="l")
hang("R903", "L_TAP12", (31.6, YA - 4.8), 2.2, side="l")
W(aout, N("R901", AOUT))
k8 = S.relay_pole("K8", 1, (37.2, YA - 3.6), rtl=True, flip=True, h=0.6, note="−12")
W(N("R902", "L_TAP6"), k8["NC"], first="h")
W(N("R903", "L_TAP12"), k8["NO"], first="h")
k7 = S.relay_pole("K7", 1, (42.4, YA - 0.6), rtl=True, flip=True, h=0.6, note="−6")
W(N("R901", AOUT), k7["NC"])
W(k8["COM"], k7["NO"], first="h")
two("C265", {"L_TRIM_OUT": (43.8, YA - 0.6), "L_ATT_TOP": (46.2, YA - 0.6)})
W(k7["COM"], N("C265", "L_TRIM_OUT"))
j120 = S.conn("J120", 48.6, YA - 0.05, ["1", "2", "3"], side="l")
W(N("C265", "L_ATT_TOP"), j120["1"])
gnd(j120["3"])
attw = node("attw", "L_ATT_W", (47.2, 89.0))
W(j120["2"], attw, (47.2, P(j120["2"])[1]))
hang("R265", "L_ATT_W", (45.6, 89.0), 2.2, side="l")
W(attw, N("R265", "L_ATT_W"))
boxB = S.instance("BL", 49.4, 91.4, 6.4, 5.6,
                  {"IN": ("l", 2.4), "OUT": ("r", 1.2), "RG": ("r", 3.2), "RG10": ("r", 4.6)},
                  title="blocco BL", sub=["0 / +3 / +10 dB"])
W(attw, boxB["IN"])
# the main output (ADR-044: 47 ohm, cap, bleeds on both sides, the mute changeover)
two("R261", {"BL_OUT": (57.6, 90.2), "L_MAIN_A": (60.0, 90.2)})
W(boxB["OUT"], N("R261", "BL_OUT"))
two("C262", {"L_MAIN_A": (61.0, 90.2), "L_MAINC": (63.4, 90.2)})
W(N("R261", "L_MAIN_A"), N("C262", "L_MAIN_A"))
hang("R264", "L_MAINC", (64.6, 90.2), 2.2)
W(N("C262", "L_MAINC"), N("R264", "L_MAINC"))
k4 = S.relay_pole("K4", 1, (66.0, 90.2), note="mute")
W(N("R264", "L_MAINC"), k4["COM"])
ground_right(k4["NC"])
mj = node("mainjack", "L_MAINJACK", (69.4, 90.7))
W(k4["NO"], mj)
hang("R263", "L_MAINJACK", (69.4, 90.7), 2.2)
j230 = S.conn("J230", 73.0, 91.25, ["1", "2"], side="l")
W(mj, j230["1"])
gnd(to(j230["2"], 0, -0.7))
# the gain legs of block B: pole 1 of K1 / K5 grounds R138 / R143 (ADR-026)
k1 = S.relay_pole("K1", 1, (57.8, 88.2), note="+3 dB")
W(boxB["RG"], k1["COM"])
ground_right(k1["NO"])
k5 = S.relay_pole("K5", 1, (57.8, 85.0), note="+10 dB")
W(boxB["RG10"], k5["COM"])
ground_right(k5["NO"])
notes(58.0, 116.8, [
    "Il canale destro è uguale e non è disegnato: le sue sigle sono quelle del sinistro",
    "+200 (R161 → R361, J101 → J301), il trim +10 (R901 → R911); le reti L_ → R_,",
    "AL_ → AR_, BL_ → BR_, F1L_ → F1R_, F2L_ → F2R_. I suoi blocchi: AR, BR, F1R, F2R.",
    "I poli dei relè comuni che portano il destro sono disegnati con le loro reti",
    "(riquadri 5, 6, 9, 10)."])
_al = sorted(F["aliases"].items())
notes(58.0, 113.4, ["Nella netlist un nodo unito prende uno solo dei suoi nomi:"]
      + [f"   {w} si chiama {g}" for w, g in _al], color=DIM)
notes(58.0, 113.4 - 0.62 * (len(_al) + 1) - 0.3, [
    "Alimentazione dei blocchi: VPLUS, VMINUS, GND, riquadro 7; J1, riquadro 6."])

# =============================================================================
# 5  SELECTOR: THE KNOB, THE COILS, THE RIGHT POLES (selector.py, ADR-064)
# =============================================================================
S.panel(86.0, 80.4, 118.0, 118.6, "5  Selettore: manopola, bobine, poli del destro",
        "una bobina accesa per volta, da VRELAY attraverso SW4")
sw4 = S.rotary_pole("SW4", 0, (90.2, 108.0), pitch=1.0, positions=["IN1", "IN2", "IN3", "IN4"])
lab(sw4["COM"], "left")
XC = {1: 114.6, 2: 108.2, 3: 101.8, 4: 95.4}       # throw 1 (top) to the farthest coil
for n in range(1, 5):
    x = XC[n]
    a1, a2 = S.relay_coil(f"K{12 + n}", (x, 104.0), (x, 101.6), note=f"SEL{n}", word="")
    W(sw4[n], a1, (x, P(sw4[n])[1]), first="h")
    ret(a2)
    two(f"D{15 + n}", {f"SEL{n}_HI": (x - 1.3, 104.0), "RLY_RET": (x - 1.3, 101.6)}, side="l",
        value="")
    W(a1, N(f"D{15 + n}", f"SEL{n}_HI"))
    ret(N(f"D{15 + n}", "RLY_RET"))
S.rotary_pole("SW4", 1, (90.2, 97.6), pitch=1.0)
S.rotary_pole("SW4", 2, (90.2, 91.8), pitch=1.0)
for n, y in zip(range(1, 5), (97.6, 94.0, 90.4, 86.8)):
    kp = S.relay_pole(f"K{12 + n}", 2, (101.4, y), note=f"IN{n} destro")
    lab(kp["COM"], "left")
    lab(kp["NO"], "right")
assert {S.comp[f"D{15 + n}"][0] for n in range(1, 5)} == {"1N4148"}
notes(86.6, 84.2, ["K13–K16: le bobine; D16–D19: 1N4148 su ciascuna",
                   "poli 1 di K13–K16 (canale sinistro): riquadro 1"])

# =============================================================================
# 6  MUTE, PERMISSIVE, CONNECTORS
# =============================================================================
S.panel(118.0, 80.4, 171.7, 118.6, "6  Mute, permesso, connettori",
        "le bobine fra VRELAY e i sink del temporizzatore (J4, scheda alimentatore); a riposo = muto")
YV = 114.6
X6 = {"K2": 122.0, "K3": 127.0, "K4": 133.0, "K6": 138.6}
NOTE6 = {"K2": "MUTE1", "K3": "IM06TS, + su 1", "K4": "MUTE3", "K6": "PERMIT"}
vr = [node("vr_0", "VRELAY", (121.6, YV))] + [node(f"vr_{r}", "VRELAY", (x, YV)) for r, x in X6.items()]
chain(*vr)
lab(vr[0], "left")
for r, x in X6.items():
    a1, a2 = S.relay_coil(r, (x, YV - 0.8), (x, YV - 3.2), note=NOTE6[r])
    W(f"vr_{r}", a1)
mc = [node(f"mc_{r}", "MUTE_CMD", (X6[r], YV - 4.2)) for r in ("K2", "K3", "K4")]
for r, n in zip(("K2", "K3", "K4"), mc):
    W(T(r, "8"), n)
chain(*mc)
lab(mc[1], "down")
lab(T("K6", "8"), "down")
# K6: VRELAY -> NC -> PERMIT_MID -> NC -> VTRIM, live while K6 is released (trim.py)
k61 = S.relay_pole("K6", 1, (122.0, 104.0), label="b")
lab(k61["COM"], "left")
lab(k61["NO"], "up")
k62 = S.relay_pole("K6", 2, (126.4, 103.5))
W(k61["NC"], k62["COM"])
vt = node("vtrim_6", "VTRIM", (130.2, 103.0))
W(k62["NC"], vt)
lab(to(vt, 0, 1.3), "up")
hang("D3", "VTRIM", (130.2, 103.0), 2.2, side="l")
two("R3", {"VTRIM": (131.4, 103.0), "MLED": (133.8, 103.0)})
W(vt, N("R3", "VTRIM"))
j7 = S.conn("J7", 136.0, 103.55, ["1", "2"], side="l", sub="LED rosso, mute")
W(N("R3", "MLED"), j7["1"])
ret(to(to(j7["2"], -0.6, 0), 0, -0.4))
notes(120.0, 98.6, ["K6 a riposo: VTRIM vivo (LED rosso, trim e guadagno",
                    "si muovono); VHOLD vivo con K6 eccitato (ADR-041, ADR-045)"])
# the timer's harness and the mute switch (ADR-045, F10)
j4 = S.conn("J4", 150.0, 112.0, ["1", "2", "3"], side="l", sub="al temporizzatore")
for p in ("1", "2", "3"):
    lab(j4[p], "left")
two("SW3", {"MUTE_SW": (143.0, 106.4), "RLY_RET": (145.4, 106.4)})
lab(N("SW3", "MUTE_SW"), "left")
ret(N("SW3", "RLY_RET"))
notes(140.2, 104.4, ["SW3 chiuso = musica: un filo rotto mette in mute"])
# J1, the supply, and J2, the relays' return
j1 = S.conn("J1", 166.4, 116.4, ["1", "2", "3", "4", "5", "6", "7"], side="l",
            sub="dall'alimentatore")
W(j1["1"], j1["2"])
lab(j1["1"], "left")
W(j1["3"], j1["4"])
lab(j1["3"], "left")
W(j1["5"], j1["6"])
lab(j1["5"], "left")
lab(j1["7"], "left")
j2 = S.conn("J2", 166.4, 107.0, ["1"], side="l", sub="ritorno dei relè")
ret(to(to(j2["1"], -1.6, 0), 0, -0.6))
# the right poles of the mute relays (ADR-044, the same changeover)
for r, y, what in (("K2", 101.0, "SINGXER destro"), ("K3", 96.0, "STAX destro"),
                   ("K4", 91.0, "MAIN destro")):
    kp = S.relay_pole(r, 2, (154.6, y), note=what)
    lab(kp["COM"], "left")
    lab(kp["NO"], "right")
    ground_right(kp["NC"])
notes(140.2, 86.2, ["poli 1 di K2–K4 (sinistro): riquadro 2. A riposo il lato",
                    "del condensatore va a massa e il jack resta isolato, tenuto",
                    "a 0 V dal suo bleed (ADR-044: «Il bleed basta»)"])

# =============================================================================
# 7a  THE GAIN BLOCK, ONCE: INPUT PAIR, MIRROR AND VAS, OUTPUT AND FEEDBACK
# =============================================================================
S.panel(0.8, 41.0, 88.0, 80.4, "7  Il blocco di guadagno, una volta (circuits/preamp/gain_block.net)",
        "le otto istanze della scheda sono questo blocco (ADR-006); le loro sigle e le parti non "
        "montate: tabella, riquadro 8. Le sigle qui sono quelle di gain_block.net")
# ---- the cascoded differential pair ---------------------------------------------
YD = 62.6
qa = S.trans(t("Q110"), "njf", "drain", (9.0, YD), rev=True, unit=1)
qb = S.trans(t("Q110"), "njf", "drain", (17.0, YD), unit=2, label_side="l")
S.nc_note(t("Q110"), ["3", "7"], (2.0, 76.4))
two(t("R111"), {b("S1"): P(qa["S"]), b("SRC"): (9.0, 59.2)})
two(t("R112"), {b("S2"): P(qb["S"]), b("SRC"): (17.0, 59.2)}, side="l")
two(t("R151"), {b("S2"): (19.2, P(qb["S"])[1]), b("SRC"): (19.2, 59.2)})
W(qb["S"], N(t("R151"), b("S2")))
q106 = S.trans(t("Q106"), "npn", "collector", (13.0, 57.0))
src = [node(f"src_{i}", b("SRC"), (x, 58.2)) for i, x in enumerate((9.0, 13.0, 17.0, 19.2))]
chain(*src)
W(N(t("R111"), b("SRC")), src[0])
W(q106["C"], src[1])
W(N(t("R112"), b("SRC")), src[2])
W(N(t("R151"), b("SRC")), src[3])
lab(q106["B"], "left")
two(t("R107"), {b("NTE"): P(q106["E"]), b("VMINUS"): (13.0, P(q106["E"])[1] - 2.4)})
rail(N(t("R107"), b("VMINUS")), up=False)
yg = P(qa["G"])[1]
two(t("R108"), {b("IN"): (4.8, yg), b("G1"): (7.2, yg)})
W(N(t("R108"), b("G1")), qa["G"])
hang(t("R113"), b("IN"), (3.4, yg), 2.4, side="l")
W(N(t("R113"), b("IN")), N(t("R108"), b("IN")))
lab(N(t("R113"), b("IN")), "up")
two(t("R109"), {b("G2"): (20.6, yg), b("FB"): (23.0, yg)})
two(t("R150"), {b("G2"): (20.6, yg + 1.8), b("FB"): (23.0, yg + 1.8)})
W(qb["G"], N(t("R109"), b("G2")))
W(N(t("R109"), b("G2")), N(t("R150"), b("G2")))
W(N(t("R109"), b("FB")), N(t("R150"), b("FB")))
lab(N(t("R109"), b("FB")), "right")
q117 = S.trans(t("Q117"), "npn", "emitter", (9.0, 64.4))
q118 = S.trans(t("Q118"), "npn", "emitter", (17.0, 64.4))
W(qa["D"], q117["E"])
W(qb["D"], q118["E"])
lab(q117["C"], "up")
lab(q118["C"], "up")
lab(q117["B"], "left")
lab(q118["B"], "left")
notes(1.6, 51.0, [f"R113 (R_IN, 1 MΩ): montata solo in {', '.join(ONLY['R_IN'])}",
                  "coppia JFET duale cascodata (ADR-013, ADR-014);",
                  "R150 e R151: la ridondanza di ADR-086"])
# ---- the mirror, the follower, the VAS (ADR-056, ADR-067, ADR-087) ----------------
YP = 76.5
vpf = [node(f"vpf_{i}", b("VPF"), (x, YP)) for i, x in enumerate((31.6, 33.6, 36.6, 39.6, 43.0))]
chain(*vpf)
lab(vpf[0], "left")
two(t("R119"), {b("VPF"): (33.6, YP), b("NME1"): (33.6, 74.1)}, side="l")
two(t("R120"), {b("VPF"): (39.6, YP), b("NME2"): (39.6, 74.1)})
ma = S.trans(t("Q121"), "pnp", "emitter", (33.6, 74.1), rev=True, unit=1, label_side="l",
             label_dy=-1.5)
mb_ = S.trans(t("Q121"), "pnp", "emitter", (39.6, 74.1), unit=2, label_dy=-1.5)
S.nc_note(t("Q121"), ["4", "5"], (2.0, 75.7))
W(ma["B"], mb_["B"])
two(t("R149"), {b("VPF"): (36.6, YP), b("NMIRI"): (36.6, 74.8)})
mbus = node("mirror_bus", b("NMIRI"), (36.6, P(ma["B"])[1]))
W(N(t("R149"), b("NMIRI")), mbus)
q148 = S.trans(t("Q148"), "pnp", "emitter", (36.6, 72.4), note="aiuto")
W(mbus, q148["E"])
rail(to(q148["C"], 0, -0.3), up=False)
nmirc = node("nmirc_h", b("NMIRC"), (33.6, P(q148["B"])[1]))
W(ma["C"], nmirc)
W(nmirc, q148["B"])
lab(to(nmirc, 0, -1.4), "down")
nhi = node("nhi_h", b("NHI"), (41.4, P(mb_["C"])[1]))
W(mb_["C"], nhi)
q146 = S.trans(t("Q146"), "pnp", "base", (42.4, P(mb_["C"])[1]), note="inseguitore")
W(nhi, q146["B"])
lab(nhi, "up")
two(t("R147"), {b("VPF"): (43.0, YP), b("NVB"): (43.0, 74.9)}, side="r")
W(N(t("R147"), b("NVB")), q146["E"])
# ADR-097: R153 + R160 in series, NFC -> NFCR -> V-
_, nfcr = hang(t("R153"), b("NFC"), P(q146["C"]), 1.3)
hang(t("R160"), b("NFCR"), P(nfcr), 1.3, sym=lambda n: rail(n, up=False))
nvb = node("nvb_j", b("NVB"), (43.0, 73.9))
q122 = S.trans(t("Q122"), "pnp", "base", (47.0, 73.9), note="VAS")
W(nvb, q122["B"])
two(t("R123"), {b("VPF"): (P(q122["E"])[0], YP), b("NVE"): P(q122["E"])})
W(vpf[-1], N(t("R123"), b("VPF")))             # the bus ends on R123, wherever Q122 puts it
nx2 = node("nx_vas", b("NX"), (47.6, 71.0))
W(q122["C"], nx2)
two(t("C124"), {b("NX"): (51.6, 71.0), b("NHI"): (51.6, 68.6)})
W(nx2, N(t("C124"), b("NX")))
lab(N(t("C124"), b("NHI")), "down")
lab(to(N(t("C124"), b("NX")), 1.6, 0), "right")
q125 = S.trans(t("Q125"), "npn", "collector", (47.6, 63.0), note="carico del VAS")
lab(to(q125["C"], 0, 0.8), "right")
lab(q125["B"], "left")
hang(t("R126"), b("NVLE"), P(q125["E"]), 2.2, sym=lambda n: rail(n, up=False))
notes(31.0, 51.0, ["specchio LS352 appaiato, aiuto Q148 (ADR-067); inseguitore",
                   "Q146 con R153 + R160 sul collettore (ADR-087, ADR-097); VAS Q122 compensato",
                   "a Miller da C124; specchio e VAS su VPF (ADR-056)"])
# ---- the Vbe multiplier, the output pair, the feedback ---------------------------
YX, YY = 72.4, 50.0
nx = [node(f"nx_{i}", b("NX"), (x, YX)) for i, x in enumerate((59.8, 63.0, 66.0, 69.0))]
ny = [node(f"ny_{i}", b("NY"), (x, YY)) for i, x in enumerate((59.8, 63.0, 66.0, 69.0))]
lab(nx[0], "left")
lab(ny[0], "left")
q127 = S.trans(t("Q127"), "npn", "collector", (63.0, 62.0), rev=True, label_side="l",
               note="moltiplicatore")
W(nx[1], q127["C"])
W(q127["E"], ny[1])
two(t("R128"), {b("NX"): (66.0, 64.6), b("NBB"): (66.0, P(q127["B"])[1])})
two(t("R129"), {b("NBB"): (66.0, P(q127["B"])[1]), b("NY"): (66.0, 58.4)})
W(q127["B"], N(t("R128"), b("NBB")))
W(nx[2], N(t("R128"), b("NX")))
W(N(t("R129"), b("NY")), ny[2])
for r, (a, c) in zip(("D154", "D155", "D156", "D157"),
                     (("NX", "NXD1"), ("NXD1", "NXD2"), ("NXD2", "NXD3"), ("NXD3", "NY"))):
    y0 = {"NX": 68.8, "NXD1": 66.4, "NXD2": 64.0, "NXD3": 61.6}[a]
    two(t(r), {b(a): (69.0, y0), b(c): (69.0, y0 - 2.4)})
W(nx[3], N(t("D154"), b("NX")))
W(N(t("D157"), b("NY")), ny[3])
two(t("R130"), {b("NX"): (72.0, YX), b("NBN"): (74.4, YX)})
two(t("R131"), {b("NY"): (72.0, YY), b("NBP"): (74.4, YY)}, side="b")
chain(*nx, N(t("R130"), b("NX")))
chain(*ny, N(t("R131"), b("NY")))
q132 = S.trans(t("Q132"), "npn", "base", (76.4, YX))
q133 = S.trans(t("Q133"), "pnp", "base", (76.4, YY))
two(t("D158"), {b("NBN"): (75.4, YX), b("NEN"): (75.4, 70.0)}, side="l")
two(t("D159"), {b("NBP"): (75.4, YY), b("NEP"): (75.4, 52.4)}, side="l")
chain(N(t("R130"), b("NBN")), N(t("D158"), b("NBN")), q132["B"])
chain(N(t("R131"), b("NBP")), N(t("D159"), b("NBP")), q133["B"])
rail(to(q132["C"], 0, 1.2))
rail(to(q133["C"], 0, -1.2), up=False)
two(t("R134"), {b("NEN"): (77.0, 70.0), b("OUT"): (77.0, 67.0)})
two(t("R135"), {b("NEP"): (77.0, 52.4), b("OUT"): (77.0, 55.4)})
W(q132["E"], N(t("R134"), b("NEN")))
W(N(t("D158"), b("NEN")), N(t("R134"), b("NEN")))
W(q133["E"], N(t("R135"), b("NEP")))
W(N(t("D159"), b("NEP")), N(t("R135"), b("NEP")))
out = node("out_j", b("OUT"), (77.0, 61.2))
W(N(t("R134"), b("OUT")), out)
W(out, N(t("R135"), b("OUT")))
two(t("R136"), {b("OUT"): (80.0, 61.2), b("FB"): (80.0, 58.2)})
two(t("C137"), {b("OUT"): (82.6, 61.2), b("FB"): (82.6, 58.2)})
chain(out, N(t("R136"), b("OUT")), N(t("C137"), b("OUT")))
lab(to(N(t("C137"), b("OUT")), 1.2, 0), "right")
two(t("R138"), {b("FB"): (80.0, 58.2), b("RG"): (80.0, 55.2)})
two(t("R143"), {b("FB"): (85.2, 58.2), b("RG10"): (85.2, 55.2)})
chain(N(t("R136"), b("FB")), N(t("C137"), b("FB")), N(t("R143"), b("FB")))
lab(N(t("R138"), b("RG")), "down")
lab(N(t("R143"), b("RG10")), "down")
lab(to(N(t("R136"), b("FB")), -1.0, 0), "left")
notes(58.6, 46.2, [f"R138 (R_g, +3 dB) e R143 (R_g10, +10 dB): montate solo in "
                   f"{', '.join(ONLY['R_g'])}; K1 / K5",
                   "le mettono a massa (riquadro 2). R136 resta fissa fra OUT e FB: l'anello",
                   "non si apre mai (ADR-004, ADR-026); D158 / D159 di ADR-095"])

# =============================================================================
# 7b  THE GAIN BLOCK: BIAS REFERENCES AND DECOUPLING
# =============================================================================
S.panel(0.8, 0.8, 58.0, 41.0, "7  (segue) Il blocco: riferimenti e disaccoppiamento",
        "ogni rete nominata sopra è generata qui, una volta sola")
YT = 34.6
gr = node("gnd_r101", b("GND"), (2.4, YT + 2.4))
two(t("R101"), {b("GND"): (4.0, YT + 2.4), b("NREF"): (4.0, YT)})
W(N(t("R101"), b("GND")), gr)
gnd(gr)
two(t("D102"), {b("NREF"): (4.0, YT), b("NREFM"): (4.0, YT - 2.4)})
two(t("D103"), {b("NREFM"): (4.0, YT - 2.4), b("VMINUS"): (4.0, YT - 4.8)})
two(t("C104"), {b("NREF"): (7.6, YT), b("VMINUS"): (7.6, YT - 4.8)})
two(t("C105"), {b("NREF"): (10.6, YT), b("VMINUS"): (10.6, YT - 4.8)})
chain(N(t("R101"), b("NREF")), N(t("C104"), b("NREF")), N(t("C105"), b("NREF")))
lab(to(N(t("C105"), b("NREF")), 1.4, 0), "right")
chain(N(t("D103"), b("VMINUS")), N(t("C104"), b("VMINUS")), N(t("C105"), b("VMINUS")))
rail(to(N(t("C105"), b("VMINUS")), 1.4, 0), up=False)
two(t("R114"), {b("VPLUS"): (19.0, YT + 2.4), b("NCASC"): (19.0, YT)})
rail(N(t("R114"), b("VPLUS")))
hang(t("R115"), b("NCASC"), (19.0, YT), 2.4)
hang(t("C116"), b("NCASC"), (22.0, YT), 2.4)
W(N(t("R114"), b("NCASC")), N(t("C116"), b("NCASC")))
lab(to(N(t("C116"), b("NCASC")), 1.4, 0), "right")
# local decoupling of the rails, a ground bus between the two rows
YG = 34.2
vp_d = [node(f"vpd_{i}", b("VPLUS"), (x, YT + 2.4)) for i, x in enumerate((30.0, 33.0))]
vm_d = [node(f"vmd_{i}", b("VMINUS"), (x, YG - 3.6)) for i, x in enumerate((30.0, 33.0))]
for r, x, top in (("C139", 30.0, True), ("C141", 33.0, True), ("C140", 30.0, False),
                  ("C142", 33.0, False)):
    other = [n for n in nets(t(r)) if n != b("GND")][0]
    if top:
        two(t(r), {other: (x, YT + 2.4), b("GND"): (x, YG)}, side="l" if x < 31 else "r")
    else:
        two(t(r), {b("GND"): (x, YG), other: (x, YG - 3.6)}, side="l" if x < 31 else "r")
assert {nets(t(r))[0] if nets(t(r))[0] != b("GND") else nets(t(r))[1]
        for r in ("C139", "C141")} == {b("VPLUS")}, "C139 / C141 non sono su VPLUS"
chain(*vp_d)
chain(*vm_d)
rail(vp_d[0])
rail(vm_d[0], up=False)
gb = node("gnd_dec", b("GND"), (35.0, YG))
W(node("gnd_dec0", b("GND"), (30.0, YG)), gb)
gnd(gb)
# VPF, the filtered V+ of the mirror and the VAS (ADR-056, ADR-086)
two(t("R144"), {b("VPLUS"): (42.0, YT + 2.4), b("VPF"): (42.0, YT)})
two(t("R152"), {b("VPLUS"): (44.6, YT + 2.4), b("VPF"): (44.6, YT)})
hang(t("C145"), b("VPF"), (47.6, YT), 2.4)
chain(N(t("R144"), b("VPLUS")), N(t("R152"), b("VPLUS")))
rail(N(t("R144"), b("VPLUS")))
chain(N(t("R144"), b("VPF")), N(t("R152"), b("VPF")), N(t("C145"), b("VPF")))
lab(to(N(t("C145"), b("VPF")), 1.4, 0), "right")
notes(1.6, 24.0, [
    "NREF: due 1N4148 sopra VMINUS, bypass verso VMINUS e non verso massa (PSRR): basi di Q106 e Q125.",
    "NCASC: il partitore R114 / R115 da VPLUS, basi dei cascode Q117 e Q118.",
    "VPF: R144 ∥ R152 + C145, il V+ filtrato di specchio e VAS (ADR-056, ADR-086).",
    "Ogni istanza ha i suoi: C139–C142 disaccoppiano i rail sul blocco.",
    "VPLUS, VMINUS e GND sono i rail della scheda (J1, riquadro 6): uguali in tutte le istanze."])

# =============================================================================
# 8  THE TABLE OF THE EIGHT INSTANCES
# =============================================================================
S.panel(58.0, 0.8, 88.0, 41.0, "8  Le otto istanze del blocco",
        "dalla numerazione di gain_block() e dalla netlist (Sheet.fold)")
yend = S.instance_table(58.6, 38.6, ["AL", "BL", "F1L", "F2L", "AR", "BR", "F1R", "F2R"],
                        colw=2.6, refw=2.6, row=0.47)
ndiff = sum(len(v) for v in F["diffs"].values())
notes(58.6, yend - 0.2, [
    "— = non montata in quell'istanza; valori diversi dal blocco: "
    + ("nessuno" if ndiff == 0 else f"{ndiff}, nelle celle")], step=0.55)

# =============================================================================
# 9  GAIN: THE KNOB, THE RELAYS, THE SELF-HOLD, THE LEDS (gain_interlock.py)
# =============================================================================
S.panel(88.0, 0.8, 130.0, 80.4, "9  Guadagno: manopola, relè, autoritenuta, LED",
        "K1 a massa R138 di BL e BR (+3 dB), K5 R143 (+10 dB); si muove solo in mute (ADR-041)")
XS = 92.4
POS = ["0 dB", "+3", "+10"]
sa = S.rotary_pole("SW2", 0, (XS, 75.0), pitch=1.0, positions=POS)
sb = S.rotary_pole("SW2", 1, (XS, 69.0), pitch=1.0, positions=POS)
sc = S.rotary_pole("SW2", 2, (XS, 59.0), pitch=1.0, positions=POS)
sd = S.rotary_pole("SW2", 3, (XS, 52.0), pitch=1.0, positions=POS)
for s in (sa, sb, sc, sd):
    lab(s["COM"], "left")
W(sa[2], sa[3])
W(sb[2], sb[3])
two("D10", {"C3": (96.2, 74.0), "G3_HI": (98.6, 74.0)})
W(sa[3], N("D10", "C3"))
two("D11", {"C10": (96.2, 58.0), "G10_HI": (98.6, 58.0)})
W(sc[3], N("D11", "C10"))
for hi, top, refs, dfw, ycom, pole, hnet, sw, hthrow in (
        ("G3_HI", 73.2, ("K1", "K11"), "D14", 67.4, "K11", "H3", sb, 2),
        ("G10_HI", 56.8, ("K5", "K12"), "D15", 50.4, "K12", "H10", sd, 3)):
    d_in = "D10" if hi == "G3_HI" else "D11"
    g = node(f"{hi}_j", hi, (100.0, top))
    W(N(d_in, hi), g, (100.0, P(N(d_in, hi))[1]))
    gh = node(f"{hi}_h", hi, (101.0, top))
    coil_tops = []
    for r, x in zip(refs, (102.4, 107.4)):
        a1, a2 = S.relay_coil(r, (x, top), (x, top - 2.4),
                              note={"K1": "GAIN", "K11": "HOLD3", "K5": "GAIN10", "K12": "HOLD10"}[r])
        ret(a2)
        coil_tops.append(a1)
    two(dfw, {hi: (112.4, top), "RLY_RET": (112.4, top - 2.4)})
    ret(N(dfw, "RLY_RET"))
    chain(g, gh, coil_tops[0], coil_tops[1], N(dfw, hi))
    # the self-hold: H -> NO of the auxiliary -> the coils (ADR-041)
    kh = S.relay_pole(pole, 1, (98.8, ycom), label="b")
    hn = node(f"{hnet}_j", hnet, (96.8, ycom))
    W(sw[hthrow], hn, (96.8, P(sw[hthrow])[1]))
    W(hn, kh["COM"])
    W(kh["NO"], gh)
    dh = "D12" if hnet == "H3" else "D13"
    two(dh, {"VHOLD": (96.8, ycom - 3.0), hnet: (96.8, ycom - 0.6)}, side="r")
    W(hn, N(dh, hnet))
    lab(N(dh, "VHOLD"), "down")
# the LEDs of the true gain state: pole 2 of K11 / K12, R2 from VRELAY
two("R2", {"VRELAY": (112.6, 66.0), "GLED_FEED": (115.0, 66.0)}, side="b")
rail(N("R2", "VRELAY"))
k112 = S.relay_pole("K11", 2, (116.0, 66.0), note="LED")
W(N("R2", "GLED_FEED"), k112["COM"])
k122 = S.relay_pole("K12", 2, (120.0, P(k112["NO"])[1]), note="LED")
W(k112["NO"], k122["COM"])
lab(k112["NC"], "down")
lab(k122["NC"], "down")
j6 = S.conn("J6", 127.6, 70.0, ["1", "2", "3", "4"], side="l", sub="LED")
for p in ("1", "2"):
    lab(j6[p], "left")
W(k122["NO"], j6["3"], (124.8, P(k122["NO"])[1]), (124.8, P(j6["3"])[1]))
ret(to(to(j6["4"], -0.8, 0), 0, -0.4))
# the right poles of K1 / K5 (block BR)
for r, y in (("K1", 50.0), ("K5", 46.0)):
    kp = S.relay_pole(r, 2, (120.0, y), note="BR")
    lab(kp["COM"], "left")
    ground_right(kp["NO"])
notes(89.0, 40.0, [
    "SW2 a: VTRIM → C3 / C10 → D10 / D11: il comando, solo con K6 a riposo (mute).",
    "SW2 b, d: VRELAY → H3 / H10 → NO di K11 / K12: il ponte che tiene il guadagno",
    "quando K6 si eccita; D12 / D13 da VHOLD, l'autoritenuta fuori dal mute.",
    "D14 / D15: le bobine di K1 + K11 e K5 + K12, in parallelo.",
    "K11 / K12 poli 2: i LED del guadagno vero (J6), non del comando."])

# =============================================================================
# 10  TRIM: THE KNOB, THE BISTABLE RELAYS, THE LEDS (trim.py, ADR-027)
# =============================================================================
S.panel(130.0, 0.8, 171.7, 80.4, "10  Trim: manopola, relè bistabili, LED",
        "SW1 a ponte H sulle bobine; i bistabili tengono lo stato a bobine spente")
XT = 134.6
TPOS = ["0 dB", "−6", "−12"]
t1 = S.rotary_pole("SW1", 0, (XT, 74.0), pitch=1.0, positions=TPOS)
t2 = S.rotary_pole("SW1", 1, (XT, 68.0), pitch=1.0, positions=TPOS)
t3 = S.rotary_pole("SW1", 2, (XT, 62.0), pitch=1.0, positions=TPOS)
t4 = S.rotary_pole("SW1", 3, (XT, 56.0), pitch=1.0, positions=TPOS)
for s in (t1, t2, t3, t4):
    lab(s["COM"], "left")
    nets_here = {}
    for i in (1, 2, 3):
        nets_here.setdefault(S.net[s[i]], []).append(s[i])
    for net, ns in nets_here.items():
        chain(*ns)
        if net == "RLY_RET":
            ret_right(ns[0], 0.6)
        else:
            lab(to(ns[0], 0.6, 0), "right")
for r_a, r_b, dv, net1, net8, y in (("K7", "K9", "D1", "TRIM1_C1", "TRIM1_C8", 74.0),
                                     ("K8", "K10", "D2", "TRIM2_C1", "TRIM2_C8", 62.0)):
    tops, bots = [], []
    for r, x in ((r_a, 146.0), (r_b, 151.0)):
        a1, a2 = S.relay_coil(r, (x, y), (x, y - 2.4),
                              note={"K7": "TRIM1", "K9": "SPIA1", "K8": "TRIM2", "K10": "SPIA2"}[r])
        tops.append(a1)
        bots.append(a2)
    two(dv, {net1: (156.0, y), net8: (156.0, y - 2.4)})
    lt = node(f"{net1}_l", net1, (144.2, y))
    lb = node(f"{net8}_l", net8, (144.2, y - 2.4))
    chain(lt, *tops, N(dv, net1))
    chain(lb, *bots, N(dv, net8))
    lab(lt, "left")
    lab(lb, "left")
# the LEDs of the trim: pole 1 of K9 / K10, R1 from VRELAY
two("R1", {"VRELAY": (141.6, 49.6), "LED_FEED": (144.0, 49.6)}, side="b")
rail(N("R1", "VRELAY"))
k91 = S.relay_pole("K9", 1, (146.0, 49.6), note="LED")
W(N("R1", "LED_FEED"), k91["COM"])
k101 = S.relay_pole("K10", 1, (150.2, P(k91["NO"])[1]), note="LED")
W(k91["NO"], k101["COM"])
lab(k91["NC"], "down")
lab(k101["NC"], "down")
lab(k101["NO"], "right")
j5 = S.conn("J5", 160.0, 52.0, ["1", "2", "3", "4"], side="l", sub="LED")
for p in ("1", "2", "3"):
    lab(j5[p], "left")
ret(to(to(j5["4"], -0.8, 0), 0, -0.4))
S.relay_pole("K9", 2, (146.0, 43.0), note="libero")
S.relay_pole("K10", 2, (150.2, 43.0), note="libero")
# the right poles of K7 / K8: the trim of the right channel
k72 = S.relay_pole("K7", 2, (140.0, 36.0), flip=True, h=0.6, note="destro")
k82 = S.relay_pole("K8", 2, (152.0, 36.0), flip=True, h=0.6, note="destro")
for kp in (k72, k82):
    lab(kp["COM"], "left")
    lab(kp["NO"], "right")
    lab(kp["NC"], "right")
notes(131.0, 28.0, [
    "0 dB: K7 in reset (AL_OUT diretta); −6: K7 set, K8 reset (L_TAP6);",
    "−12: K7 e K8 set (L_TAP12). K9 / K10 sono i gemelli dei LED: stesse",
    "bobine, il polo 1 accende il LED della posizione vera (J5).",
    "D1 / D2: le TVS sulle bobine. VTRIM c'è solo in mute (riquadro 6):",
    "fuori dal mute il trim non si può muovere (F8, F9)."])

# =============================================================================
# the legend
# =============================================================================
S.text((89.0, 20.0), "Legenda", size=FS + 0.5, halign="left")
S.d.add(__import__("schemdraw").elements.Ground(lead=False).theta(0).at((90.0, 18.8))
        .color(GNDCOL).scale(0.85))
S.text((91.0, 18.6), "GND — la massa audio (J1)", halign="left")
S.d.add(__import__("schemdraw").elements.GroundSignal(lead=False).theta(0).at((90.0, 17.2))
        .color(RETCOL).scale(0.85))
S.text((91.0, 17.0), "RLY_RET — il ritorno delle bobine e dei LED (J2); tocca GND solo sull'alimentatore",
       halign="left")
S.text((90.0, 15.4), "NOME", color=NETCOL)
S.text((91.4, 15.4), "una rete per nome: la stessa scritta in due punti è un filo", halign="left")
S.text((89.4, 14.0), "×  contatto o piedino libero (nessuna rete nella netlist)", halign="left")
S.text((89.4, 12.8), "relè disegnati a riposo; i bistabili in reset (R), S = set", halign="left")
S.text((89.4, 11.6), "i punti di giunzione li mette il disegno dove si incontrano tre fili",
       halign="left", color=DIM, size=FS - 0.8)

# =============================================================================
try:
    stats = S.finish(SVG, PDF, MANIFEST, png=os.environ.get("PREVIEW_PNG"),
                     png_dpi=int(os.environ.get("PREVIEW_DPI", "150")))
except AssertionError as e:
    if os.environ.get("PREVIEW_PNG"):           # the picture, to see what is wrong
        S.d.save(os.environ["PREVIEW_PNG"], dpi=int(os.environ.get("PREVIEW_DPI", "150")))
    raise
print(f"SVG      -> {SVG}")
print(f"PDF      -> {PDF}")
print(f"manifest -> {MANIFEST}")
print(f"parti disegnate: {stats['parts']} (blocco {len(F['tparts'])}, scheda "
      f"{stats['parts'] - len(F['tparts'])}); espanse: {len(F['expanded'])}; "
      f"terminali: {stats['terminals']}   piedini liberi segnati: {stats['nc']}")
print(f"reti: {stats['nets']}   isole: {stats['islands']}   nomi: {stats['named']}   "
      f"giunzioni: {stats['dots']}")
print("testi: nessuno sopra un altro, un filo o una parte")
