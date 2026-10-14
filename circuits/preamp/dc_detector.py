#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dc_detector.py - the DC detector on the blocks' outputs (ADR-072; L45d2b1).

Source of truth for the detector's topology (AGENTS.md rule 2). preamp_audio.py
calls dc_detector() once for the six outputs of the audio board; run on its own
this file writes spice/preamp/dc_detector.subckt, the SAME parts as a SPICE
subcircuit (spice_export.py), which the fault benches include.

WHAT IT DOES (ADR-072). When any of the six outputs - F1, F2 (the fixed
buffers, which also carry block A's DC) and B, per channel - stays outside a
window of about +-0.6 V on the same side for ~70 ms in a row, it pulls DC_FLT
(J4 pin 4) low. On the supply board that line opens the mute (MUTE_G), takes
VRELAY off this board (VR_G) and drops the toroid (MAINS_G), in hardware;
the timer reads it and stays off until the front switch (spec 4.6).

WHY PERSISTENCE AND NOT A FILTER (L45d2b1, data/2026-10-14/L45d2b1/studio/).
The jack is AC-coupled (tau ~1 s unloaded), so ~0.95 V of DC at a block's
output already keeps it above 0.87 V for more than P10's 100 ms (ADR-069): the
cut must come within ~95 ms for any DC from ~0.95 V up. A low-pass that sees
that also trips on the first half-cycle of a 20 Hz bass at 14 V (1 to 4
poles, 10-70 ms). In the band of E9 (>= 20 Hz) music has no DC: a periodic
signal crosses zero at least once per 50 ms. So each output has its own timer
that restarts from zero every time the output comes back inside the window:
    S_x  = (v + 2 VDP) / 4                    the output, moved to VDP / 2
    U_P  releases T_xP while S_x > VTHP       (v above +VT)
    U_M  releases T_xM while S_x < VTHM       (v below -VT)
    T    charges from VDP through R_T; the comparator holds it at ~0 V
    TMAX = the highest T, through a diode;  U_TRIP: TMAX > VDP / 2 => DC_FLT low
    U_POR  holds TMAX low for ~0.1 s after VDP appears (the rails' ramp)
T_HOLD 71.6 ms nominal, 62.7-81.6 ms at the corners; the cut <= 91.5 ms after
the fault for any DC from 0.81 V up; no trip on any periodic signal above
16 Hz (data/2026-10-14/L45d2b1/scelte/dimensiona.py, dimensiona.csv).

THE SUPPLY (ADR-072, choice 8). The + rail's wire open between the boards
leaves block B at the - rail: the detector must see it, so it cannot live on
VPLUS alone. VDP is the higher of VPLUS and VRELAY (two 1N4148W): 14.3 V, or
11.3 V from VRELAY. Everything sits between VDP and GND, with no negative
supply: the - rail's wire open (the blocks at the + rail) is seen too. The
window, the thresholds and the trip reference are fractions of VDP.

The detector is NOT in the signal path (ADR-022): each output sees 300k to
the shifting node and 634k back to VMINUS, ~0.2 uA of net DC with both rails
(R_COMP below: without it, 24 uA moved a faulty output that had lost its
drive, ADR-079).

Declared limits:
  - a subsonic signal (< 16 Hz) at more than ~0.6 V at an output can trip it
    (a warped record at full volume through the future phono stage);
  - a block clipping hard and long beyond E6 at high frequency can shift
    its own mean past the window (the bench's 1 kHz case, with the first
    3.5 ms filter); the report gives the measured edge;
  - for ~0.1 s after power-on it cannot trip (U_POR, above);
  - the detector itself can go blind (a dead comparator, an open line): a
    latent fault, the diagnosis's (L58, ADR-072 "Da riaprire se");
  - its comparator model is behavioural (the TLV1701 vendor model does not
    run in ngspice: vendor/comparator/ti/TLV1702/PROVENANCE.json).

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

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

FP_R = "Resistor_SMD:R_0805_2012Metric"
FP_C = "Capacitor_SMD:C_0805_2012Metric"
FP_C1206 = "Capacitor_SMD:C_1206_3216Metric"
FP_TSSOP14 = "Package_SO:TSSOP-14_4.4x5mm_P0.65mm"     # TLV1704 PW (SBOS589D)
FP_VSSOP8 = "Package_SO:VSSOP-8_3x3mm_P0.65mm"         # TLV1702 DGK (SBOS589D)
FP_SOD323 = "Diode_SMD:D_SOD-323"
FP_SOT23 = "Package_TO_SOT_SMD:SOT-23"

# ---- the numbers, each with the decision behind it ----------------------
# Every figure is computed in docs/preamp/data/2026-10-14/L45d2b1/scelte/
# dimensiona.py and simulated in ../banco/.
# The shift (ADR-072, choice 8: no negative supply): S = (v + 2 VDP) / 4,
# inside [0, VDP] for v from -15.3 to +15.3 V with VDP down to 11.3 V (1.85 V
# to 11.0 V). 0.1 %: a 1 % network would move S by ~0.3 V referred to v,
# half the window.
R_SH_V, R_SH_D, R_SH_G = "300k", "150k", "300k"
# The shift network sits at VDP / 2 = 7.2 V with the output at 0 V, so it pushes
# 7.2 V / 300k = 24 uA INTO the block's output. Into a healthy output (< 1 ohm)
# that is nothing; into a faulty one that has lost its drive (~150 kOhm,
# Q106 base-emitter shorted) it moved the output from -0.81 V to +2.9 V: the
# output crossed zero, the timer restarted, and P10 went from 66 to 122 ms on
# the main output (data/2026-10-14/L45d2b1/banco/, the first run of the
# faults). R_COMP takes the same current back to VMINUS: 15.05 V / 634k =
# 23.7 uA, so with both rails present the detector puts ~0 uA into an output
# (+0.2 uA nominal; -5.6 uA with VDP from VRELAY). With the - rail's wire open
# VMINUS goes to 0 and R_COMP does nothing: that case is seen on the + side.
R_COMP = "634k"
# The input filter: (300k || 150k || 300k) x 4.7n = 0.35 ms. It averages an
# oscillation of a faulty block (tens of kHz) and the noise, not the music:
# with 3.5 ms (L45d2b1's first draft) the B block clipping hard at 1 kHz,
# 2.3 dB beyond E6, was averaged into its own -1.1 V of asymmetry and
# tripped it (data/2026-10-14/L45d2b1/banco/, seno_1k_g10_clip).
C_SH = "4.7n"
# The thresholds and the trip reference get the SAME time constant as S
# (~51k x 6.8n = 0.35 ms): with 5 ms on them and 3.5 ms on S, the lags on a
# VDP that ramps at power-up differed by more than the window, and a
# comparator saw "outside" with every output at 0 V (the same bench).
C_REF = "6.8n"
# The window (ADR-072: "la soglia ... contro i 100 ms di P10"): VT = +-0.58 V
# at the output, 0.39-0.66 V at the corners (0.1 %, 5.5 mV of comparator
# offset x 4). Under the 0.81 V of the lowest-DC fault of L45b that P10
# fails (Q106_be on F1 / F2), above the blocks' own mV.
R_WIN_A, R_WIN_B = "100k", "4.12k"
# T_HOLD (ADR-072: "la costante di tempo ... contro i 100 ms di P10" and "la
# musica non deve farlo scattare"): 976k x 100n from ~0.35 V to VDP / 2 +
# one diode = 71.6 ms; 62.7 ms at the low corner, > the 50 ms of a period at
# 20 Hz; 81.6 ms at the high corner, so the cut is <= 91.5 ms after the fault
# with the relay's 3 ms. C_T is C0G: an X7R would lose tens of percent to
# bias and ageing (the reason psu.py's C_T is C0G too).
R_T, C_T = "976k", "100n"
# TMAX's return, so that it sits at 0 V with every timer reset; 10M is ~1 uA
# against the ~7 uA a timer still draws at VDP / 2.
R_TMAX = "10M"
# The trip reference: VDP / 2. Ratiometric: VDP from VRELAY changes T_HOLD
# by < 2 % (dimensiona.py).
R_REF = "100k"
# The line driver (an MMBT5551, already on this board with a manufacturer
# model, ADR-017): TRIP pulled up to VDP by 47k, 47k to the base, 10k
# base-emitter. It conducts only above TRIP = 3.7 V, so a VDP still below the
# comparators' 2.2 V cannot pull the line; 49 uA of base at VDP = 11.3 V
# against the ~1.9 mA of the supply board's side (pull-up + three gates).
R_TRIP_UP, R_TRIP_B, R_TRIP_BE = "47k", "47k", "10k"
# The power-on inhibit (the spare channel of the trip comparator): TMAX held
# low while POR < VDP / 2, i.e. for 1.43M x 100n x ln 2 = 99 ms after VDP
# appears. While the rails ramp the fixed outputs climb to +1.4...+4 V for
# 30-50 ms (block A finding its bias; the bench, accensione), close to
# T_HOLD's 62.7 ms floor. It ends before the jacks can close: on the
# supply's own power-up the rails are good ~34 ms after the toroid and the
# timer closes the jacks >= 150 ms after that (data/2026-10-12/
# L56-alimentatore/seq/accensione). A fault already there at power-up is
# seen ~T_HOLD after the inhibit. The diode resets POR as VDP falls, and
# keeps it from re-arming when VDP steps from VPLUS down to VRELAY.
R_POR, C_POR = "1.43M", "100n"


_ref = {"R": 950, "C": 950, "D": 950, "U": 950, "Q": 950}


def _next(p):
    _ref[p] += 1
    return f"{p}{_ref[p]}"


def _part(lib, name, value, prefix, fp):
    # tag = ref: a stable identity for SKiDL, as in psu.py (else a random tag per run)
    ref = _next(prefix)
    return Part(lib, name, value=value, footprint=fp, ref=ref, tag=ref)


def _r(val, a, b, fp=FP_R, tol=None):
    r = _part("Device", "R", val, "R", fp)
    if tol:
        r.fields["Tolerance"] = tol
    r[1] += a
    r[2] += b
    sx.spice_dev(r, "R", ["1", "2"], val)
    return r


def _c(val, a, b, fp=FP_C):
    c = _part("Device", "C", val, "C", fp)
    c[1] += a
    c[2] += b
    sx.spice_dev(c, "C", ["1", "2"], val)
    return c


def _d(a, k):
    d = _part("Device", "D", "1N4148W", "D", FP_SOD323)
    d["A"] += a
    d["K"] += k
    # D1N914: the 1N4148 model (models/diodes/1n4148.lib, limitations #20)
    sx.spice_dev(d, "D", ["A", "K"], "D1N914")
    return d


# TLV1704 (PW, TSSOP-14) has the LM2901 pinout exactly (SBOS589D pin table:
# 2OUT 1, 1OUT 2, V+ 3, 1IN- 4, 1IN+ 5, 2IN- 6, 2IN+ 7, 3IN- 8, 3IN+ 9,
# 4IN- 10, 4IN+ 11, V- 12, 4OUT 13, 3OUT 14): channel -> (out, in-, in+).
QUAD = (("2", "4", "5"), ("1", "6", "7"), ("14", "8", "9"), ("13", "10", "11"))
# TLV1702 (DGK) = LM2903: 1OUT 1, 1IN- 2, 1IN+ 3, V- 4, 2IN+ 5, 2IN- 6, 2OUT 7, V+ 8.
DUAL = (("1", "2", "3"), ("7", "6", "5"))


def _cmp(u, ch, pins, inp, inn, out, vdp, gnd, vcc_pin, vee_pin):
    o, m, p = pins
    u[p] += inp
    u[m] += inn
    u[o] += out
    # behavioural open-collector model CMPOC (the bench declares it): ports
    # in+ in- out V+ V-
    sx.spice_dev(u, "X", [p, m, o, vcc_pin, vee_pin], "CMPOC", suffix="ABCD"[ch])


def dc_detector(taps, vplus, vminus, vrelay, gnd, ret, dc_flt):
    """taps: [(tag, net)] - the six block outputs. dc_flt: J4 pin 4."""
    assert len(taps) == 6
    vdp = Net("DET_VDP")
    # ---- the supply: the higher of VPLUS and VRELAY (choice 8)
    _d(vplus, vdp)
    _d(vrelay, vdp)
    _c("1u", vdp, gnd, fp=FP_C1206)
    # ---- the window's thresholds, 0.1 %: VDP - A - VTHP - B - VTHM - A - GND
    vthp, vthm = Net("DET_VTHP"), Net("DET_VTHM")
    _r(R_WIN_A, vdp, vthp, tol="0.1%")
    _r(R_WIN_B, vthp, vthm, tol="0.1%")
    _r(R_WIN_A, vthm, gnd, tol="0.1%")
    _c(C_REF, vthp, gnd)
    _c(C_REF, vthm, gnd)
    # ---- the trip reference, VDP / 2
    ref = Net("DET_REF")
    _r(R_REF, vdp, ref)
    _r(R_REF, ref, gnd)
    _c(C_REF, ref, gnd)
    tmax = Net("DET_TMAX")
    _r(R_TMAX, tmax, gnd)

    # ---- the three quads: one output per channel pair (P, M)
    quads = []
    for _ in range(3):
        u = _part("Comparator", "LM2901", "TLV1704 (quad, open-collector)", "U",
                  FP_TSSOP14)
        u["3"] += vdp
        u["12"] += gnd
        _c("100n", vdp, gnd)
        quads.append(u)
    for i, (tag, out) in enumerate(taps):
        s = Net(f"DET_S_{tag}")
        _r(R_SH_V, out, s, tol="0.1%")
        _r(R_COMP, out, vminus)
        _r(R_SH_D, vdp, s, tol="0.1%")
        _r(R_SH_G, s, gnd, tol="0.1%")
        _c(C_SH, s, gnd)
        u = quads[i // 2]
        for side, (inp, inn) in (("P", (s, vthp)), ("M", (vthm, s))):
            ch = (i % 2) * 2 + (0 if side == "P" else 1)
            t = Net(f"DET_T_{tag}_{side}")
            _cmp(u, ch, QUAD[ch], inp, inn, t, vdp, gnd, "3", "12")
            _r(R_T, vdp, t)
            _c(C_T, t, gnd, fp=FP_C1206)
            _d(t, tmax)

    # ---- the trip: TMAX > VDP / 2 releases TRIP, the MMBT5551 pulls DC_FLT
    ut = _part("Comparator", "LM2903", "TLV1702 (dual, open-collector)", "U",
               FP_VSSOP8)
    ut["8"] += vdp
    ut["4"] += gnd
    _c("100n", vdp, gnd)
    trip = Net("DET_TRIP")
    _cmp(ut, 0, DUAL[0], tmax, ref, trip, vdp, gnd, "8", "4")
    # the power-on inhibit: POR below VDP / 2 sinks TMAX
    por = Net("DET_POR")
    _r(R_POR, vdp, por)
    _c(C_POR, por, gnd, fp=FP_C1206)
    _d(por, vdp)
    _cmp(ut, 1, DUAL[1], por, ref, tmax, vdp, gnd, "8", "4")
    _r(R_TRIP_UP, vdp, trip)
    b = Net("DET_B")
    _r(R_TRIP_B, trip, b)
    _r(R_TRIP_BE, b, ret)
    q = _part("Device", "Q_NPN", "MMBT5551", "Q", FP_SOT23)
    q["C"] += dc_flt
    q["B"] += b
    q["E"] += ret          # the line's return is the relays' (J2), not the audio ground
    sx.spice_dev(q, "Q", ["C", "B", "E"], "MMBT5551")
    return vdp


if __name__ == "__main__":
    sx.reset()
    VP, VM, VR = Net("VPLUS"), Net("VMINUS"), Net("VRELAY")
    GND, RET = Net("GND"), Net("RLY_RET")
    GND.drive = POWER
    FLT = Net("DC_FLT")
    taps = [(t, Net(t + "_OUT")) for t in ("F1L", "F2L", "BL", "F1R", "F2R", "BR")]
    dc_detector(taps, VP, VM, VR, GND, RET, FLT)
    try:
        ERC()
    except Exception as e:  # noqa: BLE001
        print("SKiDL ERC raised:", e)
    outdir = os.path.join(REPO, "spice", "preamp")
    sub = sx.subckt(
        "DCDET",
        [t + "_OUT" for t, _ in taps] + ["VPLUS", "VMINUS", "VRELAY", "RLY_RET", "DC_FLT"],
        gnd_names=("GND",),
        header=(
            "GENERATED by circuits/preamp/dc_detector.py - DO NOT HAND-EDIT.\n"
            "Ports: F1L_OUT F2L_OUT BL_OUT F1R_OUT F2R_OUT BR_OUT VPLUS VMINUS VRELAY RLY_RET DC_FLT\n"
            "(node 0 = the audio ground). DC_FLT is an open collector to RLY_RET.\n"
            "Models to include: D1N914 (models/diodes/1n4148.lib), MMBT5551\n"
            "(models/bjt_npn/mmbt5551.lib), and CMPOC - a BEHAVIOURAL open-collector\n"
            "comparator with ports in+ in- out V+ V-, declared by the bench (the\n"
            "TLV1701 vendor model does not run in ngspice)."
        ),
    )
    path = os.path.join(outdir, "dc_detector.subckt")
    with open(path, "w") as f:
        f.write(sub)
    print("SPICE subcircuit ->", path)
    print("device lines:", len([l for l in sub.splitlines() if l and not l.startswith(("*", "."))]))
