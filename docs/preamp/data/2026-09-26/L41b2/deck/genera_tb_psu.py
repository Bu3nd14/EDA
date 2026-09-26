#!/usr/bin/env python3
"""L41b2: the supply board WITH its timer hardware AND the firmware's waveforms.

Solo stdlib.
  /usr/bin/python3 genera_tb_psu.py --uscita <dir> --nome timer [--angolo min]
  /usr/bin/python3 genera_tb_psu.py --uscita <dir> --nome ldr [--cal <cal.json>] [--led max] [--v5 4.9] [--cima 12e-3]
  /usr/bin/python3 genera_tb_psu.py --uscita <dir> --nome rumore
  /usr/bin/python3 genera_tb_psu.py --uscita <dir> --nome seq --caso <caso> --uscite <core.csv> [--giro n]

COPIED from L41b1's generator (docs/preamp/data/2026-09-26/L41b1/deck/), which
stays as it was. L41b2 adds:
  --nome seq: ONE sequence case whose micro is the firmware core. The core's
    outputs (firmware/preamp_timer/test/ponte.c, CSV) become the set_ PWLs of
    MUTE_REQ / PERMIT_REQ / MAINS_REQ / VRELAY_EN (drv_ = 1 throughout: a
    running micro drives its pins), the MCP4822's dset_ / den_ PWLs (code x
    4.096 / 4096, shutdown when the core says so) and the micro's supply
    current (5 uA in STANDBY, 2 mA otherwise). The deck writes, with
    wrdata on a 100 us grid (linearize), what the micro's pins see, which
    ponte.c reads for the next pass. Iterated until the core's outputs no
    longer change: circuit and firmware then agree (corri_seq.sh).
    Declared differences from the timer deck, per case:
      - the rails' load is 56.6 ohm (15 V / 265 mA), not a current source:
        at a power-up a current source would drive a dead rail negative;
      - K501's contact (the toroid's mains) follows its coil: closed above
        8.4 V (70 %% of 12 V, ASSUMED - the G2RL datasheet is not in vendor/)
        after a 5 ms RC; the mains of both transformers follow the case's
        own envelope (a hole);
      - the front switch and SW3 are conductances driven by the case (1 S
        closed, 1 nS open);
      - .options temp=25: the core's t_c.
  --cima: the v4 table's top for the LDR deck (ADR-050: 12 mA; L41b1: 20 mA).

Copied from L41a's generator (docs/preamp/data/2026-09-26/L41a/deck/), which
stays as it was, and extended with the parts L41b1 adds. The same rules:
  - every part of psu.net becomes a SPICE element through the MAP below; a
    part the map does not know makes the generator REFUSE;
  - every case resets EVERY alteration it may touch first (limitations #34:
    an `alter` survives `destroy all`).

MODELS - declared, not vendor unless said. L41a's, unchanged (transformers,
regulators, comparator, LM4040, diodes, 2N7002 as MNGEN with VTO = 1.0 V - the
LOW end of a 2N7002's threshold, which is the worst case for D: MUTE_G's slow
fall releases the jack relays latest), plus:
  - regulators: the quiescent current is now per part (TPS7A4701 0.58 mA,
    SBVS204G; MCP1703 2 uA, L41a's figure) - L41a charged 1 mA to each,
    which only mattered once the standby budget was read off this bench;
  - comparator: + 55 uA per channel from its supply (SBOS589D, SAFETY.md);
  - ATtiny3216 (U509): BEHAVIOURAL. Each output (MUTE_REQ, PERMIT_REQ,
    MAINS_REQ, VRELAY_EN) is a 50 ohm driver to set x V5, switched off to
    HIGH IMPEDANCE by its drv_ source (a reset tri-states every output,
    DS40002205A sec. 16.3.1); every other pin is 1 GOhm. Supply current 2 mA
    running (ASSUMED, not read) or 5 uA in power-down (Table 36-5, 85 C max);
  - MCP4822 (U510): BEHAVIOURAL. Each output a 10 ohm driver to its set
    voltage, or in shutdown (den = 0) only its 500 kOhm to ground
    (DS20002249B sec. 4.1.3-4.1.4); 415 uA running, 3.3 uA shut down;
  - MCP6004 (U511): BEHAVIOURAL. DC gain 1e5, one pole at 10 Hz (GBW 1 MHz,
    DS20001733L), output clamped 25 mV inside the rails and limited to
    +-23 mA, 100 uA per amplifier. NO offset (+-4.5 mV max: the top-end
    calibration of ADR-049 takes it out) and NO noise (added by hand in the
    noise deck from the datasheet's 28 nV/rtHz);
  - BC847BS / BC857BS / BC857: models/bjt_npn|pnp generic QNGEN / QPGEN
    (IS 1e-16, BF 100, RB 10, RE 0.5): generic, declared - no beta roll-off
    at low current, no leakage, no self-heating;
  - AO3401A: MPGEN (models/mosfet_p/generic_pmos.lib) at W/L 28000 (~50 mOhm);
  - BAT54: a declared Schottky (0.3 V at 1 mA).
THE AUDIO BOARD AS A LOAD: L41a's (265 mA per rail; three jack coils on
MUTE_CMD, K6 on PERMIT_CMD, 42.4 mA of the rest to RLY_RET), plus the trim's
four bistable coils, 4 x 9.1 mA from VRELAY while K6 is released (ADR-027,
L16; NC-037), and J3's four LEDs: two VTL5C4 LEDs in series per string
(IS 2.8e-16 N 2 from models/optocoupler/vtl5c4_comportamentale.lib: 1.65 V at
20 mA typ; --led max: IS 2.47e-19, 2.0 V at 20 mA, the datasheet's max).
"""
import argparse
import json
import math
import os
import re

QUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(QUI, "..", "..", "..", "..", "..", ".."))
ap = argparse.ArgumentParser()
ap.add_argument("--net", default=os.path.join(REPO, "circuits", "preamp", "psu.net"))
ap.add_argument("--uscita", required=True)
ap.add_argument("--nome", choices=("timer", "ldr", "rumore", "seq"), required=True)
ap.add_argument("--caso", default=None)
ap.add_argument("--uscite", default=None)
ap.add_argument("--giro", type=int, default=1)
ap.add_argument("--cima", type=float, default=20e-3)
ap.add_argument("--angolo", choices=("nom", "min"), default="nom")
ap.add_argument("--cal", default=None)
ap.add_argument("--led", choices=("typ", "max"), default="typ")
ap.add_argument("--v5", type=float, default=5.0)
ARG = ap.parse_args()

I_RAIL = 0.265          # ADR-042, eight blocks
TSS = 2.0               # s of settling before any event (C_RAW at ~0.27 A)
TE = TSS                # the event: a positive zero crossing of the mains

# ---- the firmware's command law (ADR-049), the SAME numbers as psu.py -----
VREF_NOM, V5_NOM = 2.5, 5.0
R_REF = 24.9e3
R_A, R_C = 100e3, 22.1e3
DAC_FS = 2.048 * 2      # MCP4822, G = 2x
K_B, Q_E = 1.380649e-23, 1.602176634e-19

# The v4 profile (ADR-039, the contract next to J3): the points the table
# gives, per string. 10 nA of idle on both, never 0.
CIMA = ARG.cima       # ADR-050: 12 mA (L41b2); 20 mA in L41b1
PUNTI = [("S", "d0", CIMA), ("S", "d0.1", 0.2e-3), ("S", "d0.45", 4.5e-6),
         ("S", "d0.75", 0.19e-6), ("S", "riposo", 10e-9),
         ("P", "riposo", 10e-9), ("P", "d0.75", math.sqrt(10e-9 * CIMA)),
         ("P", "d1", CIMA),
         # the calibration's second point (ADR-049): 2 mA = 20 mV on the 10 ohm
         # sense, readable by the micro's ADC; the first is 20 mA itself
         ("S", "cal_2mA", 2e-3), ("P", "cal_2mA", 2e-3)]
TEMPS = (15, 25, 35, 45, 60)


def vt(tc):
    return K_B * (tc + 273.15) / Q_E


def legge(i, t_fw, cal=None):
    """DAC volts for LED current i, as the firmware computes it at the
    temperature it believes (t_fw): V_X = VREF + Vt ln(i / I_ref) (+ the
    calibration's offset and ohmic term), then the network inverted,
    quantised to 12 bits."""
    iref = (V5_NOM - VREF_NOM) / R_REF
    vx = VREF_NOM + vt(t_fw) * math.log(i / iref)
    if cal:
        vx += cal["off"] + cal["r_ohm"] * i
    ga, gc = 1 / R_A, 1 / R_C
    vdac = (vx * (ga + gc) - VREF_NOM * gc) / ga
    code = max(0, min(4095, round(vdac / DAC_FS * 4096)))
    return code * DAC_FS / 4096, code


def parse(path):
    """(components, pin_net) - the parser of check_relay_safe_state.py."""
    text = open(path).read()
    comps = {}
    for m in re.finditer(
            r'\(comp\b.*?\(ref "([^"]+)"\).*?\(value "([^"]*)"\)'
            r'.*?\(libsource\s*\(lib "([^"]*)"\)\s*\(part "([^"]*)"\)', text, re.S):
        comps[m.group(1)] = {"value": m.group(2), "lib": m.group(3), "part": m.group(4)}
    pin_net = {}
    for chunk in re.split(r"\(net\s*\(code", text.split("(nets", 1)[-1])[1:]:
        m = re.search(r'\(name "([^"]*)"\)', chunk)
        if m:
            for n in re.finditer(r'\(ref "([^"]+)"\)\s*\(pin "([^"]+)"\)', chunk):
                pin_net[(n.group(1), n.group(2))] = m.group(1)
    return comps, pin_net


def sval(v):
    """KiCad value -> SPICE (limitations #13: 'M' is mega in KiCad)."""
    m = re.match(r"^\s*([0-9]*\.?[0-9]+)\s*([a-zA-Z]*)", v)
    num, suf = m.group(1), m.group(2)
    if suf == "M":
        return num + "MEG"
    return num + {"u": "u", "n": "n", "p": "p", "k": "k", "m": "m", "": ""}.get(suf, suf)


def node(n):
    return "0" if n == "GND" else n.lower()


COMPS, PN = parse(ARG.net)


def pn(ref, pin):
    return node(PN.get((ref, pin), "nc_%s_%s" % (ref.lower(), pin)))


MCU_OUT = ("MUTE_REQ", "PERMIT_REQ", "MAINS_REQ", "VRELAY_EN")
# the timing parts whose values the min corner moves (the netlist gives the
# nominal; the corner is declared here and in the deck name)
ANGOLO = {"C528": 0.95, "R534": 0.99, "C529": 0.95, "R536": 0.99} if ARG.angolo == "min" else {}


def element(ref, c):
    part, val = c["part"], c["value"]
    k = ANGOLO.get(ref)
    if part == "R":
        v = sval(val) if k is None else "{%s*%g}" % (sval(val), k)
        return ["R%s %s %s %s" % (ref, pn(ref, "1"), pn(ref, "2"), v)]
    if part == "C":
        v = sval(val) if k is None else "{%s*%g}" % (sval(val), k)
        return ["C%s %s %s %s" % (ref, pn(ref, "1"), pn(ref, "2"), v)]
    if part == "C_Polarized":
        # ESR 30 mOhm, and the value derated -20 % (ADR-046: >= 1500 uF EFFECTIVE)
        return ["C%s %s %s_esr {0.8*%s}" % (ref, pn(ref, "1"), ref.lower(), sval(val)),
                "R%s_esr %s_esr %s 0.03" % (ref, ref.lower(), pn(ref, "2"))]
    if part == "D":
        return ["D%s %s %s D1N914" % (ref, pn(ref, "2"), pn(ref, "1"))]
    if part == "D_Schottky":
        mod = "DBAT54" if val == "BAT54" else "DSCH"
        return ["D%s %s %s %s" % (ref, pn(ref, "2"), pn(ref, "1"), mod)]
    if part == "D_Zener":
        return ["D%s %s %s DZ24" % (ref, pn(ref, "2"), pn(ref, "1"))]
    if part == "D_Bridge_+AA-":
        p, a, b, m = (pn(ref, x) for x in "1234")
        return ["D%sa %s %s DBR" % (ref, a, p), "D%sb %s %s DBR" % (ref, b, p),
                "D%sc %s %s DBR" % (ref, m, a), "D%sd %s %s DBR" % (ref, m, b)]
    if part == "2N7002":
        return ["M%s %s %s %s %s MNGEN W=2000u L=1u" % (ref, pn(ref, "3"), pn(ref, "1"),
                                                        pn(ref, "2"), pn(ref, "2"))]
    if part == "AO3401A":
        return ["M%s %s %s %s %s MPGEN W=28000u L=1u" % (ref, pn(ref, "3"), pn(ref, "1"),
                                                         pn(ref, "2"), pn(ref, "2"))]
    if part == "BC847":
        return ["Q%s %s %s %s QNGEN" % (ref, pn(ref, "3"), pn(ref, "1"), pn(ref, "2"))]
    if part == "BC857":        # Q_PNP_BEC: 1 B, 2 E, 3 C
        return ["Q%s %s %s %s QPGEN" % (ref, pn(ref, "3"), pn(ref, "1"), pn(ref, "2"))]
    if part in ("BC847BS", "BC857BS"):   # E1 1, B1 2, C2 3, E2 4, B2 5, C1 6
        mod = "QNGEN" if part == "BC847BS" else "QPGEN"
        return ["Q%sa %s %s %s %s" % (ref, pn(ref, "6"), pn(ref, "2"), pn(ref, "1"), mod),
                "Q%sb %s %s %s %s" % (ref, pn(ref, "3"), pn(ref, "5"), pn(ref, "4"), mod)]
    if part == "LM2903":
        v, g = pn(ref, "8"), pn(ref, "4")
        return ["X%sa %s %s %s %s %s CMPOD" % (ref, pn(ref, "3"), pn(ref, "2"), pn(ref, "1"), v, g),
                "X%sb %s %s %s %s %s CMPOD" % (ref, pn(ref, "5"), pn(ref, "6"), pn(ref, "7"), v, g)]
    if part == "MCP6004":
        v, g = pn(ref, "4"), pn(ref, "11")
        out = []
        for s, (o, n, p) in zip("abcd", (("1", "2", "3"), ("7", "6", "5"),
                                         ("8", "9", "10"), ("14", "13", "12"))):
            if ARG.nome in ("timer", "seq"):   # L41b2: seq is a transient too
                out.append("X%s%s %s %s %s %s %s OPA5" % (ref, s, pn(ref, p), pn(ref, n),
                                                           pn(ref, o), v, g))
            elif pn(ref, o) == pn(ref, n):
                # DC / noise decks: a section wired as a follower (out = -in)
                # is an ideal follower - its 1e5 of loop gain leaves 23 uV
                out.append("E%s%s %s 0 %s 0 1" % (ref, s, pn(ref, o), pn(ref, p)))
            else:
                # the reference loops: gain 1e3 (x ~97 of gm1 R_REF: loop
                # error 1e-5), smooth - with 1e5 Newton failed on some points
                out.append("X%s%s %s %s %s %s %s OPA5DC" % (ref, s, pn(ref, p), pn(ref, n),
                                                             pn(ref, o), v, g))
        return out
    if part == "MCP4822":
        v, g = pn(ref, "1"), pn(ref, "7")
        out = []
        for ch, pin in (("s", "8"), ("p", "6")):
            o = pn(ref, pin)
            out += ["B%s%s 0 %s I = V(den_%s)*(V(dset_%s) - V(%s,%s))/10" % (ref, ch, o, ch, ch, o, g),
                    "R%s%s_sh %s %s 500k" % (ref, ch, o, g)]
        out += ["B%sq %s %s I = 3.3u + 206u*(V(den_s) + V(den_p))" % (ref, v, g)]
        return out
    if part.startswith("ATtiny"):
        v5, g = pn(ref, "1"), pn(ref, "20")
        out = ["B%sq %s %s I = V(iq_mcu)" % (ref, v5, g)]
        for (r, p), n in sorted(PN.items()):
            if r != ref or p in ("1", "20"):
                continue
            if n in MCU_OUT:
                x = n.lower()
                out.append("B%s_%s 0 %s I = V(drv_%s)*(V(set_%s)*V(%s,%s) - V(%s,%s))/50"
                           % (ref, p, x, x, x, v5, g, x, g))
            else:
                out.append("R%s_%s %s %s 1G" % (ref, p, node(n), g))
        return out
    if part == "LM4040DBZ-2.5":
        return ["X%s %s %s SHUNT25" % (ref, pn(ref, "1"), pn(ref, "2"))]
    if part.startswith("TPS7A4701"):
        vset = {"TPS7A4701 15V": 15.0, "TPS7A4701 12V": 12.0}[val]
        # ANY-OUT: the grounded weights must give vset (checked here, from the netlist)
        w = {"4": 6.4, "5": 6.4, "6": 3.2, "8": 1.6, "9": 0.8, "10": 0.4, "11": 0.2, "12": 0.1}
        gnd = PN[(ref, "7")]
        got = 1.4 + sum(x for p, x in w.items() if PN.get((ref, p)) == gnd)
        assert abs(got - vset) < 1e-6, (ref, got, vset)
        return ["X%s %s %s %s en_%s REGP VSET=%g VDO=0.3 ILIM=1 IQ=0.58m" % (
                    ref, pn(ref, "15"), pn(ref, "1"), node(gnd), ref.lower(), vset),
                "VEN%s en_%s 0 pwl(0 1 1000 1)" % (ref, ref.lower())]
    if part.startswith("TPS7A3301"):
        # FB divider from the netlist: Vout = -1.176 * (1 + Rtop / Rbot)  [ASSUMED reference]
        fb = PN[(ref, "3")]
        rs = {r: COMPS[r]["value"] for (r, p), n in PN.items() if n == fb and COMPS[r]["part"] == "R"}
        top = [r for r in rs if PN[(r, "1")] == PN[(ref, "1")] or PN[(r, "2")] == PN[(ref, "1")]]
        bot = [r for r in rs if r not in top]
        rt, rb = (float(sval(rs[x[0]]).replace("k", "e3")) for x in (top, bot))
        vset = 1.176 * (1 + rt / rb)
        return ["X%s %s %s %s en_%s REGM VSET=%g VDO=0.3 ILIM=1 IQ=1m" % (
                    ref, pn(ref, "15"), pn(ref, "1"), pn(ref, "7"), ref.lower(), vset),
                "VEN%s en_%s 0 pwl(0 1 1000 1)" % (ref, ref.lower())]
    if part.startswith("MCP1703"):
        vset = ARG.v5
        return ["X%s %s %s %s en_%s REGP VSET=%g VDO=0.6 ILIM=0.25 IQ=2u" % (
                    ref, pn(ref, "1"), pn(ref, "3"), pn(ref, "2"), ref.lower(), vset),
                "VEN%s en_%s 0 pwl(0 1 1000 1)" % (ref, ref.lower())]
    if part == "G2RL-2A":
        return ["R%s_coil %s %s 360" % (ref, pn(ref, "A1"), pn(ref, "A2"))]
    if part in ("Fuse", "NetTie_2"):
        return ["R%s %s %s 1m" % (ref, pn(ref, "1"), pn(ref, "2"))]
    if part.startswith("Conn_01x"):
        return []           # harnesses: the stimuli below attach to their nets
    raise SystemExit("genera_tb_psu: part %s (%s) not in the map - refusing" % (ref, part))


LED_IS = {"typ": 2.8e-16, "max": 2.47e-19}[ARG.led]
VREF_SHUNT = 2.505 if ARG.angolo == "min" else 2.500

MODELS = r"""
.include {repo}/models/diodes/1n4148.lib
.include {repo}/models/mosfet_n/generic_nmos.lib
.include {repo}/models/mosfet_p/generic_pmos.lib
.include {repo}/models/bjt_npn/generic_npn.lib
.include {repo}/models/bjt_pnp/generic_pnp.lib
* declared generic models (L41a): bridge diode, Schottky, 24 V zener; L41b1: BAT54
.model DBR D(Is=1e-9 N=1.8 Rs=0.03)
.model DSCH D(Is=1e-6 N=1.1 Rs=0.05)
.model DZ24 D(Is=1e-12 N=1 Rs=1 BV=24 IBV=1m)
.model DBAT54 D(Is=2e-8 N=1.05 Rs=1)
* the VTL5C4 LED (models/optocoupler/vtl5c4_comportamentale.lib; --led max: 2.0 V at 20 mA)
.model DLEDV D(IS={led_is} N=2)

* behavioural positive / negative regulator: gm to VSET, clamped to [0, ILIM],
* dropout VDO, no reverse current, input current = output current + IQ
.subckt REGP in out gnd en VSET=15 VDO=0.3 ILIM=1 IQ=1m
Bo gnd out I = V(en)*min({{ILIM}}, max(0, 1000*(min({{VSET}}, V(in,gnd)-{{VDO}}) - V(out,gnd))))
Bi in gnd I = V(en)*min({{ILIM}}, max(0, 1000*(min({{VSET}}, V(in,gnd)-{{VDO}}) - V(out,gnd)))) + {{IQ}}*(V(in,gnd)>1)
Rl out gnd 1meg
.ends
.subckt REGM in out gnd en VSET=15 VDO=0.3 ILIM=1 IQ=1m
Bo out gnd I = V(en)*min({{ILIM}}, max(0, 1000*(min({{VSET}}, V(gnd,in)-{{VDO}}) - V(gnd,out))))
Bi gnd in I = V(en)*min({{ILIM}}, max(0, 1000*(min({{VSET}}, V(gnd,in)-{{VDO}}) - V(gnd,out)))) + {{IQ}}*(V(gnd,in)>1)
Rl out gnd 1meg
.ends
* behavioural open-drain comparator: output sinks when inn > inp, 1 us,
* high impedance with its supply below 2 V; 55 uA from its supply (L41b1)
.subckt CMPOD inp inn out vcc gnd
Bu u gnd V = 0.5*(1+tanh((V(inn)-V(inp))/1m)) * 0.5*(1+tanh((V(vcc,gnd)-2)/0.1))
Ru u uf 1k
Cu uf gnd 1n
Bs out gnd I = V(out,gnd)/50 * V(uf,gnd)
Rleak out gnd 1G
Bq vcc gnd I = 55u*(V(vcc,gnd)>1)
.ends
* behavioural LM4040-2.5 shunt
.subckt SHUNT25 k a
Bz k a I = max(0, V(k,a)-{vref})*20
.ends
* behavioural MCP6004 section: 1e5, pole 10 Hz (GBW 1 MHz), rails - 25 mV,
* +-23 mA, 100 uA; the internal node clamped to the rails (no wind-up)
.subckt OPA5 inp inn out vcc vee
Gin 0 n1 inp inn 1e-3
R1 n1 0 1e8
C1 n1 0 159p
Bcl n1 0 I = 0.1*ln(1+exp((V(n1)-V(vcc))/0.01)) - 0.1*ln(1+exp((V(vee)-V(n1))/0.01))
Bo o2 0 V = max(V(vee)+0.025, min(V(vcc)-0.025, V(n1)))
Bout 0 out I = max(-23m, min(23m, (V(o2)-V(out))/10))
Bq vcc vee I = 100u*(V(vcc,vee)>1)
.ends
* the same for the DC and noise decks, without the pole and with a smooth
* (tanh) saturation, so Newton converges: gain 1e5 at the centre, rails -25 mV
* (L41b1: the clamped version above sent every .op to the transient fallback)
.subckt OPA5DC inp inn out vcc vee
Bo o2 0 V = 0.5*(V(vcc)+V(vee)) + (0.5*V(vcc,vee)-0.025)*tanh(1e3*V(inp,inn)/(0.5*V(vcc,vee)-0.025))
Ro o2 out 10
Bq vcc vee I = 100u
.ends
"""


def mains(env, vn, va, reg, a, b, mid, tag):
    """Thevenin winding pair driven by env(t) * sin (mains 230 V x factor).
    L41b1: a 0 V sense in series with each EMF, for the standby power."""
    i_nom = va / 2.0 / vn if mid else va / vn
    voc = vn * (1 + reg)
    rs = (voc - vn) / i_nom
    vpk = voc * 2 ** 0.5
    out = []
    if mid:
        out += ["B%sa %sa_e %s V = V(%s)*%.4f*sin(2*pi*50*time)" % (a, a, node("GND"), env, vpk),
                "V%sa_sns %sa_e %sa_i 0" % (tag, a, a),
                "B%sb %s %sb_e V = V(%s)*%.4f*sin(2*pi*50*time)" % (a, node("GND"), a, env, vpk),
                "V%sb_sns %sb_e %sb_i 0" % (tag, a, a),
                "R%sa %sa_i %sa_l %.4f" % (a, a, a, rs), "L%sa %sa_l %s 100u" % (a, a, node(a)),
                "R%sb %sb_i %sb_l %.4f" % (a, a, a, rs), "L%sb %sb_l %s 100u" % (a, a, node(b))]
    else:
        out += ["B%s %s_e %s V = V(%s)*%.4f*sin(2*pi*50*time)" % (a, a, node(b), env, vpk),
                "V%s_sns %s_e %s_i 0" % (tag, a, a),
                "R%s %s_i %s_l %.4f" % (a, a, a, rs), "L%s %s_l %s 100u" % (a, a, node(a)),
                "R%s_float %s 0 10meg" % (a, node(b))]
    return out


# ============================================================ the timer deck
def pwl(*pts):
    # %.12g, not %g: %g wrote TE + 1 us as "2", a PWL that stepped nowhere
    # (ngspice: "non-increasing PWL time points"; limitations #30, L41b1)
    return " ".join("%.12g %.12g" % p for p in pts)


# micro outputs in a normal start: MAINS_REQ at 0, VRELAY_EN at 0.9 s, then
# MUTE_REQ and PERMIT_REQ at 1.0 s (the 13 ms of ADR-027 after VRELAY_EN:
# the firmware's, L41b2); DAC: series 20 mA, shunt 10 nA (music, d = 0)
DEF_SET = {"mains_req": pwl((0, 1), (1000, 1)),
           "vrelay_en": pwl((0, 0), (0.9, 0), (0.9001, 1), (1000, 1)),
           "mute_req": pwl((0, 0), (1.0, 0), (1.0001, 1), (1000, 1)),
           "permit_req": pwl((0, 0), (1.0, 0), (1.0001, 1), (1000, 1))}
DEF_DRV = pwl((0, 1), (1000, 1))


def timer_deck():
    righe = ["* L41b1 tb_psu timer (%s) - GENERATED by genera_tb_psu.py from %s" % (ARG.angolo, ARG.net),
             MODELS.format(repo=REPO, led_is=LED_IS, vref=VREF_SHUNT)]
    for ref in sorted(COMPS):
        righe += element(ref, COMPS[ref])
    for n in sorted(set(PN.values())):
        if n.startswith(("AC_", "T1_PRI", "T2_PRI")):
            righe.append("R_float_%s %s 0 1G" % (n.lower(), node(n)))
    righe += ["VENV env 0 pwl(0 1 1000 1)", "VENV1 env1 0 pwl(0 1 1000 1)"]
    righe += mains("env1", 15.0, 50, 0.08, "T1_SEC_A", "T1_SEC_B", True, "T1")
    righe += mains("env", 12.0, 5, 0.20, "T2_SEC_A", "T2_SEC_B", False, "T2")
    for x in MCU_OUT:
        x = x.lower()
        righe += ["VSET_%s set_%s 0 pwl(%s)" % (x, x, DEF_SET[x]),
                  "VDRV_%s drv_%s 0 pwl(%s)" % (x, x, DEF_DRV)]
    vs, cs = legge(20e-3, 25)
    vp, cp = legge(10e-9, 25)
    righe += ["VIQ iq_mcu 0 pwl(0 2m 1000 2m)",
              "VDEN_S den_s 0 pwl(0 1 1000 1)", "VDEN_P den_p 0 pwl(0 1 1000 1)",
              "VDSET_S dset_s 0 dc %.6f" % vs, "VDSET_P dset_p 0 dc %.6f" % vp]
    righe += [
        "IPLUS vplus 0 dc 0 pwl(0 0 0.5 %g)" % I_RAIL,
        "IMINUS 0 vminus dc 0 pwl(0 0 0.5 %g)" % I_RAIL,
        "RMUTECOIL vrelay mute_cmd %g" % (1315 / 3.0),
        "RPERMITCOIL vrelay permit_cmd 1315",
        "RRESTO vrelay rly_ret %g" % (12 / 0.0424),
        # the trim's bistables, driven while K6 is released (NC-037)
        "BTRIM vrelay rly_ret I = 0.0364*max(0, V(vrelay,rly_ret))/12"
        "*0.5*(1+tanh((V(permit_cmd,rly_ret)-6)/0.5))",
        "DLS1 ldr_s_a ls_mid DLEDV", "DLS2 ls_mid ldr_s_k DLEDV",
        "DLP1 ldr_p_a lp_mid DLEDV", "DLP2 lp_mid ldr_p_k DLEDV",
        "RSW3 mute_sw rly_ret 1",      # SW3 closed = music
        "RFRONT front_sw rly_ret 1",   # front switch on
        ".options reltol=1e-4 abstol=1e-10 vntol=1e-6",
        ".control",
        "set numdgt=15",
    ]
    for c in casi_timer():
        righe += c + ["destroy all"]
    righe += [".endc", ".end"]
    scrivi("tb_psu_timer_%s.cir" % ARG.angolo, righe)


def caso(nome, env="0 1 1000 1", env1=None, sets=None, drvs=None, extra=(), tf=None,
         misure=(), iq="0 2m 1000 2m", den="0 1 1000 1", front=1):
    """One case: every source the cases touch is reset, then this case's."""
    tf = tf or TE + 0.2
    sets = dict(DEF_SET, **(sets or {}))
    drvs = dict({x.lower(): DEF_DRV for x in MCU_OUT}, **(drvs or {}))
    out = ["* ---- %s ----" % nome,
           "alter @venv[pwl] = [ %s ]" % env,
           "alter @venv1[pwl] = [ %s ]" % (env1 or env),
           "alter @viq[pwl] = [ %s ]" % iq,
           "alter @vden_s[pwl] = [ %s ]" % den, "alter @vden_p[pwl] = [ %s ]" % den,
           "alter rfront = %g" % front]
    # EVERY alteration is reset first (limitations #34)
    out += ["alter @ven%s[pwl] = [ 0 1 1000 1 ]" % r.lower()
            for r in sorted(COMPS) if COMPS[r]["part"].startswith(("TPS7A", "MCP1703"))]
    c528 = float(sval(COMPS["C528"]["value"]).replace("n", "e-9")) * ANGOLO.get("C528", 1.0)
    out += ["alter cc528 = %.6g" % c528]
    for x in MCU_OUT:
        x = x.lower()
        out += ["alter @vset_%s[pwl] = [ %s ]" % (x, sets[x]),
                "alter @vdrv_%s[pwl] = [ %s ]" % (x, drvs[x])]
    out += list(extra) + ["echo CASO %s" % nome, "print @cc528[capacitance]"]
    out += ["tran 20u %g 0 20u uic" % tf]
    out += list(misure)
    return out


HIZ = pwl((0, 1), (TE, 1), (TE + 1e-6, 0), (1000, 0))
BASSO = pwl((0, 0), (1.0, 0), (1.0001, 1), (TE, 1), (TE + 1e-6, 0), (1000, 0))
TUTTI_HIZ = {x.lower(): HIZ for x in MCU_OUT}


def m_rilascio():
    """t_mute, t_permit: the drains rising through 6 V (the FET off, the coil
    pulling the drain to VRELAY); t_vr80: the audio board's VRELAY below
    9.6 V (80 %, L41a's figure); vr_at_permit: VRELAY when PERMIT releases."""
    return ["meas tran t_mute WHEN v(mute_cmd)=6 RISE=1 FROM=%g" % TE,
            "meas tran t_permit WHEN v(permit_cmd)=6 RISE=1 FROM=%g" % TE,
            "meas tran t_vr80 WHEN v(vrelay)=9.6 FALL=1 FROM=%g" % TE,
            "meas tran t_mute_g WHEN v(mute_g)=1.0 FALL=1 FROM=%g" % TE,
            "meas tran vrelay_min MIN v(vrelay) FROM=%g TO=%g" % (TE, TE + 0.19)]


def casi_timer():
    c = []
    # 1-2: the micro stops while the music plays, mains present
    c.append(caso("micro_reset", drvs=TUTTI_HIZ, misure=m_rilascio()))
    c.append(caso("micro_a_zero", sets={x.lower(): BASSO for x in MCU_OUT if x != "MAINS_REQ"},
                  misure=m_rilascio()))
    # 3: a firmware that drops PERMIT_REQ first, MUTE_REQ still up
    c.append(caso("solo_permit_req_giu", sets={"permit_req": BASSO}, tf=TE + 0.1,
                  misure=["meas tran permit_max MAX v(permit_cmd) FROM=%g TO=%g" % (TE, TE + 0.1),
                          "meas tran mute_max MAX v(mute_cmd) FROM=%g TO=%g" % (TE, TE + 0.1)]))
    # 4-5: mains loss, the micro stuck high or reset at the same instant
    perdita = "0 1 %.12g 1 %.12g 0 1000 0" % (TE, TE + 1e-4)
    c.append(caso("perdita_rete_micro_fermo_alto", env=perdita, tf=TE + 0.4,
                  misure=m_rilascio()[:-1] + [
                      "meas tran vrelay_min MIN v(vrelay) FROM=%g TO=%g" % (TE, TE + 0.39)]))
    c.append(caso("perdita_rete_micro_reset", env=perdita, drvs=TUTTI_HIZ, tf=TE + 0.4,
                  misure=m_rilascio()))
    # 6: U503 (VRELAY_REG) fails open, the micro reset at the same instant
    c.append(caso("guasto_U503_micro_reset", drvs=TUTTI_HIZ, tf=TE + 0.3,
                  extra=["alter @venu503[pwl] = [ 0 1 %.12g 1 %.12g 0 1000 0 ]" % (TE, TE + 1e-6)],
                  misure=m_rilascio()))
    # 7: the release, a firmware that raises MUTE_REQ alone (from mute, VRELAY on)
    muto = pwl((0, 0), (TE, 0), (TE + 1e-6, 1), (1000, 1))
    c.append(caso("rilascio_solo_mute_req", sets={"mute_req": muto, "permit_req": pwl((0, 0), (1000, 0))},
                  tf=TE + 0.1,
                  misure=["meas tran t_mute_on WHEN v(mute_cmd)=6 FALL=1 FROM=%g" % TE,
                          "meas tran t_permit_on WHEN v(permit_cmd)=6 FALL=1 FROM=%g" % TE]))
    # 8: the counterfactual - no RC on PERMIT_T (C528 = 10 pF): D must vanish
    c.append(caso("controfattuale_senza_C528", drvs=TUTTI_HIZ, extra=["alter cc528 = 10p"],
                  misure=m_rilascio()))
    # 9: standby - rear on, front off: toroid off (K501 open), VRELAY_EN,
    # MUTE_REQ, PERMIT_REQ, MAINS_REQ low, the micro in power-down (5 uA),
    # the DAC shut down
    zero = pwl((0, 0), (1000, 0))
    c.append(caso("standby", env1="0 0 1000 0", sets={x.lower(): zero for x in MCU_OUT},
                  iq="0 5u 1000 5u", den="0 0 1000 0", front=1e9, tf=TSS,
                  misure=["meas tran vrelay_j1_max MAX v(vrelay) FROM=%g TO=%g" % (TSS - 0.5, TSS),
                          "meas tran vreg_avg AVG v(vrelay_reg) FROM=%g TO=%g" % (TSS - 0.4, TSS),
                          "let p_t2 = v(t2_sec_a_e,t2_sec_b)*i(vt2_sns)",
                          "meas tran p_t2_avg AVG p_t2 FROM=%g TO=%g" % (TSS - 0.4, TSS),
                          "let p_t1 = v(t1_sec_aa_e)*i(vt1a_sns) + v(t1_sec_ab_e)*i(vt1b_sns)",
                          "meas tran p_t1_avg AVG p_t1 FROM=%g TO=%g" % (TSS - 0.4, TSS)]))
    return c


# ============================================================ the LDR decks
def ldr_parti():
    """The parts of the LDR drive only: any part with a pin on its nets."""
    pref = ("EXP_", "MIR_", "DAC_S", "DAC_P", "LDR_")
    refs = sorted({r for (r, p), n in PN.items()
                   if n.startswith(pref) and not COMPS[r]["part"].startswith("ATtiny")})
    return refs


def ldr_testa(nome):
    righe = ["* L41b1 tb_psu %s - GENERATED by genera_tb_psu.py from %s (led %s, V5 %g)"
             % (nome, ARG.net, ARG.led, ARG.v5),
             MODELS.format(repo=REPO, led_is=LED_IS, vref=VREF_SHUNT)]
    refs = ldr_parti()
    righe.append("* parts: %s" % " ".join(refs))
    for ref in refs:
        righe += element(ref, COMPS[ref])
    # ideal supplies: V5, VREF, the return and GND joined (NT501)
    righe += ["VV5 v5 0 dc %g" % ARG.v5, "VVREF vref 0 dc %g" % VREF_SHUNT,
              "VRET rly_ret 0 dc 0",
              "VDEN_S den_s 0 dc 1", "VDEN_P den_p 0 dc 1",
              "VDSET_S dset_s 0 dc 0", "VDSET_P dset_p 0 dc 0 ac 1"]
    # the micro's ADC reads: 1 GOhm (a pin)
    for n in sorted({n for n in PN.values() if n.startswith("ADC_I_")}):
        righe.append("R_pin_%s %s 0 1G" % (n.lower(), node(n)))
    # Newton's starting point for the two converters. Without it some points
    # fell to ngspice's "transient op", which returns the state at the end of
    # its ramp - with C_X (1 uF, 18 ms) still uncharged, X ~ 0 V and both
    # strings at 25 pA: a number that looked like a latch and was not one
    # (limitations #33, seen again in L41b1). analizza_ldr.py refuses any
    # point that still falls there.
    for s in ("s", "p"):
        righe.append(".nodeset v(exp_x_%s)=2.3 v(exp_b2_%s)=2.3 v(exp_e_%s)=1.9 "
                     "v(exp_n_%s)=2.5 v(exp_f_%s)=1.2 v(mir_%s)=4.3" % ((s,) * 6))
    # J3's LEDs, with a 0 V sense each string (the string current)
    righe += ["DLS1 ldr_s_a ls_mid DLEDV", "DLS2 ls_mid ls_k DLEDV", "VLS ls_k ldr_s_k 0",
              "DLP1 ldr_p_a lp_mid DLEDV", "DLP2 lp_mid lp_k DLEDV", "VLP lp_k ldr_p_k 0"]
    return righe


def ldr_deck():
    cal = json.load(open(ARG.cal)) if ARG.cal else None
    righe = ldr_testa("ldr")
    righe += [".options reltol=1e-5 abstol=1e-15 vntol=1e-8",
              ".control", "set numdgt=12"]
    # the other string idles at 10 nA with the same law
    for t in TEMPS:
        for modo in (("comp", "nocomp", "cal") if cal else ("comp", "nocomp")):
            t_fw = 25 if modo == "nocomp" else t
            for s, nome, i in PUNTI:
                cs = cal.get("%s_%d" % (s, t)) if (cal and modo == "cal") else None
                v_on, code = legge(i, t_fw, cs)
                other = "p" if s == "S" else "s"
                cso = cal.get("%s_%d" % (other.upper(), t)) if (cal and modo == "cal") else None
                v_off, _ = legge(10e-9, t_fw, cso)
                righe += ["alter vdset_%s = %.6f" % (s.lower(), v_on),
                          "alter vdset_%s = %.6f" % (other, v_off),
                          "alter vden_s = 1", "alter vden_p = 1",
                          "dc temp %d %d 1" % (t, t),
                          "echo PUNTO %s %s %s %d %.6e %d" % (modo, s, nome, t, i, code),
                          "print i(vls) i(vlp) v(mir_e2_s) v(ldr_s_a) v(mir_e2_p) v(ldr_p_a)",
                          "destroy all"]
    # the floor with the DAC shut down (reset / POR), both strings
    for t in TEMPS:
        righe += ["alter vden_s = 0", "alter vden_p = 0", "dc temp %d %d 1" % (t, t),
                  "echo PUNTO dac_reset S riposo %d 1.000000e-08 -1" % t,
                  "print i(vls) i(vlp) v(mir_e2_s) v(ldr_s_a) v(mir_e2_p) v(ldr_p_a)",
                  "destroy all"]
    righe += ["alter vden_s = 1", "alter vden_p = 1", ".endc", ".end"]
    suff = ("_cal" if cal else "") + ("_ledmax" if ARG.led == "max" else "") + \
           ("_v5_%g" % ARG.v5 if ARG.v5 != 5.0 else "") + \
           ("_cima%gmA" % (CIMA * 1e3) if CIMA != 20e-3 else "")
    scrivi("tb_psu_ldr%s.cir" % suff, righe)


def rumore_deck():
    """.noise at the shunt anode, the DAC's source as the input, at 10 nA and
    20 mA of the shunt string (25 C). The op-amps and the DAC are noiseless
    here: their share is added by hand in analizza.py from the datasheets."""
    righe = ldr_testa("rumore")
    righe += [".options reltol=1e-5 abstol=1e-15 vntol=1e-8",
              ".control", "set numdgt=8"]
    for nome, i in (("riposo_10nA", 10e-9), ("pieno_20mA", 20e-3)):
        v, _ = legge(i, 25)
        vs, _ = legge(10e-9, 25)
        righe += ["alter vdset_p = %.6f" % v, "alter vdset_s = %.6f" % vs,
                  "noise v(ldr_p_a) vdset_p dec 10 20 20k",
                  "setplot noise1",
                  "echo RUMORE %s" % nome,
                  "print onoise_spectrum[5] onoise_spectrum[20] onoise_spectrum[30]",
                  "print frequency[5] frequency[20] frequency[30]",
                  "destroy all"]
    righe += [".endc", ".end"]
    scrivi("tb_psu_rumore.cir", righe)


def scrivi(nome, righe):
    os.makedirs(ARG.uscita, exist_ok=True)
    open(os.path.join(ARG.uscita, nome), "w").write("\n".join(righe) + "\n")
    print("scritto %s/%s: %d parti tradotte" % (ARG.uscita, nome, len(COMPS)))


# ============================================================ L41b2: the sequences
# Each case: the exogenous events (the user's switches, the mains, a failed
# regulator), the simulated time, and the micro's state before t0 (the
# ponte.c preamble). t0 = TE = 2 s: the bench settles first, the core runs
# from there.
CASI_SEQ = {
    # from standby: the front switched on at TE
    # (every case: the DAC at the idle code until 0.5 s, see uscite_core)
    "accensione": dict(front=[(0, 0), (TE, 0), (TE + 1e-6, 1)], sw3=1, tf=TE + 1.3, pre=None),
    # from MUTO: SW3 to music at TE; the whole fade and the series' calibration
    "rilascio": dict(front=1, sw3=[(0, 0), (TE, 0), (TE + 1e-6, 1)], tf=TE + 7.6, pre="muto"),
    # from MUSICA: SW3 to mute at TE, back to music at TE + 3 s
    "inversione": dict(front=1, sw3=[(0, 1), (TE, 1), (TE + 1e-6, 0), (TE + 3, 0), (TE + 3 + 1e-6, 1)],
                       tf=TE + 6.3, pre="musica"),
    # from MUSICA: the front switched off at TE
    "spegnimento": dict(front=[(0, 1), (TE, 1), (TE + 1e-6, 0)], sw3=1, tf=TE + 7.0, pre="musica"),
    # from MUSICA: the mains gone for 20 ms, then for 200 ms (two holes, two runs)
    "buco20": dict(front=1, sw3=1, buco=0.020, tf=TE + 1.3, pre="musica"),
    "buco200": dict(front=1, sw3=1, buco=0.200, tf=TE + 1.6, pre="musica"),
    # from MUSICA: U502 (the - rail) fails at TE with the mains present; the
    # front stays on
    "guasto": dict(front=1, sw3=1, u502=TE, tf=TE + 1.0, pre="musica"),
}


def ctl(v):
    """A switch: 1 closed (1 S), 0 open (1 nS); a constant or [(t, 0/1), ...]."""
    if isinstance(v, (int, float)):
        v = [(0, v), (1000, v)]
    pts = [(t, 1.0 if x else 1e-9) for t, x in v]
    if pts[-1][0] < 1000:
        pts.append((1000, pts[-1][1]))
    return pwl(*pts)


def uscite_core(path):
    """The core's CSV (ponte.c / mondo.c) -> PWL strings for the micro and the DAC."""
    righe = [r.strip().split(",") for r in open(path) if r.strip() and not r.startswith("t,")]
    # The bench's cold start (V5 rising from 0): with the DAC shut down from
    # t = 0 the transient stopped at 3.4 ms ("Timestep too small", qq507a),
    # and so it did with the series commanded to its 12 mA top from t = 0
    # (the MUSICA preamble). L41b1's decks had it on at a fixed code. So in
    # every case, until AVVIO the DAC is on at the idle code (10 nA, both
    # strings), then the core's state. AVVIO is 1.5 s before the core starts:
    # nothing the core reads depends on it (C_X: 18 ms).
    AVVIO = 0.5
    if righe:
        idle = str(legge(10e-9, 25)[1])
        primo = list(righe[0])
        primo[0], primo[5], primo[6], primo[7] = "0.000000", "1", idle, idle
        if float(righe[0][0]) < AVVIO:
            righe[0] = list(righe[0])
            righe[0][0] = "%.6f" % AVVIO
        righe = [primo] + righe
    cols = {"mains_req": 1, "vrelay_en": 2, "mute_req": 3, "permit_req": 4, "dac_on": 5,
            "code_s": 6, "code_p": 7}
    out = {}
    for nome, c in cols.items():
        pts, prev = [], None
        for r in righe:
            t, v = float(r[0]), float(r[c])
            if nome.startswith("code"):
                v = v * DAC_FS / 4096
            if prev is None:
                pts.append((0.0, v))
            elif v != prev:
                # a step 1 us wide; the times at 12 digits (limitations #30)
                pts.append((t, prev))
                pts.append((t + 1e-6, v))
            prev = v
        pts.append((1000.0, prev))
        # a step at t = 0 would repeat the time: keep only increasing points
        clean = [pts[0]]
        for q in pts[1:]:
            if q[0] > clean[-1][0] + 1e-9:
                clean.append(q)
        out[nome] = pwl(*clean)
    st = [(float(r[0]), r[8]) for r in righe]
    iq, prev = [], None
    for t, s in st:
        v = 5e-6 if s == "STANDBY" else 2e-3
        if prev is None:
            iq.append((0.0, v))
        elif v != prev:
            iq += [(t, prev), (t + 1e-6, v)]
        prev = v
    iq.append((1000.0, prev))
    out["iq"] = pwl(*[q for k, q in enumerate(iq) if k == 0 or q[0] > iq[k - 1][0] + 1e-9])
    return out


SONDE = ["v(front_in)", "v(mute_sw_in)", "v(mute_g_in)", "v(adc_sup_p)", "v(adc_sup_m)",
         "v(adc_sup_vr)", "v(adc_md)", "v(adc_i_s)", "v(adc_i_p)",
         "v(mute_cmd)", "v(permit_cmd)", "v(vrelay)", "v(vrelay_reg)", "v(vplus)", "v(vminus)",
         "v(k501_f)", "v(mute_g)", "v(permit_g)", "v(ldr_s_k)", "v(ldr_p_k)", "v(env)",
         "v(mute_req)", "v(permit_req)", "v(mains_req)", "v(vrelay_en)"]


def seq_deck():
    c = CASI_SEQ[ARG.caso]
    u = uscite_core(ARG.uscite)
    righe = ["* L41b2 tb_psu seq %s (giro %d) - GENERATED by genera_tb_psu.py from %s and %s"
             % (ARG.caso, ARG.giro, ARG.net, ARG.uscite),
             MODELS.format(repo=REPO, led_is=LED_IS, vref=VREF_SHUNT)]
    for ref in sorted(COMPS):
        righe += element(ref, COMPS[ref])
    for n in sorted(set(PN.values())):
        if n.startswith(("AC_", "T1_PRI", "T2_PRI")):
            righe.append("R_float_%s %s 0 1G" % (n.lower(), node(n)))
    # the mains envelope: 1, or a hole
    if c.get("buco"):
        env = "0 1 %.12g 1 %.12g 0 %.12g 0 %.12g 1 1000 1" % (TE, TE + 1e-4, TE + c["buco"],
                                                              TE + c["buco"] + 1e-4)
    else:
        env = "0 1 1000 1"
    righe += ["VENV env 0 pwl(%s)" % env]
    # K501's contact: its coil (A1 on VRELAY_REG, A2 on MAINS_D) above 8.4 V
    # through a 5 ms RC (ASSUMED operate time); the toroid's mains = env x contact
    a1, a2 = pn("K501", "A1"), pn("K501", "A2")
    righe += ["BK501 k501_in 0 V = 0.5*(1+tanh((V(%s,%s)-8.4)/0.2))" % (a1, a2),
              "RK501 k501_in k501_f 5k", "CK501 k501_f 0 1u",
              "BENV1 env1 0 V = V(env)*0.5*(1+tanh((V(k501_f)-0.5)/0.02))"]
    righe += mains("env1", 15.0, 50, 0.08, "T1_SEC_A", "T1_SEC_B", True, "T1")
    righe += mains("env", 12.0, 5, 0.20, "T2_SEC_A", "T2_SEC_B", False, "T2")
    for x in MCU_OUT:
        x = x.lower()
        righe += ["VSET_%s set_%s 0 pwl(%s)" % (x, x, u[x]),
                  "VDRV_%s drv_%s 0 pwl(%s)" % (x, x, DEF_DRV)]
    righe += ["VIQ iq_mcu 0 pwl(%s)" % u["iq"],
              "VDEN_S den_s 0 pwl(%s)" % u["dac_on"], "VDEN_P den_p 0 pwl(%s)" % u["dac_on"],
              "VDSET_S dset_s 0 pwl(%s)" % u["code_s"], "VDSET_P dset_p 0 pwl(%s)" % u["code_p"]]
    if c.get("u502") is not None:
        righe = [r for r in righe if not r.startswith("VENU502 ")]
        righe.append("VENU502 en_u502 0 pwl(0 1 %.12g 1 %.12g 0 1000 0)" % (c["u502"], c["u502"] + 1e-6))
    righe += [
        "RLOADP vplus 0 %g" % (15.0 / I_RAIL), "RLOADM 0 vminus %g" % (15.0 / I_RAIL),
        "RMUTECOIL vrelay mute_cmd %g" % (1315 / 3.0),
        "RPERMITCOIL vrelay permit_cmd 1315",
        "RRESTO vrelay rly_ret %g" % (12 / 0.0424),
        "BTRIM vrelay rly_ret I = 0.0364*max(0, V(vrelay,rly_ret))/12"
        "*0.5*(1+tanh((V(permit_cmd,rly_ret)-6)/0.5))",
        "DLS1 ldr_s_a ls_mid DLEDV", "DLS2 ls_mid ldr_s_k DLEDV",
        "DLP1 ldr_p_a lp_mid DLEDV", "DLP2 lp_mid ldr_p_k DLEDV",
        # the switches: SW3 closed = music; the front closed = on
        "VGSW3 g_sw3 0 pwl(%s)" % ctl(c["sw3"]),
        "BSW3 mute_sw rly_ret I = V(mute_sw,rly_ret)*V(g_sw3)",
        "VGFRONT g_front 0 pwl(%s)" % ctl(c["front"]),
        "BFRONT front_sw rly_ret I = V(front_sw,rly_ret)*V(g_front)",
        # gear: with the DAC shut down from a cold start, trapezoidal stopped at
        # 4 ms ("Timestep too small", exp_f_s) and ngspice then printed only
        # "incomplete or empty netlist" (L41b2)
        ".options reltol=1e-4 abstol=1e-10 vntol=1e-6 temp=25 method=gear",
        ".control",
        "set numdgt=12",
        "set wr_singlescale", "set wr_vecnames",
        "option numdgt=12",
        "tran 100u %.12g 0 20u uic" % c["tf"],
        "linearize",
        "wrdata tb_psu_seq_%s_g%d_out.txt %s" % (ARG.caso, ARG.giro, " ".join(SONDE)),
        ".endc", ".end"]
    # the switch nodes of the timer deck are RSW3 / RFRONT: none here
    assert not any(r.startswith(("RSW3 ", "RFRONT ")) for r in righe)
    scrivi("tb_psu_seq_%s_g%d.cir" % (ARG.caso, ARG.giro), righe)


if ARG.nome == "seq":
    seq_deck()
    raise SystemExit(0)

if ARG.nome == "timer":
    timer_deck()
elif ARG.nome == "ldr":
    ldr_deck()
else:
    rumore_deck()
