#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
preamp_audio.py - the audio board: two channels, four gain blocks.

Fase 2 DRAFT. Source of truth for the topology (AGENTS.md rule 2).

This file demonstrates the ADR-006 contract in the only way that counts: the
SAME function, gain_block(), is called for every block - eight times since
L17 (ADR-023). There is no second topology to validate, and no place for the
channels or the outputs to drift apart.

                 IN_L -> [BLOCK A] -+-> [BUFFER F1] -> 47R -> 4.7u -> FIXED OUT 1 (Singxer)
                (buffer, gain 1)    +-> [BUFFER F2] -> 47R -> 4.7u -> FIXED OUT 2 (Stax)
                                    +-> attenuator (off board, 10k stepped)
                                            |
                                            v
                                       [BLOCK B] -> 47R -> 4.7u -> MAIN OUT
                               (0 / +3 / +10 dB, relays K1 + K5 on R_g)
   and the same again for the right channel.

ADR-023: class A must hold on every path someone can listen to. A short, or a
switched-off device with a low input impedance, on ONE output may take only
the block that serves THAT output out of class A - never block A, which feeds
the main path and the other fixed output. Hence one buffer per fixed output.

WHAT IS DELIBERATELY NOT HERE
-----------------------------
 - The INPUT SELECTOR and the per-input trim (F1, F2 / ADR-009, ADR-011).
   They are a separate board upstream of IN_L/IN_R, and their relays and
   jumpers do not interact with the gain blocks. Drawing them here would
   couple two boards in one file for no benefit.
 - The stepped ATTENUATOR itself (F4). It is a rotary switch on the front
   panel, not a PCB part; it appears here as a 3-pin harness connector per
   channel. Its ELECTRICAL effect - a source impedance that swings 0 -> 2.5k
   -> 0 with the knob - is what the simulations in spice/preamp/tb sweep.
 - The MUTE TIMER (ADR-012). Only the mute contacts are here, because they
   are in the signal path and change Zout. The coil drive, the delay and the
   rail-collapse detector belong to psu-engineer.

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
#   mute relay - NORMALLY CLOSED (de-energised => outputs shorted to ground
#                => silent when the supply is down, ADR-012)
# Both are asserted on the generated netlist by
# scripts/check_relay_safe_state.py, which run_tests.sh runs: a deduced pin
# map cannot come back in silence.
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


def channel(ch, base, vp, vm, gnd, k_gain, k_gain10, k_mute, k_pole):
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
    inconn[1] += a["IN"]
    inconn[2] += gnd

    # ---- attenuator harness (off-board rotary, F4/ADR-009) --------------
    # Built BEFORE the fixed-output buffers, so their inputs join this net.
    att_top, att_wiper = Net(f"{ch}_ATT_TOP"), Net(f"{ch}_ATT_W")
    att_top += a["OUT"]
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
    # A buffer on a shorted or dead-loaded jack DOES go class B (same 15 mA
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
        # The buffer's input joins block A's output. NOTE on the NAME of that
        # node in the netlist: SKiDL picks one of the merged names, and L17
        # saw it come out as F1L_IN, F2L_IN or AR_OUT depending on the run and
        # the channel - no connection order made it stable. Nothing in the
        # repo reads it; do not start relying on it.
        att_top += f["IN"]
        # 4.7 uF on BOTH fixed outputs - see the ADR-007 addendum.
        # The Stax alone would be happy at 2.2 uF (50 kOhm => 1.4 Hz), but the
        # Singxer's input impedance is NOT PUBLISHED (Fase 1 read the official
        # manual), so its corner is unknowable. 4.7 uF closes that question,
        # and using one value on all three outputs removes a BOM line and an
        # assembly error - fitting the wrong cap in the wrong position would
        # be silent. The cost is board area, which ADR-010's single chassis
        # can absorb.
        fx = Net(f"{ch}_FIX{k + 1}")
        jk = Net(f"{ch}_FIXJACK{k + 1}")
        R("47", f["OUT"], fx, base)
        C(cval, fx, jk, base, fp=FP_FILM_P15)
        # DC return for the coupling cap. Without it the far side floats when
        # nothing is plugged in, charges on leakage, and thumps on connection.
        # 470k keeps the corner where ADR-007 put it: 470k||50k = 45.2k with
        # 2.2 uF => 1.6 Hz.
        R("470k", jk, gnd, base)
        k_mute[k].append(jk)
        cn = Part("Connector_Generic", "Conn_01x02",
                  value=f"{name}_{ch}", footprint=FP_CONN2,
                  ref=f"J{base + 10 + k}")
        cn[1] += Net(f"{ch}_FIXOUT{k + 1}")
        cn[2] += gnd
        k_mute[k].append(cn[1])

    # ---------------- BLOCK B: output stage, 0 / +3 / +10 dB ---------------
    # r_in=None: the attenuator ladder is itself the gate's DC return (at most
    # 10 kOhm to ground in every knob position), so a second resistor here
    # would only add noise and load the wiper.
    b = gain_block(tag=f"B{ch}", base=base + 100, switchable=True, r_in=None,
                   vp=vp, vm=vm, gnd=gnd)
    b["IN"] += att_wiper

    _n[0] = 60
    main_a, main_j = Net(f"{ch}_MAIN_A"), Net(f"{ch}_MAINJACK")
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
    C("4.7u", main_a, main_j, base + 100, fp=FP_FILM_P22)
    R("220k", main_j, gnd, base + 100)   # bleeder; 220k||100k, 4.7u => 0.49 Hz
    mc = Part("Connector_Generic", "Conn_01x02", value=f"MAIN_{ch}",
              footprint=FP_CONN2, ref=f"J{base + 130}")
    mc[1] += Net(f"{ch}_MAINOUT")
    mc[2] += gnd
    k_mute[2].append(main_j)
    k_mute[2].append(mc[1])

    # ---- gain relay legs, ADR-004 / ADR-026 ----------------------------
    # ONE pole of each gain relay per channel: K_GAIN (K1) grounds the R_g3
    # leg, K_GAIN10 (K5) the R_g10 leg. Both relays are shared by the two
    # channels, which is why the caller creates them and not this function.
    k_gain[K_COM1 if k_pole == 0 else K_COM2] += b["RG"]
    k_gain[K_NO1 if k_pole == 0 else K_NO2] += gnd
    k_gain10[K_COM1 if k_pole == 0 else K_COM2] += b["RG10"]
    k_gain10[K_NO1 if k_pole == 0 else K_NO2] += gnd
    return a, b


if __name__ == "__main__":
    sx.reset()

    VP, VM, GND = Net("VPLUS"), Net("VMINUS"), Net("GND")
    GND.drive = POWER
    VCC_RLY = Net("VRELAY")

    # Shared relays. G6K-2F-Y is 2 Form C, so ONE relay covers both channels.
    K_GAIN = Part("Relay", "G6K-2", value="G6K-2F-Y GAIN",
                  footprint=FP_RELAY, ref="K1")
    K_GAIN[K_COIL_A] += VCC_RLY
    K_GAIN[K_COIL_B] += Net("GAIN_CMD")

    # ADR-026: the second gain relay, for the R_g10 leg. It is K5 and not K2
    # so that the three mute relays keep their references (limitations #22).
    # Coil commands, from the 3-position gain selector:
    #     0 dB    GAIN_CMD off   GAIN10_CMD off   (the de-energised state)
    #     +3 dB   GAIN_CMD on    GAIN10_CMD off
    #     +10 dB  GAIN_CMD on    GAIN10_CMD on
    # Coil budget for psu-engineer (vendor/relays/omron/G6K/en-g6k.pdf,
    # ratings table, +/-10 %): 21.1 mA at 5 V, 9.1 mA at 12 V, 4.6 mA at 24 V
    # per coil. Worst case is +10 dB out of mute, five coils energised:
    # 105.5 / 45.5 / 23.0 mA. The VRELAY voltage is not decided yet.
    K_GAIN10 = Part("Relay", "G6K-2", value="G6K-2F-Y GAIN10",
                    footprint=FP_RELAY, ref="K5")
    K_GAIN10[K_COIL_A] += VCC_RLY
    K_GAIN10[K_COIL_B] += Net("GAIN10_CMD")

    # Three mute relays: 6 output lines (3 outputs x 2 channels), 2 poles each.
    # ADR-012 puts mute on ALL outputs, and the reason is the headphone
    # branch: the turn-on transient goes straight into a pair of
    # electrostatics, not into a loudspeaker two metres away.
    # SHUNT to ground, not in series: a series contact would sit in the
    # signal path permanently, which is exactly what ADR-004 argued against.
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

    chans = {}
    for ch, base, pole in (("L", 100, 0), ("R", 300, 1)):
        chans[ch] = channel(ch, base, VP, VM, GND, K_GAIN, K_GAIN10,
                            mute_lists, pole)

    # Wire the mute contacts. mute_lists[i] holds, per output pair,
    # [jack_node_L, connector_pin_L, jack_node_R, connector_pin_R].
    # The NORMALLY CLOSED throw shorts the jack to ground when the coil is
    # de-energised, i.e. whenever the supply is down or the timer has not
    # released yet. Failing safe = failing silent.
    # The mute may be held INDEFINITELY (ADR-021, superseding ADR-012's "a few
    # seconds"): it is the trim's permissive (ADR-019). With all three jacks
    # grounded the output stages run in class B - since L17 (ADR-023) that is
    # the two fixed buffers and block B, each on its own 47 ohm; block A only
    # drives the buffers and the attenuator - and ADR-021 asks only that every
    # part stay inside its thermal and SOA limits. L11 measured that on the
    # topology without buffers; L17 re-measured it on this one. This shunt mute is NOT a short-circuit protection: during an
    # external short it adds a second ground instead of removing the first.
    for i, k in enumerate(K_MUTE):
        lst = mute_lists[i]
        for pole_i, (com, nc) in enumerate(((K_COM1, K_NC1), (K_COM2, K_NC2))):
            node = lst[pole_i * 2]
            pin = lst[pole_i * 2 + 1]
            node += pin           # signal passes straight through
            k[com] += node
            k[nc] += GND          # ...and the NC contact shorts it when muted

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

    netpath = os.path.join(REPO, "circuits", "preamp", "preamp_audio.net")
    generate_netlist(file_=netpath, tool="kicad10")
    print("KiCad netlist ->", netpath)
