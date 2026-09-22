#!/usr/bin/env python3
"""L29b2: genera spice/preamp/tb/tb_v2_mute_ldr.cir, il deck VERSIONATO di V2 col mute
graduale a monte con due LDR VTL5C4 (ADR-038). Il deck non si edita a mano: si rigenera.

Uso:  /usr/bin/python3 genera_tb_v2_mute_ldr.py [PROFILO=v3] [TD=6] [USCITA=<repo>/spice/preamp/tb/tb_v2_mute_ldr.cir]

Poi, per correrlo (le corse sono lunghe: in parallelo, una per processo):
      sed "s|@REPO@|<repo>|g" tb_v2_mute_ldr.cir > DIR/ldr.cir
      /usr/bin/python3 .../pavimento/dividi.py DIR/ldr.cir     -> DIR/corsa_*.cir, DIR/manifest.csv
      ngspice -b DIR/corsa_<nome>.cir   (per ogni corsa, in background)
      /usr/bin/python3 scripts/v2_metodo.py analizza DIR/manifest.csv DIR DIR/analisi.csv

COSA C'E' DENTRO
- Il blocco CANALE di tb_v2_mute_graduale.cir, byte per byte (v2_metodo.py canale).
- Le due LDR e il loro comando, fuori dal blocco, come ldr_catena/build.py di L29b: serie fra
  sorgente e selettore, derivazione su INA accanto a R_IN = 1 M, LED da generatori ideali con
  10 M dall'anodo (trappola di L29b), la profondita' d unica e reversibile, il rele' al jack
  (il contatto netto BJK* del blocco) chiuso 0,5 s dopo d = 1 e aperto all'inizio del rilascio.
- "set numdgt=15" prima di ogni wrdata (docs/limitations.md #30): col default il tempo si
  scrive a 100 ns sopra 10 s, e C2 fra due corse misura l'arrotondamento (7 mV a 1 kHz).
- Le celle: tre uscite (tutte in ogni wrdata) x carichi 100 k e 10 k x 20 Hz / 1 kHz / 20 kHz.
  Per ognuna: riferimenti "mai" e "sempre", l'evento "ev", lo stesso senza rele' "norele",
  l'inversione a d = 0,75 "inv", e il PAVIMENTO lungo tutta la sequenza: "ev" e "inv" rifatti
  a un altro TMAX (7 us contro 10 us; a 20 kHz 0,35 contro 0,5 us), letti come pav_num.
  A senza segnale (lz*) una volta per carico: non dipende dalla frequenza.
- TMAX: 10 us a 20 Hz e 1 kHz; 0,5 us a 20 kHz (tb_v2_mute_pavimento.cir, L29a).

I PROFILI. v3 e' la scelta dell'utente del 2026-09-21 (report L29b), ed e' il default. v4 e'
una PROPOSTA di L29b2, misurata e non adottata: la serie da 4,5 uA scende al ginocchio del buio
(0,19 uA) fino a d = 0,75 invece che a 10 nA gia' a d = 0,5 (C2 di rilascio 3,41 -> 1,47 mV).
"""
import math
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(QUI, *[".."] * 6))
PROFILO = sys.argv[1] if len(sys.argv) > 1 else "v3"
TD = float(sys.argv[2]) if len(sys.argv) > 2 else 6.0
USCITA = (sys.argv[3] if len(sys.argv) > 3
          else os.path.join(REPO, "spice", "preamp", "tb", "tb_v2_mute_ldr.cir"))
TB = os.path.join(REPO, "spice", "preamp", "tb", "tb_v2_mute_graduale.cir")

righe = open(TB).read().splitlines()
i0 = next(i for i, r in enumerate(righe) if r.startswith("* >>> CANALE"))
i1 = next(i for i, r in enumerate(righe) if r.startswith("* <<< CANALE"))
inc = [r for r in righe[:i0] if r.startswith(".include")]
CANALE = righe[i0:i1 + 1]

ION, IRIP = 20e-3, 10e-9
lg = math.log10
if PROFILO == "v3":
    SERIE = [(0, ION), (0.1, 0.2e-3), (0.45, 4.5e-6), (0.5, IRIP), (1, IRIP)]
elif PROFILO == "v4":
    SERIE = [(0, ION), (0.1, 0.2e-3), (0.45, 4.5e-6), (0.75, 0.19e-6), (0.8, IRIP), (1, IRIP)]
else:
    sys.exit("profilo sconosciuto: %s (v3 = scelta dell'utente, v4 = proposta L29b2)" % PROFILO)
BILS = "BILS 0 ALS I = pow(10, pwl(V(DEP), %s))" % ", ".join(
    "%g,%.4f" % (d, lg(i)) for d, i in SERIE)
BILP = "BILP 0 ALP I = %g * pow(%g, min(max((V(DEP) - 0.5)/0.5, 0), 1))" % (IRIP, ION / IRIP)

TI, RIT = 1.0, 0.5
T_RELE = TI + TD + RIT
TR = T_RELE + 1.0
TF = TR + TD + 3.0
DINV = 0.75
TINV = TI + DINV * TD
TFI = TINV + DINV * TD + 3.0
TG = TD + RIT
A = 3.818
FREQ = ((20, "20", 10e-6, 7e-6), (1000, "1k", 10e-6, 7e-6), (20000, "20k", 0.5e-6, 0.35e-6))
CARICHI = (("100k", "100k"), ("10k", "10k"))

H = [
    "tb_v2_mute_ldr.cir - V2 al jack col mute graduale a monte: due LDR VTL5C4 all'ingresso del blocco A, profilo %s Td %g s (ADR-038, L29b2, NC-028)" % (PROFILO, TD),
    "* Prima riga = titolo (docs/limitations.md #10).",
    "* GENERATO da docs/preamp/data/2026-09-22/L29b2/deck/genera_tb_v2_mute_ldr.py: non si",
    "* edita a mano. L'intestazione del generatore dice cosa c'e' dentro e come si corre.",
    "*",
    "* IL MODELLO DELLE CELLE e' comportamentale dal datasheet, con estrapolazione dichiarata",
    "* sopra ~10 kOhm (models/optocoupler/vtl5c4_comportamentale.lib, curva B per entrambe).",
    "* Ogni cifra di questo deck porta quell'etichetta. Il resto e' come nei deck di V2: tutto",
    "* tranne LS352 e' segnaposto, LSK489 compreso (NC-017, NC-031).",
    "*",
    "* IL PROFILO %s. Serie, log-lineare a tratti in d: %s." % (
        PROFILO, "; ".join("%g A a d = %g" % (i, d) for d, i in SERIE)),
    "* Derivazione: 10 nA fino a d = 0,5, poi log-lineare fino a 20 mA a d = 1. d va da 0 a 1",
    "* in Td = %g s dall'inserzione e torna indietro con la stessa velocita' da dove si trova." % TD,
    "* Rele' al jack chiuso a t_ins + Td + 0,5 s, aperto a t_rel.",
    "*",
    "* TEMPI: inserzione a %g s, rele' a %g s, rilascio a %g s, fine a %g s; inversione a" % (TI, T_RELE, TR, TF),
    "* d = %g, cioe' a %g s, fine a %g s. Tono 2,7 V RMS, +10 dB, fase pi/2." % (DINV, TINV, TFI),
    "*",
    "* ANALISI: scripts/v2_metodo.py analizza sul manifesto (tabella echo, nome",
    "* tb_v2_mute_ldr_manifest.csv; nessun wrdata lo nomina, #25). t_grad = Td + 0,5 s.",
    "* CONVENZIONE DI PERCORSO: `.include @REPO@/...` (tb_op.cir, L2-L3).",
    "",
] + inc + [".include @REPO@/models/optocoupler/vtl5c4_comportamentale.lib", ""] + CANALE + [
    "* ---- L29b2: le due LDR e il loro comando, fuori dal blocco CANALE (ADR-038) ----",
    "VTI NTI 0 DC 1000",
    "VTR NTR 0 DC 2000",
    "VTD NTD 0 DC %g" % TD,
    "BDIN DIN 0 V = min(max((time - V(NTI))/V(NTD), 0), 1)",
    "BDEP DEP 0 V = time < V(NTR) ? V(DIN) : max(min(max((V(NTR) - V(NTI))/V(NTD), 0), 1)"
    " - (time - V(NTR))/V(NTD), 0)",
    BILS,
    BILP,
    "* 10 M dall'anodo a massa: un LED col solo generatore non ha percorso in continua e l'op",
    "* fallisce in silenzio (trappola di L29b). E' del banco, non della scheda.",
    "RALS ALS 0 10MEG",
    "RALP ALP 0 10MEG",
    "RSRC2 SRC SRCX 1.5",
    "XLS ALS 0 SRCX SELA VTL5C4_B",
    "XLP ALP 0 INA 0 VTL5C4_B",
    "",
]

MAN = "tb_v2_mute_ldr_manifest.csv"
C = [
    ".control",
    "* limitations #30: il tempo a 16 cifre, prima di ogni wrdata",
    "set numdgt=15",
    "set d = .dat",
    "save v(mainjack) v(fixjack1) v(fixjack2) v(xls.xs) v(xlp.xs) v(dep) v(ina)",
    'echo "cella,file,variante,f_hz,amp,gm,rl,t_ins,t_rel,t_fine,tmax,tipo,rif_ins,rif_rel,t_grad" > %s' % MAN,
    "* la sorgente passa dalla LDR in serie: RSRC del blocco a 1 T, il selettore chiuso",
    "alter rsrc = 1e12",
    "alter rrgb = 0.1",
    "alter rrg10b = 0.1",
    "alter vphs dc = 1.5707963267948966",
    "alter vmhjk dc = 1",
]


def corsa(nome, f, amp, ti, tr, ron, roff, tf, tmax, stati=False):
    out = [
        "alter vamp dc = %s" % amp,
        "alter vfrq dc = %s" % f,
        "alter vti dc = %s" % ti, "alter vtr dc = %s" % tr,
        "alter vtijk dc = %s" % ron, "alter vtrjk dc = %s" % roff,
        "tran %g %s 0 %g" % (tmax, tf, tmax),
        "wrdata %s$d v(mainjack) v(fixjack1) v(fixjack2)" % nome,
    ]
    if stati:
        out.append("wrdata %s_stati$d v(xls.xs) v(xlp.xs) v(dep) v(ina)" % nome)
    return out + ["destroy all"]


def riga(cella, file, var, f, amp, rl, ti, tr, tf, tmax, tipo, rins="-", rrel="-", tg=0.0):
    return 'echo "%s,%s.dat,%s,%s,%s,10,%s,%s,%s,%s,%g,%s,%s,%s,%s" >> %s' % (
        cella, file, var, f, amp, rl, ti, tr, tf, tmax, tipo, rins, rrel, tg, MAN)


var = "ldr_%s_td%g" % (PROFILO, TD)
for rl, rlv in CARICHI:
    C += ["* ======== carico %s su tutte e tre le uscite ========" % rl,
          "alter rldm = %s" % rlv, "alter rld1 = %s" % rlv, "alter rld2 = %s" % rlv]
    for f, fn, tm, tm2 in FREQ:
        s = "_%s_%s" % (fn, rl)
        C += ["* ---- %s Hz, %s ----" % (f, rl)]
        C += corsa("mai" + s, f, A, 1000, 2000, 1000, 2000, TF, tm)
        C += [riga("mai" + s, "mai" + s, "rif", f, A, rl, TI, TR, TF, tm, "rif_mai")]
        C += corsa("sempre" + s, f, A, -10, 1000, -10, 1000, TF, tm)
        C += [riga("sempre" + s, "sempre" + s, "rif", f, A, rl, TI, TR, TF, tm, "rif_sempre")]
        C += corsa("ev" + s, f, A, TI, TR, T_RELE, TR, TF, tm, stati=True)
        C += [riga("ev" + s, "ev" + s, var, f, A, rl, TI, TR, TF, tm, "evento",
                   "sempre" + s, "mai" + s, TG)]
        C += corsa("norele" + s, f, A, TI, TR, 1000, 2000, TF, tm, stati=True)
        C += [riga("norele" + s, "norele" + s, "rif", f, A, rl, TI, TR, TF, tm, "rif_seq")]
        C += [riga("rele" + s, "ev" + s, "rele_contro_norele", f, A, rl, T_RELE, TR, TF, tm,
                   "evento", "norele" + s, "norele" + s, 0.0)]
        C += corsa("inv" + s, f, A, TI, TINV, 1000, 2000, TFI, tm, stati=True)
        C += [riga("inv" + s, "inv" + s, "inversione_d%02d" % round(100 * DINV), f, A, rl,
                   TI, TINV, TFI, tm, "evento", "sempre" + s, "mai" + s, DINV * TD)]
        # il pavimento lungo la sequenza: ev e inv a un altro TMAX
        C += corsa("evp" + s, f, A, TI, TR, T_RELE, TR, TF, tm2)
        C += corsa("invp" + s, f, A, TI, TINV, 1000, 2000, TFI, tm2)
        for k, t in enumerate((TI, T_RELE, TR)):
            C += [riga("pav_ev%d%s" % (k, s), "evp" + s, "pavimento", f, A, rl, t, 1000, TF,
                       tm2, "pav_num", "ev" + s)]
        C += [riga("pav_inv%s" % s, "invp" + s, "pavimento", f, A, rl, TINV, 1000, TFI, tm2,
                   "pav_num", "inv" + s)]
    # A senza segnale: una volta per carico
    s = "_%s" % rl
    C += ["* ---- A senza segnale, %s ----" % rl]
    C += corsa("lzmai" + s, 1000, 0, 1000, 2000, 1000, 2000, TF, 10e-6)
    C += [riga("lzmai" + s, "lzmai" + s, "rif", 1000, 0, rl, TI, TR, TF, 10e-6, "rif_mai")]
    C += corsa("lzsempre" + s, 1000, 0, -10, 1000, -10, 1000, TF, 10e-6)
    C += [riga("lzsempre" + s, "lzsempre" + s, "rif", 1000, 0, rl, TI, TR, TF, 10e-6, "rif_sempre")]
    C += corsa("lzev" + s, 1000, 0, TI, TR, T_RELE, TR, TF, 10e-6, stati=True)
    C += [riga("lzev" + s, "lzev" + s, var, 1000, 0, rl, TI, TR, TF, 10e-6, "evento",
               "lzsempre" + s, "lzmai" + s, TG)]
    C += corsa("lzinv" + s, 1000, 0, TI, TINV, 1000, 2000, TFI, 10e-6)
    C += [riga("lzinv" + s, "lzinv" + s, "inversione_d%02d" % round(100 * DINV), 1000, 0, rl,
               TI, TINV, TFI, 10e-6, "evento", "lzsempre" + s, "lzmai" + s, DINV * TD)]
C += [".endc", "", ".end"]
open(USCITA, "w").write("\n".join(H + C) + "\n")
n = sum(1 for r in C if r.startswith("tran "))
print("scritto %s: profilo %s, Td %g s, %d corse" % (USCITA, PROFILO, TD, n))
