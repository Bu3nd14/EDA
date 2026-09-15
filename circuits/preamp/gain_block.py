#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gain_block.py - THE gain block of the line preamplifier.

Fase 2 DRAFT. Source of truth for the topology (AGENTS.md rule 2).
Never hand-edit the generated netlist/schematic; edit this file.

ADR-006: one discrete block, designed once, used twice per channel:
    BLOCK A  input buffer,  gain = 1 always  (relay/R_g not fitted)
    BLOCK B  output stage,  gain = 0 / +3 / +10 dB, two relays on the
                            feedback network (ADR-019, ADR-026)

TOPOLOGY - three stages + global feedback, no op-amp, no DC servo:

    stage 1  LSK489 differential pair, CASCODED, current-mirror load
    stage 2  PNP common-emitter VAS, Miller-compensated, current-source load
    stage 3  complementary Class A emitter follower, MJE15032/33, 15 mA

  ADR-013 input pair: LSK489 monolithic dual N-JFET (C_iss 4 pF)
  ADR-014 cascode:    mandatory - without it the HF response would depend on
                      the volume-control position
  ADR-003 all-discrete Class A, no op-amp anywhere in the signal path
  ADR-007 no DC servo; DC is blocked by the output coupling capacitor, which
          lives in the CHANNEL file, not here
  ADR-004 gain relay switches R_g to ground, never R_f: see LOOP INTEGRITY

LOOP INTEGRITY (ADR-004 + REQUIREMENTS V2) - the load-bearing constraint
------------------------------------------------------------------------
R_f is HARD-WIRED from OUT to FB and is never switched. Since L27 there are
TWO R_g legs from FB, in PARALLEL, and each relay contact only connects the
far end of its own leg to ground (ADR-026):

    K1 open,   K5 open    -> gain = 1 exactly                        (0 dB)
    K1 CLOSED, K5 open    -> gain = 1 + R_f/R_g3          = 1.420   (+3.05 dB)
    K1 CLOSED, K5 CLOSED  -> gain = 1 + R_f/(R_g3||R_g10) = 3.152   (+9.97 dB)
    K1 open,   K5 CLOSED  -> 1 + R_f/R_g10 = 2.732 (+8.73 dB) - only as a fault
    any contact BOUNCING  -> gain slides inside [1, 3.152], never above it

There is no contact state - open, closed, bouncing, welded, corroded - in
which the feedback loop is broken, because the loop does not pass through a
relay at all. And because the legs are in parallel, no combination of
contacts can exceed +10 dB: closing a leg can only lower the equivalent R_g
towards R_g3||R_g10. The de-energised (power-off / coil-fault) state is unity
gain, which is also the intended normal mode per ADR-001 and ADR-019.

Run:
  /Users/roberto/EDA/env/venv/bin/python3 <this file>
"""
import os
import sys

for _ver in ("6", "7", "8", "9", "10"):
    os.environ.setdefault(
        f"KICAD{_ver}_SYMBOL_DIR",
        "/Users/roberto/Applications/KiCad.app/Contents/SharedSupport/symbols",
    )
    os.environ.setdefault(
        f"KICAD{_ver}_FOOTPRINT_DIR",
        "/Users/roberto/Applications/KiCad.app/Contents/SharedSupport/footprints",
    )

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import skidl  # noqa: E402
from skidl import Part, Net, generate_netlist, POWER, ERC  # noqa: E402

import spice_export as sx  # noqa: E402

# REPO e' la radice del checkout di cui QUESTO file fa parte, DERIVATA e mai
# cablata: <repo>/circuits/preamp/gain_block.py, quindi due directory sopra
# quella del file. E' l'equivalente Python di ROOT=${0:A:h:h}, gia' la regola
# in run_tests.sh e run_simulation.sh.
#
# Perche' non un percorso cablato (L3b): qui REPO e' un percorso di
# SCRITTURA - gain_block.net, gain_block.subckt, gain_block_flat.inc, e
# preamp_audio.net attraverso preamp_audio.py. Cablato su un worktree, era la
# meta' di scrittura dello stesso guasto che L3 ha tolto dai deck: rigenerando
# il circuito, gli artefatti nuovi finivano nell'albero vecchio e le
# simulazioni continuavano a leggere la copia non aggiornata del checkout
# corrente. Senza errore da nessuna parte, perche' la riga 498 fa
# os.makedirs(..., exist_ok=True) e la directory se la crea da se'.
REPO = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

# The project's OWN symbol library, searched in addition to KiCad's (L22).
# It exists because some parts this design needs have no KiCad symbol at
# all: the LS352 dual PNP of the input mirror (L22) and the LSK489 dual JFET
# of the input pair (L10). Derived from REPO, never hard-coded, for the
# same reason REPO itself is derived.
#
# It is appended to EVERY tool's search path, not just KICAD10's: SKiDL's
# default tool constant is version-numbered (limitations.md #6), and a list
# that happens to be keyed on the wrong version fails with a
# FileNotFoundError that says nothing about search paths.
for _tool in list(skidl.lib_search_paths):
    skidl.lib_search_paths[_tool].append(os.path.join(REPO, "library"))

# --- Footprints -------------------------------------------------------------
# P6: everything through-hole on generous pitch so the user can swap signal
# capacitors and critical resistors with an iron, not a desoldering station.
FP_R = "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal"
FP_TO92 = "Package_TO_SOT_THT:TO-92_Inline"
FP_TO220 = "Package_TO_SOT_THT:TO-220-3_Vertical"
FP_SOIC8 = "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm"
FP_DO35 = "Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal"
FP_CERAMIC = "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm"
FP_ELCO = "Capacitor_THT:CP_Radial_D8.0mm_P3.50mm"

# --- Design constants (every non-obvious one carries its ADR) ---------------
# Rails: +/-15 V regulated - E7 / ADR-003. The current budget this block needs
# is printed by __main__ and handed to psu-engineer.
R_F = "1.50k"       # ADR-004: fixed feedback resistor, NEVER switched.
# ADR-026: the three gain levels of ADR-019 from two R_g legs in PARALLEL,
# each switched to GND by its own normally-open contact (read LOOP INTEGRITY).
R_G3 = "3.57k"      # Leg 1, relay K1. Alone: 1 + 1500/3570 = 1.420 = +3.05 dB,
                    # E2's "+3 dB". The E96 neighbours give 2.99 dB (3.65k)
                    # and 2.93 dB (3.74k); 3.57k is the one whose PAIR with
                    # R_G10 lands +10 dB closest to where it always was.
R_G10 = "866"       # Leg 2, relay K5, commanded only TOGETHER with K1:
                    # 3.57k || 866 = 696.9 ohm, 1 + 1500/696.9 = 3.152 =
                    # +9.97 dB - E2's "+10 dB", 0.16 % from the single 698 ohm
                    # leg it replaces (+9.96 dB until L27). So the network at
                    # +10 dB is still a 2.2 kOhm load on the output stage
                    # (3.9 mA peak at clipping, well inside the 15 mA Class A
                    # bias), and R_f's own Johnson noise (4.98 nV/rtHz ->
                    # 0.70 uV over 20 kHz) stays far below E5's 10 uV.
                    # Why parallel and not a selector in series: no contact
                    # state, welded included, can exceed +10 dB, and a single
                    # coil fault always gives LESS gain than commanded.

R_IN = "1M"         # E3 requires >= 100 kOhm. 1 MOhm is 10x that, and it is
                    # free: the corner it forms with the tube phono's unknown
                    # output capacitor is 10x lower than a 100 kOhm input
                    # would give. REQUIREMENTS "Aperti" defers the phono cap
                    # value indefinitely - so buy margin instead of waiting.
                    # Noise cost is nil: the source (430 Ohm cathode follower,
                    # or <1.5 Ohm from the K11) shunts it.

R_GATE_STOP = "100"  # gate stopper, standard anti-parasitic practice on JFETs.
                     # NOT an RF filter - see the note below.
# NO shunt capacitor at the gate. A fixed C to ground there would form a pole
# with the SOURCE impedance, and block B's source is the stepped attenuator,
# whose Zout swings 0 -> 2.5 kOhm -> 0 with the knob (ADR-014). A 470 pF cap
# would put that pole at 124 kHz at mid-rotation and at several MHz at the
# extremes - i.e. it would reintroduce, through the back door, exactly the
# volume-dependent HF response that ADR-014 exists to eliminate. If EMC work
# later demands an RF shunt it must be <= 47 pF, so the worst-case pole stays
# above 1 MHz. Handed to pcb-automation-engineer as an EMC constraint.

R_SDEG = "100"      # source degeneration. Linearises the pair and gives a
                    # measurable node for checking the tail split. 100 Ohm
                    # adds 1.29 nV/rtHz per side; kept small for that reason.

# Cascode base reference: ~10 V from a 4.99k/10.0k divider off V+.
# THE NON-OBVIOUS NUMBER IN THE WHOLE BLOCK, and the one place where this
# draft had to extend ADR-014 rather than just implement it.
# ADR-014 mandates the cascode, but argues it from CAPACITANCE. It says
# nothing about common-mode range, and in a UNITY-GAIN FOLLOWER that is the
# binding constraint: the input pair's common mode swings with the signal, so
# at 2.7 V RMS (E6) the JFET sources reach +3.8 V pk while the cascode pins
# the drains at a FIXED voltage. Set that voltage too low and the block
# clips at the INPUT stage - and the clip appears only on the positive half,
# which is the worst kind to find on a bench.
#   source(max) = 3.8 V (E6 peak) + |Vgs| 0.49 V = 4.3 V
#   drain must stay >= source + 2 V              = 6.3 V minimum
# First draft used 8.485 V. tb_dc_headroom.cir showed the 0 dB mode losing
# gain from Vin = +7.88 V (Vds already down to 1.2 V at Vin = +6 V) - i.e.
# only 2.3 dB of margin over E6 at a conservative Vds >= 2 V criterion, while
# the negative half had no limit at all inside the rails. Raising the
# reference to ~10 V buys ~1.5 V of ceiling and costs nothing: the cascode
# transistors still sit at ~4.5 V of Vce and each JFET dissipates 19 mW.
# ADR-014's own "Da riaprire se: il cascode costa margine di tensione in un
# punto dove serve" is exactly this trade. It is paid at the input stage,
# where there is room, not at the output stage, where there is not.


def gain_block(tag="", base=100, switchable=True, r_in=R_IN,
               vp=None, vm=None, gnd=None):
    """Build one gain block. Returns a dict of its external nets.

    tag        - net-name prefix, e.g. "AL" for block A, left channel
    base       - reference designator base (100 -> Q101, R102, ...)
    switchable - True: fit R_g + the gain-relay contact node (BLOCK B).
                 False: unity gain hard-wired (BLOCK A, ADR-006).
    r_in       - gate-return resistor, or None when the source already
                 provides a DC path (block B is fed by the attenuator ladder).
    vp/vm/gnd  - pass the SHARED rail nets in when instantiating more than one
                 block. SKiDL's Net("VPLUS") creates a NEW net every call and
                 silently renames the duplicate to VPLUS_1, which would give
                 each block its own floating rail. Not hypothetical: it is the
                 obvious way to write this and it is wrong.
    """
    p = (tag + "_") if tag else ""

    def n(s):
        return Net(p + s)

    # ---- external nets ----
    VP = vp if vp is not None else Net("VPLUS")
    VM = vm if vm is not None else Net("VMINUS")
    GND = gnd if gnd is not None else Net("GND")
    GND.drive = POWER
    IN, OUT, FB = n("IN"), n("OUT"), n("FB")
    # RG / RG10 only exist on a switchable block; creating them
    # unconditionally would leave block A with pinless nets and ERC warnings.
    # RG is the +3 dB leg's contact node (relay K1), RG10 the +10 dB leg's
    # (relay K5) - ADR-026.
    RG = n("RG") if switchable else None
    RG10 = n("RG10") if switchable else None

    # ---- internal nets ----
    NREF, NREFM = n("NREF"), n("NREFM")       # negative-rail bias reference
    SRC, NTE = n("SRC"), n("NTE")             # JFET common source, tail emitter
    G1, G2 = n("G1"), n("G2")                 # gates after the stoppers
    S1, S2 = n("S1"), n("S2")                 # sources before degeneration
    D1N, D2N = n("D1N"), n("D2N")             # JFET drains = cascode emitters
    NCASC = n("NCASC")                        # cascode base reference
    NMIRI, NHI = n("NMIRI"), n("NHI")         # mirror diode node / output node
    NX, NY, NBB = n("NX"), n("NY"), n("NBB")  # spreader top / bottom / base
    NBN, NBP = n("NBN"), n("NBP")             # output base stoppers
    NEN, NEP = n("NEN"), n("NEP")             # output emitters

    i = [base]

    def R(val, a, b, fp=FP_R):
        i[0] += 1
        r = Part("Device", "R", value=val, footprint=fp, ref=f"R{i[0]}")
        r[1] += a
        r[2] += b
        sx.spice_dev(r, "R", ["1", "2"], val)
        return r

    def C(val, a, b, fp=FP_CERAMIC):
        i[0] += 1
        c = Part("Device", "C", value=val, footprint=fp, ref=f"C{i[0]}")
        c[1] += a
        c[2] += b
        sx.spice_dev(c, "C", ["1", "2"], val)
        return c

    def Q(kind, val, model, c, b, e, fp=FP_TO92):
        i[0] += 1
        sym = "Q_NPN" if kind == "npn" else "Q_PNP"
        q = Part("Device", sym, value=val, footprint=fp, ref=f"Q{i[0]}")
        q["C"] += c
        q["B"] += b
        q["E"] += e
        sx.spice_dev(q, "Q", ["C", "B", "E"], model)
        return q

    def D(val, a, k, fp=FP_DO35):
        i[0] += 1
        d = Part("Device", "D", value=val, footprint=fp, ref=f"D{i[0]}")
        d["A"] += a
        d["K"] += k
        sx.spice_dev(d, "D", ["A", "K"], "D1N4148")
        return d

    # ========================================================================
    # 1. NEGATIVE-RAIL BIAS REFERENCE
    # ========================================================================
    # Two silicon diodes (1.2 V), NOT an LED (1.8 V) and NOT a zener.
    # Pure headroom arithmetic, and it is why the +10 dB mode fits at all:
    # the reference voltage minus one Vbe is dropped across the current-source
    # emitter resistors, and every volt dropped there is a volt of output
    # swing lost at the negative rail.  LED = 1.15 V lost, 2 diodes = 0.55 V.
    # That 0.6 V is ~0.5 dB of headroom in a mode that only has ~0.8 dB.
    # Bypassed to V-, NOT to ground: a current source must hold its current
    # constant relative to the rail it stands on. That single choice is what
    # turns negative-rail PSRR from a topology problem into a decoupling one.
    R("6.81k", GND, NREF)               # ~2.0 mA through the reference string
    D("1N4148", NREF, NREFM)
    D("1N4148", NREFM, VM)
    C("100u", NREF, VM, fp=FP_ELCO)     # + terminal on NREF
    C("100n", NREF, VM)

    # ========================================================================
    # 2. INPUT STAGE - LSK489 differential pair, cascoded (ADR-013, ADR-014)
    # ========================================================================
    # Tail current sink: 4.0 mA => 2.0 mA per JFET half.
    # R = (1.2 V - Vbe)/4 mA = 0.55/4m = 137 Ohm (E96).
    Q("npn", "2N5551", "NSS2N5551", SRC, NREF, NTE)
    R("137", NTE, VM)

    # ADR-013: ONE LSK489 monolithic dual - and, since L10, ONE Part.
    # Until L10 it was two Parts with a SOIC-8 footprint each, i.e. two
    # packages on the board for one device: the same defect NC-016 closed
    # for the LS352. The symbol lives in library/preamp.kicad_sym, because
    # the KiCad 10 libraries contain no dual JFET and no LSK489 at all.
    #
    # Pin numbers below are the SOIC-8 pinout READ OFF THE FROZEN DATASHEET,
    # vendor/jfet/linear_systems/LSK489/LSK489DSRevA38.pdf (content Rev A40),
    # page 1, drawing "SOIC-A Top View":
    #     1=S1  2=D1  3=SS  4=G1  5=S2  6=D2  7=SS  8=G2
    # The drawing is a 96 ppi raster, so it was LOOKED AT, not extracted. Its
    # internal JFET symbols are drawn ROTATED - the channel bar is horizontal,
    # drain and source reach it from one side and the arrowed gate from the
    # other - and read that way they agree with the pin labels on both
    # halves. (Read as an upright JFET they seem to swap D and G: that is the
    # misreading to avoid.) The LSK389 datasheet, which this one declares
    # "fit, form and pin compatible", draws the identical symbol at legible
    # resolution; it was used to check the reading, never as the source.
    #
    # SS (pins 3, 7) is NOT CONNECTED, and that is not a decision taken here:
    # nothing was connected before either. The frozen LSK489 datasheet draws
    # SS but never defines it. The only definition found - "SS: SUBSTRATE,
    # LEAVE THESE PINS FLOATING (N/C)" - is printed for the LSK389 (its
    # datasheet Rev A27 p.7, and the Linear Systems Data Book p.15), not for
    # this part. Registered as NC-027: to be confirmed before G2.
    R(R_GATE_STOP, IN, G1)
    R(R_GATE_STOP, FB, G2)
    i[0] += 1
    # The grade is B, I_DSS 8.0 / 11.5 / 15.0 mA (datasheet RevA40 p.2): ADR-031,
    # the user's decision of 2026-09-15. The value came in with L10 unexplained.
    # L20 measured this block across the whole B window with the vendor model,
    # Vto shifted: the tail sets I_D, so I_DSS moves only V_GS - operating point,
    # E5 and V1 do not depend on it; the common-mode saturation margin shrinks
    # to 2.4 V at 15 mA. reports/2026-09-15-L20-sensibilita-idss.md.
    jp = Part("preamp", "LSK489", value="LSK489B", footprint=FP_SOIC8,
              ref=f"Q{i[0]}")
    jp["2"] += D1N        # D1 -> non-inverting half, into its cascode
    jp["4"] += G1         # G1 -> after the input gate stopper
    jp["1"] += S1         # S1 -> its own source degeneration
    jp["6"] += D2N        # D2 -> inverting (feedback) half
    jp["8"] += G2         # G2 -> after the feedback gate stopper
    jp["5"] += S2         # S2 -> its own source degeneration
    # Two SPICE elements from one Part: JQ<n>A and JQ<n>B (spice_dev suffix,
    # L22). Node order is SPICE's D G S.
    sx.spice_dev(jp, "J", ["2", "4", "1"], "LSK489X", suffix="A")
    sx.spice_dev(jp, "J", ["6", "8", "5"], "LSK489X", suffix="B")
    R(R_SDEG, S1, SRC)
    R(R_SDEG, S2, SRC)
    if r_in:
        R(r_in, IN, GND)                # E3: Zin. See R_IN above.

    # Cascode base reference (ADR-014): 4.99k/10.0k off V+, ~1 mA, bypassed so
    # the drains sit still. v(ncasc) = 9.887 V: data/2026-09-10/tb_op-LS352.log
    R("4.99k", VP, NCASC)
    R("10.0k", NCASC, GND)
    C("47u", NCASC, GND, fp=FP_ELCO)

    # Cascode transistors, common base: they hold the JFET drains at 9.21 V
    # (v(d1n)/v(d2n), same log), which kills the C_rss Miller multiplication.
    # The one above the NON-INVERTING JFET drives the mirror OUTPUT; the one
    # above the FEEDBACK JFET drives the mirror DIODE. That assignment - not
    # the other one - is what makes the global feedback negative.
    Q("npn", "2N5551", "NSS2N5551", NHI, NCASC, D1N)     # -> mirror output
    Q("npn", "2N5551", "NSS2N5551", NMIRI, NCASC, D2N)   # -> mirror diode

    # Current-mirror load, matched monolithic PNP pair.
    #
    # THE PART IS AN LS352 (ADR-018), NOT THE THAT320 THIS USED TO BE.
    # The THAT320 went end-of-life on 2026-09-01 and ADR-016 discarded the
    # last-time buy, so it had to go (NC-015). What it brought was
    # MONOLITHIC MATCHING - two devices on one die - and that is the
    # property the replacement had to reproduce, not the part number:
    # LS352 is |Vbe1-Vbe2| = 0.2 mV typ / 0.5 mV max, against the 5 mV of
    # a hand-matched discrete pair.
    #
    # IT IS ONE PART, NOT TWO. A dual is one package with two units, and
    # instantiating it as two Parts is what put a phantom second SOIC-8 on
    # this board (NC-016). Pin numbers below are the SOIC-8 pinout READ OFF
    # THE DATASHEET drawing, LS350SeriesDSRevA5.pdf page 2:
    #     1=C1  2=B1  3=E1  4=N/C  5=N/C  6=E2  7=B2  8=C2
    # The datasheet also lists PDIP-8 and DFN-8 on the product page but
    # DRAWS neither pinout, so neither was used - an unpublished pinout is
    # how the THAT320's phantom SOIC-8 happened in the first place.
    #
    # THE DEVICE IS NOISIER AND THE STAGE IS NOT. That is the whole result
    # of the re-design, and both halves are measured (L22 report).
    # Alone, on one deck run against both models at IC = 1 mA, VCB = 10 V:
    # this device is 1.685 nV/rtHz against the THAT320's 0.758, 2.22x worse,
    # because the vendor model carries RB = 200 where the THAT320 carried
    # RB = 25. But the mirror's contribution to the STAGE is set by its
    # transconductance, and degeneration buys that back faster than rbb
    # costs it.
    #
    # 220 OHM, NOT THE 47 OHM THIS USED TO BE, AND THE VALUE WAS SWEPT
    # RATHER THAN ARGUED. tb_noise_breakdown.cir worst case (config D) and
    # the mirror output transistor's own internal Vbc, which is what says
    # how close it is to saturating:
    #
    #     Re      noise (config D)     Vbc of the output half
    #      22       (not run)           -53.1 mV   saturating
    #      47        6.988 uV            -0.4 mV   on the knee
    #     100        5.149 uV          +112.5 mV
    #     150        4.580 uV          +219.4 mV
    #     220        4.231 uV  <-- min +369.1 mV   CHOSEN
    #     330        4.515 uV          +590.8 mV   noise rises again, and
    #                                              negative clipping loses
    #                                              0.77 V (-13.85 -> -13.08)
    #
    # For reference the THAT320 at 47 Ohm measured 5.697 uV on the same
    # deck, so the stage ends up 25.7% QUIETER than it was with the part
    # that went end-of-life - with a device whose own noise is 2.2x worse.
    # Phase margin is unchanged (63.5 -> 63.0 deg at 0 dB, no load) and
    # positive clipping moves by 15 mV, i.e. 0.01 dB.
    #
    # WHY THE KNEE EXISTS AT ALL: the vendor model carries RC = 231.4 ohm,
    # against the THAT320's 18. At 2.1 mA that eats 0.49 V of the ~1.2 V of
    # Vce this transistor has, so the junction sits far closer to the knee
    # than the terminal voltage suggests. It is not a model artefact - the
    # datasheet's own VCE(sat) <= 0.5 V at 1 mA implies exactly such an RC.
    NME1, NME2 = n("NME1"), n("NME2")
    R("220", VP, NME1)
    R("220", VP, NME2)
    i[0] += 1
    qm = Part("preamp", "LS352", value="LS352", footprint=FP_SOIC8,
              ref=f"Q{i[0]}")
    qm["1"] += NMIRI      # C1 -> mirror diode side (collector to its base)
    qm["2"] += NMIRI      # B1 -> common base node
    qm["3"] += NME1       # E1 -> its own 47 Ohm degeneration
    qm["8"] += NHI        # C2 -> mirror output, into the VAS
    qm["7"] += NMIRI      # B2 -> common base node
    qm["6"] += NME2       # E2 -> its own 47 Ohm degeneration
    sx.spice_dev(qm, "Q", ["1", "2", "3"], "LS350", suffix="A")
    sx.spice_dev(qm, "Q", ["8", "7", "6"], "LS350", suffix="B")

    # ========================================================================
    # 3. VOLTAGE AMPLIFIER STAGE (VAS)
    # ========================================================================
    # PNP common emitter off V+. 91 Ohm degeneration at 6 mA = 0.55 V, chosen
    # EQUAL to the drop across the VAS-load sink's emitter resistor so that
    # positive and negative clipping occur at the same amplitude. Symmetric
    # clipping is not cosmetic: V3 asks for overload-recovery behaviour, and
    # an asymmetric clip pumps a DC component into the output coupling
    # capacitor which then takes seconds to bleed off through the load.
    NVE = n("NVE")
    Q("pnp", "2N5401", "PSS2N5401", NX, NHI, NVE)
    R("91", VP, NVE)

    # Miller compensation - the dominant pole of the whole amplifier.
    # MUST be C0G/NP0: it sees ~13 V of DC bias and carries the entire
    # correction signal; an X7R here would modulate the compensation with the
    # signal. Handed to bom-component-manager as a dielectric requirement.
    C("470p", NX, NHI)

    # VAS load: current sink off the same reference string as the tail.
    # 0.55 V / 6 mA = 91.7 -> 91 Ohm (E96).
    NVLE = n("NVLE")
    Q("npn", "2N5551", "NSS2N5551", NY, NREF, NVLE)
    R("91", NVLE, VM)

    # ========================================================================
    # 4. BIAS SPREADER (Vbe multiplier)
    # ========================================================================
    # 1.69k is a SWEPT value, not a calculated one. The hand calculation was
    # wrong twice: 2.16k (textbook Vbe = 0.62 V) simulated at Iq = 22.1 mA,
    # 1.87k at 17.5 mA. spice/preamp/tb/tb_bias_sweep.cir swept the leg and
    # 1.69k lands on Iq = 14.7 mA - the honest number, not "15".
    # Sensitivity from that sweep: 50 Ohm (3 %) moves Iq by 0.78 mA (5.3 %),
    # so 1 % resistors are not the limit here; the spread of Vbe between
    # samples is. This resistor is SELECT-ON-TEST on the bench, and MUST be
    # re-swept when the vendor MJE15032/33 and 2N5551 models arrive (Fase 4):
    # it is set by device Vbe, which is exactly what a placeholder model
    # gets wrong.
    # This transistor MUST be thermally coupled to the NPN output device
    # (MJE15032) or the bias drifts. ADR-034 / NC-019: the coupling is PCB
    # COPPER, not thermal compound + cable tie - ADR-017 makes this part an
    # MMBT5551 in SOT-23, which cannot be tied to a TO-220 tab (T7 stays).
    # The copper must NOT join them galvanically: the TO-220 tab is the
    # collector, on VP, and no pin of this transistor is on VP. And
    # TO-220-3_Vertical has no tab pad. Geometry, layer, isolation and the
    # TO-220 footprint: pcb-automation-engineer, before G2. This comment is
    # the whole hand-off today - no separate layout brief exists yet.
    # NO trimmer, deliberately: with 22 Ohm emitter resistors a 50 mV Vbe
    # spread moves Iq by only +/-1.1 mA, and a trimmer with an open wiper is
    # a thermal-runaway mechanism. R(NBB-NY) is select-on-test if needed.
    Q("npn", "2N5551", "NSS2N5551", NX, NBB, NY)
    R("1.69k", NX, NBB)
    R("1.00k", NBB, NY)

    # ========================================================================
    # 5. OUTPUT STAGE - complementary Class A emitter follower
    # ========================================================================
    # MJE15032/33: confirmed Active and in stock in the Fase 1 report, and
    # deliberately oversized - at 15 mA / 15 V they dissipate 225 mW against a
    # package good for tens of watts, so the operating point never leaves the
    # flat part of the beta and Vbe curves.
    # Class A holds under the loads V1 lists, by arithmetic: the heaviest of
    # them is 100 kOhm (cj EV250) in parallel with the 2.2 kOhm feedback
    # network, i.e. 3.9 mA peak at full output - a quarter of the 15 mA bias,
    # so neither device turns off.
    # It does NOT hold with the mute engaged or with a short at an output
    # connector (NC-001, NC-010): both put ground behind 47 ohm + 4.7 uF and
    # the stage runs in class B. ADR-021 accepts class B in exactly those two
    # conditions and asks for thermal and SOA limits instead (Tj <= 125 C at
    # 60 C ambient). L11 measured them on this topology, no heatsink
    # (spice/preamp/tb/tb_mute_corto.cir, docs/preamp/data/2026-09-14/):
    # worst 484 mW per MJE, Tj 90 C, against 1.04 W allowed.
    # ADR-021 rating constraint for the BOM: the two 22 ohm emitter resistors
    # below dissipate up to 0.27 W (block B, short at MAIN, +10 dB, 20 kHz
    # full scale), so they must be rated >= 0.27 W at 60 C.
    R("10", NX, NBN)
    R("10", NY, NBP)
    Q("npn", "MJE15032", "NMJE15032", VP, NBN, NEN, fp=FP_TO220)
    Q("pnp", "MJE15033", "PMJE15033", VM, NBP, NEP, fp=FP_TO220)
    R("22", NEN, OUT)
    R("22", NEP, OUT)

    # ========================================================================
    # 6. FEEDBACK NETWORK  (ADR-004 - read LOOP INTEGRITY at the top)
    # ========================================================================
    R(R_F, OUT, FB)
    # C_f compensates the stray capacitance that the OPEN relay contacts and
    # the unused R_g legs leave hanging on the FB node (~15 pF each). Without it the
    # feedback factor rolls off near the loop's unity-gain frequency and the
    # phase margin in the 0 dB mode would be WORSE than in the +10 dB mode -
    # precisely the asymmetry that verification requirement V1 exists to catch.
    # L12 / ADR-025: 22 p -> 330 p. It is now also the lead that holds block B
    # at 0 dB above ADR-019's 60 deg with any cable up to 4.7 nF at the jack and
    # the attenuator at mid-rotation, where 22 p gave 54.97 deg (ADR-024 says
    # where the probe goes). It moves neither the Miller pole (C124) nor slew
    # rate, 20 kHz loop gain or PSRR; it costs closed-loop bandwidth at +10 dB
    # (333 -> 183 kHz). MUST be C0G/NP0, for the same reason as C124.
    C("330p", OUT, FB)
    if switchable:
        R(R_G3, FB, RG)
        # The relay contacts themselves are instantiated in the channel file:
        # one Omron G6K-2F-Y (2 poles) per leg serves both channels - K1 for
        # this leg, K5 for R_G10 below. The design needs the NORMALLY OPEN
        # throw, so that a de-energised or failed relay leaves its leg
        # floating; the contact form was read from the datasheet in L21 and
        # is asserted on the netlist by scripts/check_relay_safe_state.py.

    # local rail decoupling
    C("100n", VP, GND)
    C("100n", VM, GND)
    C("100u", VP, GND, fp=FP_ELCO)
    C("100u", VM, GND, fp=FP_ELCO)

    if switchable:
        # ADR-026: the +10 dB leg, in parallel with R_G3 from the same FB node.
        # Placed AFTER the decoupling capacitors on purpose: appended last, it
        # takes the next free number (R143 here, R242/R442 on the audio board)
        # and every reference designator that existed before L27 keeps its
        # number. A renumbering breaks decks in silence (limitations.md #22).
        R(R_G10, FB, RG10)

    return dict(IN=IN, OUT=OUT, FB=FB, RG=RG, RG10=RG10, VP=VP, VM=VM,
                GND=GND)


# ============================================================================
# HEADROOM - the arithmetic the simulation has to confirm or refute
# ============================================================================
# Positive clip: V+ - I*R_vase - Vce(sat,VAS) - Vbe(Qn) - Iq*R_en
#              = 15 - 0.55 - 0.5 - 0.65 - 0.33 = 12.97 V pk
# Negative clip: symmetric by construction (see the VAS comment).
#              => ~12.97 V pk = 9.17 V RMS
#
# *** REQUIREMENT TENSION - reported, not silently absorbed ***
# E6 (2.7 V RMS max input) x E2 (+10 dB) demands 8.54 V RMS out. Against
# ~9.2 V RMS of clipping that is ~0.6 dB of margin. Positive, so the
# requirements ARE satisfiable - but only just, and the shortfall is
# structural: +/-15 V rails (E7/ADR-003) do not have room for 2.7 x 3.16.
# Three ways out, none of which this file takes unilaterally:
#   (a) the per-input trim of ADR-011: setting the K11 input to -6 dB
#       restores 6 dB of margin. This is what the trim is FOR. RECOMMENDED.
#   (b) +/-18 V rails would give ~11.4 V RMS - a psu-engineer question, and
#       it contradicts E7 so it needs an ADR.
#   (c) accept it: +10 dB exists for a FUTURE low-output chain (ADR-004), not
#       for the K11, and V3 already names this combination as
#       "raggiungibile per errore".
# ============================================================================

# ============================================================================
# SIMULATED RESULTS - Fase 2 draft, 2026-09-08
# Every number below came out of a deck in spice/preamp/tb/, not out of a
# calculation. Re-run them all when the vendor models land (Fase 4).
# Provenance of the device models: spice/preamp/placeholder_devices.lib,
# HAND-AUTHORED PLACEHOLDERS. See the caveats in each testbench header.
#
#   OPERATING POINT (tb_op.cir) - RE-MEASURED IN L22 with the LS352 mirror
#   in place of the THAT320. Every OTHER device here is still a placeholder,
#   so these are still provisional - but the mirror line is not.
#     LSK489 halves     2.211 / 2.163 mA, gm 4.39 / 4.34 mS
#     tail sink          4.374 mA
#     cascode NPNs       2.193 / 2.145 mA
#     LS352 mirror       2.134 / 2.136 mA, Vbe 0.7028 / 0.7026 V,
#                        internal Vbc +0.493 / +0.369 V (the second is the
#                        output half, and it is the number that says how far
#                        from the knee it sits - see the mirror section)
#     VAS (2N5401)       6.443 mA
#     VAS load sink      6.443 mA
#     output pair       14.56 mA
#     output DC offset  -16.6 mV   (was -11.8 mV with the THAT320)
#
#   HEADROOM (tb_dc_headroom.cir)
#     +10 dB clipping   +13.16 / -14.00 V  => 13.16 V pk = 9.31 V RMS usable
#     0 dB CM ceiling   JFET Vds >= 2 V up to Vin = +6.75 V; gain holds to
#                       +9.43 V. Negative side has no limit inside the rails.
#
#   LOOP (tb_loop.cir, tb_loop_blockA.cir, tb_loop_bufferfissa.cir; C_f 330 p)
#     Verdicts by ADR-024 - cable at the jack, minimum over 0-4.7 nF, every V1
#     source, 100 k and 10 k loads; block A with its harness <= 1 nF.
#     Block B on the three-level network of ADR-026 (data/2026-09-14/L27/dopo/):
#     block B 0 dB   loop gain 72.4 dB, crossover 929 kHz, PM 70.2 deg bare,
#                    61.8 deg worst (attenuator at mid-rotation, 3.3 nF),
#                    61.4 deg at the tolerance corners
#     block B +3 dB  loop gain 69.1 dB, crossover 915 kHz, PM 77.4 deg bare,
#                    69.8 deg worst (2.8 nF), 68.7 deg at the corners
#     block B +10 dB loop gain 61.9 dB, crossover 527 kHz, PM 109.8 deg bare,
#                    103.0 deg worst
#     block A        PM 63.4 deg worst (430 ohm source, 1 nF of harness), L12
#     buffer         PM 61.6 deg worst (Stax, 2.7 nF), L12
#     *** THE WORSE MODE IS 0 dB, WHICH IS THE NORMAL MODE. V1 was right to
#         ask for both. ***
#
#   RESPONSE (tb_ac.cir)
#     -3 dB   0.493 Hz / 2.12 MHz (0 dB), 537 kHz (+3 dB), 183 kHz (+10 dB),
#             1.5 ohm source (L27); 1 kHz gain -0.009 / +3.037 / +9.958 dB
#             (L12: C_f 330 p, ADR-025, took +10 dB from 333 kHz to 183 kHz)
#     ADR-014 CLAIM UNDER TEST: 20 kHz response referred to 1 kHz changes by
#     0.0001 dB between attenuator Zout = 0 and 2.5 kOhm. ADR-014 predicted
#     -0.42 dB at 20 kHz WITHOUT a cascode. The cascode does what it was
#     specified to do, with four orders of magnitude to spare.
#
#   Zout (tb_zout_psrr_noise.cir)
#     at the amplifier node: 1.04 ohm (0 dB) / 3.26 ohm (+10 dB), flat to 20 kHz
#     at the jack:           58.8 ohm @1 kHz, 48.0 ohm @20 kHz  -> E4 met
#                            1693 ohm @20 Hz - that is the 4.7 uF reactance,
#                            not a source impedance. E4 read literally fails
#                            at 20 Hz for ANY capacitor-coupled output; see
#                            the report.
#
#   PSRR (same deck, bigger is better; LS352 topology, data/2026-09-13, L18)
#     from V+   72.1 / 59.6 / 39.8 dB at 100 Hz / 1 kHz / 10 kHz  (0 dB mode)
#               62.2 / 49.6 / 29.8 dB                             (+10 dB)
#     from V-   84.3 / 97.7 / 96.2 dB and 74.4 / 87.8 / 86.2 dB
#     THE POSITIVE RAIL IS THE WEAK ONE, by ~30 dB, and it is structural: the
#     mirror emitters and the VAS emitter both stand on V+. The negative rail
#     is quiet because every current source down there is referenced to V-
#     AND BYPASSED TO V- (see the bias-reference comment above).
#     -> psu-engineer: the ripple budget is ADR-020 - 1 uV RMS at the output,
#        both rails, 20 Hz-20 kHz; per-tone limits in REQUIREMENTS.md, E5.
#
#   NOISE, 20 Hz - 20 kHz unweighted (tb_noise_breakdown.cir)
#     0 dB   1.68 uV (1 ohm source) / 1.72 uV (430 ohm) / 1.91 uV (2.5 kOhm)
#     +10 dB 5.70 uV (2.5 kOhm source) - the worst single-block case
#     L27, LS352 topology: +3 dB 2.01 uV and +10 dB 4.23 uV (2.5 kOhm source)
#     Dominant contributors at 1 kHz: the CURRENT MIRROR, not the JFETs.
#       THAT320 pair ~5.3 and ~5.0 nV/rtHz, R_f (1.5k) 4.98 nV/rtHz, the two
#       47 ohm mirror degeneration resistors 4.85 nV/rtHz each, JFETs 1.6.
#     NO 1/f NOISE IS PRESENT (KF = 0 in every placeholder model). This is a
#     floor, not a prediction.
#
#   V2 - GAIN RELAYS (tb_switch_v2.cir + _counterfactual.cir), L27
#     Both relays bouncing (RON 50 mohm, ROFF 1e12, 3 bounces make / 2 break),
#     0 -> +3 -> +10 -> +3 -> 0 dB and 0 <-> +10 dB with the contacts skewed:
#       output stays inside +1.522 / -1.626 V, which IS the +10 dB envelope,
#       in every transition window. It never leaves that band.
#     Counterfactual - the arrangement ADR-004 rejected, relay in series with
#     R_f: opening that contact drives the output to -13.77 V, 1.2 V from the
#     rail. That is the number ADR-004 was protecting against.
#
#   V3 - OVERLOAD RECOVERY (tb_v3_overload.cir)
#     5.6 dB of overdrive (8 V pk in, +10 dB): clips at +13.26 / -13.79 V and
#     returns to within 5 % of its linear envelope in under 1 us. No latch-up,
#     no sticking, DC back to +3 mV at the jack.
#
#   THD: NOT MEASURED, AND NOT MEASURABLE HERE. tb_v3_overload.cir prints
#     0.00084 % at 1.57 V pk. THAT NUMBER IS MEANINGLESS. It is what a
#     hand-authored Gummel-Poon model with invented IS/BF/VAF/TF produces;
#     distortion lives entirely in the parts of a model that were guessed.
#     No distortion figure exists for this design until vendor models do.
# ============================================================================

if __name__ == "__main__":
    sx.reset()
    gain_block(tag="", base=100, switchable=True)

    outdir = os.path.join(REPO, "spice", "preamp")
    os.makedirs(outdir, exist_ok=True)

    try:
        ERC()
    except Exception as e:  # noqa: BLE001
        print("SKiDL ERC raised:", e)

    netpath = os.path.join(REPO, "circuits", "preamp", "gain_block.net")
    generate_netlist(file_=netpath, tool="kicad10")
    print("KiCad netlist ->", netpath)

    sub = sx.subckt(
        "GAINBLOCK",
        ["IN", "OUT", "FB", "RG", "RG10", "VPLUS", "VMINUS"],
        gnd_names=("GND",),
        header=(
            "GENERATED by circuits/preamp/gain_block.py - DO NOT HAND-EDIT.\n"
            "Ports: IN OUT FB RG RG10 VPLUS VMINUS   (node 0 = signal ground)\n"
            "RG, RG10: the two gain-relay contact nodes (ADR-026). An open\n"
            "contact is a stray capacitance to 0, a closed one a short:\n"
            "  0 dB   RG open,   RG10 open\n"
            "  +3 dB  RG to 0,   RG10 open\n"
            "  +10 dB RG to 0,   RG10 to 0\n"
            "Leaving either port unterminated is NOT an open contact.\n"
            "Device models are PLACEHOLDERS - see placeholder_devices.lib."
        ),
    )
    subpath = os.path.join(outdir, "gain_block.subckt")
    with open(subpath, "w") as f:
        f.write(sub)
    print("SPICE subcircuit ->", subpath)

    # Flat version of the same block: identical device lines, but at top
    # level, so that a single-block testbench can probe @q106[ic] directly
    # instead of through ngspice's subcircuit-path syntax.
    flatpath = os.path.join(outdir, "gain_block_flat.inc")
    with open(flatpath, "w") as f:
        f.write("* GENERATED by circuits/preamp/gain_block.py "
                "- DO NOT HAND-EDIT.\n")
        f.write("* Flat single-block netlist. External nodes: "
                "IN OUT FB RG RG10 VPLUS VMINUS 0\n")
        f.write(sx.flat(gnd_names=("GND",)))
    print("SPICE flat include ->", flatpath)
    print("device lines:", len([l for l in sub.splitlines()
                                if l and not l.startswith(("*", "."))]))
