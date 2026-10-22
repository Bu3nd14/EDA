#!/usr/bin/python3
"""L45d2b3a: the loop gain and a load step of U501 with TI's model (the ngspice derivative,
models/ldo_regulator/tps7a4701_ngspice.lib), feedback on the pin or on the rail.

Same network as anello.py (C511, SB340, C505 at -20 % with esr_hold, cable, 800 uF with esr_audio
plus 800 nF, the RC cells, the load as a current source). U501's set point is the source's: 15.3 V on
the pin form (ANY-OUT 6P4V1 6P4V2 0P8V 0P2V 0P1V to ground), 15.0 V on the rail form (0P2V 0P1V open).
VIN 19 V (the pin side of R550 at mains nominal is ~19-20 V; the loop does not depend on it while out
of dropout), CNR 4.7 uF (C507).

Loop gain by voltage injection at SENSE (TI's SENSE is read by an ABM only: infinite impedance).
The load step: 0.303 -> 0.353 A in 1 us at 20 ms, and back at 40 ms.

usage: anello_ti.py <out dir> <tag> forma=pin|rail esr_hold= esr_audio= r_cavo= l_cavo= i= temp=
                    [celle=si|no] [tr=si|no]
"""
import math
import os
import subprocess
import sys

NGSPICE = "/opt/homebrew/bin/ngspice"
# the repo's root is six levels up (script, L45d2b3a, 2026-10-22, data, preamp, docs)
LIB = os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 6,
                   "models", "ldo_regulator", "tps7a4701_ngspice.lib")

out_dir, tag = sys.argv[1], sys.argv[2]
p = dict(a.split("=", 1) for a in sys.argv[3:])
forma = p["forma"]
s_net = "pin" if forma == "pin" else "rail"
# 0P1V 0P2V 0P4V 0P8V 1P6V 3P2V 6P4V1 6P4V2: 0 = to ground
p01, p02 = ("0", "0") if forma == "pin" else ("n01", "n02")
rete = ["CPIN pin pin_e 10u", "RPIN pin_e 0 0.005",
        "D1 pin rail DSB340",
        "CHOLD rail hold_e {0.8*2200u}", "RHOLD hold_e 0 %s" % p["esr_hold"],
        "RCAVO rail cav %s" % p["r_cavo"], "LCAVO cav aud %s" % p["l_cavo"],
        "CAUD aud aud_e 800u", "RAUD aud_e 0 {%s/8}" % p["esr_audio"],
        "CAUDF aud 0 800n"]
if p.get("celle", "si") == "si":
    rete += ["RCELLE aud celle 1.25", "CCELLE celle 0 8000u"]
testa = ["L45d2b3a TI loop %s" % tag,
         ".include %s" % os.path.abspath(LIB),
         ".option temp=%s" % p.get("temp", "25"),
         ".model DSB340 D(Is=8.7e-5 N=1.47 Rs=0.0136)",
         "VIN in 0 19",
         "XU501 %s %s n04 0 n16 n32 0 0 in 0 nr s_in in in pin pin TPS7A4701_TRANS" % (p01, p02),
         "CNR nr 0 4.7u", "CIN in 0 10u",
         # the model's ratio V(OUT) / V(SENSE) has V(OUT) = 0 as a fixed point too, and with a
         # current-source load the rail form's .op lands there (pin 0 V, rail -0.32 V): a nodeset
         # at the working values steers the solver, it does not change the circuit
         ".nodeset v(pin)=%s v(rail)=15 v(nr)=%s" % (("15.3", "15.3") if forma == "pin"
                                                     else ("15.3", "15"))] + rete

os.makedirs(out_dir, exist_ok=True)


def gira(nome, righe):
    cir = os.path.join(out_dir, nome + ".cir")
    open(cir, "w").write("\n".join(righe) + "\n")
    r = subprocess.run([NGSPICE, "-b", cir], cwd=out_dir, capture_output=True, text=True)
    open(os.path.join(out_dir, nome + ".log"), "w").write(r.stdout + r.stderr)
    if r.returncode != 0 or "Error" in r.stdout + r.stderr:
        raise SystemExit("ERRORE ngspice %s" % nome)
    return r.stdout


# the loop
gira(tag + "_ac", testa + ["ILOAD aud 0 %s" % p["i"], "VINJ s_in %s DC 0 AC 1" % s_net,
                           ".control", "set wr_singlescale", "op",
                           "print v(pin) v(rail)",
                           "ac dec 200 1 100meg",
                           "let t = -v(%s)/v(s_in)" % s_net,
                           "wrdata %s_ac.dat mag(t) ph(t)" % tag, ".endc", ".end"])
f, mag, deg = [], [], []
for riga in open(os.path.join(out_dir, tag + "_ac.dat")):
    v = riga.split()
    try:
        f.append(float(v[0])); mag.append(float(v[1])); deg.append(float(v[2]) * 180 / math.pi)
    except (ValueError, IndexError):
        continue
for k in range(1, len(deg)):
    while deg[k] - deg[k - 1] > 180:
        deg[k] -= 360
    while deg[k] - deg[k - 1] < -180:
        deg[k] += 360
incroci = []
for k in range(1, len(f)):
    if (mag[k - 1] - 1) * (mag[k] - 1) <= 0 and mag[k - 1] != mag[k]:
        a = (1 - mag[k - 1]) / (mag[k] - mag[k - 1])
        pm = 180 + deg[k - 1] + a * (deg[k] - deg[k - 1])
        while pm > 180:
            pm -= 360
        while pm < -180:
            pm += 360
        incroci.append((f[k - 1] * (f[k] / f[k - 1]) ** a, pm))

pm_min = min(m for _, m in incroci) if incroci else float("nan")
if p.get("tr", "si") == "no":
    print("%s\t%s\t%.2f" % (tag, " ".join("%.4g Hz %.2f deg" % x for x in incroci), pm_min))
    raise SystemExit(0)

# the load step on the rail (the injection source stays, at 0 V)
tr = gira(tag + "_tr", testa + [
    "ILOAD aud 0 PWL(0 %s 20m %s 20.001m {%s+0.05} 40m {%s+0.05} 40.001m %s 60m %s)"
    % ((p["i"],) * 6),
    "VINJ s_in %s DC 0" % s_net,
    ".control", "tran 1u 60m 0 1u",
    "meas tran v_prima find v(rail) at=19.9m",
    "meas tran v_min min v(rail) from=20m to=25m",
    "meas tran v_dopo find v(rail) at=39.9m",
    "meas tran v_max max v(rail) from=40m to=45m",
    "meas tran pin_pp pp v(pin) from=20m to=22m",
    "wrdata %s_tr.dat v(rail) v(pin)" % tag, ".endc", ".end"])
mis = {}
for riga in tr.splitlines():
    if "=" in riga and riga.split("=")[0].strip() in ("v_prima", "v_min", "v_dopo", "v_max", "pin_pp"):
        mis[riga.split("=")[0].strip()] = float(riga.split("=")[1].split()[0])
print("%s\t%s\t%.2f\trail %.4f V\tcalo %.2f mV\tritorno %.2f mV\tpin pp %.2f mV" % (
    tag, " ".join("%.4g Hz %.2f deg" % x for x in incroci),
    pm_min, mis["v_prima"],
    (mis["v_prima"] - mis["v_min"]) * 1e3, (mis["v_max"] - mis["v_dopo"]) * 1e3, mis["pin_pp"] * 1e3))
