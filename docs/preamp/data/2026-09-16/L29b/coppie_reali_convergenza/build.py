"""Scratch L29b: coppie DMN6040SVT_SUB reali (serie + derivazione) con Vgs IDEALE da una
sola variabile di profondita' p(t). Misura quanto lenta deve essere la rampa di Vgs nella
finestra sottosoglia, per due pendenze ipotizzate, e prova l'inversione a meta' rampa.
NON e' il deck versionato. Il driver (VOM1271) e la sua dispersione non ci sono."""
import os
R = "/Users/roberto/EDA/.claude/worktrees/L29b"
OUT = "/Users/roberto/.claude/jobs/c42646c7/tmp/s3"
src = open(R + "/spice/preamp/tb/tb_v2_mute_graduale.cir").read().splitlines()[:181]

VON, VHI, VLO, F = 8.0, 2.2, 1.2, 0.05   # Vgs acceso, finestra lenta [VLO, VHI], tratti rapidi 50 ms
VTH = 2.0

base = []
for ln in src:
    ln = ln.replace("@REPO@", R)
    w = ln.split()
    if w and (w[0].startswith("BSER") or w[0].startswith("BJK") or w[0].startswith("RBY")):
        continue
    if w and w[0] in ("RBCM",):
        ln = "RBCM MAINC 0 220k"
    if w and w[0] in ("RBC1", "RBC2"):
        ln = "%s %s 0 470k" % (w[0], w[1])
    base.append(ln)
base[0] = "tb_seq_mosfet_scratch.cir - L29b scratch: coppie DMN6040SVT_SUB, Vgs ideale"
i = base.index(".include %s/spice/preamp/gain_block.subckt" % R)
base.insert(i + 1, ".include %s/models/mosfet_n/dmn6040svt.lib" % R)
base.insert(i + 2, ".include %s/models/mosfet_n/dmn6040svt_sottosoglia.lib" % R)


def elementi(s):
    L = [
        "* ---- profondita' del mute p(t) e le due Vgs (L29b) ----",
        "VTI NTI 0 DC 1000", "VTR NTR 0 DC 2000", "VTS NTS 0 DC 1", "VTJ NTJ 0 DC 1",
        "BPA NPA 0 V = min(max(min(time, V(NTR)) - V(NTI), 0), 0.2 + V(NTS) + V(NTJ))",
        "BP NP 0 V = max(V(NPA) - max(time - V(NTR), 0), 0)",
        "BVS VGSS 0 V = %g - %g*min(max(V(NP)/%g,0),1) - %g*min(max((V(NP)-%g)/V(NTS),0),1) - %g*min(max((V(NP)-%g-V(NTS))/%g,0),1)"
        % (VON, VON - VHI, F, VHI - VLO, F, VLO, F, F),
        "BVJ VGSJ 0 V = %g*min(max((V(NP)-%g-V(NTS))/%g,0),1) + %g*min(max((V(NP)-%g-V(NTS))/V(NTJ),0),1) + %g*min(max((V(NP)-%g-V(NTS)-V(NTJ))/%g,0),1)"
        % (VLO, 2 * F, F, VHI - VLO, 3 * F, VON - VHI, 3 * F, F),
    ]
    for u, c, j in (("M", "MAINC", "MAINJACK"), ("1", "FIXC1", "FIXJACK1"), ("2", "FIXC2", "FIXJACK2")):
        p = "params: vth=%g s=%g" % (VTH, s)
        L += [
            "XS%sa %s GS%s SS%s DMN6040SVT_SUB %s" % (u, c, u, u, p),
            "XS%sb %s GS%s SS%s DMN6040SVT_SUB %s" % (u, j, u, u, p),
            "ES%s GS%s SS%s VGSS 0 1" % (u, u, u),
            "RSS%s SS%s 0 1G" % (u, u),
            "XJ%sa %s GJ%s SJ%s DMN6040SVT_SUB %s" % (u, j, u, u, p),
            "XJ%sb 0 GJ%s SJ%s DMN6040SVT_SUB %s" % (u, u, u, p),
            "EJ%s GJ%s SJ%s VGSJ 0 1" % (u, u, u),
            "RSJ%s SJ%s 0 1G" % (u, u),
        ]
    return L


def cella(nome, var, amp, ti, tr, ts, tf, tipo, rins="-", rrel="-", tg=0.0, mti=None, mtr=None):
    return [
        "alter vamp dc = %s" % amp,
        "alter vti dc = %s" % ti, "alter vtr dc = %s" % tr,
        "alter vts dc = %s" % ts, "alter vtj dc = %s" % ts,
        "tran 10u %s 0 10u" % tf,
        "wrdata %s/%s$d v(mainjack) v(fixjack1) v(fixjack2)" % (OUT, nome),
        'echo "%s,%s.dat,%s,1000,%s,10,100k,%s,%s,%s,10e-6,%s,%s,%s,%s" >> %s/manifest.csv'
        % (nome, nome, var, amp, mti if mti is not None else ti, mtr if mtr is not None else tr, tf, tipo, rins, rrel, tg, OUT),
        "destroy all",
    ]


for s in (0.08, 0.12):
    tag = "s%d" % round(s * 100)
    L = base + elementi(s) + [
        ".control", "set d = .dat",
        "save v(mainjack) v(fixjack1) v(fixjack2)",
        "alter rrgb = 0.1", "alter rrg10b = 0.1", "alter vphs dc = 1.5707963267948966",
    ]
    if s == 0.08:
        L.insert(L.index(".control") + 1,
                 'echo "cella,file,variante,f_hz,amp,gm,rl,t_ins,t_rel,t_fine,tmax,tipo,rif_ins,rif_rel,t_grad" > %s/manifest.csv' % OUT)
    TF = 15.5
    L += cella("%s_bmmai" % tag, tag, 3.818, 1000, 2000, 3, TF, "rif_mai", mti=1.0, mtr=7.3)
    L += cella("%s_bmsempre" % tag, tag, 3.818, -100, 1000, 3, TF, "rif_sempre")
    for ts in (1.0, 3.0):
        P = 0.2 + 2 * ts
        tr = 1.0 + P + 0.1
        tf = tr + P + 2.0
        L += cella("%s_bm_t%g" % (tag, ts), "%s_rampa%gs" % (tag, ts), 3.818, 1.0, tr, ts, tf, "evento",
                   "%s_bmsempre" % tag, "%s_bmmai" % tag, P)
    if s == 0.08:
        # inversione a meta' della rampa lenta della serie, rampa 3 s
        tr = 1.0 + F + 1.5
        L += cella("%s_bm_inv" % tag, "%s_inversione" % tag, 3.818, 1.0, tr, 3.0, tr + (tr - 1.0) + 2.0, "evento",
                   "%s_bmmai" % tag, "%s_bmmai" % tag, tr - 1.0)
        # senza segnale, la rampa piu' rapida
        P = 0.2 + 2 * 1.0
        tr = 1.0 + P + 2.0
        tf = tr + P + 2.0
        L += cella("%s_lzmai" % tag, tag, 0, 1000, 2000, 1, tf, "rif_mai", mti=1.0, mtr=tr)
        L += cella("%s_lzsempre" % tag, tag, 0, -100, 1000, 1, tf, "rif_sempre")
        L += cella("%s_lz_t1" % tag, "%s_rampa1s" % tag, 0, 1.0, tr, 1.0, tf, "evento",
                   "%s_lzsempre" % tag, "%s_lzmai" % tag, P)
    L += [".endc", ".end"]
    open(os.path.join(OUT, "seq_%s.cir" % tag), "w").write("\n".join(L) + "\n")
