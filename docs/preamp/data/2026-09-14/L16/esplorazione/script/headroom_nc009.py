#!/usr/bin/env python3
"""headroom_nc009.py - the headroom figure of NC-009, with ONE declared metric.

Input: the wrdata tables of spice/preamp/tb/tb_dc_headroom.cir (col0 = v(IN),
col1 = v(OUT), DC sweep -14..14 V step 0.05 V) for the 0 / +3 / +10 dB modes.

THE METRIC CHOSEN IN L16 (M1):
    linear limit  = the output at the edges of the window around 0 V in which
                    the local gain dVout/dVin stays within 1 % of its value at
                    0 V (the dossier's definition, re-implemented in
                    reports/2026-09-09-revisione-utente-dossier.md), the smaller
                    edge in magnitude, as a sine RMS (/ sqrt 2);
    required      = 2.7 V RMS (E6) x the MEASURED gain at 0 V x the MEASURED
                    attenuation of the trim (tb_trim.cir, with the 10 k
                    attenuator load);
    margin        = 20 log10(linear limit / required).
The two figures that circulated before, re-computed and LABELLED:
    M2 (ADR-015) true saturation vs the NOMINAL requirement 2.7 x 10^(G/20)
    M3 (dossier) the 1 % limit vs the NOMINAL requirement.

Usage: headroom_nc009.py <tb_dc_headroom.csv> <_3db.csv> <_10db.csv>
                         <trim -6 dB measured> <trim -12 dB measured>
"""
import csv
import math
import sys

E6 = 2.7


def load(path):
    with open(path) as f:
        r = csv.reader(f)
        next(r)
        rows = [(float(a[0]), float(a[1])) for a in r]
    assert len(rows) > 100, f"{path}: {len(rows)} righe"
    return rows


def analyse(rows):
    vin = [x for x, _ in rows]
    vout = [y for _, y in rows]
    n = len(rows)
    i0 = min(range(n), key=lambda i: abs(vin[i]))
    g = [(vout[i + 1] - vout[i - 1]) / (vin[i + 1] - vin[i - 1])
         for i in range(1, n - 1)]
    g0 = g[i0 - 1]
    lo = hi = i0 - 1
    while lo - 1 >= 0 and abs(g[lo - 1] - g0) / abs(g0) <= 0.01:
        lo -= 1
    while hi + 1 < len(g) and abs(g[hi + 1] - g0) / abs(g0) <= 0.01:
        hi += 1
    v_lo, v_hi = vout[lo + 1], vout[hi + 1]
    lin_rms = min(abs(v_lo), abs(v_hi)) / math.sqrt(2)
    sat_rms = min(abs(max(vout)), abs(min(vout))) / math.sqrt(2)
    return g0, (vin[lo + 1], vin[hi + 1]), (v_lo, v_hi), lin_rms, sat_rms


def db(x):
    return 20 * math.log10(x)


paths = sys.argv[1:4]
trim = {"0": 0.0, "-6": float(sys.argv[4]), "-12": float(sys.argv[5])}
for label, nominal_db, path in zip(("0 dB", "+3 dB", "+10 dB"),
                                   (0.0, 3.0, 10.0), paths):
    g0, win_in, win_out, lin, sat = analyse(load(path))
    print(f"\n== modo {label}: guadagno a 0 V {g0:.6f} ({db(abs(g0)):+.4f} dB)")
    print(f"   finestra all'1 %: v(IN) {win_in[0]:+.3f} .. {win_in[1]:+.3f} V, "
          f"v(OUT) {win_out[0]:+.4f} .. {win_out[1]:+.4f} V")
    print(f"   limite lineare {lin:.4f} V RMS, saturazione vera {sat:.4f} V RMS")
    for tpos, tdb in trim.items():
        req_meas = E6 * abs(g0) * 10 ** (tdb / 20)
        req_nom = E6 * 10 ** (nominal_db / 20) * 10 ** (int(tpos) / 20)
        print(f"   trim {tpos:>3} dB (misurato {tdb:+.3f}): richiesti "
              f"{req_meas:.4f} V RMS -> M1 {db(lin / req_meas):+.2f} dB | "
              f"M2 {db(sat / req_nom):+.2f} dB | M3 {db(lin / req_nom):+.2f} dB")
