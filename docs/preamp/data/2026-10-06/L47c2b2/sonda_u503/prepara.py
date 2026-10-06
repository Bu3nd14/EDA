import sys
src = "/Users/roberto/EDA/.claude/worktrees/L47c2b2/docs/preamp/data/2026-10-06/L47c2b2/seq/guasto_u503/tb_psu_seq_guasto_u503_g1.cir"
D = "/Users/roberto/.claude/jobs/88bb8a5c/tmp/sonda_u503/"
for tf in sys.argv[1:]:
    s = open(src).read()
    assert s.count("tran 100u 3 0 20u uic") == 1
    s = s.replace("tran 100u 3 0 20u uic", "tran 100u %s 0 20u uic" % tf)
    s = s.replace("wrdata tb_psu_seq_guasto_u503_g1_out.txt", "wrdata %sout_%s.txt" % (D, tf))
    open(D + "d_%s.cir" % tf, "w").write(s)
print("ok")
