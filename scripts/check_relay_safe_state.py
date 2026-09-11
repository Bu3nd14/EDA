#!/usr/bin/env python3
"""
check_relay_safe_state.py - verify, on the GENERATED netlist, that every
relay in the design fails in the direction the ADRs require when its coil
is de-energised.

WHY THIS EXISTS
---------------
NC-014. The G6K-2F-Y pin map used to be DEDUCED from the KiCad symbol
instead of read from the datasheet, and the deduction was half right: both
armatures rest on the pad immediately to the LEFT of their own COM, but the
two terminal rows are numbered in OPPOSITE directions - 1-2-3-4 along the
bottom and 8-7-6-5 along the top. So "NO = COM+1" is correct for pole 1 and
wrong for pole 2, and pole 2 carries the RIGHT channel.

What that produced was the worst shape of defect this project can have: at
power-on the right channel was NOT shorted to ground, so the turn-on
transient went straight out - into a pair of electrostatics, on the branch
ADR-012 was written to protect. Nothing anywhere would have said so. The
complementary error on the gain relay started the right channel at +10 dB
while the left started at 0 dB, against ADR-004.

A one-off verification cannot stop that from coming back. This can.

WHAT IT ASSERTS, AND WHY IT IS NOT WRITTEN AS PIN NUMBERS
---------------------------------------------------------
The datasheet pin map lives here as DATA, with its citation. The rules,
though, are written in terms of the INTENT the ADRs state - "the mute relay
shorts the output to ground when de-energised" - and the pin numbers are
looked up from the map. Writing the rules as "pin 7 must be grounded" would
only move the assumption somewhere else; written this way, the map and the
intent have to agree, and the NC-014 inversion breaks BOTH families of
assertion rather than one.

Deliberately NOT reusing scripts/check_schematic.py's parser: that one
reads a FLAT SPICE netlist, this one reads the KiCad s-expression netlist.
They look similar and are not. Do not "consolidate" them.

USAGE
    /usr/bin/python3 scripts/check_relay_safe_state.py <netlist.net>

Exit code: 0 if every relay is safe, 1 on any finding, 2 on usage/IO error.
"""
import re
import sys
from collections import defaultdict
from pathlib import Path

# ---------------------------------------------------------------------
# The pin map, READ FROM THE DATASHEET - not deduced, not inherited.
#
# vendor/relays/omron/G6K/en-g6k.pdf, page 6, the G6K-2F-Y row, block
# "Terminal Arrangement / Internal Connections (TOP VIEW)".
#
# Re-read at the source in L21 on three independent legs that agree:
#   - the rendered page at 1200 dpi, looked at;
#   - the SVG vector coordinates: at the height of the contact tips the
#     armature passes 0.44 pt from its NC contact and 3.39 pt from its NO
#     one - ratio 7.6:1 - on BOTH poles;
#   - the polylines of the KiCad symbol G6K-2, where the armature tip's x
#     is EXACTLY the NC contact's x (3.81 mm from the NO one).
# ---------------------------------------------------------------------
G6K_2F_Y = {
    "coil": ("1", "8"),
    # pole: (COM, NC, NO).  Note NC 2 = COM 3 minus one, but NC 7 = COM 6
    # PLUS one: that asymmetry is the whole of NC-014.
    "poles": [
        {"name": "polo 1 (riga bassa 1-2-3-4)", "COM": "3", "NC": "2", "NO": "4"},
        {"name": "polo 2 (riga alta 8-7-6-5)", "COM": "6", "NC": "7", "NO": "5"},
    ],
}

# Which part in which library is a relay we know how to judge.
KNOWN_RELAYS = {("Relay", "G6K-2"): G6K_2F_Y}

# The intent, from the ADRs. `grounded` names the throw that must be tied to
# ground with the coil de-energised; the other throw must NOT be.
ROLES = {
    "MUTE": {
        "grounded": "NC",
        "why": "ADR-012: un rele' di mute diseccitato mette l'uscita a massa, "
               "cosi' il progetto si guasta verso il SILENZIO quando "
               "l'alimentazione manca",
    },
    "GAIN": {
        "grounded": "NO",
        "why": "ADR-004: un rele' di guadagno diseccitato lascia R_g "
               "flottante, cosi' il blocco riposa a guadagno unitario e "
               "nessun guasto di bobina puo' alzare il guadagno",
    },
}

GROUND_NETS = ("GND",)


def parse_netlist(path):
    """Return (components, pin_net) from a KiCad s-expression netlist.

    components: {ref: {"value": str, "lib": str, "part": str}}
    pin_net:    {(ref, pin): netname}

    Strict on purpose: this reads only what it understands and the caller
    fails loudly if it understood nothing. A checker that shrugs at an
    unparsed file is decorative.
    """
    text = path.read_text()

    components = {}
    # `(comp` appears only inside the components section, so there is no need
    # to isolate it first - and trying to bracket the section by indentation
    # is exactly the kind of brittleness this checker should not have.
    for m in re.finditer(
        r'\(comp\b.*?\(ref "([^"]+)"\).*?\(value "([^"]*)"\)'
        r'.*?\(libsource\s*\(lib "([^"]*)"\)\s*\(part "([^"]*)"\)',
        text, re.S,
    ):
        components[m.group(1)] = {
            "value": m.group(2), "lib": m.group(3), "part": m.group(4),
        }

    # Split on the net headers rather than trying to match each net's closing
    # parenthesis. The first attempt used a look-ahead for "the next (net" and
    # silently dropped the LAST net in the file - which happened to be VRELAY,
    # every relay coil. The checker caught it only because it also asserts the
    # coil pins are connected; a checker that had trusted its own parser would
    # have reported a clean pass over a netlist it had not finished reading.
    pin_net = {}
    nets_section = text.split("(nets", 1)[-1]
    for chunk in re.split(r"\(net\s*\(code", nets_section)[1:]:
        m = re.search(r'\(name "([^"]*)"\)', chunk)
        if not m:
            continue
        name = m.group(1)
        for node in re.finditer(r'\(ref "([^"]+)"\)\s*\(pin "([^"]+)"\)',
                                chunk):
            pin_net[(node.group(1), node.group(2))] = name
    return components, pin_net


def role_of(value):
    """MUTE or GAIN, read from the component's value string."""
    up = value.upper()
    hits = [r for r in ROLES if r in up]
    if len(hits) == 1:
        return hits[0]
    return None


def check(components, pin_net):
    findings = []
    relays = {ref: c for ref, c in components.items()
              if (c["lib"], c["part"]) in KNOWN_RELAYS}

    if not relays:
        # Not a pass. A netlist with no relay is either the wrong netlist or
        # a topology change nobody told this checker about.
        findings.append(
            "nessun rele' noto nella netlist. Questo controllo esiste per i "
            "rele' di mute e guadagno: se sono spariti, e' una modifica di "
            "topologia da dichiarare, non un controllo da saltare.")
        return findings, relays

    for ref in sorted(relays):
        comp = relays[ref]
        pinmap = KNOWN_RELAYS[(comp["lib"], comp["part"])]
        role = role_of(comp["value"])
        if role is None:
            findings.append(
                f"{ref} ({comp['value']!r}): non so che ruolo abbia. Il "
                f"valore deve nominare uno fra {', '.join(sorted(ROLES))} - "
                f"il ruolo decide in che verso il rele' deve guastarsi.")
            continue

        grounded_throw = ROLES[role]["grounded"]
        other_throw = "NO" if grounded_throw == "NC" else "NC"
        shapes = []

        for pole in pinmap["poles"]:
            gpin, opin, cpin = (pole[grounded_throw], pole[other_throw],
                                pole["COM"])
            gnet = pin_net.get((ref, gpin))
            onet = pin_net.get((ref, opin))
            cnet = pin_net.get((ref, cpin))
            where = f"{ref} {pole['name']}"

            if gnet not in GROUND_NETS:
                findings.append(
                    f"{where}: il contatto {grounded_throw} (pin {gpin}) "
                    f"dovrebbe essere a massa e sta su {gnet!r}. "
                    f"{ROLES[role]['why']}.")
            if onet in GROUND_NETS:
                findings.append(
                    f"{where}: il contatto {other_throw} (pin {opin}) e' a "
                    f"massa e non deve esserlo - e' il verso opposto a quello "
                    f"che {role} richiede, cioe' NC-014 che rientra.")
            if cnet is None:
                findings.append(
                    f"{where}: il COM (pin {cpin}) non e' collegato a niente.")
            elif cnet in GROUND_NETS:
                findings.append(
                    f"{where}: il COM (pin {cpin}) e' a massa. Il COM porta "
                    f"il segnale (o R_g): a massa il polo non commuta nulla.")
            shapes.append((gnet in GROUND_NETS, onet in GROUND_NETS,
                           cnet not in GROUND_NETS and cnet is not None))

        if len(set(shapes)) > 1:
            # T3 / ADR-006: the two channels are identical by contract, and
            # one pole per relay serves each. Poles wired differently is the
            # exact shape NC-014 had.
            findings.append(
                f"{ref}: i due poli sono cablati in modo diverso "
                f"({shapes[0]} contro {shapes[1]}). I due canali sono "
                f"identici per contratto (T3 / ADR-006).")

        for cpin in pinmap["coil"]:
            if pin_net.get((ref, cpin)) is None:
                findings.append(
                    f"{ref}: il pin di bobina {cpin} non e' collegato.")

    return findings, relays


def main(argv):
    if len(argv) != 2:
        print("USAGE: check_relay_safe_state.py <netlist.net>")
        return 2
    path = Path(argv[1])
    if not path.is_file():
        print(f"ERRORE: file non trovato: {path}")
        return 2

    components, pin_net = parse_netlist(path)
    if not components or not pin_net:
        print(f"ERRORE: non ho interpretato nulla in {path} "
              f"({len(components)} componenti, {len(pin_net)} nodi). "
              f"E' una netlist KiCad?")
        return 2

    findings, relays = check(components, pin_net)

    print(f"netlist : {path}")
    print(f"          {len(components)} componenti, {len(relays)} rele' noti")
    for ref in sorted(relays):
        c = relays[ref]
        print(f"          {ref}  {c['value']!r}  ruolo={role_of(c['value'])}")

    if not findings:
        print("\nOK: ogni rele' si guasta nel verso che le ADR richiedono "
              "(mute -> uscite a massa, guadagno -> R_g flottante).")
        return 0

    print(f"\nFALLITO: {len(findings)} problemi\n")
    for f in findings:
        print("  " + f)
    print("\nQuesto e' il difetto di NC-014: fallisce in silenzio, e nel "
          "verso che manda il transitorio d'accensione sulle cuffie. "
          "Correggi la topologia, non questo controllo.")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
