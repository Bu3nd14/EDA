import subprocess, time
D = "/Users/roberto/.claude/jobs/c42646c7/tmp/s3/"
s = open(D + "seq_s8.cir").read()
head = s[: s.index(".control")]
ctl = """.control
alter rrgb = 0.1
alter rrg10b = 0.1
tran 10u 1.0 0 10u
meas tran vj max v(mainjack) from=0.8 to=1.0
meas tran vsj min v(sjm) from=0.8 to=1.0
meas tran vf1 max v(fixjack1) from=0.8 to=1.0
.endc
.end
"""
OPT = ".options reltol=1e-6 vntol=1e-6 abstol=1e-12"


def run(nome, opt):
    h = head.replace(OPT, opt)
    assert opt == OPT or h != head
    open(D + "iso3_%s.cir" % nome, "w").write(h + ctl)
    t0 = time.time()
    r = subprocess.run(["/opt/homebrew/bin/ngspice", "-b", D + "iso3_%s.cir" % nome], capture_output=True, text=True)
    t = r.stdout + r.stderr
    esito = [l.strip() for l in t.splitlines() if l.strip().startswith(("vj", "vsj", "vf1")) or "too small" in l]
    print("%-12s %5.0f s %s" % (nome, time.time() - t0, esito))


run("rel1e-5", ".options reltol=1e-5 vntol=1e-6 abstol=1e-12")
run("rel1e-4", ".options reltol=1e-4 vntol=1e-6 abstol=1e-12")
run("rel1e-5_ab9", ".options reltol=1e-5 vntol=1e-6 abstol=1e-9")
run("rel1e-6_gear", ".options reltol=1e-6 vntol=1e-6 abstol=1e-12 method=gear maxord=2")
