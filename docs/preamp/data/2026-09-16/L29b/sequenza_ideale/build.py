"""Scratch L29b: sequenza serie graduale (3 s) + derivazione graduale al jack (Tj),
con capacita' da aperto sull'elemento in serie. Elemento IDEALE (stesse sorgenti B
di tb_v2_mute_graduale.cir). Non e' il deck versionato: serve a dire quanto lenta
deve essere la derivazione, prima di scegliere una tecnica."""
import sys
R = "/Users/roberto/EDA/.claude/worktrees/L29b"
OUT = "/Users/roberto/.claude/jobs/c42646c7/tmp/s2"
src = open(R + "/spice/preamp/tb/tb_v2_mute_graduale.cir").read().splitlines()[:181]
L = [ln.replace("@REPO@", R) for ln in src]
L[0] = "tb_seq_scratch.cir - L29b scratch: serie graduale + derivazione graduale, C_off"
L += [
    "CFM MAINC MAINJACK 2p",
    "CF1 FIXC1 FIXJACK1 2p",
    "CF2 FIXC2 FIXJACK2 2p",
    ".control",
    "set d = .dat",
    "save v(mainjack) v(fixjack1) v(fixjack2)",
    'echo "cella,file,variante,f_hz,amp,gm,rl,t_ins,t_rel,t_fine,tmax,tipo,rif_ins,rif_rel,t_grad" > %s/manifest.csv' % OUT,
    "alter rrgb = 0.1",
    "alter rrg10b = 0.1",
    "alter vphs dc = 1.5707963267948966",
    "alter rbym = 1e12", "alter rby1 = 1e12", "alter rby2 = 1e12",
    "alter rbcm = 220k", "alter rbc1 = 470k", "alter rbc2 = 470k",
    "alter vmhser dc = 0", "alter vmhjk dc = 0",
    "alter vtgser dc = 3",
]

TS = 3.0
TF = 11.2


def run(name, var, amp, ti_s, tr_s, ti_j, tr_j, tj, tf, tipo, rins="-", rrel="-", t_ins=1.0, t_rel=2.1, tg=0.0):
    return [
        "alter vamp dc = %s" % amp,
        "alter vtgjk dc = %s" % tj,
        "alter vtiser dc = %s" % ti_s, "alter vtrser dc = %s" % tr_s,
        "alter vtijk dc = %s" % ti_j, "alter vtrjk dc = %s" % tr_j,
        "tran 10u %s 0 10u" % tf,
        "wrdata %s/%s$d v(mainjack) v(fixjack1) v(fixjack2)" % (OUT, name),
        'echo "%s,%s.dat,%s,1000,%s,10,100k,%s,%s,%s,10e-6,%s,%s,%s,%s" >> %s/manifest.csv'
        % (name, name, var, amp, t_ins, t_rel, tf, tipo, rins, rrel, tg, OUT),
        "destroy all",
    ]


for cp in ("2p", "50p"):
    L += ["alter cfm = %s" % cp, "alter cf1 = %s" % cp, "alter cf2 = %s" % cp]
    c = cp.replace(".", "")
    # riferimenti: mai in mute, sempre in mute (serie aperta e derivazione chiusa da t=0)
    L += run("c%s_bmmai" % c, "c%s" % c, 3.818, 1000, 2000, 1000, 2000, 1, TF, "rif_mai", t_ins=1.0, t_rel=4.2)
    L += run("c%s_bmsempre" % c, "c%s" % c, 3.818, -10, 1000, -10, 1000, 1, TF, "rif_sempre")
    for tj in (0.02, 0.2, 1.0):
        ti, tr = 1.0, 1.0 + TS + tj + 0.1
        tf = tr + tj + TS + 2.0
        name = "c%s_bm_tj%g" % (c, tj * 1000)
        L += run(name, "c%s_tj%gms" % (c, tj * 1000), 3.818, ti, tr + tj, ti + TS, tr, tj, tf,
                 "evento", "c%s_bmsempre" % c, "c%s_bmmai" % c, ti, tr, TS + tj)
    if cp == "50p":
        L += run("c%s_lzmai" % c, "c%s" % c, 0, 1000, 2000, 1000, 2000, 1, 13.1, "rif_mai")
        L += run("c%s_lzsempre" % c, "c%s" % c, 0, -10, 1000, -10, 1000, 0.02, 13.1, "rif_sempre")
        tj = 0.02
        ti, tr = 1.0, 6.0
        L += run("c%s_lz_tj20" % c, "c%s_tj20ms" % c, 0, ti, tr + tj, ti + TS, tr, tj, tr + tj + TS + 2.0,
                 "evento", "c%s_lzsempre" % c, "c%s_lzmai" % c, ti, tr, TS + tj)
L += [".endc", ".end"]
open(OUT + "/seq.cir", "w").write("\n".join(L) + "\n")
