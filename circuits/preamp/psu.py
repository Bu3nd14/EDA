#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
psu.py - the supply board: the second PCB of P4 (ADR-010, ADR-048; L41a, L41b1).

Source of truth for the supply's topology (AGENTS.md rule 2), as
preamp_audio.py is for the audio board. It realises P9 (ADR-046, as ADR-048
reads it) and the contracts written on the audio board next to J1, J3 and J4.

    rear IEC module (fuse + DOUBLE-POLE switch: off = mains off everything)
      |
      +-- F501 -- T2 (small toroid, ALWAYS on while the rear is on) -- D503 --+-- D504 -- C_V --[U503 12 V]-- VRELAY_REG -+-[U504 5 V]-- V5 (logic, micro)
      |                                                                      |                                     +-[Q505]-- VRELAY (J1 pin 4, the audio board)
      |                                                                      +-- mains detector (Q504, U506 ch 1)
      +-- K501 (DPST, coil on VRELAY_REG) -- T1 (toroid 2x15 V 50 VA) -- D501 -+-- C501 --[U501 TPS7A4701]-- C505 -- VPLUS
                                                                              +-- C502 --[U502 TPS7A3301]-- C506 -- VMINUS
    supervisor U505: VPLUS < 13.5 V, |VMINUS| < 13.5 V   \
    mains detector U506 A: no half-wave for ~15 ms        -> pull MUTE_G low: Q501 off, MUTE_CMD released (mute)
    VRELAY supervisor U506 B: VRELAY_REG < 11.0 V         /

    the timer (L41b1, ADR-049): micro U509 -> MUTE_REQ, PERMIT_REQ, VRELAY_EN, MAINS_REQ
      MUTE_REQ --R513-- MUTE_G (<= PERMIT_G by D522)                         -> Q501 -> MUTE_CMD
      MUTE_REQ, PERMIT_REQ --diodes--> PERMIT_T (RC, D) -> U508 A vs VREF -> PERMIT_G -> Q502 -> PERMIT_CMD
      PERMIT_T, VRELAY_EN  --diodes--> VR_T (RC, D + D2) -> U508 B vs VREF -> VR_G -> Q506 -> Q505 (VRELAY on)
      DAC U510 -> two exponential converters (U511, Q507-Q512) -> J3, the LDR strings

WHAT L41a PUTS HERE (ADR-048)
-----------------------------
 - The mains side: the IEC module's output (J510), the always-on small
   transformer's fuse F501, the DPST mains relay K501 on the big toroid only
   (de-energised = toroid off; ADR-048 supersedes ADR-046 on that sentence).
 - The rails: bridge, reservoirs, TPS7A4701 / TPS7A3301 low-noise linear
   regulators (ADR-020's remedy: no switching anywhere, ADR-048), and the
   hold-up AFTER them, 2200 uF nominal per rail (P9 (b): >= 1500 uF effective).
 - VRELAY = 12 V from the small transformer's own winding, through its own
   reservoir behind a diode: the relay currents never touch the audio rails'
   reservoirs (the user's PSRR argument, ADR-048 point 3).
 - The supervisor: a dual comparator with a precision reference, and the
   mains detector on the small transformer's secondary. Their open-collector
   outputs pull the gate of the MUTE_CMD sink low IN HARDWARE, without the
   firmware (ADR-048 point 5).
 - The two low-side sinks of J4 (MUTE_CMD, PERMIT_CMD) and the mains relay's.

WHAT L41b1 PUTS HERE (ADR-048 point 6, ADR-049) - in place of J509 TIMER_IO
----------------------------------------------------------------------------
 - The microcontroller U509 (ATtiny3216) and its written specification,
   firmware/preamp_timer/spec/timer_spec.md: the sequence is the firmware's
   (L41b2), the ORDER is this hardware's.
 - The hardware delay D: PERMIT_CMD is released no earlier than D after the
   mute request falls, and energised no later than MUTE_CMD, whatever the
   micro does - reset (outputs tri-stated, DS40002205A sec. 16.3.1), stuck
   high, stuck low, or a firmware that drops PERMIT_REQ first.
 - VRELAY off the audio board in standby (NC-037): the high-side switch Q505
   between VRELAY_REG (U503's output) and VRELAY (J1 pin 4). The switch too
   is held in hardware, D2 after PERMIT_G, so a micro that resets while the
   music plays cannot drop every coil at once (L30's "no D" case, ~90 dB SPL).
 - The LDR drive (profile v4, ADR-039): the dual DAC U510 and two exponential
   converters, one per string, sourcing into the anodes of J3.

WHAT IS DELIBERATELY NOT HERE
-----------------------------
 - The firmware (L41b2): firmware/preamp_timer/, tested on the host.
 - The transformers themselves, the IEC module, the front power switch: they
   are chassis / panel parts, here as their harness headers (like SW1-SW3 on
   the audio board).

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

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

FP_R = "Resistor_SMD:R_0805_2012Metric"
FP_C = "Capacitor_SMD:C_0805_2012Metric"
FP_SOT23 = "Package_TO_SOT_SMD:SOT-23"
FP_SOIC8 = "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm"
FP_QFN = ("Package_DFN_QFN:Texas_RGW0020A_VQFN-20-1EP_5x5mm_P0.65mm_"
          "EP3.15x3.15mm_ThermalVias")
FP_BRIDGE = "Diode_THT:Diode_Bridge_Vishay_KBL"
FP_DO41 = "Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal"
FP_DO35 = "Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal"
FP_CP16 = "Capacitor_THT:CP_Radial_D16.0mm_P7.50mm"
FP_CP12 = "Capacitor_THT:CP_Radial_D12.5mm_P5.00mm"
FP_FUSE = "Fuse:Fuseholder_Cylinder-5x20mm_Schurter_0031_8201_Horizontal_Open"
FP_TB2 = ("TerminalBlock_Phoenix:"
          "TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal")
FP_TB3 = ("TerminalBlock_Phoenix:"
          "TerminalBlock_Phoenix_MKDS-1,5-3-5.08_1x03_P5.08mm_Horizontal")
FP_HDR = "Connector_PinHeader_2.54mm:PinHeader_1x{n:02d}_P2.54mm_Vertical"
FP_C1206 = "Capacitor_SMD:C_1206_3216Metric"      # C0G 100 nF (C_T, C_T2)
FP_SOT363 = "Package_TO_SOT_SMD:SOT-363_SC-70-6"
FP_SOD323 = "Diode_SMD:D_SOD-323"
FP_SOIC14 = "Package_SO:SOIC-14_3.9x8.7mm_P1.27mm"
FP_SOIC20W = "Package_SO:SOIC-20W_7.5x12.8mm_P1.27mm"

# ---- the numbers, each with the decision behind it ----------------------
# ADR-046 / P9 (b): >= 1500 uF EFFECTIVE after each regulator; 2200 uF
# nominal at -20 % is 1760 uF. At 265 mA the + rail then takes >= 16 ms from
# 13.5 V to 10.6 V (L30), checked on this circuit in L41a's simulation.
C_HOLD = "2200u"
# Raw reservoirs: 4700 uF, the value L41a's rectifier sweep assumed
# (data/2026-09-26/L41a/scelte/raddrizzatore.csv): valley 18.1 V at -10 %
# mains on 2x15 V 50 VA, 2.5 V above 15 V + dropout (ADR-048). 35 V parts:
# the raw reaches ~23 V at +10 % mains.
C_RAW = "4700u"
# VRELAY's own reservoir behind D504: P9 (b) wants VRELAY >= 11.4 V (12 V
# -5 %) for >= 25 ms after the trip. Simulated in L41a on T2 = 12 V AC (the
# heat preference of ADR-048 point 7), mains -10 / nom / +10 %
# (data/2026-09-26/L41a/varianti/): 2200 uF held only 14 ms at -10 % - the
# "Da riaprire se" of ADR-048 - 4700 uF holds 51 / 134 / 216 ms. 25 V parts:
# the raw is ~17 V at +10 % mains.
C_VRELAY = "4700u"
# Supervisor thresholds (ADR-046: |13.5 V|), from the LM4040 2.5 V:
#   + rail: VPLUS * 10k / (44.2k + 10k) = 2.5 V at VPLUS = 13.55 V
#   - rail: node = VM + (VREF - VM) * 118k / (10k + 118k), against VREF / 2:
#           1.25 V at VM = -13.50 V; at -15 V the node sits at +1.13 V, so the
#           comparator's inputs never go below its ground (the naive divider
#           to 0 V would put them at -0.24 V).
R_P_TOP, R_P_BOT = "44.2k", "10k"
R_M_TOP, R_M_BOT = "10k", "118k"
# Mains detector: C_MD charges through R_MD from V5 while no half-wave
# discharges it; it crosses VREF = 2.5 V after 0.693 * 220k * 100n = 15.2 ms
# with the mains gone (ADR-048 point 5: ~15-20 ms), against a ~0.8 ms gap per
# half-wave with the mains present.
R_MD, C_MD = "220k", "100n"
# VRELAY supervisor (L41a, U506 ch B): VRELAY * 10k / (34k + 10k) = 2.5 V at
# VRELAY = 11.0 V, below the -5 % tolerance (11.4 V) of a +-1-2 % regulator.
R_VR_TOP, R_VR_BOT = "34k", "10k"
C_VR_HOLD = "2200u"

# ---- the timer (L41b1; ADR-048 point 6, ADR-049) -------------------------
# Every figure below is computed in docs/preamp/data/2026-09-26/L41b1/scelte/
# dimensiona.py and simulated in ../deck/.
# D (ADR-045: 20 ms nominal, >= 10 ms guaranteed): PERMIT_T charges through a
# diode to ~4.55 V from MUTE_REQ or PERMIT_REQ and decays through R_T; U508 A
# releases PERMIT_G while it is above VREF = 2.5 V:
#   D = R_T C_T ln(4.55 / 2.5) = 332k x 100n x 0.599 = 19.9 ms; 17.2 ms with
#   C_T -5 %, R_T -1 %, V5 at 4.90 V and a 0.55 V diode. C_T is C0G: an X7R
#   would lose tens of percent to bias and ageing, and D with it.
R_T, C_T = "332k", "100n"
# D2 (ADR-049): the audio board's VRELAY stays on >= D2 after PERMIT_G falls.
# VR_T charges from PERMIT_T one diode lower, and decays 3x slower:
#   VR_G falls at 1M x 100n x ln(4.1 / 2.5) = 49.5 ms, PERMIT_G at 19.9 ms:
#   D2 = 29.6 ms nominal, >= 17.3 ms with the corners crossed.
R_T2, C_T2 = "1M", "100n"
# MUTE_G's own rise lag: 10k (R513) x 22 nF = 0.22 ms, so PERMIT_G, which D522
# already keeps above MUTE_G, leads it at the release (J4 contract: PERMIT_CMD
# energised no later than MUTE_CMD). Its fall with the micro tri-stated goes
# through R513 + the 100k pull-down, || R514: 52k x 22n = 1.1 ms, which D
# absorbs (the bench measures it, not this comment).
C_MUTE_G = "22n"
# The LDR drive, per string (ADR-039 profile v4; ADR-049). Q1's base at VREF,
# its collector held at VREF by the op-amp: I_ref = (V5 - VREF) / R_REF =
# 100 uA. Q2's current is I_ref exp((V_B2 - VREF) / Vt): the v4 table asks
# V_B2 - VREF from -265 mV (10 nA at 60 C) to +152 mV (20 mA at 60 C).
R_REF = "24.9k"
# The DAC -> Q2 base network: DAC pin --R_A-- X --R_C-- VREF, DAC pin --R_PD--
# RET. Code 0 -> X = 2.048 V, full scale -> 2.789 V: -452..+289 mV around
# VREF, 0.181 mV = 0.06 dB per LSB. With the DAC in reset (shutdown, 500 k
# typical to ground, DS20002249B sec. 4.1.3) X = 2.23 V: 1-12 nA across
# 250 k-1 M and 15-60 C - never zero, always below the 190 nA dark knee.
# R_PD makes that the board's number: without it the floor ran 0.0-90 nA.
R_A, R_C, R_PD = "100k", "22.1k", "100k"
C_X = "1u"                   # 18 k x 1 uF = 18 ms: smooths the DAC's steps
# The mirror's emitter degeneration and the current sense, both 10 ohm: at
# 20 mA two VTL5C4 LEDs at their 2.0 V max (datasheet, abs max block) leave
# 0.25 V of margin on V5 = 4.90 V. The sense goes to GND, where J3's contract
# puts the cathode end; the micro reads it (ADR-049: the top-end calibration).
R_E_MIR, R_SENSE = "10", "10"
# Q_f's collector resistor limits the tail to ~(1.88 - 0.2) / 56 = 30 mA: a
# runaway command cannot drive the LEDs to their 40 mA absolute maximum.
R_LIM = "56"


def part(lib, name, value, ref, fp, **kw):
    # tag = ref: a stable identity for SKiDL (else a random tag per run)
    return Part(lib, name, value=value, ref=ref, footprint=fp, tag=ref, **kw)


def res(value, ref, a, b):
    r = part("Device", "R", value, ref, FP_R)
    r[1] += a
    r[2] += b
    return r


def cap(value, ref, a, b, fp=FP_C, polar=False):
    c = part("Device", "C_Polarized" if polar else "C", value, ref, fp)
    c[1] += a        # + for C_Polarized
    c[2] += b
    return c


def header(value, ref, nets, fp=None):
    j = part("Connector_Generic", "Conn_01x%02d" % len(nets), value, ref,
             fp or FP_HDR.format(n=len(nets)))
    for i, n in enumerate(nets, 1):
        j[i] += n
    return j


def sink(ref, drain, gate, ret, clamp_to, rclamp, dref, zref):
    """Low-side N-MOSFET for a relay coil command, with a diode + zener clamp.

    The clamp (diode then 24 V zener to VRELAY) and not a plain flyback diode:
    a diode across the coil stretches the release, and ADR-045 / L30 rest on
    the G6K's 3 ms maximum release (en-g6k.pdf p. 3). Clamp ~12 + 24 + 0.7 V,
    inside the 2N7002's 60 V. Whether the datasheet's 3 ms is measured with
    or without suppression is NOT read yet: L41c / G2 must.
    """
    q = part("Transistor_FET", "2N7002", "2N7002", ref, FP_SOT23)
    q[1] += gate
    q[2] += ret
    q[3] += drain
    d = part("Device", "D", "1N4148", dref, FP_DO35)
    d[2] += drain                  # A
    k = Net(rclamp)
    d[1] += k                      # K
    z = part("Device", "D_Zener", "24V", zref, FP_DO35)
    z[1] += k                      # K
    z[2] += clamp_to               # A to VRELAY
    return q


if __name__ == "__main__":
    # ---- nets shared with the audio board: SAME NAMES as preamp_audio.py
    VP, VM, GND = Net("VPLUS"), Net("VMINUS"), Net("GND")
    GND.drive = POWER
    VRELAY, RET = Net("VRELAY"), Net("RLY_RET")
    MUTE_CMD, PERMIT_CMD, MUTE_SW = (Net("MUTE_CMD"), Net("PERMIT_CMD"),
                                     Net("MUTE_SW"))
    LDR = [Net(n) for n in ("LDR_S_A", "LDR_S_K", "LDR_P_A", "LDR_P_K")]
    # ---- nets of this board
    # VRELAY_REG is U503's output, always on while the rear switch is on:
    # the logic (U504), the mains relay K501 and the supervisor live on it.
    # VRELAY (the name the J1 contract uses) is the audio board's, behind the
    # standby switch Q505 (L41b1, NC-037).
    VREG = Net("VRELAY_REG")
    VRELAY_EN = Net("VRELAY_EN")
    PERMIT_T, VR_T, VR_G = Net("PERMIT_T"), Net("VR_T"), Net("VR_G")
    V5 = Net("V5")
    AC_L, AC_N = Net("AC_L"), Net("AC_N")
    T1P_L, T1P_N = Net("T1_PRI_L"), Net("T1_PRI_N")
    T2P_L = Net("T2_PRI_L")
    T1A, T1B = Net("T1_SEC_A"), Net("T1_SEC_B")
    T2A, T2B = Net("T2_SEC_A"), Net("T2_SEC_B")
    RAW_P, RAW_M = Net("RAW_P"), Net("RAW_M")
    RECT_V, RAW_V = Net("RECT_V"), Net("RAW_V")
    VREF, VREF2 = Net("VREF"), Net("VREF_HALF")
    MUTE_G, PERMIT_G, MAINS_G = Net("MUTE_G"), Net("PERMIT_G"), Net("MAINS_G")
    MUTE_REQ, PERMIT_REQ, MAINS_REQ = (Net("MUTE_REQ"), Net("PERMIT_REQ"),
                                       Net("MAINS_REQ"))
    FRONT_SW = Net("FRONT_SW")

    # ================= the mains side (P2: every part here is in SAFETY.md)
    # J510: L and N from the rear IEC module, AFTER its fuse and its
    # double-pole switch (ADR-048 point 4). Protective earth goes from the
    # IEC module to the chassis directly, not through this board.
    header("AC_IN", "J510", [AC_L, AC_N], fp=FP_TB2)
    # The small transformer T2 is ALWAYS on while the rear switch is on: its
    # own fuse, because the IEC fuse is sized for the big toroid's inrush.
    # Rating from T2's datasheet (bom-component-manager, G2).
    f = part("Device", "Fuse", "T2 primary (T, from T2 datasheet)", "F501",
             FP_FUSE)
    f[1] += AC_L
    f[2] += T2P_L
    header("T2_PRI", "J511", [T2P_L, AC_N], fp=FP_TB2)
    # K501: DPST mains relay, BOTH poles (phase and neutral), on the big
    # toroid only. De-energised = toroid disconnected (ADR-048 supersedes
    # ADR-046's "rete staccata": the mains leaves everything only from the
    # rear). 12 VDC coil on VRELAY. P5 counts ~0.4 W for its coil; a
    # sensitive-coil variant is a BOM preference (ADR-048 point 7).
    k = part("Relay", "G2RL-2A", "G2RL-2A 12VDC MAINS", "K501",
             "Relay_THT:Relay_DPST_Omron_G2RL-2A")
    k["13"] += AC_L
    k["14"] += T1P_L
    k["23"] += AC_N
    k["24"] += T1P_N
    header("T1_PRI", "J512", [T1P_L, T1P_N], fp=FP_TB2)
    k["A1"] += VREG     # on VRELAY_REG: the standby switch is the audio board's
    MAINS_D = Net("MAINS_COIL")
    k["A2"] += MAINS_D
    dk = part("Device", "D", "1N4148", "D505", FP_DO35)
    dk[2] += MAINS_D    # plain flyback: the mains relay's release time is
    dk[1] += VREG       # not in any budget (it drops >= 50 ms after the mute)
    q = part("Transistor_FET", "2N7002", "2N7002", "Q503", FP_SOT23)
    q[1] += MAINS_G
    q[2] += RET
    q[3] += MAINS_D
    res("10k", "R520", MAINS_REQ, MAINS_G)
    res("100k", "R521", MAINS_G, RET)        # no timer => toroid off

    # ================= the rails (ADR-015: +/-15 V; ADR-048: 2x15 V 50 VA)
    # The centre tap goes straight onto GND - no net of its own: SKiDL would
    # name the merged net after either (limitations #23), and J1 pin 2 must
    # stay "GND" for check_psu_harness.py. It IS the audio ground's star.
    header("T1_SEC", "J513", [T1A, GND, T1B], fp=FP_TB3)
    br = part("Device", "D_Bridge_+AA-", "KBL04", "D501", FP_BRIDGE)
    br[1] += RAW_P
    br[2] += T1A
    br[3] += T1B
    br[4] += RAW_M
    cap(C_RAW, "C501", RAW_P, GND, FP_CP16, polar=True)
    cap(C_RAW, "C502", GND, RAW_M, FP_CP16, polar=True)

    # U501, + rail. TPS7A4701 ANY-OUT: VOUT = 1.4 V + the weights of the pins
    # tied to GND (vendor/ldo_regulator/ti/TPS7A4701/tps7a47.pdf, SBVS204G,
    # sec. 6.5.1, Table 6-1: pin 4 = 6.4, 5 = 6.4, 6 = 3.2, 8 = 1.6, 9 = 0.8,
    # 10 = 0.4, 11 = 0.2, 12 = 0.1 V); SENSE to OUT, EN to IN, pad to GND.
    u = part("Regulator_Linear", "TPS7A4701xRGW", "TPS7A4701 15V", "U501",
             FP_QFN)
    u["15"] += RAW_P
    u["16"] += RAW_P
    u["13"] += RAW_P                 # EN: on whenever the toroid is on
    u["1"] += VP
    u["20"] += VP
    u["3"] += VP                     # SENSE to OUT (ANY-OUT mode)
    u["7"] += GND
    u["21"] += GND
    for p in ("4", "5", "9"):        # 6.4 + 6.4 + 0.8 = 13.6 V over 1.4 V
        u[p] += GND
    # ANY-OUT pins 6, 8, 10, 11, 12 stay open: SKiDL 2.3 has no NC marker
    # (L36), so ERC lists them as unconnected - on purpose.
    NR_P = Net("NR_P")
    u["14"] += NR_P
    cap("10u", "C507", NR_P, GND)
    cap("10u", "C509", RAW_P, GND)
    cap("10u", "C511", VP, GND)
    cap(C_HOLD, "C505", VP, GND, FP_CP16, polar=True)
    # D510: the datasheet says nothing on reverse current (no "revers*" in
    # SBVS204G, L41a), and 2200 uF sit on OUT: a Schottky OUT -> IN keeps OUT
    # from rising above IN if the raw side collapses first.
    d = part("Device", "D_Schottky", "1N5819", "D510", FP_DO41)
    d[2] += VP
    d[1] += RAW_P

    # U502, - rail. TPS7A3301, adjustable (vendor/ldo_regulator/ti/TPS7A3301/
    # tps7a33.pdf, SBVS169D): VREF = -1.175 V typ, VOUT = VREF (1 + R1 / R2)
    # (Eq. 2) = -1.175 x 12.8 = -15.04 V; divider current 117 uA > 5 uA;
    # 10 nF FB -> OUT as recommended (pin table); EN to IN allowed ("|VEN| <=
    # |VIN|"); the THERMAL PAD IS INTERNALLY GND (pin table) - L41a's first
    # draft had it on IN, i.e. RAW_M shorted to ground on the board.
    u = part("Regulator_Linear", "TPS7A3301RGW", "TPS7A3301 -15V", "U502",
             FP_QFN)
    u["15"] += RAW_M
    u["16"] += RAW_M
    u["13"] += RAW_M                 # EN
    u["21"] += GND                   # thermal pad = GND (SBVS169D pin table)
    u["1"] += VM
    u["20"] += VM
    u["7"] += GND
    FB_M = Net("FB_M")
    u["3"] += FB_M
    res("118k", "R501", VM, FB_M)
    res("10k", "R502", FB_M, GND)
    cap("10n", "C513", VM, FB_M)     # feed-forward, noise
    NR_M = Net("NR_M")
    u["14"] += NR_M
    cap("10u", "C508", GND, NR_M)
    cap("10u", "C510", GND, RAW_M)
    cap("10u", "C512", GND, VM)
    cap(C_HOLD, "C506", GND, VM, FP_CP16, polar=True)
    # D511: Abs Max "OUT pin to IN pin -0.3 V" (SBVS169D p. 5) - with 2200 uF
    # on OUT, IN must not rise above OUT by more than a Schottky's drop.
    d = part("Device", "D_Schottky", "1N5819", "D511", FP_DO41)
    d[2] += RAW_M
    d[1] += VM

    # ================= VRELAY = 12 V from T2's own winding (ADR-048 point 3)
    header("T2_SEC", "J514", [T2A, T2B], fp=FP_TB2)
    br = part("Device", "D_Bridge_+AA-", "DF04M", "D503", FP_BRIDGE)
    br[1] += RECT_V
    br[2] += T2A
    br[3] += T2B
    br[4] += RET          # VRELAY's return: its own, joined to GND only at NT501
    # D504 isolates the reservoir from RECT_V, so that RECT_V falls with the
    # mains and the detector sees it (and the hold is VRELAY's alone).
    d = part("Device", "D_Schottky", "1N5819", "D504", FP_DO41)
    d[2] += RECT_V
    d[1] += RAW_V
    cap(C_VRELAY, "C520", RAW_V, RET, FP_CP16, polar=True)
    u = part("Regulator_Linear", "TPS7A4701xRGW", "TPS7A4701 12V", "U503",
             FP_QFN)
    u["15"] += RAW_V
    u["16"] += RAW_V
    u["13"] += RAW_V
    u["1"] += VREG
    u["20"] += VREG
    u["3"] += VREG
    u["7"] += RET
    u["21"] += RET
    for p in ("4", "6", "9", "11"):  # 6.4 + 3.2 + 0.8 + 0.2 = 10.6 V over 1.4
        u[p] += RET
    # ANY-OUT pins 5, 8, 10, 12 open, on purpose (ERC lists them).
    NR_V = Net("NR_V")
    u["14"] += NR_V
    cap("10u", "C521", NR_V, RET)
    cap("10u", "C522", RAW_V, RET)
    # C523: a hold-up AFTER U503 (L41a). If U503 itself fails open, the
    # jack relays are released by U506 ch B (VRELAY < 11 V) while this keeps
    # K6, K1 / K5 and K11 / K12 up, so D survives the fault (ADR-045). ~87 mA
    # left after the jack coils drop; 11.0 -> 9.6 V (80 %) in >= 25 ms wants
    # >= 1.55 mF: 2200 uF, -20 % = 1760 uF. Without it, L41a's first fault
    # run dropped every coil together - L30's "no D" case, 69 mV.
    # L41b1: it stays on VRELAY_REG, BEFORE the standby switch Q505, so the
    # supervisor and the hold are exactly L41a's; the audio board draws on it
    # through Q505, which the timer holds on for D + D2 after the mute.
    cap(C_VR_HOLD, "C523", VREG, RET, FP_CP16, polar=True)
    d = part("Device", "D_Schottky", "1N5819", "D512", FP_DO41)   # as D510
    d[2] += VREG
    d[1] += RAW_V
    # V5, the logic: MCP1703A-5002, ~2 uA quiescent, for the standby budget.
    u = part("Regulator_Linear", "MCP1703Ax-500xxDB", "MCP1703A-5002",
             "U504", "Package_TO_SOT_SMD:SOT-223-3_TabPin2")
    u["1"] += VREG
    u["2"] += RET
    u["3"] += V5
    cap("1u", "C524", VREG, RET)
    cap("1u", "C525", V5, RET)

    # The star: the ONE point where VRELAY's return meets the audio ground.
    # Here, next to T1's centre tap, so that no relay current crosses the
    # audio ground anywhere else.
    nt = part("Device", "NetTie_2", "STAR", "NT501", "NetTie:NetTie-2_SMD_Pad0.5mm")
    nt[1] += RET
    nt[2] += GND

    # ================= the supervisor (ADR-046, ADR-048 point 5)
    # LM4040 2.5 V shunt from V5; VREF / 2 for the - rail's comparator.
    ref = part("Reference_Voltage", "LM4040DBZ-2.5", "LM4040A-2.5", "U507",
               FP_SOT23)
    ref["1"] += VREF
    ref["2"] += RET
    res("2k", "R503", V5, VREF)           # ~1.2 mA through the shunt
    res("10k", "R504", VREF, VREF2)
    res("10k", "R505", VREF2, RET)
    cap("100n", "C514", VREF, RET)
    # U505 ch A, + rail: out LOW when VPLUS * 10/54.2 < VREF, i.e. < 13.55 V.
    # U505 ch B, - rail: out LOW when the VM node > VREF / 2, i.e. |VM| < 13.5 V.
    NP, NM = Net("SUP_P"), Net("SUP_M")
    res(R_P_TOP, "R506", VP, NP)
    res(R_P_BOT, "R507", NP, RET)
    cap("1n", "C515", NP, RET)            # 10 us: noise, not delay (<< 1 ms)
    res(R_M_TOP, "R508", VREF, NM)
    res(R_M_BOT, "R509", NM, VM)
    cap("1n", "C516", NM, RET)
    cmp_ = part("Comparator", "LM2903", "TLV1702 (dual, open-drain)", "U505",
                FP_SOIC8)
    cmp_["3"] += NP        # A +
    cmp_["2"] += VREF      # A -
    cmp_["1"] += MUTE_G    # A out, open-drain: pulls the gate low
    cmp_["5"] += VREF2     # B +
    cmp_["6"] += NM        # B -
    cmp_["7"] += MUTE_G    # B out
    cmp_["8"] += V5
    cmp_["4"] += RET
    cap("100n", "C517", V5, RET)

    # ================= the mains detector (ADR-048 point 5)
    # RECT_V is T2's full-wave output before D504: it falls to 0 with the
    # mains. Each half-wave turns Q504 on and empties C_MD; with the mains
    # gone, C_MD charges through R_MD and crosses VREF after ~15 ms.
    MB, MD = Net("MD_B"), Net("MD")
    res("22k", "R510", RECT_V, MB)
    res("4.7k", "R511", MB, RET)          # on above ~4 V of RECT_V
    qd = part("Transistor_BJT", "BC847", "BC847", "Q504", FP_SOT23)
    qd[1] += MB
    qd[2] += RET
    qd[3] += MD
    res(R_MD, "R512", V5, MD)
    cap(C_MD, "C518", MD, RET)
    cmp2 = part("Comparator", "LM2903", "TLV1702 (dual, open-drain)", "U506",
                FP_SOIC8)
    cmp2["3"] += VREF      # A +
    cmp2["2"] += MD        # A -: out LOW when MD > VREF (no mains)
    cmp2["1"] += MUTE_G
    # ch B: VRELAY itself (L41a). Out LOW when VRELAY < 11.0 V: a failed
    # VRELAY regulator mutes BEFORE the coils sag, and C523 keeps the
    # permissive and the gain relays up for D (see C523).
    NV = Net("SUP_VR")
    res(R_VR_TOP, "R522", VREG, NV)
    res(R_VR_BOT, "R523", NV, RET)
    cap("1n", "C526", NV, RET)
    cmp2["5"] += NV        # B +
    cmp2["6"] += VREF      # B -
    cmp2["7"] += MUTE_G
    cmp2["8"] += V5
    cmp2["4"] += RET
    cap("100n", "C519", V5, RET)

    # ================= the J4 commands (ADR-045, ADR-048 point 6, ADR-049)
    # Every micro output that commands a relay has a pull-down: after a
    # reset the ATtiny's outputs are tri-stated (DS40002205A sec. 16.3.1),
    # and tri-stated must read as "at rest" (ADR-022 condition 1; 2e).
    res("100k", "R525", MUTE_REQ, RET)
    res("100k", "R526", PERMIT_REQ, RET)
    res("100k", "R527", VRELAY_EN, RET)
    res("100k", "R528", MAINS_REQ, RET)
    # MUTE_CMD: the timer asks through MUTE_REQ, but any comparator output
    # overrides it by pulling MUTE_G low; the pull-down makes a dead timer
    # a mute. Active-for-music, ADR-046.
    res("10k", "R513", MUTE_REQ, MUTE_G)
    res("100k", "R514", MUTE_G, RET)
    cap(C_MUTE_G, "C527", MUTE_G, RET)
    sink("Q501", MUTE_CMD, MUTE_G, RET, VRELAY, "CLAMP_MUTE", "D506", "D507")
    # MUTE_G can never stand above PERMIT_G: a Schottky from MUTE_G to
    # PERMIT_G clamps it to PERMIT_G + ~0.3 V, below any 2N7002 threshold
    # while PERMIT_G is low. So the jack relays cannot be energised before
    # the permissive, by any firmware (J4 contract, release).
    d = part("Device", "D_Schottky", "BAT54", "D522", FP_SOD323)
    d[2] += MUTE_G                 # A
    d[1] += PERMIT_G               # K
    # PERMIT_CMD: D in hardware (ADR-048 point 6). PERMIT_T is charged
    # through a diode from EITHER request, MUTE_REQ or PERMIT_REQ, so the
    # permissive stays up while the timer asks for music whatever it does
    # with PERMIT_REQ, and D after the LAST of the two falls. The 1k limits
    # the pin current into C_T + C_T2 (tau 0.2 ms).
    PTA, PTB = Net("PT_A"), Net("PT_B")
    res("1k", "R532", MUTE_REQ, PTA)
    d = part("Device", "D", "1N4148", "D520", FP_DO35)
    d[2] += PTA
    d[1] += PERMIT_T
    res("1k", "R533", PERMIT_REQ, PTB)
    d = part("Device", "D", "1N4148", "D521", FP_DO35)
    d[2] += PTB
    d[1] += PERMIT_T
    cap(C_T, "C528", PERMIT_T, RET, FP_C1206)
    res(R_T, "R534", PERMIT_T, RET)
    dly = part("Comparator", "LM2903", "TLV1702 (dual, open-drain)", "U508",
               FP_SOIC8)
    dly["3"] += PERMIT_T   # A +: out released (high) while PERMIT_T > VREF
    dly["2"] += VREF       # A -
    dly["1"] += PERMIT_G
    res("10k", "R524", V5, PERMIT_G)
    res("100k", "R516", PERMIT_G, RET)     # a dead U508: permissive released
    sink("Q502", PERMIT_CMD, PERMIT_G, RET, VRELAY, "CLAMP_PERMIT", "D508",
         "D509")

    # ================= VRELAY to the audio board: the standby switch (NC-037)
    # VR_T is charged from PERMIT_T (one diode lower) and from VRELAY_EN, and
    # decays 3x slower than PERMIT_T: the switch opens D2 after PERMIT_G at
    # the earliest. With the micro in reset while the music plays, the order
    # is MUTE_CMD, then PERMIT_CMD >= D later, then VRELAY >= D2 later.
    d = part("Device", "D", "1N4148", "D523", FP_DO35)
    d[2] += PERMIT_T
    d[1] += VR_T
    VEA = Net("VE_A")
    res("1k", "R535", VRELAY_EN, VEA)
    d = part("Device", "D", "1N4148", "D524", FP_DO35)
    d[2] += VEA
    d[1] += VR_T
    cap(C_T2, "C529", VR_T, RET, FP_C1206)
    res(R_T2, "R536", VR_T, RET)
    dly["5"] += VR_T       # B +
    dly["6"] += VREF       # B -
    dly["7"] += VR_G
    dly["8"] += V5
    dly["4"] += RET
    cap("100n", "C530", V5, RET)
    res("10k", "R537", V5, VR_G)
    res("100k", "R538", VR_G, RET)         # a dead U508: switch open
    # Q506 pulls Q505's gate down through R539: Vgs = -12 x 100 / 147 =
    # -8.2 V, inside the AO3401A's +-12 V. C531 slows both edges (~3 ms on,
    # ~10 ms off): no inrush into the audio board's decoupling, and the off
    # edge only adds to D2.
    SWD, PG = Net("SW_D"), Net("SW_G")
    q = part("Transistor_FET", "2N7002", "2N7002", "Q506", FP_SOT23)
    q[1] += VR_G
    q[2] += RET
    q[3] += SWD
    res("47k", "R539", SWD, PG)
    res("100k", "R540", PG, VREG)
    cap("100n", "C531", PG, VREG)
    q = part("Transistor_FET", "AO3401A", "AO3401A", "Q505", FP_SOT23)
    q[1] += PG
    q[2] += VREG           # S
    q[3] += VRELAY         # D: J1 pin 4

    # MUTE_SW (SW3 on the audio board pulls it to RLY_RET = music) and the
    # front power switch: inputs of the timer, pulled up to V5, each through
    # 1k + 100 nF to its pin (panel wiring: ESD, and the first debounce pole).
    res("100k", "R517", V5, MUTE_SW)
    res("100k", "R518", V5, FRONT_SW)
    header("POWER_SW", "J508", [FRONT_SW, RET])
    FRONT_IN, SW3_IN = Net("FRONT_IN"), Net("MUTE_SW_IN")
    res("1k", "R541", FRONT_SW, FRONT_IN)
    cap("100n", "C532", FRONT_IN, RET)
    res("1k", "R542", MUTE_SW, SW3_IN)
    cap("100n", "C533", SW3_IN, RET)

    # ================= the micro (ADR-049; spec: firmware/preamp_timer/spec/)
    # ATtiny3216 on V5: power-down 0.1 uA typ, 2 uA max at 25 C (DS40002205A
    # Table 36-5). What it reads goes through 47k, so an unpowered or
    # latched-up pin cannot load a supervisor node.
    mcu = part("MCU_Microchip_ATtiny", "ATtiny3216-S", "ATtiny3216", "U509",
               FP_SOIC20W)
    mcu["1"] += V5
    mcu["20"] += RET
    cap("100n", "C534", V5, RET)
    UPDI = Net("UPDI")
    mcu["16"] += UPDI                  # PA0: UPDI, one-wire programming
    header("UPDI", "J515", [UPDI, V5, RET])
    DSDI, DSCK, DCS = Net("DAC_SDI"), Net("DAC_SCK"), Net("DAC_CS")
    mcu["17"] += DSDI                  # PA1: SPI0 MOSI
    mcu["19"] += DSCK                  # PA3: SPI0 SCK
    mcu["2"] += DCS                    # PA4: DAC chip select
    mcu["11"] += MUTE_REQ              # PB0
    mcu["10"] += PERMIT_REQ            # PB1
    mcu["9"] += MAINS_REQ              # PB2
    mcu["8"] += VRELAY_EN              # PB3
    mcu["12"] += FRONT_IN              # PC0
    mcu["13"] += SW3_IN                # PC1
    # PC3 (15) is spare, left open on purpose (ERC lists it).
    # The analog reads (ADC0: AIN2 PA2, AIN5-7 PA5-7, AIN8 PB5, AIN9 PB4):
    # which supervisor fired, so the firmware can tell a mains hole the rails
    # rode through from a fault with the mains present (ADR-048 point 5); and
    # the two LED currents, for the top-end calibration (ADR-049).
    # MUTE_G_IN (PC2) reads back the hardware's verdict through 1 M, not 47k:
    # a firmware that turned PC2 into an output driven high would otherwise
    # lift MUTE_G around MUTE_REQ. Through 1 M against MUTE_G's ~52k to RET it
    # reaches ~0.25 V, below any 2N7002 threshold (2e, --timer, T2).
    SUP_P_, SUP_M_, MD_ = NP, NM, MD
    MG_IN = Net("MUTE_G_IN")
    res("1M", "R543", MUTE_G, MG_IN)
    mcu["14"] += MG_IN
    for ref, src, pin, name in (("R544", SUP_P_, "3", "ADC_SUP_P"),
                                ("R545", SUP_M_, "4", "ADC_SUP_M"),
                                ("R546", NV, "5", "ADC_SUP_VR"),
                                ("R547", MD_, "6", "ADC_MD")):
        n = Net(name)
        res("47k", ref, src, n)
        mcu[pin] += n

    # ================= the LDR drive (ADR-039 profile v4, ADR-048 point 6)
    # The DAC: MCP4822, G = 2x on its 2.048 V reference (0-4.095 V). LDAC
    # to RET: every write updates at once. VA = the series string, VB = the
    # shunt string.
    dac = part("Analog_DAC", "MCP4822", "MCP4822", "U510", FP_SOIC8)
    dac["1"] += V5
    dac["7"] += RET
    dac["2"] += DCS
    dac["3"] += DSCK
    dac["4"] += DSDI
    dac["5"] += RET
    cap("100n", "C535", V5, RET)
    DAC_S, DAC_P = Net("DAC_S"), Net("DAC_P")
    dac["8"] += DAC_S
    dac["6"] += DAC_P
    opa = part("Amplifier_Operational", "MCP6004", "MCP6004", "U511",
               FP_SOIC14)
    opa["4"] += V5
    opa["11"] += RET
    cap("100n", "C536", V5, RET)
    # One exponential converter per string. Per string:
    #   Q1 (pair unit 1): base VREF, collector N held at VREF by the op-amp
    #     (loop: op-amp out -> Q_f, a PNP follower, -> the common emitters E),
    #     so Q1 carries I_ref = (V5 - VREF) / R_REF = 100 uA at any command;
    #   Q2 (pair unit 2): base = the buffered command X, collector into a PNP
    #     mirror whose output sources the string: anode on J3, cathode on J3,
    #     back through R_SENSE to GND (the J3 contract: cathode end to GND).
    # A matched pair in one package (BCM847BS, BC847BS footprint): Q1 and Q2
    # see the same temperature, and the firmware scales the command with the
    # micro's sensor for Vt (ADR-049). NOT modelled: Q2's self-heating at
    # 20 mA (~44 mW) against Q1 - the top-end calibration takes it out on the
    # prototype; SPICE's BJT has no thermal node.
    strings = (("S", DAC_S, LDR[0], LDR[1], ("1", "2", "3"), ("5", "6", "7"),
                ("Q507", "Q509", "Q511"), "R548", "7", "ADC_I_S"),
               ("P", DAC_P, LDR[2], LDR[3], ("8", "9", "10"), ("12", "13", "14"),
                ("Q508", "Q510", "Q512"), "R560", "18", "ADC_I_P"))
    for fn, dacn, anode, cathode, loop_p, buf_p, (qp, qf, qm), r0, mpin, adcn \
            in strings:
        rn = int(r0[1:])

        def r(k):
            return "R%d" % (rn + k)

        N, E, F, FC = (Net("EXP_N_" + fn), Net("EXP_E_" + fn),
                       Net("EXP_F_" + fn), Net("EXP_FC_" + fn))
        X, B2, MI, EM1, EM2 = (Net("EXP_X_" + fn), Net("EXP_B2_" + fn),
                               Net("MIR_" + fn), Net("MIR_E1_" + fn),
                               Net("MIR_E2_" + fn))
        # the reference loop
        res(R_REF, r(0), V5, N)
        pair = part("Transistor_BJT", "BC847BS", "BCM847BS (matched pair)", qp,
                    FP_SOT363)
        pair["6"] += N          # C1
        pair["2"] += VREF       # B1
        pair["1"] += E          # E1
        pair["4"] += E          # E2
        pair["5"] += B2         # B2
        pair["3"] += MI         # C2
        o_out, o_neg, o_pos = loop_p
        opa[o_out] += F
        opa[o_neg] += N
        opa[o_pos] += VREF
        cap("10n", "C%d" % (537 if fn == "S" else 541), F, N)   # loop comp.
        qfol = part("Transistor_BJT", "BC857", "BC857", qf, FP_SOT23)
        qfol["1"] += F          # B
        qfol["2"] += E          # E
        qfol["3"] += FC         # C
        res(R_LIM, r(1), FC, RET)
        # the command: DAC -> X -> buffer -> Q2's base
        res(R_PD, r(2), dacn, RET)
        res(R_A, r(3), dacn, X)
        res(R_C, r(4), VREF, X)
        cap(C_X, "C%d" % (538 if fn == "S" else 542), X, RET)
        b_pos, b_neg, b_out = buf_p
        opa[b_pos] += X
        opa[b_neg] += B2
        opa[b_out] += B2
        # the PNP mirror, emitters degenerated, sourcing into the anode
        mir = part("Transistor_BJT", "BC857BS", "BCM857BS (matched pair)", qm,
                   FP_SOT363)
        res(R_E_MIR, r(5), V5, EM1)
        res(R_E_MIR, r(6), V5, EM2)
        mir["1"] += EM1         # E1: the input, diode-connected
        mir["2"] += MI          # B1
        mir["6"] += MI          # C1
        mir["4"] += EM2         # E2: the output
        mir["5"] += MI          # B2
        mir["3"] += anode       # C2 -> J3 anode
        # the sense, and the micro's read of it
        res(R_SENSE, r(7), cathode, GND)
        n = Net(adcn)
        res("47k", r(8), cathode, n)
        mcu[mpin] += n

    # ================= the harnesses to the audio board (check_psu_harness.py)
    header("POWER", "J1", [VP, GND, VM, VRELAY])
    header("RLY_RET", "J2", [RET])
    header("LDR_CMD", "J3", LDR)
    header("MUTE_TIMER", "J4", [MUTE_CMD, PERMIT_CMD, MUTE_SW])

    # ERC, explained (L41a): "POWER-OUT connected to POWER-OUT" on VPLUS and
    # VRELAY_REG is the KiCad symbol's two OUT pins (1, 20) of ONE TPS7A4701,
    # both typed power_out, which the datasheet wants joined; "insufficient
    # drive" on RAW_P / RAW_M / RAW_V / RLY_RET is a bridge output (passive
    # pins) feeding a power_in - L41b1 adds the ground pins of U508-U511 to
    # the RLY_RET list, same cause. Unconnected: the ANY-OUT pins (above) and
    # the micro's spare PC3. L41b1: 21 warnings, the same 2 "errors".
    try:
        ERC()
    except Exception as e:  # noqa: BLE001
        print("SKiDL ERC raised:", e)

    netpath = os.environ.get(
        "PSU_NET_OUT", os.path.join(REPO, "circuits", "preamp", "psu.net"))
    generate_netlist(file_=netpath, tool="kicad10")
    print("KiCad netlist ->", netpath)
