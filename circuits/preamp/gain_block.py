#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gain_block.py - THE gain block of the line preamplifier.

Fase 2 DRAFT. Source of truth for the topology (AGENTS.md rule 2).
Never hand-edit the generated netlist/schematic; edit this file.

ADR-006: one discrete block, designed once, used twice per channel:
    BLOCK A  input buffer,  gain = 1 always  (relay/R_g not fitted)
    BLOCK B  output stage,  gain = 0 / +10 dB, relay on the feedback network

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
R_f is HARD-WIRED from OUT to FB and is never switched. The relay only
connects the far end of R_g to ground.

    contacts CLOSED   -> gain = 1 + R_f/R_g = 3.149  (+9.97 dB)
    contacts OPEN     -> gain = 1 exactly            (0 dB)
    contacts BOUNCING -> gain slides between 1 and 3.149, monotonically

There is no contact state - open, closed, bouncing, welded, corroded - in
which the feedback loop is broken, because the loop does not pass through the
relay at all. The de-energised (power-off / coil-fault) state is unity gain,
which is also the intended normal mode per ADR-001.

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
# all: the LS352 dual PNP of the input mirror is the first, and the LSK489
# dual JFET (L10) is the next. Derived from REPO, never hard-coded, for the
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
R_G = "698"         # ADR-004: switched to GND by the relay.
                    # 1 + 1500/698 = 3.149 = +9.97 dB, i.e. E2's "+10 dB"
                    # to within 0.03 dB using two E96 values.
                    # Chosen small enough that R_f's own Johnson noise
                    # (4.98 nV/rtHz -> 0.70 uV over 20 kHz) stays far below
                    # E5's 10 uV, and large enough that the network is a
                    # 2.2 kOhm load on the output stage at +10 dB (3.9 mA
                    # peak at clipping) - well inside the 15 mA Class A bias.

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
    # RG only exists on a switchable block; creating it unconditionally
    # would leave block A with a pinless net and an ERC warning.
    RG = n("RG") if switchable else None

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

    def J(val, d, g, s, fp=FP_SOIC8):
        i[0] += 1
        j = Part("Device", "Q_NJFET_DGS", value=val, footprint=fp,
                 ref=f"Q{i[0]}")
        j["D"] += d
        j["G"] += g
        j["S"] += s
        sx.spice_dev(j, "J", ["D", "G", "S"], "LSK489X")
        return j

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

    # ADR-013: ONE LSK489 monolithic dual. It is drawn here as two symbols
    # because the KiCad 10 libraries contain no dual-JFET symbol and no
    # LSK489 at all. KNOWN GAP, not an accident: before G2 a project symbol
    # library must supply a single 2-unit LSK489 symbol with the pinout read
    # off the datasheet, or the PCB will place two packages.
    # Flagged to bom-component-manager and pcb-automation-engineer.
    R(R_GATE_STOP, IN, G1)
    R(R_GATE_STOP, FB, G2)
    J("LSK489B (1/2)", D1N, G1, S1)     # non-inverting side
    J("LSK489B (2/2)", D2N, G2, S2)     # inverting side (feedback)
    R(R_SDEG, S1, SRC)
    R(R_SDEG, S2, SRC)
    if r_in:
        R(r_in, IN, GND)                # E3: Zin. See R_IN above.

    # Cascode base reference: 8.485 V from a ~1 mA divider off V+, heavily
    # bypassed to ground so the JFET drains sit still while the rail moves.
    R("4.99k", VP, NCASC)
    R("10.0k", NCASC, GND)
    C("47u", NCASC, GND, fp=FP_ELCO)

    # Cascode transistors, common base: they hold the JFET drains at a fixed
    # 7.8 V, which is what kills the Miller multiplication of C_rss.
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
    # This transistor MUST be thermally coupled to the NPN output device's tab
    # (thermal compound + cable tie is enough at 225 mW) or the bias drifts.
    # Handed to pcb-automation-engineer as a placement rule.
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
    # Class A is guaranteed by arithmetic, not by hope: the heaviest load the
    # stage ever sees is 100 kOhm (cj EV250) in parallel with the 2.2 kOhm
    # feedback network, i.e. 3.9 mA peak at full output - a quarter of the
    # 15 mA bias, so neither device ever turns off.
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
    # C_f compensates the stray capacitance that the OPEN relay contact and
    # the unused R_g leave hanging on the FB node (~15 pF). Without it the
    # feedback factor rolls off near the loop's unity-gain frequency and the
    # phase margin in the 0 dB mode would be WORSE than in the +10 dB mode -
    # precisely the asymmetry that verification requirement V1 exists to catch.
    C("22p", OUT, FB)
    if switchable:
        R(R_G, FB, RG)
        # The relay contact itself is instantiated in the channel file: one
        # Omron G6K-2F-Y (2 poles) serves both channels. The design needs the
        # NORMALLY OPEN throw, so that a de-energised or failed relay leaves
        # the block at unity gain. CONTACT FORM NOT YET CONFIRMED against the
        # Omron datasheet - flagged to bom-component-manager.

    # local rail decoupling
    C("100n", VP, GND)
    C("100n", VM, GND)
    C("100u", VP, GND, fp=FP_ELCO)
    C("100u", VM, GND, fp=FP_ELCO)

    return dict(IN=IN, OUT=OUT, FB=FB, RG=RG, VP=VP, VM=VM, GND=GND)


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
#   LOOP (tb_loop.cir, tb_loop_blockA.cir)
#     0 dB   loop gain 72.3 dB, crossover 954 kHz, PM 63.5 deg (no load cap)
#            PM 58.8 deg at 1 nF of cable, 56.3 deg at 2.2 nF
#     +10 dB loop gain 61.8 dB, crossover 306 kHz, PM 86.2 deg
#     block A PM 69.8 deg bare, 64.1 deg with 1 nF straight on the output node
#     *** THE WORSE MODE IS 0 dB, WHICH IS THE NORMAL MODE. V1 was right to
#         ask for both. ***
#
#   RESPONSE (tb_ac.cir)
#     -3 dB   0.493 Hz / 2.45 MHz (0 dB), 0.493 Hz / 330 kHz (+10 dB)
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
#   PSRR (same deck, bigger is better)
#     from V+   72.0 / 59.5 / 39.7 dB at 100 Hz / 1 kHz / 10 kHz  (0 dB mode)
#               62.1 / 49.6 / 29.8 dB                             (+10 dB)
#     from V-   88.9 / 100.5 / 96.9 dB and 79.0 / 90.5 / 86.9 dB
#     THE POSITIVE RAIL IS THE WEAK ONE, by ~30 dB, and it is structural: the
#     mirror emitters and the VAS emitter both stand on V+. The negative rail
#     is quiet because every current source down there is referenced to V-
#     AND BYPASSED TO V- (see the bias-reference comment above).
#     -> psu-engineer: V+ ripple at 100 Hz must be <= 1 mV pk for the
#        rail contribution to stay under 1 uV at the output in +10 dB mode.
#
#   NOISE, 20 Hz - 20 kHz unweighted (tb_noise_breakdown.cir)
#     0 dB   1.68 uV (1 ohm source) / 1.72 uV (430 ohm) / 1.91 uV (2.5 kOhm)
#     +10 dB 5.70 uV (2.5 kOhm source) - the worst single-block case
#     Dominant contributors at 1 kHz: the CURRENT MIRROR, not the JFETs.
#       THAT320 pair ~5.3 and ~5.0 nV/rtHz, R_f (1.5k) 4.98 nV/rtHz, the two
#       47 ohm mirror degeneration resistors 4.85 nV/rtHz each, JFETs 1.6.
#     NO 1/f NOISE IS PRESENT (KF = 0 in every placeholder model). This is a
#     floor, not a prediction.
#
#   V2 - GAIN RELAY (tb_switch_v2.cir + _counterfactual.cir)
#     With bounce modelled (RON 50 mohm, ROFF 1e12, 3 bounces make / 2 break):
#       output stays inside +/-1.61 V, which IS the +10 dB envelope. It never
#       leaves the band bounded by the two gain settings, at any point.
#     Counterfactual - the arrangement ADR-004 rejected, relay in series with
#     R_f: opening that contact drives the output to -13.68 V, 1.3 V from the
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
        ["IN", "OUT", "FB", "RG", "VPLUS", "VMINUS"],
        gnd_names=("GND",),
        header=(
            "GENERATED by circuits/preamp/gain_block.py - DO NOT HAND-EDIT.\n"
            "Ports: IN OUT FB RG VPLUS VMINUS   (node 0 = signal ground)\n"
            "RG: gain-relay contact node. Tie to 0 for +10 dB; leave it on a\n"
            "stray capacitance for 0 dB - that is what an open contact is.\n"
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
                "IN OUT FB RG VPLUS VMINUS 0\n")
        f.write(sx.flat(gnd_names=("GND",)))
    print("SPICE flat include ->", flatpath)
    print("device lines:", len([l for l in sub.splitlines()
                                if l and not l.startswith(("*", "."))]))
