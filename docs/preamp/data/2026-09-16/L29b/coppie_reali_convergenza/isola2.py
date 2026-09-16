import subprocess
D = "/Users/roberto/.claude/jobs/c42646c7/tmp/s3/"
s = open(D + "seq_s8.cir").read()
head = s[: s.index(".control")]
ctl = """.control
alter rrgb = 0.1
alter rrg10b = 0.1
tran 10u 0.5 0 10u
meas tran vj max v(mainjack) from=0.35 to=0.5
meas tran vsj min v(sjm) from=0.35 to=0.5
.endc
.end
"""


def run(nome, h):
    open(D + "iso2_%s.cir" % nome, "w").write(h + ctl)
    r = subprocess.run(["/opt/homebrew/bin/ngspice", "-b", D + "iso2_%s.cir" % nome], capture_output=True, text=True)
    t = r.stdout + r.stderr
    esito = [l.strip() for l in t.splitlines() if l.strip().startswith(("vj", "vsj")) or "too small" in l]
    print("%-14s %s" % (nome, esito))


add = lambda txt: head.replace("RSJ2 SJ2 0 1G", "RSJ2 SJ2 0 1G\n" + txt)
run("c_1p", add("CSJM SJM 0 1p\nCSJ1 SJ1 0 1p\nCSJ2 SJ2 0 1p\nCSSM SSM 0 1p\nCSS1 SS1 0 1p\nCSS2 SS2 0 1p"))
run("gear", head.replace(".options reltol=1e-6 vntol=1e-6 abstol=1e-12", ".options reltol=1e-6 vntol=1e-6 abstol=1e-12 method=gear"))
run("rsj_1t", head.replace(" 0 1G\n", " 0 1T\n"))
run("solo_jM", "\n".join(l for l in head.splitlines() if not (l.split() and l.split()[0] in ("XJ1a", "XJ1b", "XJ2a", "XJ2b", "EJ1", "EJ2", "RSJ1", "RSJ2"))) + "\n")
