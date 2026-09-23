#!/usr/bin/env python3
"""L29c: genera spice/preamp/tb/tb_v2_casopeggiore.cir, il deck VERSIONATO del caso peggiore di
V2 col mute reale (NC-028): LDR v4 a monte (ADR-038/039/040) piu' il rele' al jack, sul circuito
di ADR-042. Il deck non si edita a mano: si rigenera.

Uso:
  /usr/bin/python3 genera_tb_v2_casopeggiore.py [--matrice l29c|controfattuale]
          [--curve SERIE DERIV] [--uscita PATH]

  --matrice l29c            (default) la matrice di L29c, scritta nel deck versionato
  --matrice controfattuale  le 11 corse della cella di L40 (1 kHz, 100 k) con TUTTE le aggiunte
                            di questo banco in posizione neutra: devono ridare la cella di L40
  --curve B B               le curve della VTL5C4 per la cella in serie e quella in derivazione
                            (A = resistenza piu' bassa ... D = piu' alta). Il deck versionato e'
                            B B, come tb_v2_mute_ldr.cir; le altre si generano nei dati di L29c.

Poi si corre come tb_v2_mute_ldr.cir (L29b2): sed @REPO@, dividi.py, una corsa per processo,
v2_metodo.py analizza. Il manifesto ha due colonne in piu', ignorate da analizza:
  gruppo  il punto del mandato di L29c (1 guadagno, 2 trim, 3 dispersione, 4 durata del mute,
          5 accensione e spegnimento, 6 curve; 0 riferimenti e pavimenti)
  conta   le grandezze che per quella riga sono VERDETTO (A_ins, A_rel, B2, S_ins, S_rel),
          separate da ';'. Il resto che analizza scrive e' diagnostica: una riga di sequenza
          (per esempio il cambio di guadagno) legge anche grandezze che non hanno senso li'.

COSA C'E' DENTRO, oltre a tb_v2_mute_ldr.cir (L29b2). Il blocco CANALE e' byte per byte quello
di tb_v2_mute_graduale.cir (v2_metodo.py canale): tutto si aggiunge FUORI.
- I contatti del guadagno che commutano nel tempo: K1 (RGB) e K5 (RG10B), conduttanze
  comportamentali in parallelo a RRGB/RRG10B (1 G nel blocco, con i loro 15 pF), chiuse a
  100 mohm, con fronte e rimbalzi del contatto al jack (BSJKR). Sequenza di tb_switch_v2.cir:
  0 -> +10 con K5 per primo e K1 0,3 ms dopo; +10 -> 0 con K1 per primo.
- Il trim (ADR-027, candidato 2 di trim.py): RATTT del blocco aperto (alter rattt = 1e12), la
  scala 845 / 464 / 464 da OUTA, i quattro contatti T1R, T1S, T2R, T2S con 15 pF ciascuno, i
  100 pF del cablaggio e RATTH (la parte alta dell'attenuatore) fino a W. RATTB del blocco e' la
  parte bassa. Un rele' del trim e' un deviatore: il contatto che apre apre a t, quello che chiude
  chiude 1 ms dopo (ipotesi dichiarata: il tempo di trasferimento non e' nel datasheet letto).
- La dispersione: VOSA / VOSB / VOSF1 / VOSF2 del blocco (offset d'ingresso), e il gruppo B di
  ADR-031 con `altermod lsk489a vto` e la sonda JPRB su nodi propri (docs/limitations.md #29).
- I rail: `alter @vpp[pwl]` / `alter @vmm[pwl]` sulle sorgenti DC del blocco (sonda di L29c:
  l'op parte dal valore della PWL a t = 0, malgrado la nota «dc value used for op»). Il comando
  dei LED segue il rail positivo (VPWL, fattore 0..1): all'accensione i LED non hanno corrente
  prima dei rail, allo spegnimento la perdono con loro.
- `set numdgt=15` prima di ogni wrdata (#30). Nessun corpo di `if` vuoto (#32).

IPOTESI DI ACCENSIONE E SPEGNIMENTO (ADR-039 non le fissa; l'alimentatore e' di L30):
- accensione: rele' del jack chiuso (NC diseccitato), comando dei LED a d = 1 da subito; rail
  da 0 a +-15 V in TR_RAIL; il temporizzatore rilascia 2,5 s dopo l'inizio della rampa;
- spegnimento: da regime, rail a 0 in TR_RAIL; nessuna dissolvenza (caso peggiore: il comando
  non se ne accorge); il rele' del jack si chiude con un ritardo dall'inizio della discesa.
"""
import argparse
import math
import os

QUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(QUI, *[".."] * 6))
ap = argparse.ArgumentParser()
ap.add_argument("--matrice", default="l29c", choices=("l29c", "controfattuale"))
ap.add_argument("--curve", nargs=2, default=("B", "B"), metavar=("SERIE", "DERIV"))
ap.add_argument("--uscita", default=os.path.join(REPO, "spice", "preamp", "tb", "tb_v2_casopeggiore.cir"))
ARG = ap.parse_args()
CS, CP = ARG.curve
TB = os.path.join(REPO, "spice", "preamp", "tb", "tb_v2_mute_graduale.cir")

righe = open(TB).read().splitlines()
i0 = next(i for i, r in enumerate(righe) if r.startswith("* >>> CANALE"))
i1 = next(i for i, r in enumerate(righe) if r.startswith("* <<< CANALE"))
inc = [r for r in righe[:i0] if r.startswith(".include")]
CANALE = righe[i0:i1 + 1]

# ---------------------------------------------------------------- il profilo v4 (ADR-040)
ION, IRIP = 20e-3, 10e-9
lg = math.log10
SERIE = [(0, ION), (0.1, 0.2e-3), (0.45, 4.5e-6), (0.75, 0.19e-6), (0.8, IRIP), (1, IRIP)]
BILS = "BILS 0 ALS I = V(NPWL) * pow(10, pwl(V(DEP), %s))" % ", ".join(
    "%g,%.4f" % (d, lg(i)) for d, i in SERIE)
BILP = "BILP 0 ALP I = V(NPWL) * %g * pow(%g, min(max((V(DEP) - 0.5)/0.5, 0), 1))" % (IRIP, ION / IRIP)

# ---------------------------------------------------------------- i tempi
TI, TD, RIT = 1.0, 6.0, 0.5
T_RELE = TI + TD + RIT            # 7,5 s: il rele' al jack si chiude
TG_LDR = TD + RIT                 # t_grad di una riga d'inserzione
A = 3.818                         # 2,7 V RMS
FREQ = {"20": (20, 10e-6, 7e-6), "1k": (1000, 10e-6, 7e-6), "20k": (20000, 0.5e-6, 0.35e-6)}
T_CAMBIO = T_RELE + 0.5           # il cambio di guadagno o di trim, a rele' chiuso
TR_CAMBIO = T_CAMBIO + 2.0        # il rilascio: 2 s dopo il cambio, finestra piena di A
TF_CAMBIO = TR_CAMBIO + TD + 3.0
TF_LUNGO = T_RELE + 20.0 + TD + 3.0   # il mute di 20 s: i riferimenti durano quanto lui

# ---------------------------------------------------------------- i contatti che commutano
MAKE = "-1e4,0, 0,0, 1u,1, 150u,1, 151u,0, 300u,0, 301u,1, 450u,1, 451u,0, 520u,0, 521u,1, 1e4,1"
BREAK = "-1e4,1, 0,1, 1u,0, 400u,0, 401u,1, 600u,1, 601u,0, 1e4,0"


def contatto(n, a, b, cpar):
    out = [
        "V%sI N%sI 0 DC 0" % (n, n),
        "V%sT N%sT 0 DC 1000" % (n, n),
        "B%sR S%sR 0 V = (1 - V(N%sI)) * pwl(time - V(N%sT), %s)" % (n, n, n, n, MAKE),
        "+ + V(N%sI) * pwl(time - V(N%sT), %s)" % (n, n, BREAK),
        "R%sS S%sR S%s 1k" % (n, n, n),
        "C%sS S%s 0 4.55n" % (n, n),
        "B%s %s %s I = V(%s,%s) * pow(10, -12 + 13*V(S%s))" % (n, a, b, a, b, n),
    ]
    if cpar:
        out.append("C%sP %s %s 15p" % (n, a, b))
    return out


CONTATTI = ("K1", "K5", "T1R", "T1S", "T2R", "T2S")
AGGIUNTE = (
    ["* ---- L29c: i contatti del guadagno, in parallelo a RRGB / RRG10B del blocco ----"]
    + contatto("K1", "RGB", "0", False) + contatto("K5", "RG10B", "0", False)
    + ["* ---- L29c: il trim (ADR-027, trim.py candidato 2) fra OUTA e l'attenuatore ----",
       "* RATTT del blocco si apre nel .control (alter rattt = 1e12): OUTA arriva a W da qui.",
       "RL1 OUTA TAP6 845", "RL2 TAP6 TAP12 464", "RL3 TAP12 0 464"]
    + contatto("T1R", "OUTA", "ATOP", True) + contatto("T1S", "T2C", "ATOP", True)
    + contatto("T2R", "TAP6", "T2C", True) + contatto("T2S", "TAP12", "T2C", True)
    + ["CWIRE ATOP 0 100p", "RATTH ATOP W 1m",
       "* ---- L29c: la sonda del gruppo B (limitations #29), su nodi propri (#24) ----",
       "VPRBD PRBD 0 DC 15", "VPRBG PRBG 0 DC 0", "JPRB PRBD PRBG 0 LSK489A",
       "* ---- L29c: l'alimentazione del comando dei LED, 0..1, segue il rail positivo ----",
       "VPWL NPWL 0 DC 1", ""]
)

H = [
    "tb_v2_casopeggiore.cir - V2 al jack, il caso peggiore col mute reale: LDR VTL5C4 v4 a monte e rele' al jack, guadagno, trim, dispersione, accensione (L29c, NC-028)",
    "* Prima riga = titolo (docs/limitations.md #10).",
    "* GENERATO da docs/preamp/data/2026-09-23/L29c/deck/genera_tb_v2_casopeggiore.py: non si",
    "* edita a mano. L'intestazione del generatore dice cosa c'e' dentro, le ipotesi di",
    "* accensione e spegnimento, e come si corre. Matrice: %s. Curve: serie %s, derivazione %s." % (ARG.matrice, CS, CP),
    "*",
    "* IL MODELLO DELLE CELLE e' comportamentale dal datasheet, con estrapolazione dichiarata",
    "* (models/optocoupler/vtl5c4_comportamentale.lib). Ogni dispositivo attivo e' il modello del",
    "* costruttore in models/ (L39); nessuno porta la dispersione, che qui si inietta: VOS* e",
    "* `altermod lsk489a vto` (gruppo B, ADR-031). UN MODELLO ALTERATO PORTA ANCORA IL NOME",
    "* LSK489A (limitations #29): le corse alterate lo dicono nel nome (_gb*) e stampano showmod",
    "* e la corrente della sonda JPRB.",
    "*",
    "* IL PROFILO v4, Td %g s (ADR-039, ADR-040). Rele' al jack chiuso 0,5 s dopo d = 1." % TD,
    "* ANALISI: scripts/v2_metodo.py analizza sul manifesto; le colonne gruppo e conta dicono",
    "* quali grandezze di ogni riga sono verdetto. Si corre DIVISO (dividi.py): le corse di",
    "* accensione alterano le sorgenti dei rail, e in sequenza l'alterazione resterebbe.",
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
    "XLS ALS 0 SRCX SELA VTL5C4_%s" % CS,
    "XLP ALP 0 INA 0 VTL5C4_%s" % CP,
    "",
] + AGGIUNTE

MAN = "tb_v2_casopeggiore_manifest.csv"
C = [
    ".control",
    "* limitations #30: il tempo a 16 cifre, prima di ogni wrdata",
    "set numdgt=15",
    "set d = .dat",
    "save v(mainjack) v(fixjack1) v(fixjack2) v(xls.xs) v(xlp.xs) v(dep) v(ina) v(vplus) v(vminus) v(main_a)",
    'echo "cella,file,variante,f_hz,amp,gm,rl,t_ins,t_rel,t_fine,tmax,tipo,rif_ins,rif_rel,t_grad,gruppo,conta" > %s' % MAN,
    "* la sorgente passa dalla LDR in serie: RSRC del blocco a 1 T, il selettore chiuso",
    "alter rsrc = 1e12",
    "alter vphs dc = 1.5707963267948966",
    "alter vmhjk dc = 1",
    "* il trim porta OUTA all'attenuatore: RATTT del blocco aperto",
    "alter rattt = 1e12",
]

# ---------------------------------------------------------------- lo stato di una corsa
GUADAGNO = {0: (0, 0), 3: (1, 0), 10: (1, 1)}          # (K1, K5) chiusi
TRIM = {0: (1, 0, 1, 0), 6: (0, 1, 1, 0), 12: (0, 1, 0, 1)}   # (T1R, T1S, T2R, T2S)
ATT = {"max": ("1m", "10k"), "meta": ("5k", "5k"), "m20": ("9k", "1k")}
VTO = {"b_min": "-2.086", "b_tip": "-2.557", "b_max": "-2.976"}   # ADR-031, tb_idss_loop.cir


def cambio_guadagno(g1, g2, t):
    """(init, t_commutazione) di K1 e K5 per il passaggio g1 -> g2 a t (None = statico g1)."""
    k1i, k5i = GUADAGNO[g1]
    if g2 is None or g2 == g1:
        return {"K1": (k1i, 1000), "K5": (k5i, 1000)}
    k1f, k5f = GUADAGNO[g2]
    t1 = t5 = 1000
    salita = g2 > g1
    if k1i != k1f:
        t1 = t
    if k5i != k5f:
        t5 = t
    if k1i != k1f and k5i != k5f:
        # tb_switch_v2.cir: 0 -> +10 K5 per primo; +10 -> 0 K1 per primo, K5 0,3 ms dopo
        if salita:
            t1 = t + 0.3e-3
        else:
            t5 = t + 0.3e-3
    return {"K1": (k1i, t1), "K5": (k5i, t5)}


def cambio_trim(p1, p2, t):
    i = TRIM[p1]
    if p2 is None or p2 == p1:
        return dict(zip(("T1R", "T1S", "T2R", "T2S"), [(x, 1000) for x in i]))
    f = TRIM[p2]
    out = {}
    for n, a, b in zip(("T1R", "T1S", "T2R", "T2S"), i, f):
        if a == b:
            out[n] = (a, 1000)
        else:
            # deviatore: chi apre apre a t, chi chiude chiude 1 ms dopo
            out[n] = (a, t if a == 1 else t + 1e-3)
    return out


def corsa(nome, amp=A, f=1000, tmax=10e-6, tf=17.5, ti=1000, tr=2000, tijk=1000, trjk=2000,
          g1=10, g2=None, tg=1000, p1=0, p2=None, tp=1000, vos=(0, 0, 0, 0), att="max",
          rl="100k", trim_montato=True, cwire="100p", vto=None, rail=None, stati=True):
    out = [
        "alter vamp dc = %s" % amp,
        "alter vfrq dc = %s" % f,
        "alter rldm = %s" % rl, "alter rld1 = %s" % rl, "alter rld2 = %s" % rl,
        "alter vti dc = %s" % ti, "alter vtr dc = %s" % tr,
        "alter vtijk dc = %s" % tijk, "alter vtrjk dc = %s" % trjk,
        "alter vosa dc = %s" % vos[0], "alter vosb dc = %s" % vos[1],
        "alter vosf1 dc = %s" % vos[2], "alter vosf2 dc = %s" % vos[3],
        "alter ratth = %s" % ATT[att][0], "alter rattb = %s" % ATT[att][1],
        "alter rl1 = %s" % ("845" if trim_montato else "1e12"),
        "alter cwire = %s" % cwire,
    ]
    st = {}
    st.update(cambio_guadagno(g1, g2, tg))
    st.update(cambio_trim(p1, p2, tp))
    for n in CONTATTI:
        i, t = st[n]
        out += ["alter v%si dc = %s" % (n.lower(), i), "alter v%st dc = %.6f" % (n.lower(), t)]
    if vto is not None:
        out += ["altermod lsk489a vto = %s" % VTO[vto],
                "showmod jprb : vto beta",
                "op",
                "print -i(vprbd)"]
        # niente destroy qui: dividi.py chiude una corsa al primo "destroy all"
    if rail is not None:
        vp, vm, pw = rail
        out += ["alter @vpp[pwl] = [ %s ]" % vp, "alter @vmm[pwl] = [ %s ]" % vm,
                "alter @vpwl[pwl] = [ %s ]" % pw]
    out += ["tran %g %s 0 %g" % (tmax, tf, tmax),
            "wrdata %s$d v(mainjack) v(fixjack1) v(fixjack2)" % nome]
    if stati:
        out.append("wrdata %s_stati$d v(xls.xs) v(xlp.xs) v(dep) v(ina) v(vplus) v(vminus) v(main_a)" % nome)
    return out + ["destroy all"]


def riga(cella, file, var, f, amp, gm, rl, ti, tr, tf, tmax, tipo, rins="-", rrel="-", tg=0.0,
         gruppo=0, conta=""):
    return 'echo "%s,%s.dat,%s,%s,%s,%s,%s,%s,%s,%s,%g,%s,%s,%s,%s,%s,%s" >> %s' % (
        cella, file, var, f, amp, gm, rl, ti, tr, tf, tmax, tipo, rins, rrel, tg, gruppo, conta, MAN)


# ---------------------------------------------------------------- le matrici
def controfattuale():
    """La cella di L40 (1 kHz, 100 k), corse e righe come genera_tb_v2_mute_ldr.py, con le
    aggiunte neutre: guadagno +10 statico dai contatti nuovi, trim smontato (RL1 aperto, T1R
    chiuso), niente cablaggio, VOS 0, attenuatore al massimo."""
    n = dict(trim_montato=False, cwire="1e-18")
    TR, TF = T_RELE + 1.0, T_RELE + 1.0 + TD + 3.0
    TINV = TI + 0.75 * TD
    TFI = TINV + 0.75 * TD + 3.0
    s, var, fq = "_1k_100k", "ldr_v4_td6", 1000
    out = []
    out += corsa("mai" + s, tf=TF, ti=1000, tr=2000, **n)
    out += [riga("mai" + s, "mai" + s, "rif", fq, A, 10, "100k", TI, TR, TF, 10e-6, "rif_mai")]
    out += corsa("sempre" + s, tf=TF, ti=-10, tr=1000, tijk=-10, trjk=1000, **n)
    out += [riga("sempre" + s, "sempre" + s, "rif", fq, A, 10, "100k", TI, TR, TF, 10e-6, "rif_sempre")]
    out += corsa("ev" + s, tf=TF, ti=TI, tr=TR, tijk=T_RELE, trjk=TR, **n)
    out += [riga("ev" + s, "ev" + s, var, fq, A, 10, "100k", TI, TR, TF, 10e-6, "evento",
                 "sempre" + s, "mai" + s, TG_LDR)]
    out += corsa("norele" + s, tf=TF, ti=TI, tr=TR, **n)
    out += [riga("norele" + s, "norele" + s, "rif", fq, A, 10, "100k", TI, TR, TF, 10e-6, "rif_seq")]
    out += [riga("rele" + s, "ev" + s, "rele_contro_norele", fq, A, 10, "100k", T_RELE, TR, TF, 10e-6,
                 "evento", "norele" + s, "norele" + s, 0.0)]
    out += corsa("inv" + s, tf=TFI, ti=TI, tr=TINV, **n)
    out += [riga("inv" + s, "inv" + s, "inversione_d75", fq, A, 10, "100k", TI, TINV, TFI, 10e-6,
                 "evento", "sempre" + s, "mai" + s, 0.75 * TD)]
    out += corsa("evp" + s, tmax=7e-6, tf=TF, ti=TI, tr=TR, tijk=T_RELE, trjk=TR, stati=False, **n)
    out += corsa("invp" + s, tmax=7e-6, tf=TFI, ti=TI, tr=TINV, stati=False, **n)
    for k, t in enumerate((TI, T_RELE, TR)):
        out += [riga("pav_ev%d%s" % (k, s), "evp" + s, "pavimento", fq, A, 10, "100k", t, 1000, TF,
                     7e-6, "pav_num", "ev" + s)]
    out += [riga("pav_inv%s" % s, "invp" + s, "pavimento", fq, A, 10, "100k", TINV, 1000, TFI, 7e-6,
                 "pav_num", "inv" + s)]
    s = "_100k"
    out += corsa("lzmai" + s, amp=0, tf=TF, **n)
    out += [riga("lzmai" + s, "lzmai" + s, "rif", 1000, 0, 10, "100k", TI, TR, TF, 10e-6, "rif_mai")]
    out += corsa("lzsempre" + s, amp=0, tf=TF, ti=-10, tr=1000, tijk=-10, trjk=1000, **n)
    out += [riga("lzsempre" + s, "lzsempre" + s, "rif", 1000, 0, 10, "100k", TI, TR, TF, 10e-6, "rif_sempre")]
    out += corsa("lzev" + s, amp=0, tf=TF, ti=TI, tr=TR, tijk=T_RELE, trjk=TR, **n)
    out += [riga("lzev" + s, "lzev" + s, var, 1000, 0, 10, "100k", TI, TR, TF, 10e-6, "evento",
                 "lzsempre" + s, "lzmai" + s, TG_LDR)]
    out += corsa("lzinv" + s, amp=0, tf=TFI, ti=TI, tr=TINV, **n)
    out += [riga("lzinv" + s, "lzinv" + s, "inversione_d75", 1000, 0, 10, "100k", TI, TINV, TFI, 10e-6,
                 "evento", "lzsempre" + s, "lzmai" + s, 0.75 * TD)]
    return out


def matrice_l29c():
    out = []
    var = "ldr_v4_td6_%s%s" % (CS, CP)

    def rif(nome, fk, amp, tf, g=10, p=0, tmax=None):
        """mai / sempre in mute, allo stato statico (g, p)"""
        f, tm, _ = FREQ[fk] if fk else (1000, 10e-6, 7e-6)
        tm = tmax or tm
        o = corsa("%smai_%s" % (nome, fk or "lz"), amp=amp, f=f, tmax=tm, tf=tf, g1=g, p1=p)
        o += corsa("%ssempre_%s" % (nome, fk or "lz"), amp=amp, f=f, tmax=tm, tf=tf, ti=-10,
                   tr=1000, tijk=-10, trjk=1000, g1=g, p1=p)
        for k in ("mai", "sempre"):
            c = "%s%s_%s" % (nome, k, fk or "lz")
            o += [riga(c, c, "rif", f, amp, g, "100k", TI, T_RELE + 1.0, tf, tm, "rif_" + k, gruppo=0)]
        return o

    # ======== riferimenti: +10 dB lunghi quanto il mute di 20 s; 0 e +3 dB quanto un cambio
    for fk, amp in (("1k", A), ("20", A), (None, 0)):
        out += ["* ---- riferimenti %s ----" % (fk or "senza segnale")]
        out += rif("g10", fk, amp, TF_LUNGO, g=10)
        out += rif("g0", fk, amp, TF_CAMBIO, g=0)
        out += rif("g3", fk, amp, TF_CAMBIO, g=3)
    # il trim a -6 / -12 dB, +10 dB di guadagno: senza segnale e a 1 kHz
    for fk, amp in (("1k", A), (None, 0)):
        out += rif("t6", fk, amp, TF_CAMBIO, g=10, p=6)
        out += rif("t12", fk, amp, TF_CAMBIO, g=10, p=12)
    # ======== 20 kHz, 100 k: il solo riferimento mai in mute a +10 dB (S usa il livello pieno
    # del rif_rel; A con musica e C2 sono diagnostica). ~4 ore a corsa: si lanciano per prime.
    f20k, tm20k, _ = FREQ["20k"]
    tf20k = TF_CAMBIO
    out += ["* ---- 20 kHz ----"]
    out += corsa("g10mai_20k", f=f20k, tmax=tm20k, tf=tf20k, g1=10)
    out += [riga("g10mai_20k", "g10mai_20k", "rif", f20k, A, 10, "100k", TI, T_RELE + 1, tf20k, tm20k,
                 "rif_mai")]

    def rif_nome(pref, k, fk):
        return "%s%s_%s" % (pref, k, fk or "lz")

    # ======== 1: i passaggi di guadagno sotto mute, e a caldo
    PASSI = [(0, 3), (3, 0), (3, 10), (10, 3), (0, 10), (10, 0)]
    for fk, amp in (("1k", A), ("20", A), (None, 0), ("20k", A)):
        if fk == "20k":
            passi = [(0, 10)]
        else:
            passi = PASSI
        f, tm, _ = FREQ[fk] if fk else (1000, 10e-6, 7e-6)
        sfx = fk or "lz"
        for g1, g2 in passi:
            nome = "gm%dx%d_%s" % (g1, g2, sfx)
            out += ["* ---- 1: %d -> %d dB sotto mute, %s ----" % (g1, g2, sfx)]
            out += corsa(nome, amp=amp, f=f, tmax=tm, tf=TF_CAMBIO, ti=TI, tr=TR_CAMBIO,
                         tijk=T_RELE, trjk=TR_CAMBIO, g1=g1, g2=g2, tg=T_CAMBIO)
            gm = "%da%d" % (g1, g2)
            if fk == "20k":
                ri, rr = "-", "g%dmai_20k" % g2
                # la sola riga del cambio e del rilascio: S_rel contro il pieno a G2
                out += [riga(nome + "_c", nome, var, f, amp, gm, "100k", T_CAMBIO, TR_CAMBIO,
                             TF_CAMBIO, tm, "evento", ri, rr, 0.0, 1, "S_rel;B2")]
                continue
            # l'inserzione a G1 (fino al cambio): S_ins con musica, A_ins senza
            out += [riga(nome + "_i", nome, var, f, amp, gm, "100k", TI, T_CAMBIO, TF_CAMBIO, tm,
                         "evento", rif_nome("g%d" % g1, "sempre", fk), rif_nome("g%d" % g1, "mai", fk),
                         TG_LDR, 1, "A_ins;B2" if amp == 0 else "S_ins;B2")]
            # il cambio a rele' chiuso e il rilascio a G2
            out += [riga(nome + "_c", nome, var, f, amp, gm, "100k", T_CAMBIO, TR_CAMBIO, TF_CAMBIO,
                         tm, "evento", rif_nome("g%d" % g2, "sempre", fk),
                         rif_nome("g%d" % g2, "mai", fk), 0.0, 1,
                         "A_ins;A_rel;B2" if amp == 0 else "S_rel;B2")]
            if amp == 0:
                # il cambio A CALDO, criterio 3 di ADR-030: senza mute, stesso passaggio a 1 s
                nc = "gc%dx%d_lz" % (g1, g2)
                out += corsa(nc, amp=0, tf=3.5, g1=g1, g2=g2, tg=TI)
                out += [riga(nc, nc, "caldo", 1000, 0, gm, "100k", TI, 1000, 3.5, 10e-6, "evento",
                             rif_nome("g%d" % g2, "mai", None), "-", 0.0, 1, "A_ins")]
        if fk is None:
            # pavimento numerico di A sul passaggio piu' largo
            nomep = "gm0x10p_lz"
            out += corsa(nomep, amp=0, tmax=7e-6, tf=TF_CAMBIO, ti=TI, tr=TR_CAMBIO, tijk=T_RELE,
                         trjk=TR_CAMBIO, g1=0, g2=10, tg=T_CAMBIO, stati=False)
            for k, t in enumerate((TI, T_CAMBIO, TR_CAMBIO)):
                out += [riga("pav_gm0x10_%d" % k, nomep, "pavimento", 1000, 0, "0a10", "100k", t, 1000,
                             TF_CAMBIO, 7e-6, "pav_num", "gm0x10_lz_i", "-", 0.0, 0, "")]

    # ======== 4: la durata del mute, a +10 dB
    MUTE = [("inv25", TI + 0.25 * TD, None), ("inv50", TI + 0.50 * TD, None),
            ("inv75", TI + 0.75 * TD, None), ("h01", T_RELE + 0.1, T_RELE),
            ("ev", T_RELE + 1.0, T_RELE), ("h2", T_RELE + 2.0, T_RELE), ("h20", T_RELE + 20.0, T_RELE)]
    for fk, amp in (("1k", A), ("20", A), (None, 0), ("20k", A)):
        f, tm, _ = FREQ[fk] if fk else (1000, 10e-6, 7e-6)
        sfx = fk or "lz"
        for m, tr, trele in MUTE:
            if fk == "20k" and m != "h2":
                continue
            nome = "m%s_%s" % (m, sfx)
            d_rel = min((tr - TI) / TD, 1.0)
            tf = tr + d_rel * TD + 3.0
            out += ["* ---- 4: mute %s, %s ----" % (m, sfx)]
            out += corsa(nome, amp=amp, f=f, tmax=tm, tf=tf, ti=TI, tr=tr,
                         tijk=trele if trele else 1000, trjk=tr if trele else 2000)
            tg = TG_LDR if trele else d_rel * TD
            ri = "-" if fk == "20k" else rif_nome("g10", "sempre", fk)
            conta = "A_ins;A_rel;B2" if amp == 0 else "S_ins;S_rel;B2"
            if fk == "20k":
                conta = "S_ins;S_rel;B2"
            out += [riga(nome, nome, var + "_" + m, f, amp, 10, "100k", TI, tr, tf, tm, "evento",
                         ri, rif_nome("g10", "mai", fk), tg, 4, conta)]
        if fk in ("1k", "20"):
            # il rele' al jack contro la stessa sequenza senza rele' (L29b2)
            nn = "mnorele_%s" % sfx
            out += corsa(nn, f=f, tmax=tm, tf=T_RELE + 1.0 + TD + 3.0, ti=TI, tr=T_RELE + 1.0)
            out += [riga(nn, nn, "rif", f, A, 10, "100k", TI, T_RELE + 1, T_RELE + 1 + TD + 3, tm,
                         "rif_seq")]
            out += [riga("rele_%s" % sfx, "mev_%s" % sfx, "rele_contro_norele", f, A, 10, "100k",
                         T_RELE, T_RELE + 1.0, T_RELE + 1.0 + TD + 3.0, tm, "evento", nn, nn, 0.0, 4,
                         "S_ins;S_rel")]
    # pavimento numerico di A sul mute
    out += corsa("mevp_lz", amp=0, tmax=7e-6, tf=T_RELE + 1 + TD + 3, ti=TI, tr=T_RELE + 1,
                 tijk=T_RELE, trjk=T_RELE + 1, stati=False)
    for k, t in enumerate((TI, T_RELE, T_RELE + 1)):
        out += [riga("pav_mev_%d" % k, "mevp_lz", "pavimento", 1000, 0, 10, "100k", t, 1000,
                     T_RELE + 1 + TD + 3, 7e-6, "pav_num", "mev_lz", "-", 0.0, 0, "")]

    # ======== 2: il trim sotto mute, a +10 dB
    TPASSI = [(0, 6), (6, 0), (6, 12), (12, 6), (0, 12), (12, 0)]
    for fk, amp in (("1k", A), (None, 0)):
        f, tm, _ = FREQ[fk] if fk else (1000, 10e-6, 7e-6)
        sfx = fk or "lz"
        for p1, p2 in TPASSI:
            nome = "tm%dx%d_%s" % (p1, p2, sfx)
            out += ["* ---- 2: trim %d -> %d dB sotto mute, %s ----" % (-p1, -p2, sfx)]
            out += corsa(nome, amp=amp, f=f, tmax=tm, tf=TF_CAMBIO, ti=TI, tr=TR_CAMBIO,
                         tijk=T_RELE, trjk=TR_CAMBIO, g1=10, p1=p1, p2=p2, tp=T_CAMBIO)
            ref = lambda p, k: rif_nome("g10" if p == 0 else "t%d" % p, k, fk)
            out += [riga(nome + "_i", nome, var, f, amp, "t%da%d" % (p1, p2), "100k", TI, T_CAMBIO,
                         TF_CAMBIO, tm, "evento", ref(p1, "sempre"), ref(p1, "mai"), TG_LDR, 2,
                         "A_ins;B2" if amp == 0 else "S_ins;B2")]
            out += [riga(nome + "_c", nome, var, f, amp, "t%da%d" % (p1, p2), "100k", T_CAMBIO,
                         TR_CAMBIO, TF_CAMBIO, tm, "evento", ref(p2, "sempre"), ref(p2, "mai"), 0.0, 2,
                         "A_ins;A_rel;B2" if amp == 0 else "S_rel;B2")]
    return out


C += controfattuale() if ARG.matrice == "controfattuale" else matrice_l29c()
C += [".endc", "", ".end"]
os.makedirs(os.path.dirname(os.path.abspath(ARG.uscita)), exist_ok=True)
open(ARG.uscita, "w").write("\n".join(H + C) + "\n")
n = sum(1 for r in C if r.startswith("tran "))
print("scritto %s: matrice %s, curve %s %s, %d corse" % (ARG.uscita, ARG.matrice, CS, CP, n))
