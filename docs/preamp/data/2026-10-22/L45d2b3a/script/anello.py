#!/usr/bin/python3
"""L45d2b3a: the loop gain of a rail regulator, feedback on the pin or on the rail after the diode.

The regulator is GENERIC and single-pole: an integrator with crossover fc (when it senses its own pin)
and a source at the pin behind ro (open-loop output resistance, default 0). NOT a bound either way:
a real LDO adds the pole of its pass device with the pin's capacitance (less phase). TI's model
reads its ratio V(OUT) / V(SENSE) after its own 4 mOhm, a local loop T ~ b H / (s tau + ro / Z_pin)
that this generic regulator has not: 58.9 deg there against 43.9 here (ro 0) and 43.6 (ro 4 mOhm),
the nominal case of this lot. Which of the two is nearer the part, no curve of SBVS204G says.

The network is the rail's (ADR-093, psu.py; genera_tb_psu.py of L45d2b2b1 for the values):
  pin: C511 / C512 10 uF ceramic (ESR 5 mOhm);
  the series diode: SB340, D(Is=8.7e-5 N=1.47 Rs=0.0136) (Vishay 88719 fig. 3, read by eye);
  rail: C505 / C506 2200 uF at -20 % (ADR-046) with esr_hold;
  the cable to the audio board: r_cavo, l_cavo;
  the audio board: 8 x (100 uF with esr_audio + 100 nF); on the + rail also the eight RC cells,
  1000 uF behind 2 x 20 ohm each, lumped as 8000 uF behind 1.25 ohm (genera_tb_psu.py);
  the load: a current source (op-amps draw near-constant current: no damping, the careful case).
The - rail is the same circuit in small signal (D516 carries the load current forward, VMINUS ->
pin), without the RC cells.

Loop gain by voltage injection at the regulator's sense input (an ideal high-impedance input: the
injection is exact): V(s_in) = V(s_net) + Vinj, T = -V(s_net) / V(s_in).

usage: anello.py <out dir> <tag> forma=pin|rail fc=<Hz> esr_hold=<ohm> esr_audio=<ohm>
                 r_cavo=<ohm> l_cavo=<H> i=<A> temp=<C> celle=si|no [ro=<ohm>] [rete=reale|rc:<R>:<C>]
prints one line: tag, crossings (f, phase margin) and the worst margin.
"""
import math
import os
import subprocess
import sys

NGSPICE = "/opt/homebrew/bin/ngspice"

out_dir, tag = sys.argv[1], sys.argv[2]
p = dict(a.split("=", 1) for a in sys.argv[3:])
forma = p["forma"]
fc = float(p["fc"])
rete = p.get("rete", "reale")

righe = ["L45d2b3a loop gain %s" % tag,
         ".option temp=%s" % p.get("temp", "25"),
         ".model DSB340 D(Is=8.7e-5 N=1.47 Rs=0.0136)",
         # the regulator: integrator dVint/dt = 2 pi fc (VSET - V(s_in)), ideal source at the pin
         "VSET vset 0 15",
         "GINT 0 vint vset s_in %g" % (2 * math.pi * fc),
         "CINT vint 0 1",
         "RINT vint 0 1e15",
         "EPASS pass 0 vint 0 1",
         "RO pass pin %s" % (p.get("ro", "0") if float(p.get("ro", "0")) > 0 else "1e-9")]
if rete == "reale":
    righe += ["CPIN pin pin_e 10u", "RPIN pin_e 0 0.005",
              "D1 pin rail DSB340",
              "CHOLD rail hold_e {0.8*2200u}", "RHOLD hold_e 0 %s" % p["esr_hold"],
              "RCAVO rail cav %s" % p["r_cavo"], "LCAVO cav aud %s" % p["l_cavo"],
              "CAUD aud aud_e 800u", "RAUD aud_e 0 {%s/8}" % p["esr_audio"],
              "CAUDF aud 0 800n",
              "ILOAD aud 0 %s" % p["i"]]
    if p.get("celle", "no") == "si":
        righe += ["RCELLE aud celle 1.25", "CCELLE celle 0 8000u"]
    s_net = "pin" if forma == "pin" else "rail"
else:
    # the instrument's known case: one RC pole between pin and sense, T = (wc / s) / (1 + s R C)
    _, r, c = rete.split(":")
    righe += ["RK pin rail %s" % r, "CK rail 0 %s" % c]
    s_net = "pin" if forma == "pin" else "rail"
righe += ["VINJ s_in %s DC 0 AC 1" % s_net,
          ".control",
          "set wr_singlescale",
          "ac dec 200 1 100meg",
          "let t = -v(%s)/v(s_in)" % s_net,
          "wrdata %s.dat mag(t) ph(t)" % tag,
          ".endc", ".end"]
os.makedirs(out_dir, exist_ok=True)
cir = os.path.join(out_dir, tag + ".cir")
open(cir, "w").write("\n".join(righe) + "\n")
log = subprocess.run([NGSPICE, "-b", cir], cwd=out_dir, capture_output=True, text=True)
open(os.path.join(out_dir, tag + ".log"), "w").write(log.stdout + log.stderr)
if log.returncode != 0 or "Error" in log.stdout + log.stderr:
    raise SystemExit("ERRORE ngspice %s (vedi %s.log)" % (tag, tag))

f, mag, ph = [], [], []
for riga in open(os.path.join(out_dir, tag + ".dat")):
    v = riga.split()
    if len(v) < 3:
        continue
    try:
        f.append(float(v[0])); mag.append(float(v[1])); ph.append(float(v[2]))
    except ValueError:
        continue
# unwrap the phase (radians from ngspice's ph()) and cross |T| = 1
deg = [x * 180 / math.pi for x in ph]
for k in range(1, len(deg)):
    while deg[k] - deg[k - 1] > 180:
        deg[k] -= 360
    while deg[k] - deg[k - 1] < -180:
        deg[k] += 360
incroci = []
for k in range(1, len(f)):
    if (mag[k - 1] - 1) * (mag[k] - 1) <= 0 and mag[k - 1] != mag[k]:
        a = (1 - mag[k - 1]) / (mag[k] - mag[k - 1])
        fx = f[k - 1] * (f[k] / f[k - 1]) ** a
        px = deg[k - 1] + a * (deg[k] - deg[k - 1])
        # T = -V(net)/V(in) carries the loop's own inversion: phase margin = 180 + phase of (-T)
        # written as the phase of T itself, referred to -180 (T's phase starts at -90 for wc/s)
        pm = 180 + px
        while pm > 180:
            pm -= 360
        while pm < -180:
            pm += 360
        incroci.append((fx, pm))
peggiore = min(m for _, m in incroci) if incroci else float("nan")
print("%s\t%s\t%.2f" % (tag, " ".join("%.4g Hz %.2f deg" % x for x in incroci), peggiore))
