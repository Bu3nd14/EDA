#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sheet_kit.py - the kit for a COMPLETE schematic page drawn from a KiCad netlist (L63).

DERIVED DOCUMENTATION, NOT A SOURCE OF TRUTH. The topology lives in
circuits/preamp/*.py; a page made with this kit only draws it.

gain_block_draw.py (L4) draws 61 devices from a SPICE include, with the nets
transcribed by hand and checked by scripts/check_schematic.py. A board page has
two to ten times the parts, integrated circuits with twenty pins, connectors and
relays: hand transcription would only add a place to be wrong. So here the nets
are READ from the netlist, and the guarantee moves to what the DRAWING does with
them. Each of these refuses, it does not warn:

  1. wire() joins two nodes only if the netlist puts them on the same net. A
     terminal's net comes from the netlist, never from the call site.
  2. Two nodes of different nets on the same point, a node of one net on a wire
     of another, two wires of different nets on top of each other: a short in
     the picture, an error here. Wires of different nets may only CROSS.
  3. ISLANDS. The drawn wires split each net into islands. A net drawn as one
     island needs no name; a net drawn as several needs a name - a label, a
     ground or a rail symbol - on EVERY island, or the reader cannot see that
     they are one. Two same-net wires crossing without a junction are refused
     too: the reader would take them for two nets.
  4. COVERAGE. Every part of the netlist is drawn, every pin the netlist
     connects is a terminal of the drawing, and every pin of an integrated
     circuit's symbol is either one of those or drawn as not connected.

The manifest is then emitted FROM THE DRAWING - each terminal with the name of
its island - and scripts/check_schematic.py compares it to the netlist in both
directions (block 2d of run_tests.sh), as it does for the gain block.

Junction dots are placed by the kit, wherever three or more wire ends of the same
net meet: the caller cannot forget one or put one where nothing joins.

Pin names come from the KiCad symbol libraries (the netlist SKiDL writes has no
libparts section); a symbol that `extends` another is followed. The project's own
parts (lib "preamp": LSK489, LS352) come from library/preamp.kicad_sym (L63b).

A FOLDED PAGE (L63b, the audio board: «Blocco una volta, un canale»). Eight
instances of one gain block and two equal channels would make a page of repeats.
So a page may draw:
  - a TEMPLATE once - a second netlist (circuits/preamp/gain_block.net), its refs
    and nets under a namespace ("BLK:R108"), printed without it - and a box for
    each instance it stands for;
  - the LEFT channel only, the right one given by a rule (refs and net prefixes).
Sheet.fold() DERIVES the table template -> instance from the numbering of
gain_block() and the instance's part count, and asserts it on the netlist: one
solution only, same part and value on every row, every template net landing on
one net of the instance. finish() then EXPANDS the drawing - the template into
its eight instances through the table, the left channel into the right through
the rule - so the manifest names all the parts of the board and
scripts/check_schematic.py compares it to the netlist as it does for a flat
page. Coverage becomes "every part either drawn or expanded, exactly once".
"""
import itertools
import json
import math
import os
import re

import matplotlib
matplotlib.use("Agg")
import schemdraw                      # noqa: E402
import schemdraw.elements as elm      # noqa: E402

SYMBOLS = "/Users/roberto/Applications/KiCad.app/Contents/SharedSupport/symbols"
# the project's own symbols (lib "preamp"), next to the sources in the repo
LIBRARY = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))), "library")

INK = "#111111"
DIM = "#5a5a5a"
NETCOL = "#1f4e9c"      # net labels
GNDCOL = "#1f6b2c"      # GND, the audio ground
RETCOL = "#9a4b00"      # RLY_RET, the return of the relay and logic currents
FRAME = "#9a9a9a"

A3_W_IN, A3_H_IN = 420 / 25.4, 297 / 25.4

EPS = 1e-6


# =============================================================================
# reading the netlist and the symbols
# =============================================================================
def read_kicad_net(path):
    """{ref: (value, lib, part)} and {(ref, pin): net} from a KiCad netlist.

    The same expressions psu_blocks_draw.py has used since L42b."""
    src = open(path, encoding="utf-8").read()
    comp = {}
    for m in re.finditer(r'\(comp\b.*?\(ref "([^"]+)"\).*?\(value "([^"]*)"\)'
                         r'.*?\(libsource\s*\(lib "([^"]*)"\)\s*\(part "([^"]*)"\)',
                         src, re.S):
        comp[m.group(1)] = (m.group(2), m.group(3), m.group(4))
    pin = {}
    for chunk in re.split(r"\(net\s*\(code", src.split("(nets", 1)[-1])[1:]:
        nm = re.search(r'\(name "([^"]*)"\)', chunk)
        if not nm:
            continue
        for r, p in re.findall(r'\(ref "([^"]+)"\)\s*\(pin "([^"]+)"\)', chunk):
            pin[(r, p)] = nm.group(1)
    return comp, pin


def _symbol_block(text, name):
    i = text.find(f'(symbol "{name}"')
    if i < 0:
        return None
    depth = 0
    for j in range(i, len(text)):
        if text[j] == "(":
            depth += 1
        elif text[j] == ")":
            depth -= 1
            if depth == 0:
                return text[i:j + 1]
    return None


_SYM_CACHE = {}


def symbol_pins(lib, part):
    """{pin number: pin name} of a KiCad library symbol, following `extends`."""
    key = (lib, part)
    if key in _SYM_CACHE:
        return _SYM_CACHE[key]
    path = os.path.join(SYMBOLS, lib + ".kicad_sym")
    if not os.path.exists(path):
        path = os.path.join(LIBRARY, lib + ".kicad_sym")
    text = open(path, encoding="utf-8").read()
    blk = _symbol_block(text, part)
    assert blk is not None, f"simbolo {lib}:{part} assente da {path}"
    ext = re.search(r'\(extends "([^"]+)"\)', blk)
    if ext:
        out = symbol_pins(lib, ext.group(1))
    else:
        out = {}
        for m in re.finditer(r'\(pin \w+ \w+.*?\(name "([^"]*)".*?\(number "([^"]*)"',
                             blk, re.S):
            out[m.group(2)] = m.group(1)
    _SYM_CACHE[key] = out
    return out


# =============================================================================
# values as a person reads them
# =============================================================================
def _num(s):
    m = re.fullmatch(r"([0-9.]+)\s*([pnumkM]?)", s)
    return (float(m.group(1)), m.group(2)) if m else None


def _it(x):
    s = f"{x:g}"
    return s.replace(".", ",")


def value_text(value, part):
    """'44.2k' -> '44,2 kΩ', '2200u' -> '2200 µF', '24V' -> '24 V'; else verbatim."""
    if part == "R":
        n = _num(value)
        if n:
            return f"{_it(n[0])} {n[1]}Ω".replace("u", "µ")
    if part in ("C", "C_Polarized"):
        n = _num(value)
        if n:
            return f"{_it(n[0])} {n[1].replace('u', 'µ')}F"
    m = re.fullmatch(r"([0-9.]+)V", value)
    if m:
        return f"{_it(float(m.group(1)))} V"
    return value


# =============================================================================
# geometry
# =============================================================================
def _p(xy):
    return (round(float(xy[0]), 6), round(float(xy[1]), 6))


def _on_interior(pt, seg):
    """pt strictly inside the axis-aligned segment seg (not at its ends)."""
    (x0, y0), (x1, y1) = seg
    x, y = pt
    if abs(x0 - x1) < EPS:                       # vertical
        return abs(x - x0) < EPS and min(y0, y1) + EPS < y < max(y0, y1) - EPS
    if abs(y0 - y1) < EPS:                       # horizontal
        return abs(y - y0) < EPS and min(x0, x1) + EPS < x < max(x0, x1) - EPS
    return False


def _overlap(s, t):
    """Two collinear axis-aligned segments sharing more than a point."""
    (a0, a1), (b0, b1) = s, t
    if abs(a0[0] - a1[0]) < EPS and abs(b0[0] - b1[0]) < EPS and abs(a0[0] - b0[0]) < EPS:
        lo = max(min(a0[1], a1[1]), min(b0[1], b1[1]))
        hi = min(max(a0[1], a1[1]), max(b0[1], b1[1]))
        return hi - lo > EPS
    if abs(a0[1] - a1[1]) < EPS and abs(b0[1] - b1[1]) < EPS and abs(a0[1] - b0[1]) < EPS:
        lo = max(min(a0[0], a1[0]), min(b0[0], b1[0]))
        hi = min(max(a0[0], a1[0]), max(b0[0], b1[0]))
        return hi - lo > EPS
    return False


def _cross(s, t):
    """Interior crossing of a horizontal and a vertical segment."""
    for h, v in ((s, t), (t, s)):
        (h0, h1), (v0, v1) = h, v
        if abs(h0[1] - h1[1]) < EPS and abs(v0[0] - v1[0]) < EPS:
            x, y = v0[0], h0[1]
            if (min(h0[0], h1[0]) + EPS < x < max(h0[0], h1[0]) - EPS
                    and min(v0[1], v1[1]) + EPS < y < max(v0[1], v1[1]) - EPS):
                return (x, y)
    return None


# =============================================================================
# the sheet
# =============================================================================
class Sheet:
    """One page. Coordinates in schemdraw units, y upwards, (0, 0) the page's
    lower left corner; `width` units span the A3 width (landscape)."""

    def __init__(self, netlist, source_rel, width=122.0, page=(A3_W_IN, A3_H_IN),
                 fontsize=5.0, lw=0.7):
        self.comp, self.pin = read_kicad_net(netlist)
        self.source_rel = source_rel
        self.W = float(width)
        self.H = self.W * page[1] / page[0]
        self.ipu = page[0] / self.W
        schemdraw.config(inches_per_unit=self.ipu, fontsize=fontsize, lw=lw,
                         margin=0, unit=2)
        self.d = schemdraw.Drawing(show=False)
        self.fs = fontsize
        self.nets = set(self.pin.values())
        self.xy = {}            # node -> point
        self.net = {}           # node -> net
        self.terminals = {}     # (ref, pin) -> node
        self.touched = set()
        self.parent = {}        # union-find over nodes
        self.named = {}         # node -> the name a label / symbol gives it
        self.segs = []          # (p, q, net)
        self.placed = set()
        self.nc = set()         # (ref, pin) drawn as not connected
        self.ic_refs = {}       # ref -> pins the symbol declares
        self.texts = []
        self.bodies = []        # (kind, geometry, ref): what a wire may not run through
        self.sym_refs = set()   # refs whose every symbol pin must be a terminal or nc
        self.marks = []         # (rect, what): ground / return / rail symbols, for texts
        self.tmpl = None        # the template netlist of a folded page (L63b)
        self.folded = None      # what Sheet.fold() derived
        self.boxes = {}         # tag -> {port: node}: the instance boxes
        for name in list(self.comp) + list(self.nets):
            assert ":" not in name, f"{name}: ':' e' il separatore dello spazio dei nomi"
        self._auto = 0
        # the page frame: the drawing's bounding box IS the page
        self._line((0, 0), (self.W, 0), FRAME, 0.5)
        self._line((self.W, 0), (self.W, self.H), FRAME, 0.5)
        self._line((self.W, self.H), (0, self.H), FRAME, 0.5)
        self._line((0, self.H), (0, 0), FRAME, 0.5)

    # ---- the template of a folded page ------------------------------------------
    @staticmethod
    def show(name):
        """A ref or a net as printed: without the template's namespace."""
        return name.split(":", 1)[1] if ":" in name else name

    def template(self, netlist, ns, source_rel):
        """Load a second netlist - the block drawn once - under namespace `ns`:
        "BLK:R108" on "BLK:NREF". Its parts must all be drawn, like the page's."""
        assert self.tmpl is None, "un solo modello per pagina"
        comp, pin = read_kicad_net(netlist)
        for r, v in comp.items():
            assert ":" not in r
            self.comp[f"{ns}:{r}"] = v
        for (r, p), n in pin.items():
            self.pin[(f"{ns}:{r}", p)] = f"{ns}:{n}"
            self.nets.add(f"{ns}:{n}")
        self.tmpl = {"ns": ns, "comp": comp, "pin": pin, "source": source_rel}

    def is_tmpl(self, ref):
        return self.tmpl is not None and ref.startswith(self.tmpl["ns"] + ":")

    # ---- low level -----------------------------------------------------------
    def _line(self, p, q, color=INK, lw=None, ls="-"):
        e = elm.Line().at(_p(p)).to(_p(q)).color(color).linestyle(ls)
        if lw:
            e = e.linewidth(lw)
        self.d.add(e)

    def text(self, xy, s, size=None, color=INK, halign="center", valign="center",
             rotation=0):
        self.d.add(elm.Label().at(_p(xy)).label(
            s, loc="center", halign=halign, valign=valign,
            fontsize=size or self.fs, color=color, rotate=rotation))

    def _find(self, n):
        while self.parent[n] != n:
            self.parent[n] = self.parent[self.parent[n]]
            n = self.parent[n]
        return n

    def _union(self, a, b):
        ra, rb = self._find(a), self._find(b)
        if ra != rb:
            self.parent[ra] = rb

    # ---- nodes -------------------------------------------------------------
    def node(self, name, net, xy):
        assert name not in self.xy, f"nodo {name} dichiarato due volte"
        assert net in self.nets, f"nodo {name}: la rete {net} non esiste nella netlist"
        self.xy[name] = _p(xy)
        self.net[name] = net
        self.parent[name] = name
        return name

    def at(self, n, dx=0.0, dy=0.0, name=None):
        """A new node on n's net, offset from it (not yet wired)."""
        if name is None:
            self._auto += 1
            name = f"_{self._auto}"
        x, y = self.xy[n]
        return self.node(name, self.net[n], (x + dx, y + dy))

    def term(self, ref, pin, xy):
        key = (ref, pin)
        assert key in self.pin, (
            f"{ref}.{pin}: la netlist non lo collega a niente - va disegnato "
            "come non collegato (nc), non come terminale")
        assert key not in self.terminals, f"terminale {ref}.{pin} disegnato due volte"
        name = f"{ref}.{pin}"
        self.node(name, self.pin[key], xy)
        self.terminals[key] = name
        return name

    def T(self, ref, pin):
        """The node of a drawn terminal."""
        return self.terminals[(ref, pin)]

    def P(self, n):
        return self.xy[n]

    def _touch(self, n):
        self.touched.add(n)

    # ---- wires ---------------------------------------------------------------
    def wire(self, a, b, *via, first="v", color=INK):
        """Wire two nodes; same net or AssertionError; orthogonal, never diagonal.

        first='v' goes vertical first at each elbow, 'h' horizontal first."""
        assert self.net[a] == self.net[b], (
            f"filo {a}({self.net[a]}) -> {b}({self.net[b]}): reti diverse")
        net = self.net[a]
        pts = [self.xy[a]] + [_p(v) for v in via] + [self.xy[b]]
        ortho = [pts[0]]
        for q in pts[1:]:
            px, py = ortho[-1]
            if abs(px - q[0]) > EPS and abs(py - q[1]) > EPS:
                ortho.append(_p((px, q[1])) if first == "v" else _p((q[0], py)))
            ortho.append(q)
        for p, q in zip(ortho, ortho[1:]):
            if p != q:
                self._line(p, q, color)
                self.segs.append((p, q, net, a))     # a: the wire's own node
        self._union(a, b)
        self._touch(a)
        self._touch(b)
        return b

    def to(self, a, dx=0.0, dy=0.0, name=None):
        """Wire from a to a new node offset (dx, dy); returns the new node."""
        n = self.at(a, dx, dy, name)
        self.wire(a, n)
        return n

    def toxy(self, a, xy, name=None):
        x, y = self.xy[a]
        return self.to(a, xy[0] - x, xy[1] - y, name)

    # ---- names: labels, grounds, rails ----------------------------------------
    def _name(self, n, text):
        assert text == self.show(self.net[n])
        self.named[n] = self.net[n]          # the island's name IS its net
        self._touch(n)

    def label(self, n, direction="right", length=0.8, text=None, size=None):
        """A net label at the end of a short stub: a named island."""
        net = self.net[n]
        text = text or self.show(net)
        assert text == self.show(net), f"etichetta {text} su {n}, che sta su {net}"
        x, y = self.xy[n]
        dx, dy = {"right": (length, 0), "left": (-length, 0),
                  "up": (0, length), "down": (0, -length)}[direction]
        end = self.at(n, dx, dy)
        self.wire(n, end, color=NETCOL)
        ha = {"right": "left", "left": "right", "up": "center", "down": "center"}[direction]
        off = {"right": (0.15, 0), "left": (-0.15, 0), "up": (0, 0.3), "down": (0, -0.3)}[direction]
        ex, ey = self.xy[end]
        self.d.add(elm.Dot(radius=0.07).at((ex, ey)).color(NETCOL))
        self.text((ex + off[0], ey + off[1]), text, size=size or self.fs, color=NETCOL,
                  halign=ha)
        self._name(end, text)
        return end

    def _mark(self, x0, y0, x1, y1, what):
        """A symbol's footprint on the page: a text over it is unreadable (L63b - a
        ground symbol on a resistor's label passed the text check of L63a)."""
        self.marks.append(((min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)), what))

    def gnd(self, n):
        assert self.show(self.net[n]) == "GND", f"simbolo di massa su {n}, che sta su {self.net[n]}"
        self.d.add(elm.Ground(lead=False).theta(0).at(self.xy[n]).color(GNDCOL).scale(0.85))
        x, y = self.xy[n]
        self._mark(x - 0.32, y - 0.45, x + 0.32, y, "simbolo GND")
        self._name(n, "GND")

    def ret(self, n):
        assert self.show(self.net[n]) == "RLY_RET", f"simbolo RLY_RET su {n}, che sta su {self.net[n]}"
        self.d.add(elm.GroundSignal(lead=False).theta(0).at(self.xy[n]).color(RETCOL).scale(0.85))
        x, y = self.xy[n]
        self._mark(x - 0.32, y - 0.45, x + 0.32, y, "simbolo RLY_RET")
        self._name(n, "RLY_RET")

    def rail(self, n, up=True, text=None, size=None):
        """A supply arrow with the net's name: a named island."""
        net = self.net[n]
        text = text or self.show(net)
        assert text == self.show(net), f"rail {text} su {n}, che sta su {net}"
        x, y = self.xy[n]
        s = 1 if up else -1
        self._line((x, y), (x, y + 0.45 * s), NETCOL)
        self._line((x - 0.3, y + 0.45 * s), (x + 0.3, y + 0.45 * s), NETCOL, 1.1)
        self._mark(x - 0.3, y + 0.4 * s, x + 0.3, y + 0.5 * s, f"simbolo {text}")
        # below the bar the text needs its own height of room (L63b: at -0.8 the bar
        # crossed it)
        self.text((x, y + (0.8 if up else 1.1) * s), text, size=size or self.fs, color=NETCOL)
        self._name(n, text)

    # ---- parts ---------------------------------------------------------------
    def _part(self, ref):
        assert ref in self.comp, f"{ref} non esiste nella netlist"
        assert ref not in self.placed, f"{ref} disegnato due volte"
        self.placed.add(ref)
        return self.comp[ref]

    def _lbl2(self, ref, a, b, side, extra=None, size=None):
        """Reference and value next to a two-terminal part."""
        value, lib, part = self.comp[ref]
        ref = self.show(ref)                 # printed without the namespace
        val = value_text(value, part) if extra is None else extra
        if getattr(self, "_value_override", None) is not None:
            val = self._value_override       # "" prints the reference alone
        (x0, y0), (x1, y1) = self.xy[a], self.xy[b]
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        fs = size or self.fs
        vertical = abs(x0 - x1) < EPS
        if side is None:
            side = "r" if vertical else "t"
        # a line of text is ~1.2 x its size tall: 5 pt at 0.135 in/unit is 0.62 units,
        # so two lines are LINE apart, never less (L63a: 0.44 overlapped 170 times)
        LINE = 0.64
        if side in ("r", "l"):
            dx = 0.5 if side == "r" else -0.5
            ha = "left" if side == "r" else "right"
            if not vertical:
                dx = (abs(x1 - x0) / 2 + 0.2) * (1 if side == "r" else -1)
            if val:
                self.text((mx + dx, my + LINE / 2), ref, size=fs, halign=ha)
                self.text((mx + dx, my - LINE / 2), val, size=fs - 0.5, color=DIM, halign=ha)
            else:
                self.text((mx + dx, my), ref, size=fs, halign=ha)
        elif side == "tb":                      # reference above, value below
            self.text((mx, my + 0.62), ref, size=fs)
            if val:
                self.text((mx, my - 0.62), val, size=fs - 0.5, color=DIM)
        else:
            dy = 0.6 if side == "t" else -0.6
            if vertical:
                dy = (abs(y1 - y0) / 2 + 0.35) * (1 if side == "t" else -1)
            first, second = (dy + LINE, dy) if side == "t" else (dy, dy - LINE)
            self.text((mx, my + first), ref, size=fs)
            if val:
                self.text((mx, my + second), val, size=fs - 0.5, color=DIM)

    def _two(self, ref, e, n1, n2, side, extra=None):
        self.d.add(e.at(self.xy[n1]).to(self.xy[n2]))
        self.bodies.append(("seg", (self.xy[n1], self.xy[n2]), ref))
        self._touch(n1)
        self._touch(n2)
        self._lbl2(ref, n1, n2, side, extra)
        return n1, n2

    def res(self, ref, p1, p2, side=None):
        _, _, part = self._part(ref)
        assert part == "R", f"{ref} non e' una resistenza ({part})"
        a, b = self.term(ref, "1", p1), self.term(ref, "2", p2)
        return self._two(ref, elm.Resistor(), a, b, side)

    def cap(self, ref, p1, p2, side=None):
        """pin 1 at p1: the + of an electrolytic (KiCad C_Polarized)."""
        _, _, part = self._part(ref)
        assert part in ("C", "C_Polarized"), f"{ref} non e' un condensatore ({part})"
        a, b = self.term(ref, "1", p1), self.term(ref, "2", p2)
        if side is None and part == "C_Polarized" and abs(p1[0] - p2[0]) < EPS:
            # schemdraw draws the + beside pin 1, on the right of a part drawn
            # downwards and on the left of one drawn upwards: the label goes opposite
            side = "l" if p1[1] > p2[1] else "r"
        return self._two(ref, elm.Capacitor(polar=(part == "C_Polarized")), a, b, side)

    def dio(self, ref, anode, cathode, side=None):
        """KiCad Device:D*: pin 1 = K, pin 2 = A. schemdraw draws start = anode."""
        _, _, part = self._part(ref)
        kind = {"D": elm.Diode, "D_Schottky": elm.Schottky, "D_Zener": elm.Zener}[part]
        assert symbol_pins("Device", part) == {"1": "K", "2": "A"}
        a, k = self.term(ref, "2", anode), self.term(ref, "1", cathode)
        return self._two(ref, kind(), a, k, side)

    def fuse(self, ref, p1, p2, side=None):
        _, _, part = self._part(ref)
        assert part == "Fuse"
        a, b = self.term(ref, "1", p1), self.term(ref, "2", p2)
        return self._two(ref, elm.Fuse(), a, b, side)

    def tvs(self, ref, p1, p2, side=None):
        """A bidirectional TVS: symmetric, pins 1 / 2 (A1 / A2)."""
        _, lib, part = self._part(ref)
        assert part == "D_TVS" and symbol_pins(lib, part) == {"1": "A1", "2": "A2"}
        a, b = self.term(ref, "1", p1), self.term(ref, "2", p2)
        return self._two(ref, elm.DiodeTVS(), a, b, side)

    def spst(self, ref, p1, p2, side=None):
        """A panel switch drawn open (its rest state)."""
        _, lib, part = self._part(ref)
        assert part == "SW_SPST"
        a, b = self.term(ref, "1", p1), self.term(ref, "2", p2)
        return self._two(ref, elm.Switch(), a, b, side)

    # ---- transistors: single and dual (L63b) ---------------------------------------
    _BJT = {"npn": (elm.BjtNpn, {"C": "collector", "B": "base", "E": "emitter"}),
            "pnp": (elm.BjtPnp, {"C": "collector", "B": "base", "E": "emitter"}),
            "njf": (elm.JFetN, {"D": "drain", "G": "gate", "S": "source"})}

    def trans(self, ref, kind, anchor, xy, rev=False, unit=None, label_side="r",
              note=None, label_dy=0.0):
        """A transistor with `anchor` ('collector', 'emitter', 'drain', 'base' ...)
        at xy, the control terminal on the left (rev: on the right).

        `unit` picks one half of a dual (LS352, LSK489): its pins are the symbol's
        names with the unit's digit (C1 B1 E1, D2 G2 S2). Every pin of a dual's
        symbol must end up a terminal or a declared free pin (nc_note)."""
        value, lib, part = self.comp[ref]
        if ref not in self.placed:
            self._part(ref)
        cls, roles = self._BJT[kind]
        names = symbol_pins(lib, part)
        byname = {}
        for num, nm in names.items():
            byname.setdefault(nm, num)
        e = cls().right()                    # .right() pins the vertical orientation
        if rev:
            e = e.reverse()
        e = e.scale(0.8).anchor(anchor).at(_p(xy))
        self.d.add(e)
        out = {}
        for role, anch in roles.items():
            nm = role + (str(unit) if unit else "")
            assert nm in byname, f"{ref}: il simbolo {lib}:{part} non ha il piedino {nm}"
            out[role] = self.term(ref, byname[nm], e.absanchors[anch])
            self._touch(out[role])
        if unit:
            self.sym_refs.add(ref)
        # the body: no wire may run through the transistor's core
        xs = [e.absanchors[a][0] for a in roles.values()]
        ys = [e.absanchors[a][1] for a in roles.values()]
        self.bodies.append(("rect", (min(xs) + 0.15, min(ys) + 0.15,
                                     max(xs) - 0.15, max(ys) - 0.15), ref))
        c = e.absanchors["center"]
        sgn = 1 if label_side == "r" else -1
        ha = "left" if label_side == "r" else "right"
        name = self.show(ref) + ("ABCD"[unit - 1] if unit else "")
        self.text((c[0] + 0.85 * sgn, c[1] + 0.32 + label_dy), name, halign=ha)
        self.text((c[0] + 0.85 * sgn, c[1] - 0.32 + label_dy),
                  note or (value + (f" {unit}/2" if unit else "")),
                  size=self.fs - 0.5, color=DIM, halign=ha)
        return out

    def nc_note(self, ref, pins, xy, halign="left"):
        """Pins of a symbol the netlist leaves free, written down instead of drawn
        as stubs (the substrate pins of a dual): each must be free, each is recorded."""
        for p in pins:
            assert (ref, p) not in self.pin, f"{ref}.{p} e' collegato: non e' libero"
            self.nc.add((ref, p))
        self.sym_refs.add(ref)
        value, lib, part = self.comp[ref]
        names = symbol_pins(lib, part)
        self.text(xy, f"{self.show(ref)}: " + ", ".join(f"{p} {names[p]}" for p in pins)
                  + " liberi", size=self.fs - 1.2, color=DIM, halign=halign)

    # ---- relays and rotary switches (L63b) ----------------------------------------
    # G6K-2, G6KU-2, IM06: the pin map of circuits/preamp/preamp_audio.py
    # (K_COM / K_NO / K_NC, read on en-g6k.pdf p. 6, NC-014); on the bistable
    # G6KU-2 the throws are SET (4 / 5) and RESET (2 / 7), trim.py
    RELAY_POLES = {1: ("3", "4", "2"), 2: ("6", "5", "7")}
    RELAY_COIL = ("1", "8")

    def _free_cross(self, ref, pin, xy):
        assert (ref, pin) not in self.pin, f"{ref}.{pin} e' collegato: non e' libero"
        self.nc.add((ref, pin))
        x, y = xy
        self._line((x - 0.18, y - 0.18), (x + 0.18, y + 0.18), INK)
        self._line((x - 0.18, y + 0.18), (x + 0.18, y - 0.18), INK)

    def _pin_or_free(self, ref, pin, xy):
        if (ref, pin) in self.pin:
            n = self.term(ref, pin, xy)
            self._touch(n)
            return n
        self._free_cross(ref, pin, xy)
        return None

    def relay_pole(self, ref, pole, xy, length=2.2, h=0.5, flip=False, note=None,
                   label="t", rtl=False):
        """One changeover pole, drawn at rest: COM at xy, the throws `length` to its
        right (to its left with rtl), NO (SET on a bistable) above and NC (RESET)
        below - or the other way with flip. A throw the netlist leaves free carries
        its cross."""
        value, lib, part = self.comp[ref]
        assert part in ("G6K-2", "G6KU-2", "IM06"), f"{ref}: {part} non e' un rele' noto"
        if ref not in self.placed:
            self._part(ref)
        self.sym_refs.add(ref)
        com, no, nc = self.RELAY_POLES[pole]
        bist = part == "G6KU-2"
        x, y = _p(xy)
        s = -1 if flip else 1
        k = -1 if rtl else 1
        xno, yno, ync = x + k * length, y + h * s, y - h * s
        out = {"COM": self._pin_or_free(ref, com, (x, y)),
               "NO": self._pin_or_free(ref, no, (xno, yno)),
               "NC": self._pin_or_free(ref, nc, (xno, ync))}
        piv = (x + k * 0.45, y)
        self._line((x, y), piv)
        self.d.add(elm.Dot(radius=0.07).at(piv))
        self._line((xno - k * 0.55, yno), (xno, yno))
        self._line((xno - k * 0.55, ync), (xno, ync))
        self._line(piv, (xno - k * 0.55, ync + 0.09 * s))       # the blade, at rest
        xa, xb = sorted((x + k * 0.3, xno - k * 0.3))
        self.bodies.append(("rect", (xa, min(yno, ync) + 0.12, xb, max(yno, ync) - 0.12), ref))
        tno, tnc = ("S", "R") if bist else ("NO", "NC")
        # the pin texts sit over the contacts, clear of a wire that reaches a throw
        # from outside (it arrives at xno, vertically or horizontally)
        self.text((xno - k * 0.65, yno + 0.3 * s), f"{tno} {no}", size=self.fs - 1.6,
                  color=DIM)
        self.text((xno - k * 0.65, ync - 0.3 * s), f"{tnc} {nc}", size=self.fs - 1.6,
                  color=DIM)
        self.text((x + k * 0.2, y - 0.3), com, size=self.fs - 1.6, color=DIM,
                  halign="left" if k > 0 else "right")
        lx, ly = (x + k * length / 2, max(yno, ync) + 0.95) if label == "t" else \
            (x + k * length / 2, min(yno, ync) - 0.95)
        self.text((lx, ly), f"{self.show(ref)}·{pole}" + (f"  {note}" if note else ""),
                  size=self.fs - 0.5)
        return out

    def relay_coil(self, ref, a1, a2, side="r", note=None, pins=("A1", "A2"), word=" bobina"):
        """The coil of a relay whose contacts are drawn elsewhere (same ref).
        pins: the coil's pin numbers, the first at a1 (G6K / IM06: RELAY_COIL);
        word: printed after the ref ("" where the coils stand in a tight row)."""
        value, lib, part = self.comp[ref]
        if ref not in self.placed:
            self._part(ref)
        if part in ("G6K-2", "G6KU-2", "IM06"):
            self.sym_refs.add(ref)
            pins = self.RELAY_COIL
        A1, A2 = self.term(ref, pins[0], a1), self.term(ref, pins[1], a2)
        (x, y0), (_, y1) = self.xy[A1], self.xy[A2]
        assert abs(self.xy[A1][0] - self.xy[A2][0]) < EPS
        top, bot = max(y0, y1), min(y0, y1)
        m = (top + bot) / 2
        self._line((x, top), (x, m + 0.5))
        self._line((x, bot), (x, m - 0.5))
        for p, q in (((x - 0.4, m - 0.5), (x + 0.4, m - 0.5)), ((x + 0.4, m - 0.5), (x + 0.4, m + 0.5)),
                     ((x + 0.4, m + 0.5), (x - 0.4, m + 0.5)), ((x - 0.4, m + 0.5), (x - 0.4, m - 0.5))):
            self._line(p, q, INK, 1.0)
        self._line((x - 0.4, m - 0.5), (x + 0.4, m + 0.5), INK)
        self.bodies.append(("seg", ((x, m - 0.5), (x, m + 0.5)), ref))
        self._touch(A1)
        self._touch(A2)
        dx, ha = (0.6, "left") if side == "r" else (-0.6, "right")
        self.text((x + dx, m + 0.32), f"{self.show(ref)}{word}", halign=ha)
        self.text((x + dx, m - 0.32), note or value, size=self.fs - 0.8, color=DIM, halign=ha)
        # pin numbers inside the leads' corner, clear of a wire along the top or bottom
        sx = 1 if side == "l" else -1
        self.text((x + 0.55 * sx, top - 0.3), pins[0], size=self.fs - 1.6, color=DIM,
                  halign="left" if sx > 0 else "right")
        self.text((x + 0.55 * sx, bot + 0.3), pins[1], size=self.fs - 1.6, color=DIM,
                  halign="left" if sx > 0 else "right")
        return A1, A2

    # SW_Rotary_4x3: commons 13-16, throws 1-2-3, 4-5-6, 7-8-9, 10-11-12;
    # SW_Rotary_3x4: commons 13-15, throws 1-4, 5-8, 9-12; the k-th throw of each
    # pole is position k (pin geometry read on the KiCad symbol in L48a:
    # circuits/preamp/selector.py, gain_interlock.py, trim.py)
    ROTARY = {"SW_Rotary_4x3": [("13", ("1", "2", "3")), ("14", ("4", "5", "6")),
                                ("15", ("7", "8", "9")), ("16", ("10", "11", "12"))],
              "SW_Rotary_3x4": [("13", ("1", "2", "3", "4")), ("14", ("5", "6", "7", "8")),
                                ("15", ("9", "10", "11", "12"))]}

    def rotary_pole(self, ref, pole, xy, pitch=0.8, length=2.4, positions=None, label=True):
        """One pole of a rotary switch: the common at xy on the left, its throws in a
        column on the right, position 1 on top; the wiper drawn on position 1.
        `positions` names them (0 dB, +3 dB ...). A free pin carries its cross."""
        value, lib, part = self.comp[ref]
        if ref not in self.placed:
            self._part(ref)
        self.sym_refs.add(ref)
        com, throws = self.ROTARY[part][pole]
        x, y = _p(xy)
        n = len(throws)
        ys = [y + (n - 1) / 2 * pitch - i * pitch for i in range(n)]
        xt = x + length
        out = {"COM": self._pin_or_free(ref, com, (x, y))}
        piv = (x + 0.45, y)
        self._line((x, y), piv)
        self.d.add(elm.Dot(radius=0.07).at(piv))
        for i, (t, yt) in enumerate(zip(throws, ys)):
            out[i + 1] = self._pin_or_free(ref, t, (xt, yt))
            self._line((xt - 0.55, yt), (xt, yt))
            self.d.add(elm.Dot(radius=0.06, open=True).at((xt - 0.6, yt)))
            lbl = f"{t}" + (f" {positions[i]}" if positions else "")
            # over the throw, ending short of it: a wire may join two throws at xt
            self.text((xt - 0.3, yt + 0.27), lbl, size=self.fs - 1.8, color=DIM, halign="right")
        self._line(piv, (xt - 0.68, ys[0] - 0.05))             # the wiper, on position 1
        self.bodies.append(("rect", (x + 0.3, min(ys) - 0.1, xt - 0.7, max(ys) + 0.1), ref))
        self.text((x - 0.1, y + 0.3), com, size=self.fs - 1.6, color=DIM, halign="right")
        if label:
            self.text((x + length / 2, max(ys) + 0.85),
                      f"{self.show(ref)} polo {'abcd'[pole]}", size=self.fs - 0.5)
        return out

    def nettie(self, ref, p1, p2, side=None):
        """A net tie: the one place two named nets are allowed to meet."""
        _, _, part = self._part(ref)
        assert part == "NetTie_2"
        a, b = self.term(ref, "1", p1), self.term(ref, "2", p2)
        (x0, y0), (x1, y1) = self.xy[a], self.xy[b]
        self._line((x0, y0), (x1, y1), INK, 2.2)
        self._touch(a)
        self._touch(b)
        self._lbl2(ref, a, b, side, extra="tie stellare")
        return a, b

    def two(self, ref, at, side=None, value=None):
        """A two-terminal part placed BY NET: at = {net: point, net: point}.

        Which pin goes where - and so which way a diode or an electrolytic
        points - is read from the netlist, never chosen at the call site.
        `value` replaces the printed value (a netlist value too long for the
        page); the caller then prints the netlist's own text somewhere else."""
        _, lib, part = self.comp[ref]
        pins = {p: n for (r, p), n in self.pin.items() if r == ref}
        assert sorted(pins.values()) == sorted(at), (
            f"{ref}: nella netlist su {sorted(pins.values())}, disegnato su {sorted(at)}")
        p1, p2 = at[pins["1"]], at[pins["2"]]
        self._value_override = value
        try:
            if part in ("D", "D_Schottky", "D_Zener"):
                return self.dio(ref, anode=p2, cathode=p1, side=side)
            fn = {"R": self.res, "C": self.cap, "C_Polarized": self.cap,
                  "Fuse": self.fuse, "NetTie_2": self.nettie,
                  "D_TVS": self.tvs, "SW_SPST": self.spst}[part]
            return fn(ref, p1, p2, side=side)
        finally:
            self._value_override = None

    def N(self, ref, net):
        """The drawn terminal of `ref` that sits on `net` (exactly one)."""
        got = [n for (r, p), n in self.terminals.items() if r == ref and self.net[n] == net]
        assert len(got) == 1, f"{ref} su {net}: {got}"
        return got[0]

    def zref(self, ref, anode, cathode, side=None, shown=None):
        """A shunt reference (LM4040): drawn as a zener, K and A from its symbol;
        the other pins of the symbol must be unconnected, and are recorded so.
        `shown` replaces the printed value, as `value` in two(): the caller prints the
        netlist's own text elsewhere."""
        value, lib, part = self._part(ref)
        sym = symbol_pins(lib, part)
        byname = {nm: num for num, nm in sym.items()}
        a = self.term(ref, byname["A"], anode)
        k = self.term(ref, byname["K"], cathode)
        for num in sym:
            if num not in (byname["A"], byname["K"]):
                assert (ref, num) not in self.pin, f"{ref}.{num} e' collegato"
                self.nc.add((ref, num))
        self._value_override = shown
        try:
            self._two(ref, elm.Zener(), a, k, side,
                      extra=value + "  (" + ", ".join(f"{n} nc" for n in sorted(sym)
                                                      if n not in (byname["A"], byname["K"])) + ")")
        finally:
            self._value_override = None
        return a, k

    def dio_pair(self, ref, a1, com, k2, side=None):
        """Two diodes in series in one SOT-23 (Diode:BAV99, fitted as BAV99 or BAV199,
        L57b): pin 1 = A1, pin 3 = K1/A2 the common node, pin 2 = K2 - by NUMBER, as the
        Nexperia datasheets say (BAV199 p. 1, table 2). The KiCad symbol names pins 1 / 2
        "K" / "A", against its own drawing: the names are not read."""
        _, lib, part = self._part(ref)
        assert (lib, part) == ("Diode", "BAV99"), f"{ref}: {lib}:{part}"
        assert sorted(symbol_pins(lib, part)) == ["1", "2", "3"]
        a = self.term(ref, "1", a1)
        c = self.term(ref, "3", com)
        k = self.term(ref, "2", k2)
        for p, q in ((a, c), (c, k)):
            self.d.add(elm.Diode().at(self.xy[p]).to(self.xy[q]))
            self.bodies.append(("seg", (self.xy[p], self.xy[q]), ref))
        for n in (a, c, k):
            self._touch(n)
        self._lbl2(ref, a, k, side)
        return a, c, k

    def _mos(self, ref, e, pinmap, xy_anchor, anchor, label_side):
        value, lib, part = self._part(ref)
        names = symbol_pins(lib, part)
        e = e.anchor(anchor).at(_p(xy_anchor))
        self.d.add(e)
        out = {}
        for num, nm in names.items():
            pos = e.absanchors[pinmap[nm]]
            out[nm] = self.term(ref, num, pos)
            self._touch(out[nm])
        c = e.absanchors["center"]
        dx = 1.0 if label_side == "r" else -1.0
        ha = "left" if label_side == "r" else "right"
        self.text((c[0] + dx, c[1] + 0.32), ref, halign=ha)
        self.text((c[0] + dx, c[1] - 0.32), value, size=self.fs - 0.5, color=DIM, halign=ha)
        return out

    def nmos(self, ref, drain, gate="left", label_side=None):
        """N-channel, drain up, source down; the drain at `drain`."""
        e = elm.NFet().right()               # .right() pins the vertical orientation
        if gate == "left":
            e = e.reverse()
        return self._mos(ref, e.scale(0.8), {"G": "gate", "S": "source", "D": "drain"},
                         drain, "drain", label_side or ("r" if gate == "left" else "l"))

    def pmos(self, ref, source, gate="left", label_side=None):
        """P-channel, source up, drain down; the source at `source`."""
        e = elm.PFet().right()
        if gate == "left":
            e = e.reverse()
        return self._mos(ref, e.scale(0.8), {"G": "gate", "S": "source", "D": "drain"},
                         source, "source", label_side or ("r" if gate == "left" else "l"))

    def npn(self, ref, collector, base="left", label_side=None):
        e = elm.BjtNpn().right()
        if base == "right":
            e = e.reverse()
        return self._mos(ref, e.scale(0.8), {"B": "base", "E": "emitter", "C": "collector"},
                         collector, "collector", label_side or ("r" if base == "left" else "l"))

    def comparator(self, ref, unit, pins, out_xy, flip=False, power=None, note=None):
        """One half of a dual comparator, drawn as a triangle pointing right.

        pins = {'-': n, '+': n, 'out': n}; power = (v+ pin, v- pin) on the unit that
        carries them. flip puts + on top. The part is 'placed' when its first unit is."""
        value, lib, part = self.comp[ref]
        if ref not in self.placed:
            self._part(ref)
        names = symbol_pins(lib, part)
        e = elm.Opamp(leads=False).right().scale(0.8)
        if flip:
            e = e.flip()
        e = e.anchor("out").at(_p(out_xy))
        self.d.add(e)
        A = e.absanchors
        _o = A["out"]
        # the triangle's core: the inputs (+-0.5) and the supply pins (+-0.67) stay outside
        self.bodies.append(("rect", (_o[0] - 1.73, _o[1] - 0.45, _o[0] - 0.1, _o[1] + 0.45), ref))
        res = {}
        for role, anch in (("-", "in1"), ("+", "in2"), ("out", "out")):
            num = pins[role]
            if role in "+-":
                assert names[num] == role, f"{ref}.{num} e' {names[num]!r}, non {role!r}"
            res[role] = self.term(ref, num, A[anch])
            self._touch(res[role])
        if power:
            res["V+"] = self.term(ref, power[0], A["vd"])
            res["V-"] = self.term(ref, power[1], A["vs"])
            assert names[power[0]] == "V+" and names[power[1]] == "V-"
            self._touch(res["V+"])
            self._touch(res["V-"])
        o = A["out"]
        self.text((o[0] + 0.15, o[1] + 0.38), f"{ref}{unit}", halign="left")
        if note:
            self.text((o[0] + 0.15, o[1] - 0.38), note, size=self.fs - 0.8, color=DIM,
                      halign="left")
        return res

    def ic(self, ref, x0, y1, w, h, pins, nc=(), title=None, sub=None, names=None):
        """A box, upper left (x0, y1), w x h. pins: {num: (side, offset)}, side in
        l r t b, offset from the top (l, r) or from the left (t, b). Pin names from
        the symbol (or `names`). Every pin the symbol declares must be in pins or nc."""
        value, lib, part = self._part(ref)
        sym = symbol_pins(lib, part)
        declared = set(sym)
        given = set(pins) | set(nc)
        assert given == declared, (
            f"{ref}: piedini del simbolo {sorted(declared - given)} non disegnati, "
            f"{sorted(given - declared)} inventati")
        self.ic_refs[ref] = declared
        x1, y0 = x0 + w, y1 - h
        self.bodies.append(("rect", (x0, y0, x1, y1), ref))
        for p, q in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)),
                     ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
            self._line(p, q, INK, 1.0)
        stub = 0.6
        out = {}
        for num, (side, off) in list(pins.items()) + [(n, s) for n, s in
                                                      (nc.items() if isinstance(nc, dict) else [])]:
            if side == "l":
                pin_in, pin_out = (x0, y1 - off), (x0 - stub, y1 - off)
                nxy, nh = (x0 + 0.15, y1 - off), "left"
                numxy, numh = (x0 - 0.1, y1 - off + 0.36), "right"
            elif side == "r":
                pin_in, pin_out = (x1, y1 - off), (x1 + stub, y1 - off)
                nxy, nh = (x1 - 0.15, y1 - off), "right"
                numxy, numh = (x1 + 0.1, y1 - off + 0.36), "left"
            elif side == "t":
                pin_in, pin_out = (x0 + off, y1), (x0 + off, y1 + stub)
                nxy, nh = (x0 + off, y1 - 0.3), "center"
                numxy, numh = (x0 + off - 0.1, y1 + 0.3), "right"
            else:
                pin_in, pin_out = (x0 + off, y0), (x0 + off, y0 - stub)
                nxy, nh = (x0 + off, y0 + 0.3), "center"
                numxy, numh = (x0 + off - 0.1, y0 - 0.3), "right"
            self._line(pin_in, pin_out, INK)
            nm = (names or {}).get(num, sym[num])
            nm = nm.replace("~{RESET}", "RESET̅")
            if side in ("t", "b"):
                # the names stand upright inside the box; centred on half their
                # length (a rotated text does not honour valign the way it reads)
                half = 0.2 + 0.17 * len(nm)
                cy = y0 + half if side == "b" else y1 - half
                self.text((nxy[0], cy), nm, size=self.fs - 1.0, halign="center",
                          valign="center", rotation=90)
            else:
                self.text(nxy, nm, size=self.fs - 1.0, halign=nh)
            self.text(numxy, num, size=self.fs - 1.4, color=DIM, halign=numh)
            if num in pins:
                out[num] = self.term(ref, num, pin_out)
            else:
                assert (ref, num) not in self.pin, f"{ref}.{num} e' collegato: non e' nc"
                self.nc.add((ref, num))
                px, py = pin_out
                self._line((px - 0.18, py - 0.18), (px + 0.18, py + 0.18), INK)
                self._line((px - 0.18, py + 0.18), (px + 0.18, py - 0.18), INK)
        self.text(((x0 + x1) / 2, y1 + (1.05 if any(s == "t" for s, _ in pins.values()) else 0.55)),
                  title or f"{ref}  {value}", size=self.fs + 0.5)
        if sub:
            self.text(((x0 + x1) / 2, y0 - (1.0 if any(s == "b" for s, _ in pins.values()) else 0.45)),
                      sub, size=self.fs - 0.8, color=DIM)
        return out

    def conn(self, ref, x, ytop, pins, side="l", pitch=0.8, title=None, sub=None):
        """A connector: a narrow box with its pins, in order, on one side.

        pins: list of pin numbers, top to bottom; the stubs point to `side`."""
        value, lib, part = self._part(ref)
        sym = symbol_pins(lib, part)
        assert set(pins) == set(sym), f"{ref}: piedini {sorted(sym)} != {sorted(pins)}"
        w, h = 1.1, pitch * len(pins) + 0.3
        x0, x1, y1 = x, x + w, ytop
        y0 = y1 - h
        self.bodies.append(("rect", (x0, y0, x1, y1), ref))
        for p, q in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)),
                     ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
            self._line(p, q, INK, 1.0)
        out = {}
        for i, num in enumerate(pins):
            y = y1 - 0.15 - pitch * (i + 0.5)
            if side == "l":
                a, b = (x0, y), (x0 - 0.6, y)
                self.text((x0 + 0.15, y), num, size=self.fs - 1.0, halign="left")
            else:
                a, b = (x1, y), (x1 + 0.6, y)
                self.text((x1 - 0.15, y), num, size=self.fs - 1.0, halign="right")
            self._line(a, b, INK)
            self.d.add(elm.Dot(radius=0.06, open=True).at(_p(b)))
            out[num] = self.term(ref, num, b)
        self.text(((x0 + x1) / 2, y1 + 1.05), ref, size=self.fs)
        self.text(((x0 + x1) / 2, y1 + 0.42), title or value, size=self.fs - 0.8, color=DIM)
        if sub:
            self.text(((x0 + x1) / 2, y0 - 0.4), sub, size=self.fs - 0.8, color=DIM)
        return out

    def testpoint(self, ref, xy, length=1.0):
        """A test point (ADR-107, L58a): an open ring with its reference on the left
        and a stub to the right ending in its net's label - the net is read by name.
        The value, "TP_<net>", is not printed: the label already says it."""
        value, lib, part = self._part(ref)
        assert part == "TestPoint", f"{ref} non e' un test point ({part})"
        assert set(symbol_pins(lib, part)) == {"1"}, f"{ref}: un solo piedino"
        x, y = xy
        r = 0.22
        self.d.add(elm.Dot(radius=r, open=True).at(_p((x, y))))
        self.bodies.append(("rect", (x - r, y - r, x + r, y + r), ref))
        self.text((x - r - 0.15, y), self.show(ref), size=self.fs - 0.5, halign="right")
        n = self.term(ref, "1", (x + r, y))
        return self.label(n, "right", length)

    def bridge(self, ref, c, r=1.4, label_side="l"):
        """A bridge drawn diode by diode: + (pin 1) on top, - (pin 4) at the
        bottom, ~ (pins 2, 3) left and right. The four cathodes of the + corner
        and the four anodes of the - corner are drawn, not assumed from a symbol."""
        value, lib, part = self._part(ref)
        assert part == "D_Bridge_+AA-"
        sym = symbol_pins(lib, part)
        assert sym["1"] == "+" and sym["4"] == "-"
        cx, cy = c
        W, N, E, S = (cx - r, cy), (cx, cy + r), (cx + r, cy), (cx, cy - r)
        for a, k in ((W, N), (E, N), (S, W), (S, E)):       # anode -> cathode
            self.d.add(elm.Diode().at(_p(a)).to(_p(k)))
        out = {"+": self.term(ref, "1", N), "~1": self.term(ref, "2", W),
               "~2": self.term(ref, "3", E), "-": self.term(ref, "4", S)}
        for n in out.values():
            self._touch(n)
        self.text((N[0] + 0.25, N[1] - 0.05), "+", size=self.fs, halign="left")
        self.text((S[0] + 0.25, S[1] + 0.05), "−", size=self.fs, halign="left")
        dx = -r - 0.3 if label_side == "l" else r + 0.3
        ha = "right" if label_side == "l" else "left"
        self.text((cx + dx, cy + r * 0.75), ref, halign=ha)
        self.text((cx + dx, cy + r * 0.75 - 0.64), value, size=self.fs - 0.5, color=DIM, halign=ha)
        return out

    def relay_contact(self, ref, p_in, p_out, xy_in, xy_out, note=None):
        """One normally-open contact, horizontal, left (p_in) to right (p_out)."""
        if ref not in self.placed:
            self._part(ref)
        a, b = self.term(ref, p_in, xy_in), self.term(ref, p_out, xy_out)
        self.d.add(elm.Switch().at(self.xy[a]).to(self.xy[b]).scale(0.8))
        self._touch(a)
        self._touch(b)
        (x0, y0), (x1, _) = self.xy[a], self.xy[b]
        self.text(((x0 + x1) / 2, y0 + 0.75), f"{ref}  {p_in}–{p_out}", size=self.fs - 0.5)
        return a, b

    # ---- the fold: one block for eight, one channel for two (L63b) ----------------
    @staticmethod
    def _num(ref):
        m = re.fullmatch(r"([A-Z]+)(\d+)", ref)
        assert m, f"sigla non numerata: {ref}"
        return m.group(1), int(m.group(2))

    def fold(self, instances, optional, tbase, left, ref_lr, net_lr, pairs,
             value_lr=lambda v: v, fixed=None):
        """Derive, and assert on the netlist, what the drawing stands for.

        instances  [(tag, base)]: every instance of the template on the board;
        optional   {role: (net, net)}: the template's parts gain_block() fits only
                   with some parameters, found by their two TEMPLATE nets;
        tbase      the template's own base (gain_block.net: 100);
        left       predicate: an audio part of the left channel outside the blocks,
                   drawn, whose twin on the right is NOT drawn;
        ref_lr, net_lr, value_lr   the left -> right rules for its ref, its nets and
                   its value (a connector's value names its channel: IN1_L);
        pairs      [(left tag, right tag)]: the right instance a left box stands for.
        fixed      None, or an offset: the template parts numbered from tbase + fixed
                   up are NOT on the running count - gain_block() numbers them from
                   base + fixed on every instance (section 14, ADR-099, L45d2b3b2b1:
                   R190.. so as not to land on the channel's own base + 61..), so no
                   left-out part shifts them, and they are found in base + fixed ..
                   base + 99.

        The table template ref -> instance ref is DERIVED from the numbering of
        gain_block() (one counter from `base`, a part skipped is a number not used):
        for each subset of optional parts left out, every template part t maps to
        base + (t - tbase) - (left-out parts numbered below t), and exactly one
        subset must give the instance's parts. Then, row by row: the same symbol and
        the same value (or the difference is recorded, to be printed), and every
        template net landing on ONE net of the instance - its own prefixed net, a
        rail, or a port of the instance."""
        assert self.tmpl is not None, "fold() vuole un modello (template())"
        ns = self.tmpl["ns"]
        tc, tp = self.tmpl["comp"], self.tmpl["pin"]
        tparts = sorted(tc, key=lambda r: (self._num(r)[1], r))
        letters = {self._num(r)[0] for r in tparts}
        opt = {}
        for role, nets in optional.items():
            hits = [r for r in tparts
                    if sorted(n for (q, _), n in tp.items() if q == r) == sorted(nets)]
            assert len(hits) == 1, f"parte opzionale {role} su {nets}: {hits}"
            opt[role] = hits[0]
        audio = {r for r in self.comp if not self.is_tmpl(r)}
        apin = {k: n for k, n in self.pin.items() if not self.is_tmpl(k[0])}
        tnets = sorted(set(tp.values()))
        table, absent, diffs, netmap = {}, {}, {}, {}
        for tag, base in instances:
            inst = sorted(r for r in audio if self._num(r)[0] in letters
                          and (base < self._num(r)[1] < base + 60
                               or (fixed is not None
                                   and base + fixed <= self._num(r)[1] < base + 100)))
            sols = []
            for k in range(len(opt) + 1):
                for out in itertools.combinations(sorted(opt.values()), k):
                    mp = {}
                    for t in tparts:
                        if t in out:
                            continue
                        lt, nt = self._num(t)
                        shift = (0 if fixed is not None and nt - tbase >= fixed
                                 else sum(1 for o in out if self._num(o)[1] < nt))
                        mp[t] = f"{lt}{base + nt - tbase - shift}"
                    if sorted(mp.values()) == inst:
                        sols.append((out, mp))
            assert len(sols) == 1, (
                f"istanza {tag} (base {base}): {len(sols)} soluzioni della numerazione "
                f"per {len(inst)} parti")
            out, mp = sols[0]
            table[tag], absent[tag] = mp, {r: o for r, o in opt.items() if o in out}
            diffs[tag] = {}
            for t, i in mp.items():
                (tv, tl, tpart), (iv, il, ipart) = tc[t], self.comp[i]
                assert (tl, tpart) == (il, ipart), f"{tag}: {t} e' {tl}:{tpart}, {i} e' {il}:{ipart}"
                if tv != iv:
                    diffs[tag][t] = iv
            nm = {}
            for (t, p), x in tp.items():
                if t not in mp:
                    continue
                got = apin.get((mp[t], p))
                assert got is not None, f"{tag}: {mp[t]}.{p} libero, {t}.{p} su {x}"
                nm.setdefault(x, set()).add(got)
            for (i, p) in apin:
                if i in inst:
                    t = {v: k for k, v in mp.items()}[i]
                    assert (t, p) in tp, f"{tag}: {i}.{p} collegato, {t}.{p} no"
            # a template net is a RAIL where it keeps its name (VPLUS, GND), a PORT
            # where a part outside the instance shares it (IN, OUT, RG), and
            # otherwise INTERNAL - and then its name must be the rule's, tag_X
            kinds = {}
            insts = set(inst)
            for x in tnets:
                got = nm.get(x)
                if not got:              # a net only the left-out parts touch (RG on A)
                    continue
                assert len(got) == 1, f"{tag}: la rete {x} del blocco cade su {sorted(got)}"
                g = got.pop()
                outside = any(n == g and r not in insts for (r, _), n in apin.items())
                if g == x:
                    kinds[x] = ("rail", g)
                elif outside:
                    kinds[x] = ("port", g)
                else:
                    assert g == f"{tag}_{x}", f"{tag}: la rete interna {x} si chiama {g}"
                    kinds[x] = ("int", g)
            netmap[tag] = kinds
        # the right channel: the rule, asserted part by part (values too: the
        # manifest check compares only the connections)
        lefts = sorted(r for r in audio if left(r))
        in_blocks = {i for mp in table.values() for i in mp.values()}
        assert not set(lefts) & in_blocks, f"parti del canale nei blocchi: {sorted(set(lefts) & in_blocks)}"
        mirror = {}
        for r in lefts:
            q = ref_lr(r)
            assert q in audio, f"{r} -> {q}: non esiste nella netlist"
            (v, l, p), (vq, lq, pq) = self.comp[r], self.comp[q]
            assert (value_lr(v), l, p) == (vq, lq, pq), f"{r} {self.comp[r]} -> {q} {self.comp[q]}"
            mirror[r] = q
        # the nets: the rule names them, the netlist must agree. A merged node takes
        # ONE of its names in SKiDL (preamp_audio.py: "do not start relying on it"),
        # so where the rule's name does not exist the right net is the one the
        # mirrored pins sit on - recorded as an alias, printed on the page. Either
        # way the correspondence must be a bijection: one left net, one right net.
        seen = {}
        for r, q in mirror.items():
            lp_ = {p: n for (rr, p), n in apin.items() if rr == r}
            rq_ = {p: n for (rr, p), n in apin.items() if rr == q}
            assert set(lp_) == set(rq_), f"{r} -> {q}: piedini {sorted(lp_)} != {sorted(rq_)}"
            for p in lp_:
                seen.setdefault(lp_[p], set()).add(rq_[p])
        for lt, rt in pairs:
            assert table[lt] and set(table[lt]) == set(table[rt]), f"{lt} e {rt} diversi"
            lp = {x: g for x, (k, g) in netmap[lt].items() if k == "port"}
            rp = {x: g for x, (k, g) in netmap[rt].items() if k == "port"}
            assert set(lp) == set(rp), f"porte di {rt} {sorted(rp)} != di {lt} {sorted(lp)}"
            for x in lp:
                seen.setdefault(lp[x], set()).add(rp[x])
        lr, aliases = {}, {}
        anets = set(apin.values())
        for n, got in sorted(seen.items()):
            assert len(got) == 1, f"la rete {n} del sinistro cade a destra su {sorted(got)}"
            g = got.pop()
            want = net_lr(n)
            if want in anets:
                assert g == want, f"{n} -> {want} per la regola, ma la netlist dice {g}"
            else:
                aliases[want] = g
            lr[n] = g
        inv = {}
        for n, g in lr.items():
            assert g not in inv, f"{inv.get(g)} e {n} del sinistro cadono entrambe su {g}"
            inv[g] = n
        expanded = {}
        for tag in table:
            for t, i in table[tag].items():
                assert i not in expanded, f"{i} espanso due volte"
                expanded[i] = ("istanza", tag, t)
        for r, q in mirror.items():
            assert q not in expanded, f"{q} espanso due volte"
            expanded[q] = ("destro", r)
        self.folded = {"table": table, "absent": absent, "diffs": diffs, "netmap": netmap,
                       "mirror": mirror, "net_lr": lambda n: lr[n], "lr": lr,
                       "aliases": aliases, "pairs": dict(pairs),
                       "expanded": expanded, "instances": [t for t, _ in instances],
                       "tparts": tparts, "optional": opt}
        return self.folded

    def instance(self, tag, x0, y1, w, h, ports, title=None, sub=None):
        """A box for one instance of the template: its ports, on the instance's
        own nets (derived by fold()), are nodes the drawing must wire or label.
        ports = {template net: (side, offset)}, as ic(); every port, no others."""
        F = self.folded
        assert F is not None, "instance() dopo fold()"
        assert tag not in self.boxes, f"istanza {tag} disegnata due volte"
        have = {x: g for x, (k, g) in F["netmap"][tag].items() if k == "port"}
        assert set(ports) == set(have), f"{tag}: porte {sorted(have)} != disegnate {sorted(ports)}"
        x1, yb = x0 + w, y1 - h
        self.bodies.append(("rect", (x0, yb, x1, y1), f"istanza {tag}"))
        for p, q in (((x0, yb), (x1, yb)), ((x1, yb), (x1, y1)),
                     ((x1, y1), (x0, y1)), ((x0, y1), (x0, yb))):
            self._line(p, q, INK, 1.1)
        out = {}
        for x, (side, off) in ports.items():
            if side == "l":
                pin_in, pin_out, txy, ha = (x0, y1 - off), (x0 - 0.6, y1 - off), (x0 + 0.15, y1 - off), "left"
            elif side == "r":
                pin_in, pin_out, txy, ha = (x1, y1 - off), (x1 + 0.6, y1 - off), (x1 - 0.15, y1 - off), "right"
            elif side == "b":
                pin_in, pin_out, txy, ha = (x0 + off, yb), (x0 + off, yb - 0.6), (x0 + off, yb + 0.35), "center"
            else:
                pin_in, pin_out, txy, ha = (x0 + off, y1), (x0 + off, y1 + 0.6), (x0 + off, y1 - 0.35), "center"
            self._line(pin_in, pin_out, INK)
            self.text(txy, x, size=self.fs - 1.0, halign=ha)
            out[x] = self.node(f"{tag}.{x}", have[x], pin_out)
        self.boxes[tag] = out
        self.text(((x0 + x1) / 2, y1 + 0.5), title or f"blocco {tag}", size=self.fs + 0.5)
        if sub:                                 # under the top edge, above the ports
            for i, line in enumerate(sub if isinstance(sub, (list, tuple)) else [sub]):
                self.text(((x0 + x1) / 2, y1 - 0.55 - 0.55 * i), line,
                          size=self.fs - 1.0, color=DIM)
        return out

    def instance_table(self, x0, y1, order, colw=2.55, refw=3.2, row=0.5, size=None):
        """The table of the instances: one row per template part (the ref printed on
        the block), one column per instance (`order`), the instance's own ref - or
        '—' where that instance does not fit it; a value that differs from the
        block's is printed in the cell. Every cell comes from fold()."""
        F = self.folded
        fs = size or self.fs - 0.8
        ns = self.tmpl["ns"]
        cols = list(order)
        assert sorted(cols) == sorted(F["instances"])
        hdr = ["blocco", "valore"] + cols
        xs = [x0, x0 + refw] + [x0 + refw + 2.6 + colw * i for i in range(len(cols))]
        y = y1
        for x, t in zip(xs, hdr):
            self.text((x, y), t, size=fs, halign="left")
        self._line((x0, y - 0.38), (xs[-1] + colw, y - 0.38), FRAME, 0.5)
        y -= row + 0.35
        rows = sorted(F["tparts"], key=lambda r: ("QRCD".find(self._num(r)[0][0]), self._num(r)[1]))
        for t in rows:
            v, lib, part = self.tmpl["comp"][t]
            cells = [t, value_text(v, part)]
            for tag in cols:
                i = F["table"][tag].get(t)
                d = F["diffs"][tag].get(t)
                cells.append("—" if i is None else (i + (f" {d}" if d else "")))
            for x, c in zip(xs, cells):
                self.text((x, y), c, size=fs, halign="left",
                          color=DIM if c == "—" else INK)
            y -= row
        self._line((x0, y + row - 0.3), (xs[-1] + colw, y + row - 0.3), FRAME, 0.5)
        y -= 0.15
        ports = sorted({x for tag in cols for x, (k, _) in F["netmap"][tag].items() if k == "port"})
        for x in ports:
            cells = [f"porta {x}", ""]
            for tag in cols:
                k = F["netmap"][tag].get(x)
                cells.append(k[1] if k and k[0] == "port" else "—")
            for xx, c in zip(xs, cells):
                self.text((xx, y), c, size=fs - 0.6, halign="left", color=NETCOL if c not in ("", "—") else DIM)
            y -= row
        return y

    # ---- decoration ------------------------------------------------------------
    def panel(self, x0, y0, x1, y1, title, sub=None):
        for p, q in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)),
                     ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
            self._line(p, q, FRAME, 0.6)
        self.text((x0 + 0.4, y1 - 0.55), title, size=self.fs + 2.5, halign="left")
        if sub:
            self.text((x0 + 0.4, y1 - 1.2), sub, size=self.fs - 0.5, color=DIM, halign="left")

    def dashed_box(self, x0, y0, x1, y1, title, sub=None):
        for p, q in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)),
                     ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
            self._line(p, q, DIM, 0.6, ls="--")
        self.text(((x0 + x1) / 2, (y0 + y1) / 2 + 0.34), title, size=self.fs, color=DIM)
        if sub:
            self.text(((x0 + x1) / 2, (y0 + y1) / 2 - 0.34), sub, size=self.fs - 1.0, color=DIM)

    # ---- the checks, then the files --------------------------------------------
    def finish(self, svg, pdf, manifest, png=None, png_dpi=150):
        problems = []
        # (2) shorts in the picture
        by_pt = {}
        for n, p in self.xy.items():
            by_pt.setdefault(p, []).append(n)
        for p, group in sorted(by_pt.items()):
            nets = {self.net[g] for g in group}
            if len(nets) > 1:
                problems.append(f"CORTO: in {p} reti diverse {sorted(nets)} ({', '.join(sorted(group))})")
            for g in group[1:]:
                self._union(group[0], g)
            if len(group) > 1:
                for g in group:
                    self._touch(g)
        for i, (p, q, net, _o) in enumerate(self.segs):
            for n, xy in self.xy.items():
                if _on_interior(xy, (p, q)):
                    if self.net[n] != net:
                        problems.append(f"CORTO: {n} ({self.net[n]}) sta su un filo di {net} in {xy}")
            for p2, q2, net2, _o2 in self.segs[i + 1:]:
                if _overlap((p, q), (p2, q2)) and net != net2:
                    problems.append(f"CORTO: fili sovrapposti di {net} e {net2} ({p}-{q} / {p2}-{q2})")
                if net == net2 and _cross((p, q), (p2, q2)):
                    problems.append(f"AMBIGUO: due fili di {net} si incrociano senza giunzione in "
                                    f"{_cross((p, q), (p2, q2))}")
                if net != net2:
                    for e in (p2, q2):
                        if _on_interior(e, (p, q)):
                            problems.append(f"CORTO: un filo di {net2} finisce su uno di {net} in {e}")
                    for e in (p, q):
                        if _on_interior(e, (p2, q2)):
                            problems.append(f"CORTO: un filo di {net} finisce su uno di {net2} in {e}")
        # T-junctions on the same net join islands; dots where >= 3 ends meet
        degree = {}
        for p, q, net, _o in self.segs:
            for e in (p, q):
                degree[(e, net)] = degree.get((e, net), 0) + 1
        for n, xy in self.xy.items():           # a node on the interior of a same-net wire
            for p, q, net, owner in self.segs:
                if net == self.net[n] and _on_interior(xy, (p, q)):
                    degree[(xy, net)] = degree.get((xy, net), 0) + 2
                    self._union(n, owner)
                    self._touch(n)
        for p, q, net, owner in self.segs:      # a wire END (an elbow too) on a same-net wire
            for e in (p, q):
                if e in by_pt:                  # a node: counted just above
                    continue
                for p2, q2, net2, owner2 in self.segs:
                    if net2 == net and _on_interior(e, (p2, q2)):
                        degree[(e, net)] = degree.get((e, net), 0) + 2
                        self._union(owner, owner2)
        for p, q, net, owner in self.segs:      # two wires of one net meeting at an elbow
            for e in (p, q):
                if e in by_pt:
                    continue
                for p2, q2, net2, owner2 in self.segs:
                    if net2 == net and e in (p2, q2) and owner2 != owner:
                        self._union(owner, owner2)
        for n in self.terminals.values():      # a terminal is one wire end of its own
            xy = self.xy[n]
            degree[(xy, self.net[n])] = degree.get((xy, self.net[n]), 0) + 1
        dots = sorted({xy for (xy, net), k in degree.items() if k >= 3})
        for xy in dots:
            self.d.add(elm.Dot(radius=0.09).at(xy))
        # (2b) a wire through a PART: a resistor, a diode, a box, a triangle. The
        # picture would show a connection, or hide one, that the netlist does not have
        own = {}
        for (ref, pin), n in self.terminals.items():
            own.setdefault(ref, set()).add(self.xy[n])
        for kind, geo, ref in self.bodies:
            if kind == "seg":
                body = geo
                for p, q, net, _o in self.segs:
                    if _overlap(body, (p, q)) or _cross(body, (p, q)):
                        problems.append(f"ATTRAVERSA: un filo di {net} passa su {ref} ({p}-{q})")
                    for e in (p, q):
                        if _on_interior(e, body):
                            problems.append(f"ATTRAVERSA: un filo di {net} finisce sul corpo di {ref} in {e}")
                for n, xy in self.xy.items():
                    if _on_interior(xy, body) and xy not in own.get(ref, ()):
                        problems.append(f"ATTRAVERSA: {n} sta sul corpo di {ref}")
            else:
                x0, y0, x1, y1 = geo
                for p, q, net, _o in self.segs:
                    if abs(p[1] - q[1]) < EPS and y0 + EPS < p[1] < y1 - EPS:
                        lo, hi = max(min(p[0], q[0]), x0), min(max(p[0], q[0]), x1)
                    elif abs(p[0] - q[0]) < EPS and x0 + EPS < p[0] < x1 - EPS:
                        lo, hi = max(min(p[1], q[1]), y0), min(max(p[1], q[1]), y1)
                    else:
                        continue
                    if hi - lo > EPS:
                        problems.append(f"ATTRAVERSA: un filo di {net} entra in {ref} ({p}-{q})")
        # (4) coverage: on a folded page, every part is drawn or expanded, once
        required = set(self.comp)
        if self.folded is not None:
            exp = self.folded["expanded"]
            required -= set(exp)
            for ref in sorted(self.placed & set(exp)):
                problems.append(f"DOPPIO: {ref} disegnato, ed e' anche espanso da {exp[ref]}")
            for tag in self.folded["instances"]:
                lt = {v: k for k, v in self.folded["pairs"].items()}.get(tag, tag)
                if lt not in self.boxes:
                    problems.append(f"OMESSO: il riquadro dell'istanza {lt} non disegnato")
            for tag, ports in self.boxes.items():
                for x, n in ports.items():
                    if n not in self.touched:
                        problems.append(f"PENZOLA: la porta {x} di {tag} ne' cablata ne' etichettata")
        for ref in sorted(required - self.placed):
            problems.append(f"OMESSO: {ref} non disegnato")
        for key in sorted(k for k in set(self.pin) - set(self.terminals) if k[0] in required):
            problems.append(f"OMESSO: piedino {key[0]}.{key[1]} ({self.pin[key]}) non disegnato")
        for ref in sorted(self.sym_refs):
            sym = set(symbol_pins(*self.comp[ref][1:]))
            done = {p for (r, p) in self.terminals if r == ref} | {p for (r, p) in self.nc if r == ref}
            if sym - done:
                problems.append(f"OMESSO: {ref}, piedini del simbolo non disegnati {sorted(sym - done)}")
        for key, n in sorted(self.terminals.items()):
            if n not in self.touched:
                problems.append(f"PENZOLA: {n} ne' cablato ne' etichettato")
        # (3) islands
        islands = {}
        for n in self.xy:
            islands.setdefault(self.net[n], {}).setdefault(self._find(n), []).append(n)
        names = {}
        for net, isl in sorted(islands.items()):
            for root, members in isl.items():
                tags = {self.named[m] for m in members if m in self.named}
                assert len(tags) <= 1
                names[root] = tags.pop() if tags else net
                if len(isl) > 1 and not tags and not any(m in self.named for m in members):
                    shown = ", ".join(sorted(m for m in members if not m.startswith("_"))[:6])
                    problems.append(f"ISOLA SENZA NOME: {net} e' disegnata in {len(isl)} pezzi, "
                                    f"e questo non ha etichetta ({shown})")
        # (5) readability: a text on a text, or on a wire or a part, is refused too -
        # the connections are right, and the page still cannot be read
        for a, b in self.text_overlaps():
            problems.append(f"ILLEGGIBILE: {a!r} sopra {b!r}")
        if problems:
            raise AssertionError(f"{len(problems)} problemi nel disegno:\n  " + "\n  ".join(problems))
        devices = {}
        for (ref, pin), n in self.terminals.items():
            devices.setdefault(ref, {})[pin] = names[self._find(n)]
        if self.folded is not None:
            devices = self._expand(devices, names)
        self.d.save(svg)
        self.d.save(pdf)
        if png:
            self.d.save(png, dpi=png_dpi)
        with open(manifest, "w") as f:
            json.dump({"source_netlist": self.source_rel, "devices": devices}, f,
                      indent=2, sort_keys=True)
            f.write("\n")
        n_isl = sum(len(v) for v in islands.values())
        return {"parts": len(self.placed), "terminals": len(self.terminals),
                "nc": len(self.nc), "nets": len(islands), "islands": n_isl,
                "dots": len(dots), "named": len(self.named)}

    def _expand(self, devices, names):
        """The manifest of a folded page: what is drawn, plus the template through
        the table into every instance, plus the left channel through the rule into
        the right. The nets of an expanded pin come from the DRAWING - the template's
        island, renamed by the rule (tag_X), a rail as it is, a port from the island
        its box's port sits on - and never from the netlist the manifest is then
        compared with."""
        F = self.folded
        tdev = {self.show(r): {p: self.show(x) for p, x in pins.items()}
                for r, pins in devices.items() if self.is_tmpl(r)}
        drawn = {r: pins for r, pins in devices.items() if not self.is_tmpl(r)}
        out = dict(drawn)
        rev = {rt: lt for lt, rt in F["pairs"].items()}
        boxed = {tag: {x: names[self._find(n)] for x, n in ports.items()}
                 for tag, ports in self.boxes.items()}

        def port(tag, x):
            if tag in boxed:
                return boxed[tag][x]
            return F["net_lr"](boxed[rev[tag]][x])

        for tag in F["instances"]:
            kinds = F["netmap"][tag]
            for t, pins in sorted(tdev.items()):
                i = F["table"][tag].get(t)
                if i is None:
                    continue
                assert i not in out, f"{i} gia' nel manifesto"
                row = {}
                for p, x in pins.items():
                    k = kinds[x][0]
                    row[p] = f"{tag}_{x}" if k == "int" else (x if k == "rail" else port(tag, x))
                out[i] = row
        for r, q in sorted(F["mirror"].items()):
            if r in drawn:
                assert q not in out, f"{q} gia' nel manifesto"
                out[q] = {p: F["net_lr"](n) for p, n in drawn[r].items()}
        return out

    def text_overlaps(self):
        """Pairs of texts whose boxes overlap on the rendered page (readability)."""
        fig = self.d.draw(show=False)
        mfig, ax = fig.fig, fig.ax
        # until save() the figure is matplotlib's default 6.4 x 4.8 in, and a text
        # (sized in points) would be measured against the wrong page: set it to A3
        mfig.set_size_inches(self.W * self.ipu, self.H * self.ipu)
        ax.set_position([0, 0, 1, 1])
        ax.set_xlim(0, self.W)
        ax.set_ylim(0, self.H)
        r = mfig.canvas.get_renderer()
        boxes = []
        for t in ax.texts:
            if not t.get_text().strip() or t.get_text() == "+":
                continue
            bb = t.get_window_extent(renderer=r)
            boxes.append((t.get_text(), bb))
        hits = []
        for i, (s, a) in enumerate(boxes):
            for u, b in boxes[i + 1:]:
                if a.overlaps(b):
                    hits.append((s, u))
        # a text over a wire or a two-terminal part reads as a crossed-out wire
        inv = ax.transData.inverted()
        lines = [(p, q, net) for p, q, net, _o in self.segs]
        lines += [(geo[0], geo[1], ref) for kind, geo, ref in self.bodies if kind == "seg"]
        for s, bb in boxes:
            if s == "+":                        # the polarity mark of an electrolytic
                continue
            (tx0, ty0), (tx1, ty1) = inv.transform([(bb.x0, bb.y0), (bb.x1, bb.y1)])
            sx, sy = (tx1 - tx0) * 0.04, (ty1 - ty0) * 0.12      # a little slack
            tx0, tx1, ty0, ty1 = tx0 + sx, tx1 - sx, ty0 + sy, ty1 - sy
            for (x0, y0), (x1, y1), what in lines:
                if abs(y0 - y1) < EPS and ty0 < y0 < ty1 and min(x0, x1) < tx1 and max(x0, x1) > tx0:
                    hits.append((s, f"filo/parte {what}"))
                    break
                if abs(x0 - x1) < EPS and tx0 < x0 < tx1 and min(y0, y1) < ty1 and max(y0, y1) > ty0:
                    hits.append((s, f"filo/parte {what}"))
                    break
            for (mx0, my0, mx1, my1), what in self.marks:
                if mx0 < tx1 and mx1 > tx0 and my0 < ty1 and my1 > ty0:
                    hits.append((s, what))
                    break
        return hits
