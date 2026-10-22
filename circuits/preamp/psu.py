#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
psu.py - the supply board: the second PCB of P4 (ADR-010, ADR-048; L41a, L41b1).

Source of truth for the supply's topology (AGENTS.md rule 2), as
preamp_audio.py is for the audio board. It realises P9 (ADR-046, as ADR-048
reads it) and the contracts written on the audio board next to J1 and J4.

    rear IEC module (fuse + DOUBLE-POLE switch: off = mains off everything)
      |
      +-- F501 -- T2 (small toroid, ALWAYS on while the rear is on) -- D503 --+-- D504 -- C_V --[U503 12 V]-- VRELAY_REG -+-[U504 5 V]-[U512 5 V]-- V5 (logic, micro; ADR-094)
      |                                                                      |                                     +-[Q505]-- VRELAY (J1 pin 4, the audio board)
      |                                                                      +-- mains detector (Q504, U506 ch 1)
      +-- K501 (DPST, coil on VRELAY_REG) -- T1 (toroid 2x15 V 50 VA) -- D501 -+-- C501 -- R550 --[U501 TPS7A4701]-- VPLUS_REG --D515>-- C505 -- VPLUS
                                                                              +-- C502 -- R551 --[U502 TPS7A3301]-- VMINUS_REG --<D516-- C506 -- VMINUS
    supervisor U505: VPLUS < 13.5 V, |VMINUS| < 13.5 V   \
    mains detector U506 A: no half-wave for ~15 ms        -> pull MUTE_G low: Q501 off, MUTE_CMD released (mute)
    VRELAY supervisor U506 B: VRELAY_REG < 11.0 V         /

    the timer (L41b1, ADR-049): micro U509 -> MUTE_REQ, PERMIT_REQ, VRELAY_EN, MAINS_REQ
      MUTE_REQ --R513-- MUTE_G (<= PERMIT_G by D522)                         -> Q501 -> MUTE_CMD
      MUTE_REQ, PERMIT_REQ --diodes--> PERMIT_T (RC, D) -> U508 A vs VREF -> PERMIT_G -> Q502 -> PERMIT_CMD
      PERMIT_T, VRELAY_EN  --diodes--> VR_T (RC, D + D2) -> U508 B vs VREF -> VR_G -> Q506 -> Q505 (VRELAY on)

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
 - (Until L47c1: the LDR drive of ADR-039 / ADR-049 - the dual DAC U510, two
   exponential converters, J3. ADR-062 removed the graduated mute, and the
   drive with it: the mute cuts with the audio board's jack relays alone.)

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
# ADR-092: R550 / R551, 0.44-0.46 W at regime - a 2 W axial, lifted off the board (piste larghe)
FP_R_2W = "Resistor_THT:R_Axial_DIN0414_L11.9mm_D4.5mm_P15.24mm_Horizontal"
FP_C = "Capacitor_SMD:C_0805_2012Metric"
FP_SOT23 = "Package_TO_SOT_SMD:SOT-23"
FP_SOIC8 = "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm"
FP_QFN = ("Package_DFN_QFN:Texas_RGW0020A_VQFN-20-1EP_5x5mm_P0.65mm_"
          "EP3.15x3.15mm_ThermalVias")
FP_BRIDGE = "Diode_THT:Diode_Bridge_Vishay_KBL"
FP_DO41 = "Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal"
# ADR-093: the SB340s (3 A, 40 V) of the rail regulators - in series after OUT, and on the pins
FP_DO201 = "Diode_THT:D_DO-201AD_P15.24mm_Horizontal"
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
# (data/2026-09-26/L41a/scelte/raddrizzatore.csv; ADR-048). On TODAY's load
# (L51b: the rails of tb_op, the selector's coils; data/2026-10-09/L51b/rete/
# analisi.csv) the valley is 17.89 V at -10 % mains on 2x15 V 50 VA, 2.6 V
# above 15 V + dropout (L41a's load: 18.05 V). 35 V parts: the raw reaches
# ~23 V at +10 % mains.
C_RAW = "4700u"
# VRELAY's own reservoir behind D504: P9 (b) wants VRELAY >= 11.4 V (12 V
# -5 %) for >= 25 ms after the trip. Chosen in L41a on T2 = 12 V AC (the heat
# preference of ADR-048 point 7): 2200 uF held only 14 ms at -10 % mains -
# the "Da riaprire se" of ADR-048. On TODAY's circuit and load (L51b: without
# the LDR drive of ADR-062, with the selector's coils of ADR-064 and the rails
# of tb_op; data/2026-10-09/L51b/rete/analisi.csv) 4700 uF holds VRELAY_REG
# >= 11.4 V for 48.3 / 121.7 / 195.4 ms after the jack relays release, at
# mains -10 / nom / +10 %: 23 ms over P9. The load sets it (NC-050): 61.1 ms
# without the selector (L47c2a), 36.1 with the drive (L42b), 62.8 with
# L41a's load. Smaller values on L47c2a's bench (data/2026-10-05/L47c2a/
# varianti/): 3300 uF 41.0 ms, 2200 uF 25.1 ms at -10 %. Kept at 4700 uF by
# the user's choice (L47c2a), for the loads still to come before the freeze.
# L60c2: K3 an IM06TS (ADR-085, 11.7 mA instead of 9.1) -> 46.4 / 119.7 /
# 193.3 ms on L51b's bench with that one change (data/2026-10-15/L60c2/rete/).
# 25 V parts: the raw is ~17 V at +10 % mains.
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
R_MD_HALF = "110k"      # ADR-094: R_MD as two in series (R512 + R555), 2 x 110k = 220k
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


def sink(ref, drain, gate, ret, clamp_to, rclamp, dref, dref2, zref):
    """Low-side N-MOSFET for a relay coil command, with a diode + zener clamp.

    The clamp (diode then 24 V zener to VRELAY) and not a plain flyback diode:
    a diode across the coil stretches the release, and ADR-045 / L30 rest on
    the G6K's 3 ms maximum release (en-g6k.pdf p. 3). Clamp ~12 + 24 + 0.7 V,
    inside the 2N7002's 60 V. Whether the datasheet's 3 ms is measured with
    or without suppression is NOT read yet: L41c / G2 must.

    ADR-094 (L45d2b2b2, ADR-075): the diode is TWO 1N4148 in series (dref, dref2). With one
    shorted the zener, forward from VRELAY, put VRELAY on the drain: 0.87 A in a 2N7002 saturated
    (its datasheet), ~9 W, and at mains +10 % for good (VRELAY_REG never below the supervisor's
    11.0 V), Delta lost on PERMIT_CMD (~70 dB SPL). With two, one shorted leaves the other
    blocking: 0 mA. The clamp rises one diode, ~12 + 25.6 + 1.7 = 39.3 V at the worst.
    """
    q = part("Transistor_FET", "2N7002", "2N7002", ref, FP_SOT23)
    q[1] += gate
    q[2] += ret
    q[3] += drain
    d = part("Device", "D", "1N4148", dref, FP_DO35)
    d[2] += drain                  # A
    m = Net(rclamp + "_D")
    d[1] += m                      # K
    d = part("Device", "D", "1N4148", dref2, FP_DO35)
    d[2] += m                      # A
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
    # plain flyback: the mains relay's release time is not in any budget (it drops >= 50 ms after
    # the mute). ADR-094: two 1N4148 in series, D505 + D532 - one shorted put VRELAY_REG on Q503
    # (0.89 A, 10.6 W in a 2N7002, Delta lost, ~70 dB SPL); with two the other blocks, 0 mA
    MAINS_DM = Net("MAINS_COIL_D")
    dk = part("Device", "D", "1N4148", "D505", FP_DO35)
    dk[2] += MAINS_D
    dk[1] += MAINS_DM
    dk = part("Device", "D", "1N4148", "D532", FP_DO35)
    dk[2] += MAINS_DM
    dk[1] += VREG
    # R552, ADR-094: 47 ohm between the coil and Q503, outside the flyback loop (coil + D505 / D532).
    # A shorted coil put VRELAY_REG on Q503 and dumped C523 (2200 uF) into it: 0.89 A, 10.6 W in
    # a 2N7002 - a 60 V / 2 A MOSFET instead took 14.7 A, 137 W (L45d2b2b2's bench). With R552:
    # 0.24 A, Q503 at <= 114 C with 60 C of air, R552 2.7 W for ~0.2 s (0.56 J) until the firmware
    # drops MAINS_REQ, the mute ordered (~16 dB SPL), Delta 17.2 ms. At regime 29.5 mA, 41 mW in
    # R552, the coil at 12 x 360 / 407 = 10.6 V (88 %). A 2 W axial as R550 (piste larghe): its
    # short-time overload against 2.7 W for 0.2 s is read at the part's choice (G2)
    MAINS_S = Net("MAINS_SINK")
    r = part("Device", "R", "47", "R552", FP_R_2W)
    r[1] += MAINS_D
    r[2] += MAINS_S
    q = part("Transistor_FET", "2N7002", "2N7002", "Q503", FP_SOT23)
    q[1] += MAINS_G
    q[2] += RET
    q[3] += MAINS_S
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
    # ADR-092 (L45d2b2a): R550, 4.7 ohm between the reservoir and the regulator's IN. At regime
    # U501 dissipates (RAW - 15 V) x ~0.3 A: 2.34 W at mains +10 %, 136 C with 60 C of air at
    # SBVS204G's 32.5 C/W, over the 125 C of ADR-021. With R550 1.90 W (122 C) and 0.44 W in the
    # resistor (a 2 W axial: <= half its rating at 60 C); the headroom IN - OUT at mains -10 %
    # goes from 2.88 to 1.45 V, over the 1 V the PSRR quota of ADR-020 assumes. The rest is the
    # copper under the pad at the layout (<= 27 C/W, NC-072). EN, C509 and D510 sit on the pin's
    # side, RAW_PR: EN must not exceed IN, and D510 guards the pin.
    RAW_PR = Net("RAW_PR")
    r = part("Device", "R", "4.7", "R550", FP_R_2W)
    r[1] += RAW_P
    r[2] += RAW_PR
    # ADR-093 (L45d2b2b1, ADR-074): OUT is VPLUS_REG, and D515 (SB340) carries it to VPLUS. In a
    # short of the raw side the hold-up (C505, the audio board's 800 uF and its RC cells) can no
    # longer flow back into the short through D510: the rail stays up until the jack opens (13.5 V
    # at the jack in all 24 rows of ADR-074, ~32 dB SPL at the worst, against ~78 dB SPL with the
    # pin's ceramic C509 shorted before). SENSE stays on the PIN, not on the rail: the regulator
    # sees its own 10 uF (C511) as today. ADR-096 (L45d2b3a) measured the other form: with the
    # diode inside the loop (~0.13 ohm against the rail's mF) the phase margin falls to 51 deg
    # with TI's model and 22-59 deg with a generic one, lowest with low-ESR hold-up capacitors;
    # here 89-91 deg. The rail is the pin minus the SB340's ~0.31 V (25 C typical, Vishay 88719
    # fig. 3), so the set point is 15.3 V.
    VP_REG = Net("VPLUS_REG")
    u = part("Regulator_Linear", "TPS7A4701xRGW", "TPS7A4701 15.3V", "U501",
             FP_QFN)
    u["15"] += RAW_PR
    u["16"] += RAW_PR
    u["13"] += RAW_PR                # EN: on whenever the toroid is on
    u["1"] += VP_REG
    u["20"] += VP_REG
    u["3"] += VP_REG                 # SENSE to OUT (ANY-OUT mode), at the pin (ADR-093)
    u["7"] += GND
    u["21"] += GND
    # 6.4 + 6.4 + 0.8 = 13.6 V over 1.4 V, and ADR-093's 0.2 + 0.1 V: 15.3 V
    for p in ("4", "5", "9", "11", "12"):
        u[p] += GND
    # ANY-OUT pins 6, 8, 10 stay open: SKiDL 2.3 has no NC marker
    # (L36), so ERC lists them as unconnected - on purpose.
    NR_P = Net("NR_P")
    u["14"] += NR_P
    # C507, ADR-091 (L45d2b2a, NC-063): 4.7 uF. The NR capacitor is also the soft-start:
    # t_SS = 100 kOhm x C_NR x ln((15 + 5) / 5) = 0.65 s (SBVS204G eq. 5), with C508 on U502 the
    # two rails together (0.65 / 0.56 s) and settled before the jack relays close (0.71 s from
    # MAINS_REQ), inside the firmware's 2 s (timer_spec.md 4.1). With 10 uF it was 1.39 s and the -
    # rail 12 s: GUASTO at every power-up. Not 1 uF: ~9.6 mF downstream (C505, the audio board's
    # 800.8 uF and the eight 1000 uF cells) would put U501 in current limit, 1.0 A and 16 W.
    # The noise bound of ADR-020 is drawn at C_NR 1 uF (fig. 5-1): it still holds.
    cap("4.7u", "C507", NR_P, GND)
    cap("10u", "C509", RAW_PR, GND)
    cap("10u", "C511", VP_REG, GND)  # at the pin (ADR-093)
    # D515, ADR-093: the series diode, 0.095 W at regime (SB340 on its leads' copper: +3 C)
    d = part("Device", "D_Schottky", "SB340", "D515", FP_DO201)
    d[2] += VP_REG                   # A
    d[1] += VP                       # K
    cap(C_HOLD, "C505", VP, GND, FP_CP16, polar=True)
    # D510: the datasheet says nothing on reverse current (no "revers*" in
    # SBVS204G, L41a): a Schottky OUT -> IN keeps OUT from rising above IN if
    # the raw side collapses first. ADR-093: behind D515 only C511 (10 uF) is
    # left on OUT, and D510 + D513 (two SB340 in parallel, 0.28 V at 0.22 A,
    # the worst of ADR-074's rows) discharge it; the pin side of R550 (ADR-092).
    for ref in ("D510", "D513"):
        d = part("Device", "D_Schottky", "SB340", ref, FP_DO201)
        d[2] += VP_REG
        d[1] += RAW_PR

    # U502, - rail. TPS7A3301, adjustable (vendor/ldo_regulator/ti/TPS7A3301/
    # tps7a33.pdf, SBVS169D): VREF = -1.175 V typ, VOUT = VREF (1 + R1 / R2)
    # (Eq. 2) = -1.175 x 13.0 = -15.28 V at the pin since ADR-093 (-15.04 V with 118k before);
    # divider current 117 uA > 5 uA;
    # 10 nF FB -> OUT as recommended (pin table); EN to IN allowed ("|VEN| <=
    # |VIN|"); the THERMAL PAD IS INTERNALLY GND (pin table) - L41a's first
    # draft had it on IN, i.e. RAW_M shorted to ground on the board.
    # ADR-092 (L45d2b2a): R551, 4.7 ohm, as R550 on the + rail - U502 2.38 -> 1.91 W at mains
    # +10 % (137 -> 122 C with 60 C of air), 0.46 W in R551, the headroom at mains -10 % 2.79 ->
    # 1.32 V; EN, C510 and D511 on the pin's side, RAW_MR.
    RAW_MR = Net("RAW_MR")
    r = part("Device", "R", "4.7", "R551", FP_R_2W)
    r[1] += RAW_MR
    r[2] += RAW_M
    # ADR-093 (L45d2b2b1, ADR-074): as U501 - OUT is VMINUS_REG, D516 (SB340) carries it to
    # VMINUS, the divider and C512 on the pin. SBVS169D p. 5: OUT to IN no lower than -0.3 V; in
    # ADR-074's rows the hold-up can no longer pull IN above OUT through D511 (68 A and 3.9 V before,
    # with C510 shorted), only C512's 10 uF can: 0.28 V at the worst.
    VM_REG = Net("VMINUS_REG")
    u = part("Regulator_Linear", "TPS7A3301RGW", "TPS7A3301 -15.3V", "U502",
             FP_QFN)
    u["15"] += RAW_MR
    u["16"] += RAW_MR
    u["13"] += RAW_MR                # EN
    u["21"] += GND                   # thermal pad = GND (SBVS169D pin table)
    u["1"] += VM_REG
    u["20"] += VM_REG
    u["7"] += GND
    FB_M = Net("FB_M")
    u["3"] += FB_M
    # ADR-093: 120k, -1.175 x (1 + 120 / 10) = -15.28 V at the pin, the rail ~-14.97 V behind D516;
    # the divider on the pin, not on the rail (ADR-096)
    res("120k", "R501", VM_REG, FB_M)
    res("10k", "R502", FB_M, GND)
    cap("10n", "C513", VM_REG, FB_M)  # feed-forward, noise
    NR_M = Net("NR_M")
    u["14"] += NR_M
    # C508, ADR-091 (L45d2b2a, NC-063): 470 nF. t_SS = 1.2 ms per nF = 0.56 s (SBVS169D eq. 1),
    # with C507 the two rails together; with 10 uF it was 12 s, and above the 1 uF that SBVS169D
    # recommends for C_NR. The noise bound of ADR-020 is drawn at 10 nF (fig. 22): it still holds.
    cap("470n", "C508", GND, NR_M)
    cap("10u", "C510", GND, RAW_MR)
    cap("10u", "C512", GND, VM_REG)  # at the pin (ADR-093)
    # D516, ADR-093: the series diode, the rail's current from VMINUS into the pin, 0.098 W
    d = part("Device", "D_Schottky", "SB340", "D516", FP_DO201)
    d[2] += VM                       # A
    d[1] += VM_REG                   # K
    cap(C_HOLD, "C506", GND, VM, FP_CP16, polar=True)
    # D511: Abs Max "OUT pin to IN pin -0.3 V" (SBVS169D p. 5): IN must not
    # rise above OUT by more than a Schottky's drop. ADR-093: D511 + D514, two
    # SB340 in parallel, on C512 alone; the pin's side of R551 (ADR-092).
    for ref in ("D511", "D514"):
        d = part("Device", "D_Schottky", "SB340", ref, FP_DO201)
        d[2] += RAW_MR
        d[1] += VM_REG

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
    d = part("Device", "D_Schottky", "1N5819", "D512", FP_DO41)   # as D510 was before ADR-093
    d[2] += VREG
    d[1] += RAW_V
    # V5, the logic: MCP1703A-5002, ~2 uA quiescent, for the standby budget.
    # ADR-094 (L45d2b2b2, ADR-075): TWO in series, U504 then U512, through V5_PRE. U504 with IN
    # shorted to OUT put VRELAY_REG on V5: 12.0 V on the ATtiny3216 (6.0 V absolute maximum,
    # DS40002205A Table 36-1). With two, either shorted leaves the other regulating: V5 5.000 V at
    # the three mains levels, the working one at 0.027 W. U512 runs in dropout, V5 ~4.98 V (650 mV
    # max at 250 mA, DS20005122B p4: ~16 mV at the logic's few mA); +2 uA in standby. ADR-075's
    # zener with a resettable fuse would take ~6 W for up to 0.2 s and not hold V5 under 6.0 V.
    V5_PRE = Net("V5_PRE")
    u = part("Regulator_Linear", "MCP1703Ax-500xxDB", "MCP1703A-5002",
             "U504", "Package_TO_SOT_SMD:SOT-223-3_TabPin2")
    u["1"] += VREG
    u["2"] += RET
    u["3"] += V5_PRE
    cap("1u", "C524", VREG, RET)
    cap("1u", "C536", V5_PRE, RET)    # U504's output, U512's input (>= 1 uF, MCP1703A)
    u = part("Regulator_Linear", "MCP1703Ax-500xxDB", "MCP1703A-5002",
             "U512", "Package_TO_SOT_SMD:SOT-223-3_TabPin2")
    u["1"] += V5_PRE
    u["2"] += RET
    u["3"] += V5
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
    # ~1.2 mA through the shunt. ADR-094: 2k as two 1k in series (R503 + R553). One 2k shorted put
    # V5 on the LM4040 - 0.25 A, 0.62 W against its 20 mA / 0.22 W with 60 C of air, U504 at its
    # limit (2.4 W) and the logic at ~2.5 V; with one 1k shorted, 2.2 mA
    VREF_R = Net("VREF_R")
    res("1k", "R503", V5, VREF_R)
    res("1k", "R553", VREF_R, VREF)
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
    # ADR-094: 22k as two 11k (R510 + R554). One 22k shorted put RECT_V (~17 V peak) on Q504's base:
    # 4.8-7.6 W in a BC847 (0.18 W with 60 C of air); with one 11k shorted, < 1 mW
    MB_R = Net("MD_B_R")
    res("11k", "R510", RECT_V, MB_R)
    res("11k", "R554", MB_R, MB)
    res("4.7k", "R511", MB, RET)          # on above ~4 V of RECT_V
    qd = part("Transistor_BJT", "BC847", "BC847", "Q504", FP_SOT23)
    qd[1] += MB
    qd[2] += RET
    qd[3] += MD
    # ADR-094: R_MD as two halves (R512 + R555). One R_MD shorted let Q504 pull V5 down at each
    # half-wave through U504's limit (133-149 C in Q504 with the bench's beta of 100; a BC847B's
    # higher gain takes more); with one half shorted, < 0.3 mW. The time constant is the sum
    MD_R = Net("MD_R")
    res(R_MD_HALF, "R512", V5, MD_R)
    res(R_MD_HALF, "R555", MD_R, MD)
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
    sink("Q501", MUTE_CMD, MUTE_G, RET, VRELAY, "CLAMP_MUTE", "D506", "D530", "D507")
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
    sink("Q502", PERMIT_CMD, PERMIT_G, RET, VRELAY, "CLAMP_PERMIT", "D508", "D531",
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
    # PA1 (17), PA3 (19), PA4 (2): the SPI to the LDR drive's DAC until
    # L47c1; open since ADR-062 removed it (ERC lists them). PA1 read the
    # DC detector's line DC_FLT in L45d2b1 (ADR-072, with D525-D527, R548,
    # R549, C535); open again since L60b, the detector gone (ADR-081). The firmware
    # (L47c2a, the user's choice) leaves every open pin an input with its
    # digital input buffer disabled (ISC = INPUT_DISABLE, DS40002205A
    # sec. 16.3.1): firmware/preamp_timer/spec/timer_spec.md sec. 2, checked
    # against this netlist by the host test pin_liberi.
    mcu["11"] += MUTE_REQ              # PB0
    mcu["10"] += PERMIT_REQ            # PB1
    mcu["9"] += MAINS_REQ              # PB2
    mcu["8"] += VRELAY_EN              # PB3
    mcu["12"] += FRONT_IN              # PC0
    mcu["13"] += SW3_IN                # PC1
    # PC3 (15) is spare, left open on purpose (ERC lists it); input buffer
    # disabled like the others (L47c2a).
    # The analog reads (ADC0: AIN2 PA2, AIN5-7 PA5-7, AIN8 PB5, AIN9 PB4):
    # which supervisor fired, so the firmware can tell a mains hole the rails
    # rode through from a fault with the mains present (ADR-048 point 5).
    # PB4 (7) and PA2 (18) read the two LED currents of the LDR drive until
    # L47c1; open since ADR-062 removed it, input buffer disabled (L47c2a).
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

    # ================= the harnesses to the audio board (check_psu_harness.py)
    # J1 on seven pins since L60b (ADR-082 point 2, ADR-083): each rail and
    # the ground on two pins and two wires, VRELAY on pin 7. J4 on three
    # again: its pin 4, DC_FLT (L45d2b1), went with the detector (ADR-081).
    header("POWER", "J1", [VP, VP, GND, GND, VM, VM, VRELAY])
    header("RLY_RET", "J2", [RET])
    header("MUTE_TIMER", "J4", [MUTE_CMD, PERMIT_CMD, MUTE_SW])

    # ERC, explained (L41a): "POWER-OUT connected to POWER-OUT" on VPLUS and
    # VRELAY_REG is the KiCad symbol's two OUT pins (1, 20) of ONE TPS7A4701,
    # both typed power_out, which the datasheet wants joined; "insufficient
    # drive" on RAW_P / RAW_M / RAW_V / RLY_RET is a bridge output (passive
    # pins) feeding a power_in - L41b1 adds the ground pins of U508-U511 to
    # the RLY_RET list, same cause. Unconnected: the ANY-OUT pins (above) and
    # the micro's spare PC3. L41b1: 21 warnings, the same 2 "errors". L47c1
    # (ADR-062): U510 / U511 are gone with their two "insufficient drive",
    # and the micro's PA1, PA2, PA3, PA4 and PB4 are unconnected too: 24
    # warnings. L45d2b1: PA1 read DC_FLT, 23. L60b (ADR-081): PA1 open
    # again, 24 warnings and the same 2 "errors" (read from the run).
    # ADR-093 (L45d2b2b1): U501's OUT pins are on VPLUS_REG now, so the first
    # "error" is there; its ANY-OUT pins 11 and 12 are grounded: 22 warnings.
    # ADR-094 (L45d2b2b2): U512's ground pin on RLY_RET, "insufficient drive" as U504's: 23 warnings,
    # the same 2 "errors" (read from the run).
    try:
        ERC()
    except Exception as e:  # noqa: BLE001
        print("SKiDL ERC raised:", e)

    netpath = os.environ.get(
        "PSU_NET_OUT", os.path.join(REPO, "circuits", "preamp", "psu.net"))
    generate_netlist(file_=netpath, tool="kicad10")
    print("KiCad netlist ->", netpath)
