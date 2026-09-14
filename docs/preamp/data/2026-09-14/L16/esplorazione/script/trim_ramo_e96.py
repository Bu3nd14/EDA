#!/usr/bin/env python3
"""trim_ramo_e96.py - dimensioning of the common trim on the VARIABLE-output
branch only (L16, ADR-027; the user's decision "B" of 2026-09-14).

    block A OUT --R1-- TAP6 --R2-- TAP12 --R3-- GND

T1/T2 connect the top of the 10 k stepped attenuator (F4) to OUT (0 dB), TAP6
(-6 dB) or TAP12 (-12 dB). The fixed-output buffers hang on block A's OUT
BEFORE the trim, so they are not in this calculation.

What matters now (E3 no longer depends on the trim - block A sits in front):
  - attenuation -6.0 / -12.0 dB within +/-0.1 dB, WITH the 10 k attenuator
    loading the tap;
  - the Thevenin resistance at the attenuator top: it adds to the attenuator's
    own source impedance seen by block B, whose worst case becomes
    (10 k + R_th) / 4 instead of 2.5 k (V1, SIMULATED in tb_loop.cir);
  - the load on block A: Rtot || 10 k at 0 dB is the heaviest. It must stay
    far inside the class A current (15 mA bias; E6 2.7 V RMS = 3.82 V pk).
Noise is SIMULATED in tb_trim.cir; nothing here is a result.

Usage: /usr/bin/python3 trim_ramo_e96.py [ZLOAD_MIN_ohm ...]
"""
import math
import sys

R_ATT = 10e3
VPK = 2.7 * math.sqrt(2)
E96 = [1.00, 1.02, 1.05, 1.07, 1.10, 1.13, 1.15, 1.18, 1.21, 1.24, 1.27, 1.30,
       1.33, 1.37, 1.40, 1.43, 1.47, 1.50, 1.54, 1.58, 1.62, 1.65, 1.69, 1.74,
       1.78, 1.82, 1.87, 1.91, 1.96, 2.00, 2.05, 2.10, 2.15, 2.21, 2.26, 2.32,
       2.37, 2.43, 2.49, 2.55, 2.61, 2.67, 2.74, 2.80, 2.87, 2.94, 3.01, 3.09,
       3.16, 3.24, 3.32, 3.40, 3.48, 3.57, 3.65, 3.74, 3.83, 3.92, 4.02, 4.12,
       4.22, 4.32, 4.42, 4.53, 4.64, 4.75, 4.87, 4.99, 5.11, 5.23, 5.36, 5.49,
       5.62, 5.76, 5.90, 6.04, 6.19, 6.34, 6.49, 6.65, 6.81, 6.98, 7.15, 7.32,
       7.50, 7.68, 7.87, 8.06, 8.25, 8.45, 8.66, 8.87, 9.09, 9.31, 9.53, 9.76]
VALS = [round(m * 10 ** k, 3) for k in (2, 3, 4) for m in E96]


def par(a, b):
    return a * b / (a + b)


def evaluate(r1, r2, r3):
    """{pos: (att_dB, load_on_A_ohm, Rth_at_attenuator_top_ohm)}"""
    rows = {0: (0.0, par(r1 + r2 + r3, R_ATT), 0.0)}
    low6 = par(r2 + r3, R_ATT)
    rows[-6] = (20 * math.log10(low6 / (r1 + low6)), r1 + low6,
                par(r1, r2 + r3))
    low12 = par(r3, R_ATT)
    rows[-12] = (20 * math.log10(low12 / (r1 + r2 + low12)), r1 + r2 + low12,
                 par(r1 + r2, r3))
    return rows


def search(zload_min):
    found = []
    for r1 in VALS:
        if not 200 <= r1 <= 10e3:
            continue
        for r2 in VALS:
            if r2 > r1:
                continue
            for r3 in VALS:
                if r3 > r1:
                    continue
                rows = evaluate(r1, r2, r3)
                if abs(rows[-6][0] + 6.0) > 0.1 or abs(rows[-12][0] + 12.0) > 0.1:
                    continue
                if min(v[1] for v in rows.values()) < zload_min:
                    continue
                rth = max(v[2] for v in rows.values())
                found.append((rth, r1, r2, r3, rows))
    found.sort()
    return found


if __name__ == "__main__":
    for zl in [float(x) for x in sys.argv[1:]] or [1000.0, 1500.0, 2000.0]:
        res = search(zl)
        print(f"\n== carico minimo sul blocco A >= {zl:.0f} ohm: {len(res)} terne ==")
        for rth, r1, r2, r3, rows in res[:6]:
            txt = "  ".join(
                f"{p:>3} dB: {a:+.3f} dB carico {z:7.1f} ohm Rth {t:6.1f} ohm"
                for p, (a, z, t) in sorted(rows.items(), reverse=True))
            zmin = min(v[1] for v in rows.values())
            print(f"R1 {r1:g} R2 {r2:g} R3 {r3:g} | {txt} | Ipk {VPK / zmin * 1e3:.2f} mA "
                  f"| sorgente B max {(R_ATT + rth) / 4:.0f} ohm")
