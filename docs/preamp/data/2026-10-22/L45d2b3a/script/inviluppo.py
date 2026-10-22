#!/usr/bin/python3
"""L45d2b3a: the envelope of the rail form's phase margin (anello.py over a grid).

The pin form is 90 degrees by construction in the generic model (the pin is driven, T = wc / s):
one row per rail and fc is kept as the control.

Grid (each value a declared assumption, the parts are not chosen yet):
  fc         10k 30k 100k 300k 1M  - the regulator's own crossover, unknown: TI's model has a 1.6 us
                                     pole (~100 kHz) that no known case of the datasheet confirms;
  esr_hold   10 20 30 60 mOhm      - 2200 uF: polymer-like to generic; L45d2b2b1's bench has 30;
  esr_audio  0.05 0.2 ohm per 100 uF - ADR-056's careful value and a generic electrolytic;
  cavo       none / 20 mOhm + 200 nH;
  i          the rail's load (carico.txt of L45d2b2b1: 303.373 / 311.539 mA), 0.1 A, 0.03 A;
  temp       0 25 60 C             - the diode's rd = N Vt / I moves with it.

usage: inviluppo.py <out dir> <csv>
"""
import itertools
import os
import subprocess
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
out_dir, csv = sys.argv[1], sys.argv[2]

RAIL = {"piu": ("si", 0.303373), "meno": ("no", 0.311539)}
FC = (10e3, 30e3, 100e3, 300e3, 1e6)
ESR_HOLD = (0.01, 0.02, 0.03, 0.06)
ESR_AUDIO = (0.05, 0.2)
CAVO = (("0", "0"), ("0.02", "200n"))
I_ALTRI = (0.1, 0.03)
TEMP = (0, 25, 60)

righe = ["rail,forma,fc_Hz,esr_hold_ohm,esr_audio_ohm,r_cavo_ohm,l_cavo_H,i_A,temp_C,incroci,pm_min_deg"]


def corri(tag, rail, forma, fc, eh, ea, rc, lc, i, t):
    celle = RAIL[rail][0]
    r = subprocess.run(["/usr/bin/python3", "-I", os.path.join(QUI, "anello.py"), out_dir, tag,
                        "forma=" + forma, "fc=%g" % fc, "esr_hold=%g" % eh, "esr_audio=%g" % ea,
                        "r_cavo=" + rc, "l_cavo=" + lc, "i=%g" % i, "temp=%g" % t, "celle=" + celle],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(r.stdout + r.stderr)
    _, incroci, pm = r.stdout.rstrip("\n").split("\t")
    righe.append("%s,%s,%g,%g,%g,%s,%s,%g,%g,%s,%s" % (rail, forma, fc, eh, ea, rc, lc, i, t,
                                                        incroci.replace(",", ";"), pm))


n = 0
for rail in RAIL:
    for fc in FC:
        corri("%s_pin_%g" % (rail, fc), rail, "pin", fc, 0.03, 0.05, "0", "0", RAIL[rail][1], 25)
    for fc, eh, ea, (rc, lc), i, t in itertools.product(FC, ESR_HOLD, ESR_AUDIO, CAVO,
                                                         (RAIL[rail][1],) + I_ALTRI, TEMP):
        n += 1
        corri("%s_rail_%d" % (rail, n), rail, "rail", fc, eh, ea, rc, lc, i, t)
open(csv, "w").write("\n".join(righe) + "\n")
print("righe %d" % (len(righe) - 1))
