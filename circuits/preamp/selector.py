#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
selector.py - the input selector: four relays, one per input, and the knob
that feeds their coils.

Fase 2 DRAFT, L48a. Source of truth for the topology (AGENTS.md rule 2). Not
run on its own: preamp_audio.py calls it while it builds the audio board.
The signal side (per input: the connector, the coupling capacitor, its
resistors to ground, and one pole of the input's relay per channel) stays in
preamp_audio.channel(); this file owns the coils.

WHAT THIS IS (ADR-064, the user's choices of 2026-10-06)
--------------------------------------------------------
 - F1: 4 unbalanced inputs, switched by RELAYS driven directly by a rotary
   switch (ADR-009: only DC for the coils reaches the panel). No firmware:
   with a capacitor on every input (NC-040) the change needs no mute.
 - "Monostabili dalla manopola": one G6K-2F-Y per input, pole 1 = left,
   pole 2 = right. The knob feeds exactly one coil from VRELAY; the coil
   returns on RLY_RET, as the gain coils do (gain_interlock.py).
 - De-energised = NO input connected (the NO throws carry the signal). With
   VRELAY down - standby (NC-037), a fault - block A's input sits on its
   R_IN = 1 MOhm to ground.

THE KNOB. SW4 is Switch:SW_Rotary_3x4: commons 13 / 14 / 15, throws 1-4,
5-8, 9-12, the k-th throw of each pole being position k (pin geometry read
from the KiCad symbol in L48a: 13 sits by 1-4, 14 by 5-8, 15 by 9-12).
Only pole a is used: COM on VRELAY, throw k -> SEL<k>_HI. Poles b and c are
free (ERC warns, like SW1 / SW2's free throws). Like SW1 and SW2 it is a
panel part, wired by its 16-way harness header.

THE COIL BUDGET. +9.1 mA at 12 V (en-g6k.pdf ratings table), one coil in
every position, in and out of mute: the VRELAY worst case of
preamp_audio.py goes from 72.8 to 81.9 mA of coils.

WHAT IS DELIBERATELY NOT HERE
-----------------------------
 - Input LEDs: the knob's position is the indication (F9 asks LEDs of the
   trim only; ADR-041 added the gain's because the gain moves only in mute).
 - Any mute on a change of input (ADR-064: not needed for the DC, and the
   jump between two programmes is accepted by F1).
"""
from skidl import Part, Net

FP_RELAY = "Relay_SMD:Relay_DPDT_Omron_G6K-2F-Y"
FP_D = "Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal"
FP_SW = "Connector_PinHeader_2.54mm:PinHeader_2x08_P2.54mm_Vertical"

N_INPUTS = 4

# SW4 (Switch:SW_Rotary_3x4), pole a: COM pin and its four throws, position
# 1..4. scripts/check_relay_safe_state.py keeps the same grouping as DATA
# (KNOWN_SWITCHES) and walks the netlist position by position (SEL_KNOB).
SW_COM = "13"
SW_THROWS = ("1", "2", "3", "4")

# Refs: K13-K16 and D16-D19 follow the gain's K11 / K12 and D10-D15; SW4
# follows SW1 (trim), SW2 (gain) and SW3 (the mute switch, preamp_audio.py)
# - SKiDL renamed a second SW3 to SW3_1 in silence, L48a. Explicit, so
# that nothing renumbers (limitations #22).
K_REFS = tuple(f"K{13 + i}" for i in range(N_INPUTS))
D_REFS = tuple(f"D{16 + i}" for i in range(N_INPUTS))


def selector_relays(vrelay, ret, g6k_pins):
    """Make K13-K16, their freewheel diodes and SW4. Returns the 4 relays,
    input 1 first; preamp_audio.channel() wires one pole of each.

    vrelay   - VRELAY, the knob's common.
    ret      - RLY_RET, the coils' return (trim.trim_relays()["RET"]).
    g6k_pins - (coil_a, coil_b, com1, no1, nc1, com2, no2, nc2) of the
               G6K-2F-Y, the ONE copy in preamp_audio.py (NC-014).
    """
    coil_a, coil_b = g6k_pins[0], g6k_pins[1]
    sw = Part("Switch", "SW_Rotary_3x4", value="INPUT 1/2/3/4",
              footprint=FP_SW, ref="SW4")
    sw[SW_COM] += vrelay
    relays = []
    for i in range(N_INPUTS):
        hi = Net(f"SEL{i + 1}_HI")
        sw[SW_THROWS[i]] += hi
        # ADR-064 value string: the checker reads the role (SEL) and the
        # input number from it.
        k = Part("Relay", "G6K-2", value=f"G6K-2F-Y SEL{i + 1}",
                 footprint=FP_RELAY, ref=K_REFS[i])
        k[coil_a] += hi             # pin 1 +, en-g6k.pdf p. 6
        k[coil_b] += ret
        # Freewheel across the coil: the knob breaks it.
        d = Part("Device", "D", value="1N4148", footprint=FP_D, ref=D_REFS[i])
        d[1] += hi                  # K
        d[2] += ret                 # A
        relays.append(k)
    return relays
