#!/usr/bin/env python3
"""
spice_export.py - emit an ngspice netlist from the SAME SKiDL Part/Net objects
that produce the KiCad netlist.

WHY THIS EXISTS
---------------
docs/limitations.md #2: SKiDL's native SPICE path (generate_netlist(tool=
"spice")) does not work with KiCad-library parts. The documented workaround is
generate_schematic() -> kicad-cli sch export netlist --format spice, which in
turn walks straight into limitation #3 (SKiDL silently drops Sim.Type /
Sim.Device) and #5 (unusable auto-placement) for every one of the ~40 parts in
this block.

Rather than fight that for a circuit this size, this module walks the SKiDL
object graph directly. It is a *reader* of circuits/preamp/*.py, never a second
definition of the topology: if a part is not registered here it simply does not
appear in the SPICE deck, and if a net is renamed in the SKiDL source it is
renamed in the deck automatically. AGENTS.md rule 2 (one-way sync, code ->
everything else) is preserved.

Usage: a circuit module calls spice_dev(part, prefix, pin_order, tail) as it
builds, then subckt(...) or deck(...) to emit.
"""

import re

# ---------------------------------------------------------------------------
# KiCad value strings are NOT SPICE-safe. THIS BIT SILENTLY GIVES A WRONG
# ANSWER IF YOU SKIP IT, so it is not a convenience.
#
#   KiCad / engineering notation : "1M"  = 1 megohm
#   SPICE                        : "1M"  = 1 MILLIohm      (1e-3)
#                                  "1MEG"= 1 megohm
#
# Found the hard way in this project: R_IN = "1M" (the E3 input-impedance
# resistor) exported as 1 milliohm. The .op, the DC sweep and the loop-gain
# runs were all unaffected, because each of those drives the input from a
# stiff voltage source - so the bug stayed invisible until the first AC run
# with a real source impedance, which came back 63 dB down. Nothing errored.
#
# SPICE is case-insensitive, so lowercase "m" (milli) needs no change; only
# an UPPERCASE "M" has to become "MEG".
# ---------------------------------------------------------------------------
_VAL = re.compile(r"^\s*([0-9]*\.?[0-9]+)\s*([a-zA-Z]*)\s*$")


def spice_value(v):
    """Translate a KiCad/SKiDL value string into an unambiguous SPICE value."""
    s = str(v)
    m = _VAL.match(s)
    if not m:
        raise ValueError(f"value {s!r} is not a plain number+suffix; refusing "
                         f"to guess its SPICE meaning")
    num, suf = m.group(1), m.group(2)
    if suf == "M" or suf.lower() == "meg":
        return num + "MEG"          # KiCad mega -> SPICE MEG
    if suf in ("u", "\u00b5", "U"):
        return num + "u"
    if suf == "":
        return num
    if suf in ("p", "n", "m", "k", "K", "G", "T", "f", "P", "N"):
        return num + suf
    raise ValueError(f"unknown unit suffix {suf!r} in value {s!r}")


# registry: list of (part, spice_prefix, [pin identifiers in SPICE order], tail)
_REGISTRY = []


def reset():
    _REGISTRY.clear()


def spice_dev(part, prefix, pin_order, tail="", suffix=""):
    """Register `part` for SPICE emission.

    prefix     - SPICE element letter ('R', 'C', 'Q', 'J', 'D', ...)
    pin_order  - pin numbers/names of the KiCad symbol, in SPICE node order
    tail       - everything after the nodes (value, model name, params)
    suffix     - appended to the SPICE element name.

    WHY `suffix` EXISTS (L22). A MULTI-UNIT part is one physical package
    holding several devices: the LS352 dual PNP of the input current mirror
    is one SOIC-8 with two transistors on one die. It is therefore ONE
    SKiDL Part with ONE reference - which is the whole point, because two
    Parts would place two packages on the board (that was NC-016) - but it
    must emit TWO SPICE elements. Without a suffix both lines would be
    named after the same ref, and a SPICE netlist with two elements called
    Q7 is not a netlist. The suffix makes them Q7A and Q7B.
    """
    if tail and prefix in ("R", "C", "L"):
        tail = spice_value(tail)
    _REGISTRY.append((part, prefix, list(pin_order), tail, suffix))
    return part


def _node(part, pin_id, gnd_names):
    pin = part[pin_id]
    net = pin.net
    if net is None:
        raise ValueError(f"{part.ref} pin {pin_id} is not connected to any net")
    name = net.name
    return "0" if name in gnd_names else name


def _lines(gnd_names):
    out = []
    for part, prefix, pin_order, tail, suffix in _REGISTRY:
        ref = part.ref
        # SKiDL ref already starts with the symbol's reference prefix (R1, C3,
        # Q7...). Use the SPICE prefix + the numeric/unique part of the ref so
        # e.g. a Device:Q_NPN with ref "Q7" becomes "QQ7" -> normalise to "Q7".
        name = ref if ref[0].upper() == prefix.upper() else prefix + ref
        name += suffix
        nodes = " ".join(_node(part, p, gnd_names) for p in pin_order)
        out.append(f"{name} {nodes} {tail}".rstrip())
    return sorted(out)


def subckt(name, ports, gnd_names=("GND",), header=""):
    """Return a .subckt block as a string. `ports` is a list of net names."""
    body = _lines(gnd_names)
    txt = []
    if header:
        txt += ["* " + l for l in header.strip().splitlines()]
    txt.append(f".subckt {name} " + " ".join(ports))
    txt += body
    txt.append(".ends " + name)
    return "\n".join(txt) + "\n"


def flat(gnd_names=("GND",)):
    return "\n".join(_lines(gnd_names)) + "\n"
