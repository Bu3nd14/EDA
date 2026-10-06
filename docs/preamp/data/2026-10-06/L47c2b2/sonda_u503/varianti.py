src = "/Users/roberto/EDA/.claude/worktrees/L47c2b2/docs/preamp/data/2026-10-06/L47c2b2/seq/guasto_u503/tb_psu_seq_guasto_u503_g1.cir"
D = "/Users/roberto/.claude/jobs/88bb8a5c/tmp/sonda_u503/"
OPT = ".options reltol=1e-4 abstol=1e-10 vntol=1e-6 temp=25 method=gear gmin=1e-10"
VAR = {
    "rshunt": OPT + " rshunt=1e12",
    "trap": OPT.replace("method=gear", "method=trap"),
    "reltol": OPT.replace("reltol=1e-4", "reltol=1e-3"),
}
for k, o in VAR.items():
    s = open(src).read()
    assert s.count(OPT) == 1
    s = s.replace(OPT, o)
    s = s.replace("wrdata tb_psu_seq_guasto_u503_g1_out.txt", "wrdata %sout_%s.txt" % (D, k))
    open(D + "v_%s.cir" % k, "w").write(s)
print("ok")
