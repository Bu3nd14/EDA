"""Varianti del banco off.cir: quale fa convergere l'op, e l'AC della coppia aperta torna capacitiva?"""
import subprocess
D = "/Users/roberto/.claude/jobs/c42646c7/tmp/vom/"
base = open(D + "t5.cir").read()
var = {
    "base": base,
    "iled_1u": base.replace("ILED 0 LA DC 0", "ILED 0 LA DC 1u"),
    "rleak_la": base.replace("ILED 0 LA DC 0", "ILED 0 LA DC 0\nRLA LA 0 1MEG"),
    "rs_gnd": base.replace("RGS G S 1MEG", "RGS G S 1MEG\nRSG S 0 10MEG"),
    "va_dc": base.replace("VA A 0 DC 0 AC 1", "VA A 0 DC 1 AC 1"),
}
for k, s in var.items():
    open(D + "v_%s.cir" % k, "w").write(s)
    out = subprocess.run(["/opt/homebrew/bin/ngspice", "-b", D + "v_%s.cir" % k], capture_output=True, text=True)
    txt = out.stdout + out.stderr
    fail = "stepping failed" in txt
    x5 = [l for l in txt.splitlines() if l.startswith("x5 =")]
    print("%-10s op_fallito=%s  %s" % (k, fail, x5))
