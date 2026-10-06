#!/usr/bin/env python3
"""L47c2a: the supply bench WITHOUT the LDR drive (ADR-062), with the firmware
of the mute with the relays alone.

COPIED from L42b's generator (docs/preamp/data/2026-09-27/L42b/deck/), which
stays as it was. L47c1 took U510 (MCP4822), U511 (MCP6004), Q507-Q512 and J3
off psu.py; this copy follows:
  - gone: the LDR law (legge, PUNTI, TEMPS, --cima, --cal, --led), the ldr and
    rumore decks, the MCP4822 and MCP6004 entries of the map (a part the map
    does not know makes the generator refuse: if they came back, it would
    say so), the OPA5 / OPA5DC models, the VTL5C4 LED model and the four LEDs
    of J3 on the audio board's side, the DAC's den_ / dset_ sources;
  - the core's CSV is the firmware's of L47c2a: t, mains_req, vrelay_en,
    mute_req, permit_req, stato (uscite_core); no DAC, no cold-start AVVIO;
  - the sequence cases: inversione is gone (ADR-062: the insertion is not
    reversible, MUTE_REQ falls at once); the end of rilascio and spegnimento
    is set by the new sequences (no 6 s fade); the L41c cases stay for
    L47c2b, with spegnimento_l shortened the same way (to be confirmed there);
  - the probes: v(adc_i_s), v(adc_i_p), v(ldr_s_k), v(ldr_p_k) are gone;
  - --carico l41a: the counterfactual of L42b now removes only the trim's
    bistables and the micro's 2 mA (the strings are gone from the circuit).
Everything else, the map, the models, the cases, as L42b.

L42b's header follows.

L42b: L41a's two decks, `rete` and `guasti`, on TODAY's psu.net.

COPIED from L41c's generator (docs/preamp/data/2026-09-26/L41c/psu/), which
stays as it was. L41a's decks ran on the psu.py of L41a, which L41b1 rewrote
(the timer, Q505 on VRELAY, the LDR drive): L41c's generator no longer made
them, and the dossier would have shown a number of a circuit that is gone.
L42b adds --nome rete and --nome guasti, with L41a's cases and probes:
  - rete: regime and mains loss at mains -10 % / nominal / +10 %;
  - guasti: U501, U502, U503 off with the mains present; the mains loss with
    the mains detector disabled (R512 = 1e15), at the three mains factors.
Declared differences from L41a's decks, all from today's circuit:
  - the micro is L41b1's timer-deck micro, running (MAINS_REQ at 0, VRELAY_EN
    at 0.9 s, MUTE_REQ and PERMIT_REQ at 1.0 s) and HELD through the event:
    the hardware path alone, as L41a's fixed sources were;
  - the load is L41b1's timer deck's (L41a's plus the trim's bistables and
    J3's LEDs);
  - one probe more, v(vrelay_reg): since L41b1 Q505 separates the regulator's
    output (VRELAY_REG, which L41a called VRELAY) from J1's VRELAY, and
    VRELAY at J1 falls by design D2 after PERMIT_CMD (ADR-049);
  - every case resets R512 too (limitations #34), and prints it;
  - the DAC's series channel at the idle code until 0.5 s, then at the top
    (12 mA, ADR-050): L41c's cold-start fix (uscite_core). With the top from
    t = 0 the mains -10 % case stopped at 4.6 ms on exp_e_s.
The analysis is L42b/deck/analizza.py (L41a's, with the one probe more).

L41c's header follows.

L41c: the supply board WITH its timer hardware AND the firmware's waveforms,
and the cases that L30's bench drew by hand.

COPIED from L41b2's generator (docs/preamp/data/2026-09-26/L41b2/deck/), which
stays as it was. L41c adds sequence cases only (CASI_SEQ, seq_deck), each
from MUSICA unless said, each iterated to the fixed point like L41b2's:
  - spegnimento_l: L41b2's spegnimento, run on until the rails and the LED
    strings are gone (L41b2 stopped 20 ms after MAINS_REQ fell);
  - perdita: the mains gone at TE, for good (both transformers);
  - guasto_u501: U501 (the + rail) off at TE, the mains present;
  - guasto_u503: U503 (VRELAY_REG) off at TE, the mains present;
  - cf_nodelta: perdita with C528 = 10 pF - D gone, L30's counterfactual;
  - corto_u503: U503's output to ground (0.1 ohm) at TE - the question for
    the user (NC-036);
  - perdita_min, guasto_u503_min: the same at the timing parts' minimum
    corner (--angolo min is REQUIRED for them and refused otherwise).
  Also written: the two LED strings' sense voltages were already probed;
  L41c's bridge (ponte/estrai_ponte.py) reads them as currents (/10 ohm).

L41b2's header follows.

L41b2: the supply board WITH its timer hardware AND the firmware's waveforms.

Solo stdlib (L47c2a's usage).
  /usr/bin/python3 genera_tb_psu.py --uscita <dir> --nome timer [--angolo min --v5 4.9]
  /usr/bin/python3 genera_tb_psu.py --uscita <dir> --nome rete|guasti [--carico l41a]
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
import math
import os
import re

# L48a (ADR-064), the ONLY change from L47c2a's copy: the rest of the audio
# board's VRELAY load gains the selector's coil, one G6K-2F-Y on in every
# state (9.1 mA at 12 V, en-g6k.pdf): 42.4 -> 51.5 mA. --resto 42.4 gives
# back L47c2a's decks.
I_RESTO = 0.0515
import sys as _sys
if "--resto" in _sys.argv:
    _i = _sys.argv.index("--resto")
    I_RESTO = float(_sys.argv[_i + 1]) / 1000
    del _sys.argv[_i:_i + 2]
QUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(QUI, "..", "..", "..", "..", "..", "..", ".."))
ap = argparse.ArgumentParser()
ap.add_argument("--net", default=os.path.join(REPO, "circuits", "preamp", "psu.net"))
ap.add_argument("--uscita", required=True)
ap.add_argument("--nome", choices=("timer", "seq", "rete", "guasti"), required=True)
ap.add_argument("--caso", default=None)
ap.add_argument("--uscite", default=None)
ap.add_argument("--giro", type=int, default=1)
ap.add_argument("--angolo", choices=("nom", "min"), default="nom")
ap.add_argument("--v5", type=float, default=5.0)
# L42b: the counterfactual of the load - the bench without what L41a's had not
# (the trim's bistables, the micro's 2 mA; L47c2a: J3's LED strings and the
# DAC are gone from the circuit itself): if it gives back L41a's figures,
# today's supply is L41a's supply and every difference is the load
ap.add_argument("--carico", choices=("oggi", "l41a"), default="oggi")
ARG = ap.parse_args()

I_RAIL = 0.265          # ADR-042, eight blocks
TSS = 2.0               # s of settling before any event (C_RAW at ~0.27 A)
TE = TSS                # the event: a positive zero crossing of the mains

# L47c2a: the LDR law (ADR-049) is gone with the drive (ADR-062).


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
    # L47c2a: MCP6004 (U511) and MCP4822 (U510) are gone (ADR-062); if either
    # came back it would fall to the refusal at the end
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
# the firmware's, L41b2)
DEF_SET = {"mains_req": pwl((0, 1), (1000, 1)),
           "vrelay_en": pwl((0, 0), (0.9, 0), (0.9001, 1), (1000, 1)),
           "mute_req": pwl((0, 0), (1.0, 0), (1.0001, 1), (1000, 1)),
           "permit_req": pwl((0, 0), (1.0, 0), (1.0001, 1), (1000, 1))}
DEF_DRV = pwl((0, 1), (1000, 1))


def timer_deck():
    righe = ["* L47c2a tb_psu timer (%s) - GENERATED by genera_tb_psu.py from %s" % (ARG.angolo, ARG.net),
             MODELS.format(repo=REPO, vref=VREF_SHUNT)]
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
    righe += ["VIQ iq_mcu 0 pwl(0 2m 1000 2m)"]
    righe += [
        "IPLUS vplus 0 dc 0 pwl(0 0 0.5 %g)" % I_RAIL,
        "IMINUS 0 vminus dc 0 pwl(0 0 0.5 %g)" % I_RAIL,
        "RMUTECOIL vrelay mute_cmd %g" % (1315 / 3.0),
        "RPERMITCOIL vrelay permit_cmd 1315",
        "RRESTO vrelay rly_ret %g" % (12 / I_RESTO),
        # the trim's bistables, driven while K6 is released (NC-037)
        "BTRIM vrelay rly_ret I = 0.0364*max(0, V(vrelay,rly_ret))/12"
        "*0.5*(1+tanh((V(permit_cmd,rly_ret)-6)/0.5))",
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
         misure=(), iq="0 2m 1000 2m", front=1):
    """One case: every source the cases touch is reset, then this case's."""
    tf = tf or TE + 0.2
    sets = dict(DEF_SET, **(sets or {}))
    drvs = dict({x.lower(): DEF_DRV for x in MCU_OUT}, **(drvs or {}))
    out = ["* ---- %s ----" % nome,
           "alter @venv[pwl] = [ %s ]" % env,
           "alter @venv1[pwl] = [ %s ]" % (env1 or env),
           "alter @viq[pwl] = [ %s ]" % iq,
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
    # MUTE_REQ, PERMIT_REQ, MAINS_REQ low, the micro in power-down (5 uA)
    zero = pwl((0, 0), (1000, 0))
    c.append(caso("standby", env1="0 0 1000 0", sets={x.lower(): zero for x in MCU_OUT},
                  iq="0 5u 1000 5u", front=1e9, tf=TSS,
                  misure=["meas tran vrelay_j1_max MAX v(vrelay) FROM=%g TO=%g" % (TSS - 0.5, TSS),
                          "meas tran vreg_avg AVG v(vrelay_reg) FROM=%g TO=%g" % (TSS - 0.4, TSS),
                          "let p_t2 = v(t2_sec_a_e,t2_sec_b)*i(vt2_sns)",
                          "meas tran p_t2_avg AVG p_t2 FROM=%g TO=%g" % (TSS - 0.4, TSS),
                          "let p_t1 = v(t1_sec_aa_e)*i(vt1a_sns) + v(t1_sec_ab_e)*i(vt1b_sns)",
                          "meas tran p_t1_avg AVG p_t1 FROM=%g TO=%g" % (TSS - 0.4, TSS)]))
    return c


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
    "accensione": dict(front=[(0, 0), (TE, 0), (TE + 1e-6, 1)], sw3=1, tf=TE + 1.3, pre=None),
    # from MUTO: SW3 to music at TE (L47c2a: no fade, MUSICA 10 ms after the
    # relays; 0.5 s shows the coils settled)
    "rilascio": dict(front=1, sw3=[(0, 0), (TE, 0), (TE + 1e-6, 1)], tf=TE + 0.5, pre="muto"),
    # L47c2a: "inversione" is gone - the insertion is not reversible (ADR-062)
    # from MUSICA: the front switched off at TE (L47c2a: MUTE_REQ at ~TE + 27
    # ms, MAINS_REQ ~100 ms later; to TE + 0.4 s, K501 open and the rails
    # falling)
    "spegnimento": dict(front=[(0, 1), (TE, 1), (TE + 1e-6, 0)], sw3=1, tf=TE + 0.4, pre="musica"),
    # from MUSICA: the mains gone for 20 ms, then for 200 ms (two holes, two runs)
    "buco20": dict(front=1, sw3=1, buco=0.020, tf=TE + 1.3, pre="musica"),
    "buco200": dict(front=1, sw3=1, buco=0.200, tf=TE + 1.6, pre="musica"),
    # from MUSICA: U502 (the - rail) fails at TE with the mains present; the
    # front stays on
    "guasto": dict(front=1, sw3=1, u502=TE, tf=TE + 1.0, pre="musica"),
    # ---- L41c (L30's bench on the real supply)
    # the soft power-down, on until the rails and the strings are gone: K501
    # opens at ~TE + 6.63 s, the rails' hold (0.8 x 2200 uF on 56.6 ohm) is
    # tau ~0.1 s once U501 / U502 drop out. Ends at TE + 7.6 s: the first run
    # to TE + 7.8 stopped at TE + 7.641 ("Timestep too small", xu511a.bout,
    # the node that stopped L41b2's power-down too), with the rails at
    # +0.73 / -0.70 V and both strings at 5 nA - after everything V2 reads
    # (jack open ~TE + 6.53, V+ below 10.6 V ~TE + 6.75). At TE + 7.6 the
    # rails are at +0.83 / -0.81 V; the bridge holds them from there (L41c)
    # L47c2a: without the fade K501 opens at ~TE + 0.13 s, so the same 1 s
    # after it is TE + 1.1 (L47c2b runs this case and confirms the end)
    "spegnimento_l": dict(front=[(0, 1), (TE, 1), (TE + 1e-6, 0)], sw3=1, tf=TE + 1.1,
                          pre="musica"),
    # the mains gone at TE for good
    "perdita": dict(front=1, sw3=1, buco=1000.0, tf=TE + 1.0, pre="musica"),
    "perdita_min": dict(front=1, sw3=1, buco=1000.0, tf=TE + 1.0, pre="musica", angolo="min"),
    # a regulator off with the mains present: + rail, VRELAY_REG
    "guasto_u501": dict(front=1, sw3=1, spento={"U501": TE}, tf=TE + 1.0, pre="musica"),
    "guasto_u503": dict(front=1, sw3=1, spento={"U503": TE}, tf=TE + 1.0, pre="musica"),
    "guasto_u503_min": dict(front=1, sw3=1, spento={"U503": TE}, tf=TE + 1.0, pre="musica",
                            angolo="min"),
    # L30's counterfactual: no D (C528 = 10 pF), the mains gone
    "cf_nodelta": dict(front=1, sw3=1, buco=1000.0, tf=TE + 1.0, pre="musica", c528="10p"),
    # U503's output shorted to ground: C523 (on VRELAY_REG) goes with it
    "corto_u503": dict(front=1, sw3=1, corto=TE, tf=TE + 1.0, pre="musica"),
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
    """The core's CSV (ponte.c / mondo.c, L47c2a: t, mains_req, vrelay_en,
    mute_req, permit_req, stato) -> PWL strings for the micro's outputs and
    its supply current. L47c2a: no DAC, so no cold-start AVVIO."""
    righe = [r.strip().split(",") for r in open(path) if r.strip() and not r.startswith("t,")]
    assert righe and all(len(r) == 6 for r in righe), "uscite del core: non e' il CSV di L47c2a"
    cols = {"mains_req": 1, "vrelay_en": 2, "mute_req": 3, "permit_req": 4}
    out = {}
    for nome, c in cols.items():
        pts, prev = [], None
        for r in righe:
            t, v = float(r[0]), float(r[c])
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
    st = [(float(r[0]), r[5]) for r in righe]
    iq, prev = [], None
    for t, s_ in st:
        v = 5e-6 if s_ == "STANDBY" else 2e-3
        if prev is None:
            iq.append((0.0, v))
        elif v != prev:
            iq += [(t, prev), (t + 1e-6, v)]
        prev = v
    iq.append((1000.0, prev))
    out["iq"] = pwl(*[q for k, q in enumerate(iq) if k == 0 or q[0] > iq[k - 1][0] + 1e-9])
    return out


SONDE = ["v(front_in)", "v(mute_sw_in)", "v(mute_g_in)", "v(adc_sup_p)", "v(adc_sup_m)",
         "v(adc_sup_vr)", "v(adc_md)",
         "v(mute_cmd)", "v(permit_cmd)", "v(vrelay)", "v(vrelay_reg)", "v(vplus)", "v(vminus)",
         "v(k501_f)", "v(mute_g)", "v(permit_g)", "v(env)",
         "v(mute_req)", "v(permit_req)", "v(mains_req)", "v(vrelay_en)"]


def seq_deck():
    c = CASI_SEQ[ARG.caso]
    # L41c: a corner case runs only with --angolo min (ANGOLO and VREF_SHUNT are
    # set from it at import), and a nominal case never with it
    if (c.get("angolo") == "min") != (ARG.angolo == "min"):
        raise SystemExit("caso %s: --angolo %s non e' il suo" % (ARG.caso, ARG.angolo))
    u = uscite_core(ARG.uscite)
    righe = ["* L47c2a tb_psu seq %s (giro %d) - GENERATED by genera_tb_psu.py from %s and %s"
             % (ARG.caso, ARG.giro, ARG.net, ARG.uscite),
             MODELS.format(repo=REPO, vref=VREF_SHUNT)]
    for ref in sorted(COMPS):
        righe += element(ref, COMPS[ref])
    for n in sorted(set(PN.values())):
        if n.startswith(("AC_", "T1_PRI", "T2_PRI")):
            righe.append("R_float_%s %s 0 1G" % (n.lower(), node(n)))
    # the mains envelope: 1, or a hole
    if c.get("buco", 0) >= 100:
        # L41c: the mains gone for good
        env = "0 1 %.12g 1 %.12g 0 1000 0" % (TE, TE + 1e-4)
    elif c.get("buco"):
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
    righe += ["VIQ iq_mcu 0 pwl(%s)" % u["iq"]]
    if c.get("u502") is not None:
        righe = [r for r in righe if not r.startswith("VENU502 ")]
        righe.append("VENU502 en_u502 0 pwl(0 1 %.12g 1 %.12g 0 1000 0)" % (c["u502"], c["u502"] + 1e-6))
    # L41c: a regulator off (its enable to 0 in 1 us, as L41b2's u502)
    for ref, t in sorted(c.get("spento", {}).items()):
        v = "VEN%s " % ref
        assert sum(r.startswith(v) for r in righe) == 1, ref
        righe = [r for r in righe if not r.startswith(v)]
        righe.append("VEN%s en_%s 0 pwl(0 1 %.12g 1 %.12g 0 1000 0)" % (ref, ref.lower(), t, t + 1e-6))
    # L41c: the counterfactual without D - C528 replaced, nothing else
    if c.get("c528"):
        k = [i for i, r in enumerate(righe) if r.startswith("CC528 ")]
        assert len(k) == 1
        p = righe[k[0]].split()
        righe[k[0]] = "CC528 %s %s %s" % (p[1], p[2], c["c528"])
    # L41c: U503's output shorted - a conductance from VRELAY_REG to the return,
    # 0 before, 10 S (0.1 ohm) from the case's instant (1 us edge)
    if c.get("corto") is not None:
        vr, ret = pn("U503", "1"), pn("C523", "2")
        assert vr == "vrelay_reg", vr
        righe += ["VGCORTO g_corto 0 pwl(0 0 %.12g 0 %.12g 10 1000 10)" % (c["corto"], c["corto"] + 1e-6),
                  "BCORTO %s %s I = V(%s,%s)*V(g_corto)" % (vr, ret, vr, ret)]
    righe += [
        "RLOADP vplus 0 %g" % (15.0 / I_RAIL), "RLOADM 0 vminus %g" % (15.0 / I_RAIL),
        "RMUTECOIL vrelay mute_cmd %g" % (1315 / 3.0),
        "RPERMITCOIL vrelay permit_cmd 1315",
        "RRESTO vrelay rly_ret %g" % (12 / I_RESTO),
        "BTRIM vrelay rly_ret I = 0.0364*max(0, V(vrelay,rly_ret))/12"
        "*0.5*(1+tanh((V(permit_cmd,rly_ret)-6)/0.5))",
        # the switches: SW3 closed = music; the front closed = on
        "VGSW3 g_sw3 0 pwl(%s)" % ctl(c["sw3"]),
        "BSW3 mute_sw rly_ret I = V(mute_sw,rly_ret)*V(g_sw3)",
        "VGFRONT g_front 0 pwl(%s)" % ctl(c["front"]),
        "BFRONT front_sw rly_ret I = V(front_sw,rly_ret)*V(g_front)",
        # (L47c2a: the two reasons below were the LDR drive's, which is gone;
        # the options are kept so that a difference from L41b2 is the circuit's)
        # gear: with the DAC shut down from a cold start, trapezoidal stopped at
        # 4 ms ("Timestep too small", exp_f_s) and ngspice then printed only
        # "incomplete or empty netlist" (L41b2)
        # gmin 1e-10 (default 1e-12): with a core that shut the supply down at
        # another instant (the fault case with FALSO 6) the transient stopped
        # at K501's opening, 3 ms after MAINS_REQ ("Timestep too small",
        # blamed on xu511a.bout, which was not moving); rshunt, maxord=2,
        # trtol=1 and a smooth OPA5 did not help, gmin did. 100 pS across a
        # junction at 0.5 V is 50 pA: 0.5 % of the 10 nA idle (L41b2)
        ".options reltol=1e-4 abstol=1e-10 vntol=1e-6 temp=25 method=gear gmin=1e-10",
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


# ============================================================ L42b: L41a's decks
# L41a's probes (analizza.py reads them in this order), plus v(vrelay_reg)
SAVE_RETE = ("v(vplus) v(vminus) v(vrelay) v(v5) v(raw_p) v(raw_m) v(raw_v) v(rect_v) "
             "v(mute_g) v(permit_g) v(md) v(sup_p) v(sup_m) v(vref) v(mute_cmd) v(permit_cmd) "
             "v(mains_coil) v(vrelay_reg)")


def caso_rete(nome, env, extra=(), tf=None):
    """L41a's case on today's bench: timer-deck micro held, R512 reset first."""
    r512 = sval(COMPS["R512"]["value"])
    return caso(nome, env=env, tf=tf,
                extra=["alter rr512 = %s" % r512] + list(extra) + ["print @rr512[resistance]"],
                misure=["wrdata %s/%s.txt %s" % (ARG.uscita, nome, SAVE_RETE)])


def rete_deck():
    righe = ["* L47c2a tb_psu %s - GENERATED by genera_tb_psu.py from %s" % (ARG.nome, ARG.net),
             MODELS.format(repo=REPO, vref=VREF_SHUNT)]
    for ref in sorted(COMPS):
        righe += element(ref, COMPS[ref])
    for n in sorted(set(PN.values())):
        if n.startswith(("AC_", "T1_PRI", "T2_PRI")):
            righe.append("R_float_%s %s 0 1G" % (n.lower(), node(n)))
    # both transformers follow the mains factor, as in L41a
    righe += ["VENV env 0 pwl(0 1 1000 1)", "VENV1 env1 0 pwl(0 1 1000 1)"]
    righe += mains("env1", 15.0, 50, 0.08, "T1_SEC_A", "T1_SEC_B", True, "T1")
    righe += mains("env", 12.0, 5, 0.20, "T2_SEC_A", "T2_SEC_B", False, "T2")
    for x in MCU_OUT:
        x = x.lower()
        righe += ["VSET_%s set_%s 0 pwl(%s)" % (x, x, DEF_SET[x]),
                  "VDRV_%s drv_%s 0 pwl(%s)" % (x, x, DEF_DRV)]
    righe += ["VIQ iq_mcu 0 pwl(0 2m 1000 2m)"]
    righe += [
        "IPLUS vplus 0 dc 0 pwl(0 0 0.5 %g)" % I_RAIL,
        "IMINUS 0 vminus dc 0 pwl(0 0 0.5 %g)" % I_RAIL,
        "RMUTECOIL vrelay mute_cmd %g" % (1315 / 3.0),
        "RPERMITCOIL vrelay permit_cmd 1315",
        "RRESTO vrelay rly_ret %g" % (12 / I_RESTO),
        "BTRIM vrelay rly_ret I = 0.0364*max(0, V(vrelay,rly_ret))/12"
        "*0.5*(1+tanh((V(permit_cmd,rly_ret)-6)/0.5))",
        "RSW3 mute_sw rly_ret 1",
        "RFRONT front_sw rly_ret 1",
        ".options reltol=1e-4 abstol=1e-10 vntol=1e-6",
        ".control",
        "set numdgt=15",
    ]
    TL = TSS          # a positive zero crossing of the mains, as in L41a
    casi = []
    if ARG.nome == "rete":
        for f, k in (("m10", 0.9), ("nom", 1.0), ("p10", 1.1)):
            casi.append(caso_rete("regime_%s" % f, "0 %g 1000 %g" % (k, k), tf=TSS))
            casi.append(caso_rete("perdita_rete_%s" % f,
                                  "0 %g %.12g %g %.12g 0 1000 0" % (k, TL, k, TL + 1e-4), tf=TL + 0.4))
    else:
        for u in ("U501", "U502", "U503"):
            casi.append(caso_rete("guasto_%s" % u.lower(), "0 1 1000 1", tf=TL + 0.3,
                                  extra=["alter @ven%s[pwl] = [ 0 1 %.12g 1 %.12g 0 1000 0 ]"
                                         % (u.lower(), TL, TL + 1e-6)]))
        for f, k in (("m10", 0.9), ("nom", 1.0), ("p10", 1.1)):
            casi.append(caso_rete("perdita_senza_rivelatore_%s" % f,
                                  "0 %g %.12g %g %.12g 0 1000 0" % (k, TL, k, TL + 1e-4), tf=TL + 0.4,
                                  extra=["alter rr512 = 1e15"]))
    if ARG.carico == "l41a":
        via = ("BTRIM ",)
        assert sum(r.startswith(via) for r in righe) == len(via)
        righe = [r for r in righe if not r.startswith(via)]
        righe = [r.replace("iq_mcu 0 pwl(0 2m 1000 2m)", "iq_mcu 0 pwl(0 0 1000 0)") for r in righe]
        # L47c2a: with the trapezoidal method the rete counterfactual stopped in
        # regime_m10 at 0.900153 s, VRELAY_EN's edge ("Timestep too small",
        # qq504); gear, the sequence decks' method, runs it. Only here: the
        # decks of today's load keep L42b's options
        k = [i for i, r in enumerate(righe) if r == ".options reltol=1e-4 abstol=1e-10 vntol=1e-6"]
        assert len(k) == 1
        righe[k[0]] += " method=gear"
        casi = [[x.replace("alter @viq[pwl] = [ 0 2m 1000 2m ]", "alter @viq[pwl] = [ 0 0 1000 0 ]")
                 for x in c] for c in casi]
        assert all(any("alter @viq[pwl] = [ 0 0 1000 0 ]" == x for x in c) for c in casi)
    for c in casi:
        righe += c + ["destroy all"]
    righe += [".endc", ".end"]
    scrivi("tb_psu_%s%s.cir" % (ARG.nome, "_carico_l41a" if ARG.carico == "l41a" else ""), righe)


if ARG.nome in ("rete", "guasti"):
    rete_deck()
elif ARG.nome == "seq":
    seq_deck()
else:
    timer_deck()
