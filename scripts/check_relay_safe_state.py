#!/usr/bin/env python3
"""
check_relay_safe_state.py - verify, on the GENERATED netlist, that every
relay in the design fails in the direction the ADRs require when its coil
is de-energised - and, since L16, that the trim's bistable relays can be
commanded ONLY while the mute is inserted.

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

NC-023 (L16). F8 wants the trim to work ONLY with the mute inserted, through
an ELECTRICAL interlock, and the value to stay applied when the mute is
released. ADR-027 does it with bistable relays (G6KU-2F-Y) whose command
supply VTRIM comes through the normally-closed contacts of a permissive
relay, K6, whose coil sits on the mute command. A bistable has no
"de-energised state", so the de-energised-state rules below cannot judge it:
what can be judged is WHERE ITS COIL CAN GET CURRENT FROM, in each state of
the monostables. That is the interlock proof at the bottom of this file.

WHAT IT ASSERTS, AND WHY IT IS NOT WRITTEN AS PIN NUMBERS
---------------------------------------------------------
The datasheet pin maps live here as DATA, with their citations. The rules,
though, are written in terms of the INTENT the ADRs state - "the mute relay
shorts the output to ground when de-energised", "the trim's coils cannot be
reached out of mute" - and the pin numbers are looked up from the maps.
Writing the rules as "pin 7 must be grounded" would only move the assumption
somewhere else; written this way, the map and the intent have to agree, and
the NC-014 inversion breaks the assertions rather than slipping past them.

ROLES, read from the part's value string:
  MUTE    monostable. NC to ground on both poles (ADR-012).
  GAIN    monostable. NO to ground on both poles (ADR-004 / ADR-026).
  PERMIT  monostable. Coil on the SAME two nets as the mute relays
          (ADR-019 para. 2, ADR-027). Its contacts are judged by the proof.
  TRIM    bistable, TRIM1 and TRIM2 (ADR-027). Per pole: TRIM1's set throw is
          TRIM2's COM (the cascade), and the RESET throws sit at the TOP of
          the ladder - TRIM1 reset on the unattenuated node, a resistor down
          to TRIM2 reset (-6 dB), another down to TRIM2 set (-12 dB), and one
          down to ground. So reset = 0 dB, the state the part ships in.
  SPIA    bistable, SPIA1 / SPIA2 (F9). Coil on the SAME nets, same polarity,
          as TRIM1 / TRIM2; contacts never on a net a TRIM contact touches.

THE INTERLOCK PROOF. A graph of nets, walked from VRELAY:
  - edges: resistors, diodes, LEDs, TVS, a relay coil (pin to pin), the known
    rotary switch (each COM to ALL its throws: any position), and relay
    contacts by state - a monostable COM-NC de-energised, COM-NO energised;
    a bistable COM to BOTH throws (it may be in either state);
  - GND and RLY_RET are sinks: a path that reaches them is a return, not a
    supply, so the walk does not continue through them;
  - connectors and everything else are not traversed.
  OUT OF MUTE = every monostable whose coil is on the mute relays' two nets
  is energised; every other monostable (the gain relays - and a permissive
  wired to the wrong net) is tried BOTH ways. In every such state no TRIM or
  SPIA coil pin may be reachable. IN MUTE = those same relays de-energised:
  every TRIM and SPIA coil pin must be reachable - an interlock that also
  stops the trim from ever working would pass the first half alone.

THE GRADUATED MUTE (ADR-038, L29b2). Not a relay, but the same kind of
silent defect: two photoresistors per channel (Isolator:VTL5C, value
"... LDR_S_<ch>" / "... LDR_P_<ch>"). Asserted, by intent:
  - the SERIES cell sits between the channel's input connector (IN_<ch>) and
    the node that carries R_IN = 1M, block A's input - one point per channel
    that fades all three outputs;
  - the SHUNT cell sits from that same node to GND;
  - the LEDs are OUTSIDE the signal path (ADR-022): a net that touches a LED
    pin may touch only other LDR LED pins and the LDR_CMD harness;
  - one pair per channel. No LDR at all is a finding, not a pass: the check
    must not go blind.
A cell swapped end for end (series on the far side of R_IN, shunt on the
connector) or a LED hung on a signal net still generates, still simulates,
and fades nothing or leaks the drive into a 1 MOhm node.

Deliberately NOT reusing scripts/check_schematic.py's parser: that one
reads a FLAT SPICE netlist, this one reads the KiCad s-expression netlist.
They look similar and are not. Do not "consolidate" them.

USAGE
    /usr/bin/python3 scripts/check_relay_safe_state.py <netlist.net>

Exit code: 0 if every relay is safe, 1 on any finding, 2 on usage/IO error.
"""
import itertools
import re
import sys
from collections import defaultdict
from pathlib import Path

# ---------------------------------------------------------------------
# The pin maps, READ FROM THE DATASHEET - not deduced, not inherited.
#
# G6K-2F-Y: vendor/relays/omron/G6K/en-g6k.pdf, page 6, the G6K-2F-Y row,
# block "Terminal Arrangement / Internal Connections (TOP VIEW)".
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

# ---------------------------------------------------------------------
# G6KU-2F-Y (single-winding latching): vendor/relays/omron/G6K/en-g6k.pdf
# (K106-E1-11) page 7 and vendor/relays/omron/G6K-K106-E1-16/K106-E1.pdf
# (K106-E1-16) page 7, row G6KU-2F-Y. Read in L16 on three legs that agree:
# the rendered page; the SVG vector coordinates (armature 0.44 pt from the
# contact on its left, 3.39 pt from the one on its right, both poles, both
# revisions); the polylines of the KiCad symbol Relay:G6KU-2. The drawing is
# the RESET state, so for a bistable "NC" below means CLOSED AT RESET and
# "NO" CLOSED AT SET. Coil: SET = pin 1 +, RESET = pin 8 +.
# ---------------------------------------------------------------------
G6KU_2F_Y = {
    "coil": ("1", "8"),
    "poles": [
        {"name": "polo 1 (riga bassa 1-2-3-4)", "COM": "3", "NC": "2", "NO": "4"},
        {"name": "polo 2 (riga alta 8-7-6-5)", "COM": "6", "NC": "7", "NO": "5"},
    ],
}

# Which part in which library is a relay we know how to judge.
KNOWN_RELAYS = {("Relay", "G6K-2"): G6K_2F_Y, ("Relay", "G6KU-2"): G6KU_2F_Y}
BISTABLE = {("Relay", "G6KU-2")}

# Switch:SW_Rotary_4x3 (KiCad symbol): commons 13-16, throws 1-3, 4-6, 7-9,
# 10-12. For the proof only the grouping matters: each COM reaches its throws.
KNOWN_SWITCHES = {
    ("Switch", "SW_Rotary_4x3"): {"13": ("1", "2", "3"), "14": ("4", "5", "6"),
                                  "15": ("7", "8", "9"), "16": ("10", "11", "12")},
}
TWO_TERMINAL = {("Device", p) for p in ("R", "D", "LED", "D_TVS")}

# The intent, from the ADRs. `grounded` names the throw that must be tied to
# ground with the coil de-energised; the other throw must NOT be.
ROLES = {
    "MUTE": {
        "grounded": "NC", "bistable": False,
        "why": "ADR-012: un rele' di mute diseccitato mette l'uscita a massa, "
               "cosi' il progetto si guasta verso il SILENZIO quando "
               "l'alimentazione manca",
    },
    "GAIN": {
        "grounded": "NO", "bistable": False,
        "why": "ADR-004: un rele' di guadagno diseccitato lascia R_g "
               "flottante, cosi' il blocco riposa a guadagno unitario e "
               "nessun guasto di bobina puo' alzare il guadagno",
    },
    "PERMIT": {"grounded": None, "bistable": False},
    "TRIM": {"grounded": None, "bistable": True},
    "SPIA": {"grounded": None, "bistable": True},
}

# Isolator:VTL5C (KiCad symbol, read in L29b2): 1 = LED cathode, 2 = LED
# anode, 3 and 4 = the cell. The cell is symmetric; the LED is not.
KNOWN_LDR = {("Isolator", "VTL5C"): {"led": ("1", "2"), "cell": ("3", "4")}}
LDR_CHANNELS = ("L", "R")

GROUND_NETS = ("GND",)
SINK_NETS = ("GND", "RLY_RET")
SUPPLY_NET = "VRELAY"


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
    """MUTE, GAIN, PERMIT, TRIM or SPIA, read from the component's value."""
    up = value.upper()
    hits = [r for r in ROLES if r in up]
    if len(hits) == 1:
        return hits[0]
    return None


def index_of(value):
    """The trailing digit of TRIM1 / SPIA2, or None."""
    m = re.search(r"(\d+)\s*$", value)
    return m.group(1) if m else None


def coil_nets(ref, relays, pin_net):
    pm = KNOWN_RELAYS[(relays[ref]["lib"], relays[ref]["part"])]
    return tuple(pin_net.get((ref, p)) for p in pm["coil"])


def check_monostable_role(ref, comp, role, pinmap, pin_net, findings):
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


def resistors_between(components, pin_net):
    """{frozenset({net_a, net_b}): [ref, ...]} for every Device:R."""
    out = defaultdict(list)
    for ref, c in components.items():
        if (c["lib"], c["part"]) == ("Device", "R"):
            a, b = pin_net.get((ref, "1")), pin_net.get((ref, "2"))
            if a and b:
                out[frozenset((a, b))].append(ref)
    return out


def check_trim(components, relays, by_role, pin_net, findings):
    trims = {index_of(relays[r]["value"]): r for r in by_role["TRIM"]}
    if not by_role["TRIM"]:
        return
    if set(trims) != {"1", "2"} or len(by_role["TRIM"]) != 2:
        findings.append(
            f"rele' TRIM attesi esattamente TRIM1 e TRIM2, trovati "
            f"{sorted((relays[r]['value'], r) for r in by_role['TRIM'])} "
            f"(ADR-027: due bistabili in cascata).")
        return
    t1, t2 = trims["1"], trims["2"]
    res = resistors_between(components, pin_net)
    pm1 = KNOWN_RELAYS[(relays[t1]["lib"], relays[t1]["part"])]
    pm2 = KNOWN_RELAYS[(relays[t2]["lib"], relays[t2]["part"])]
    shapes = []
    for p1, p2 in zip(pm1["poles"], pm2["poles"]):
        n = {k: pin_net.get((t1, p1[k])) for k in ("COM", "NC", "NO")}
        m = {k: pin_net.get((t2, p2[k])) for k in ("COM", "NC", "NO")}
        where = f"{t1}/{t2} {p1['name']}"
        missing = [f"{t1}.{k}" for k, v in n.items() if v is None] + \
                  [f"{t2}.{k}" for k, v in m.items() if v is None]
        grounded = [f"{t1}.{k}" for k, v in n.items() if v in GROUND_NETS] + \
                   [f"{t2}.{k}" for k, v in m.items() if v in GROUND_NETS]
        if missing:
            findings.append(f"{where}: contatti non collegati {missing}.")
        if grounded:
            findings.append(f"{where}: contatti a massa {grounded}: un "
                            f"contatto del trim porta segnale.")
        cascade = n["NO"] is not None and n["NO"] == m["COM"]
        if not cascade:
            findings.append(
                f"{where}: il contatto di SET di {t1} (pin {p1['NO']}, "
                f"{n['NO']!r}) deve essere il COM di {t2} ({m['COM']!r}). "
                f"Se e' il RESET a finirci, il trim riposa attenuato, non a "
                f"0 dB - la famiglia di NC-014 (ADR-027).")
        ladder = (bool(res.get(frozenset((n["NC"], m["NC"]))))
                  and bool(res.get(frozenset((m["NC"], m["NO"]))))
                  and bool(res.get(frozenset((m["NO"], "GND")))))
        if not ladder:
            findings.append(
                f"{where}: la scala non scende dal RESET: attesi un resistore "
                f"da {t1} reset ({n['NC']!r}) a {t2} reset ({m['NC']!r}), uno "
                f"da {t2} reset a {t2} set ({m['NO']!r}) e uno da {t2} set a "
                f"GND. Reset deve essere il verso MENO attenuato: 0 dB su "
                f"{t1}, -6 dB su {t2} (ADR-027).")
        shapes.append((cascade, ladder, not missing, not grounded))
    if len(set(shapes)) > 1:
        findings.append(
            f"{t1}/{t2}: i due poli del trim sono cablati in modo diverso "
            f"({shapes[0]} contro {shapes[1]}): i canali sono identici per "
            f"contratto (T3), e poli diversi sono la forma di NC-014.")

    # SPIA: same coil, same polarity; contacts off the signal.
    trim_contact_nets = set()
    for t in (t1, t2):
        pm = KNOWN_RELAYS[(relays[t]["lib"], relays[t]["part"])]
        for pole in pm["poles"]:
            for k in ("COM", "NC", "NO"):
                if pin_net.get((t, pole[k])):
                    trim_contact_nets.add(pin_net[(t, pole[k])])
    spie = {index_of(relays[r]["value"]): r for r in by_role["SPIA"]}
    if set(spie) != {"1", "2"} or len(by_role["SPIA"]) != 2:
        findings.append(
            f"rele' SPIA attesi esattamente SPIA1 e SPIA2 (F9, ADR-027), "
            f"trovati {sorted(by_role['SPIA'])}.")
        return
    for i in ("1", "2"):
        s, t = spie[i], trims[i]
        if coil_nets(s, relays, pin_net) != coil_nets(t, relays, pin_net):
            findings.append(
                f"{s}: la bobina deve stare sulle stesse net di {t}, con la "
                f"stessa polarita' - {coil_nets(s, relays, pin_net)} contro "
                f"{coil_nets(t, relays, pin_net)}. Altrimenti il LED dice uno "
                f"stato che il trim non ha (F9).")
        pm = KNOWN_RELAYS[(relays[s]["lib"], relays[s]["part"])]
        for pole in pm["poles"]:
            for k in ("COM", "NC", "NO"):
                net = pin_net.get((s, pole[k]))
                if net in trim_contact_nets or net in GROUND_NETS:
                    findings.append(
                        f"{s} {pole['name']}: il contatto {k} sta su {net!r}, "
                        f"una net di segnale del trim o la massa audio. Le "
                        f"spie non toccano il segnale.")


def interlock(components, relays, by_role, pin_net, findings):
    """The proof of F8 on the netlist. Returns a list of report lines."""
    targets = set()
    for r in by_role["TRIM"] + by_role["SPIA"]:
        for net in coil_nets(r, relays, pin_net):
            if net is not None:
                targets.add(net)
    if not targets:
        return []
    report = []
    if not by_role["MUTE"]:
        findings.append("ci sono rele' del trim ma nessun rele' di MUTE: "
                        "l'interblocco di F8 non ha un comando da cui partire.")
        return report
    mute_coils = {coil_nets(r, relays, pin_net) for r in by_role["MUTE"]}
    if len(mute_coils) != 1:
        findings.append(f"i rele' di mute non condividono le net di bobina: "
                        f"{mute_coils}.")
        return report
    mute_coil = next(iter(mute_coils))

    for r in by_role["PERMIT"]:
        if coil_nets(r, relays, pin_net) != mute_coil:
            findings.append(
                f"{r} (PERMIT): la bobina sta su {coil_nets(r, relays, pin_net)}"
                f", non sulle net dei rele' di mute {mute_coil}. Il permissivo "
                f"deve seguire il comando del mute (ADR-019, ADR-027).")
    if not by_role["PERMIT"]:
        findings.append("ci sono rele' del trim ma nessun rele' PERMIT "
                        "(ADR-027): da dove passa l'interblocco?")

    on_mute = sorted(r for r in relays if (relays[r]["lib"], relays[r]["part"])
                     not in BISTABLE and coil_nets(r, relays, pin_net) == mute_coil)
    free = sorted(r for r in relays if (relays[r]["lib"], relays[r]["part"])
                  not in BISTABLE and r not in on_mute)

    def walk(energised):
        adj = defaultdict(set)

        def link(a, b):
            if a and b:
                adj[a].add(b)
                adj[b].add(a)

        for ref, c in components.items():
            key = (c["lib"], c["part"])
            if key in TWO_TERMINAL:
                link(pin_net.get((ref, "1")), pin_net.get((ref, "2")))
            elif key in KNOWN_SWITCHES:
                for com, throws in KNOWN_SWITCHES[key].items():
                    for t in throws:
                        link(pin_net.get((ref, com)), pin_net.get((ref, t)))
            elif key in KNOWN_RELAYS:
                pm = KNOWN_RELAYS[key]
                link(*(pin_net.get((ref, p)) for p in pm["coil"]))
                for pole in pm["poles"]:
                    com = pin_net.get((ref, pole["COM"]))
                    if key in BISTABLE:
                        throws = ("NC", "NO")
                    else:
                        throws = ("NO",) if ref in energised else ("NC",)
                    for t in throws:
                        link(com, pin_net.get((ref, pole[t])))
        seen, stack = {SUPPLY_NET}, [SUPPLY_NET]
        while stack:
            x = stack.pop()
            for y in adj[x]:
                if y not in seen:
                    seen.add(y)
                    if y not in SINK_NETS:
                        stack.append(y)
        return seen

    n_states = 0
    for combo in itertools.product((False, True), repeat=len(free)):
        n_states += 1
        energised = set(on_mute) | {r for r, e in zip(free, combo) if e}
        hit = sorted(targets & walk(energised))
        if hit:
            findings.append(
                f"INTERBLOCCO VIOLATO fuori mute (eccitati: "
                f"{sorted(energised)}): da {SUPPLY_NET} si raggiungono le "
                f"bobine del trim {hit}. F8: fuori mute il comando del trim "
                f"non deve raggiungere i suoi rele' (NC-023, ADR-027).")
    energised_in_mute = set()
    for combo in itertools.product((False, True), repeat=len(free)):
        energised = energised_in_mute | {r for r, e in zip(free, combo) if e}
        miss = sorted(targets - walk(energised))
        if miss:
            findings.append(
                f"in mute (eccitati: {sorted(energised)}) le bobine {miss} non "
                f"sono raggiungibili da {SUPPLY_NET}: un trim che non si "
                f"comanda mai non e' un interblocco, e' un guasto (F8).")
            break
    report.append(f"interblocco: {len(targets)} net di bobina bistabili, "
                  f"{len(on_mute)} rele' sul comando di mute "
                  f"({', '.join(on_mute)}), {n_states} stati provati fuori "
                  f"mute e in mute")
    return report


def check_ldr(components, pin_net, findings):
    """The graduated mute's cells, by intent (ADR-038, ADR-022)."""
    ldrs = {ref: c for ref, c in components.items()
            if (c["lib"], c["part"]) in KNOWN_LDR}
    if not ldrs:
        findings.append(
            "nessuna LDR del mute graduale (Isolator:VTL5C) nella netlist. "
            "ADR-038 ne vuole due per canale: se sono sparite, e' una modifica "
            "di topologia da dichiarare, non un controllo da saltare.")
        return []
    members = defaultdict(set)
    for (ref, pin), net in pin_net.items():
        members[net].add((ref, pin))
    report = []
    by = {}
    for ref, c in sorted(ldrs.items()):
        m = re.search(r"LDR_([SP])_([LR])\b", c["value"].upper())
        if not m:
            findings.append(
                f"{ref} ({c['value']!r}): una LDR deve dire nel valore se e' "
                f"la serie (LDR_S_<canale>) o la derivazione (LDR_P_<canale>).")
            continue
        if m.group(0) in by:
            findings.append(
                f"{ref}: {m.group(0)} c'e' due volte ({by[m.group(0)]}).")
            continue
        by[m.group(0)] = ref
    for ch in LDR_CHANNELS:
        s_ref, p_ref = by.get(f"LDR_S_{ch}"), by.get(f"LDR_P_{ch}")
        if not s_ref or not p_ref:
            findings.append(
                f"canale {ch}: manca la LDR "
                f"{'in serie' if not s_ref else 'verso massa'} (ADR-038: una "
                f"in serie e una verso massa per canale).")
            continue
        pm = KNOWN_LDR[(ldrs[s_ref]["lib"], ldrs[s_ref]["part"])]
        s_nets = [pin_net.get((s_ref, p)) for p in pm["cell"]]
        p_nets = [pin_net.get((p_ref, p)) for p in pm["cell"]]
        conn = [n for n in s_nets if n and any(
            components.get(r, {}).get("value") == f"IN_{ch}" and pin == "1"
            for r, pin in members[n])]
        r_in = [n for n in s_nets if n and any(
            components.get(r, {}).get("part") == "R"
            and components[r]["value"] == "1M" for r, _ in members[n])]
        if len(conn) != 1 or len(r_in) != 1 or conn == r_in:
            findings.append(
                f"{s_ref} (serie, canale {ch}): la cella deve stare fra il "
                f"connettore IN_{ch} e il nodo di R_IN = 1M (l'ingresso del "
                f"blocco A); sta su {s_nets}. ADR-038: un punto per canale "
                f"che silenzia tutte e tre le uscite.")
        elif sorted(p_nets, key=str) != sorted([r_in[0], "GND"], key=str):
            findings.append(
                f"{p_ref} (derivazione, canale {ch}): la cella deve andare "
                f"dal nodo di R_IN ({r_in[0]}) a GND; sta su {p_nets}.")
        else:
            report.append(f"mute LDR {ch}: {s_ref} {conn[0]} -> {r_in[0]}, "
                          f"{p_ref} {r_in[0]} -> GND")
    for ref, c in sorted(ldrs.items()):
        pm = KNOWN_LDR[(c["lib"], c["part"])]
        for p in pm["led"]:
            n = pin_net.get((ref, p))
            if n is None:
                findings.append(f"{ref}: il pin del LED {p} non e' collegato.")
                continue
            bad = sorted(
                f"{r}.{pin}" for r, pin in members[n]
                if not ((r in ldrs and pin in pm["led"])
                        or components.get(r, {}).get("value") == "LDR_CMD"))
            if bad:
                findings.append(
                    f"{ref}: il LED (pin {p}) sta sulla rete {n}, che tocca "
                    f"{', '.join(bad)}. ADR-022: il comando dei LED sta fuori "
                    f"dal percorso del segnale, e un LED su una rete di "
                    f"segnale porta il comando dentro un nodo a 1 MOhm.")
    return report


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
        return findings, relays, []

    by_role = defaultdict(list)
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
        bistable = (comp["lib"], comp["part"]) in BISTABLE
        if bistable != ROLES[role]["bistable"]:
            findings.append(
                f"{ref} ({comp['value']!r}): il ruolo {role} vuole un rele' "
                f"{'bistabile' if ROLES[role]['bistable'] else 'monostabile'}"
                f", e {comp['part']} non lo e'. Un bistabile non ha uno stato "
                f"a riposo su cui fondare MUTE, GAIN o PERMIT; un monostabile "
                f"perde il trim all'uscita dal mute (F8).")
            continue
        by_role[role].append(ref)
        if ROLES[role]["grounded"] is not None:
            check_monostable_role(ref, comp, role, pinmap, pin_net, findings)
        for p in pinmap["coil"]:
            if pin_net.get((ref, p)) is None:
                findings.append(
                    f"{ref}: il pin di bobina {p} non e' collegato.")

    check_trim(components, relays, by_role, pin_net, findings)
    report = interlock(components, relays, by_role, pin_net, findings)
    report += check_ldr(components, pin_net, findings)
    return findings, relays, report


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

    findings, relays, report = check(components, pin_net)

    print(f"netlist : {path}")
    print(f"          {len(components)} componenti, {len(relays)} rele' noti")
    for ref in sorted(relays, key=lambda r: int(re.sub(r"\D", "", r) or 0)):
        c = relays[ref]
        print(f"          {ref}  {c['value']!r}  ruolo={role_of(c['value'])}")
    for line in report:
        print(f"          {line}")

    if not findings:
        print("\nOK: ogni rele' si guasta nel verso che le ADR richiedono "
              "(mute -> uscite a massa, guadagno -> R_g flottante), e il "
              "trim si comanda solo a mute inserito (F8); le LDR del mute graduale "
              "stanno dove ADR-038 le vuole, col comando fuori dal segnale.")
        return 0

    print(f"\nFALLITO: {len(findings)} problemi\n")
    for f in findings:
        print("  " + f)
    print("\nQuesto e' il difetto di NC-014 o di NC-023: fallisce in silenzio. "
          "Correggi la topologia, non questo controllo.")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
