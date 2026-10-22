#!/usr/bin/python3
"""L45d2b3a: TI's U501 model (anello_ti.py, AC only) over inviluppo.py's network grid, both forms.
The + rail only: TI's TPS7A3301 model has no loop (V(OUT) = VREF V(OUT) / V(FB), no pole), so
U502 has no vendor number.

usage: inviluppo_ti.py <out dir> <csv>
"""
import itertools
import os
import subprocess
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
out_dir, csv = sys.argv[1], sys.argv[2]

ESR_HOLD = (0.01, 0.02, 0.03, 0.06)
ESR_AUDIO = (0.05, 0.2)
CAVO = (("0", "0"), ("0.02", "200n"))
CARICO = (0.303373, 0.1, 0.03)
TEMP = (0, 25, 60)

righe = ["forma,esr_hold_ohm,esr_audio_ohm,r_cavo_ohm,l_cavo_H,i_A,temp_C,incroci,pm_min_deg"]
n = 0
for forma in ("pin", "rail"):
    for eh, ea, (rc, lc), i, t in itertools.product(ESR_HOLD, ESR_AUDIO, CAVO, CARICO, TEMP):
        n += 1
        r = subprocess.run(["/usr/bin/python3", "-I", os.path.join(QUI, "anello_ti.py"), out_dir,
                            "ti_%s_%d" % (forma, n), "forma=" + forma, "esr_hold=%g" % eh,
                            "esr_audio=%g" % ea, "r_cavo=" + rc, "l_cavo=" + lc, "i=%g" % i,
                            "temp=%g" % t, "tr=no"], capture_output=True, text=True)
        if r.returncode != 0:
            raise SystemExit(r.stdout + r.stderr)
        _, incroci, pm = r.stdout.rstrip("\n").split("\t")
        righe.append("%s,%g,%g,%s,%s,%g,%g,%s,%s" % (forma, eh, ea, rc, lc, i, t, incroci, pm))
open(csv, "w").write("\n".join(righe) + "\n")
print("righe %d" % (len(righe) - 1))
