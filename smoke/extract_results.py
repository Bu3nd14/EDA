#!/usr/bin/env python3
"""
Post-process ngspice wrdata output (rc_tran_out.txt, rc_ac_out.txt) into
CSV + a JSON summary with physical-correctness checks against the
analytical RC step response and -3dB point.

Run with any python3 that has numpy (the SKiDL venv works):
  /Users/roberto/EDA/env/venv/bin/python3 /Users/roberto/EDA/smoke/extract_results.py
"""
import csv
import json
import math

import numpy as np

R, C = 1000.0, 100e-9
tau_theory = R * C
fc_theory = 1 / (2 * math.pi * R * C)

# --- Transient (step response / time constant check) ---
tran = np.loadtxt("rc_tran_out.txt")
t, vin, vout = tran[:, 0], tran[:, 1], tran[:, 3]
with open("rc_tran_results.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["time_s", "vin_V", "vout_V"])
    for i in range(0, len(t), 50):
        w.writerow([f"{t[i]:.6e}", f"{vin[i]:.6f}", f"{vout[i]:.6f}"])

checks = []
for mult in (1, 2, 3, 5):
    tt = mult * tau_theory
    idx = int(np.argmin(np.abs(t - tt)))
    theory = 1 - math.exp(-mult)
    checks.append(
        {
            "t_target_s": tt,
            "t_actual_s": float(t[idx]),
            "vout_sim_V": float(vout[idx]),
            "vout_theory_V": theory,
            "abs_error_V": abs(float(vout[idx]) - theory),
        }
    )

# --- AC (frequency response / -3dB point check) ---
ac = np.loadtxt("rc_ac_out.txt")
freq, vdb = ac[:, 0], ac[:, 1]
fc_sim = None
for i in range(len(vdb) - 1):
    if vdb[i] >= -3 >= vdb[i + 1]:
        f0, f1, v0, v1 = freq[i], freq[i + 1], vdb[i], vdb[i + 1]
        frac = (-3 - v0) / (v1 - v0)
        fc_sim = f0 * (f1 / f0) ** frac
        break

with open("rc_ac_results.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["freq_Hz", "vout_dB"])
    for i in range(len(freq)):
        w.writerow([f"{freq[i]:.6e}", f"{vdb[i]:.6f}"])

summary = {
    "fixture": "RC lowpass, R=1k, C=100n",
    "R_ohm": R,
    "C_farad": C,
    "tau_theory_s": tau_theory,
    "fc_theory_Hz": fc_theory,
    "fc_sim_Hz": fc_sim,
    "fc_error_pct": abs(fc_sim - fc_theory) / fc_theory * 100 if fc_sim else None,
    "transient_step_checks": checks,
    "ngspice_version": "47",
}
with open("rc_sim_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print(json.dumps(summary, indent=2))
