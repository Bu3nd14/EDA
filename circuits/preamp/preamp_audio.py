#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
preamp_audio.py - the audio board: two channels, four gain blocks.

Fase 2 DRAFT. Source of truth for the topology (AGENTS.md rule 2).

This file demonstrates the ADR-006 contract in the only way that counts: the
SAME function, gain_block(), is called for every block - eight times since
L17 (ADR-023). There is no second topology to validate, and no place for the
channels or the outputs to drift apart.

   IN_L -> LDR_S -+-> [BLOCK A] -+-> [BUFFER F1] -> 47R -> 4.7u -> K2 -> FIXED OUT 1 (Singxer)
    (ADR-038)   LDR_P  (buffer,  +-> [BUFFER F2] -> 47R -> 4.7u -> K3 -> FIXED OUT 2 (Stax)
                  |    gain 1)
                 GND
                                    +-> [TRIM 0/-6/-12 dB] -> attenuator (off board, 10k stepped)
                                           (trim.py, K7/K8)          |
                                                                     v
                                                                [BLOCK B] -> 47R -> 4.7u -> K4 -> MAIN OUT
                                                        (0 / +3 / +10 dB, relays K1 + K5 on R_g)
   and the same again for the right channel.

ADR-023: class A must hold on every path someone can listen to. A short, or a
switched-off device with a low input impedance, on ONE output may take only
the block that serves THAT output out of class A - never block A, which feeds
the main path and the other fixed output. Hence one buffer per fixed output.

ADR-027 (L16): ONE trim for all inputs, on the VARIABLE branch only. The fixed
outputs take block A's output before it and stay a faithful copy of the
source; the trim sets the level of the main output alone. Its bistable relays,
its LEDs and its interlock with the mute live in trim.py.

WHAT IS DELIBERATELY NOT HERE
-----------------------------
 - The INPUT SELECTOR (F1 / ADR-009). It is upstream of IN_L/IN_R, and its
   relays do not interact with the gain blocks.
 - The stepped ATTENUATOR itself (F4). It is a rotary switch on the front
   panel, not a PCB part; it appears here as a 3-pin harness connector per
   channel. Its ELECTRICAL effect - a source impedance that swings 0 -> 2.5k
   -> 0 with the knob, 2.611k at most behind the trim - is what the
   simulations in spice/preamp/tb sweep.
 - The MUTE TIMER (ADR-012) and the VRELAY supply. Only the mute contacts are
   here, because they are in the signal path and change Zout, plus the mute
   COMMAND net, because the trim's permissive hangs on it. The coil drive, the
   delay and the rail-collapse detector belong to psu-engineer.
 - The DRIVE of the graduated mute's LEDs (ADR-038, L29b2): two current
   sources and the depth generator. Only the cells (in the signal path) and
   the J3 harness to the LEDs are here; the contract the drive must honour
   is written next to J3 below (profile v4, Td = 6 s, ADR-039, ADR-040).

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

from skidl import Part, Net, generate_netlist, POWER, ERC  # noqa: E402

import spice_export as sx  # noqa: E402
import trim  # noqa: E402
import gain_interlock  # noqa: E402
from gain_block import (  # noqa: E402
    gain_block, FP_R, FP_ELCO, REPO,
)

FP_FILM_P15 = "Capacitor_THT:C_Rect_L16.5mm_W7.0mm_P15.00mm_MKT"
FP_FILM_P22 = "Capacitor_THT:C_Rect_L26.5mm_W10.5mm_P22.50mm_MKS4"
FP_RELAY = "Relay_SMD:Relay_DPDT_Omron_G6K-2F-Y"
FP_CONN3 = "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical"
FP_CONN2 = "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical"

# Omron G6K-2F-Y, 2 Form C. READ FROM THE DATASHEET, not deduced:
# vendor/relays/omron/G6K/en-g6k.pdf, page 6, the G6K-2F-Y row, block
# "Terminal Arrangement / Internal Connections (TOP VIEW)".
#
#   coil     1, 8
#   pole 1   COM 3   NC 2   NO 4      (bottom row, numbered 1-2-3-4)
#   pole 2   COM 6   NC 7   NO 5      (top row,    numbered 8-7-6-5)
#
# THE TRAP, and it is why this used to be wrong (NC-014, blocking, opened
# by L8 and closed by L21): both armatures lean the SAME way - each rests
# on the pad immediately to the LEFT of its own COM - but the two rows are
# numbered in OPPOSITE directions. So "NO = COM+1" is right for pole 1 and
# WRONG for pole 2. Until L21 this file carried the deduced version,
# K_NO2/K_NC2 swapped, which left the RIGHT channel un-muted at power-on:
# the silent failure ADR-012 exists to prevent, into a pair of
# electrostatics.
#
# Re-read at the source in L21 on three independent legs that agree - the
# rendered page, the SVG vector coordinates (the armature passes 0.44 pt
# from its NC contact and 3.39 pt from its NO one, ratio 7.6:1, on BOTH
# poles), and the polylines of the KiCad symbol G6K-2, where the armature
# tip's x is EXACTLY the NC contact's x. Details in
# docs/preamp/reports/2026-09-11-L21-polo-2-rele.md and, for L8's first
# reading, reports/2026-09-10-L8-parti-nuove.md.
#
# What each relay needs, and the design fails safe only if they are right:
#   gain relays - NORMALLY OPEN (de-energised => R_g leg floating; both
#                 de-energised => 0 dB, ADR-004 / ADR-019 / ADR-026)
#   mute relay - a CHANGEOVER per output (ADR-044): de-energised => NC
#                grounds the cap side, NO leaves the jack open on its bleed
#                => silent when the supply is down (ADR-012)
#   permissive  - NORMALLY CLOSED, twice in series (de-energised = muted =>
#                 the trim command is live, ADR-019 / ADR-027; trim.py);
#                 since L36 its pole-1 NO is VHOLD, the gain hold's supply
#   gain aux    - K11 / K12 (L36, ADR-030 road B): coil in parallel with
#                 K1 / K5, pole 1 NO = the self-hold, pole 2 = the LEDs
#                 (gain_interlock.py)
# All are asserted on the generated netlist by
# scripts/check_relay_safe_state.py, which run_tests.sh runs: a deduced pin
# map cannot come back in silence. This is the ONE copy of the G6K-2F-Y map:
# trim.py receives it, it does not keep its own.
K_COIL_A, K_COIL_B = "1", "8"
K_COM1, K_NO1, K_NC1 = "3", "4", "2"
K_COM2, K_NO2, K_NC2 = "6", "5", "7"

_n = [0]


def R(val, a, b, base, fp=FP_R):
    _n[0] += 1
    r = Part("Device", "R", value=val, footprint=fp, ref=f"R{base + _n[0]}")
    r[1] += a
    r[2] += b
    return r


def C(val, a, b, base, fp=FP_FILM_P15):
    _n[0] += 1
    c = Part("Device", "C", value=val, footprint=fp, ref=f"C{base + _n[0]}")
    c[1] += a
    c[2] += b
    return c


def channel(ch, base, vp, vm, gnd, k_gain, k_gain10, k_mute, k_trim, k_pole):
    """One complete channel. ch is "L" or "R"; base offsets the refs."""
    global _n
    # ---------------- BLOCK A: input buffer, gain 1 always -----------------
    # switchable=False: R_g and the relay leg are simply NOT FITTED (ADR-006 -
    # same board, same part numbers, one resistor left out).
    a = gain_block(tag=f"A{ch}", base=base, switchable=False, r_in="1M",
                   vp=vp, vm=vm, gnd=gnd)

    _n[0] = 60
    inconn = Part("Connector_Generic", "Conn_01x02", value=f"IN_{ch}",
                  footprint=FP_CONN2, ref=f"J{base + 1}")
    in_src = Net(f"{ch}_IN_SRC")
    inconn[1] += in_src
    inconn[2] += gnd

    # ---- the graduated mute, UPSTREAM (ADR-038, L29b2) --------------------
    # Two opto-coupled photoresistors (Excelitas VTL5C4) per channel at block
    # A's input: one IN SERIES from the connector to block A, one TO GROUND on
    # block A's input, next to R_IN = 1 MOhm (gain_block.py). Block A feeds
    # all three outputs, so one point per channel fades them all; and there is
    # no DC here (the input is referred to ground by R_IN), which is what ESP
    # asks of a mute ("no DC along with the signal", ADR-038).
    # The LEDs are driven from ground, OUTSIDE the signal path (ADR-022): only
    # the cells (pins 3-4) touch these nets; the LEDs go to the harness J3 in
    # the caller. The part is NOT confirmed at a distributor (ADR-038, before
    # G2). Every figure on it comes from
    # models/optocoupler/vtl5c4_comportamentale.lib: "modello comportamentale
    # dal datasheet, con estrapolazione dichiarata" (docs/preamp/reports/
    # 2026-09-21-L29b-mute-ldr-misura.md, 2026-09-22-L29b2-*.md).
    ls = Part("Isolator", "VTL5C", value=f"VTL5C4 LDR_S_{ch}",
              footprint="OptoDevice:PerkinElmer_VTL5C", ref=f"U{base + 1}")
    ls[3] += in_src
    ls[4] += a["IN"]
    lp = Part("Isolator", "VTL5C", value=f"VTL5C4 LDR_P_{ch}",
              footprint="OptoDevice:PerkinElmer_VTL5C", ref=f"U{base + 2}")
    lp[3] += a["IN"]
    lp[4] += gnd

    # ---- attenuator harness (off-board rotary, F4/ADR-009) --------------
    # Since L16 (ADR-027) its top pin is NOT block A's output: it is the COM
    # of the trim relay T1, which connects it to block A's output (0 dB) or to
    # a tap of the trim ladder. See trim.trim_channel() below.
    att_top, att_wiper = Net(f"{ch}_ATT_TOP"), Net(f"{ch}_ATT_W")
    ac = Part("Connector_Generic", "Conn_01x03", value=f"ATT_{ch} 10k",
              footprint=FP_CONN3, ref=f"J{base + 20}")
    ac[1] += att_top
    ac[2] += att_wiper
    ac[3] += gnd

    # ---- two fixed-level outputs, ONE BUFFER EACH (ADR-023) --------------
    # Until L17 both fixed outputs hung straight off block A's output, which
    # is also block A's feedback node and the top of the attenuator (ADR-008).
    # A switched-off device with a low Zin on either jack then pushed block A
    # into class B: I_C(Q132) minimum -0.23 uA at 10 ohm downstream
    # (NC-010, docs/preamp/data/2026-09-14/tb_blockA_carichi_10.csv) - and
    # with it the MAIN path and the other fixed output, which someone may be
    # listening to. ADR-023 (the user's decision of 2026-09-14) forbids that
    # and supersedes ADR-008: each fixed output gets its own buffer, and a
    # fault on one jack stays inside the block that serves that jack.
    #
    # The buffer is THE gain block again (T3 / ADR-006), wired as block A is:
    # switchable=False, unity gain by construction. r_in=None: its gate is
    # DC-returned by block A's output, a ~1 ohm DC-coupled source, so a
    # 1 MOhm to ground would only load block A for nothing - the same
    # reasoning as block B, whose gate the attenuator returns.
    # A buffer on a shorted or dead-loaded jack DOES go class B (same ~20 mA
    # bias, same 47 ohm): ADR-023 admits that, because nobody listens to that
    # output, provided P7 / ADR-021 hold for it (tb_mute_corto.cir, L17).
    #
    # 47 ohm isolation resistors - see the ADR-008 addendum of 2026-09-08.
    # The designer implemented the original "~100 ohm" as written and RAISED
    # the conflict with E4 (which asks Zout < 100 ohm, and 100 ohm sits AT
    # the limit rather than under it) instead of editing the ADR unilaterally.
    # The orchestrator resolved it to 47 ohm: satisfies E4 with margin. With
    # one buffer per output it is no longer what isolates Singxer from Stax -
    # the buffers are - but it still keeps the cable capacitance outside the
    # buffer's loop, exactly as on the main output.
    # ADR-021 rating constraint for the BOM: with a short at a fixed
    # connector each 47 ohm dissipates up to 0.155 W (tb_mute_corto.cir),
    # so rate it >= 0.16 W at 60 C.
    for k, (name, cval) in enumerate((("SINGXER", "4.7u"), ("STAX", "4.7u"))):
        # Refs 500/600 (L) and 700/800 (R): 1xx-4xx are blocks A and B.
        # The passives below keep the channel's own numbering (R161-R166,
        # R361-R366), which is what preamp_blocks_draw.py reads.
        f = gain_block(tag=f"F{k + 1}{ch}", base=base + 400 + 100 * k,
                       switchable=False, r_in=None, vp=vp, vm=vm, gnd=gnd)
        # The buffer's input joins block A's output, BEFORE the trim: the
        # fixed outputs are a faithful copy of the source (ADR-027). NOTE on
        # the NAME of that node in the netlist: SKiDL picks one of the merged
        # names, and L17 saw it come out as F1L_IN, F2L_IN or AR_OUT depending
        # on the run and the channel - no connection order made it stable.
        # Nothing in the repo reads it; do not start relying on it.
        a["OUT"] += f["IN"]
        # 4.7 uF on BOTH fixed outputs - see the ADR-007 addendum.
        # The Stax alone would be happy at 2.2 uF (50 kOhm => 1.4 Hz), but the
        # Singxer's input impedance is NOT PUBLISHED (Fase 1 read the official
        # manual), so its corner is unknowable. 4.7 uF closes that question,
        # and using one value on all three outputs removes a BOM line and an
        # assembly error - fitting the wrong cap in the wrong position would
        # be silent. The cost is board area, which ADR-010's single chassis
        # can absorb.
        fx = Net(f"{ch}_FIX{k + 1}")
        # ADR-044 (geometry iii): the mute relay's changeover sits BETWEEN the
        # coupling cap and the jack, so the cap's far side is its own node,
        # FIXC. The jack node is FIXJACK, joined to the connector pin below.
        fc = Net(f"{ch}_FIXC{k + 1}")
        jk = Net(f"{ch}_FIXJACK{k + 1}")
        R("47", f["OUT"], fx, base)
        C(cval, fx, fc, base, fp=FP_FILM_P15)
        # DC return for the coupling cap. Without it the far side floats when
        # nothing is plugged in, charges on leakage, and thumps on connection.
        # 470k keeps the corner where ADR-007 put it: 470k||50k = 45.2k with
        # 2.2 uF => 1.6 Hz. It stays ON THE JACK: with the relay at rest
        # the jack is grounded only through it - ADR-044 point 2, the user's
        # "Il bleed basta" (RBL1 / RBL2 in the V2 decks).
        R("470k", jk, gnd, base)
        # ADR-044: the bleed on the CAP side (RBC1 / RBC2 in the V2 decks),
        # 470k as measured in L29d2. It only matters in the 1 ms transfer of
        # the changeover, when neither throw holds FIXC; L29e kept it on the
        # user's decision of 2026-09-25 ("Tenerlo"): no run measured the
        # geometry without it. Explicit ref, so that nothing after it in
        # this channel renumbers (limitations #22).
        rbc = Part("Device", "R", value="470k", footprint=FP_R,
                   ref=f"R{base + 67 + k}")
        rbc[1] += fc
        rbc[2] += gnd
        cn = Part("Connector_Generic", "Conn_01x02",
                  value=f"{name}_{ch}", footprint=FP_CONN2,
                  ref=f"J{base + 10 + k}")
        cn[1] += Net(f"{ch}_FIXOUT{k + 1}")
        cn[2] += gnd
        jk += cn[1]
        k_mute[k].append(fc)
        k_mute[k].append(jk)

    # ---- the common trim, variable branch only (L16, ADR-027) ------------
    # Between block A's output and the attenuator harness. Ladder and signal
    # contacts per channel; the relays are shared and made by the caller.
    trim.trim_channel(ch, a["OUT"], att_top, gnd, k_trim["T1"], k_trim["T2"],
                      k_pole)

    # ---------------- BLOCK B: output stage, 0 / +3 / +10 dB ---------------
    # r_in=None: the attenuator ladder is itself the gate's DC return (at most
    # 10 kOhm to ground in every knob position), so a second resistor here
    # would only add noise and load the wiper.
    b = gain_block(tag=f"B{ch}", base=base + 100, switchable=True, r_in=None,
                   vp=vp, vm=vm, gnd=gnd)
    b["IN"] += att_wiper

    _n[0] = 60
    main_a, main_j = Net(f"{ch}_MAIN_A"), Net(f"{ch}_MAINJACK")
    main_c = Net(f"{ch}_MAINC")    # the cap's far side, ADR-044 (see above)
    # 47 ohm output isolation. The feedback is taken BEFORE it, on purpose:
    # that keeps every picofarad of interconnect cable outside the loop, at
    # the cost of 47 ohm of Zout - which E4 (<100 ohm) has room for.
    # Taking feedback after it would give ~1 ohm of Zout and put the cable
    # capacitance inside the loop, which is the classic way to make a
    # discrete stage ring on a long interconnect.
    # ADR-021 rating constraint for the BOM: with a short at MAIN_OUT and the
    # block at +10 dB, 20 kHz full scale, this resistor dissipates 1.10 W
    # (tb_mute_corto.cir, docs/preamp/data/2026-09-14/). It must be rated
    # >= 1.1 W at 60 C; the DIN0207 footprint alone does not guarantee that.
    R("47", b["OUT"], main_a, base + 100)
    # C_out: 4.7u film - ADR-007. Sized for a FUTURE 10 kOhm power amp
    # (3.4 Hz), not for the cj EV250's 100 kOhm, on the same logic that put
    # the +10 dB mode in (ADR-004): the load may change, the capacitor won't.
    C("4.7u", main_a, main_c, base + 100, fp=FP_FILM_P22)
    # bleeder; 220k||100k, 4.7u => 0.49 Hz. On the JACK, as on the fixed
    # outputs: ADR-044 point 2 (RBLM in the V2 decks).
    R("220k", main_j, gnd, base + 100)
    # ADR-044: the cap-side bleed (RBCM in the V2 decks), 220k as measured in
    # L29d2 and kept by the user in L29e. Explicit ref (limitations #22).
    rbcm = Part("Device", "R", value="220k", footprint=FP_R,
                ref=f"R{base + 164}")
    rbcm[1] += main_c
    rbcm[2] += gnd
    mc = Part("Connector_Generic", "Conn_01x02", value=f"MAIN_{ch}",
              footprint=FP_CONN2, ref=f"J{base + 130}")
    mc[1] += Net(f"{ch}_MAINOUT")
    mc[2] += gnd
    main_j += mc[1]
    k_mute[2].append(main_c)
    k_mute[2].append(main_j)

    # ---- gain relay legs, ADR-004 / ADR-026 ----------------------------
    # ONE pole of each gain relay per channel: K_GAIN (K1) grounds the R_g3
    # leg, K_GAIN10 (K5) the R_g10 leg. Both relays are shared by the two
    # channels, which is why the caller creates them and not this function.
    k_gain[K_COM1 if k_pole == 0 else K_COM2] += b["RG"]
    k_gain[K_NO1 if k_pole == 0 else K_NO2] += gnd
    k_gain10[K_COM1 if k_pole == 0 else K_COM2] += b["RG10"]
    k_gain10[K_NO1 if k_pole == 0 else K_NO2] += gnd
    return a, b, ls, lp


if __name__ == "__main__":
    sx.reset()

    VP, VM, GND = Net("VPLUS"), Net("VMINUS"), Net("GND")
    GND.drive = POWER
    VCC_RLY = Net("VRELAY")

    # Shared relays. G6K-2F-Y is 2 Form C, so ONE relay covers both channels.
    # The gain relays K1 (R_g3 leg) and K5 (R_g10 leg, ADR-026: K5 and not K2
    # so that the mute relays keep their references, limitations #22) are
    # made below by gain_interlock.gain_relays(), since L36 (ADR-041): their
    # coils hang on the gain selector, the trim's permissive and their
    # self-holding auxiliaries K11 / K12.
    #     0 dB    K1 off  K5 off   (the de-energised state, F5)
    #     +3 dB   K1 on   K5 off
    #     +10 dB  K1 on   K5 on
    # Coil budget for psu-engineer (vendor/relays/omron/G6K/en-g6k.pdf,
    # ratings table, +/-10 %): 21.1 mA at 5 V, 9.1 mA at 12 V, 4.6 mA at 24 V
    # per coil, the same for the G6KU-2F-Y bistables. Since L36 (ADR-030
    # road B, ADR-041), the worst case is +10 dB, EIGHT coils either way:
    #   out of mute: K1, K5, their auxiliaries K11 / K12, K2-K4 and the
    #     permissive K6 = 168.8 / 72.8 / 36.8 mA; the bistables draw nothing;
    #   in mute: K1, K5, K11, K12, plus the four bistable coils (K7-K10)
    #     driven continuously by the trim knob = 168.8 / 72.8 / 36.8 mA,
    #     plus ~4 mA of LED (trim and gain, one each).
    # The VRELAY voltage is not decided yet. One more constraint since L36:
    # the gain pick-up passes through a Schottky (gain_interlock.py), so
    # VRELAY - V_F(42 mA) >= 80 % of the rated coil voltage, at -5 % and warm.

    # Three mute relays: 6 output lines (3 outputs x 2 channels), 2 poles each.
    # ADR-012 puts mute on ALL outputs, and the reason is the headphone
    # branch: the turn-on transient goes straight into a pair of
    # electrostatics, not into a loudspeaker two metres away.
    # Until L29e this was a SHUNT at the jack, on the argument that a series
    # contact would sit in the signal path for good (ADR-004). L29c measured
    # the price: 0.1 ohm behind 47 ohm attenuates only ~1/471, and a gain
    # change with the relay closed put 111-267 uV on the jack. ADR-044
    # (geometry iii, the user's choice of 2026-09-25) makes each pole a
    # CHANGEOVER: COM on the cap's far side, NO to the jack, NC to ground.
    # The series contact is the price ADR-004 feared, and L29d2 paid it on
    # the whole V2 matrix: 0 cells out of 253.
    K_MUTE = []
    mute_lists = [[], [], []]
    MUTE_CMD = Net("MUTE_CMD")   # ONE net: SKiDL's Net("MUTE_CMD") inside the
                                 # loop would have made MUTE_CMD, MUTE_CMD1,
                                 # MUTE_CMD2 - three coils on three separate
                                 # nets, and only an ERC warning to say so.
    for i in range(3):
        k = Part("Relay", "G6K-2", value=f"G6K-2F-Y MUTE{i + 1}",
                 footprint=FP_RELAY, ref=f"K{i + 2}")
        k[K_COIL_A] += VCC_RLY
        k[K_COIL_B] += MUTE_CMD
        K_MUTE.append(k)

    # ADR-027 / F8 / F9: the trim's relays (K7, K8), their LED twins (K9,
    # K10), the command switch and the permissive K6 on MUTE_CMD. Every mute
    # pole carries signal, so the permissive is a relay of its own.
    K_TRIM = trim.trim_relays(VCC_RLY, MUTE_CMD,
                              (K_COIL_A, K_COIL_B, K_COM1, K_NO1, K_NC1,
                               K_COM2, K_NO2, K_NC2))

    # ADR-041 / ADR-030 road B (L36): the gain changes only in mute, like the
    # trim, through the same permissive K6; K1 / K5 hold themselves out of
    # mute through their auxiliaries K11 / K12, whose free poles light the
    # three gain LEDs. The race at mute release is closed in there.
    K_GAIN, K_GAIN10 = gain_interlock.gain_relays(
        VCC_RLY, K_TRIM, (K_COIL_A, K_COIL_B, K_COM1, K_NO1, K_NC1,
                          K_COM2, K_NO2, K_NC2))

    chans = {}
    for ch, base, pole in (("L", 100, 0), ("R", 300, 1)):
        chans[ch] = channel(ch, base, VP, VM, GND, K_GAIN, K_GAIN10,
                            mute_lists, K_TRIM, pole)

    # ---- the LDR command harness, J3 (ADR-038, ADR-022; L29b2) -----------
    # The LEDs of the SAME function are in SERIES across the two channels
    # (series cell L then R, shunt cell L then R): one current source per
    # function, so the channels cannot fade at different speeds from a drive
    # mismatch - what is left is the parts' own spread, which is L29c's.
    # The drive is OFF THIS BOARD, like the mute timer: a current source per
    # string, cathode end to GND at the source (psu-engineer / L35).
    # THE CONTRACT the drive must honour - profile v4 with Td = 6 s, the
    # user's choice of 2026-09-22 (ADR-039, ADR-040; Td from L29b):
    #   one depth d in [0, 1], reversible, 0 -> 1 in Td = 6 s on insertion
    #   and back from wherever it is on release (a half-way reversal
    #   retraces the same path, ADR-038 point 3);
    #   series string, log-linear by segments: 20 mA at d = 0 -> 0.2 mA at
    #     d = 0.1 -> 4.5 uA at d = 0.45 -> 0.19 uA at d = 0.75 (the dark
    #     knee, curve B) -> 10 nA at d = 0.8 and beyond. The segment down to
    #     the knee is slow ON PURPOSE: on release the cell turns on as fast
    #     as its LED, and v3's 10 nA -> 4.5 uA in 0.3 s put a 30 dB jump in
    #     100 ms on the jack (limit 20 dB, ADR-040); v4 makes it 4 dB;
    #   shunt string: 10 nA up to d = 0.5 -> 20 mA at d = 1, log-linear;
    #   10 nA of idle current on BOTH strings, never 0: it sits below the
    #     dark knee (0.19 uA, curve B) but the anode never jumps from 0 V,
    #     which through the 0.5 pF LED-cell coupling had put 4.8 mV into a
    #     1 MOhm node (profile v1, L29b);
    #   the jack relays follow the FULL depth: MUTE_CMD de-energises (jacks
    #     disconnected, cap sides grounded: ADR-012 as ADR-044 reads it) 0.5 s after d = 1 and re-energises at the start
    #     of the release, before d moves. 0.5 s because the series cell
    #     darkens slowly: 50 ms left it at 576 kOhm and C2 at 1.05 mV (L29b).
    j3 = Part("Connector_Generic", "Conn_01x04", value="LDR_CMD",
              footprint="Connector_PinHeader_2.54mm:"
                        "PinHeader_1x04_P2.54mm_Vertical", ref="J3")
    for fn, pin_a, pin_k, idx in (("S", 1, 2, 2), ("P", 3, 4, 3)):
        left, right = chans["L"][idx], chans["R"][idx]
        # VTL5C symbol: pin 2 = LED anode (+), pin 1 = LED cathode (-).
        j3[pin_a] += left[2]
        left[1] += Net(f"LDR_{fn}_MID")
        right[2] += left[1]
        j3[pin_k] += right[1]

    # Wire the mute contacts - ADR-044, geometry iii. mute_lists[i] holds, per
    # output pair, [cap_side_L, jack_L, cap_side_R, jack_R]; each jack node
    # already carries its connector pin. Each pole is a CHANGEOVER:
    #   COM - the coupling cap's far side (FIXCk / MAINC);
    #   NO  - the jack: the signal passes only with the coil energised;
    #   NC  - ground: with the coil de-energised the cap side is grounded
    #         through the contact and the JACK is isolated, held at ground
    #         only by its bleed (220k / 470k). That is ADR-012's safe state
    #         as ADR-044 point 2 reads it ("Il bleed basta", the user).
    # Break-before-make is the changeover's own: on insertion the NO opens
    # and then the NC closes, on release the NC opens and then the NO closes
    # - the order L29d2 simulated, with 1 ms of transfer. The pin map is read
    # from the datasheet (en-g6k.pdf p. 6 of the PDF, G6K-2F-Y, TOP VIEW,
    # de-energised; re-read in L29e): armature pivots on 3 / 6, rests on
    # 2 / 7, open to 4 / 5 - K_COM/K_NC/K_NO above (NC-014).
    # Failing safe = failing silent: supply down or timer not released =>
    # coil de-energised => every jack disconnected from its stage.
    # The mute may be held INDEFINITELY (ADR-021, superseding ADR-012's "a few
    # seconds"): its command is the trim's permissive, through K6 (ADR-019,
    # ADR-027). P7, re-read in L29e: in mute the output stages still run in
    # class B - since L17 (ADR-023) the two fixed buffers and block B, each
    # on its own 47 ohm; block A only drives the buffers and the trim. What
    # goes to ground is now the cap's far side instead of the jack, and the
    # stage sees the SAME load either way: 47 ohm plus 4.7 uF to ground.
    # tb_mute_corto.cir (L17) grounds the jack side of that cap through
    # 0.01 ohm; here it is the cap side through the contact (0.1 ohm, the
    # contact's own figure in the V2 decks), so L17's P7 figures keep
    # holding for the mute case, 0.09 ohm behind 47 ohm aside. ADR-021 asks
    # only that every part stay inside its thermal and SOA limits.
    # Unlike the shunt at the jack it replaces, this mute DOES isolate an
    # external short on a jack from its stage - but only while muted: it is
    # still not a short-circuit protection.
    for i, k in enumerate(K_MUTE):
        lst = mute_lists[i]
        for pole_i, (com, no, nc) in enumerate(((K_COM1, K_NO1, K_NC1),
                                                (K_COM2, K_NO2, K_NC2))):
            k[com] += lst[pole_i * 2]       # cap side
            k[no] += lst[pole_i * 2 + 1]    # jack: passes when energised
            k[nc] += GND                    # cap side to ground at rest

    pc = Part("Connector_Generic", "Conn_01x04", value="POWER",
              footprint="Connector_PinHeader_2.54mm:"
                        "PinHeader_1x04_P2.54mm_Vertical", ref="J1")
    pc[1] += VP
    pc[2] += GND
    pc[3] += VM
    pc[4] += VCC_RLY

    try:
        ERC()
    except Exception as e:  # noqa: BLE001
        print("SKiDL ERC raised:", e)

    netpath = os.environ.get(
        "PREAMP_AUDIO_NET_OUT",
        os.path.join(REPO, "circuits", "preamp", "preamp_audio.net"))
    generate_netlist(file_=netpath, tool="kicad10")
    print("KiCad netlist ->", netpath)
