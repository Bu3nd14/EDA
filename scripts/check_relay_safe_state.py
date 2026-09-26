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
  MUTE    monostable. NC to ground on both poles (ADR-012), and since L29e
          a changeover in geometry iii (ADR-044): COM on the coupling cap's
          far side, NO on the jack, a bleed to ground on both.
  GAIN    monostable. NO to ground on both poles (ADR-004 / ADR-026).
  PERMIT  monostable. Since L35 (ADR-045) its coil is on a command of its
          OWN, not on the mute relays' nets: the timer releases it a delay
          after MUTE_CMD on insertion. Until L35 it had to share them
          (ADR-019 para. 2, ADR-027). Its contacts are judged by the proof.
  TRIM    bistable, TRIM1 and TRIM2 (ADR-027). Per pole: TRIM1's set throw is
          TRIM2's COM (the cascade), and the RESET throws sit at the TOP of
          the ladder - TRIM1 reset on the unattenuated node, a resistor down
          to TRIM2 reset (-6 dB), another down to TRIM2 set (-12 dB), and one
          down to ground. So reset = 0 dB, the state the part ships in.
  HOLD    monostable, HOLD3 / HOLD10 (L36). Judged by the gain proof.
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
  OUT OF MUTE = every monostable whose coil is on the mute command or on
  the permissive's command is energised (ADR-045: K6 still counts as "the
  mute", energised out of mute); every other monostable (the gain relays -
  and a permissive wired to a third net) is tried BOTH ways. In every such
  state no TRIM or SPIA coil pin may be reachable. THE WINDOW D of ADR-045 =
  the permissive still energised, the jack relays already released: the
  same must hold. IN MUTE = all of them de-energised: every TRIM and SPIA
  coil pin must be reachable - an interlock that also stops the trim from
  ever working would pass the first half alone. The opposite window (jack
  relays energised, permissive released) is what the timer's contract next
  to J4 excludes: declared, not provable on a netlist.

THE COMMANDS (ADR-045, ADR-028; L35). The mute relays' command and the
permissive's are two DIFFERENT nets, each with VRELAY on the coil's other
end, each on its own pin of the timer's harness (value MUTE_TIMER, pins as
TIMER_PINS); the mute switch (value MUTE) goes from RLY_RET to that harness'
switch pin. A permissive back on the mute command is the residue of L36
returning, and fails here by name.

THE GAIN INTERLOCK (L36, ADR-041 = road B of ADR-030). Role HOLD: the
auxiliary of a gain relay (HOLD3 on K1, HOLD10 on K5), coil on the same nets.
Walked with the same graph, with two things the trim proof does not need:
diodes and LEDs conduct anode -> cathode only, and the gain selector (the
switch whose value says GAIN) is set position by position against the
GAIN_KNOB table. Out of mute the powered gain coils must be exactly the
state, in every position; in mute exactly the knob's table, from every
state; and with every relay on the mute command caught BETWEEN throws (no
contact closed) and the knob where the state is, still exactly the state -
the race of ADR-030 at mute release, proved by structure because the
datasheet gives no figure to prove it by timing. Plus ADR-026 (K5 never
without K1), and the window D of ADR-045 (the permissive energised, the jack
relays released: still exactly the state).

THE PANEL LEDS (F9, F11, ADR-028; L35). The LEDs are panel parts: the board
carries their harness headers, found by value (PANEL_LEDS, the same maps as
LED_PINS in trim.py / gain_interlock.py). Walked with the same graph, a
header pin counts as lit when its net is reached from VRELAY. Asserted: the
return pin on RLY_RET; no anode net on a signal contact or on the audio
ground; the trim's three pins, for each of the four states of SPIA1 / SPIA2,
exactly the right one lit; the gain's, for each gain state, exactly the
right one; the mute pin lit in mute and dark out of mute AND in the window
D - it must read a contact, and never say "muted" with a jack connected.

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
TWO_TERMINAL = {("Device", p) for p in ("R", "D", "D_Schottky", "LED",
                                        "D_TVS")}
# Of those, the ones that conduct one way only (L36; see reach()).
DIRECTED = {("Device", p) for p in ("D", "D_Schottky", "LED")}

# L36, ADR-041 / ADR-026: what the GAIN selector commands, position by
# position (1 = 0 dB, 2 = +3 dB, 3 = +10 dB), as the set of gain steps whose
# coil it asks for. "3" is K1 (value "... GAIN"), "10" is K5 ("... GAIN10").
# The netlist must implement exactly this, in mute; and ADR-026 wants no
# position with "10" and without "3".
GAIN_KNOB = {1: frozenset(), 2: frozenset({"3"}), 3: frozenset({"3", "10"})}
GAIN_STATES = tuple(GAIN_KNOB.values())
GAIN_LED_DB = {frozenset(): 0, frozenset({"3"}): 3, frozenset({"3", "10"}): 10}

# L35, ADR-028 / F9 / F11: the panel LEDs' harness headers, by connector
# value: {pin: what that LED says}, and the return pin. The same maps as
# trim.LED_PINS and gain_interlock.LED_PINS; the two copies must agree.
PANEL_LEDS = {
    "TRIM_LED": ({"1": 0, "2": -6, "3": -12}, "4"),
    "GAIN_LED": ({"1": 0, "2": 3, "3": 10}, "4"),
    "MUTE_LED": ({"1": "MUTE"}, "2"),
}
# L35, ADR-045 / ADR-028 point 4: the mute timer's harness and its pins.
TIMER_CONN = "MUTE_TIMER"
TIMER_PINS = {"MUTE": "1", "PERMIT": "2", "SWITCH": "3"}

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
    # L36, ADR-030 road B: the auxiliary of a gain relay, HOLD3 on K1 and
    # HOLD10 on K5. Judged by the gain proof, like PERMIT by the trim's.
    "HOLD": {"grounded": None, "bistable": False},
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


def check_mute_geometry(components, relays, by_role, pin_net, findings):
    """ADR-044 (L29e): every mute pole is a CHANGEOVER in geometry iii.

    Read by intent, not by pin number:
      COM - the coupling cap's far side: a net that touches a capacitor, no
            connector, and has a resistor to ground (the cap-side bleed,
            kept by the user in L29e);
      NC  - ground (already asserted by check_monostable_role);
      NO  - the jack: a net that touches a connector's signal pin, no
            capacitor, and has a resistor to ground (the jack bleed: with
            the coil de-energised it is the jack's only way to ground,
            ADR-044 point 2, "Il bleed basta").
    And no mute contact other than the NO touches a jack net. Until L29e the
    jack itself sat on COM and NC grounded it (the shunt at the jack): this
    function is what makes that shape FAIL, since the NC-ground rule alone
    passes on both."""
    net_pins = defaultdict(list)
    for (ref, pin), net in pin_net.items():
        net_pins[net].append((ref, pin))
    res = resistors_between(components, pin_net)

    def kinds(net):
        out = set()
        for ref, pin in net_pins.get(net, ()):
            c = components.get(ref, {})
            if (c.get("lib"), c.get("part")) == ("Device", "C"):
                out.add("C")
            if c.get("lib") == "Connector_Generic" and pin == "1":
                out.add("JACK")
        return out

    def bleed(net):
        return any(res.get(frozenset((net, g))) for g in GROUND_NETS)

    report = []
    jacks = set()
    for ref in by_role["MUTE"]:
        pm = KNOWN_RELAYS[(relays[ref]["lib"], relays[ref]["part"])]
        for pole in pm["poles"]:
            where = f"{ref} {pole['name']}"
            cnet = pin_net.get((ref, pole["COM"]))
            onet = pin_net.get((ref, pole["NO"]))
            if cnet is None or onet is None:
                findings.append(
                    f"{where}: COM ({cnet!r}) o NO ({onet!r}) non collegato. "
                    f"ADR-044: ogni polo del mute e' un deviatore, COM al lato "
                    f"del condensatore e NO al jack.")
                continue
            if cnet in GROUND_NETS or onet in GROUND_NETS:
                continue   # already a finding of check_monostable_role
            kc, ko = kinds(cnet), kinds(onet)
            if kc != {"C"}:
                findings.append(
                    f"{where}: il COM (pin {pole['COM']}) sta su {cnet!r}, che "
                    f"tocca {sorted(kc) or 'nessun condensatore'}: deve essere "
                    f"il lato del condensatore d'uscita e non il jack "
                    f"(ADR-044, geometria iii). Se tocca il connettore, e' la "
                    f"derivazione al jack di prima di L29e.")
            if ko != {"JACK"}:
                findings.append(
                    f"{where}: il NO (pin {pole['NO']}) sta su {onet!r}, che "
                    f"tocca {sorted(ko) or 'nessun connettore'}: deve essere il "
                    f"jack, cosi' il segnale passa solo a bobina eccitata "
                    f"(ADR-044).")
            if not bleed(cnet):
                findings.append(
                    f"{where}: il lato del condensatore {cnet!r} non ha un "
                    f"resistore verso massa. Nel ms del trasferimento resta "
                    f"sospeso: L29d2 l'ha misurato col bleed, e l'utente l'ha "
                    f"tenuto in L29e.")
            if not bleed(onet):
                findings.append(
                    f"{where}: il jack {onet!r} non ha un resistore verso "
                    f"massa. A bobina diseccitata e' l'unica cosa che lo tiene "
                    f"a massa (ADR-044 punto 2, «Il bleed basta»).")
            jacks.add(onet)
    mute_set = set(by_role["MUTE"])
    for net in jacks:
        for ref, pin in net_pins[net]:
            if ref in mute_set:
                pm = KNOWN_RELAYS[(relays[ref]["lib"], relays[ref]["part"])]
                if pin not in {p["NO"] for p in pm["poles"]}:
                    findings.append(
                        f"{ref} pin {pin} sta sul jack {net!r}: sul jack puo' "
                        f"stare solo il NO di un deviatore (ADR-044).")
    if by_role["MUTE"]:
        report.append(f"mute ADR-044: {len(jacks)} jack su NO, lato "
                      f"condensatore su COM, NC a massa, bleed su entrambi i "
                      f"lati")
    return report


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


def reach(components, pin_net, energised, transfer=(), positions=None,
          latched=None):
    """The nets reachable from VRELAY in one state of the relays.

    energised  - monostables whose coil is on: COM-NO; the others COM-NC.
    transfer   - monostables caught BETWEEN throws (L36): no contact closed.
                 It is the instant of the race of ADR-030.
    positions  - {switch ref: position 1..n}: that switch's COM reaches the
                 throw of that position only. A switch not listed reaches
                 ALL its throws (any position), as the trim proof wants.
    latched    - {bistable ref: "NC" (reset) or "NO" (set)} (L35, the trim
                 LEDs' proof). A bistable not listed reaches BOTH throws.
    Diodes and LEDs conduct from anode (pin 2) to cathode (pin 1) only:
    since L36 the gain interlock rests on diodes that stop a return, and a
    walk that let current flow backwards through them would find paths the
    circuit does not have - and, worse, would pass a netlist whose diode is
    fitted the wrong way round, if the only paths were the backward ones.
    Resistors, coils and bidirectional TVS conduct both ways.
    """
    positions = positions or {}
    latched = latched or {}
    adj = defaultdict(set)

    def link(a, b, both=True):
        if a and b:
            adj[a].add(b)
            if both:
                adj[b].add(a)

    for ref, c in components.items():
        key = (c["lib"], c["part"])
        if key in DIRECTED:
            # pin 2 = A, pin 1 = K (KiCad Device:D, D_Schottky, LED)
            link(pin_net.get((ref, "2")), pin_net.get((ref, "1")), both=False)
        elif key in TWO_TERMINAL:
            link(pin_net.get((ref, "1")), pin_net.get((ref, "2")))
        elif key in KNOWN_SWITCHES:
            for com, throws in KNOWN_SWITCHES[key].items():
                if ref in positions:
                    throws = (throws[positions[ref] - 1],)
                for t in throws:
                    link(pin_net.get((ref, com)), pin_net.get((ref, t)))
        elif key in KNOWN_RELAYS:
            pm = KNOWN_RELAYS[key]
            link(*(pin_net.get((ref, p)) for p in pm["coil"]))
            for pole in pm["poles"]:
                com = pin_net.get((ref, pole["COM"]))
                if key in BISTABLE:
                    throws = ((latched[ref],) if ref in latched
                              else ("NC", "NO"))
                elif ref in transfer:
                    throws = ()
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


def command_relays(relays, by_role, pin_net):
    """(on_mute, on_permit): the monostables on the mute relays' coil nets
    and those on the permissive's (ADR-045, L35). Out of mute both sets are
    energised; in the window D only on_permit. With the permissive wrongly
    back on the mute command the two sets coincide - check_commands() says
    so - and every proof below still runs."""
    mono = [r for r in relays
            if (relays[r]["lib"], relays[r]["part"]) not in BISTABLE]
    mute_coils = {coil_nets(r, relays, pin_net) for r in by_role["MUTE"]}
    permit_coils = {coil_nets(r, relays, pin_net) for r in by_role["PERMIT"]}
    on_mute = sorted(r for r in mono
                     if coil_nets(r, relays, pin_net) in mute_coils)
    on_permit = sorted(r for r in mono
                       if coil_nets(r, relays, pin_net) in permit_coils)
    return on_mute, on_permit


def command_net(nets):
    """The command end of a coil whose other end is VRELAY, else None."""
    rest = [n for n in nets if n != SUPPLY_NET]
    if SUPPLY_NET in nets and len(rest) == 1 and rest[0] is not None:
        return rest[0]
    return None


def check_commands(components, relays, by_role, pin_net, findings):
    """ADR-045 / ADR-028 (L35): the two commands and the mute switch."""
    report = []
    if not by_role["MUTE"] or not by_role["PERMIT"]:
        return report
    mute_coils = {coil_nets(r, relays, pin_net) for r in by_role["MUTE"]}
    if len(mute_coils) != 1:
        return report                  # interlock() already says so
    mute_cmd = command_net(next(iter(mute_coils)))
    if mute_cmd is None:
        findings.append(
            f"i rele' di mute hanno la bobina su {next(iter(mute_coils))}: "
            f"attesi {SUPPLY_NET} da un lato e un comando dall'altro.")
        return report
    permit_cmd = set()
    for r in by_role["PERMIT"]:
        nets = coil_nets(r, relays, pin_net)
        if set(nets) == {SUPPLY_NET, mute_cmd}:
            findings.append(
                f"{r} (PERMIT): la bobina sta sul comando dei rele' di mute "
                f"{mute_cmd!r}. ADR-045: il permissivo ha un comando proprio, "
                f"rilasciato un ritardo dopo {mute_cmd!r} all'inserimento del "
                f"mute; sullo stesso comando rilascia insieme ai rele' del jack, "
                f"e guadagno e trim possono cambiare prima che i jack si "
                f"stacchino (il residuo di L36, fino a ~90 dB SPL di picco).")
            continue
        c = command_net(nets)
        if c is None:
            findings.append(f"{r} (PERMIT): la bobina sta su {nets}: attesi "
                            f"{SUPPLY_NET} e un comando proprio (ADR-045).")
            continue
        permit_cmd.add(c)
    conns = [ref for ref, c in components.items()
             if c["lib"] == "Connector_Generic" and c["value"] == TIMER_CONN]
    if len(conns) != 1:
        findings.append(
            f"connettore del temporizzatore del mute (valore {TIMER_CONN!r}) "
            f"atteso uno, trovati {conns}. ADR-028 / ADR-045: {mute_cmd!r} e il "
            f"comando del permissivo escono dalla scheda verso il "
            f"temporizzatore, che sta all'alimentatore.")
        return report
    j = conns[0]
    want = {"MUTE": {mute_cmd}, "PERMIT": permit_cmd}
    for role, pin in TIMER_PINS.items():
        if role == "SWITCH":
            continue
        net = pin_net.get((j, pin))
        if not want[role] or net not in want[role]:
            findings.append(
                f"{j} pin {pin}: atteso il comando "
                f"{'dei rele' + chr(39) + ' di mute' if role == 'MUTE' else 'del permissivo'}"
                f" {sorted(want[role])}, trovato {net!r}. Il temporizzatore "
                f"sfasa i due comandi (ADR-045): un comando che non arriva al "
                f"connettore non lo pilota nessuno.")
    sw_net = pin_net.get((j, TIMER_PINS["SWITCH"]))
    sws = [ref for ref, c in components.items()
           if (c["lib"], c["part"]) == ("Switch", "SW_SPST")
           and c["value"].upper() == "MUTE"]
    if len(sws) != 1:
        findings.append(f"interruttore di mute (Switch:SW_SPST, valore MUTE) "
                        f"atteso uno, trovati {sws} (F10, ADR-028).")
        return report
    sw = sws[0]
    ends = sorted([pin_net.get((sw, "1")), pin_net.get((sw, "2"))], key=str)
    if sw_net is None or sw_net in SINK_NETS or \
            ends != sorted([sw_net, "RLY_RET"], key=str):
        findings.append(
            f"{sw} (mute): i capi stanno su {ends}, attesi RLY_RET e il pin "
            f"{TIMER_PINS['SWITCH']} di {j} ({sw_net!r}). F10: l'interruttore e' "
            f"un ingresso del temporizzatore, che mette il mute se e' aperto "
            f"OPPURE se l'accensione non e' finita; in serie a un comando "
            f"perderebbe lo sfasamento di ADR-045.")
    report.append(f"comandi ADR-045: {mute_cmd} e {', '.join(sorted(permit_cmd))}"
                  f" distinti su {j} pin {TIMER_PINS['MUTE']}/"
                  f"{TIMER_PINS['PERMIT']}, interruttore {sw} su pin "
                  f"{TIMER_PINS['SWITCH']}; la finestra opposta (jack eccitati, "
                  f"permissivo rilasciato) la esclude il contratto di {j}, non "
                  f"la netlist")
    return report


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
    if not by_role["PERMIT"]:
        findings.append("ci sono rele' del trim ma nessun rele' PERMIT "
                        "(ADR-027): da dove passa l'interblocco?")

    # ADR-045 (L35): "out of mute" = the mute relays AND the permissive
    # energised; the permissive's command is checked by check_commands().
    on_mute, on_permit = command_relays(relays, by_role, pin_net)
    on = sorted(set(on_mute) | set(on_permit))
    free = sorted(r for r in relays if (relays[r]["lib"], relays[r]["part"])
                  not in BISTABLE and r not in on)

    def walk(energised):
        return reach(components, pin_net, energised)

    n_states = 0
    for combo in itertools.product((False, True), repeat=len(free)):
        n_states += 1
        extra = {r for r, e in zip(free, combo) if e}
        for label, energised in (("fuori mute", set(on) | extra),
                                 ("nella finestra D di ADR-045",
                                  set(on_permit) | extra)):
            hit = sorted(targets & walk(energised))
            if hit:
                findings.append(
                    f"INTERBLOCCO VIOLATO {label} (eccitati: "
                    f"{sorted(energised)}): da {SUPPLY_NET} si raggiungono le "
                    f"bobine del trim {hit}. F8: fuori mute il comando del "
                    f"trim non deve raggiungere i suoi rele' (NC-023, "
                    f"ADR-027); e nella finestra D i jack sono gia' staccati "
                    f"ma il permissivo no (ADR-045).")
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
                  f"fuori mute {', '.join(on)} eccitati (permissivo "
                  f"{', '.join(on_permit) or '-'}), {n_states} stati provati "
                  f"fuori mute, nella finestra D e in mute")
    return report


def gain_step(value):
    """'10' for a GAIN10 relay, '3' for the plain GAIN one (ADR-026)."""
    return "10" if "GAIN10" in value.upper() else "3"


def gain_interlock(components, relays, by_role, pin_net, findings):
    """The proof of ADR-041 on the netlist (L36). Returns report lines.

    For every consistent gain state S (0, +3, +10 dB: GAIN and its HOLD
    energised together) and every position of the gain selector:
      OUT OF MUTE  - the powered gain coils are exactly S: the knob moves
                     nothing, an ON coil holds itself and an OFF coil cannot
                     be reached (F5 as ADR-041 extends F8 to it);
      IN MUTE      - the powered coils are exactly GAIN_KNOB[position]: the
                     coils follow the knob, both ways;
      TRANSFER     - every relay on the mute command caught between throws
                     (no contact closed: the instant of ADR-030's race), with
                     the knob where the state is: the powered coils are
                     still exactly S. A coil that is on and unfed here drops
                     or not depending on figures the datasheet does not give.
    "Powered" = a coil net other than the return is reachable from VRELAY,
    and the coil's other net IS a return.
    """
    gains = by_role["GAIN"]
    if not gains:
        return []
    report = []
    by_step = {gain_step(relays[r]["value"]): r for r in gains}
    holds = {index_of(relays[r]["value"]): r for r in by_role["HOLD"]}
    if set(by_step) != {"3", "10"} or len(gains) != 2:
        findings.append(f"rele' GAIN attesi esattamente GAIN e GAIN10 "
                        f"(ADR-026), trovati {sorted(gains)}.")
        return report
    if set(holds) != {"3", "10"} or len(by_role["HOLD"]) != 2:
        findings.append(
            f"rele' ausiliari attesi HOLD3 su {by_step['3']} e HOLD10 su "
            f"{by_step['10']}, trovati {sorted(by_role['HOLD'])}. ADR-041 / "
            f"ADR-030 strada B: senza ausiliari il guadagno non si tiene fuori "
            f"mute, e il suo comando non e' interbloccato col mute.")
        return report
    for step in ("3", "10"):
        g, h = by_step[step], holds[step]
        if coil_nets(g, relays, pin_net) != coil_nets(h, relays, pin_net):
            findings.append(
                f"{h}: la bobina deve stare sulle stesse net di {g}, con la "
                f"stessa polarita' - {coil_nets(h, relays, pin_net)} contro "
                f"{coil_nets(g, relays, pin_net)}. Altrimenti la tenuta e i "
                f"LED seguono un rele' che non e' quello del guadagno.")
    coil_hi = {}
    for step in ("3", "10"):
        nets = coil_nets(by_step[step], relays, pin_net)
        hi = [n for n in nets if n not in SINK_NETS]
        lo = [n for n in nets if n in SINK_NETS]
        if len(hi) != 1 or len(lo) != 1 or hi[0] == SUPPLY_NET:
            findings.append(
                f"{by_step[step]}: la bobina sta su {nets}. ADR-041 la vuole "
                f"comandata dal lato alto come quelle del trim, fra una net "
                f"propria e il ritorno {SINK_NETS}: su {SUPPLY_NET}, o senza "
                f"ritorno, la prova non ha niente da dire.")
            return report
        coil_hi[step] = hi[0]

    sws = [r for r, c in components.items()
           if (c["lib"], c["part"]) in KNOWN_SWITCHES
           and "GAIN" in c["value"].upper()]
    if len(sws) != 1:
        findings.append(f"commutatore del guadagno atteso uno (valore con "
                        f"GAIN), trovati {sws} (F10, ADR-041).")
        return report
    sw = sws[0]
    npos = len(next(iter(KNOWN_SWITCHES[(components[sw]["lib"],
                                         components[sw]["part"])].values())))
    if npos != len(GAIN_KNOB):
        findings.append(f"{sw}: {npos} posizioni, la tabella ne vuole "
                        f"{len(GAIN_KNOB)}.")
        return report

    # ADR-045 (L35): out of mute = the mute relays and the permissive.
    on_mute, on_permit = command_relays(relays, by_role, pin_net)
    on = sorted(set(on_mute) | set(on_permit))

    def gain_on(state):
        return {x for s in state for x in (by_step[s], holds[s])}

    def powered(seen):
        return frozenset(s for s in ("3", "10") if coil_hi[s] in seen)

    def name(state):
        return f"{GAIN_LED_DB[frozenset(state)]:+d} dB" if state else "0 dB"

    n = 0
    for state in GAIN_STATES:
        for pos, knob in GAIN_KNOB.items():
            n += 1
            for label, cmd in (("fuori mute", on),
                               ("nella finestra D di ADR-045", on_permit)):
                out = powered(reach(components, pin_net,
                                    set(cmd) | gain_on(state), (), {sw: pos}))
                if out != state:
                    findings.append(
                        f"INTERBLOCCO DEL GUADAGNO VIOLATO {label}: stato "
                        f"{name(state)}, manopola in posizione {pos} "
                        f"({name(knob)}), bobine alimentate {sorted(out)} "
                        f"invece di {sorted(state)}. ADR-041: fuori mute la "
                        f"manopola non muove nulla, e una bobina accesa si "
                        f"tiene da se'; ADR-045: nemmeno coi jack gia' "
                        f"staccati e il permissivo ancora eccitato.")
            inm = powered(reach(components, pin_net, gain_on(state), (),
                                {sw: pos}))
            if inm != knob:
                findings.append(
                    f"in mute, dallo stato {name(state)} con la manopola in "
                    f"posizione {pos}, le bobine alimentate sono {sorted(inm)} "
                    f"invece di {sorted(knob)}: a mute inserito le bobine "
                    f"devono seguire la manopola, nei due versi (ADR-030 "
                    f"punto 1, ADR-041).")
            if "10" in inm and "3" not in inm:
                findings.append(
                    f"in mute, posizione {pos}: K5 alimentato senza K1 "
                    f"(ADR-026: K5 mai senza K1).")
            if knob == state:
                tr = powered(reach(components, pin_net, gain_on(state),
                                   set(on), {sw: pos}))
                if tr != state:
                    findings.append(
                        f"CORSA APERTA: con {', '.join(on)} in "
                        f"trasferimento (nessun contatto chiuso), stato e "
                        f"manopola a {name(state)}, le bobine alimentate sono "
                        f"{sorted(tr)} invece di {sorted(state)}. E' la corsa "
                        f"di ADR-030 al rilascio del mute: che la bobina cada "
                        f"o no dipende da induttanza, corrente di rilascio e "
                        f"tempo di trasferimento, che il datasheet non da'.")
    for pos, knob in GAIN_KNOB.items():
        if "10" in knob and "3" not in knob:
            findings.append(f"la tabella GAIN_KNOB comanda K5 senza K1 in "
                            f"posizione {pos} (ADR-026).")

    # The LEDs of the true gain state (ADR-030 point 2, twin of F9): on the
    # HOLD contacts, one lit per state, the right one, out of mute.
    hold_nets = set()
    for h in holds.values():
        pm = KNOWN_RELAYS[(relays[h]["lib"], relays[h]["part"])]
        for pole in pm["poles"]:
            for k in ("COM", "NC", "NO"):
                net = pin_net.get((h, pole[k]))
                if net in GROUND_NETS:
                    findings.append(f"{h} {pole['name']}: il contatto {k} e' "
                                    f"a massa audio: gli ausiliari non "
                                    f"toccano il segnale.")
                if net:
                    hold_nets.add(net)
    signal = set()
    for r in by_role["MUTE"] + by_role["GAIN"] + by_role["TRIM"]:
        pm = KNOWN_RELAYS[(relays[r]["lib"], relays[r]["part"])]
        for pole in pm["poles"]:
            for k in ("COM", "NC", "NO"):
                if pin_net.get((r, pole[k])):
                    signal.add(pin_net[(r, pole[k])])
    for net in sorted(hold_nets & signal):
        findings.append(f"la net {net!r} tocca un contatto di un ausiliario "
                        f"e uno di segnale (mute, guadagno o trim).")
    # L35: the LEDs are on the panel; their anodes are the pins of the
    # GAIN_LED header (PANEL_LEDS), and each must hang on a HOLD contact.
    leds = panel_pins(components, pin_net, "GAIN_LED", findings)
    if leds is not None:
        for pin, (anode, db) in sorted(leds.items()):
            if anode not in hold_nets:
                findings.append(
                    f"GAIN_LED pin {pin} ({db:+d} dB) sta su {anode!r}, che "
                    f"non e' un contatto degli ausiliari (ADR-030 punto 2: i "
                    f"LED leggono lo stato vero dai poli liberi degli "
                    f"ausiliari).")
        for state in GAIN_STATES:
            for label, cmd in (("fuori mute", on), ("in mute", ())):
                seen = reach(components, pin_net, set(cmd) | gain_on(state),
                             (), {sw: 1})
                lit = sorted(db for a, db in leds.values() if a in seen)
                if lit != [GAIN_LED_DB[frozenset(state)]]:
                    findings.append(
                        f"LED del guadagno ({label}): nello stato "
                        f"{name(state)} si accendono i pin di {lit} dB invece "
                        f"di [{GAIN_LED_DB[frozenset(state)]}]. Il LED deve "
                        f"dire lo stato vero (ADR-030 punto 2).")
    report.append(f"interblocco del guadagno: {by_step['3']}+{holds['3']}, "
                  f"{by_step['10']}+{holds['10']}, selettore {sw}; {n} coppie "
                  f"stato/posizione fuori mute e in mute, {len(GAIN_STATES)} "
                  f"trasferimenti di {', '.join(on)} con la manopola "
                  f"allo stato, e la finestra D; LED a pannello "
                  f"{len(leds or {})}")
    return report


def panel_pins(components, pin_net, value, findings):
    """{pin: (anode net, meaning)} of the panel LED header `value`, after
    asserting it exists once, its return is on RLY_RET and no anode sits on
    a sink. None if the header cannot be judged (a finding says why)."""
    conns = [ref for ref, c in components.items()
             if c["lib"] == "Connector_Generic" and c["value"] == value]
    if len(conns) != 1:
        findings.append(
            f"header dei LED a pannello {value!r} atteso uno, trovati {conns}."
            f" ADR-028: i LED stanno sul pannello, cablati a filo, e sulla "
            f"scheda resta il loro header.")
        return None
    j = conns[0]
    pins, ret = PANEL_LEDS[value]
    if pin_net.get((j, ret)) != "RLY_RET":
        findings.append(
            f"{j} ({value}) pin {ret}: il ritorno dei LED sta su "
            f"{pin_net.get((j, ret))!r}, non su RLY_RET: nessun LED si accende, "
            f"o si chiude sulla massa audio (P4).")
    out = {}
    for pin, meaning in pins.items():
        net = pin_net.get((j, pin))
        if net is None or net in SINK_NETS or net == SUPPLY_NET:
            findings.append(
                f"{j} ({value}) pin {pin}: l'anodo sta su {net!r}. Un LED "
                f"scollegato, in corto sul ritorno o sempre acceso non dice "
                f"nessuno stato.")
            continue
        out[pin] = (net, meaning)
    return out


def check_panel_leds(components, relays, by_role, pin_net, findings):
    """The trim's and the mute's panel LEDs (F9, F11; L35). The gain's are
    judged inside gain_interlock(), where the gain states are known."""
    report = []
    signal = set()
    for r in by_role["MUTE"] + by_role["GAIN"] + by_role["TRIM"]:
        pm = KNOWN_RELAYS[(relays[r]["lib"], relays[r]["part"])]
        for pole in pm["poles"]:
            for k in ("COM", "NC", "NO"):
                if pin_net.get((r, pole[k])):
                    signal.add(pin_net[(r, pole[k])])
    every = {}
    for value in PANEL_LEDS:
        pins = panel_pins(components, pin_net, value, findings)
        if pins is None:
            continue
        every[value] = pins
        for pin, (net, _m) in sorted(pins.items()):
            if net in signal or net in GROUND_NETS:
                findings.append(
                    f"{value} pin {pin}: l'anodo sta su {net!r}, una rete di "
                    f"segnale o la massa audio. Sul pannello passa solo la "
                    f"continua di bobine e LED (ADR-028).")
    on_mute, on_permit = command_relays(relays, by_role, pin_net)
    on = sorted(set(on_mute) | set(on_permit))

    # The trim: SPIA1 reset -> 0 dB (SPIA2 either way), SPIA1 set and SPIA2
    # reset -> -6 dB, both set -> -12 dB (ADR-027 para. 3). The TRIM relays
    # latch with their twins: same coil, same polarity (check_trim).
    spie = {index_of(relays[r]["value"]): r for r in by_role["SPIA"]}
    trims = {index_of(relays[r]["value"]): r for r in by_role["TRIM"]}
    tl = every.get("TRIM_LED")
    if tl is not None and set(spie) == {"1", "2"} and set(trims) == {"1", "2"}:
        for s1, s2 in itertools.product(("NC", "NO"), repeat=2):
            want = 0 if s1 == "NC" else (-6 if s2 == "NC" else -12)
            lat = {spie["1"]: s1, trims["1"]: s1, spie["2"]: s2,
                   trims["2"]: s2}
            for label, cmd in (("fuori mute", on), ("in mute", ())):
                seen = reach(components, pin_net, set(cmd), latched=lat)
                lit = sorted(m for n, m in tl.values() if n in seen)
                if lit != [want]:
                    findings.append(
                        f"LED del trim ({label}): con SPIA1 "
                        f"{'reset' if s1 == 'NC' else 'set'} e SPIA2 "
                        f"{'reset' if s2 == 'NC' else 'set'} si accendono i "
                        f"pin di {lit} dB invece di [{want}]. F9: il LED dice "
                        f"lo stato vero del trim.")
    # The mute: lit in mute, dark out of mute and in the window D.
    ml = every.get("MUTE_LED")
    if ml is not None and by_role["MUTE"]:
        (net, _m), = ml.values()
        for label, cmd, want in (("in mute", (), True),
                                 ("fuori mute", on, False),
                                 ("nella finestra D di ADR-045", on_permit,
                                  False)):
            seen = reach(components, pin_net, set(cmd))
            if (net in seen) != want:
                findings.append(
                    f"LED di mute {label}: {'spento' if want else 'acceso'}. "
                    f"F11: indica il mute inserito, letto da un contatto; "
                    f"acceso a jack collegati, o spento a mute inserito, dice "
                    f"il falso (ADR-028 punto 5).")
    if every:
        report.append(f"LED a pannello: {', '.join(sorted(every))}; trim 4 "
                      f"stati dei bistabili, mute in mute / fuori / finestra D")
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
    report = check_mute_geometry(components, relays, by_role, pin_net,
                                 findings)
    report += check_commands(components, relays, by_role, pin_net, findings)
    report += interlock(components, relays, by_role, pin_net, findings)
    report += gain_interlock(components, relays, by_role, pin_net, findings)
    report += check_panel_leds(components, relays, by_role, pin_net, findings)
    report += check_ldr(components, pin_net, findings)
    return findings, relays, report


# ---------------------------------------------------------------------------
# THE TIMER (L41b1, ADR-022 condition 1, ADR-048 point 6, ADR-049)
#
# ADR-022 admits a microcontroller off the signal path on three conditions;
# the first is that with the micro off, in reset, in brown-out or with its
# pins high-impedance every relay it commands is AT REST, and that THIS
# guardian extends to the command lines when the micro enters the topology.
# It entered in L41b1, on the supply board (psu.net). Run with --timer.
#
# What is asserted, by intent, on the netlist:
#   T1. every relay-command N-MOSFET (a 2N7002 whose drain is a coil command
#       or the standby switch's gate drive) has a resistor from its gate to
#       its source: a dead driver leaves it off;
#   T2. every net that joins a micro pin to such a gate, through resistors
#       and forward diodes with LESS than 1 MOhm in series (the cheapest
#       path), carries a resistor to RLY_RET / GND at the micro's end: the
#       ATtiny's tri-stated pins after a reset read as "at rest". A read-back
#       through >= 1 MOhm cannot lift a gate past a threshold (psu.py, R543)
#       and is not a command;
#   T3. a gate that a SUPPLY can pull up (V5, through a resistor, without a
#       micro pin in between) is the open-drain output of a comparator whose
#       + input is an RC timing node (a capacitor AND a resistor to the
#       return) - the delays D and D2 are hardware, not firmware;
#   T3b. such a delayed gate is reached from a micro pin (under 1 MOhm) ONLY
#       through its timing node or through another command gate - a request
#       wired straight onto it would skip the RC, and the delay with it;
#   T4. MUTE_CMD's gate can never stand above PERMIT_CMD's: a diode from the
#       first to the second (the jack relays cannot be energised before the
#       permissive, J4 contract);
#   T5. the timing node of PERMIT_CMD's comparator is charged, through
#       resistors and FORWARD diodes, from the net that drives MUTE_CMD's gate
#       (the permissive is held while the music is requested, whatever the
#       firmware does with PERMIT_REQ), and the timing node of the standby
#       switch from PERMIT_CMD's (the switch opens after the permissive).
# The timings themselves are simulated (docs/preamp/data/2026-09-26/L41b1/).
# ---------------------------------------------------------------------------
TIMER_SUPPLIES = ("V5", "VRELAY", "VRELAY_REG", "VPLUS", "VMINUS")
TIMER_RETURNS = ("RLY_RET", "GND")
TIMER_COMMANDS = ("MUTE_CMD", "PERMIT_CMD", "MAINS_COIL")


def _two_pin(components, pin_net, part):
    """[(ref, net pin 1, net pin 2)] for every two-pin part named `part`."""
    return [(r, pin_net.get((r, "1")), pin_net.get((r, "2")))
            for r, c in components.items() if c["part"] == part]


def _timer_walk(components, pin_net, start, stop):
    """Nets reachable from `start` through resistors (both ways) and diodes
    (anode -> cathode only), never through a net in `stop`."""
    edges = defaultdict(set)
    for _, a, b in _two_pin(components, pin_net, "R"):
        if a and b:
            edges[a].add(b)
            edges[b].add(a)
    for part in ("D", "D_Schottky"):
        # Device:D / D_Schottky: pin 1 = K, pin 2 = A
        for _, k, a in _two_pin(components, pin_net, part):
            if a and k:
                edges[a].add(k)
    seen, todo = {start}, [start]
    while todo:
        n = todo.pop()
        for m in edges[n]:
            if m not in seen:
                seen.add(m)
                if m not in stop:
                    todo.append(m)
    return seen


def _ohms(value):
    """'24.9k' -> 24900.0, '1M' -> 1e6 (KiCad: M is mega), '10' -> 10.0."""
    m = re.match(r"^\s*([0-9]*\.?[0-9]+)\s*([kKM]?)", value)
    if not m:
        return None
    return float(m.group(1)) * {"": 1, "k": 1e3, "K": 1e3, "M": 1e6}[m.group(2)]


def _series_r(components, pin_net, start, goal, stop):
    """The least series resistance from `start` to `goal` through resistors
    (both ways) and forward diodes (0 ohm), never through `stop`; None if
    there is no path."""
    import heapq
    edges = defaultdict(list)
    for r, a, b in _two_pin(components, pin_net, "R"):
        v = _ohms(components[r]["value"])
        if a and b and v is not None:
            edges[a].append((b, v))
            edges[b].append((a, v))
    for part in ("D", "D_Schottky"):
        for _, k, a in _two_pin(components, pin_net, part):
            if a and k:
                edges[a].append((k, 0.0))
    best, heap = {start: 0.0}, [(0.0, start)]
    while heap:
        d, n = heapq.heappop(heap)
        if n == goal:
            return d
        if d > best.get(n, float("inf")) or (n in stop and n != start):
            continue
        for m, w in edges[n]:
            if d + w < best.get(m, float("inf")):
                best[m] = d + w
                heapq.heappush(heap, (d + w, m))
    return None


COMMAND_MAX_OHMS = 1e6


def check_timer(components, pin_net):
    findings, report = [], []
    mcus = [r for r, c in components.items() if c["part"].startswith("ATtiny")]
    if len(mcus) != 1:
        findings.append("timer: attesi un microcontrollore ATtiny*, trovati %s"
                        % (mcus or "nessuno"))
        return findings, report
    mcu = mcus[0]
    mcu_nets = {n for (r, p), n in pin_net.items() if r == mcu}
    nfets = [r for r, c in components.items() if c["part"] == "2N7002"]
    # the command FETs: drain on a coil command, or on the switch's gate drive
    # (the drain of a 2N7002 that reaches a P-MOSFET's gate through a resistor)
    pgates = {pin_net.get((r, "1")) for r, c in components.items()
              if c["part"] in ("AO3401A",)}
    cmd = {}
    for q in nfets:
        d = pin_net.get((q, "3"))
        if d in TIMER_COMMANDS or _timer_walk(components, pin_net, d,
                                              set(TIMER_SUPPLIES)) & pgates:
            cmd[q] = (pin_net.get((q, "1")), pin_net.get((q, "2")), d)
    if not cmd:
        findings.append("timer: nessun MOSFET di comando trovato - il controllo "
                        "non puo' passare alla cieca")
        return findings, report
    resistors = _two_pin(components, pin_net, "R")
    caps = _two_pin(components, pin_net, "C")
    # comparator outputs (LM2903 symbol: 1 out A, 3 +A; 7 out B, 5 +B)
    comp_out = {}
    for r, c in components.items():
        if c["part"] == "LM2903":
            for out, plus in (("1", "3"), ("7", "5")):
                comp_out.setdefault(pin_net.get((r, out)), []).append(
                    (r, pin_net.get((r, plus))))

    def has_r(a, b_set):
        return any((x == a and y in b_set) or (y == a and x in b_set)
                   for _, x, y in resistors)

    def has_c(a, b_set):
        return any((x == a and y in b_set) or (y == a and x in b_set)
                   for _, x, y in caps)

    for q, (g, s, d) in sorted(cmd.items()):
        # T1
        if not has_r(g, {s}):
            findings.append("timer T1: %s (%s) non ha una resistenza gate-source: "
                            "un pilota morto lo lascia flottante" % (q, d))
        # T2: micro nets that reach this gate
        for n in sorted(mcu_nets):
            if n in TIMER_SUPPLIES or n in TIMER_RETURNS:
                continue
            rs = _series_r(components, pin_net, n, g,
                           set(TIMER_SUPPLIES) | set(TIMER_RETURNS))
            if rs is not None and rs < COMMAND_MAX_OHMS:
                if not has_r(n, set(TIMER_RETURNS)):
                    findings.append(
                        "timer T2: %s (pin di %s) raggiunge il gate di %s (%s) "
                        "senza un pull-down verso il ritorno: dopo un reset il "
                        "pin e' in alta impedenza (DS40002205A 16.3.1)"
                        % (n, mcu, q, d))
        # T3: a supply pull-up must land on a comparator output with an RC +
        ups = [x for x in ("V5",) if has_r(g, {x})]
        if ups:
            outs = comp_out.get(g, [])
            ok = [plus for _, plus in outs
                  if has_c(plus, set(TIMER_RETURNS)) and has_r(plus, set(TIMER_RETURNS))]
            if not ok:
                findings.append(
                    "timer T3: il gate di %s (%s) e' tirato su da V5 ma non e' "
                    "l'uscita open-drain di un comparatore con un RC sul "
                    "morsetto +: il ritardo non e' in hardware" % (q, d))
            else:
                report.append("timer: %s (%s) gate %s = comparatore su RC %s"
                              % (q, d, g, ok[0]))
                # T3b
                others = {x for x, _, _ in cmd.values()} - {g}
                stop = (set(TIMER_SUPPLIES) | set(TIMER_RETURNS) | set(ok)
                        | others)
                for n in sorted(mcu_nets - set(TIMER_SUPPLIES) - set(TIMER_RETURNS)):
                    rs = _series_r(components, pin_net, n, g, stop)
                    if rs is not None and rs < COMMAND_MAX_OHMS:
                        findings.append(
                            "timer T3b: %s (pin di %s) arriva al gate ritardato "
                            "di %s (%s) senza passare dal suo RC %s: il "
                            "ritardo si scavalca" % (n, mcu, q, d, ok[0]))
    by_drain = {d: g for q, (g, s, d) in cmd.items()}
    gm, gp = by_drain.get("MUTE_CMD"), by_drain.get("PERMIT_CMD")
    # T4
    diodes = [(a, k) for part in ("D", "D_Schottky")
              for _, k, a in _two_pin(components, pin_net, part)]
    if not gm or not gp or (gm, gp) not in diodes:
        findings.append("timer T4: nessun diodo dal gate di MUTE_CMD (%s) a quello "
                        "di PERMIT_CMD (%s): i jack potrebbero eccitarsi prima del "
                        "permissivo" % (gm, gp))
    else:
        report.append("timer: %s <= %s (diodo), i jack mai prima del permissivo"
                      % (gm, gp))

    # T5
    def timing_node(g):
        return [plus for _, plus in comp_out.get(g, [])]

    # the net driving MUTE_CMD's gate from the micro: the micro net that
    # reaches gm without a comparator output in between
    drivers = [n for n in mcu_nets if n not in TIMER_SUPPLIES + TIMER_RETURNS
               and (_series_r(components, pin_net, n, gm,
                              set(TIMER_SUPPLIES) | set(TIMER_RETURNS)) or 1e99)
               < COMMAND_MAX_OHMS]
    stop = set(TIMER_SUPPLIES) | set(TIMER_RETURNS)
    pt = timing_node(gp)
    if not drivers or not pt or not any(
            pt[0] in _timer_walk(components, pin_net, n, stop | {gm})
            for n in drivers):
        findings.append("timer T5: il nodo di temporizzazione di PERMIT_CMD (%s) "
                        "non si carica dalla richiesta di mute (%s): il "
                        "permissivo non e' tenuto mentre si chiede la musica"
                        % (pt, drivers))
    else:
        report.append("timer: %s si carica da %s" % (pt[0], ", ".join(drivers)))
    sw = [g for q, (g, s, d) in cmd.items() if d not in TIMER_COMMANDS]
    for g in sw:
        vt_ = timing_node(g)
        if not pt or not vt_ or vt_[0] not in _timer_walk(components, pin_net,
                                                          pt[0], stop):
            findings.append("timer T5: il nodo dell'interruttore di standby (%s) "
                            "non si carica da quello del permissivo (%s): "
                            "VRELAY potrebbe cadere prima di PERMIT_CMD"
                            % (vt_, pt))
        else:
            report.append("timer: %s (interruttore) si carica da %s"
                          % (vt_[0], pt[0]))
    return findings, report


def main_timer(path):
    components, pin_net = parse_netlist(path)
    if not components or not pin_net:
        print(f"ERRORE: non ho interpretato nulla in {path}")
        return 2
    findings, report = check_timer(components, pin_net)
    print(f"netlist : {path} (--timer)")
    for line in report:
        print(f"          {line}")
    if not findings:
        print("\nOK: col micro in reset o coi pin in alta impedenza ogni rele' "
              "che comanda e' a riposo (ADR-022 condizione 1); i ritardi D e D2 "
              "sono comparatori su RC, il permissivo e' tenuto dalla richiesta "
              "di mute, i jack non si eccitano prima del permissivo e "
              "l'interruttore di VRELAY si apre dopo il permissivo (ADR-049).")
        return 0
    print(f"\nFALLITO: {len(findings)} problemi\n")
    for f in findings:
        print("  " + f)
    return 1


def main(argv):
    if len(argv) == 3 and argv[1] == "--timer":
        return main_timer(Path(argv[2]))
    if len(argv) != 2:
        print("USAGE: check_relay_safe_state.py <netlist.net>\n"
              "       check_relay_safe_state.py --timer <psu.net>")
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
              "(mute -> jack staccati e lato condensatore a massa, ADR-044; "
              "guadagno -> R_g flottante), il "
              "trim si comanda solo a mute inserito (F8), il guadagno pure e "
              "si tiene da se' anche durante il trasferimento (ADR-041, L36); "
              "il permissivo ha un comando proprio, distinto da quello del "
              "mute, e guadagno e trim restano fermi nella finestra D "
              "(ADR-045); i LED a pannello dicono lo stato vero (F9, F11); "
              "le LDR del mute graduale "
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
