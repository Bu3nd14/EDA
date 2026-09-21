#!/usr/bin/env python3
"""Scratch L29b: il rele' al jack a 20 kHz, a mute LDR inserito (ADR-038 lo stima a
0,57 mV sulla principale). Non e' il deck versionato.

Uso:  /usr/bin/python3 build20k.py OUTDIR   ->  OUTDIR/rele20k.cir

La sequenza intera non si rifa' col passo da 0,5 us che 20 kHz chiede (L29a:
tb_v2_mute_pavimento.cir, 0,7 s, TMAX 0,5 us e 0,25 us per il pavimento). Si prende
lo STATO delle due LDR agli istanti del rele' dalla corsa a 1 kHz (ldr1k.cir, post.py):
  chiusura  (t = 4,05 s):  serie 5,756e5 ohm, derivazione 88,32 ohm
  apertura  (t = 5,00 s):  serie 1,372e6 ohm, derivazione 88,32 ohm
e ogni cella diventa il suo equivalente a stato fermo: la resistenza e i 5 pF della cella
(CCELL del modello). Nella finestra di 0,2 s la serie si muove di < 0,08 decadi (0,397
decadi/s): dichiarato. L'accoppiamento LED-cella (CIO 0,5 pF) e' escluso: il LED e'
fermo. Stesso blocco CANALE di tb_v2_mute_graduale.cir, copiato senza toccarlo.
"""
import os
import sys

R = os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."] * 6))
OUT = os.path.abspath(sys.argv[1])
TB = os.path.join(R, "spice", "preamp", "tb", "tb_v2_mute_graduale.cir")
righe = open(TB).read().splitlines()
fine = next(i for i, r in enumerate(righe) if r.startswith("* <<< CANALE"))
L = [r.replace("@REPO@", R) for r in righe[:fine + 1]]
L[0] = "rele20k.cir - L29b scratch: rele' al jack a 20 kHz, LDR a stato fermo"
L += [
    "* ---- L29b: le LDR a stato fermo, fuori dal blocco CANALE ----",
    "RSRC2 SRC SRCX 1.5",
    "RLS SRCX SELA 5.756e5",
    "CLS SRCX SELA 5p",
    "RLP INA 0 88.32",
    "CLP INA 0 5p",
]
MAN = os.path.join(OUT, "manifest.csv")
TI, TF, A = 0.3, 0.7, 3.818
L += [
    ".control",
    "set d = .dat",
    "save v(mainjack) v(fixjack1) v(fixjack2)",
    'echo "cella,file,variante,f_hz,amp,gm,rl,t_ins,t_rel,t_fine,tmax,tipo,rif_ins,rif_rel,t_grad" > %s' % MAN,
    "alter rsrc = 1e12",
    "alter rrgb = 0.1",
    "alter rrg10b = 0.1",
    "alter vphs dc = 1.5707963267948966",
    "alter vmhjk dc = 1",
    "alter vfrq dc = 20000",
    "alter vamp dc = %s" % A,
]


def corsa(nome, on, off, tmax):
    return ["alter vtijk dc = %s" % on, "alter vtrjk dc = %s" % off,
            "tran %g %g 0 %g" % (tmax, TF, tmax),
            "wrdata %s/%s$d v(mainjack) v(fixjack1) v(fixjack2)" % (OUT, nome), "destroy all"]


def riga(cella, file, var, t_ins, t_rel, tmax, tipo, rins="-", rrel="-"):
    return 'echo "%s,%s.dat,%s,20000,%s,10,100k,%s,%s,%s,%g,%s,%s,%s,0" >> %s' % (
        cella, file, var, A, t_ins, t_rel, TF, tmax, tipo, rins, rrel, MAN)


# chiusura: LDR allo stato di 4,05 s; il rele' si chiude a TI
L += corsa("c_ev", TI, 1000, 0.5e-6) + corsa("c_rif", 1000, 2000, 0.5e-6) + corsa("c_pav", 1000, 2000, 0.25e-6)
L += [riga("c_ev", "c_ev", "chiusura_rele", TI, 1000, 0.5e-6, "evento", "c_rif", "-"),
      riga("c_rif", "c_rif", "rif", TI, 1000, 0.5e-6, "rif_mai"),
      riga("c_pav", "c_pav", "pavimento", TI, 1000, 0.25e-6, "pav_num", "c_rif")]
# apertura: LDR allo stato di 5,00 s; il rele' chiuso da t = 0 si apre a TI
L += ["alter rls = 1.372e6"]
L += corsa("a_ev", -1, TI, 0.5e-6) + corsa("a_rif", 1000, 2000, 0.5e-6) + corsa("a_pav", 1000, 2000, 0.25e-6)
L += [riga("a_ev", "a_ev", "apertura_rele", 1000, TI, 0.5e-6, "evento", "-", "a_rif"),
      riga("a_rif", "a_rif", "rif", TI, 1000, 0.5e-6, "rif_mai"),
      riga("a_pav", "a_pav", "pavimento", TI, 1000, 0.25e-6, "pav_num", "a_rif")]
L += [".endc", ".end"]
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, "rele20k.cir"), "w").write("\n".join(L) + "\n")
print("scritto", os.path.join(OUT, "rele20k.cir"))
