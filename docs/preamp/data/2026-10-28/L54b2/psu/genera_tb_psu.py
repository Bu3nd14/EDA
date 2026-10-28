#!/usr/bin/env python3
"""L45d2b3b1: COPIED from L45d2b2b2's (with the whole psu/ folder), which stays as it was. One addition:
the fault primitive ("carico", a, b, R) in applica_guasto(), a resistor from tg (C145 shorted: the
RC cell's 10 ohm on VPLUS). Every deck without it is L45d2b2b2's line for line (checked on two
source cases, README).

L45d2b2b2: COPIED from L45d2b2b1's generator (data/2026-10-20/L45d2b2b1/psu/), which stays as it was.
Additions, for ADR-075's rows (the relay command, the resistors, U504) - in the fault cases only, so
that every other deck stays L45d2b2b1's line for line:
  - SONDE_I: a 0 V source in series with a chosen PIN of a part (pin_nodo() below; the part's line
    then reaches the net through si_<ref>_<pin>): i(vsi<ref>_<pin>) is the current flowing from the
    net INTO that pin. Default: the drains of Q501, Q502, Q503 (2N7002) and Q505 (AO3401A), the
    anodes of the clamp zeners D507 / D509, the LM4040's cathode, Q504's collector and base, the
    outputs of U503 and U504. --sonde REF:pin,... replaces the list, --sonde no drops it;
  - the current through the fault itself, i(vfc), a 0 V source in series with the "corto"
    primitive's conductance;
  - the voltages the analysis needs for the parts' power (SONDE_075).
Checked before use (README, «Il controllo della sonda»).

L45d2b2a: COPIED from L45d2b1's generator (data/2026-10-14/L45d2b1/psu/), which stays as it was.
Checked before use (controllo/, README): with only the detector's lines taken out, on the psu.net of
before this lot, accensione and perdita gave L45d2b1's and L56's core CSV byte for byte; with
--ss no --cap-audio no --bobine g6k accensione gave the same again; the rete deck with --bobine im06
gave L60c2's hold of VRELAY_REG at mains -10 %, 46.367 ms (46.372). Changes, each declared at its line:
  - gone: L45d2b1's primitive "riv" and the probes v(dc_flt), v(dc_flt_in) (the detector, ADR-081);
  - the mute coils with K3 IM06TS (ADR-085): R_MUTECOIL 401.17 ohm (--bobine g6k: 438.33);
  - the soft-start of the TPS7A regulators (REGPSS / REGMSS, NC-063), C_NR read from the netlist
    (--cnr overrides; --ss no gives back REGP / REGM), with a sense on IN for the probes;
  - the audio board's capacitance on the rails (CAP_AUDIO, --cap-audio no to drop it);
  - --rpre: a resistor before a regulator (ADR-092 was chosen on it); the netlist's R550 / R551
    are read by resistenza_davanti() for the regime measures;
  - accensione to TE + 2.5 s, accensione_m10 (mains -10 %), the regime measures of the rete deck
    (misure_regime), gear in the rete deck with the soft-start.
The load is carico.txt of this lot (today's block, L62b).

L45d2b1: COPIED from L45c2's generator (data/2026-10-14/L45c2/psu/), which stays as it was. Before
any change this copy, on today's psu.net (the DC detector's line, D525-D527, R548, R549, C535),
gave back L56's perdita byte for byte (core CSV at the fixed point): with DC_FLT high the three
diodes do nothing. Additions (ADR-072):
  - the primitive ("riv", ritardo, r_carico): DC_FLT pulled to RLY_RET from tg + ritardo while the
    audio board's detector has a supply, and an optional load on VPLUS from tg (applica_guasto);
  - the probes v(dc_flt), v(dc_flt_in), v(vr_g), v(mains_g) (SONDE); ponte.c reads v(dc_flt_in).
Everything else is L45c2's.

L45c2: COPIED from L45c1's generator (data/2026-10-13/L45c1/psu/), which stays as it was. Before
any change this copy gave back L45c1's perdita and guasto_u501 byte for byte (core CSV and bridge
JSON). Additions, all for the fault cases of modi.py (the relay line and the commands):
  - the primitive ("spento", ref): a regulator's enable to 0 at the fault's instant (U504, V5);
  - the primitive ("niente",): no fault - the base case of an event that L45c1 had not (ins);
  - the events ins (SW3 to mute at TE: the mute inserted from the front, the firmware's own
    sequence) and gu503 (U503 off at TE, with metodo_u503 of carico.txt, as guasto_u503).
Everything else is L45c1's.

L45c1: COPIED from L56's generator (data/2026-10-12/L56-alimentatore/psu/), which stays as
it was. One addition: the FAULT cases of the supply's audio rails, f_<ref>_<modo>_<evento>,
read from modi.py next to this file (its header says the primitives), applied by
applica_guasto() to the sequence deck. Every other case, the map, the models and the loads are
L56's: before the addition this copy gave back L56's perdita and guasto_u501 byte for byte
(core CSV and bridge JSON).

L51b: COPIED from L47c2b2's generator (data/2026-10-06/L47c2b2/psu/), which
stays as it was, with L48a's change made general: the audio board's load -
the two rails and the rest of VRELAY - is no longer written here but read
from carico.txt at the root of the lot (see below, at I_PIU). The same file
is in L51b/ (today's load) and in L51b-prima/ (the load before, which must
give back L47c2a and L47c2b2). The deck headers still say L47c2a: they are
L47c2a's decks with another load, and the comparison reads them as such.

L47c2b2: COPIED from L47c2a's generator (data/2026-10-05/L47c2a/deck/), which
stays as it was; the only change is the comment on spegnimento_l's end, TE + 1.1 s,
confirmed by the user («1,1 s»).

L47c2a: the supply bench WITHOUT the LDR drive (ADR-062), with the firmware
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
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(QUI, "..", "..", "..", "..", "..", ".."))
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
# L45d2b2a: the three mute coils on MUTE_CMD. K3, the Stax's mute relay, is a TE Axicom IM06TS
# since ADR-085 (L60c2): 1029 ohm (12 V, 140 mW), so 1315 || 1315 || 1029 = 401.17 ohm, as L60c2's
# prepara_rete.py. --bobine g6k gives back the three G6K of before (438.33 ohm), for the check.
ap.add_argument("--bobine", choices=("im06", "g6k"), default="im06")
# L45d2b2a: the soft-start of the three TPS7A regulators (NC-063). --ss no gives back L45d2b1's
# regulators without it (the check); --cnr U501=1u,U502=1u overrides the NR capacitors read from
# the netlist, for the options put to the user before the source changes.
ap.add_argument("--ss", choices=("si", "no"), default="si")
ap.add_argument("--cap-audio", dest="cap_audio", choices=("si", "no"), default="si")
ap.add_argument("--cnr", default=None)
# L45d2b2a: a resistor in series before a regulator's IN (the heat at regime, a question of the
# user's): --rpre U501=4.7,U502=4.7. The reservoir and the rest of RAW_P / RAW_M stay where they are.
ap.add_argument("--rpre", default=None)
# L45d2b2b1: another lot's carico.txt (the control on L45c1's cases runs on L45c1's load)
ap.add_argument("--file-carico", dest="file_carico", default=None)
# L45d2b2b1, ADR-074's options (variante() below): --variante uscita puts a Schottky in series
# between each rail regulator's OUT pin and its rail (the hold-up C505 / C506, the supervisor, the
# audio board), the regulator regulating the rail after it; C511 / C512 and D510 / D511 stay on the
# pin. --dserie / --dclamp "Is,N,Rs": the model of that series diode / of D510 and D511 (default:
# DSCH, the generic 1N5819 of L41a).
ap.add_argument("--variante", choices=("no", "uscita"), default="no")
# --senso: where the regulator regulates with --variante uscita - the rail after the diode
# (REGPSSF / REGMSSF) or its own pin (REGPSS / REGMSS as today, the rail = pin - Vf); --dvset: volts
# added to both set points (ANY-OUT pins / the U502 divider), so that the rail stays near 15 V
ap.add_argument("--senso", choices=("rail", "piedino"), default="rail")
ap.add_argument("--dvset", type=float, default=0.0)
ap.add_argument("--valore", default=None)
ap.add_argument("--dserie", default=None)
ap.add_argument("--dclamp", default=None)
# L45d2b2b2: the current probes of the fault cases (SONDE_I below): "REF:pin,REF:pin", or "no"
ap.add_argument("--sonde", default=None)
# L45d2b2b2: the 2N7002's saturation. MNGEN at W 2000u (L41a) gives K = KP W / L = 0.4 A/V^2: ~2.5 A
# at VGS 4.5 V, where Nexperia's 2N7002 (Rev. 7, p6 fig. 5, typical, read by eye) saturates at
# ~0.55-0.7 A. "ds": W 571u, K = 0.114 A/V^2 - 0.70 A at VGS 4.5 V, 0.91 A at 5 V with the bench's
# VTO 1.0 V; RDS(on) in the linear region ~2.5 ohm (the datasheet's 3.8 typ at 75 mA: declared)
ap.add_argument("--n2n7002", choices=("l41a", "ds"), default="l41a")
# L45d2b2b2: a sink replaced by another MOSFET (ADR-075's "un MOSFET che regga"): --mos Q503=DMN6075S
ap.add_argument("--mos", default=None)
# L45d2b2b2, ADR-075's options without touching the source: --serie2 D506,R503,... puts each named
# diode or resistor as TWO in series (a resistor as two halves), through <ref>_m; a "corto" fault on
# the part's two nodes then shorts the FIRST of the two only (applica_guasto). --u504doppio: a second
# MCP1703A-5002 (U504B) between U504's output (v5_m) and V5, 1 uF on v5_m; U504 IN-OUT then shorts
# the first.
ap.add_argument("--serie2", default=None)
ap.add_argument("--u504doppio", action="store_true")
# L45d2b2b2: --rk 47 - a resistor between K501's coil (MAINS_COIL) and Q503's drain, outside the
# flyback loop (coil + D505): it limits a shorted coil to VRELAY_REG / R. v(q503_rk) is the drain.
ap.add_argument("--rk", type=float, default=None)
# L54a (NC-054): who drives MUTE_REQ / MAINS_REQ / VRELAY_EN. micro = the firmware core (ponte.c),
# as every lot before; comparatori = the all-analog timer of TIMER_AN with the standby (K501 and
# the front switch as today); diretto = the same timer without the standby: K501's contact always
# closed (a mains switch, the bench's env), the front switch closed for good
# L54b1: sorgente = the timer of psu.net itself (ADR-102, in the source since L54b1): no TIMER_AN,
# its parts through the MAP like every other part. Refused on a netlist with the micro, and the
# three modes above refused on a netlist with the timer (they would add TIMER_AN to it)
ap.add_argument("--timer", choices=("micro", "comparatori", "diretto", "sorgente"), default="micro")
# L54b2: the comparators of the source with TI's model (models/comparator/tlv1701_ngspice.lib, its
# named variant TLV1701_OC: limitations #77) instead of CMPOD, through the wrapper CMPTI with
# CMPOD's pins (inp inn out vcc gnd), so that the instance names and the output token that modi.py
# moves stay the same. costruttore = the twelve channels of U513-U515; costruttore18 = those and the
# six of U505 / U506 / U508. Only with --timer sorgente; comportamentale leaves the deck as it was
ap.add_argument("--comparatore", choices=("comportamentale", "costruttore", "costruttore18"),
                default="comportamentale")
# L54a: a mains factor on ANY sequence case (holes included), e.g. 0.9 / 1.1 (the case's own
# "fattore", accensione_m10's, if any, is refused together with this)
ap.add_argument("--rete", type=float, default=None)
# L54a: the settling before the event (TSS = TE). The analog timers power up for real from t = 0
# (the micro's preamble put it in MUSICA at 1.0 s): rails at ~1.4 s, then the 0.47 s of AT_PGT -
# they run with 3.0; every micro deck keeps 2.0
ap.add_argument("--tss", type=float, default=2.0)
# L54a: also write T2's EMF and its sense current (L41b1's VT2_sns), for the standby power
# read on a sequence deck; without it the decks are unchanged
ap.add_argument("--sonda-t2", dest="sonda_t2", action="store_true")
# L54a: where VRELAY comes from with --timer diretto. t2 = today's small transformer, switched with
# the mains; t1 = no T2 (its EMF at 0): an auxiliary full-wave rectifier on T1's two secondaries
# into RECT_V (two DBR diodes, the centre tap is GND), so that the coils keep their own reservoir
# (C_V) and never draw from the audio rails' raw (ADR-048 point 3), and the mains detector reads T1
ap.add_argument("--vrelay-da", dest="vrelay_da", choices=("t2", "t1"), default="t2")
ARG = ap.parse_args()
SERIE2 = set(ARG.serie2.split(",")) if ARG.serie2 else set()
DOPPI = {}      # ref -> (node a, node b, mid): filled by element(), read by applica_guasto()
W_2N7002 = "2000u" if ARG.n2n7002 == "l41a" else "571u"
MOS = dict(x.split("=") for x in ARG.mos.split(",")) if ARG.mos else {}
assert set(MOS.values()) <= {"DMN6075S"}, MOS
CNR_OVR = dict(x.split("=") for x in ARG.cnr.split(",")) if ARG.cnr else {}
R_MUTECOIL = (1315 / 3.0 if ARG.bobine == "g6k"
              else 1.0 / (2 / 1315.0 + 1 / 1029.0))
# L45d2b2a: the audio board's capacitance on the rails (capacita_rail.py on preamp_audio.net):
# per rail 8 x (100 uF electrolytic + 100 nF) = 800.8 uF direct; on VPLUS also the eight RC cells
# of ADR-056 / ADR-086, 1000 uF behind 2 x 20 ohm each, lumped as 8000 uF behind 1.25 ohm. Nominal
# values, no ESR (declared). The benches before L45d2b2a had none of it: --cap-audio no.
CAP_AUDIO = (["CAUDIOP vplus 0 800.8u", "RCELLE vplus vpf_celle 1.25", "CCELLE vpf_celle 0 8000u",
              "CAUDIOM 0 vminus 800.8u"] if ARG.cap_audio == "si" else [])

# L51b: the audio board's load is read from carico.txt at the root of the lot
# (this folder's parent), so that the same script, byte for byte, runs today's
# load (L51b/: the rails of today's tb_op, 8 x |i(vpp)| and 8 x |i(vmm)|, and
# the selector's coil on VRELAY, L48a) and the load before (L51b-prima/: 265 mA
# per rail, L41a, and 42.4 mA of the rest, L47c2a), which must give back the
# folders of L47c2a and L47c2b2. No carico.txt, no deck: there is no default.
_CARICO = ARG.file_carico or os.path.join(QUI, "..", "carico.txt")
if not os.path.exists(_CARICO):
    raise SystemExit("RIFIUTATO: manca %s (i_piu_mA, i_meno_mA, resto_mA)" % _CARICO)
_C = {}
for _r in open(_CARICO):
    _r = _r.split("#")[0].split()
    if len(_r) == 2:
        _C[_r[0]] = _r[1]
# L56: an OPTIONAL metodo_u503_min, the method of guasto_u503_min alone. On L56's load (+10 mA
# per rail, ADR-067) gear stops it at 2.47 s ("Timestep too small" on b.xu508b.bq) while
# trap + gmin 1e-8 runs it in 9 s, and the nominal case is the other way round - the same split
# L51b found the other way (../sonda_u503/esiti_l56.tsv). Without the key, L51b's behaviour.
if not ({"i_piu_mA", "i_meno_mA", "resto_mA", "metodo_u503"} <= set(_C)
        <= {"i_piu_mA", "i_meno_mA", "resto_mA", "metodo_u503", "metodo_u503_min"}):
    raise SystemExit("RIFIUTATO: %s deve avere i_piu_mA, i_meno_mA, resto_mA, metodo_u503" % _CARICO)
I_PIU, I_MENO, I_RESTO = (float(_C[k]) / 1000 for k in ("i_piu_mA", "i_meno_mA", "resto_mA"))
# L51b: the method of the two U503-off cases goes with the load. L47c2b2 needed
# trap + gmin 1e-9 on its load (gear did not end, > 45 min); on today's load it
# is the other way round - trap does not end guasto_u503 (> 300 s, even stopped
# at TE + 0.5 s) and stops guasto_u503_min at 2.968 s, while gear, every other
# sequence deck's method, runs both in ~12 s (L51b/sonda_u503/: gear against
# trap + gmin 1e-8 on the nominal case, the jack, the gain and V+ < 10.6 V at
# the same instants, the rails within 0.5 mV). carico.txt says which: "trap" in
# L51b-prima/ (L47c2b2's), "gear" in L51b/.
if _C["metodo_u503"] not in ("trap", "gear"):
    raise SystemExit("RIFIUTATO: metodo_u503 e' trap o gear, non %r" % _C["metodo_u503"])
U503_NUM = (dict(metodo="trap", gmin="1e-9") if _C["metodo_u503"] == "trap" else {})
U503_NUM_MIN = U503_NUM
if "metodo_u503_min" in _C:
    if _C["metodo_u503_min"] != "trap8":
        raise SystemExit("RIFIUTATO: metodo_u503_min e' trap8, non %r" % _C["metodo_u503_min"])
    U503_NUM_MIN = dict(metodo="trap", gmin="1e-8")
# the counterfactual takes L41a's load off today's: it is L41a's only on the
# load before (265 / 265 / 42.4 mA); on any other it would be neither
if ARG.carico == "l41a" and tuple(round(x * 1e4) for x in (I_PIU, I_MENO, I_RESTO)) != (2650, 2650, 424):
    raise SystemExit("RIFIUTATO: --carico l41a solo col carico di prima (265 / 265 / 42,4 mA)")
TSS = ARG.tss           # s of settling before any event (C_RAW at ~0.27 A); 2.0 before L54a
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
# L54b1: the mode and the netlist must agree (see --timer)
_HA_TIMER = any(c["part"] == "LM339" for c in COMPS.values())
_HA_MICRO = any(c["part"].startswith("ATtiny") for c in COMPS.values())
if (ARG.timer == "sorgente") != _HA_TIMER or (ARG.timer == "sorgente" and _HA_MICRO):
    raise SystemExit("RIFIUTATO: --timer %s su %s (temporizzatore %s, micro %s)"
                     % (ARG.timer, ARG.net, _HA_TIMER, _HA_MICRO))
# L45d2b2b1: --valore REF=val[,REF=val]: a part's value instead of the netlist's (an option of
# ADR-074 with R550 / R551 at another value); the part must exist
for _x in (ARG.valore.split(",") if ARG.valore else []):
    _r, _v = _x.split("=")
    assert _r in COMPS, _r
    COMPS[_r] = dict(COMPS[_r], value=_v)


def pn(ref, pin):
    # L45d2b2b2: a probed pin reaches its net through the 0 V source VSI<ref>_<pin> (sonde_i_righe)
    if (ref, pin) in SONDE_I:
        return "si_%s_%s" % (ref.lower(), pin)
    return node(PN.get((ref, pin), "nc_%s_%s" % (ref.lower(), pin)))


# L45d2b2b2: the probed pins, in the fault cases only (ADR-075's parts; the header says why each)
_SONDE_DEF = ("Q501:3,Q502:3,Q503:3,Q505:3,D507:2,D509:2,U507:1,Q504:3,Q504:1,U503:1,U504:3"
              if (ARG.caso or "").startswith("f_") else "no")
# ADR-094 in the netlist: the second 5 V regulator's output too
if _SONDE_DEF != "no" and ("U512", "3") in PN:
    _SONDE_DEF += ",U512:3"
SONDE_I = set()
for _x in ((ARG.sonde or _SONDE_DEF).split(",") if (ARG.sonde or _SONDE_DEF) != "no" else []):
    _r, _p = _x.split(":")
    assert (_r, _p) in PN, ("--sonde: pin assente", _x)
    SONDE_I.add((_r, _p))


def sonde_i_righe():
    """The 0 V sources of SONDE_I: from the net to the probed pin (i > 0 = into the pin)."""
    return ["VSI%s_%s %s si_%s_%s 0" % (r, p, node(PN[(r, p)]), r.lower(), p) for r, p in sorted(SONDE_I)]


def farad(v):
    m = re.match(r"^\s*([0-9]*\.?[0-9]+)\s*([munp]?)", v)
    return float(m.group(1)) * {"m": 1e-3, "u": 1e-6, "n": 1e-9, "p": 1e-12, "": 1.0}[m.group(2)]


def cnr(ref):
    """L45d2b2a: the NR capacitor of a TPS7A (pin 14) from the netlist - exactly one capacitor
    on that net, or the generator refuses - unless --cnr overrides it. (value, its ref)."""
    n = PN[(ref, "14")]
    cs = [r for (r, p), x in PN.items() if x == n and COMPS[r]["part"] == "C"]
    assert len(cs) == 1, (ref, n, cs)
    if ref in CNR_OVR:
        return farad(CNR_OVR[ref]), cs[0] + " (--cnr)"
    return farad(COMPS[cs[0]]["value"]), cs[0]


SS_LOG = []          # L45d2b2a: what each regulator's soft-start is, written in the deck's header


RPRE = dict((k, float(v)) for k, v in (x.split("=") for x in ARG.rpre.split(","))) if ARG.rpre else {}
# L45d2b2b1: the Schottkys between each rail regulator's OUT and IN get a current probe, in the
# fault cases only (every other deck stays L45d2b2a's, byte for byte)
SONDA_D = {"D510", "D511"} if (ARG.caso or "").startswith("f_") else set()
# ADR-093 in the netlist: the second SB340 on each pin (D513 / D514) and the series ones (D515 / D516)
if SONDA_D:
    SONDA_D |= {r for r in ("D513", "D514", "D515", "D516") if r in COMPS}
# L45d2b2b1: --variante uscita - the regulator's OUT pin node, the rail after the series diode
PIN = {"U501": "vplus_reg", "U502": "vminus_reg"} if ARG.variante == "uscita" else {}
PIN_DI = {"C511": "U501", "D510": "U501", "C512": "U502", "D511": "U502"}
if PIN:
    assert ARG.ss == "si", "--variante uscita has only the soft-start's regulators"


def modello(arg, nome):
    """--dserie / --dclamp: a .model line from "Is,N,Rs", or DSCH's values (L41a)."""
    i_s, n, rs = (arg or "1e-6,1.1,0.05").split(",")
    return ".model %s D(Is=%s N=%s Rs=%s)" % (nome, i_s, n, rs)


def al_piedino(ref, righe):
    """--variante uscita: in the lines of C511 / C512 / D510 / D511 the rail's node becomes the
    regulator's pin node (exactly one token each, asserted)."""
    reg = PIN_DI.get(ref)
    if not PIN or reg is None:
        return righe
    rail = pn(reg, "1")
    out, n = [], 0
    for r in righe:
        p = r.split()
        k = [i for i in (1, 2) if p[i] == rail]
        n += len(k)
        for i in k:
            p[i] = PIN[reg]
        out.append(" ".join(p))
    assert n == 1, (ref, righe)
    return out


def serie(ref):
    """--variante uscita: the series Schottky (with its 0 V current probe) from the pin to the rail
    (U501, anode on the pin) or from the rail to the pin (U502, anode on the rail)."""
    if ref not in PIN:
        return []
    rail, x = pn(ref, "1"), ref[1:]
    a, k = (PIN[ref], rail) if ref == "U501" else (rail, PIN[ref])
    return ["DSER%s %s ser_%s DSERIE" % (x, a, x), "VSSER%s ser_%s %s 0" % (x, x, k)]


def ingresso(ref, n):
    """L45d2b2a: the regulator's IN node - <n>_pre behind a --rpre resistor, or n itself."""
    return n + "_pre" if ref in RPRE else n


def rpre_righe(ref, n):
    """The resistor, and 10 uF ceramic at the regulator's pin behind it: on the board the input
    ceramic (C509 / C510) sits at the pin. Here C509 / C510 stay on the reservoir's side too:
    10 uF more on a 4700 uF node (declared). Without it the node had no capacitance and the
    solver stopped at 0.7 ms ("Timestep too small", raw_p_pre)."""
    if ref not in RPRE:
        return []
    g = node(PN[(ref, "7")])
    return ["RPRE_%s %s %s_pre %g" % (ref, n, n, RPRE[ref]),
            "CPRE_%s %s_pre %s 10u" % (ref, n, g)]


def regolatore(ref, tipo, nodi, vset, vdo, ilim, iq):
    """L45d2b2a: a TPS7A as REGP / REGM (L41a's, --ss no) or with its soft-start (REGPSS / REGMSS:
    the reference from the NR capacitor, SBVS204G eq. 5 / SBVS169D eq. 1)."""
    if ARG.ss == "no":
        return "X%s %s %s %s en_%s %s VSET=%g VDO=%g ILIM=%g IQ=%s" % (
            (ref,) + nodi + (ref.lower(), tipo, vset, vdo, ilim, iq))
    c, cref = cnr(ref)
    # L45d2b2b1: --variante uscita - OUT on the pin node, the rail as the sense (REGPSSF / REGMSSF)
    f, sens = ("F", " " + nodi[1]) if ref in PIN and ARG.senso == "rail" else ("", "")
    if ref in PIN:
        nodi = (nodi[0], PIN[ref], nodi[2])
        vset += ARG.dvset
    if tipo == "REGP":
        tau = 1e5 * c
        SS_LOG.append("%s %s = %.4g F: tau %.4g s, t_SS = tau ln((%g + 5) / 5) = %.4g s (eq. 5)"
                      % (ref, cref, c, tau, vset, tau * math.log((vset + 5) / 5.0)))
        return "X%s %s %s %s en_%s%s REGPSS%s VSET=%g VDO=%g ILIM=%g IQ=%s TAU=%.6g" % (
            (ref,) + nodi + (ref.lower(), sens, f, vset, vdo, ilim, iq, tau))
    tss = 1.2e-3 * c / 1e-9
    SS_LOG.append("%s %s = %.4g F: t_SS = 1.2 ms/nF = %.4g s (eq. 1)" % (ref, cref, c, tss))
    return "X%s %s %s %s en_%s%s REGMSS%s VSET=%g VDO=%g ILIM=%g IQ=%s TSS=%.6g" % (
        (ref,) + nodi + (ref.lower(), sens, f, vset, vdo, ilim, iq, tss))


MCU_OUT = ("MUTE_REQ", "PERMIT_REQ", "MAINS_REQ", "VRELAY_EN")
# the timing parts whose values the min corner moves (the netlist gives the
# nominal; the corner is declared here and in the deck name)
ANGOLO = {"C528": 0.95, "R534": 0.99, "C529": 0.95, "R536": 0.99} if ARG.angolo == "min" else {}


def element(ref, c):
    part, val = c["part"], c["value"]
    k = ANGOLO.get(ref)
    if part == "R":
        v = sval(val) if k is None else "{%s*%g}" % (sval(val), k)
        if ref in SERIE2:
            m = "%s_m" % ref.lower()
            DOPPI[ref] = (node(PN[(ref, "1")]), node(PN[(ref, "2")]), m)
            return ["R%s %s %s {%s/2}" % (ref, pn(ref, "1"), m, v),
                    "R%sB %s %s {%s/2}" % (ref, m, pn(ref, "2"), v)]
        return ["R%s %s %s %s" % (ref, pn(ref, "1"), pn(ref, "2"), v)]
    if part == "C":
        v = sval(val) if k is None else "{%s*%g}" % (sval(val), k)
        return ["C%s %s %s %s" % (ref, pn(ref, "1"), pn(ref, "2"), v)]
    if part == "C_Polarized":
        # ESR 30 mOhm, and the value derated -20 % (ADR-046: >= 1500 uF EFFECTIVE)
        return ["C%s %s %s_esr {0.8*%s}" % (ref, pn(ref, "1"), ref.lower(), sval(val)),
                "R%s_esr %s_esr %s 0.03" % (ref, ref.lower(), pn(ref, "2"))]
    if part == "D":
        if ref in SERIE2:
            m = "%s_m" % ref.lower()
            DOPPI[ref] = (node(PN[(ref, "2")]), node(PN[(ref, "1")]), m)
            return ["D%s %s %s D1N914" % (ref, pn(ref, "2"), m), "D%sB %s %s D1N914" % (ref, m, pn(ref, "1"))]
        return ["D%s %s %s D1N914" % (ref, pn(ref, "2"), pn(ref, "1"))]
    if part == "D_Schottky":
        mod = "DBAT54" if val == "BAT54" else "DSCH"
        if val == "SB340":
            mod = "DSB340"      # L45d2b2b1: ADR-093's parts, from the netlist
        if ARG.dclamp and ref in ("D510", "D511"):
            mod = "DCLAMP"      # L45d2b2b1: --dclamp
        if ref in SONDA_D:
            # L45d2b2b1: a 0 V source in series, i(vsd510) / i(vsd511) = the diode's forward current
            return ["D%s %s sd_%s %s" % (ref, pn(ref, "2"), ref.lower(), mod),
                    "VSD%s sd_%s %s 0" % (ref, ref.lower(), pn(ref, "1"))]
        return ["D%s %s %s %s" % (ref, pn(ref, "2"), pn(ref, "1"), mod)]
    if part == "D_Zener":
        return ["D%s %s %s DZ24" % (ref, pn(ref, "2"), pn(ref, "1"))]
    if part == "D_Bridge_+AA-":
        p, a, b, m = (pn(ref, x) for x in "1234")
        return ["D%sa %s %s DBR" % (ref, a, p), "D%sb %s %s DBR" % (ref, b, p),
                "D%sc %s %s DBR" % (ref, m, a), "D%sd %s %s DBR" % (ref, m, b)]
    if part == "2N7002":
        # L45d2b2b2: --mos (another part in its place), --n2n7002 (the saturation, see above)
        if ref == "Q503" and ARG.rk:
            return ["MQ503 q503_rk %s %s %s %s L=1u" % (pn(ref, "1"), pn(ref, "2"), pn(ref, "2"),
                                                       "MDMN6075 W=1u" if MOS.get(ref) == "DMN6075S"
                                                       else "MNGEN W=%s" % W_2N7002),
                    "RRK %s q503_rk %g" % (pn(ref, "3"), ARG.rk)]
        if MOS.get(ref) == "DMN6075S":
            return ["M%s %s %s %s %s MDMN6075 W=1u L=1u" % (ref, pn(ref, "3"), pn(ref, "1"),
                                                           pn(ref, "2"), pn(ref, "2"))]
        return ["M%s %s %s %s %s MNGEN W=%s L=1u" % (ref, pn(ref, "3"), pn(ref, "1"),
                                                     pn(ref, "2"), pn(ref, "2"), W_2N7002)]
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
        m = "CMPTI" if ARG.comparatore == "costruttore18" else "CMPOD"
        return ["X%sa %s %s %s %s %s %s" % (ref, pn(ref, "3"), pn(ref, "2"), pn(ref, "1"), v, g, m),
                "X%sb %s %s %s %s %s %s" % (ref, pn(ref, "5"), pn(ref, "6"), pn(ref, "7"), v, g, m)]
    if part == "LM339":
        # L54b1: the TLV1704 of ADR-102 on the LM339 symbol (SBOS589D p. 5): channels a-d =
        # (+, -, out) 5 4 2, 7 6 1, 9 8 14, 11 10 13; V+ 3, V- 12. The same CMPOD as TIMER_AN's
        v, g = pn(ref, "3"), pn(ref, "12")
        m = "CMPOD" if ARG.comparatore == "comportamentale" else "CMPTI"
        return ["X%s%s %s %s %s %s %s %s" % (ref, u, pn(ref, a), pn(ref, b), pn(ref, o), v, g, m)
                for u, (a, b, o) in zip("abcd", (("5", "4", "2"), ("7", "6", "1"),
                                                 ("9", "8", "14"), ("11", "10", "13")))]
    # L47c2a: MCP6004 (U511) and MCP4822 (U510) are gone (ADR-062); if either
    # came back it would fall to the refusal at the end
    if part.startswith("ATtiny"):
        v5, g = pn(ref, "1"), pn(ref, "20")
        out = ["B%sq %s %s I = V(iq_mcu)" % (ref, v5, g)]
        for (r, p), n in sorted(PN.items()):
            if r != ref or p in ("1", "20"):
                continue
            if n in MCU_OUT and ARG.timer == "micro":
                x = n.lower()
                out.append("B%s_%s 0 %s I = V(drv_%s)*(V(set_%s)*V(%s,%s) - V(%s,%s))/50"
                           % (ref, p, x, x, x, v5, g, x, g))
            else:
                out.append("R%s_%s %s %s 1G" % (ref, p, node(n), g))
        return out
    if part == "LM4040DBZ-2.5":
        return ["X%s %s %s SHUNT25" % (ref, pn(ref, "1"), pn(ref, "2"))]
    if part.startswith("TPS7A4701"):
        # L45d2b2b1: 15.3 V since ADR-093 (the rail behind the series SB340)
        vset = {"TPS7A4701 15V": 15.0, "TPS7A4701 12V": 12.0, "TPS7A4701 15.3V": 15.3}[val]
        # ANY-OUT: the grounded weights must give vset (checked here, from the netlist)
        w = {"4": 6.4, "5": 6.4, "6": 3.2, "8": 1.6, "9": 0.8, "10": 0.4, "11": 0.2, "12": 0.1}
        gnd = PN[(ref, "7")]
        got = 1.4 + sum(x for p, x in w.items() if PN.get((ref, p)) == gnd)
        assert abs(got - vset) < 1e-6, (ref, got, vset)
        return [regolatore(ref, "REGP", (ingresso(ref, pn(ref, "15")), pn(ref, "1"), node(gnd)), vset, 0.3, 1, "0.58m"),
                "VEN%s en_%s 0 pwl(0 1 1000 1)" % (ref, ref.lower())] + rpre_righe(ref, pn(ref, "15"))
    if part.startswith("TPS7A3301"):
        # FB divider from the netlist: Vout = -1.176 * (1 + Rtop / Rbot)  [ASSUMED reference]
        fb = PN[(ref, "3")]
        rs = {r: COMPS[r]["value"] for (r, p), n in PN.items() if n == fb and COMPS[r]["part"] == "R"}
        top = [r for r in rs if PN[(r, "1")] == PN[(ref, "1")] or PN[(r, "2")] == PN[(ref, "1")]]
        bot = [r for r in rs if r not in top]
        rt, rb = (float(sval(rs[x[0]]).replace("k", "e3")) for x in (top, bot))
        vset = 1.176 * (1 + rt / rb)
        return [regolatore(ref, "REGM", (ingresso(ref, pn(ref, "15")), pn(ref, "1"), pn(ref, "7")), vset, 0.3, 1, "1m"),
                "VEN%s en_%s 0 pwl(0 1 1000 1)" % (ref, ref.lower())] + rpre_righe(ref, pn(ref, "15"))
    if part.startswith("MCP1703"):
        vset = ARG.v5
        if ARG.u504doppio:
            # L45d2b2b2: two in series; the second runs in dropout. REGP's dropout is a constant VDO,
            # 0.6 V for U504 (L41a): on the second it would give 4.4 V. DS20005122B p4: 650 mV max at
            # 250 mA, ~2.6 ohm, i.e. ~16 mV at the logic's ~6 mA: VDO 0.02 V on U504B (declared; the
            # quiescent current in dropout is not in the datasheet - 2 uA as the first)
            DOPPI[ref] = (node(PN[(ref, "1")]), node(PN[(ref, "3")]), "v5_m")  # the NETS: a probe renames the pin (first run)
            return ["X%s %s v5_m %s en_%s REGP VSET=%g VDO=0.6 ILIM=0.25 IQ=2u" % (
                        ref, pn(ref, "1"), pn(ref, "2"), ref.lower(), vset),
                    "X%sB v5_m %s %s en_%s REGP VSET=%g VDO=0.02 ILIM=0.25 IQ=2u" % (
                        ref, pn(ref, "3"), pn(ref, "2"), ref.lower(), vset),
                    "C%sB v5_m %s 1u" % (ref, pn(ref, "2")),
                    "VEN%s en_%s 0 pwl(0 1 1000 1)" % (ref, ref.lower())]
        # ADR-094 in the netlist: U512 after U504 (IN on V5_PRE) runs in dropout: VDO 0.02 V as
        # --u504doppio's U504B (declared there)
        vdo = 0.02 if PN.get((ref, "1")) == "V5_PRE" else 0.6
        return ["X%s %s %s %s en_%s REGP VSET=%g VDO=%g ILIM=0.25 IQ=2u" % (
                    ref, pn(ref, "1"), pn(ref, "3"), pn(ref, "2"), ref.lower(), vset, vdo),
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
* L45d2b2a (NC-063): the same two regulators WITH their soft-start. A reference node r (1 F) is
* charged while EN is high and IN is above the UVLO, and discharged in 1 ms otherwise (ASSUMED:
* the datasheets do not say how fast NR is discharged); the output regulates to min(VSET, V(r)).
*  - TPS7A4701 (SBVS204G, UVLO 2.67 V rising): r charges by RC, time constant TAU = 100 kOhm x C_NR,
*    towards VSET + 5 V, so that it reaches VSET at TAU ln((VSET + 5) / 5) - eq. 5, the only figure
*    the datasheet gives (a typical device; the shape before it is ASSUMED);
*  - TPS7A3301 (SBVS169D, UVLO -2 V): r rises linearly to VSET in TSS = 1.2 ms per nF - eq. 1 (the
*    linear ramp is ASSUMED, as fig. 29 draws it).
.subckt REGPSS in out gnd en VSET=15 VDO=0.3 ILIM=1 IQ=1m TAU=1
* (a 0 V sense on IN: i(v.x<ref>.vsns) is the current the regulator draws, positive)
Vsns in ins 0
Bon on 0 V = V(en)*0.5*(1+tanh((V(ins,gnd)-2.67)/0.05))
Cr r 0 1
Br 0 r I = V(on)*({{VSET}}+5-V(r))/{{TAU}} - (1-V(on))*V(r)/1m
Bo gnd out I = V(en)*min({{ILIM}}, max(0, 1000*(min(min({{VSET}}, V(r)), V(ins,gnd)-{{VDO}}) - V(out,gnd))))
Bi ins gnd I = V(en)*min({{ILIM}}, max(0, 1000*(min(min({{VSET}}, V(r)), V(ins,gnd)-{{VDO}}) - V(out,gnd)))) + {{IQ}}*(V(ins,gnd)>1)
Rl out gnd 1meg
.ends
.subckt REGMSS in out gnd en VSET=15 VDO=0.3 ILIM=1 IQ=1m TSS=1
Vsns ins in 0
Bon on 0 V = V(en)*0.5*(1+tanh((V(gnd,ins)-2)/0.05))
Cr r 0 1
Br 0 r I = V(on)*{{VSET}}/{{TSS}}*0.5*(1-tanh((V(r)-{{VSET}}-0.5)/0.05)) - (1-V(on))*V(r)/1m
Bo out gnd I = V(en)*min({{ILIM}}, max(0, 1000*(min(min({{VSET}}, V(r)), V(gnd,ins)-{{VDO}}) - V(gnd,out))))
Bi gnd ins I = V(en)*min({{ILIM}}, max(0, 1000*(min(min({{VSET}}, V(r)), V(gnd,ins)-{{VDO}}) - V(gnd,out)))) + {{IQ}}*(V(gnd,ins)>1)
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

# L45d2b2b1: the models of ADR-074's options, after MODELS and only when an option asks (the decks
# without options stay L45d2b2a's byte for byte). REGPSSF / REGMSSF are REGPSS / REGMSS regulating a
# SENSE node fb (the rail after the series diode, as the feedback divider / SENSE would on the board)
# instead of OUT; the dropout still acts at the pin: the pin cannot go past IN - VDO.
MODELLI_074 = []
if PIN:
    MODELLI_074 += [modello(ARG.dserie, "DSERIE"), r"""
.subckt REGPSSF in out gnd en fb VSET=15 VDO=0.3 ILIM=1 IQ=1m TAU=1
Vsns in ins 0
Bon on 0 V = V(en)*0.5*(1+tanh((V(ins,gnd)-2.67)/0.05))
Cr r 0 1
Br 0 r I = V(on)*({VSET}+5-V(r))/{TAU} - (1-V(on))*V(r)/1m
Bo gnd out I = V(en)*min({ILIM}, max(0, 1000*min(min({VSET}, V(r)) - V(fb,gnd), V(ins,gnd)-{VDO}-V(out,gnd))))
Bi ins gnd I = V(en)*min({ILIM}, max(0, 1000*min(min({VSET}, V(r)) - V(fb,gnd), V(ins,gnd)-{VDO}-V(out,gnd)))) + {IQ}*(V(ins,gnd)>1)
Rl out gnd 1meg
.ends
.subckt REGMSSF in out gnd en fb VSET=15 VDO=0.3 ILIM=1 IQ=1m TSS=1
Vsns ins in 0
Bon on 0 V = V(en)*0.5*(1+tanh((V(gnd,ins)-2)/0.05))
Cr r 0 1
Br 0 r I = V(on)*{VSET}/{TSS}*0.5*(1-tanh((V(r)-{VSET}-0.5)/0.05)) - (1-V(on))*V(r)/1m
Bo out gnd I = V(en)*min({ILIM}, max(0, 1000*min(min({VSET}, V(r)) - V(gnd,fb), V(gnd,ins)-{VDO}-V(gnd,out))))
Bi gnd ins I = V(en)*min({ILIM}, max(0, 1000*min(min({VSET}, V(r)) - V(gnd,fb), V(gnd,ins)-{VDO}-V(gnd,out)))) + {IQ}*(V(gnd,ins)>1)
Rl out gnd 1meg
.ends""".strip("\n")]
if ARG.dclamp:
    MODELLI_074.append(modello(ARG.dclamp, "DCLAMP"))
# L45d2b2b2: DMN6075S (Diodes Rev 7-2 2025) as LEVEL 1, declared: VTO 2.0 V (1.3-2.7 V, p2), K 3.8 A/V^2
# from fig. 1 (~11-12 A at VDS 2 V, VGS 4.5 V, read by eye): RDS(on) 0.105 ohm at 4.5 V (0.12 max, p2)
if MOS:
    MODELLI_074.append(".model MDMN6075 NMOS (LEVEL=1 VTO=2.0 KP=3.8 LAMBDA=0.02)")
# ADR-093's SB340 when the netlist has it: the fit of Vishay 88719 fig. 3, 25 C typical, three points
# read from the curve (0.1 A 0.27 V, 1 A 0.37 V, 10 A 0.58 V; +-0.03-0.05 V) by the bom-component-
# manager in L45d2b2b1 - declared, not a vendor model (none published, not found)
if any(c["part"] == "D_Schottky" and c["value"] == "SB340" for c in COMPS.values()):
    MODELLI_074.append(".model DSB340 D(Is=8.7e-5 N=1.47 Rs=0.0136)")
# L54b2: TI's comparator (see --comparatore); TIMER_AN's CMPOD lines are not touched, so the option
# is refused on the modes that use them
if ARG.comparatore != "comportamentale":
    if ARG.timer != "sorgente":
        raise SystemExit("RIFIUTATO: --comparatore %s solo con --timer sorgente" % ARG.comparatore)
    MODELLI_074 += [".include %s/models/comparator/tlv1701_ngspice.lib" % REPO,
                    ".subckt CMPTI inp inn out vcc gnd",
                    "X1 inp inn vcc gnd out TLV1701_OC",
                    ".ends"]


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
             MODELS.format(repo=REPO, vref=VREF_SHUNT)] + MODELLI_074
    for ref in sorted(COMPS):
        righe += al_piedino(ref, element(ref, COMPS[ref])) + serie(ref)
    righe += ["* L45d2b2a soft-start: " + s for s in SS_LOG] + CAP_AUDIO
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
        "IPLUS vplus 0 dc 0 pwl(0 0 0.5 %g)" % I_PIU,
        "IMINUS 0 vminus dc 0 pwl(0 0 0.5 %g)" % I_MENO,
        "RMUTECOIL vrelay mute_cmd %g" % R_MUTECOIL,
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
    # L45d2b2a: to TE + 2.5 s (was 1.3): the soft-start puts the rails at ~1.2-1.4 s, and the
    # firmware's GUASTO without rails comes at TE + 2 s (timer_spec.md 4.1)
    "accensione": dict(front=[(0, 0), (TE, 0), (TE + 1e-6, 1)], sw3=1, tf=TE + 2.5, pre=None),
    # L45d2b2a: the same at mains -10 % (both transformers), the factor of L41a's rete cases
    "accensione_m10": dict(front=[(0, 0), (TE, 0), (TE + 1e-6, 1)], sw3=1, tf=TE + 2.5, pre=None,
                           fattore=0.9),
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
    # after it is TE + 1.1 (L47c2b2: confirmed by the user, «1,1 s»)
    "spegnimento_l": dict(front=[(0, 1), (TE, 1), (TE + 1e-6, 0)], sw3=1, tf=TE + 1.1,
                          pre="musica"),
    # the mains gone at TE for good
    "perdita": dict(front=1, sw3=1, buco=1000.0, tf=TE + 1.0, pre="musica"),
    "perdita_min": dict(front=1, sw3=1, buco=1000.0, tf=TE + 1.0, pre="musica", angolo="min"),
    # a regulator off with the mains present: + rail, VRELAY_REG
    "guasto_u501": dict(front=1, sw3=1, spento={"U501": TE}, tf=TE + 1.0, pre="musica"),
    # L47c2b2: U503 off with the method trap and gmin 1e-9. With gear (every
    # other sequence deck) the first pass never ended: 12 s up to TE + 0.5 s,
    # then > 45 min with no end between TE + 0.50 and 0.55 s, where V5 is down
    # to ~0.9 V and the micro's domain floats (MUTE_G_IN ~0.92 V, ADC_MD
    # ringing). L41c ran with the LDR drive's loads on V5 (U510 / U511), gone
    # with ADR-062. trap alone ran the nominal case (24 s) but not the corner
    # one; trap with gmin 1e-9 runs both (~17 s). Up to TE + 0.5 s it is
    # gear's, on both: the jack, the gain and V+ < 10.6 V at the same instants,
    # the rails within 0.54 mV. gear + rshunt 1e12 and gear with a 5 us step
    # did not end in 3 min. 1 nS across a junction at 0.5 V is 0.5 nA: no
    # current of the board is that small since the LDR strings are gone
    # (L47c2b2 README, «U503 e il metodo»)
    "guasto_u503": dict(front=1, sw3=1, spento={"U503": TE}, tf=TE + 1.0, pre="musica",
                        **U503_NUM),
    "guasto_u503_min": dict(front=1, sw3=1, spento={"U503": TE}, tf=TE + 1.0, pre="musica",
                            angolo="min", **U503_NUM_MIN),
    # L54a: the mains switched on at TE with everything cold (the power-up of --timer diretto,
    # and of the other two after a long blackout)
    "fredda": dict(front=1, sw3=1, fredda=True, tf=TE + 2.5, pre=None),
    # L54a: the front switched on with U501 dead from the start (timer_spec.md 4.1: no rails within
    # 2 s = GUASTO, K501 off); and a fault (U502 off at TE) reset from the front - off at TE + 0.5,
    # on again at TE + 1.0 with U502 still dead: the power-up again, then the latch again
    "accensione_u501": dict(front=[(0, 0), (TE, 0), (TE + 1e-6, 1)], sw3=1, tf=TE + 3.0, pre=None,
                            spento={"U501": 1e-3}),
    "fredda_u501": dict(front=1, sw3=1, fredda=True, tf=TE + 3.0, pre=None, spento={"U501": 1e-3}),
    "ritenuta_frontale": dict(front=[(0, 1), (TE + 0.5, 1), (TE + 0.5 + 1e-6, 0), (TE + 1.0, 0),
                                     (TE + 1.0 + 1e-6, 1)], sw3=1, u502=TE, tf=TE + 3.5, pre="musica"),
    # L30's counterfactual: no D (C528 = 10 pF), the mains gone
    "cf_nodelta": dict(front=1, sw3=1, buco=1000.0, tf=TE + 1.0, pre="musica", c528="10p"),
    # U503's output shorted to ground: C523 (on VRELAY_REG) goes with it
    "corto_u503": dict(front=1, sw3=1, corto=TE, tf=TE + 1.0, pre="musica"),
}


# ---- L45c1: the fault cases (modi.py)
sys.path.insert(0, QUI)
import modi  # noqa: E402

GUASTI = {c[0]: c for c in modi.SIMULATI}


def caso_fmea(nome):
    """CASI_SEQ's dict for f_<ref>_<modo>_<evento>: the event's switches, the fault's instant
    (TE with the event mus, 0 - latent - with any other) and its primitive."""
    ev = nome.split("_")[-1]
    e = dict(modi.EVENTI[ev])
    # L45c2: modi.TF shortens a case that stops after everything is off (modi.py)
    c = dict(sw3=1, pre="musica", tf=TE + modi.TF.get(nome, e["tf"]))
    c["front"] = [(0, 1), (TE, 1), (TE + 1e-6, 0)] if e["front"] == "giu" else 1
    # L45c2: the mute inserted from the front (SW3 opens at TE)
    c["sw3"] = [(0, 1), (TE, 1), (TE + 1e-6, 0)] if e["sw3"] == "giu" else 1
    if e.get("buco"):
        c["buco"] = e["buco"]
    if e.get("u502"):
        c["u502"] = TE
    if e.get("spento"):
        c["spento"] = {e["spento"]: TE}
        # L45c2: U503 off takes guasto_u503's method (carico.txt)
        if e["spento"] == "U503":
            c.update(U503_NUM)
    c["guasto"] = GUASTI[nome][3]
    c["t_guasto"] = TE if ev.startswith("mus") else 0.0
    # L45d2b2b1: musm10 / musp10, the mains factor from t = 0 (as accensione_m10)
    if e.get("fattore"):
        c["fattore"] = e["fattore"]
    return c


if ARG.caso and ARG.caso.startswith("f_"):
    if ARG.caso not in GUASTI:
        raise SystemExit("genera_tb_psu: %s non e' in modi.py - rifiutato" % ARG.caso)
    CASI_SEQ[ARG.caso] = caso_fmea(ARG.caso)


def interruttore(nome, tg, chiude):
    """The switch's control: 0 -> 1 at tg (chiude) or 1 -> 0 (apre); from t = 0 if tg == 0."""
    a, b = (0, 1) if chiude else (1, 0)
    if tg <= 0:
        return "VGF_%s gf_%s 0 pwl(0 %d 1000 %d)" % (nome, nome, b, b)
    return "VGF_%s gf_%s 0 pwl(0 %d %.12g %d %.12g %d 1000 %d)" % (nome, nome, a, tg, a, tg + 1e-6, b, b)


def applica_guasto(righe, g, tg):
    """L45c1: the fault primitive g (modi.py) on the deck lines of the supply's parts. Each
    primitive asserts that what it touches exists exactly once: a line or a node the deck does
    not have makes the generator refuse."""
    tipo = g[0]
    if tipo == "niente":
        return list(righe)
    # L45d2b2a: L45d2b1's primitive "riv" (the DC detector) is gone with the detector (ADR-081)
    if tipo == "spento":
        # L45c2: a regulator's enable to 0 at tg (from t = 0 if latent)
        _, reg = g
        ie = [i for i, r in enumerate(righe) if r.split()[0] == "VEN%s" % reg]
        assert len(ie) == 1, (reg, ie)
        out = list(righe)
        if tg <= 0:
            out[ie[0]] = "VEN%s en_%s 0 pwl(0 0 1000 0)" % (reg, reg.lower())
        else:
            out[ie[0]] = "VEN%s en_%s 0 pwl(0 1 %.12g 1 %.12g 0 1000 0)" % (reg, reg.lower(), tg, tg + 1e-6)
        return out
    if tipo == "corto":
        a, b = g[1], g[2]
        # L45d2b2b2: --serie2 / --u504doppio - a short on a doubled part's two nodes shorts its first
        # half only (a -> its middle node); declared in the deck. A fourth item names ANOTHER part on
        # the same two nodes (K501's coil across D505): no remapping
        for ref, (na, nb, m) in (sorted(DOPPI.items()) if len(g) == 3 else []):
            if {a, b} == {na, nb}:
                a, b = (na, m) if a == na else (m, na)
                righe = righe + ["* L45d2b2b2: corto di %s sulla prima meta' (%s - %s)" % (ref, a, b)]
                break
        nodi = set(x for r in righe for x in r.split()[1:3])
        assert a in nodi and b in nodi, (a, b)
        # L45d2b2b2: i(vfc), the fault's own current from a to b, through a 0 V source
        return righe + [interruttore("c", tg, True),
                        "BF_c %s fc_s I = V(%s,%s)*10*V(gf_c)" % (a, a, b),
                        "VFC fc_s %s 0" % b]
    if tipo == "carico":
        # L45d2b3b1: ("carico", a, b, R) - a resistor R from a to b from tg, through VFC like
        # "corto" (i(vfc) is its current): C145 shorted puts R144 || R152 (10 ohm) from VPLUS to
        # ground, as L45d2b1's ("riv", None, 10.0) without the detector
        a, b, rc = g[1], g[2], g[3]
        nodi = set(x for r in righe for x in r.split()[1:3])
        assert a in nodi and b in nodi, (a, b)
        return righe + [interruttore("c", tg, True),
                        "BF_c %s fc_s I = V(%s,%s)/%g*V(gf_c)" % (a, a, b, rc),
                        "VFC fc_s %s 0" % b]
    if tipo == "aperto":
        out, vecchio = list(righe), None
        for linea, k in g[1]:
            idx = [i for i, r in enumerate(out) if r.split()[0] == linea]
            assert len(idx) == 1, (linea, idx)
            p = out[idx[0]].split()
            assert vecchio in (None, p[k]), (vecchio, p[k])
            vecchio = p[k]
            p[k] = "f_ap"
            out[idx[0]] = " ".join(p)
        # 1 kS before the fault, 1 nS after (a 1 nS leak keeps the node defined)
        out += [interruttore("a", tg, False),
                "BF_a %s f_ap I = V(%s,f_ap)*(1e3*V(gf_a) + 1e-9)" % (vecchio, vecchio)]
        # L45c2: an optional third item, a capacitance across the opening (declared in modi.py)
        if len(g) > 2:
            out.append("CF_a %s f_ap %g" % (vecchio, g[2]))
        return out
    if tipo == "vset":
        _, reg, v = g
        ix = [i for i, r in enumerate(righe) if r.split()[0] == "X%s" % reg]
        ie = [i for i, r in enumerate(righe) if r.split()[0] == "VEN%s" % reg]
        assert len(ix) == 1 and len(ie) == 1, (reg, ix, ie)
        p = righe[ix[0]].split()
        assert p[5] in ("REGP", "REGM", "REGPSS", "REGMSS") and p[6].startswith("VSET="), p
        out = list(righe)
        out[ie[0]] = "VEN%s en_%s 0 pwl(0 1 %.12g 1 %.12g 0 1000 0)" % (reg, reg.lower(), tg, tg + 1e-6)
        twin = p[:]
        twin[0], twin[4], twin[6] = "X%sF" % reg, "en_%sf" % reg.lower(), "VSET=%g" % v
        twin = [x if not x.startswith("IQ=") else "IQ=0" for x in twin]
        # L45d2b2a: the twin is the failed regulator's new output at tg, at once: no soft-start
        twin[5] = twin[5].replace("SS", "")
        twin = [x for x in twin if not x.startswith(("TAU=", "TSS="))]
        return out + [" ".join(twin),
                      "VEN%sF en_%sf 0 pwl(0 0 %.12g 0 %.12g 1 1000 1)" % (reg, reg.lower(), tg, tg + 1e-6)]
    if tipo == "j1":
        _, rail, c = g
        psu = rail + "_psu"
        n = 0
        out = []
        for r in righe:
            p = r.split()
            if p and p[0][0] in "RCDXLMQB" and rail in p[1:5]:
                p = [psu if (1 <= k <= 4 and x == rail) else x for k, x in enumerate(p)]
                n += 1
                r = " ".join(p)
            out.append(r)
        assert n >= 4, (rail, n)        # regulator, hold-up, ceramic, Schottky or divider
        a, b = (psu, rail) if rail == "vplus" else (rail, psu)
        return out + [interruttore("j", tg, False),
                      "BF_j %s %s I = V(%s,%s)*(1e3*V(gf_j) + 1e-9)" % (a, b, a, b),
                      "CF_audio %s 0 %.6g" % (rail, c)]
    raise SystemExit("applica_guasto: primitiva %r sconosciuta" % (tipo,))


SONDE_SS = ["i(v.xu501.vsns)", "i(v.xu502.vsns)"]
# L45d2b2a: the regulators' IN when it is not RAW_P / RAW_M (a resistor before it, ADR-092)
for _r in ("U501", "U502"):
    _n = ingresso(_r, pn(_r, "15"))
    if _n not in ("raw_p", "raw_m"):
        SONDE_SS.append("v(%s)" % _n)


def sonde_guasto(c):
    """L45c1: the fault cases also write the raw rails (D510 / D511 read OUT against IN), and
    in the harness cases the supply's side of the open wire. ponte.c and estrai_ponte.py read
    their columns by name: a column more changes nothing for them."""
    if not c.get("guasto"):
        # L45d2b2a: with the soft-start, also the raw rails and the regulators' input currents
        return ["v(raw_p)", "v(raw_m)"] + SONDE_SS if ARG.ss == "si" else []
    s = ["v(raw_p)", "v(raw_m)"]
    if ARG.ss == "si":
        s += SONDE_SS
    # L45d2b2b1: the regulators' IN (when behind R550 / R551) and the Schottkys' currents, always
    # in a fault case: OUT - IN is read at the pin, and the diodes against their ratings
    s += [x for x in SONDE_SS if x.startswith("v(") and x not in s]
    s += ["i(vsd%s)" % r.lower() for r in sorted(SONDA_D) if r in COMPS]
    # --variante uscita: the regulators' OUT pins and the series diodes' currents
    s += ["v(%s)" % PIN[r] for r in sorted(PIN)] + ["i(vsser%s)" % r[1:] for r in sorted(PIN)]
    # ADR-093 in the netlist: the regulators' OUT pins when they are not the rails
    s += ["v(%s)" % pn(r, "1") for r in ("U501", "U502") if pn(r, "1") not in ("vplus", "vminus")]
    if c["guasto"][0] == "j1":
        s.append("v(%s_psu)" % c["guasto"][1])
    # L45d2b2b2: the probed pins' currents, the fault's current, and the nodes of the parts' power
    s += ["i(vsi%s_%s)" % (r.lower(), p) for r, p in sorted(SONDE_I)]
    if c["guasto"][0] == "corto":
        s.append("i(vfc)")
    s += [x for x in SONDE_075 if x not in s and x not in SONDE]
    if ARG.rk:
        s.append("v(q503_rk)")
    # ADR-094 in the netlist: Q503's drain behind R552, U504's output before U512
    s += ["v(%s)" % n.lower() for n in ("MAINS_SINK", "V5_PRE") if n in set(PN.values())]
    return s


# L45d2b2b2: what analizza_075.py needs for each part's voltage (Vds, Vce, the zener, the regulators)
SONDE_075 = ["v(rly_ret)", "v(raw_v)", "v(v5)", "v(vref)", "v(md)", "v(md_b)", "v(rect_v)",
             "v(clamp_mute)", "v(clamp_permit)", "v(mains_coil)", "v(sw_g)"]


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
         "v(mute_req)", "v(permit_req)", "v(mains_req)", "v(vrelay_en)",
         # L45d2b1's v(dc_flt), v(dc_flt_in) are gone with the detector (ADR-081, L60b); the two
         # gates stay (L45d2b2b reads them)
         "v(vr_g)", "v(mains_g)"]


# ============================================================ L54a: the all-analog timer (NC-054)
# Not in psu.py: a candidate, on the bench only. Every comparator is a TLV1702 / TLV1704 channel
# (CMPOD: it sinks its output when inn > inp), on V5 and RLY_RET like U505-U508. The supervisor on
# MUTE_G, D and D2 (U508), the pull-downs and the sinks are today's and are NOT touched: this
# replaces only what U509 drives (MUTE_REQ, PERMIT_REQ, MAINS_REQ, VRELAY_EN).
#   AT_PG  power good: the supervisor's four thresholds on four NEW channels (the same divider
#          nodes, high-impedance inputs). pa + rail, pb - rail, pc VRELAY_REG, pd the mains
#          detector; pd's output reaches AT_PG, AT_F and AT_T2S through three Schottkys
#          (one channel, three nodes).
#   AT_PGT 820k / 1 uF from V5, emptied through a Schottky into AT_PG: power good for
#          0.69 x 0.82 s = 0.57 s before the release (timer_spec.md 4.3 / 4.5: >= 100 ms at power-up,
#          >= 500 ms after a hole - one delay for both, the longer one rounded).
#   AT_MRQ 200k / 100 nF from V5 (the debounce: every input good for ~14 ms before it crosses
#          VREF), emptied by: AT_PGT below VREF (mg), SW3 in mute (sw), AT_ON low (a Schottky).
#          mq squares it into MUTE_REQ, mp into PERMIT_REQ, 10k pull-up each.
#   AT_ON  the front switch (on): 10k pull-up, sunk by the front comparator when FRONT_IN > VREF.
#          It is VRELAY_EN (through R535 and D524 into VR_T, as today) and feeds AT_MT and AT_T2S.
#   AT_MT  K501: 1M / 100 nF charged through diodes from AT_ON and from VR_G (pull-up R537),
#          squared by mr into MAINS_REQ (22k pull-up: MAINS_G ~3.8 V). With the front off it
#          falls ~0.54 x 100 ms after VR_G: K501 ~84 ms after PERMIT_CMD (ADR-046: >= 50 ms).
#   AT_T2S armed: 2.7M / 1 uF from AT_ON, 1.87 s to VREF; emptied by the mains detector (pd) and
#          by AT_ON low. "On, with the mains present for ~1.9 s" (timer_spec.md 4.1: no rails
#          within 2 s = GUASTO; 4.5: a hole re-runs the power-up).
#   AT_F   the fault: 100k / 330 nF from V5, emptied while not armed (fa), with the mains gone
#          (pd) or the power good (fc). High = a rail or VRELAY_REG out, the mains present, armed:
#          through 47k into the latch's NPN base (trips at ~0.9 V, ~6.6 ms).
#   latch  BC847 + BC857 as a thyristor, its anode on AT_ON: tripped, it holds AT_ON at ~0.8 V
#          (mute, VRELAY_EN and K501 down in D / D2 / D3) until the front switch sinks AT_ON
#          (timer_spec.md 4.6, ADR-048 point 5). 100k base-emitter on each.
# Channels: pa pb pc pd mg on sw mq mp mr fa fc = 12, three TLV1704.
TIMER_AN = [
    "* L54a all-analog timer (genera_tb_psu.py, TIMER_AN)",
    "XATpa sup_p vref at_pg v5 rly_ret CMPOD",
    "XATpb vref_half sup_m at_pg v5 rly_ret CMPOD",
    "XATpc sup_vr vref at_pg v5 rly_ret CMPOD",
    "XATpd vref md at_md v5 rly_ret CMPOD",
    "RATmd v5 at_md 100k",
    "DATmd1 at_pg at_md DBAT54", "DATmd2 at_f at_md DBAT54", "DATmd3 at_t2s at_md DBAT54",
    "RATpg v5 at_pg 100k",
    # 820k (first runs 680k: after a 20 ms hole the music came back 435 ms after the mains, under
    # timer_spec.md 4.5's 500 ms)
    "RATpgt v5 at_pgt 820k", "CATpgt at_pgt rly_ret 1u", "DATpgt at_pgt at_pg DBAT54",
    "XATmg at_pgt vref at_mrq v5 rly_ret CMPOD",
    "RATmrq v5 at_mrq 200k", "CATmrq at_mrq rly_ret 100n",
    "XATsw vref mute_sw_in at_mrq v5 rly_ret CMPOD",
    "DATmon at_mrq at_on DBAT54",
    "XATmq at_mrq vref mute_req v5 rly_ret CMPOD", "RATmq v5 mute_req 10k",
    # mp: PERMIT_REQ from the same AT_MRQ (first run without it: D522 holds MUTE_G at PERMIT_G
    # + 0.3 V, MUTE_G loads MUTE_REQ through R513 to 2.5 V, PERMIT_T stops at ~1.9 V < VREF, and
    # the permissive - so the jacks - never come: the micro's 50-ohm pin had no such problem)
    # and PERMIT_REQ falls ~24 ms after AT_MRQ (the firmware's 20 ms, timer_spec.md 4.2): AT_PRT
    # holds it through a diode, 4.7M / 10 nF (second run: from AT_MRQ directly D was 15.4 ms,
    # C3 out - PERMIT_T starts lower than with the micro's pin)
    "DATprt at_mrq at_prt D1N914", "RATprt at_prt rly_ret 4.7MEG", "CATprt at_prt rly_ret 10n",
    "XATmp at_prt vref permit_req v5 rly_ret CMPOD", "RATmp v5 permit_req 10k",
    # 10k, not 47k: VRELAY_EN keeps R527 (100k) to RET, and 47k left AT_ON at 3.3 V (first run)
    "XATon vref front_in at_on v5 rly_ret CMPOD", "RATon v5 at_on 10k",
    "RATve at_on vrelay_en 1",
    "RATma at_on at_ma 1k", "DATma at_ma at_mt D1N914", "DATmb vr_g at_mt D1N914",
    "CATmt at_mt rly_ret 100n", "RATmt at_mt rly_ret 1MEG",
    "XATmr at_mt vref mains_req v5 rly_ret CMPOD", "RATmr v5 mains_req 22k",
    "RATt2s at_on at_t2s 2.7MEG", "CATt2s at_t2s rly_ret 1u", "DATt2s at_t2s at_on DBAT54",
    "XATfa at_t2s vref at_f v5 rly_ret CMPOD",
    "XATfc vref at_pg at_f v5 rly_ret CMPOD",
    "RATf v5 at_f 100k", "CATf at_f rly_ret 330n",
    "RATfb at_f at_bn 47k",
    "QATn at_bp at_bn rly_ret QNGEN", "RATbn at_bn rly_ret 100k",
    "QATp at_bn at_bp at_on QPGEN", "RATbp at_on at_bp 100k",
    # 1 nF base-emitter on each (first runs: every fault case stopped at the latch's edge,
    # "Timestep too small" on at_bp / at_bn - the generic models have no capacitance, and the
    # regeneration was instantaneous; on the board the same 1 nF keeps a dv/dt from tripping it)
    "CATbn at_bn rly_ret 1n", "CATbp at_on at_bp 1n",
]
SONDE_AN = ["v(at_pg)", "v(at_pgt)", "v(at_mrq)", "v(at_on)", "v(at_mt)", "v(at_t2s)", "v(at_f)",
            "v(at_md)", "v(at_prt)", "v(permit_t)", "v(vr_t)"]


def sonde_seq():
    """L54b1: SONDE, without the micro's nodes on the source (mute_g_in, adc_*: gone with it)."""
    if ARG.timer != "sorgente":
        return SONDE
    # by name: k501_f and env are the bench's own nodes, not the netlist's (first deck: dropped)
    via = {"v(mute_g_in)", "v(adc_sup_p)", "v(adc_sup_m)", "v(adc_sup_vr)", "v(adc_md)"}
    return [s for s in SONDE if s not in via]


def sonde_an():
    """L54b1: SONDE_AN; on the source AT_ON is VRELAY_EN itself (in SONDE already)."""
    return [s for s in SONDE_AN if not (ARG.timer == "sorgente" and s == "v(at_on)")]


def seq_deck():
    c = CASI_SEQ[ARG.caso]
    if ARG.rete is not None:
        # L54a: the mains factor from the command line, on any case
        assert not c.get("fattore"), "--rete su un caso che ha gia' il suo fattore"
        c = dict(c, fattore=ARG.rete)
    # L41c: a corner case runs only with --angolo min (ANGOLO and VREF_SHUNT are
    # set from it at import), and a nominal case never with it
    if (c.get("angolo") == "min") != (ARG.angolo == "min"):
        raise SystemExit("caso %s: --angolo %s non e' il suo" % (ARG.caso, ARG.angolo))
    # L54a: with the analog timers there is no core: the micro is gone (no supply current either)
    u = uscite_core(ARG.uscite) if ARG.timer == "micro" else {"iq": pwl((0, 0), (1000, 0))}
    if ARG.timer == "diretto":
        # no standby: the front switch is not an input any more (closed for good, its comparator
        # idle); off = the mains switch, i.e. the bench's env
        c = dict(c, front=1)
    righe = ["* L47c2a tb_psu seq %s (giro %d) - GENERATED by genera_tb_psu.py from %s and %s"
             % (ARG.caso, ARG.giro, ARG.net, ARG.uscite)
             + ("" if ARG.timer == "micro" else " - L54a --timer %s%s" % (
                 ARG.timer, "" if ARG.rete is None else " --rete %g" % ARG.rete)),
             MODELS.format(repo=REPO, vref=VREF_SHUNT)] + MODELLI_074
    if ARG.comparatore != "comportamentale":
        righe.append("* L54b2 --comparatore %s" % ARG.comparatore)
    for ref in sorted(COMPS):
        righe += al_piedino(ref, element(ref, COMPS[ref])) + serie(ref)
    righe += sonde_i_righe()           # L45d2b2b2 (empty outside the fault cases)
    # (CAP_AUDIO goes with the audio board's loads below, after the fault)
    righe += ["* L45d2b2a soft-start: " + s for s in SS_LOG]
    for n in sorted(set(PN.values())):
        if n.startswith(("AC_", "T1_PRI", "T2_PRI")):
            righe.append("R_float_%s %s 0 1G" % (n.lower(), node(n)))
    # the mains envelope: 1, or a hole
    if c.get("fredda"):
        # L54a: a cold start - nothing powered (uic: every node at 0) until the mains arrive at TE
        env = "0 0 %.12g 0 %.12g 1 1000 1" % (TE, TE + 1e-4)
    elif c.get("buco", 0) >= 100:
        # L41c: the mains gone for good
        env = "0 1 %.12g 1 %.12g 0 1000 0" % (TE, TE + 1e-4)
    elif c.get("buco"):
        env = "0 1 %.12g 1 %.12g 0 %.12g 0 %.12g 1 1000 1" % (TE, TE + 1e-4, TE + c["buco"],
                                                              TE + c["buco"] + 1e-4)
    else:
        env = "0 1 1000 1"
    if c.get("fattore"):
        # L45d2b2a: a mains factor on the whole envelope. L54a: on any envelope (holes, cold
        # start), each level times the factor; with no hole the string is L45d2b2a's, byte for byte
        if env == "0 1 1000 1":
            env = "0 %g 1000 %g" % (c["fattore"], c["fattore"])
        else:
            p_ = env.split()
            env = " ".join(x if k % 2 == 0 else "%g" % (float(x) * c["fattore"])
                           for k, x in enumerate(p_))
    righe += ["VENV env 0 pwl(%s)" % env]
    # K501's contact: its coil (A1 on VRELAY_REG, A2 on MAINS_D) above 8.4 V
    # through a 5 ms RC (ASSUMED operate time); the toroid's mains = env x contact
    a1, a2 = pn("K501", "A1"), pn("K501", "A2")
    righe += ["BK501 k501_in 0 V = 0.5*(1+tanh((V(%s,%s)-8.4)/0.2))" % (a1, a2),
              "RK501 k501_in k501_f 5k", "CK501 k501_f 0 1u",
              ("BENV1 env1 0 V = V(env)" if ARG.timer == "diretto" else
               "BENV1 env1 0 V = V(env)*0.5*(1+tanh((V(k501_f)-0.5)/0.02))")]
    righe += mains("env1", 15.0, 50, 0.08, "T1_SEC_A", "T1_SEC_B", True, "T1")
    if ARG.vrelay_da == "t1":
        assert ARG.timer == "diretto", "--vrelay-da t1 solo con --timer diretto"
        righe += ["VENVZ envz 0 0"] + mains("envz", 12.0, 5, 0.20, "T2_SEC_A", "T2_SEC_B", False, "T2")
        righe += ["DAUXa t1_sec_a rect_v DBR", "DAUXb t1_sec_b rect_v DBR"]
    else:
        righe += mains("env", 12.0, 5, 0.20, "T2_SEC_A", "T2_SEC_B", False, "T2")
    if ARG.timer == "micro":
        for x in MCU_OUT:
            x = x.lower()
            righe += ["VSET_%s set_%s 0 pwl(%s)" % (x, x, u[x]),
                      "VDRV_%s drv_%s 0 pwl(%s)" % (x, x, DEF_DRV)]
    elif ARG.timer == "diretto":
        # no K501 without the standby: MAINS_REQ undriven (R528 holds it low), so its coil draws
        # nothing (first runs drove it: 29.5 mA on VRELAY_REG that the circuit would not have)
        righe += [r for r in TIMER_AN if not r.startswith(("XATmr ", "RATmr "))]
    elif ARG.timer == "sorgente":
        pass                # L54b1: the timer's parts are already in the deck, from psu.net
    else:
        righe += TIMER_AN
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
        if ARG.timer != "micro":
            # L54a: the analog timers hold PERMIT_REQ ~24 ms through AT_PRT as well - a second D in
            # series with C528's; the counterfactual removes both (first run: C3 passed without it)
            # L54b1: found by its nodes (CATprt on the bench, C550 in the source)
            k = [i for i, r in enumerate(righe)
                 if r.startswith("C") and set(r.split()[1:3]) == {"at_prt", "rly_ret"}]
            assert len(k) == 1, k
            p = righe[k[0]].split()
            righe[k[0]] = "%s %s %s %s" % (p[0], p[1], p[2], c["c528"])
    # L41c: U503's output shorted - a conductance from VRELAY_REG to the return,
    # 0 before, 10 S (0.1 ohm) from the case's instant (1 us edge)
    if c.get("corto") is not None:
        vr, ret = pn("U503", "1"), pn("C523", "2")
        assert vr == "vrelay_reg", vr
        righe += ["VGCORTO g_corto 0 pwl(0 0 %.12g 0 %.12g 10 1000 10)" % (c["corto"], c["corto"] + 1e-6),
                  "BCORTO %s %s I = V(%s,%s)*V(g_corto)" % (vr, ret, vr, ret)]
    # L45c1: the fault, on the supply's lines only - BEFORE the audio board's loads, so that
    # the harness case (j1) leaves the load on the audio board's side of the open wire
    if c.get("guasto"):
        righe = applica_guasto(righe, c["guasto"], c["t_guasto"])
    righe += [
        "RLOADP vplus 0 %g" % (15.0 / I_PIU), "RLOADM 0 vminus %g" % (15.0 / I_MENO)] + CAP_AUDIO + [
        "RMUTECOIL vrelay mute_cmd %g" % R_MUTECOIL,
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
        ".options reltol=1e-4 abstol=1e-10 vntol=1e-6 temp=25 method=%s gmin=%s"
        % (c.get("metodo", "gear"), c.get("gmin", "1e-10")),
        ".control",
        "set numdgt=12",
        "set wr_singlescale", "set wr_vecnames",
        "option numdgt=12",
        "tran 100u %.12g 0 20u uic" % c["tf"],
        "linearize",
        "wrdata tb_psu_seq_%s_g%d_out.txt %s" % (ARG.caso, ARG.giro, " ".join(
            sonde_seq() + sonde_guasto(c) + ([] if ARG.timer == "micro" else sonde_an())
            + (["v(t2_sec_a_e,t2_sec_b)", "i(vt2_sns)", "v(t1_sec_aa_e)", "i(vt1a_sns)",
                "v(t1_sec_ab_e)", "i(vt1b_sns)"] if ARG.sonda_t2 else []))),
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
                misure=["wrdata %s/%s.txt %s" % (ARG.uscita, nome, SAVE_RETE)] + misure_regime(nome, tf))


def misure_regime(nome, tf):
    """L45d2b2a: at regime, over the last 0.2 s: each regulator's mean power (IN - OUT) x I_IN, its
    --rpre resistor's, and the least headroom IN - |OUT| (the PSRR quota of ADR-020 assumes >= 1 V).
    Only with the soft-start's regulators (their sense source) and only in the regime cases."""
    if ARG.ss != "si" or not nome.startswith("regime"):
        return []
    out = []
    for ref, vin, vout, seg in (("U501", "raw_p", "vplus", 1), ("U502", "raw_m", "vminus", -1)):
        vi = ingresso(ref, pn(ref, "15"))
        x = ref.lower()
        if ref in PIN:
            # L45d2b2b1: --variante uscita - the regulator ends at its pin; the series diode's power
            out += ["let pd_%s = %d*(v(%s)-v(%s))*i(vsser%s)" % (x, seg, PIN[ref], vout, ref[1:]),
                    "meas tran pd_%s_avg AVG pd_%s FROM=%g TO=%g" % (x, x, tf - 0.2, tf),
                    "let hr_%s = %d*(v(%s)-v(%s))" % (x, seg, vi, vout),
                    "meas tran hr_%s_min MIN hr_%s FROM=%g TO=%g" % (x, x, tf - 0.2, tf)]
            vout = PIN[ref]
        elif pn(ref, "1") != vout:
            # L45d2b2b1: the netlist's own series diode (ADR-093): the regulator ends at its pin;
            # the diode's power from the regulator's IN current (its output current + IQ, declared)
            pin = pn(ref, "1")
            out += ["let pd_%s = %d*(v(%s)-v(%s))*i(v.x%s.vsns)" % (x, seg, pin, vout, x),
                    "meas tran pd_%s_avg AVG pd_%s FROM=%g TO=%g" % (x, x, tf - 0.2, tf),
                    "let hr_%s = %d*(v(%s)-v(%s))" % (x, seg, vi, vout),
                    "meas tran hr_%s_min MIN hr_%s FROM=%g TO=%g" % (x, x, tf - 0.2, tf)]
            vout = pin
        out += ["let p_%s = %d*(v(%s)-v(%s))*i(v.x%s.vsns)" % (x, seg, vi, vout, x),
                "meas tran p_%s_avg AVG p_%s FROM=%g TO=%g" % (x, x, tf - 0.2, tf),
                "let h_%s = %d*(v(%s)-v(%s))" % (x, seg, vi, vout),
                "meas tran h_%s_min MIN h_%s FROM=%g TO=%g" % (x, x, tf - 0.2, tf)]
        r = resistenza_davanti(ref)
        if r:
            out += ["let pr_%s = (v(%s)-v(%s))^2/%g" % (x, vin, vi, r),
                    "meas tran pr_%s_avg AVG pr_%s FROM=%g TO=%g" % (x, x, tf - 0.2, tf)]
    return out


def resistenza_davanti(ref):
    """L45d2b2a: the resistor between the bridge's raw rail and the regulator's IN - --rpre's, or
    the netlist's (R550 / R551 since ADR-092), or None."""
    if ref in RPRE:
        return RPRE[ref]
    vi = PN[(ref, "15")]
    raw = {"U501": "RAW_P", "U502": "RAW_M"}[ref]
    if vi == raw:
        return None
    rs = [r for r, c in COMPS.items() if c["part"] == "R"
          and sorted([PN.get((r, "1")), PN.get((r, "2"))]) == sorted([vi, raw])]
    assert len(rs) == 1, (ref, rs)
    return float(sval(COMPS[rs[0]]["value"]))


def rete_deck():
    righe = ["* L47c2a tb_psu %s - GENERATED by genera_tb_psu.py from %s" % (ARG.nome, ARG.net),
             MODELS.format(repo=REPO, vref=VREF_SHUNT)] + MODELLI_074
    for ref in sorted(COMPS):
        righe += al_piedino(ref, element(ref, COMPS[ref])) + serie(ref)
    righe += ["* L45d2b2a soft-start: " + s for s in SS_LOG] + CAP_AUDIO
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
        "IPLUS vplus 0 dc 0 pwl(0 0 0.5 %g)" % I_PIU,
        "IMINUS 0 vminus dc 0 pwl(0 0 0.5 %g)" % I_MENO,
        "RMUTECOIL vrelay mute_cmd %g" % R_MUTECOIL,
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
    elif ARG.ss == "si":
        # L45d2b2a: with the soft-start the trapezoidal method stops regime_m10 at 0.900153 s,
        # VRELAY_EN's edge (qq504) - the stop L47c2a found on the counterfactual's load; gear,
        # the sequence decks' method, runs it. --ss no keeps L42b's options (the check)
        k = [i for i, r in enumerate(righe) if r == ".options reltol=1e-4 abstol=1e-10 vntol=1e-6"]
        assert len(k) == 1
        righe[k[0]] += " method=gear"
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
