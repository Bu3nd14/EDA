#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gain_interlock.py - the gain relays K1 / K5, their self-holding auxiliaries,
the gain selector and the three LEDs of the TRUE gain state.

Fase 2 DRAFT, L36. Source of truth for the topology (AGENTS.md rule 2). Not
run on its own: preamp_audio.py calls it while it builds the audio board.
The signal side of K1 / K5 (one pole per channel on R_g3 / R_g10, ADR-026)
stays in preamp_audio.channel(); this file owns the coils.

WHAT THIS IS (ADR-041, realised as road B of ADR-030)
-----------------------------------------------------
The user, 2026-09-22: "interlock al mute, come TRIM, nessuna invenzione,
avremo LED anche per il guadagno".
 - The gain changes ONLY with the mute inserted, like the trim (F8, ADR-027).
   Out of mute the knob moves nothing. No automatic mute.
 - K1 and K5 stay MONOSTABLE (ADR-030 road B: a coil fault can only LOWER the
   gain, F5). Each has an AUXILIARY monostable with its coil in parallel,
   K11 (HOLD3, on K1) and K12 (HOLD10, on K5).
 - One pole of each auxiliary is the SELF-HOLD, the other lights the LEDs
   (ADR-030 point 2: "letti dai poli liberi degli ausiliari").

THE COILS, HIGH-SIDE SWITCHED like the trim's: K1 + K11 between G3_HI and
RLY_RET, K5 + K12 between G10_HI and RLY_RET. Coil polarity from the
datasheet (en-g6k.pdf, p. 6 of the PDF, G6K-2F-Y, TOP VIEW): pin 1 +,
pin 8 -, re-read in L36.

WHAT FEEDS G3_HI (G10_HI is the same with "+10 only"):
  a) COMMAND  VTRIM -> SW2 pole a (+3, +10) -> C3 -> Schottky D10 -> G3_HI.
              VTRIM is the trim's own permissive rail: VRELAY through the two
              NC of K6 in series, live only in mute (trim.py). The diode stops
              G3_HI, held at VRELAY out of mute, from back-feeding VTRIM - that
              would make the TRIM commandable out of mute (F8).
  b) BRIDGE   VRELAY -> SW2 pole b (+3, +10) -> H3 -> K11 NO -> G3_HI.
  c) HOLD     VHOLD -> D12 -> H3 -> K11 NO -> G3_HI. VHOLD is K6's pole-1 NO
              (COM on VRELAY): VRELAY OUT of mute, open in mute.
So: in mute (a) picks the coil up and (a)+(b) keep it while the knob says
so; turning the knob down drops it, since VHOLD is dead. Out of mute a coil
that is OFF has no source - (a) is dead, (b) and (c) pass through its own
open auxiliary contact - and a coil that is ON is held by (c) whatever the
knob says. The knob moves nothing (F8 as ADR-041 extends it to F5).

THE RACE (ADR-030: "quando K6 commuta, per un istante ne' il comando ne' la
tenuta alimentano le bobine"). With only (a) and (c), K6's transfer - NC
open, NO not yet closed - leaves the coil unfed, and whether K1 drops then
depends on the coil inductance, the drop-out current and the transfer time.
The G6K datasheet gives NONE of the three ("operate 3 ms max, release 3 ms
max", nothing else; en-g6k.pdf p. 3), so no timing argument can close it.
(b) closes it by STRUCTURE: when the knob agrees with the state - which it
does at every mute release and every insertion after a change made in mute
- the coil is fed through a path with no K6 contact in it, for any L and
any transfer. Proved on the netlist by scripts/check_relay_safe_state.py
(the "transfer" state) and simulated in docs/preamp/data/2026-09-25/L36/.
No charge-storing part, no extra permissive: neither "Da riaprire se" of
ADR-030 applies.

THE RESIDUE, declared (L36 report, NC-028). If the knob is turned OUT of
mute and the mute is then inserted, the gain goes to the knob when VHOLD
dies (K6's NO opens), one K1 release time later. K6 moves with K2-K4 - same
coil net, same part - so the change follows the jacks' disconnection by
that release time, exactly as the trim follows it by its set time. It is
ordered, not closed by the datasheet.

WHAT IS DELIBERATELY NOT HERE
-----------------------------
 - The panel: SW2 is a panel part and appears as its 16-way harness header,
   like SW1; the LEDs sit on the board like the trim's until L35 moves them.
 - The VRELAY supply (psu-engineer). The pick-up passes through the
   Schottky: VRELAY - V_F(42 mA) must stay >= 80 % of the rated 5 V (must
   operate, en-g6k.pdf p. 3) at -5 % and warm. A 1N4148 does not fit.
"""
from skidl import Part, Net

from gain_block import FP_R

FP_RELAY = "Relay_SMD:Relay_DPDT_Omron_G6K-2F-Y"
FP_D = "Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal"
FP_SCHOTTKY = "Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal"
FP_LED = "LED_THT:LED_D3.0mm"
FP_SW = "Connector_PinHeader_2.54mm:PinHeader_2x08_P2.54mm_Vertical"

# LED current limiter from VRELAY, as the trim's (trim.R_LED): ~2 mA in a red
# LED at VRELAY = 5 V. VRELAY is not decided yet: re-size with it.
R_LED = "1.5k"

# SW2 (Switch:SW_Rotary_4x3): commons 13 / 14 / 15 / 16, throws 1-2-3, 4-5-6,
# 7-8-9, 10-11-12, the k-th throw of each pole being position k.
# Position 1 = 0 dB, 2 = +3 dB, 3 = +10 dB (ADR-026 table). What each pole's
# COM is tied to, and which throws are live (None = not connected):
#   a  K1 command  COM VTRIM   -> C3   at +3, +10
#   b  K1 bridge   COM VRELAY  -> H3   at +3, +10
#   c  K5 command  COM VTRIM   -> C10  at +10 only   (ADR-026: never K5
#   d  K5 bridge   COM VRELAY  -> H10  at +10 only    without K1)
# scripts/check_relay_safe_state.py keeps the same table as DATA and walks
# the netlist position by position; the two must agree.
SW_POLES = (("13", ("1", "2", "3")), ("14", ("4", "5", "6")),
            ("15", ("7", "8", "9")), ("16", ("10", "11", "12")))
SW_TABLE = (("VTRIM", (None, "C3", "C3")),
            ("VRELAY", (None, "H3", "H3")),
            ("VTRIM", (None, None, "C10")),
            ("VRELAY", (None, None, "H10")))


def gain_relays(vrelay, trim_parts, g6k_pins):
    """Make K1, K5, their auxiliaries, SW2 and the LEDs. Returns (K1, K5).

    trim_parts - what trim.trim_relays() returns: K6, VTRIM and RLY_RET are
                 shared with the trim (ADR-041, "come TRIM").
    g6k_pins   - (coil_a, coil_b, com1, no1, nc1, com2, no2, nc2) of the
                 G6K-2F-Y, the ONE copy in preamp_audio.py (NC-014).
    """
    coil_a, coil_b, com1, no1, _nc1, com2, no2, nc2 = g6k_pins
    vtrim, ret, k6 = trim_parts["VTRIM"], trim_parts["RET"], trim_parts["K6"]

    # VHOLD: K6 pole 1 is VRELAY -> NC -> PERMIT_MID (trim.py); its NO, free
    # until L36, gives VRELAY exactly while the mute is released.
    vhold = Net("VHOLD")
    k6[no1] += vhold

    nets = {"VTRIM": vtrim, "VRELAY": vrelay}
    out = {}
    aux = {}
    # (step, main ref, aux ref, command diode, hold diode, freewheel)
    for step, kref, aref, dcmd, dhold, dfw in (("3", "K1", "K11", "D10",
                                                "D12", "D14"),
                                               ("10", "K5", "K12", "D11",
                                                "D13", "D15")):
        hi, c, h = Net(f"G{step}_HI"), Net(f"C{step}"), Net(f"H{step}")
        nets[f"C{step}"], nets[f"H{step}"] = c, h
        # ADR-026 value strings: the checker reads the role from them.
        main = Part("Relay", "G6K-2",
                    value="G6K-2F-Y GAIN" if step == "3" else
                    "G6K-2F-Y GAIN10", footprint=FP_RELAY, ref=kref)
        # ADR-030 road B: the auxiliary, coil in parallel with the main one.
        ka = Part("Relay", "G6K-2", value=f"G6K-2F-Y HOLD{step}",
                  footprint=FP_RELAY, ref=aref)
        for k in (main, ka):
            k[coil_a] += hi         # pin 1 +, en-g6k.pdf p. 6
            k[coil_b] += ret
        # (a) the command, through the trim's permissive. Schottky, because
        # the pick-up must see >= 80 % of 5 V after it (see the docstring).
        d = Part("Device", "D_Schottky", value="Schottky 1A",
                 footprint=FP_SCHOTTKY, ref=dcmd)
        d[1] += hi                  # K
        d[2] += c                   # A
        # (c) the hold from VHOLD. Its diode keeps H3 and H10 apart: without
        # it, in mute, H3 (fed by the bridge at +3) would reach H10 through
        # the floating VHOLD and keep K5 held at +3.
        d = Part("Device", "D", value="1N4148", footprint=FP_D, ref=dhold)
        d[1] += h                   # K
        d[2] += vhold               # A
        # The self-hold pole, pole 1 of the auxiliary: H -> NO -> coil.
        # Its NC stays unconnected (an ERC warning, like K6's pole-2 NO).
        ka[com1] += h
        ka[no1] += hi
        # Freewheel across the coil pair: the knob and the hold contact break
        # it. It lengthens the release, which only helps the residue above.
        d = Part("Device", "D", value="1N4148", footprint=FP_D, ref=dfw)
        d[1] += hi                  # K
        d[2] += ret                 # A
        out[step] = main
        aux[step] = ka

    # ---- SW2, the gain selector (F10: rotary, 3 positions) -----------------
    sw = Part("Switch", "SW_Rotary_4x3", value="GAIN 0/+3/+10 dB",
              footprint=FP_SW, ref="SW2")
    for (com, throws), (src, dests) in zip(SW_POLES, SW_TABLE):
        sw[com] += nets[src]
        for throw, dest in zip(throws, dests):
            if dest is not None:    # None: left unconnected, ERC warns
                sw[throw] += nets[dest]

    # ---- the LEDs of the true gain state, pole 2 of the auxiliaries --------
    # VRELAY -R2- HOLD3 COM: rest -> LED 0 dB; energised -> HOLD10 COM:
    # rest -> LED +3 dB, energised -> LED +10 dB. One LED at a time, one
    # resistor, the trim's pattern (F9, ADR-027).
    feed = Net("GLED_FEED")
    rl = Part("Device", "R", value=R_LED, footprint=FP_R, ref="R2")
    rl[1] += vrelay
    rl[2] += feed
    a3, a10 = aux["3"], aux["10"]
    a3[com2] += feed
    mid = Net("GLED_MID")
    a3[no2] += mid
    a10[com2] += mid
    for ref, label, (relay, pin) in (("D7", "LED 0dB", (a3, nc2)),
                                     ("D8", "LED +3dB", (a10, nc2)),
                                     ("D9", "LED +10dB", (a10, no2))):
        led = Part("Device", "LED", value=label, footprint=FP_LED, ref=ref)
        anode = Net(f"{ref}_A")
        led[2] += anode             # A
        led[1] += ret               # K
        relay[pin] += anode
    return out["3"], out["10"]
