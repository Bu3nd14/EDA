"""Scratch L29b passo 1: B statico del mute in serie con capacita' da aperto.
AC di piccolo segnale sullo stesso blocco CANALE di tb_v2_mute_graduale.cir.
NON e' una misura V2: e' la verifica di un calcolo."""
R = "/Users/roberto/EDA/.claude/worktrees/L29b"
src = open(R + "/spice/preamp/tb/tb_v2_mute_graduale.cir").read().splitlines()[:181]
out = []
for ln in src:
    ln = ln.replace("@REPO@", R)
    if ln.startswith("RSRC SRC SELA 1.5"):
        out.append("VACS SRC SRCX DC 0 AC 1")
        ln = "RSRC SRCX SELA 1.5"
    out.append(ln)
out += [
    "* capacita' da aperto dell'elemento in serie, e derivazione al jack",
    "CFM MAINC MAINJACK 1f",
    "CF1 FIXC1 FIXJACK1 1f",
    "CF2 FIXC2 FIXJACK2 1f",
    "RSHM MAINJACK 0 1e12",
    "RSH1 FIXJACK1 0 1e12",
    "RSH2 FIXJACK2 0 1e12",
    ".control",
    "alter rrgb = 0.1",
    "alter rrg10b = 0.1",
    "alter vamp dc = 0",
    "alter vmhser dc = 0",
    "alter vtiser dc = -10",
    "alter vtgser dc = 1",
    "alter vtrser dc = 1000",
    "alter rbym = 1e12",
    "alter rby1 = 1e12",
    "alter rby2 = 1e12",
    "alter rbcm = 220k",
    "alter rbc1 = 470k",
    "alter rbc2 = 470k",
    'echo "coff_pF,shunt_ohm,rl,f,main,fix1,main_a,fix1_pre" > coff.csv',
]
for cp in ("1f", "0.5p", "2p", "10p"):
    for sh in ("1e12", "0.1"):
        for rl in ("100k", "10k"):
            out += [
                f"alter cfm = {cp}", f"alter cf1 = {cp}", f"alter cf2 = {cp}",
                f"alter rshm = {sh}", f"alter rsh1 = {sh}", f"alter rsh2 = {sh}",
                f"alter rldm = {rl}", f"alter rld1 = {rl}", f"alter rld2 = {rl}",
            ]
            for f in (20, 1000, 20000):
                out += [
                    f"ac lin 1 {f} {f}",
                    "let a = mag(v(mainjack))[0]",
                    "let b = mag(v(fixjack1))[0]",
                    "let c = mag(v(main_a))[0]",
                    "let d = mag(v(fix1))[0]",
                    'set va = "$&a"', 'set vb = "$&b"', 'set vc = "$&c"', 'set vd = "$&d"',
                    f'echo "{cp},{sh},{rl},{f},$va,$vb,$vc,$vd" >> coff.csv',
                    "destroy all",
                ]
out += [".endc", ".end"]
open("/Users/roberto/.claude/jobs/c42646c7/tmp/s1/coff.cir", "w").write("\n".join(out) + "\n")
