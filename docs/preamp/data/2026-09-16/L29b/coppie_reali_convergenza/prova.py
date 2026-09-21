import subprocess
D = "/Users/roberto/.claude/jobs/c42646c7/tmp/s3/"
s = open(D + "seq_s8.cir").read()
head = s[: s.index(".control")]
ctl = """.control
alter rrgb = 0.1
alter rrg10b = 0.1
op
print v(gsm,ssm) v(gjm,sjm) v(mainjack) v(mainc)
alter vti dc = -100
alter vtr dc = 1000
op
print v(gsm,ssm) v(gjm,sjm) v(np)
alter vti dc = 1000
alter vtr dc = 2000
tran 10u 0.5 0 10u
meas tran vj max v(mainjack) from=0.35 to=0.5
meas tran vc max v(main_a) from=0.35 to=0.5
.endc
.end
"""
open(D + "prova.cir", "w").write(head + ctl)
r = subprocess.run(["/opt/homebrew/bin/ngspice", "-b", D + "prova.cir"], capture_output=True, text=True)
t = r.stdout + r.stderr
for l in t.splitlines():
    if any(k in l for k in ("v(gsm", "v(gjm", "v(np", "v(main", "vj ", "vc ", "rror", "failed", "= ")):
        print(l)
