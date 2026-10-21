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
libparts section); a symbol that `extends` another is followed.
"""
import json
import math
import os
import re

import matplotlib
matplotlib.use("Agg")
import schemdraw                      # noqa: E402
import schemdraw.elements as elm      # noqa: E402

SYMBOLS = "/Users/roberto/Applications/KiCad.app/Contents/SharedSupport/symbols"

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
        self._auto = 0
        # the page frame: the drawing's bounding box IS the page
        self._line((0, 0), (self.W, 0), FRAME, 0.5)
        self._line((self.W, 0), (self.W, self.H), FRAME, 0.5)
        self._line((self.W, self.H), (0, self.H), FRAME, 0.5)
        self._line((0, self.H), (0, 0), FRAME, 0.5)

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
        self.named[n] = text
        self._touch(n)

    def label(self, n, direction="right", length=0.8, text=None, size=None):
        """A net label at the end of a short stub: a named island."""
        net = self.net[n]
        text = text or net
        assert text == net, f"etichetta {text} su {n}, che sta su {net}"
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

    def gnd(self, n):
        assert self.net[n] == "GND", f"simbolo di massa su {n}, che sta su {self.net[n]}"
        self.d.add(elm.Ground(lead=False).theta(0).at(self.xy[n]).color(GNDCOL).scale(0.85))
        self._name(n, "GND")

    def ret(self, n):
        assert self.net[n] == "RLY_RET", f"simbolo RLY_RET su {n}, che sta su {self.net[n]}"
        self.d.add(elm.GroundSignal(lead=False).theta(0).at(self.xy[n]).color(RETCOL).scale(0.85))
        self._name(n, "RLY_RET")

    def rail(self, n, up=True, text=None, size=None):
        """A supply arrow with the net's name: a named island."""
        net = self.net[n]
        text = text or net
        assert text == net, f"rail {text} su {n}, che sta su {net}"
        x, y = self.xy[n]
        s = 1 if up else -1
        self._line((x, y), (x, y + 0.45 * s), NETCOL)
        self._line((x - 0.3, y + 0.45 * s), (x + 0.3, y + 0.45 * s), NETCOL, 1.1)
        self.text((x, y + 0.8 * s), text, size=size or self.fs, color=NETCOL)
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
        val = value_text(value, part) if extra is None else extra
        if getattr(self, "_value_override", None):
            val = self._value_override
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
                  "Fuse": self.fuse, "NetTie_2": self.nettie}[part]
            return fn(ref, p1, p2, side=side)
        finally:
            self._value_override = None

    def N(self, ref, net):
        """The drawn terminal of `ref` that sits on `net` (exactly one)."""
        got = [n for (r, p), n in self.terminals.items() if r == ref and self.net[n] == net]
        assert len(got) == 1, f"{ref} su {net}: {got}"
        return got[0]

    def zref(self, ref, anode, cathode, side=None):
        """A shunt reference (LM4040): drawn as a zener, K and A from its symbol;
        the other pins of the symbol must be unconnected, and are recorded so."""
        value, lib, part = self._part(ref)
        sym = symbol_pins(lib, part)
        byname = {nm: num for num, nm in sym.items()}
        a = self.term(ref, byname["A"], anode)
        k = self.term(ref, byname["K"], cathode)
        for num in sym:
            if num not in (byname["A"], byname["K"]):
                assert (ref, num) not in self.pin, f"{ref}.{num} e' collegato"
                self.nc.add((ref, num))
        self._two(ref, elm.Zener(), a, k, side,
                  extra=value + "  (" + ", ".join(f"{n} nc" for n in sorted(sym)
                                                  if n not in (byname["A"], byname["K"])) + ")")
        return a, k

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

    def relay_coil(self, ref, a1, a2, side="r", note=None):
        """The coil of a relay whose contacts are drawn elsewhere (same ref)."""
        value, lib, part = self.comp[ref]
        if ref not in self.placed:
            self._part(ref)
        A1, A2 = self.term(ref, "A1", a1), self.term(ref, "A2", a2)
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
        self._touch(A1)
        self._touch(A2)
        dx, ha = (0.6, "left") if side == "r" else (-0.6, "right")
        self.text((x + dx, m + 0.32), f"{ref} bobina", halign=ha)
        self.text((x + dx, m - 0.32), note or value, size=self.fs - 0.8, color=DIM, halign=ha)
        self.text((x + 0.55, top - 0.15), "A1", size=self.fs - 1.6, color=DIM, halign="left")
        self.text((x + 0.55, bot + 0.15), "A2", size=self.fs - 1.6, color=DIM, halign="left")
        return A1, A2

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
        # (4) coverage
        for ref in sorted(set(self.comp) - self.placed):
            problems.append(f"OMESSO: {ref} non disegnato")
        for key in sorted(set(self.pin) - set(self.terminals)):
            problems.append(f"OMESSO: piedino {key[0]}.{key[1]} ({self.pin[key]}) non disegnato")
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
        return hits
