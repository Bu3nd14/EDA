#!/usr/bin/env python3
"""L41b2: the first guess of an iteration - pins as a healthy, settled supply shows them.

Solo stdlib. /usr/bin/python3 sano.py <out.txt> <tf> [--muto]

Writes a two-row wrdata-like file with the columns ponte.c reads: the front
on, SW3 at music (or mute), MUTE_G up when at music, the supervisors' nodes
at their nominal values, the sense pins at 0. ponte.c then holds the core's
preamble state from t0 to tf: that constant output is pass 0 of the
iteration (corri_seq.sh), which the circuit corrects from pass 1 on.
"""
import sys

out, tf = sys.argv[1], float(sys.argv[2])
muto = "--muto" in sys.argv
cols = ["time", "v(front_in)", "v(mute_sw_in)", "v(mute_g_in)", "v(adc_sup_p)", "v(adc_sup_m)",
        "v(adc_sup_vr)", "v(adc_md)", "v(adc_i_s)", "v(adc_i_p)"]
val = [0.0, 5.0 if muto else 0.0, 0.0 if muto else 5.0, 15 * 10 / 54.2, 1.13, 12 * 10 / 44, 0.5, 0.0, 0.0]
with open(out, "w") as f:
    f.write(" ".join(cols) + "\n")
    for t in (0.0, tf):
        f.write(" ".join("%.9e" % x for x in [t] + val) + "\n")
