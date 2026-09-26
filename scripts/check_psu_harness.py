#!/usr/bin/env python3
"""check_psu_harness.py - the harness between the two boards (L41a, ADR-048, P4).

Usage: check_psu_harness.py <preamp_audio.net> <psu.net>
Exit 0 if every harness agrees, 1 otherwise (and 2 on a usage error).

The audio board (circuits/preamp/preamp_audio.py) and the supply board
(circuits/preamp/psu.py) meet on four harnesses, each a connector on BOTH
boards, found by its VALUE (the ref may differ; the value is the contract):

    POWER       J1  1 VPLUS   2 GND   3 VMINUS   4 VRELAY
    RLY_RET     J2  1 RLY_RET
    LDR_CMD     J3  1 series anode  2 series cathode  3 shunt anode  4 shunt cathode
    MUTE_TIMER  J4  1 MUTE_CMD  2 PERMIT_CMD  3 MUTE_SW

A pin that lands on the wrong wire at the other end does not error anywhere:
each netlist is fine on its own, and the fault is between them. The classic
one is J1 pins 1 and 3 swapped, which puts -15 V on the + rail.

What is checked:
  1. each harness exists ONCE on each board, with the same pin count;
  2. audio side: the named pins sit on the named nets (VPLUS, GND, ...), and
     J3's four pins reach the LEDs 2e expects (series L anode, series R
     cathode, shunt L anode, shunt R cathode) - by device pin, not by net
     name, because SKiDL does not name merged nets reproducibly
     (limitations #23);
  3. supply side: the same named nets on the same pins, and they are what
     their name says - VPLUS / VMINUS on the OUT pin of a TPS7A4701 /
     TPS7A3301, MUTE_CMD and PERMIT_CMD each on the DRAIN of its own
     N-MOSFET whose source is RLY_RET, MUTE_SW pulled to a logic rail, and
     every TPS7A's thermal pad on its GND;
  4. (L41b1, ADR-049, NC-037) VRELAY is the DRAIN of a P-MOSFET - the
     standby switch - whose source is the OUT of a TPS7A4701; the timer's
     placeholder J509 TIMER_IO is gone, and the four requests (MUTE_REQ,
     PERMIT_REQ, MAINS_REQ, VRELAY_EN) come from the microcontroller; J3's
     two anodes are each the collector of a PNP (a current source), and its
     two cathodes return to GND through a resistor (J3's contract: "cathode
     end to GND at the source").

Parser: the same as scripts/check_relay_safe_state.py (2e), copied, not
imported, so that the two checkers cannot break each other.
"""
import re
import sys
from pathlib import Path

HARNESS = {
    "POWER": {"1": "VPLUS", "2": "GND", "3": "VMINUS", "4": "VRELAY"},
    "RLY_RET": {"1": "RLY_RET"},
    "LDR_CMD": {"1": "LDR_S_A", "2": "LDR_S_K", "3": "LDR_P_A", "4": "LDR_P_K"},
    "MUTE_TIMER": {"1": "MUTE_CMD", "2": "PERMIT_CMD", "3": "MUTE_SW"},
}
# The audio side's J3 by device pin (VTL5C: pin 2 LED anode, pin 1 cathode;
# preamp_audio.py, the J3 block). U101/U301 series cells, U102/U302 shunt.
LDR_AUDIO = {"1": ("U101", "2"), "2": ("U301", "1"),
             "3": ("U102", "2"), "4": ("U302", "1")}
# Supply side: which net must be the OUT of which regulator part. VRELAY is
# not in the list since L41b1: it comes through the standby switch (below).
REG_OUT = {"VPLUS": "TPS7A4701", "VMINUS": "TPS7A3301"}
SINKS = ("MUTE_CMD", "PERMIT_CMD")
# L41b1: the timer's requests, each driven by a pin of the microcontroller.
MCU_PART_PREFIX = "ATtiny"
REQUESTS = ("MUTE_REQ", "PERMIT_REQ", "MAINS_REQ", "VRELAY_EN")
# The KiCad symbols' pin numbers (read from the symbol libraries in L41b1):
# Transistor_FET 2N7002 / AO3401A: 1 G, 2 S, 3 D; Q_PNP_BEC (BC857): 3 C;
# dual BC847BS / BC857BS: C1 = 6, C2 = 3.
PNP_COLLECTORS = {"BC857": ("3",), "BC857BS": ("6", "3")}
P_MOSFETS = ("AO3401A",)


def parse_netlist(path):
    """(components, pin_net) - copied from check_relay_safe_state.py."""
    text = path.read_text()
    components = {}
    for m in re.finditer(
        r'\(comp\b.*?\(ref "([^"]+)"\).*?\(value "([^"]*)"\)'
        r'.*?\(libsource\s*\(lib "([^"]*)"\)\s*\(part "([^"]*)"\)',
        text, re.S,
    ):
        components[m.group(1)] = {
            "value": m.group(2), "lib": m.group(3), "part": m.group(4),
        }
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


def harness(components, pin_net, value, board, findings):
    refs = [r for r, c in components.items() if c["value"] == value]
    if len(refs) != 1:
        findings.append("%s: harness %s found %d times (%s), expected once"
                        % (board, value, len(refs), ", ".join(sorted(refs))))
        return None
    ref = refs[0]
    pins = {p: n for (r, p), n in pin_net.items() if r == ref}
    want = HARNESS[value]
    if set(pins) != set(want):
        findings.append("%s: %s (%s) connected pins %s, expected %s"
                        % (board, value, ref, sorted(pins), sorted(want)))
    return ref, pins


def pins_of_net(pin_net, net):
    return [(r, p) for (r, p), n in pin_net.items() if n == net]


def check_audio(components, pin_net, findings):
    for value, want in HARNESS.items():
        got = harness(components, pin_net, value, "audio", findings)
        if got is None:
            continue
        ref, pins = got
        for pin, name in want.items():
            net = pins.get(pin)
            if value == "LDR_CMD":
                dev = LDR_AUDIO[pin]
                if net is None or pin_net.get(dev) != net:
                    findings.append("audio: %s pin %s does not reach %s pin %s"
                                    % (ref, pin, dev[0], dev[1]))
            elif net != name:
                findings.append("audio: %s pin %s on %r, expected %r"
                                % (ref, pin, net, name))


def check_psu(components, pin_net, findings):
    for value, want in HARNESS.items():
        got = harness(components, pin_net, value, "psu", findings)
        if got is None:
            continue
        ref, pins = got
        for pin, name in want.items():
            if pins.get(pin) != name:
                findings.append("psu: %s pin %s on %r, expected %r"
                                % (ref, pin, pins.get(pin), name))
    # the rails are what their names say
    for net, part in REG_OUT.items():
        outs = [(r, p) for (r, p) in pins_of_net(pin_net, net)
                if components.get(r, {}).get("part", "").startswith(part)
                and p in ("1", "20")]
        if not outs:
            findings.append("psu: %s is not the OUT of any %s" % (net, part))
    # every TPS7A's thermal pad (21) on its own GND pin's net (7): both
    # datasheets say the pad is internally GND (SBVS204G, SBVS169D). L41a's
    # first draft put the TPS7A3301's pad on IN - RAW_M shorted to ground.
    for r, c in components.items():
        if c.get("part", "").startswith("TPS7A") and \
                pin_net.get((r, "21")) != pin_net.get((r, "7")):
            findings.append("psu: %s thermal pad on %r, its GND on %r (the pad "
                            "is internally GND)" % (r, pin_net.get((r, "21")),
                                                   pin_net.get((r, "7"))))
    # each command is the drain of its own low-side N-MOSFET to RLY_RET
    for net in SINKS:
        fets = [r for (r, p) in pins_of_net(pin_net, net)
                if components.get(r, {}).get("lib") == "Transistor_FET"
                and p == "3"]
        good = [r for r in fets if pin_net.get((r, "2")) == "RLY_RET"]
        if len(good) != 1:
            findings.append("psu: %s must be the drain of exactly one "
                            "N-MOSFET with its source on RLY_RET, found %s"
                            % (net, good or fets or "none"))
        # (two commands on ONE drain cannot happen in a netlist: a pin is on
        # one net only - so "exactly one each" already means two MOSFETs)
    # MUTE_SW must be an input with a pull-up, never a rail or RLY_RET itself
    if pin_net and "MUTE_SW" in set(pin_net.values()):
        pulls = [r for (r, p) in pins_of_net(pin_net, "MUTE_SW")
                 if components.get(r, {}).get("part") == "R"]
        if not pulls:
            findings.append("psu: MUTE_SW has no pull-up resistor")
    check_timer(components, pin_net, findings)


def check_timer(components, pin_net, findings):
    """L41b1: the standby switch, the micro's requests, the LDR drive."""
    # VRELAY: drain of a P-MOSFET whose source is a TPS7A4701's OUT
    sw = [r for (r, p) in pins_of_net(pin_net, "VRELAY")
          if components.get(r, {}).get("part") in P_MOSFETS and p == "3"]
    good = []
    for r in sw:
        src = pin_net.get((r, "2"))
        outs = [x for (x, p) in pins_of_net(pin_net, src)
                if components.get(x, {}).get("part", "").startswith("TPS7A4701")
                and p in ("1", "20")]
        if outs:
            good.append(r)
    if len(good) != 1:
        findings.append("psu: VRELAY must be the drain of exactly one P-MOSFET "
                        "whose source is the OUT of a TPS7A4701 (the standby "
                        "switch, NC-037), found %s" % (good or sw or "none"))
    # the placeholder is gone
    if any(c["value"] == "TIMER_IO" for c in components.values()):
        findings.append("psu: the placeholder TIMER_IO (J509) is still there")
    # the micro drives the four requests
    mcus = [r for r, c in components.items()
            if c.get("part", "").startswith(MCU_PART_PREFIX)]
    if len(mcus) != 1:
        findings.append("psu: expected one %s* microcontroller, found %s"
                        % (MCU_PART_PREFIX, mcus or "none"))
    else:
        for net in REQUESTS:
            if not [p for (r, p) in pins_of_net(pin_net, net) if r == mcus[0]]:
                findings.append("psu: %s is not driven by the micro %s"
                                % (net, mcus[0]))
    # J3: anodes on a PNP collector, cathodes to GND through a resistor
    for net in ("LDR_S_A", "LDR_P_A"):
        srcs = [r for (r, p) in pins_of_net(pin_net, net)
                if p in PNP_COLLECTORS.get(components.get(r, {}).get("part"), ())]
        if len(srcs) != 1:
            findings.append("psu: %s must be the collector of exactly one PNP "
                            "(the current source of its string), found %s"
                            % (net, srcs or "none"))
    for net in ("LDR_S_K", "LDR_P_K"):
        to_gnd = [r for (r, p) in pins_of_net(pin_net, net)
                  if components.get(r, {}).get("part") == "R"
                  and "GND" in (pin_net.get((r, "1")), pin_net.get((r, "2")))]
        if len(to_gnd) != 1:
            findings.append("psu: %s must return to GND through one resistor "
                            "(J3 contract), found %s" % (net, to_gnd or "none"))


def main(argv):
    if len(argv) != 3:
        print(__doc__.split("\n\n")[1], file=sys.stderr)
        return 2
    findings = []
    ca, pa = parse_netlist(Path(argv[1]))
    cp, pp = parse_netlist(Path(argv[2]))
    if not ca or not pa or not cp or not pp:
        print("FAIL: a netlist parsed empty - refusing to pass blind")
        return 1
    check_audio(ca, pa, findings)
    check_psu(cp, pp, findings)
    print("audio : %s (%d components)" % (argv[1], len(ca)))
    print("psu   : %s (%d components)" % (argv[2], len(cp)))
    if findings:
        for f in findings:
            print("FAIL: " + f)
        return 1
    print("OK: J1 POWER, J2 RLY_RET, J3 LDR_CMD and J4 MUTE_TIMER agree pin by "
          "pin on both boards; the rails come from their regulators and the "
          "two commands from two low-side sinks to RLY_RET (ADR-045, ADR-048); "
          "VRELAY through the standby switch, the requests from the micro, "
          "J3 from two PNP sources back to GND (ADR-049)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
