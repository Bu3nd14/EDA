#!/usr/bin/env python3
"""L41a: the supply board ALONE, generated from circuits/preamp/psu.net.

Solo stdlib. /usr/bin/python3 genera_tb_psu.py [--net <psu.net>] --uscita <dir>

Every part of psu.net becomes a SPICE element through the MAP below; a part
the map does not know makes the generator REFUSE, so a part added to psu.py
cannot silently vanish from the bench (the same rule as spice_export.py).
The deck therefore follows the source: the supervisor's divider values, the
mains detector's RC, the reservoirs and the hold-up come from the netlist.

MODELS - declared, not vendor unless said (L41a report, section 3):
  - T1, T2: Thevenin per winding, from L41a's rectifier sweep (scelte/): T1
    2x15 V 50 VA, regulation 8 %; T2 12 V AC 5 VA, regulation 20 %
    (ASSUMPTIONS). 100 uH leakage. The mains is an envelope on the sine: the
    mains loss is the envelope going to 0 at a zero crossing.
  - regulators (TPS7A4701, TPS7A3301, MCP1703): BEHAVIOURAL - a
    transconductance to the set voltage, clamped to [0, ILIM], so NO reverse
    current, dropout VDO, the same current drawn from the input. No PSRR, no
    noise: ADR-020's ripple quota is NOT verified by this bench.
  - comparator (TLV1702 in the LM2903 symbol): BEHAVIOURAL open-drain, 1 us,
    HIGH-IMPEDANCE when its supply is below 2 V (the worst case for a mute
    that must fail safe: only the pull-down holds the gate).
  - LM4040: a behavioural shunt at 2.500 V.
  - diodes: 1N4148 from models/diodes/1n4148.lib (vendor, L24); the bridge,
    1N5819 and 24 V zener: declared generic models.
  - 2N7002: models/mosfet_n/generic_nmos.lib MNGEN with W/L sized for 200 mA;
    BC847: models/bjt_npn/generic_npn.lib QNGEN.
  - K501 coil: 360 ohm (12 V, 0.4 W, P5's assumption), no inductance.
THE AUDIO BOARD AS A LOAD (ADR-042, ADR-048): 265 mA on each rail; on VRELAY
the three jack coils (12 VDC, 1315 ohm each, en-g6k.pdf p. 3) between VRELAY
and MUTE_CMD, K6 between VRELAY and PERMIT_CMD, and the rest - K1, K5, K11,
K12 and ~6 mA of LEDs, 42.4 mA - as a resistor to RLY_RET. No coil inductance:
the datasheet gives none (L36).
"""
import argparse
import os
import re

QUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(QUI, "..", "..", "..", "..", "..", ".."))
ap = argparse.ArgumentParser()
ap.add_argument("--net", default=os.path.join(REPO, "circuits", "preamp", "psu.net"))
ap.add_argument("--uscita", required=True)
# variants (declared in the deck name): T2's secondary in V AC, and C520 (VRELAY's
# reservoir) overriding the netlist's value
ap.add_argument("--t2", type=float, default=12.0)
ap.add_argument("--cvr", default=None)
ap.add_argument("--nome", default="rete")
ARG = ap.parse_args()

I_RAIL = 0.265          # ADR-042, eight blocks
TSS = 2.0               # s of settling before any event (C_RAW at ~0.27 A)


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


def element(ref, c):
    part, val = c["part"], c["value"]
    if part == "R":
        return ["R%s %s %s %s" % (ref, pn(ref, "1"), pn(ref, "2"), sval(val))]
    if part == "C":
        return ["C%s %s %s %s" % (ref, pn(ref, "1"), pn(ref, "2"), sval(val))]
    if part == "C_Polarized":
        # ESR 30 mOhm, and the value derated -20 % (ADR-046: >= 1500 uF EFFECTIVE)
        return ["C%s %s %s_esr {0.8*%s}" % (ref, pn(ref, "1"), ref.lower(), sval(val)),
                "R%s_esr %s_esr %s 0.03" % (ref, ref.lower(), pn(ref, "2"))]
    if part == "D":
        return ["D%s %s %s D1N914" % (ref, pn(ref, "2"), pn(ref, "1"))]
    if part == "D_Schottky":
        return ["D%s %s %s DSCH" % (ref, pn(ref, "2"), pn(ref, "1"))]
    if part == "D_Zener":
        return ["D%s %s %s DZ24" % (ref, pn(ref, "2"), pn(ref, "1"))]
    if part == "D_Bridge_+AA-":
        p, a, b, m = (pn(ref, x) for x in "1234")
        return ["D%sa %s %s DBR" % (ref, a, p), "D%sb %s %s DBR" % (ref, b, p),
                "D%sc %s %s DBR" % (ref, m, a), "D%sd %s %s DBR" % (ref, m, b)]
    if part == "2N7002":
        return ["M%s %s %s %s %s MNGEN W=2000u L=1u" % (ref, pn(ref, "3"), pn(ref, "1"),
                                                        pn(ref, "2"), pn(ref, "2"))]
    if part == "BC847":
        return ["Q%s %s %s %s QNGEN" % (ref, pn(ref, "3"), pn(ref, "1"), pn(ref, "2"))]
    if part == "LM2903":
        v, g = pn(ref, "8"), pn(ref, "4")
        return ["X%sa %s %s %s %s %s CMPOD" % (ref, pn(ref, "3"), pn(ref, "2"), pn(ref, "1"), v, g),
                "X%sb %s %s %s %s %s CMPOD" % (ref, pn(ref, "5"), pn(ref, "6"), pn(ref, "7"), v, g)]
    if part == "LM4040DBZ-2.5":
        return ["X%s %s %s SHUNT25" % (ref, pn(ref, "1"), pn(ref, "2"))]
    if part.startswith("TPS7A4701"):
        vset = {"TPS7A4701 15V": 15.0, "TPS7A4701 12V": 12.0}[val]
        # ANY-OUT: the grounded weights must give vset (checked here, from the netlist)
        w = {"4": 6.4, "5": 6.4, "6": 3.2, "8": 1.6, "9": 0.8, "10": 0.4, "11": 0.2, "12": 0.1}
        gnd = PN[(ref, "7")]
        got = 1.4 + sum(x for p, x in w.items() if PN.get((ref, p)) == gnd)
        assert abs(got - vset) < 1e-6, (ref, got, vset)
        return ["X%s %s %s %s en_%s REGP VSET=%g VDO=0.3 ILIM=1" % (
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
        return ["X%s %s %s %s en_%s REGM VSET=%g VDO=0.3 ILIM=1" % (
                    ref, pn(ref, "15"), pn(ref, "1"), pn(ref, "7"), ref.lower(), vset),
                "VEN%s en_%s 0 pwl(0 1 1000 1)" % (ref, ref.lower())]
    if part.startswith("MCP1703"):
        return ["X%s %s %s %s en_%s REGP VSET=5 VDO=0.6 ILIM=0.25" % (
                    ref, pn(ref, "1"), pn(ref, "3"), pn(ref, "2"), ref.lower()),
                "VEN%s en_%s 0 pwl(0 1 1000 1)" % (ref, ref.lower())]
    if part == "G2RL-2A":
        return ["R%s_coil %s %s 360" % (ref, pn(ref, "A1"), pn(ref, "A2"))]
    if part in ("Fuse", "NetTie_2"):
        return ["R%s %s %s 1m" % (ref, pn(ref, "1"), pn(ref, "2"))]
    if part.startswith("Conn_01x"):
        return []           # harnesses: the stimuli below attach to their nets
    raise SystemExit("genera_tb_psu: part %s (%s) not in the map - refusing" % (ref, part))


MODELS = r"""
.include {repo}/models/diodes/1n4148.lib
.include {repo}/models/mosfet_n/generic_nmos.lib
.include {repo}/models/bjt_npn/generic_npn.lib
* declared generic models (L41a): bridge diode, Schottky, 24 V zener
.model DBR D(Is=1e-9 N=1.8 Rs=0.03)
.model DSCH D(Is=1e-6 N=1.1 Rs=0.05)
.model DZ24 D(Is=1e-12 N=1 Rs=1 BV=24 IBV=1m)

* behavioural positive / negative regulator: gm to VSET, clamped to [0, ILIM],
* dropout VDO, no reverse current, input current = output current + 1 mA
.subckt REGP in out gnd en VSET=15 VDO=0.3 ILIM=1
Bo gnd out I = V(en)*min({{ILIM}}, max(0, 1000*(min({{VSET}}, V(in,gnd)-{{VDO}}) - V(out,gnd))))
Bi in gnd I = V(en)*min({{ILIM}}, max(0, 1000*(min({{VSET}}, V(in,gnd)-{{VDO}}) - V(out,gnd)))) + 1m*(V(in,gnd)>1)
Rl out gnd 1meg
.ends
.subckt REGM in out gnd en VSET=15 VDO=0.3 ILIM=1
Bo out gnd I = V(en)*min({{ILIM}}, max(0, 1000*(min({{VSET}}, V(gnd,in)-{{VDO}}) - V(gnd,out))))
Bi gnd in I = V(en)*min({{ILIM}}, max(0, 1000*(min({{VSET}}, V(gnd,in)-{{VDO}}) - V(gnd,out)))) + 1m*(V(gnd,in)>1)
Rl out gnd 1meg
.ends
* behavioural open-drain comparator: output sinks when inn > inp, 1 us,
* high impedance with its supply below 2 V
.subckt CMPOD inp inn out vcc gnd
Bu u gnd V = 0.5*(1+tanh((V(inn)-V(inp))/1m)) * 0.5*(1+tanh((V(vcc,gnd)-2)/0.1))
Ru u uf 1k
Cu uf gnd 1n
Bs out gnd I = V(out,gnd)/50 * V(uf,gnd)
Rleak out gnd 1G
.ends
* behavioural LM4040-2.5 shunt
.subckt SHUNT25 k a
Bz k a I = max(0, V(k,a)-2.5)*20
.ends
"""


def mains(env, vn, va, reg, a, b, mid):
    """Thevenin winding pair driven by env(t) * sin (mains 230 V x factor)."""
    i_nom = va / 2.0 / vn if mid else va / vn
    voc = vn * (1 + reg)
    rs = (voc - vn) / i_nom
    vpk = voc * 2 ** 0.5
    out = []
    if mid:
        out += ["B%sa %sa_i %s V = V(%s)*%.4f*sin(2*pi*50*time)" % (a, a, node("GND"), env, vpk),
                "B%sb %s %sb_i V = V(%s)*%.4f*sin(2*pi*50*time)" % (a, node("GND"), a, env, vpk),
                "R%sa %sa_i %sa_l %.4f" % (a, a, a, rs), "L%sa %sa_l %s 100u" % (a, a, node(a)),
                "R%sb %sb_i %sb_l %.4f" % (a, a, a, rs), "L%sb %sb_l %s 100u" % (a, a, node(b))]
    else:
        out += ["B%s %s_i %s V = V(%s)*%.4f*sin(2*pi*50*time)" % (a, a, node(b), env, vpk),
                "R%s %s_i %s_l %.4f" % (a, a, a, rs), "L%s %s_l %s 100u" % (a, a, node(a)),
                "R%s_float %s 0 10meg" % (a, node(b))]
    return out


def deck(nome, casi):
    """One deck, one case per .control block run (tran + measures + wrdata)."""
    righe = ["* L41a tb_psu %s - GENERATED by genera_tb_psu.py from %s" % (nome, ARG.net),
             MODELS.format(repo=REPO)]
    for ref in sorted(COMPS):
        righe += element(ref, COMPS[ref])
    # the mains side is not simulated (the transformers are Thevenin secondaries
    # driven by ENV): its nets get 1 GOhm to ground so the matrix is not singular
    for n in sorted(set(PN.values())):
        if n.startswith(("AC_", "T1_PRI", "T2_PRI")):
            righe.append("R_float_%s %s 0 1G" % (n.lower(), node(n)))
    # the mains: envelope ENV (1 = present, scaled by the mains factor)
    righe += ["VENV env 0 pwl(0 1 1000 1)"]
    righe += mains("env", 15.0, 50, 0.08, "T1_SEC_A", "T1_SEC_B", True)
    righe += mains("env", ARG.t2, 5, 0.20, "T2_SEC_A", "T2_SEC_B", False)
    # the audio board as a load (J1, J4); the timer (J509) as sources
    righe += [
        "IPLUS vplus 0 dc 0 pwl(0 0 0.5 %g)" % I_RAIL,
        "IMINUS 0 vminus dc 0 pwl(0 0 0.5 %g)" % I_RAIL,
        "RMUTECOIL vrelay mute_cmd %g" % (1315 / 3.0),
        "RPERMITCOIL vrelay permit_cmd 1315",
        "RRESTO vrelay rly_ret %g" % (12 / 0.0424),
        "VMUTEREQ mute_req rly_ret pwl(0 0 1.0 0 1.001 5)",
        "VPERMITREQ permit_req rly_ret pwl(0 0 1.0 0 1.001 5)",
        "VMAINSREQ mains_req rly_ret dc 5",
        "RSW3 mute_sw rly_ret 1",      # SW3 closed = music
        "RFRONT front_sw rly_ret 1",   # front switch on
        ".options reltol=1e-4 abstol=1e-10 vntol=1e-6",
        ".control",
        "set numdgt=15",
    ]
    for c in casi:
        righe += c + ["destroy all"]
    righe += [".endc", ".end"]
    os.makedirs(ARG.uscita, exist_ok=True)
    open(os.path.join(ARG.uscita, "tb_psu_%s.cir" % nome), "w").write("\n".join(righe) + "\n")


SAVE = ("v(vplus) v(vminus) v(vrelay) v(v5) v(raw_p) v(raw_m) v(raw_v) v(rect_v) "
        "v(mute_g) v(permit_g) v(md) v(sup_p) v(sup_m) v(vref) v(mute_cmd) v(permit_cmd) v(mains_coil)")


def caso(nome, env, extra=(), tf=None, vrelay_rip=False):
    """env: PWL of the mains envelope; extra: alter lines before the tran."""
    tf = tf or TSS + 0.3
    # EVERY alteration is reset first: an ngspice `alter` survives `destroy all`
    # and stays on the circuit for the next case. L41a's first fault deck ran
    # U501's fault into U502's case and both into U503's (caught from the
    # numbers: the + rail falling in the - regulator's fault).
    reset = ["alter @ven%s[pwl] = [ 0 1 1000 1 ]" % r.lower()
             for r in sorted(COMPS) if COMPS[r]["part"].startswith(("TPS7A", "MCP1703"))]
    reset += ["alter rr512 = %s" % sval(COMPS["R512"]["value"])]
    out = (["* ---- %s ----" % nome, "alter @venv[pwl] = [ %s ]" % env] + reset
           + list(extra) + ["print @rr512[resistance]"])
    out += ["tran 20u %g 0 20u uic" % tf,
            "wrdata %s/%s.txt %s" % (ARG.uscita, nome, SAVE)]
    return out


# t_loss at a positive zero crossing after TSS: 2.0 s is one (50 Hz)
TL = TSS
casi = []
for f, k in (("m10", 0.9), ("nom", 1.0), ("p10", 1.1)):
    casi.append(caso("regime_%s" % f, "0 %g 1000 %g" % (k, k), tf=TSS))
    casi.append(caso("perdita_rete_%s" % f, "0 %g %g %g %g 0 1000 0" % (k, TL, k, TL + 1e-4),
                     tf=TL + 0.4))
if ARG.nome == "guasti":
    casi = []
    for u in ("U501", "U502", "U503"):
        casi.append(caso("guasto_%s" % u.lower(), "0 1 1000 1", tf=TL + 0.3,
                         extra=["alter @ven%s[pwl] = [ 0 1 %g 1 %g 0 1000 0 ]" % (u.lower(), TL, TL + 1e-6)]))
    # the rails' path alone: the mains detector disabled (R512 open, MD never charges)
    for f, k in (("m10", 0.9), ("nom", 1.0), ("p10", 1.1)):
        casi.append(caso("perdita_senza_rivelatore_%s" % f,
                         "0 %g %g %g %g 0 1000 0" % (k, TL, k, TL + 1e-4), tf=TL + 0.4,
                         extra=["alter rr512 = 1e15"]))
if ARG.cvr:
    # -20 % as for every electrolytic here (ADR-046: effective)
    casi = [["alter cc520 = %g" % (0.8 * float(ARG.cvr.replace("u", "e-6")))] + c for c in casi]
deck(ARG.nome, casi)
print("scritto %s: %d parti tradotte" % (ARG.uscita, len(COMPS)))
