#!/usr/bin/python3
"""L45d2b3a: the + rail's impedance seen by the audio board (node aud, behind the cable) and on the
supply board (node rail), TI's U501 model, both forms, the nominal network of anello_ti.py
(esr_hold 30 mOhm, esr_audio 0.05 ohm per 100 uF, no cable, 0.303 A, 25 C, the RC cells).
An AC current of 1 A into the node: |V| is the impedance.

usage: zrail_ti.py <out dir> <csv> f1 f2 ...
"""
import os
import subprocess
import sys

NGSPICE = "/opt/homebrew/bin/ngspice"
# the repo's root is six levels up (script, L45d2b3a, 2026-10-22, data, preamp, docs)
LIB = os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 6,
                   "models", "ldo_regulator", "tps7a4701_ngspice.lib")
out_dir, csv = sys.argv[1], sys.argv[2]
FREQ = [float(x) for x in sys.argv[3:]]
os.makedirs(out_dir, exist_ok=True)

righe = ["forma,nodo," + ",".join("Z_%g_Hz_ohm" % f for f in FREQ)]
for forma in ("pin", "rail"):
    s_net = "pin" if forma == "pin" else "rail"
    p01, p02 = ("0", "0") if forma == "pin" else ("n01", "n02")
    for nodo in ("rail", "aud"):
        tag = "z_%s_%s" % (forma, nodo)
        deck = ["L45d2b3a rail impedance %s" % tag,
                ".include %s" % os.path.abspath(LIB),
                ".model DSB340 D(Is=8.7e-5 N=1.47 Rs=0.0136)",
                "VIN in 0 19",
                "XU501 %s %s n04 0 n16 n32 0 0 in 0 nr %s in in pin pin TPS7A4701_TRANS" % (p01, p02, s_net),
                "CNR nr 0 4.7u", "CIN in 0 10u",
                ".nodeset v(pin)=15.3 v(rail)=15 v(nr)=%s" % ("15.3" if forma == "pin" else "15"),
                "CPIN pin pin_e 10u", "RPIN pin_e 0 0.005",
                "D1 pin rail DSB340",
                "CHOLD rail hold_e {0.8*2200u}", "RHOLD hold_e 0 0.03",
                "RCAVO rail aud 1e-6",
                "CAUD aud aud_e 800u", "RAUD aud_e 0 {0.05/8}", "CAUDF aud 0 800n",
                "RCELLE aud celle 1.25", "CCELLE celle 0 8000u",
                "ILOAD aud 0 0.303373",
                "IZ 0 %s DC 0 AC 1" % nodo,
                ".control", "op"]
        for k, f in enumerate(FREQ):
            deck += ["ac lin 1 %g %g" % (f, f), "print mag(v(%s))" % nodo]
        deck += [".endc", ".end"]
        cir = os.path.join(out_dir, tag + ".cir")
        open(cir, "w").write("\n".join(deck) + "\n")
        r = subprocess.run([NGSPICE, "-b", cir], cwd=out_dir, capture_output=True, text=True)
        open(os.path.join(out_dir, tag + ".log"), "w").write(r.stdout + r.stderr)
        z = [float(x.split("=")[1]) for x in r.stdout.splitlines() if x.startswith("mag(v(")]
        if len(z) != len(FREQ):
            raise SystemExit("ERRORE %s" % tag)
        righe.append("%s,%s,%s" % (forma, nodo, ",".join("%.4g" % v for v in z)))
open(csv, "w").write("\n".join(righe) + "\n")
print("\n".join(righe))
