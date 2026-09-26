#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
psu.py - the supply board: the second PCB of P4 (ADR-010, ADR-048; L41a).

Source of truth for the supply's topology (AGENTS.md rule 2), as
preamp_audio.py is for the audio board. It realises P9 (ADR-046, as ADR-048
reads it) and the contracts written on the audio board next to J1, J3 and J4.

    rear IEC module (fuse + DOUBLE-POLE switch: off = mains off everything)
      |
      +-- F501 -- T2 (small toroid, ALWAYS on while the rear is on) -- D503 --+-- D504 -- C_V --[U503 12 V]-- VRELAY -+-[U504 5 V]-- V5 (logic)
      |                                                                      |                                 |
      |                                                                      +-- mains detector (Q504, U506 ch 1)|
      +-- K501 (DPST, coil on VRELAY) -- T1 (toroid 2x15 V 50 VA) -- D501 -+-- C501 --[U501 TPS7A4701]-- C505 -- VPLUS
                                                                          +-- C502 --[U502 TPS7A3301]-- C506 -- VMINUS
    supervisor U505: VPLUS < 13.5 V, |VMINUS| < 13.5 V   \
    mains detector U506 A: no half-wave for ~15 ms        -> pull MUTE_G low: Q501 off, MUTE_CMD released (mute)
    VRELAY supervisor U506 B: VRELAY < 11.0 V             /

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

WHAT IS DELIBERATELY NOT HERE (L41b)
------------------------------------
 - The microcontroller, the hardware delay D (PERMIT_CMD released no earlier
   than D after MUTE_CMD, ADR-048 point 6) and the LDR current drive (profile
   v4, ADR-039). They appear as the placeholder header J509 TIMER_IO, whose
   nets L41b drives. Until then PERMIT_CMD's gate and the LDR strings are
   driven only through that header.
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
    k["A1"] += VRELAY
    MAINS_D = Net("MAINS_COIL")
    k["A2"] += MAINS_D
    dk = part("Device", "D", "1N4148", "D505", FP_DO35)
    dk[2] += MAINS_D    # plain flyback: the mains relay's release time is
    dk[1] += VRELAY     # not in any budget (it drops >= 50 ms after the mute)
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
    u["1"] += VRELAY
    u["20"] += VRELAY
    u["3"] += VRELAY
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
    cap(C_VR_HOLD, "C523", VRELAY, RET, FP_CP16, polar=True)
    d = part("Device", "D_Schottky", "1N5819", "D512", FP_DO41)   # as D510
    d[2] += VRELAY
    d[1] += RAW_V
    # V5, the logic: MCP1703A-5002, ~2 uA quiescent, for the standby budget.
    u = part("Regulator_Linear", "MCP1703Ax-500xxDB", "MCP1703A-5002",
             "U504", "Package_TO_SOT_SMD:SOT-223-3_TabPin2")
    u["1"] += VRELAY
    u["2"] += RET
    u["3"] += V5
    cap("1u", "C524", VRELAY, RET)
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
    res(R_VR_TOP, "R522", VRELAY, NV)
    res(R_VR_BOT, "R523", NV, RET)
    cap("1n", "C526", NV, RET)
    cmp2["5"] += NV        # B +
    cmp2["6"] += VREF      # B -
    cmp2["7"] += MUTE_G
    cmp2["8"] += V5
    cmp2["4"] += RET
    cap("100n", "C519", V5, RET)

    # ================= the J4 commands (ADR-045, ADR-048 point 6)
    # MUTE_CMD: the timer asks through MUTE_REQ, but any comparator output
    # overrides it by pulling MUTE_G low; the pull-down makes a dead timer
    # (or none, as today) a mute. Active-for-music, ADR-046.
    res("10k", "R513", MUTE_REQ, MUTE_G)
    res("100k", "R514", MUTE_G, RET)
    sink("Q501", MUTE_CMD, MUTE_G, RET, VRELAY, "CLAMP_MUTE", "D506", "D507")
    # PERMIT_CMD: from the timer alone in L41a; L41b adds the hardware delay
    # D after MUTE_G (ADR-048 point 6) between PERMIT_REQ and PERMIT_G.
    res("10k", "R515", PERMIT_REQ, PERMIT_G)
    res("100k", "R516", PERMIT_G, RET)
    sink("Q502", PERMIT_CMD, PERMIT_G, RET, VRELAY, "CLAMP_PERMIT", "D508",
         "D509")
    # MUTE_SW (SW3 on the audio board pulls it to RLY_RET = music) and the
    # front power switch: inputs of the timer, pulled up to V5.
    res("100k", "R517", V5, MUTE_SW)
    res("100k", "R518", V5, FRONT_SW)
    header("POWER_SW", "J508", [FRONT_SW, RET])

    # ================= the harnesses to the audio board (check_psu_harness.py)
    header("POWER", "J1", [VP, GND, VM, VRELAY])
    header("RLY_RET", "J2", [RET])
    header("LDR_CMD", "J3", LDR)
    header("MUTE_TIMER", "J4", [MUTE_CMD, PERMIT_CMD, MUTE_SW])

    # ================= L41b's placeholder: the timer's I/O
    header("TIMER_IO", "J509",
           [V5, RET, MUTE_REQ, PERMIT_REQ, MAINS_REQ, MUTE_G, FRONT_SW,
            MUTE_SW] + LDR)

    # ERC, explained (L41a): "POWER-OUT connected to POWER-OUT" on VPLUS and
    # VRELAY is the KiCad symbol's two OUT pins (1, 20) of ONE TPS7A4701, both
    # typed power_out, which the datasheet wants joined; "insufficient drive"
    # on RAW_P / RAW_M / RAW_V / RLY_RET is a bridge output (passive pins)
    # feeding a power_in.
    try:
        ERC()
    except Exception as e:  # noqa: BLE001
        print("SKiDL ERC raised:", e)

    netpath = os.environ.get(
        "PSU_NET_OUT", os.path.join(REPO, "circuits", "preamp", "psu.net"))
    generate_netlist(file_=netpath, tool="kicad10")
    print("KiCad netlist ->", netpath)
