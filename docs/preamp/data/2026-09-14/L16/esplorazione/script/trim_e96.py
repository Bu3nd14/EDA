#!/usr/bin/env python3
"""trim_e96.py - dimensioning of the common input trim (L16, ADR-027).

The ladder, one per channel, after the input selector:

    TRIM_IN --R1-- TAP6 --R2-- TAP12 --R3-- GND

and block A's R_IN (1 MOhm, gain_block.py) in parallel with whichever node
the trim relays select:

    0 dB    R_IN on TRIM_IN   Zin = (R1+R2+R3) || R_IN
    -6 dB   R_IN on TAP6      Zin = R1 + (R2+R3) || R_IN
    -12 dB  R_IN on TAP12     Zin = R1 + R2 + R3 || R_IN

Constraints (REQUIREMENTS "Nota su E3", ADR-011/ADR-015):
  - attenuation -6.0 and -12.0 dB within +/-0.1 dB, R_IN included;
  - DC Zin >= ZMIN in every position (the AC minimum over 20 Hz - 20 kHz is
    SIMULATED in tb_trim.cir; this script only picks candidates);
  - the lower the Thevenin resistance seen by block A, the lower the Johnson
    noise it injects (E5 is SIMULATED too - the kT figure printed here is a
    ranking aid, not a result).

Usage: /usr/bin/python3 trim_e96.py [ZMIN_kohm ...]
"""
import math
import sys

R_IN = 1e6
E96 = [1.00, 1.02, 1.05, 1.07, 1.10, 1.13, 1.15, 1.18, 1.21, 1.24, 1.27, 1.30,
       1.33, 1.37, 1.40, 1.43, 1.47, 1.50, 1.54, 1.58, 1.62, 1.65, 1.69, 1.74,
       1.78, 1.82, 1.87, 1.91, 1.96, 2.00, 2.05, 2.10, 2.15, 2.21, 2.26, 2.32,
       2.37, 2.43, 2.49, 2.55, 2.61, 2.67, 2.74, 2.80, 2.87, 2.94, 3.01, 3.09,
       3.16, 3.24, 3.32, 3.40, 3.48, 3.57, 3.65, 3.74, 3.83, 3.92, 4.02, 4.12,
       4.22, 4.32, 4.42, 4.53, 4.64, 4.75, 4.87, 4.99, 5.11, 5.23, 5.36, 5.49,
       5.62, 5.76, 5.90, 6.04, 6.19, 6.34, 6.49, 6.65, 6.81, 6.98, 7.15, 7.32,
       7.50, 7.68, 7.87, 8.06, 8.25, 8.45, 8.66, 8.87, 9.09, 9.31, 9.53, 9.76]
VALS = [round(m * 10 ** k, 3) for k in (3, 4, 5) for m in E96]
K_T = 4 * 1.380649e-23 * 300.0 * (20000 - 20)   # 4kTB, 300 K, 20 Hz - 20 kHz


def par(a, b):
    return a * b / (a + b)


def db(x):
    return 20 * math.log10(x)


def evaluate(r1, r2, r3, rs=0.0):
    """Attenuation (dB, incl. a source rs) and Zin for the three positions."""
    rows = {}
    z0 = par(r1 + r2 + r3, R_IN)
    rows[0] = (db(z0 / (z0 + rs)), z0, rs)          # Thevenin ~ source only
    low6 = par(r2 + r3, R_IN)
    z6 = r1 + low6
    rows[-6] = (db(low6 / z6 * z6 / (z6 + rs)), z6, par(r1 + rs, low6))
    low12 = par(r3, R_IN)
    z12 = r1 + r2 + low12
    rows[-12] = (db(low12 / z12 * z12 / (z12 + rs)), z12,
                 par(r1 + r2 + rs, low12))
    return rows


def search(zmin):
    found = []
    for r1 in VALS:
        if not 30e3 <= r1 <= 150e3:
            continue
        for r2 in VALS:
            if r2 > r1:
                continue
            for r3 in VALS:
                rows = evaluate(r1, r2, r3)
                a6, z6, _ = rows[-6]
                a12, z12, _ = rows[-12]
                if abs(a6 + 6.0) > 0.1 or abs(a12 + 12.0) > 0.1:
                    continue
                if min(rows[0][1], z6, z12) < zmin:
                    continue
                rth = max(rows[-6][2], rows[-12][2])
                found.append((rth, r1, r2, r3, rows))
    found.sort()
    return found


if __name__ == "__main__":
    zmins = [float(x) * 1e3 for x in sys.argv[1:]] or [100e3, 110e3, 120e3]
    for zmin in zmins:
        res = search(zmin)
        print(f"\n== ZMIN {zmin / 1e3:.0f} k: {len(res)} terne E96 ==")
        for rth, r1, r2, r3, rows in res[:8]:
            txt = "  ".join(
                f"{pos:>3} dB: {a:+.3f} dB Zin {z / 1e3:6.2f} k Rth {th / 1e3:5.2f} k"
                for pos, (a, z, th) in sorted(rows.items(), reverse=True))
            vn = math.sqrt(K_T * rth) * 1e6
            print(f"R1 {r1 / 1e3:g}k R2 {r2 / 1e3:g}k R3 {r3 / 1e3:g}k | {txt} "
                  f"| 4kTRB(Rth max) {vn:.2f} uV")
        if res:
            _, r1, r2, r3, _ = res[0]
            print("  con sorgente phono 430 ohm:",
                  {k: round(v[0], 3) for k, v in evaluate(r1, r2, r3, 430).items()})
