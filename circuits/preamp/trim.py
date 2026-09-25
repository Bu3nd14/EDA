#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
trim.py - the common level trim of the VARIABLE output, its bistable relays,
its LED indication and its electrical interlock with the mute.

Fase 2 DRAFT, L16. Source of truth for the topology (AGENTS.md rule 2). It is
not run on its own: preamp_audio.py calls it while it builds the audio board.

WHAT THIS IS (ADR-027; REQUIREMENTS F2, F8, F9)
----------------------------------------------
 - ONE trim for all inputs, 0 / -6 / -12 dB, per channel on the branch that
   goes from block A to the stepped attenuator. The two fixed-output buffers
   hang on block A's output BEFORE it: the fixed outputs stay a faithful copy
   of the source (the user's decision of 2026-09-14).
 - Two BISTABLE relays carry the signal (Omron G6KU-2F-Y, single winding):
       T1 = K7   reset -> attenuator top on block A OUT (0 dB)
                 set   -> attenuator top on T2's COM
       T2 = K8   reset -> TAP6 (-6 dB), set -> TAP12 (-12 dB)
   one pole per channel, as ADR-026 did for the gain relays: a coil fault
   moves both channels together (T3). Reset is 0 dB, the state the relay
   leaves the factory in.
 - Two more G6KU-2F-Y, the SPIA relays K9 / K10, have their coils IN PARALLEL
   with K7 / K8 and their contacts light one LED of three. The LEDs read the
   relays, never the command: out of mute the command may not match the state
   (F8), and F9 asks for the state.
 - The command is a 4-pole 3-position rotary switch (SW1, off-board on the
   panel). Each PAIR of poles is an H bridge of contacts across one coil pair,
   each side thrown to VTRIM or to RLY_RET. While VTRIM is live the coils are
   driven continuously towards the knob's position, in the right polarity.
 - THE INTERLOCK (F8, ADR-019 para. 2, NC-023). VTRIM comes from VRELAY through
   the two NORMALLY CLOSED contacts of K6 in series. K6 is a monostable
   G6K-2F-Y whose coil sits on MUTE_CMD with the three mute relays: energised
   = out of mute = VTRIM dead = the knob moves nothing; de-energised = muted
   (or power down, or the mute timer not yet released) = VTRIM live. The two
   NC in series: one welded contact alone does not defeat the interlock.
   Out of mute the bistables keep their state with no current: the value set
   stays applied when the mute is released.
 - POWER-ON STATE: the preamp powers up muted (ADR-012), so the coils are
   driven to the knob's position BEFORE the mute releases. What the trim
   comes up in is the knob's position, not "whatever it was last".

WHAT IS DELIBERATELY NOT HERE
-----------------------------
 - The input selector (still off-board, upstream of block A).
 - The mute timer and the VRELAY supply (psu-engineer). A constraint for
   them, from the datasheet: the mute must release no earlier than 10 ms
   (minimum set/reset signal width) + 3 ms (set time) after VRELAY is valid.

THE PIN MAP, READ FROM THE DATASHEET - not inherited from the G6K-2F-Y:
vendor/relays/omron/G6K/en-g6k.pdf (K106-E1-11) page 7 and
vendor/relays/omron/G6K-K106-E1-16/K106-E1.pdf (K106-E1-16) page 7, row
G6KU-2F-Y, "Terminal Arrangement / Internal Connections (TOP VIEW)", read in
L16 on three legs that agree (raster, SVG vector coordinates - the armature
passes 0.44 pt from the contact on its left and 3.39 pt from the one on its
right on BOTH poles, in both revisions - and the polylines of the KiCad symbol
Relay:G6KU-2). The drawing is the RESET state:
    coil     1, 8        SET  = pin 1 +, pin 8 -;  RESET = pin 8 +, pin 1 -
    pole 1   COM 3   closed at reset 2   closed at set 4   (row 1-2-3-4)
    pole 2   COM 6   closed at reset 7   closed at set 5   (row 8-7-6-5)
It has the same shape as the G6K-2F-Y's - including the NC-014 trap (the two
rows are numbered in opposite directions) - and it is asserted on the
generated netlist by scripts/check_relay_safe_state.py.
"""
from skidl import Part, Net

from gain_block import FP_R

FP_RELAY = "Relay_SMD:Relay_DPDT_Omron_G6K-2F-Y"   # same land pattern: the
# datasheet gives the G6KU-2F-Y the same mounting dimensions as the G6K-2F-Y,
# and KiCad's own symbol filter for G6KU-2 matches this footprint.
FP_TVS = "Diode_SMD:D_SMA"
FP_D = "Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal"
FP_LED = "LED_THT:LED_D3.0mm"
FP_SW = "Connector_PinHeader_2.54mm:PinHeader_2x08_P2.54mm_Vertical"  # the
# rotary switch is a PANEL part: on the board it is the 16-way harness header.
FP_CONN1 = "Connector_PinHeader_2.54mm:PinHeader_1x01_P2.54mm_Vertical"

# G6KU-2F-Y, see the docstring.
KU_SET_PLUS, KU_SET_MINUS = "1", "8"
KU_COM1, KU_RESET1, KU_SET1 = "3", "2", "4"
KU_COM2, KU_RESET2, KU_SET2 = "6", "7", "5"

# The ladder, per channel: OUT -R1- TAP6 -R2- TAP12 -R3- GND, loaded at the
# selected tap by the 10 k stepped attenuator (F4).
# ADR-027, from docs/preamp/data/2026-09-14/L16/esplorazione/script/
# trim_ramo_e96.py and SIMULATED in spice/preamp/tb/tb_trim.cir: -6.003 dB and
# -11.939 dB with the attenuator load. Low impedance on purpose - E3 does not
# see it (block A is in front), and the Thevenin it adds to block B's source
# (at most 442 ohm, -> 2.611 k instead of 2.5 k at mid-travel) cost V1 0.026
# deg (tb_loop.cir, L16). The heaviest load on block A is 1.51 k at 0 dB:
# 3.82 V peak of E6 draws 2.5 mA from a ~20 mA class A stage (ADR-042).
R1_TRIM, R2_TRIM, R3_TRIM = "845", "464", "464"

# LED current limiter from VRELAY, sized for VRELAY = 5 V (~2 mA in a red LED).
# VRELAY is not decided yet (psu-engineer, ADR-026): re-size with it.
R_LED = "1.5k"

# SW1 (Switch:SW_Rotary_4x3): commons 13 / 14 / 15 / 16, throws 1-2-3, 4-5-6,
# 7-8-9, 10-11-12, the k-th throw of each pole being position k.
SW_POLES = (("13", ("1", "2", "3")), ("14", ("4", "5", "6")),
            ("15", ("7", "8", "9")), ("16", ("10", "11", "12")))
# Position 1 = 0 dB, 2 = -6 dB, 3 = -12 dB. What each pole connects, in order
# T1 pin 1, T1 pin 8, T2 pin 1, T2 pin 8 (SET = pin 1 +):
#            0 dB: T1 reset, T2 reset
#           -6 dB: T1 set,   T2 reset
#          -12 dB: T1 set,   T2 set
SW_TABLE = {
    "T1_1": ("RET", "VTRIM", "VTRIM"),
    "T1_8": ("VTRIM", "RET", "RET"),
    "T2_1": ("RET", "RET", "VTRIM"),
    "T2_8": ("VTRIM", "VTRIM", "RET"),
}


def trim_relays(vrelay, mute_cmd, g6k_pins):
    """The parts both channels share. Returns {"T1": K7, "T2": K8}, plus
    "K6", "VTRIM" and "RET": since L36 the gain interlock (gain_interlock.py,
    ADR-041 "come TRIM") shares the permissive and its rails. It takes
    VHOLD from K6's pole-1 NO, free until then; nothing here changes.

    g6k_pins = (coil_a, coil_b, com1, no1, nc1, com2, no2, nc2) of the
    G6K-2F-Y as preamp_audio.py holds them: ONE pin map for the monostables,
    not a second copy that could drift from the first (NC-014).
    """
    coil_a, coil_b, com1, _no1, nc1, com2, _no2, nc2 = g6k_pins
    vtrim, ret = Net("VTRIM"), Net("RLY_RET")
    rails = {"VTRIM": vtrim, "RET": ret}

    # ---- K6: the permissive (F8). Coil on the MUTE command, two NC in series.
    k6 = Part("Relay", "G6K-2", value="G6K-2F-Y PERMIT",
              footprint=FP_RELAY, ref="K6")
    k6[coil_a] += vrelay
    k6[coil_b] += mute_cmd
    mid = Net("PERMIT_MID")
    k6[com1] += vrelay
    k6[nc1] += mid
    k6[com2] += mid
    k6[nc2] += vtrim

    # Freewheel: at mute release K6 opens with up to four coils conducting;
    # their current always flows OUT of VTRIM, so one diode from RLY_RET
    # catches it and VTRIM cannot swing below the return.
    dfw = Part("Device", "D", value="1N4148", footprint=FP_D, ref="D3")
    dfw[1] += vtrim          # K
    dfw[2] += ret            # A

    # ---- T1/T2 and their SPIA twins, coils in parallel ----------------------
    relays = {}
    coils = {}
    spia = []
    for i in (1, 2):
        c1, c8 = Net(f"TRIM{i}_C1"), Net(f"TRIM{i}_C8")
        kt = Part("Relay", "G6KU-2", value=f"G6KU-2F-Y TRIM{i}",
                  footprint=FP_RELAY, ref=f"K{6 + i}")
        ks = Part("Relay", "G6KU-2", value=f"G6KU-2F-Y SPIA{i}",
                  footprint=FP_RELAY, ref=f"K{8 + i}")
        for k in (kt, ks):
            k[KU_SET_PLUS] += c1
            k[KU_SET_MINUS] += c8
        # Bidirectional clamp across the coil pair: the rotary switch breaks
        # before it makes, and the coil current has nowhere else to go.
        tvs = Part("Device", "D_TVS", value="TVS bidir", footprint=FP_TVS,
                   ref=f"D{i}")
        tvs[1] += c1
        tvs[2] += c8
        relays[f"T{i}"] = kt
        coils[f"T{i}_1"], coils[f"T{i}_8"] = c1, c8
        spia.append(ks)

    # ---- SW1: the command ---------------------------------------------------
    sw = Part("Switch", "SW_Rotary_4x3", value="TRIM 0/-6/-12 dB",
              footprint=FP_SW, ref="SW1")
    for (com, throws), coil in zip(SW_POLES, ("T1_1", "T1_8", "T2_1", "T2_8")):
        sw[com] += coils[coil]
        for throw, rail in zip(throws, SW_TABLE[coil]):
            sw[throw] += rails[rail]

    # ---- F9: the LEDs, lit by the SPIA contacts ------------------------------
    # VRELAY -R- SPIA1 COM: reset -> LED 0 dB; set -> SPIA2 COM: reset ->
    # LED -6 dB, set -> LED -12 dB. One LED at a time, one resistor.
    feed = Net("LED_FEED")
    rl = Part("Device", "R", value=R_LED, footprint=FP_R, ref="R1")
    rl[1] += vrelay
    rl[2] += feed
    s1, s2 = spia
    s1[KU_COM1] += feed
    s_mid = Net("SPIA_MID")
    s1[KU_SET1] += s_mid
    s2[KU_COM1] += s_mid
    for ref, label, anode_pin in (("D4", "LED 0dB", (s1, KU_RESET1)),
                                  ("D5", "LED -6dB", (s2, KU_RESET1)),
                                  ("D6", "LED -12dB", (s2, KU_SET1))):
        led = Part("Device", "LED", value=label, footprint=FP_LED, ref=ref)
        anode = Net(f"{ref}_A")
        led[2] += anode      # A
        led[1] += ret        # K
        relay, pin = anode_pin
        relay[pin] += anode

    # The coil and LED return leaves the board on its own pin, not on the
    # audio GND (P4, star ground).
    jr = Part("Connector_Generic", "Conn_01x01", value="RLY_RET",
              footprint=FP_CONN1, ref="J2")
    jr[1] += ret
    relays.update(K6=k6, VTRIM=vtrim, RET=ret)
    return relays


def trim_channel(ch, a_out, att_top, gnd, t1, t2, pole):
    """The ladder and the two signal contacts of one channel.

    a_out   - block A's output net (the fixed-output buffers are on it too)
    att_top - the net of the attenuator harness' top pin
    pole    - 0 = pole 1 of each relay (channel L), 1 = pole 2 (channel R)
    """
    com, reset, set_ = ((KU_COM1, KU_RESET1, KU_SET1) if pole == 0
                        else (KU_COM2, KU_RESET2, KU_SET2))
    base = 900 if ch == "L" else 910
    tap6, tap12, t2c = Net(f"{ch}_TAP6"), Net(f"{ch}_TAP12"), Net(f"{ch}_T2C")
    for n, (val, a, b) in enumerate(((R1_TRIM, a_out, tap6),
                                     (R2_TRIM, tap6, tap12),
                                     (R3_TRIM, tap12, gnd)), start=1):
        r = Part("Device", "R", value=val, footprint=FP_R, ref=f"R{base + n}")
        r[1] += a
        r[2] += b
    t1[com] += att_top
    t1[reset] += a_out       # 0 dB, the reset state
    t1[set_] += t2c
    t2[com] += t2c
    t2[reset] += tap6        # -6 dB
    t2[set_] += tap12        # -12 dB
