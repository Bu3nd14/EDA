#!/usr/bin/env python3
"""L29b2, riscritto in L47c2b1: genera spice/preamp/tb/tb_v2_mute_taglio.cir, il deck VERSIONATO
di V2 col mute che TAGLIA coi soli rele' al jack (ADR-062, PR-21). Il deck non si edita a mano:
si rigenera.

Fino a L47c2a si chiamava genera_tb_v2_mute_ldr.py e scriveva tb_v2_mute_ldr.cir: due
fotoresistenze a monte del blocco A col loro profilo (ADR-038, poi la NSL-32SR3 di ADR-058..061).
ADR-062 le ha tolte, e il nome mentiva. L'ultima versione con le celle e' quella del commit
dffa7148. Uscite con loro: la corsa «norele» (senza fotoresistenze non e' un mute) e
l'inversione a d = 0,75 (il firmware di L47c2a non la permette: l'inserzione non e' reversibile).

Uso:  /usr/bin/python3 genera_tb_v2_mute_taglio.py [USCITA=<repo>/spice/preamp/tb/tb_v2_mute_taglio.cir]

Poi, per correrlo (in parallelo, una corsa per processo):
      sed "s|@REPO@|<repo>|g" tb_v2_mute_taglio.cir > DIR/taglio.cir
      /usr/bin/python3 .../pavimento/dividi.py DIR/taglio.cir     -> DIR/corsa_*.cir, DIR/manifest.csv
      ngspice -b DIR/corsa_<nome>.cir   (per ogni corsa, in background)
      /usr/bin/python3 scripts/v2_metodo.py analizza DIR/manifest.csv DIR DIR/analisi.csv

COSA C'E' DENTRO
- Il blocco CANALE di tb_v2_mute_graduale.cir, byte per byte (v2_metodo.py canale), con la
  sorgente sulla sua RSRC e il guadagno a +10 dB (RRGB, RRG10B a 0,1 ohm).
- Il mute e' il contatto del blocco al jack (BJK*, geometria N: la derivazione al jack), NON la
  geometria iii del sorgente: quella sta in tb_v2_casopeggiore.cir, che legge la netlist. Questo
  deck e' il riferimento piu' semplice, e il controfattuale di tb_v2_casopeggiore.cir (tutte le
  sue aggiunte in posizione neutra) deve ridarne la cella a 1 kHz e 100 k.
- I tempi del firmware di L47c2a: il contatto si muove T_ATT = 24 ms dopo il tasto (MUTE_CMD
  21 ms, piu' 3 ms del G6K), all'inserimento e al rilascio. t_ins e t_rel sono il tasto.
- "set numdgt=15" prima di ogni wrdata (docs/limitations.md #30).
- Le celle: tre uscite (tutte in ogni wrdata) x carichi 100 k e 10 k x 20 Hz / 1 kHz / 20 kHz.
  Per ognuna: riferimenti "mai" e "sempre", l'evento "ev", e il PAVIMENTO: "ev" rifatto a un
  altro TMAX (7 us contro 10 us; a 20 kHz 0,35 contro 0,5 us), letto come pav_num.
  A senza segnale (lz*) una volta per carico: non dipende dalla frequenza.
- TMAX: 10 us a 20 Hz e 1 kHz; 0,5 us a 20 kHz (tb_v2_mute_pavimento.cir, L29a).
"""
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(QUI, *[".."] * 6))
USCITA = (sys.argv[1] if len(sys.argv) > 1
          else os.path.join(REPO, "spice", "preamp", "tb", "tb_v2_mute_taglio.cir"))
TB = os.path.join(REPO, "spice", "preamp", "tb", "tb_v2_mute_graduale.cir")

righe = open(TB).read().splitlines()
i0 = next(i for i, r in enumerate(righe) if r.startswith("* >>> CANALE"))
i1 = next(i for i, r in enumerate(righe) if r.startswith("* <<< CANALE"))
inc = [r for r in righe[:i0] if r.startswith(".include")]
CANALE = righe[i0:i1 + 1]

# I tempi (ADR-062; firmware di L47c2a, data/2026-10-05/L47c2a/seq/analisi_seq.txt)
TI = 1.0                  # il tasto del mute
T_ATT = 0.021 + 3e-3      # MUTE_CMD 21 ms dopo il tasto, piu' il rilascio massimo del G6K
TR = TI + 1.0             # il tasto del rilascio
TF = TR + 3.0             # A vuole >= 2 s dopo il contatto del rilascio
TG = T_ATT                # t_grad: B2 parte da t_ins + TG + 20 ms
A = 3.818
FREQ = ((20, "20", 10e-6, 7e-6), (1000, "1k", 10e-6, 7e-6), (20000, "20k", 0.5e-6, 0.35e-6))
CARICHI = (("100k", "100k"), ("10k", "10k"))

H = [
    "tb_v2_mute_taglio.cir - V2 al jack col mute che taglia coi soli rele' al jack (ADR-062, L47c2b1; fino a L47c2a tb_v2_mute_ldr.cir, con le fotoresistenze)",
    "* Prima riga = titolo (docs/limitations.md #10).",
    "* GENERATO da docs/preamp/data/2026-09-22/L29b2/deck/genera_tb_v2_mute_taglio.py: non si",
    "* edita a mano. L'intestazione del generatore dice cosa c'e' dentro e come si corre.",
    "*",
    "* Da L39 (NC-017) ogni dispositivo attivo e' il modello del costruttore in models/, e da L44",
    "* tutti hanno KF (1/f; ADR-057).",
    "*",
    "* IL MUTE e' il contatto del blocco al jack (geometria N), %g ms dopo il tasto (MUTE_CMD 21 ms" % (T_ATT * 1e3),
    "* del firmware di L47c2a, piu' 3 ms del G6K); al rilascio lo stesso. La geometria iii del",
    "* sorgente e' in tb_v2_casopeggiore.cir.",
    "*",
    "* TEMPI: tasto del mute a %g s, contatto a %g s, tasto del rilascio a %g s, fine a %g s." % (TI, TI + T_ATT, TR, TF),
    "* Tono 2,7 V RMS, +10 dB, fase pi/2.",
    "*",
    "* ANALISI: scripts/v2_metodo.py analizza sul manifesto (tabella echo, nome",
    "* tb_v2_mute_taglio_manifest.csv; nessun wrdata lo nomina, #25). t_grad = %g ms." % (TG * 1e3),
    "* CONVENZIONE DI PERCORSO: `.include @REPO@/...` (tb_op.cir, L2-L3).",
    "",
] + inc + [""] + CANALE + [""]

MAN = "tb_v2_mute_taglio_manifest.csv"
C = [
    ".control",
    "* limitations #30: il tempo a 16 cifre, prima di ogni wrdata",
    "set numdgt=15",
    "set d = .dat",
    "save v(mainjack) v(fixjack1) v(fixjack2) v(ina)",
    'echo "cella,file,variante,f_hz,amp,gm,rl,t_ins,t_rel,t_fine,tmax,tipo,rif_ins,rif_rel,t_grad" > %s' % MAN,
    "alter rrgb = 0.1",
    "alter rrg10b = 0.1",
    "alter vphs dc = 1.5707963267948966",
    "alter vmhjk dc = 1",
]


def corsa(nome, f, amp, ron, roff, tmax, stati=False):
    """ron / roff: gli istanti in cui il contatto del jack chiude e riapre (1000 / 2000 = mai)."""
    out = [
        "alter vamp dc = %s" % amp,
        "alter vfrq dc = %s" % f,
        "alter vtijk dc = %.6f" % ron, "alter vtrjk dc = %.6f" % roff,
        "tran %g %s 0 %g" % (tmax, TF, tmax),
        "wrdata %s$d v(mainjack) v(fixjack1) v(fixjack2)" % nome,
    ]
    if stati:
        out.append("wrdata %s_stati$d v(ina)" % nome)
    return out + ["destroy all"]


def riga(cella, file, var, f, amp, rl, ti, tr, tmax, tipo, rins="-", rrel="-", tg=0.0):
    return 'echo "%s,%s.dat,%s,%s,%s,10,%s,%s,%s,%s,%g,%s,%s,%s,%s" >> %s' % (
        cella, file, var, f, amp, rl, ti, tr, TF, tmax, tipo, rins, rrel, tg, MAN)


MAI, SEMPRE, EVENTO = (1000, 2000), (-10, 1000), (TI + T_ATT, TR + T_ATT)
var = "taglio"
for rl, rlv in CARICHI:
    C += ["* ======== carico %s su tutte e tre le uscite ========" % rl,
          "alter rldm = %s" % rlv, "alter rld1 = %s" % rlv, "alter rld2 = %s" % rlv]
    for f, fn, tm, tm2 in FREQ:
        s = "_%s_%s" % (fn, rl)
        C += ["* ---- %s Hz, %s ----" % (f, rl)]
        C += corsa("mai" + s, f, A, *MAI, tm)
        C += [riga("mai" + s, "mai" + s, "rif", f, A, rl, TI, TR, tm, "rif_mai")]
        C += corsa("sempre" + s, f, A, *SEMPRE, tm)
        C += [riga("sempre" + s, "sempre" + s, "rif", f, A, rl, TI, TR, tm, "rif_sempre")]
        C += corsa("ev" + s, f, A, *EVENTO, tm, stati=True)
        C += [riga("ev" + s, "ev" + s, var, f, A, rl, TI, TR, tm, "evento",
                   "sempre" + s, "mai" + s, TG)]
        # il pavimento lungo la sequenza: ev a un altro TMAX
        C += corsa("evp" + s, f, A, *EVENTO, tm2)
        for k, t in enumerate((TI, TR)):
            C += [riga("pav_ev%d%s" % (k, s), "evp" + s, "pavimento", f, A, rl, t, 1000,
                       tm2, "pav_num", "ev" + s)]
    # A senza segnale: una volta per carico
    s = "_%s" % rl
    C += ["* ---- A senza segnale, %s ----" % rl]
    C += corsa("lzmai" + s, 1000, 0, *MAI, 10e-6)
    C += [riga("lzmai" + s, "lzmai" + s, "rif", 1000, 0, rl, TI, TR, 10e-6, "rif_mai")]
    C += corsa("lzsempre" + s, 1000, 0, *SEMPRE, 10e-6)
    C += [riga("lzsempre" + s, "lzsempre" + s, "rif", 1000, 0, rl, TI, TR, 10e-6, "rif_sempre")]
    C += corsa("lzev" + s, 1000, 0, *EVENTO, 10e-6, stati=True)
    C += [riga("lzev" + s, "lzev" + s, var, 1000, 0, rl, TI, TR, 10e-6, "evento",
               "lzsempre" + s, "lzmai" + s, TG)]
C += [".endc", "", ".end"]
open(USCITA, "w").write("\n".join(H + C) + "\n")
n = sum(1 for r in C if r.startswith("tran "))
print("scritto %s: %d corse" % (USCITA, n))
