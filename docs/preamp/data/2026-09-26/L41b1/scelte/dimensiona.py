#!/usr/bin/env python3
"""L41b1: the timer's hardware numbers, computed BEFORE they go into psu.py.

Solo stdlib. /usr/bin/python3 dimensiona.py  (prints; writes dimensiona.txt next to it)

Three pieces (ADR-048 point 6, ADR-049):
  1. D  - PERMIT_CMD released no earlier than D >= 10 ms after the timer's mute
     request falls, for ANY micro state: an RC on PERMIT_T, charged through
     diodes from MUTE_REQ and PERMIT_REQ, read by a comparator against VREF.
  2. D2 - the switch that takes VRELAY off the audio board in standby (NC-037)
     opens no earlier than D2 after PERMIT_G falls: a slower RC on VR_T,
     charged from PERMIT_T and from VRELAY_EN.
  3. the LDR drive - two exponential converters (one per string) from the
     MCP4822; the resistor network that maps the DAC onto the base of Q2, the
     floor with the DAC in reset (500 kOhm to ground, DS20002249B sec. 4.1.3),
     and the compliance of two LEDs in series at 20 mA (VTL5C4: 2.0 V max,
     1.65 V typ at 20 mA, vendor/optocoupler/excelitas/VTL5C3_VTL5C4).

Every figure here is a hand model; the circuit is simulated in ../deck/.
"""
import math
import os

OUT = []


def p(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    OUT.append(s)


K = 1.380649e-23
Q = 1.602176634e-19


def vt(tc):
    return K * (tc + 273.15) / Q


# ------------------------------------------------------------------ 1. D
p("== 1. D: PERMIT_T -> comparator vs VREF (ADR-045: D = 20 ms nominal, >= 10 ms)")
R_T, C_T = 332e3, 100e-9
VREF = 2.500
# the charge level: the micro's VOH (~V5 at microamps) minus a 1N4148 at the
# ~13 uA the RC draws in steady state (~0.45 V)
for name, voh, vf, vref, rk, ck in (("nominale", 5.00, 0.45, 2.500, 1.00, 1.00),
                                    ("minimo", 4.90, 0.55, 2.505, 0.99, 0.95),
                                    ("massimo", 5.05, 0.40, 2.495, 1.01, 1.05)):
    v0 = voh - vf
    d = R_T * rk * C_T * ck * math.log(v0 / vref)
    p("  %-9s V0 = %.2f V, VREF = %.3f V -> D = %.1f ms" % (name, v0, vref, d * 1e3))
p("  (C_T C0G +-5 %, R_T 1 %; MUTE_G's own fall, R513 + R_pd || R514 on 22 nF,")
p("   is subtracted in the bench: tau = 52 k x 22 nF = 1.1 ms with the micro high-Z)")

# ------------------------------------------------------------------ 2. D2
p("")
p("== 2. D2: VR_T charged from PERMIT_T (one diode below it), slower RC")
R_T2, C_T2 = 1.0e6, 100e-9
for name, voh, vf, vref, rk, ck in (("nominale", 5.00, 0.45, 2.500, 1.00, 1.00),
                                    ("minimo", 4.90, 0.55, 2.505, 0.99, 0.95)):
    v0 = voh - vf
    t_perm = R_T * rk * C_T * ck * math.log(v0 / vref)
    t_vr = R_T2 * rk * C_T2 * ck * math.log((v0 - vf) / vref)
    p("  %-9s PERMIT_G falls at %.1f ms, VR_G at %.1f ms -> D2 = %.1f ms" % (
        name, t_perm * 1e3, t_vr * 1e3, (t_vr - t_perm) * 1e3))
# worst for D2: PERMIT at its max, VR at its min
t_perm_max = R_T * 1.01 * C_T * 1.05 * math.log((5.05 - 0.40) / 2.495)
t_vr_min = R_T2 * 0.99 * C_T2 * 0.95 * math.log((4.90 - 0.55 - 0.55) / 2.505)
p("  corners crossed (PERMIT slowest, VR fastest): D2 >= %.1f ms" % ((t_vr_min - t_perm_max) * 1e3))

# ------------------------------------------------------------------ 3. LDR
p("")
p("== 3. the LDR drive (per string): Q1 base = VREF, I_ref = (V5 - VREF) / R_REF")
R_REF = 24.9e3
V5 = 5.0
I_REF = (V5 - VREF) / R_REF
p("  I_ref = %.1f uA (R_REF = %.1f k from V5; +-2 %% of V5 -> +-4 %% of I_ref, the"
  " top-end calibration of ADR-049 takes it out)" % (I_REF * 1e6, R_REF / 1e3))
TABLE = [("serie d=0", 20e-3), ("serie d=0.1", 0.2e-3), ("serie d=0.45", 4.5e-6),
         ("serie d=0.75 (ginocchio)", 0.19e-6), ("riposo / d>=0.8", 10e-9)]
TEMPS = (15, 25, 35, 45, 60)
p("  V_c = V(base Q2) - VREF needed, mV, per chassis temperature %s C:" % (TEMPS,))
need_lo, need_hi = 0.0, 0.0
for name, i in TABLE:
    row = [1e3 * vt(t) * math.log(i / I_REF) for t in TEMPS]
    need_lo, need_hi = min(need_lo, *row), max(need_hi, *row)
    p("    %-26s %s" % (name, "  ".join("%+7.1f" % x for x in row)))
p("  span needed: %+.1f .. %+.1f mV" % (need_lo, need_hi))

# the network: DAC pin --R_PD-- RET, DAC pin --R_A-- X --R_C-- VREF; buffer
# X -> base Q2. R_PD makes the reset state the board's, not the DAC's: a first
# draft without it (R_B 1.18 M from X to RET instead) put the floor anywhere
# from 0.0 to 90 nA across the DAC's "500 k typical" shutdown load.
R_A, R_C, R_PD = 100e3, 22.1e3, 100e3
DAC_FS = 4.095            # G = 2x, 2.048 V internal reference


def vx(vdac=None, rsh=None):
    """X with the DAC driving vdac, or in shutdown (rsh to ground at its pin)."""
    ga, gc = 1 / R_A, 1 / R_C
    if vdac is None:
        rpin = 1 / (1 / R_PD + 1 / rsh)
        ga = 1 / (R_A + rpin)
        return VREF * gc / (ga + gc)
    return (vdac * ga + VREF * gc) / (ga + gc)


slope = (vx(DAC_FS) - vx(0.0)) / DAC_FS
p("  network R_A %.0fk, R_C %.1fk, R_PD %.0fk at the DAC pin:" % (R_A / 1e3, R_C / 1e3,
                                                                 R_PD / 1e3))
p("    X(code 0) = %.4f V, X(full scale) = %.4f V, slope %.4f V/V -> 1 LSB = %.3f mV"
  % (vx(0.0), vx(DAC_FS), slope, slope * 1e3 * DAC_FS / 4096))
lsb_db = 20 * math.log10(math.exp(slope * DAC_FS / 4096 / vt(25)))
p("    1 LSB = %.3f dB of LED current at 25 C" % lsb_db)
p("    covers %+.0f .. %+.0f mV around VREF (needed %+.0f .. %+.0f)" % (
    1e3 * (vx(0.0) - VREF), 1e3 * (vx(DAC_FS) - VREF), need_lo, need_hi))
p("  the floor with the DAC in reset (outputs 500 k typ to ground):")
for rsh in (250e3, 500e3, 1e6):
    x = vx(None, rsh)
    cur = ["%.1f" % (1e9 * I_REF * math.exp((x - VREF) / vt(t))) for t in TEMPS]
    p("    R_shdn %4.0fk: X = %.4f V -> %s nA at %s C (never 0; below the 190 nA knee)"
      % (rsh / 1e3, x, ", ".join(cur), TEMPS))
p("  Thevenin at X: %.1f k -> with C_X = 1 uF, tau = %.0f ms (smooths DAC steps; the"
  " profile is 6 s)" % (1 / (1 / R_A + 1 / R_C) / 1e3,
                        1e3 * 1e-6 / (1 / R_A + 1 / R_C)))

p("")
p("== compliance at 20 mA, V5 = 4.90 V, LEDs at their 2.0 V max (two in series):")
drop = {"mirror emitter 10 ohm": 0.20, "mirror output Vce(sat), BC857BS at 20 mA": 0.25,
        "2 x LED (VTL5C4 max 2.0 V at 20 mA)": 4.00, "sense 10 ohm": 0.20}
for k, v in drop.items():
    p("    %-45s %.2f V" % (k, v))
p("    margin: %.2f V (>= 0: it fits on V5)" % (4.90 - sum(drop.values())))
p("  current limit: Q_f collector 56 ohm to RET, E node ~1.88 V -> ~%.0f mA max"
  % ((1.88 - 0.2) / 56 * 1e3))
p("")
p("== the VTL5C4 LED rating against the chassis (vendor datasheet, abs max @25 C):")
for t in (25, 35, 45, 52.2, 58, 60):
    imax = 40 - 0.9 * max(0, t - 30)
    p("    %5.1f C: LED max %.1f mA %s" % (t, imax, "< 20 mA of ADR-039" if imax < 20 else ""))

here = os.path.dirname(os.path.abspath(__file__))
open(os.path.join(here, "dimensiona.txt"), "w").write("\n".join(OUT) + "\n")
