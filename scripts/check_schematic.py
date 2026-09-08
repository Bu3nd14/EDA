#!/usr/bin/env python3
"""
check_schematic.py - verify a hand-laid-out schematic drawing against the
netlist generated from the canonical SKiDL source.

WHY THIS EXISTS
---------------
Readable analog schematics cannot be auto-placed. This was researched and
tested, not assumed - see docs/limitations.md #16. Every tool that does
automatic placement targets DIGITAL netlists, where dataflow dictates the
layout; analog readability lives in conventions (supplies top and bottom,
signal left to right, a current mirror drawn as a mirror) that encode the
designer's intent and are simply not present in the netlist.

So the drawing is laid out by hand, in code, with schemdraw. That buys a
text source that versions and diffs - but it introduces the risk the whole
repo is built to eliminate: the drawing silently drifting away from the
circuit it claims to describe.

You cannot auto-place. You CAN auto-verify.

The drawing script emits a connectivity manifest alongside its SVG. This
script compares that manifest to the netlist in BOTH directions:

  * every device and connection the drawing shows must exist in the netlist
    (the drawing may not invent connections)
  * every device in the netlist must appear in the drawing
    (the drawing may not quietly omit a device)

A mismatch is a FAILURE, not a warning. Drift stops being a silent risk
and becomes a red test.

MANIFEST FORMAT
---------------
    {
      "source_netlist": "spice/preamp/gain_block_flat.inc",
      "devices": {
        "Q106": {"C": "SRC", "B": "NREF", "E": "NTE"},
        "R107": {"1": "NTE",  "2": "VMINUS"}
      }
    }

Pin names must match the netlist's positional order for the device letter
(see PINOUTS below). Net names are compared case-insensitively, since SPICE
is case-insensitive about node names.

USAGE
-----
    /usr/bin/python3 scripts/check_schematic.py <manifest.json> <netlist.cir>

Exit codes:  0 = drawing matches the netlist
             1 = mismatch (details on stdout)
             2 = bad invocation / unreadable input
"""
import json
import re
import sys
from pathlib import Path

# Positional pin order per SPICE device letter. Only the device types this
# project actually uses; extend deliberately rather than guessing.
PINOUTS = {
    "R": ["1", "2"],
    "C": ["1", "2"],
    "L": ["1", "2"],
    "D": ["A", "K"],           # anode, cathode
    "Q": ["C", "B", "E"],      # BJT: collector, base, emitter
    "J": ["D", "G", "S"],      # JFET: drain, gate, source
    "M": ["D", "G", "S", "B"],  # MOSFET
    "V": ["P", "N"],
    "I": ["P", "N"],
}


def device_letter(refdes: str) -> str:
    """First alphabetic character decides the device type.

    SKiDL emits refdes like 'JQ110' for a JFET (the 'Q' is part of the
    generated name, not the type), so only the FIRST character counts.
    """
    return refdes[0].upper()


def parse_netlist(path: Path) -> dict:
    """Parse a flat SPICE netlist into {refdes: {pin: net}}.

    Deliberately strict: a device whose letter is not in PINOUTS, or which
    has fewer nodes than its pinout needs, is reported rather than skipped.
    Silently ignoring a line we do not understand is how a checker becomes
    decorative.
    """
    devices, unknown = {}, []
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith(("*", ".", "+")):
            continue
        parts = line.split()
        refdes = parts[0]
        letter = device_letter(refdes)
        pins = PINOUTS.get(letter)
        if pins is None:
            unknown.append(refdes)
            continue
        nodes = parts[1:1 + len(pins)]
        if len(nodes) < len(pins):
            unknown.append(f"{refdes} (nodi insufficienti)")
            continue
        devices[refdes.upper()] = {p: n.upper() for p, n in zip(pins, nodes)}
    return {"devices": devices, "unknown": unknown}


def compare(manifest: dict, netlist: dict) -> list:
    """Return a list of human-readable findings. Empty list == match."""
    findings = []
    drawn = {k.upper(): {p.upper(): v.upper() for p, v in d.items()}
             for k, d in manifest.get("devices", {}).items()}
    real = netlist["devices"]

    only_drawn = sorted(set(drawn) - set(real))
    only_real = sorted(set(real) - set(drawn))

    for ref in only_drawn:
        findings.append(
            f"INVENTATO   {ref}: disegnato ma assente dalla netlist")
    for ref in only_real:
        findings.append(
            f"OMESSO      {ref}: presente nella netlist ma non disegnato")

    for ref in sorted(set(drawn) & set(real)):
        for pin in sorted(set(drawn[ref]) | set(real[ref])):
            a = drawn[ref].get(pin)
            b = real[ref].get(pin)
            if a is None:
                findings.append(f"PIN MANCANTE {ref}.{pin}: netlist={b}")
            elif b is None:
                findings.append(f"PIN INVENTATO {ref}.{pin}: disegno={a}")
            elif a != b:
                findings.append(
                    f"DISCORDE    {ref}.{pin}: disegno={a} netlist={b}")
    return findings


def main(argv):
    if len(argv) != 3:
        print(__doc__.strip().split("USAGE")[-1])
        return 2
    manifest_path, netlist_path = Path(argv[1]), Path(argv[2])
    for p in (manifest_path, netlist_path):
        if not p.is_file():
            print(f"ERRORE: file non trovato: {p}")
            return 2

    manifest = json.loads(manifest_path.read_text())
    netlist = parse_netlist(netlist_path)

    print(f"disegno : {manifest_path}")
    print(f"netlist : {netlist_path}")
    print(f"          {len(netlist['devices'])} dispositivi nella netlist, "
          f"{len(manifest.get('devices', {}))} nel disegno")
    if netlist["unknown"]:
        # Not a failure by itself, but it must be visible: an unparsed line
        # is a device the checker is blind to.
        print(f"ATTENZIONE: righe non interpretate ({len(netlist['unknown'])}): "
              f"{', '.join(netlist['unknown'][:8])}")

    findings = compare(manifest, netlist)
    if not findings:
        print("\nOK: il disegno corrisponde alla netlist in entrambe le "
              "direzioni.")
        return 0

    print(f"\nFALLITO: {len(findings)} discordanze\n")
    for f in findings:
        print("  " + f)
    print("\nIl disegno e la netlist sono divergenti. Correggi il disegno "
          "(o la topologia), non questo controllo.")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
