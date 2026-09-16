import subprocess, re
D = "/Users/roberto/.claude/jobs/c42646c7/tmp/s3/"
s = open(D + "seq_s8.cir").read()
head = s[: s.index(".control")]
ctl = """.control
alter rrgb = 0.1
alter rrg10b = 0.1
tran 10u 0.5 0 10u
meas tran vj max v(mainjack) from=0.35 to=0.5
.endc
.end
"""


def run(nome, h):
    open(D + "iso_%s.cir" % nome, "w").write(h + ctl)
    r = subprocess.run(["/opt/homebrew/bin/ngspice", "-b", D + "iso_%s.cir" % nome], capture_output=True, text=True)
    t = r.stdout + r.stderr
    esito = [l.strip() for l in t.splitlines() if l.strip().startswith("vj") or "too small" in l or "failed" in l]
    print("%-22s %s" % (nome, esito))


run("com_e", head)
# 1: senza sottosoglia (solo modello del costruttore dentro il wrapper)
run("senza_bsub", head.replace("\nBSUB", "\n*BSUB") if "BSUB" in head else head)
# 2: coppie sostituite da resistenze: serie 1m, derivazione 1G
lines = []
for l in head.splitlines():
    w = l.split()
    if w and w[0].startswith("XS") and w[0].endswith("a"):
        lines.append("R%s %s %s 1m" % (w[0], w[1], {"MAINC": "MAINJACK", "FIXC1": "FIXJACK1", "FIXC2": "FIXJACK2"}[w[1]]))
        continue
    if w and (w[0].startswith("XS") or w[0].startswith("XJ") or w[0].startswith("ES") or w[0].startswith("EJ") or w[0].startswith("RSS") or w[0].startswith("RSJ")):
        continue
    lines.append(l)
run("resistenze", "\n".join(lines) + "\n")
# 3: solo le serie reali, derivazioni tolte
lines = [l for l in head.splitlines() if not (l.split() and (l.split()[0].startswith("XJ") or l.split()[0].startswith("EJ") or l.split()[0].startswith("RSJ")))]
run("solo_serie", "\n".join(lines) + "\n")
