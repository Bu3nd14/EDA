#!/usr/bin/env python3
"""L29c: genera spice/preamp/tb/tb_v2_casopeggiore.cir, il deck VERSIONATO del caso peggiore di
V2 col mute reale (NC-028). Da L47c2b1 il mute TAGLIA coi soli rele' al jack (ADR-062, PR-21):
niente fotoresistenze, niente profilo, niente S. Il deck non si edita a mano: si rigenera.

L47c2b1 (2026-10-05). Fino a L47b2b1 qui c'erano due LDR a monte del blocco A col loro profilo
(ADR-038/039/040, poi la NSL-32SR3 di ADR-058..061); le ha tolte ADR-062. L'ultima versione che le
genera e' quella del commit dffa7148. Con loro sono uscite le matrici che esistevano solo per la
sfumatura: `l29c` (le inversioni a d = 0,25 / 0,5 / 0,75) e `curve` (le curve A-E della cella).
La sorgente torna sulla RSRC del blocco CANALE, come nella cella di L40.

Uso:
  /usr/bin/python3 genera_tb_v2_casopeggiore.py [--matrice sorgente|...] [--uscita PATH]

  --matrice sorgente        (default) la matrice di L29d2 sul sorgente, scritta nel deck versionato
  --matrice controfattuale  la cella di L40 (1 kHz, 100 k) con TUTTE le aggiunte di questo banco
                            in posizione neutra: deve ridare la stessa cella di tb_v2_mute_taglio.cir
  --matrice caldo          il cambio di guadagno A CALDO (criterio 3 di ADR-030), coi suoi
                            riferimenti, in un deck a parte: K1 e K5 hanno anche il contatto
                            comportamentale del blocco (fronte 4,55 us), che commuta al posto
                            dell'interruttore nativo. Con l'interruttore netto il cambio a caldo
                            che muove K5 si ferma su 'Timestep too small' a un rimbalzo.
  --matrice sonda_l29d      L29d: la sonda del contatto IN SERIE al jack (NC-028), sulle celle
                            peggiori di L29c, in cinque geometrie (N, iA, iB, ii, iii): vedi
                            SONDA L29D in fondo a questa intestazione. Si scrive nei dati di L29d.
  --matrice l30             L30 (ADR-046): lo spegnimento morbido, il guasto dell'alimentatore e i
                            controfattuali, sul sorgente come 'sorgente', col gemello di K1/K5 come
                            'caldo'. Si scrive nei dati di L30 (README li' accanto).
  --matrice l41c --ponte D  L41c (NC-036): il banco di l30 con le forme d'onda del circuito vero
                            dell'alimentatore (rail, istanti dei contatti), dai JSON del ponte. Da
                            L47c2b1 senza le correnti delle stringhe LED (non ci sono piu'). Si
                            scrive nei dati del lotto che la corre (README li' accanto).

I TEMPI DEL MUTE (L47c2b1, il firmware di L47c2a: data/2026-10-05/L47c2a/seq/analisi_seq.txt).
Il tasto a t_ins; MUTE_CMD cade T_CMD = 21 ms dopo (20 ms di antirimbalzo piu' il passo del
firmware; 21,10 ms misurati sul circuito al rilascio); il contatto in serie si apre T_RIL = 3 ms
dopo il comando (il rilascio massimo del G6K, come in L30) e la derivazione lato condensatore
chiude TT = 1 ms dopo ancora (geometria iii, geo_alter). Al rilascio lo stesso ritardo, con
l'intervento massimo (<= 3 ms, REQUIREMENTS V2). PERMIT_CMD cade Delta dopo MUTE_CMD (ADR-045):
il cambio di guadagno o di trim sotto mute sta a T_RELE + 0,5 s, ben oltre.

Poi si corre come tb_v2_mute_taglio.cir: sed @REPO@, dividi.py, una corsa per processo,
v2_metodo.py analizza. Il manifesto ha due colonne in piu', ignorate da analizza:
  gruppo  il punto del mandato di L29c (1 guadagno, 2 trim, 3 dispersione, 4 durata del mute,
          5 accensione e spegnimento; 0 riferimenti e pavimenti)
  conta   le grandezze che la riga porta al verdetto (A_ins, A_rel, B2; con la musica B2g, il
          jack grezzo, ADR-063) o alla tabella del clic (C2_ins, C2_rel e, con la musica, B2: la
          coda del filtro dopo il taglio; DICHIARATE, senza soglia, ADR-062 e ADR-063), separate
          da ';'. Il resto che analizza scrive e' diagnostica.

IL CONTATTO IN SERIE (L47c2b1, ADR-063): e' BSERx del blocco CANALE, col suo fronte di ~4,55 us,
e non l'interruttore nativo SKSx, che resta aperto (geo_alter).

COSA C'E' DENTRO, oltre a tb_v2_mute_taglio.cir. Il blocco CANALE e' byte per byte quello
di tb_v2_mute_graduale.cir (v2_metodo.py canale): tutto si aggiunge FUORI.
- I contatti del guadagno che commutano nel tempo: K1 (RGB) e K5 (RG10B), interruttori nativi
  (SW, come tb_switch_v2.cir) in parallelo a RRGB/RRG10B (1 G nel blocco, con i loro 15 pF),
  chiusi a 100 mohm, coi rimbalzi del contatto al jack (BSJKR) ma senza il suo fronte da
  4,55 us: la conduttanza comportamentale rendeva l'op dipendente dal percorso (limitations
  #33). Sequenza di tb_switch_v2.cir:
  0 -> +10 con K5 per primo e K1 0,3 ms dopo; +10 -> 0 con K1 per primo.
- Il trim (ADR-027, candidato 2 di trim.py): RATTT del blocco aperto (alter rattt = 1e12), la
  scala 845 / 464 / 464 da OUTA, i quattro contatti T1R, T1S, T2R, T2S con 15 pF ciascuno, i
  100 pF del cablaggio e RATTH (la parte alta dell'attenuatore) fino a W. RATTB del blocco e' la
  parte bassa. Un rele' del trim e' un deviatore: il contatto che apre apre a t, quello che chiude
  chiude 1 ms dopo (ipotesi dichiarata: il tempo di trasferimento non e' nel datasheet letto).
- La dispersione: VOSA / VOSB / VOSF1 / VOSF2 del blocco (offset d'ingresso), e il gruppo B di
  ADR-031 con `altermod lsk489a vto` e la sonda JPRB su nodi propri (docs/limitations.md #29).
- I rail: `alter @vpp[pwl]` / `alter @vmm[pwl]` sulle sorgenti DC del blocco (sonda di L29c:
  l'op parte dal valore della PWL a t = 0, malgrado la nota «dc value used for op»). Il terzo
  elemento della terna `rail` (il comando dei LED, VPWL fino a L47b2b1) e' ignorato da corsa().
- IOSA (L47b2b1, limitations #44): la corrente che VOSA fa scorrere in R113 dentro il blocco.
- `set numdgt=15` prima di ogni wrdata (#30). Nessun corpo di `if` vuoto (#32).

IPOTESI DI ACCENSIONE E SPEGNIMENTO (ADR-039 non le fissa; l'alimentatore e' di L30):
- accensione: rele' del jack chiuso (NC diseccitato); rail
  da 0 a +-15 V in TR_RAIL; il temporizzatore rilascia 2,5 s dopo l'inizio della rampa;
- spegnimento: da regime, rail a 0 in TR_RAIL; nessuna dissolvenza (caso peggiore: il comando
  non se ne accorge); il rele' del jack si chiude con un ritardo dall'inizio della discesa.

SONDA L29D (--matrice sonda_l29d; decisione dell'utente del 2026-09-25: sonda, poi ci si ferma).
Il contatto in serie fra il condensatore d'uscita e il jack, sulle tre uscite, FUORI dal blocco:
- la serie: interruttore nativo SWK (0,1 ohm) in parallelo a BSERx (tenuto aperto: vtiser = -10)
  e al ponte RBYx (aperto: 1e12). Contatto aperto = 5 pF fra i capi (IPOTESI: "qualche pF");
  nessun cavo al jack (caso peggiore per il passaggio capacitivo);
- la derivazione lato CONDENSATORE (solo iii): interruttore nativo SWK da MAINC / FIXCx a massa;
- la derivazione lato jack e' BJKx del blocco (vtijk / vtrjk), com'era in L29c;
- con la serie il lato condensatore ha il bleed di L29a: rbcm = 220k, rbc1 = rbc2 = 470k
  (IPOTESI; nel blocco e' 1 T: col contatto aperto il nodo sarebbe sospeso);
- trasferimento fra i contatti 1 ms (IPOTESI, la stessa del trim).
Geometrie (t_ins / t_rel = chiusura / apertura del rele' al jack di L29c):
  N    neutra = L29c: serie sempre chiusa, ponte 1 m, bleed 1 T, derivazione jack t_ins..t_rel
  iA   serie apre a t_ins, derivazione jack chiude +1 ms; rilascio: derivazione apre, serie +1 ms
  iB   come iA all'inserzione; rilascio: serie chiude a t_rel, derivazione apre +1 ms
  ii   serie sola: apre a t_ins, chiude a t_rel
  iii  serie apre a t_ins, derivazione lato condensatore chiude +1 ms; rilascio all'inverso
All'accensione ogni geometria parte a riposo (t_ins = -10): serie aperta, derivazione chiusa.

MATRICE L29D2 (--matrice l29d2): la matrice di L29c sulla geometria iii. Decisioni dell'utente
del 2026-09-25, con le sue parole:
- geometria: «iii»;
- stato sicuro: «Il bleed basta» (a riposo il jack va a massa attraverso il bleed, nessun polo in
  piu');
- valori: «C dal datasheet + cavo realistico». Contatto aperto CK_DS = 0,1 pF (0,075-0,080 pF
  dalla curva d'isolamento del G6K, per eccesso: data/2026-09-25/L29d2/script/c_contatto.py);
  cavo al jack 0 pF (caso peggiore) e 100 pF (variante c100). Bleed 220k / 470k e
  trasferimento 1 ms invariati.
Varianti nello stesso deck, scelte dal regex di corri.sh: "" (0 pF, 100 k), c100 (cavo 100 pF),
r10k (carico 10 k), k5 (contatto 5 pF, il ponte con la sonda L29d). Nomi: la cella di L29c, poi
_<variante>, poi _iii. Il controfattuale N ha i nomi della sonda L29d (controfattuale_N.py).
"""
import argparse
import math
import os

QUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(QUI, *[".."] * 6))
ap = argparse.ArgumentParser()
RITIRATE = ("l29c", "curve")   # L47c2b1: esistevano solo per la sfumatura (ADR-062)
ap.add_argument("--matrice", default="sorgente",
                choices=("sorgente", "controfattuale", "caldo", "sonda_l29d", "l29d2", "l30", "l41c")
                + RITIRATE)
ap.add_argument("--ponte", default=None,
                help="solo --matrice l41c: la cartella dei JSON di ponte/estrai_ponte.py (L41c)")
ap.add_argument("--netlist", default=os.path.join(REPO, "circuits", "preamp", "preamp_audio.net"),
                help="solo --matrice sorgente: la netlist da cui leggere il mute (L29e)")
ap.add_argument("--uscita", default=os.path.join(REPO, "spice", "preamp", "tb", "tb_v2_casopeggiore.cir"))
ARG = ap.parse_args()
if ARG.matrice in RITIRATE:
    raise SystemExit("--matrice %s esisteva solo per la sfumatura delle fotoresistenze, tolta da "
                     "ADR-062 (L47c2b1): si genera dal commit dffa7148" % ARG.matrice)
TB = os.path.join(REPO, "spice", "preamp", "tb", "tb_v2_mute_graduale.cir")

righe = open(TB).read().splitlines()
i0 = next(i for i, r in enumerate(righe) if r.startswith("* >>> CANALE"))
i1 = next(i for i, r in enumerate(righe) if r.startswith("* <<< CANALE"))
inc = [r for r in righe[:i0] if r.startswith(".include")]
CANALE = righe[i0:i1 + 1]

# ---------------------------------------------------------------- i tempi (L47c2b1, ADR-062)
# Il mute taglia: nessuna dissolvenza, il contatto al jack si muove T_ATT dopo il tasto. t_ins e
# t_rel del manifesto sono gli istanti del TASTO; i contatti stanno T_ATT dopo (intestazione).
TI = 1.0                          # il tasto del mute
T_CMD = 0.021                     # MUTE_CMD dopo il tasto: firmware di L47c2a (21,10 ms misurati)
T_RIL = 3e-3                      # il rilascio / l'intervento massimo del G6K (en-g6k.pdf p. 3)
T_ATT = T_CMD + T_RIL             # dal tasto al contatto in serie
T_RELE = TI + T_ATT               # il contatto in serie si apre
TG = T_ATT                        # t_grad di una riga d'inserzione: B2 parte da t_ins + TG + 20 ms
A = 3.818                         # 2,7 V RMS
FREQ = {"20": (20, 10e-6, 7e-6), "1k": (1000, 10e-6, 7e-6), "20k": (20000, 0.5e-6, 0.35e-6)}
# il cambio di guadagno o di trim, a rele' aperto, ben oltre Delta. 2 s dopo il contatto: A
# all'inserimento (la riga _i finisce al cambio) vuole una finestra >= 2 s (ADR-032), che la
# prima stesura di L47c2b1 (0,5 s) non dava («finestra corta: non accetta», 29 righe)
T_CAMBIO = T_RELE + 2.0
TR_CAMBIO = T_CAMBIO + 2.0        # il tasto del rilascio: 2 s dopo il cambio, finestra piena di A
TF_CAMBIO = TR_CAMBIO + 3.0       # A vuole >= 2 s dopo il contatto del rilascio
TF_LUNGO = TI + 20.0 + 3.0        # il mute di 20 s: i riferimenti durano quanto lui

# ---------------------------------------------------------------- i contatti che commutano
MAKE = "-1e4,0, 0,0, 1u,1, 150u,1, 151u,0, 300u,0, 301u,1, 450u,1, 451u,0, 520u,0, 521u,1, 1e4,1"
BREAK = "-1e4,1, 0,1, 1u,0, 400u,0, 401u,1, 600u,1, 601u,0, 1e4,0"


def contatto(n, a, b, cpar):
    out = [
        "V%sI N%sI 0 DC 0" % (n, n),
        "V%sT N%sT 0 DC 1000" % (n, n),
        "B%sR S%sR 0 V = (1 - V(N%sI)) * pwl(time - V(N%sT), %s)" % (n, n, n, n, MAKE),
        "+ + V(N%sI) * pwl(time - V(N%sT), %s)" % (n, n, BREAK),
        # L29c: interruttore NATIVO comandato dalla pwl coi rimbalzi, come tb_switch_v2.cir (L27).
        # La conduttanza comportamentale pow(10, -12 + 13 s) del blocco, usata qui dentro l'anello
        # (K1/K5) e in serie al segnale (trim), rendeva l'op dipendente dal percorso: il 'transient
        # op' finiva in uno stato incollato al rail, e nessuna opzione lo sistemava in tutte le
        # corse (sonde/op/, limitations #33). Commutazione netta, senza il fronte di 4,55 us:
        # dichiarata.
        "S%s %s %s S%sR 0 SWK" % (n, a, b, n),
    ]
    if cpar:
        # contatto aperto = 1 G + 15 pF, la convenzione del blocco (RRGB, CRGB) e di
        # tb_e3_e5_ldr.cir. Senza l'1 G il nodo T2C del deviatore resta appeso ai soli 1e-12 S
        # nelle prime iterazioni e l'op fallisce (gmin e source stepping): trovato nella prova
        # di fumo di L29c.
        out += ["C%sP %s %s 15p" % (n, a, b), "R%sP %s %s 1G" % (n, a, b)]
    return out


CONTATTI = ("K1", "K5", "T1R", "T1S", "T2R", "T2S")


def sonda_aggiunte(ck="5p", cavo=False):
    """L29d: la serie (KS, chiusa a riposo) e la derivazione lato condensatore (KC, aperta a
    riposo), un comando per tipo sulle tre uscite. Due eventi per corsa, coi rimbalzi di L29c:
      serie        c = BREAK(t - t_apre) + MAKE(t - t_chiude)     (1 prima, 0 in mezzo, 1 dopo)
      derivazione  c = MAKE(t - t_chiude) + BREAK(t - t_apre) - 1 (0 prima, 1 in mezzo, 0 dopo)
    Tempi di riposo 1000 / 2000: lo stato fermo. pwl() estrapola (limitations #31): i punti
    estremi +-1e4 coprono ogni t - V(N..) di queste corse."""
    out = ["* ---- L29d: il contatto in serie al jack e la derivazione lato condensatore ----",
           "VKSA NKSA 0 DC 1000", "VKSB NKSB 0 DC 2000",
           "BKSR NKSR 0 V = pwl(time - V(NKSA), %s) + pwl(time - V(NKSB), %s)" % (BREAK, MAKE),
           "VKCA NKCA 0 DC 1000", "VKCB NKCB 0 DC 2000",
           "BKCR NKCR 0 V = pwl(time - V(NKCA), %s) + pwl(time - V(NKCB), %s) - 1" % (MAKE, BREAK)]
    for x, c, j in (("M", "MAINC", "MAINJACK"), ("1", "FIXC1", "FIXJACK1"), ("2", "FIXC2", "FIXJACK2")):
        out += ["SKS%s %s %s NKSR 0 SWK" % (x, c, j), "CKS%s %s %s %s" % (x, c, j, ck),
                "SKC%s %s 0 NKCR 0 SWK" % (x, c)]
        if cavo:
            # L29d2: il cavo al jack, 1e-18 = nessun cavo; la corsa lo altera (variante c100)
            out += ["CCAV%s %s 0 1e-18" % (x, j)]
    return out + [""]


TT = 1e-3   # L29d: il trasferimento fra i contatti (ipotesi, come il trim)
CK_DS = "0.1p"   # L29d2: il contatto aperto dal datasheet del G6K (c_contatto.py), per eccesso


RBC_BANCO = {"m": "220k", "1": "470k", "2": "470k"}   # L29d2: il bleed lato condensatore
RBC = RBC_BANCO   # --matrice sorgente lo sostituisce coi valori letti dalla netlist (L29e)


def geo_alter(geo, tijk, trjk, rbc=RBC_BANCO):
    """L29d: le alter di una geometria, date t_ins / t_rel del rele' al jack di L29c. Vengono
    DOPO le alter vtijk / vtrjk di corsa() e le sostituiscono."""
    ks, kc, jk = (1000, 2000), (1000, 2000), (tijk, trjk)
    if geo == "iA":
        ks, jk = (tijk, trjk + TT), (tijk + TT, trjk)
    elif geo == "iB":
        ks, jk = (tijk, trjk), (tijk + TT, trjk + TT)
    elif geo == "ii":
        ks, jk = (tijk, trjk), (1000, 2000)
    elif geo == "iii":
        ks, kc, jk = (tijk, trjk + TT), (tijk + TT, trjk), (1000, 2000)
    elif geo != "N":
        raise SystemExit("geometria sconosciuta: %s" % geo)
    serie = geo != "N"
    # L47c2b1 (ADR-063, scelta dell'utente: «Tutta la matrice»): con la serie, il contatto in serie
    # e' BSERx del blocco CANALE (conduttanza pow(10, -12 + 13*(1 - SSER)), SSER dai rimbalzi
    # filtrati da 1 k + 4,55 nF: un fronte di ~4,55 us), e l'interruttore nativo SKSx resta APERTO
    # (vksa = -10, vksb = 1000). L'interruttore ideale si fermava su 'Timestep too small' ogni volta
    # che si chiudeva con volt di musica ai suoi capi (data/2026-10-05/L47c2b1/sonda/). Con N il
    # nativo resta chiuso com'era (ks = 1000 / 2000) e BSERx chiuso.
    if serie:
        nat, ser = ("-10", "1000"), ("%.6f" % ks[0], "%.6f" % ks[1])
    else:
        nat, ser = ("%.6f" % ks[0], "%.6f" % ks[1]), ("1000", "2000")
    return [
        "alter vtijk dc = %.6f" % jk[0], "alter vtrjk dc = %.6f" % jk[1],
        "alter vksa dc = %s" % nat[0], "alter vksb dc = %s" % nat[1],
        "alter vkca dc = %.6f" % kc[0], "alter vkcb dc = %.6f" % kc[1],
        "alter vtiser dc = %s" % ser[0],
        "alter vtrser dc = %s" % ser[1],
    ] + ["alter %s = %s" % (r, "1m" if not serie else "1e12") for r in ("rbym", "rby1", "rby2")] + [
        "alter rbcm = %s" % ("1e12" if not serie else rbc["m"]),
        "alter rbc1 = %s" % ("1e12" if not serie else rbc["1"]),
        "alter rbc2 = %s" % ("1e12" if not serie else rbc["2"]),
    ]


def gemello(n, a):
    """Il contatto comportamentale del blocco (BSJKR: pwl coi rimbalzi, 1 k + 4,55 nF, conduttanza
    log-lineare fino a 10 S), in parallelo all'interruttore nativo. Solo nel deck 'caldo'."""
    m = n + "B"
    return [
        "V%sI N%sI 0 DC 0" % (m, m),
        "V%sT N%sT 0 DC 1000" % (m, m),
        "B%sR S%sR 0 V = (1 - V(N%sI)) * pwl(time - V(N%sT), %s)" % (m, m, m, m, MAKE),
        "+ + V(N%sI) * pwl(time - V(N%sT), %s)" % (m, m, BREAK),
        "R%sS S%sR S%s 1k" % (m, m, m),
        "C%sS S%s 0 4.55n" % (m, m),
        "B%s %s 0 I = V(%s) * pow(10, -12 + 13*V(S%s))" % (m, a, a, m),
    ]
AGGIUNTE = (
    ["* ---- L29c: i contatti del guadagno, in parallelo a RRGB / RRG10B del blocco ----",
     "* interruttore nativo: 0,1 ohm chiuso (il massimo del G6K), 1 T aperto; soglia 0,5 V sulla",
     "* pwl 0/1 dei rimbalzi, isteresi 0,25 V",
     ".model SWK SW(RON=0.1 ROFF=1e12 VT=0.5 VH=0.25)"]
    + contatto("K1", "RGB", "0", False) + contatto("K5", "RG10B", "0", False)
    + (gemello("K1", "RGB") + gemello("K5", "RG10B") if ARG.matrice in ("caldo", "l30", "l41c") else [])
    + (sonda_aggiunte() if ARG.matrice == "sonda_l29d" else [])
    + (sonda_aggiunte(CK_DS, True) if ARG.matrice in ("l29d2", "sorgente", "l30", "l41c") else [])
    + ["* ---- L29c: il trim (ADR-027, trim.py candidato 2) fra OUTA e l'attenuatore ----",
       "* RATTT del blocco si apre nel .control (alter rattt = 1e12): OUTA arriva a W da qui.",
       "RL1 OUTA TAP6 845", "RL2 TAP6 TAP12 464", "RL3 TAP12 0 464"]
    + contatto("T1R", "OUTA", "ATOP", True) + contatto("T1S", "T2C", "ATOP", True)
    + contatto("T2R", "TAP6", "T2C", True) + contatto("T2S", "TAP12", "T2C", True)
    + ["CWIRE ATOP 0 100p", "RATTH ATOP W 1m",
       "* ---- L29c: la sonda del gruppo B (limitations #29), su nodi propri (#24) ----",
       "VPRBD PRBD 0 DC 15", "VPRBG PRBG 0 DC 0", "JPRB PRBD PRBG 0 LSK489A",
       "* ---- L29c: il punto di partenza di Newton per l'op (limitations #33) ----",
       "* Con l'interruttore del trim fra OUTA e W il blocco A ha una seconda soluzione in continua,",
       "* agganciata al rail (+13 V): gmin e source stepping falliscono e il 'transient op' finisce",
       "* li', 'successfully'. Il nodeset e' solo il primo tentativo di Newton: la soluzione resta",
       "* una soluzione del circuito, e ridà quella del deck di main (sonde/op/, controfattuale).",
       ".nodeset V(OUTA)=0 V(W)=0 V(ATOP)=0 V(OUTB)=0 V(MAIN_A)=0 V(OUTF1)=0 V(OUTF2)=0",
       ""]
)

H = [
    "tb_v2_casopeggiore.cir - V2 al jack, il caso peggiore col mute che taglia coi soli rele' al jack (ADR-062): guadagno, trim, dispersione, durata del mute, accensione (L29c, NC-028, L47c2b1)",
    "* Prima riga = titolo (docs/limitations.md #10).",
    "* GENERATO da docs/preamp/data/2026-09-23/L29c/deck/genera_tb_v2_casopeggiore.py: non si",
    "* edita a mano. L'intestazione del generatore dice cosa c'e' dentro, le ipotesi di",
    "* accensione e spegnimento, e come si corre. Matrice: %s." % ARG.matrice,
    "*",
    "* NIENTE FOTORESISTENZE (ADR-062, L47c2b1): la sorgente arriva al blocco A dalla sua RSRC,",
    "* come nella cella di L40. Ogni dispositivo attivo e' il modello del",
    "* costruttore in models/ (L39); nessuno porta la dispersione, che qui si inietta: VOS* e",
    "* `altermod lsk489a vto` (gruppo B, ADR-031). UN MODELLO ALTERATO PORTA ANCORA IL NOME",
    "* LSK489A (limitations #29): le corse alterate lo dicono nel nome (_gb*) e stampano showmod",
    "* e la corrente della sonda JPRB.",
    "*",
    "* IL MUTE TAGLIA: il contatto in serie al jack si apre %g ms dopo il tasto (MUTE_CMD 21 ms," % (T_ATT * 1e3),
    "* firmware di L47c2a, piu' 3 ms del G6K), la derivazione 1 ms dopo; al rilascio lo stesso.",
    "* t_ins e t_rel del manifesto sono gli istanti del tasto.",
    "* ANALISI: scripts/v2_metodo.py analizza sul manifesto; le colonne gruppo e conta dicono",
    "* quali grandezze di ogni riga sono verdetto. Si corre DIVISO (dividi.py): le corse di",
    "* accensione alterano le sorgenti dei rail, e in sequenza l'alterazione resterebbe.",
    "* CONVENZIONE DI PERCORSO: `.include @REPO@/...` (tb_op.cir, L2-L3).",
    "",
] + inc + [""] + CANALE + [
    "* ---- L47b2b1: IOSA fornisce a R113 (dentro il blocco A) la corrente dovuta a VOSA, che",
    "* nel circuito non passa nella rete d'ingresso: vedi iosa() nel generatore, limitations #44 ----",
    "IOSA INAX 0 DC 0",
    "",
] + AGGIUNTE

if ARG.matrice in ("sorgente", "l30", "l41c"):
    H[5:5] = [
        "* MATRICE sorgente (L29e, ADR-044): il mute al jack e' la geometria iii com'e' in",
        "* circuits/preamp/preamp_audio.net - un deviatore per uscita, COM al lato del condensatore,",
        "* NC a massa, NO al jack. Il generatore la LEGGE dalla netlist col controllo del 2e e rifiuta",
        "* se non c'e'; i bleed lato condensatore (rbcm/rbc1/rbc2) sono i valori della netlist, il",
        "* bleed del jack deve coincidere con RBLx del blocco. Dal banco restano: il contatto aperto",
        "* 0,1 pF (datasheet, L29d2), il trasferimento 1 ms (ipotesi) e 0 pF di cavo (caso peggiore).",
        "* Nomi e righe sono quelli di L29d2 (suffisso _iii), variante di progetto.",
    ]

MAN = "tb_v2_casopeggiore_manifest.csv"
C = [
    ".control",
    "* limitations #30: il tempo a 16 cifre, prima di ogni wrdata",
    "set numdgt=15",
    "set d = .dat",
    "* L29c: corri.sh rifiuta ogni corsa col 'Transient op' nel log (limitations #33).",
    "save v(mainjack) v(fixjack1) v(fixjack2) v(ina) v(vplus) v(vminus) v(main_a)",
    'echo "cella,file,variante,f_hz,amp,gm,rl,t_ins,t_rel,t_fine,tmax,tipo,rif_ins,rif_rel,t_grad,gruppo,conta" > %s' % MAN,
    "* la sorgente arriva dalla RSRC del blocco, col selettore chiuso (L47c2b1: niente LDR)",
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


def iosa(vos):
    """L47b2b1 (scelta dell'utente: correggere il banco): la corrente che VOSA fa scorrere in R113
    (1 Mohm, dentro il blocco A, fra INAX e massa) la fornisce IOSA, non la rete delle celle. Nel
    circuito R_IN sta sul gate e un offset del differenziale non manda corrente nell'ingresso; col
    banco di prima 20 nA passavano nelle due fotoresistenze e a meta' sfumatura davano un click di
    211 uV (A), 0,38 uV senza (data/2026-10-03/L47b2b1/v2/cf_offset/; limitations #44)."""
    s = str(vos)
    v = float(s[:-1]) * 1e-3 if s.endswith("m") else float(s)
    return "%.6g" % (v / 1e6)


def corsa(nome, amp=A, f=1000, tmax=10e-6, tf=17.5, ti=1000, tr=2000, tijk=None, trjk=None,
          g1=10, g2=None, tg=1000, p1=0, p2=None, tp=1000, vos=(0, 0, 0, 0), att="max",
          rl="100k", trim_montato=True, cwire="100p", vto=None, rail=None, stati=True, geo=None,
          ck=None, cavo=None):
    """ti / tr: il tasto del mute e del rilascio (L47c2b1, ADR-062). I contatti del jack si
    muovono T_ATT dopo, salvo tijk / trjk dati (accensione, spegnimento, riferimenti 'sempre',
    L30 e L41c, dove non c'e' un tasto). 1000 / 2000 = mai."""
    tijk = ti + T_ATT if tijk is None else tijk
    trjk = tr + T_ATT if trjk is None else trjk
    out = [
        "alter vamp dc = %s" % amp,
        "alter vfrq dc = %s" % f,
        "alter rldm = %s" % rl, "alter rld1 = %s" % rl, "alter rld2 = %s" % rl,
        "alter vtijk dc = %.6f" % tijk, "alter vtrjk dc = %.6f" % trjk,
        "alter vosa dc = %s" % vos[0], "alter iosa dc = %s" % iosa(vos[0]),
        "alter vosb dc = %s" % vos[1],
        "alter vosf1 dc = %s" % vos[2], "alter vosf2 dc = %s" % vos[3],
        "alter ratth = %s" % ATT[att][0], "alter rattb = %s" % ATT[att][1],
        "alter rl1 = %s" % ("845" if trim_montato else "1e12"),
        "alter cwire = %s" % cwire,
    ]
    st = {}
    st.update(cambio_guadagno(g1, g2, tg))
    st.update(cambio_trim(p1, p2, tp))
    if ARG.matrice in ("caldo", "l30", "l41c"):
        # il guadagno lo portano i gemelli comportamentali; gli interruttori nativi restano aperti
        for n in ("K1", "K5"):
            i, t = st[n]
            out += ["alter v%sbi dc = %s" % (n.lower(), i), "alter v%sbt dc = %.6f" % (n.lower(), t)]
            st[n] = (0, 1000)
    for n in CONTATTI:
        i, t = st[n]
        out += ["alter v%si dc = %s" % (n.lower(), i), "alter v%st dc = %.6f" % (n.lower(), t)]
    if geo is not None:
        out += geo_alter(geo, tijk, trjk, RBC)
    if ck is not None:
        # L29d2: il contatto aperto e il cavo, reimpostati da ogni corsa; la tabella dell'op li
        # stampa (una variante sul nome sbagliato non cambierebbe niente: limitations #29)
        out += ["alter %s = %s" % (c, ck) for c in ("cksm", "cks1", "cks2")]
        out += ["alter %s = %s" % (c, cavo) for c in ("ccavm", "ccav1", "ccav2")]
        out += ["print @cksm[capacitance] @cks1[capacitance] @cks2[capacitance]"
                " @ccavm[capacitance] @ccav1[capacitance] @ccav2[capacitance]"]
    if vto is not None:
        out += ["altermod lsk489a vto = %s" % VTO[vto],
                "showmod jprb : vto beta",
                # la corrente della sonda si legge nella tabella dell'op, riga vprbd#branch
                # (un print di i(vprbd) non la trova: il save non la tiene)
                "op"]
        # niente destroy qui: dividi.py chiude una corsa al primo "destroy all"
    if rail is not None:
        # il terzo elemento (il comando dei LED, VPWL) non c'e' piu' da L47c2b1: ignorato
        vp, vm = rail[:2]
        out += ["alter @vpp[pwl] = [ %s ]" % vp, "alter @vmm[pwl] = [ %s ]" % vm]
    out += ["tran %g %s 0 %g" % (tmax, tf, tmax),
            "wrdata %s$d v(mainjack) v(fixjack1) v(fixjack2)" % nome]
    if stati:
        out.append("wrdata %s_stati$d v(ina) v(vplus) v(vminus) v(main_a)" % nome
                   + (" v(mainc) v(fixc1) v(fixc2)" if geo is not None else ""))
    return out + ["destroy all"]


def riga(cella, file, var, f, amp, gm, rl, ti, tr, tf, tmax, tipo, rins="-", rrel="-", tg=0.0,
         gruppo=0, conta=""):
    return 'echo "%s,%s.dat,%s,%s,%s,%s,%s,%s,%s,%s,%g,%s,%s,%s,%s,%s,%s" >> %s' % (
        cella, file, var, f, amp, gm, rl, ti, tr, tf, tmax, tipo, rins, rrel, tg, gruppo, conta, MAN)


# ---------------------------------------------------------------- le matrici
def controfattuale():
    """La cella di L40 (1 kHz, 100 k), corse e righe come genera_tb_v2_mute_taglio.py, con le
    aggiunte neutre: guadagno +10 statico dai contatti nuovi, trim smontato (RL1 aperto, T1R
    chiuso), niente cablaggio, VOS 0, attenuatore al massimo. Il mute e' il contatto del blocco
    (geometria N), come nel deck del taglio: L47c2b1, senza fotoresistenze ne' inversioni."""
    n = dict(trim_montato=False, cwire="1e-18")
    TR, TF = TI + 1.0, TI + 1.0 + 3.0
    s, var, fq = "_1k_100k", "taglio", 1000
    out = []
    out += corsa("mai" + s, tf=TF, **n)
    out += [riga("mai" + s, "mai" + s, "rif", fq, A, 10, "100k", TI, TR, TF, 10e-6, "rif_mai")]
    out += corsa("sempre" + s, tf=TF, tijk=-10, trjk=1000, **n)
    out += [riga("sempre" + s, "sempre" + s, "rif", fq, A, 10, "100k", TI, TR, TF, 10e-6, "rif_sempre")]
    out += corsa("ev" + s, tf=TF, ti=TI, tr=TR, **n)
    out += [riga("ev" + s, "ev" + s, var, fq, A, 10, "100k", TI, TR, TF, 10e-6, "evento",
                 "sempre" + s, "mai" + s, TG)]
    out += corsa("evp" + s, tmax=7e-6, tf=TF, ti=TI, tr=TR, stati=False, **n)
    for k, t in enumerate((TI, TR)):
        out += [riga("pav_ev%d%s" % (k, s), "evp" + s, "pavimento", fq, A, 10, "100k", t, 1000, TF,
                     7e-6, "pav_num", "ev" + s)]
    s = "_100k"
    out += corsa("lzmai" + s, amp=0, tf=TF, **n)
    out += [riga("lzmai" + s, "lzmai" + s, "rif", 1000, 0, 10, "100k", TI, TR, TF, 10e-6, "rif_mai")]
    out += corsa("lzsempre" + s, amp=0, tf=TF, tijk=-10, trjk=1000, **n)
    out += [riga("lzsempre" + s, "lzsempre" + s, "rif", 1000, 0, 10, "100k", TI, TR, TF, 10e-6, "rif_sempre")]
    out += corsa("lzev" + s, amp=0, tf=TF, ti=TI, tr=TR, **n)
    out += [riga("lzev" + s, "lzev" + s, var, 1000, 0, 10, "100k", TI, TR, TF, 10e-6, "evento",
                 "lzsempre" + s, "lzmai" + s, TG)]
    return out


# ======== 3: la dispersione dell'LSK489, senza segnale, a +10 dB
# Il gradino d'offset e' lineare negli offset d'ingresso: il caso peggiore ha i VOS che si
# SOMMANO alla parte sistematica del blocco (-15,45 mV, L40), il segno opposto e' il controllo.
# ATTENZIONE AL SEGNO: VOSB sta fra W (+) e WB (-), quindi VOS = +20 mV porta il gate a W - 20 mV
# e si somma alla parte sistematica. Il peggiore e' "p", non "n" (misurato in L29c: 267 contro
# 31 uV sul cambio sotto mute; la prima stesura di questo commento diceva il contrario). VOSF1 / VOSF2 a +20 / -20 mV sempre (le fisse non cambiano guadagno). Il gruppo B
# e' l'altermod del Vto (ADR-031) con la sonda; "a" e' il modello del costruttore com'e'.
DISP_VOS = {"n": ("-20m", "-20m", "20m", "-20m"), "p": ("20m", "20m", "20m", "-20m")}
DISP_VTO = ("a", "b_min", "b_max")
DISP_ATT = ("max", "m20")


# ======== 5: accensione e spegnimento, senza segnale, +10 dB (ipotesi nell'intestazione)
T0_ON, T_TIMER = 0.1, 2.5
T_OFF = 1.0
RAMPE = (0.01, 0.3)
SFASI = {"s": (0.0, 0.0), "p": (0.05, 0.0), "m": (0.0, 0.05)}   # ritardo del rail + / -
RIT_RELE = (0.0, 0.005, 0.02, 0.1)


def matrice_caldo():
    """Il cambio di guadagno a caldo, senza segnale e senza mute, coi riferimenti mai in mute a
    ogni guadagno, nello stesso deck (con gli stessi gemelli, aperti)."""
    out = []
    for g in (0, 3, 10):
        n = "hmai_g%d" % g
        out += corsa(n, amp=0, tf=3.5, g1=g)
        out += [riga(n, n, "rif", 1000, 0, g, "100k", TI, 1000, 3.5, 10e-6, "rif_mai", gruppo=1)]
    for g1, g2 in [(0, 3), (3, 0), (3, 10), (10, 3), (0, 10), (10, 0)]:
        n = "hc%dx%d_lz" % (g1, g2)
        out += corsa(n, amp=0, tf=3.5, g1=g1, g2=g2, tg=TI)
        out += [riga(n, n, "caldo_morbido", 1000, 0, "%da%d" % (g1, g2), "100k", TI, 1000, 3.5, 10e-6,
                     "evento", "hmai_g%d" % g2, "-", 0.0, 1, "A_ins")]
    return out


# ======== L29d: la sonda del contatto in serie, celle peggiori di L29c, senza segnale, +10 dB
GEOMETRIE = ("N", "iA", "iB", "ii", "iii")
# lo stato a riposo e' lo stesso in tutte le geometrie con la serie (S); a mute inserito iA = iB
CLASSE_MAI = {"N": "N", "iA": "S", "iB": "S", "ii": "S", "iii": "S"}
CLASSE_SEMPRE = {"N": "N", "iA": "i", "iB": "i", "ii": "ii", "iii": "iii"}
GEO_DI = {"N": "N", "S": "ii", "i": "iA", "ii": "ii", "iii": "iii"}


def matrice_sonda(geometrie=GEOMETRIE, kx={}):
    """kx: argomenti in piu' di corsa() (L29d2: ck e cavo per il controfattuale N)."""
    out = []
    tf_rif = TF_CAMBIO   # copre ogni evento della sonda (mev 17,5 s, accensione 11,6 s)
    servono = {CLASSE_MAI[g] for g in geometrie} | {CLASSE_SEMPRE[g] for g in geometrie}
    for g in (0, 10):
        for k, cl, extra in [("mai", c, {}) for c in ("N", "S")] + [
                ("sempre", c, dict(ti=-10, tr=1000, tijk=-10, trjk=1000)) for c in ("N", "i", "ii", "iii")]:
            if cl not in servono:
                continue
            n = "g%d%s_lz_%s" % (g, k, cl)
            out += ["* ---- riferimento %s ----" % n]
            out += corsa(n, amp=0, tf=tf_rif, g1=g, geo=GEO_DI[cl], **dict(extra, **kx))
            out += [riga(n, n, "rif", 1000, 0, g, "100k", TI, TI + 1.0, tf_rif, 10e-6, "rif_" + k,
                         gruppo=0)]
    for geo in geometrie:
        var = "l29d_%s" % geo
        rif = lambda g, k: "g%d%s_lz_%s" % (g, k, (CLASSE_MAI if k == "mai" else CLASSE_SEMPRE)[geo])
        # 1: il cambio 0 -> +10 a rele' chiuso, e il rilascio 2 s dopo
        n = "gm0x10_lz_%s" % geo
        out += ["* ---- %s ----" % n]
        out += corsa(n, amp=0, tf=TF_CAMBIO, ti=TI, tr=TR_CAMBIO,
                     g1=0, g2=10, tg=T_CAMBIO, geo=geo, **kx)
        out += [riga(n + "_i", n, var, 1000, 0, "0a10", "100k", TI, T_CAMBIO, TF_CAMBIO, 10e-6, "evento",
                     rif(0, "sempre"), rif(0, "mai"), TG, 1, "A_ins;B2")]
        out += [riga(n + "_c", n, var, 1000, 0, "0a10", "100k", T_CAMBIO, TR_CAMBIO, TF_CAMBIO, 10e-6,
                     "evento", rif(10, "sempre"), rif(10, "mai"), 0.0, 1, "A_ins;A_rel;B2")]
        # 4: il mute semplice, rele' tenuto 1 s
        n = "mev_lz_%s" % geo
        tf = TI + 1.0 + 3.0
        out += ["* ---- %s ----" % n]
        out += corsa(n, amp=0, tf=tf, ti=TI, tr=TI + 1.0, geo=geo, **kx)
        out += [riga(n, n, var + "_ev", 1000, 0, 10, "100k", TI, TI + 1.0, tf, 10e-6, "evento",
                     rif(10, "sempre"), rif(10, "mai"), TG, 4, "A_ins;A_rel;B2")]
        # 5: le due accensioni peggiori di L29c
        for tr, sk in ((0.3, "p"), (0.01, "m")):
            dp, dm = SFASI[sk]
            n = "on_r%g%s_%s" % (tr * 1e3, sk, geo)
            t_rel = T0_ON + T_TIMER
            tf = t_rel + 3.0
            rail = ("0 0 %g 0 %g 15 1000 15" % (T0_ON + dp, T0_ON + dp + tr),
                    "0 0 %g 0 %g -15 1000 -15" % (T0_ON + dm, T0_ON + dm + tr),
                    "0 0 %g 0 %g 1 1000 1" % (T0_ON + dp, T0_ON + dp + tr))
            out += ["* ---- %s ----" % n]
            out += corsa(n, amp=0, tf=tf, ti=-100, tr=t_rel, tijk=-10, trjk=t_rel, rail=rail, geo=geo, **kx)
            out += [riga(n, n, "accensione_" + geo, 1000, 0, 10, "100k", T0_ON, t_rel, tf, 10e-6, "evento",
                         rif(10, "sempre"), rif(10, "mai"), 0.0, 5, "A_ins;A_rel")]
    return out


# ======== L29d2: la matrice di L29c sulla geometria iii (decisioni nell'intestazione)
VARIANTI = (("", {}), ("c100", dict(cavo="100p")), ("r10k", dict(rl="10k")), ("k5", dict(ck="5p")))
MUTE_RELE = [("h01", TI + 0.1), ("ev", TI + 1.0), ("h2", TI + 2.0), ("h20", TI + 20.0)]   # il tasto del rilascio


def clic(geo, sx, kw, var):
    """L47c2b1: le corse che completano la tabella del clic del taglio (scelta dell'utente:
    «Tabella intera», tre uscite x 20 Hz / 1 kHz / 20 kHz x inserimento / rilascio). Il gruppo 4
    copre 20 Hz e 1 kHz a 100 k (mev_*); qui i 20 kHz a 100 k e i tre toni a 10 k, i due carichi
    di V2. Ognuna col suo «mai» e «sempre» a +10 dB. A 20 kHz (passo 0,5 us) il tasto del
    rilascio e' 0,5 s dopo e la corsa finisce 0,5 s dopo ancora: C2 guarda [t - 20 ms,
    t + t_grad + 200 ms], e A con la musica e' diagnostica (ADR-036)."""
    out = []
    SEMPRE = dict(ti=-10, tr=1000, tijk=-10, trjk=1000)
    for rl, sxc in (("100k", sx), ("10k", "_r10k" + sx)):
        for fk in ("20", "1k", "20k"):
            if rl == "100k" and fk != "20k":
                continue
            f, tm, _ = FREQ[fk]
            tr = TI + (0.5 if fk == "20k" else 1.0)
            tf = tr + (0.5 if fk == "20k" else 3.0)
            k = dict(kw, rl=rl)
            out += ["* ---- L47c2b1 clic: %s Hz, %s ----" % (f, rl)]
            rifs = {}
            for kk, extra in (("mai", {}), ("sempre", SEMPRE)):
                c = "g10%s_%s%s" % (kk, fk, sxc)
                rifs[kk] = c
                out += corsa(c, f=f, tmax=tm, tf=tf, g1=10, **dict(k, **extra))
                out += [riga(c, c, "rif", f, A, 10, rl, TI, tr, tf, tm, "rif_" + kk, gruppo=0)]
            n = "mev_%s%s" % (fk, sxc)
            out += corsa(n, f=f, tmax=tm, tf=tf, ti=TI, tr=tr, **k)
            out += [riga(n, n, var + "_clic", f, A, 10, rl, TI, tr, tf, tm, "evento",
                         rifs["sempre"], rifs["mai"], TG, 4, "C2_ins;C2_rel;B2;B2g")]
    return out


def blocco_l29d2(vs, vkw, geo="iii"):
    """La matrice di L29c su una geometria e una variante. Le inversioni non ci sono (L47c2b1:
    non esistono piu', il mute taglia); i 20 kHz e i 10 k della tabella del clic sono in clic(),
    solo nella variante di progetto."""
    out = []
    sx = ("_" + vs if vs else "") + "_" + geo
    rl = vkw.get("rl", "100k")
    kw = dict(geo=geo, rl=rl, ck=vkw.get("ck", CK_DS), cavo=vkw.get("cavo", "1e-18"))
    var = "l29d2_%s%s" % (geo, "_" + vs if vs else "")
    SEMPRE = dict(ti=-10, tr=1000, tijk=-10, trjk=1000)

    def nome(pref, k, fk):
        return "%s%s_%s%s" % (pref, k, fk or "lz", sx)

    def rif(pref, fk, amp, tf, g=10, p=0):
        f, tm, _ = FREQ[fk] if fk else (1000, 10e-6, 7e-6)
        o = []
        for k, extra in (("mai", {}), ("sempre", SEMPRE)):
            c = nome(pref, k, fk)
            o += corsa(c, amp=amp, f=f, tmax=tm, tf=tf, g1=g, p1=p, **dict(kw, **extra))
            o += [riga(c, c, "rif", f, amp, g, rl, TI, TI + 1.0, tf, tm, "rif_" + k, gruppo=0)]
        return o

    SEGNALI = (("1k", A), ("20", A), (None, 0))
    for fk, amp in SEGNALI:
        out += ["* ---- L29d2%s: riferimenti %s ----" % (sx, fk or "senza segnale")]
        out += rif("g10", fk, amp, TF_LUNGO, g=10)
        out += rif("g0", fk, amp, TF_CAMBIO, g=0)
        out += rif("g3", fk, amp, TF_CAMBIO, g=3)
    for fk, amp in (("1k", A), (None, 0)):
        out += rif("t6", fk, amp, TF_CAMBIO, g=10, p=6)
        out += rif("t12", fk, amp, TF_CAMBIO, g=10, p=12)

    # ---- 1: guadagno sotto mute (rele' chiuso), come matrice_l29c
    for fk, amp in SEGNALI:
        f, tm, _ = FREQ[fk] if fk else (1000, 10e-6, 7e-6)
        sfx = fk or "lz"
        for g1, g2 in [(0, 3), (3, 0), (3, 10), (10, 3), (0, 10), (10, 0)]:
            n = "gm%dx%d_%s%s" % (g1, g2, sfx, sx)
            out += ["* ---- L29d2 1: %s ----" % n]
            out += corsa(n, amp=amp, f=f, tmax=tm, tf=TF_CAMBIO, ti=TI, tr=TR_CAMBIO,
                         g1=g1, g2=g2, tg=T_CAMBIO, **kw)
            gm = "%da%d" % (g1, g2)
            out += [riga(n + "_i", n, var, f, amp, gm, rl, TI, T_CAMBIO, TF_CAMBIO, tm, "evento",
                         nome("g%d" % g1, "sempre", fk), nome("g%d" % g1, "mai", fk), TG, 1,
                         "A_ins;B2" if amp == 0 else "C2_ins;B2;B2g")]
            out += [riga(n + "_c", n, var, f, amp, gm, rl, T_CAMBIO, TR_CAMBIO, TF_CAMBIO, tm, "evento",
                         nome("g%d" % g2, "sempre", fk), nome("g%d" % g2, "mai", fk), 0.0, 1,
                         "A_ins;A_rel;B2" if amp == 0 else "C2_rel;B2;B2g")]
    n = "gm0x10p_lz" + sx
    out += corsa(n, amp=0, tmax=7e-6, tf=TF_CAMBIO, ti=TI, tr=TR_CAMBIO,
                 g1=0, g2=10, tg=T_CAMBIO, stati=False, **kw)
    for k, t in enumerate((TI, T_CAMBIO, TR_CAMBIO)):
        out += [riga("pav_gm0x10_%d%s" % (k, sx), n, "pavimento", 1000, 0, "0a10", rl, t, 1000,
                     TF_CAMBIO, 7e-6, "pav_num", "gm0x10_lz%s_i" % sx, "-", 0.0, 0, "")]

    # ---- 2: trim sotto mute, +10 dB
    for fk, amp in (("1k", A), (None, 0)):
        f, tm, _ = FREQ[fk] if fk else (1000, 10e-6, 7e-6)
        sfx = fk or "lz"
        ref = lambda p, k: nome("g10" if p == 0 else "t%d" % p, k, fk)
        for p1, p2 in [(0, 6), (6, 0), (6, 12), (12, 6), (0, 12), (12, 0)]:
            n = "tm%dx%d_%s%s" % (p1, p2, sfx, sx)
            out += ["* ---- L29d2 2: %s ----" % n]
            out += corsa(n, amp=amp, f=f, tmax=tm, tf=TF_CAMBIO, ti=TI, tr=TR_CAMBIO,
                         g1=10, p1=p1, p2=p2, tp=T_CAMBIO, **kw)
            gm = "t%da%d" % (p1, p2)
            out += [riga(n + "_i", n, var, f, amp, gm, rl, TI, T_CAMBIO, TF_CAMBIO, tm, "evento",
                         ref(p1, "sempre"), ref(p1, "mai"), TG, 2,
                         "A_ins;B2" if amp == 0 else "C2_ins;B2;B2g")]
            out += [riga(n + "_c", n, var, f, amp, gm, rl, T_CAMBIO, TR_CAMBIO, TF_CAMBIO, tm, "evento",
                         ref(p2, "sempre"), ref(p2, "mai"), 0.0, 2,
                         "A_ins;A_rel;B2" if amp == 0 else "C2_rel;B2;B2g")]

    # ---- 3: la dispersione peggiore di L29c, VOS "p" e attenuatore al massimo, tre gruppi B
    for vt in DISP_VTO:
        dsx = "dp%smax" % vt.replace("b_", "")
        dkw = dict(kw, amp=0, vos=DISP_VOS["p"], att="max", vto=None if vt == "a" else vt)
        out += ["* ---- L29d2 3: dispersione %s%s ----" % (dsx, sx)]
        dref = lambda g, p, k: "r%s_g%dt%d_%s%s" % (k, g, p, dsx, sx)
        for g, p in ((10, 0), (0, 0), (10, 12)):
            for k, extra in (("mai", {}), ("sempre", SEMPRE)):
                n = dref(g, p, k)
                out += corsa(n, tf=TF_CAMBIO, g1=g, p1=p, **dict(dkw, **extra))
                out += [riga(n, n, "rif_" + dsx, 1000, 0, g, rl, TI, TI + 1, TF_CAMBIO, 10e-6,
                             "rif_" + k, gruppo=3)]
        for (g1, g2, p1, p2) in ((0, 10, 0, 0), (10, 0, 0, 0), (10, 10, 0, 12), (10, 10, 12, 0)):
            n = "x%d%d%d%d_%s%s" % (g1, g2, p1, p2, dsx, sx)
            out += corsa(n, tf=TF_CAMBIO, ti=TI, tr=TR_CAMBIO,
                         g1=g1, g2=g2, tg=T_CAMBIO if g1 != g2 else 1000,
                         p1=p1, p2=p2, tp=T_CAMBIO if p1 != p2 else 1000, **dkw)
            gm = "g%da%d_t%da%d" % (g1, g2, p1, p2)
            out += [riga(n + "_i", n, var + "_" + dsx, 1000, 0, gm, rl, TI, T_CAMBIO, TF_CAMBIO, 10e-6,
                         "evento", dref(g1, p1, "sempre"), dref(g1, p1, "mai"), TG, 3, "A_ins;B2")]
            out += [riga(n + "_c", n, var + "_" + dsx, 1000, 0, gm, rl, T_CAMBIO, TR_CAMBIO, TF_CAMBIO,
                         10e-6, "evento", dref(g2, p2, "sempre"), dref(g2, p2, "mai"), 0.0, 3,
                         "A_ins;A_rel;B2")]
        n = "xm_%s%s" % (dsx, sx)
        # il mute semplice, tenuto 2 s (L47c2b1: A all'inserimento vuole >= 2 s di finestra)
        out += corsa(n, tf=TI + 2 + 3, ti=TI, tr=TI + 2, **dkw)
        out += [riga(n, n, var + "_" + dsx, 1000, 0, 10, rl, TI, TI + 2, TI + 2 + 3, 10e-6,
                     "evento", dref(10, 0, "sempre"), dref(10, 0, "mai"), TG, 3, "A_ins;A_rel;B2")]

    # ---- 4: il mute col rele' (tasto del rilascio 0,1 / 1 / 2 / 20 s dopo): con la musica il
    # clic del taglio (C2, dichiarato: ADR-062) e B2 col contatto aperto (NC-053). La corsa
    # «senza rele'» di prima non c'e' piu': senza fotoresistenze non e' un mute (L47c2b1).
    for fk, amp in SEGNALI:
        f, tm, _ = FREQ[fk] if fk else (1000, 10e-6, 7e-6)
        sfx = fk or "lz"
        for m, tr in MUTE_RELE:
            n = "m%s_%s%s" % (m, sfx, sx)
            tf = tr + 3.0
            out += ["* ---- L29d2 4: %s ----" % n]
            out += corsa(n, amp=amp, f=f, tmax=tm, tf=tf, ti=TI, tr=tr, **kw)
            out += [riga(n, n, var + "_" + m, f, amp, 10, rl, TI, tr, tf, tm, "evento",
                         nome("g10", "sempre", fk), nome("g10", "mai", fk), TG, 4,
                         # L47c2b1: senza segnale, A all'inserimento conta dove la finestra
                         # arriva a 2 s (h2, h20); h01 ed ev, la stessa inserzione, contano il
                         # rilascio
                         (("A_ins;A_rel;B2" if tr - TI >= 2.0 else "A_rel;B2") if amp == 0
                          else "C2_ins;C2_rel;B2;B2g"))]
    if not vs:
        out += clic(geo, sx, kw, var)
    n = "mevp_lz" + sx
    out += corsa(n, amp=0, tmax=7e-6, tf=TI + 1 + 3, ti=TI, tr=TI + 1,
                 stati=False, **kw)
    for k, t in enumerate((TI, T_RELE, TI + 1)):
        out += [riga("pav_mev_%d%s" % (k, sx), n, "pavimento", 1000, 0, 10, rl, t, 1000,
                     TI + 1 + 3, 7e-6, "pav_num", "mev_lz" + sx, "-", 0.0, 0, "")]

    # ---- 5: accensione (verdetto) e spegnimento (diagnostica per L30, ADR-043)
    for tr in RAMPE:
        for sk, (dp, dm) in SFASI.items():
            n = "on_r%g%s%s" % (tr * 1e3, sk, sx)
            t_rel = T0_ON + T_TIMER
            tf = t_rel + 3.0
            rail = ("0 0 %g 0 %g 15 1000 15" % (T0_ON + dp, T0_ON + dp + tr),
                    "0 0 %g 0 %g -15 1000 -15" % (T0_ON + dm, T0_ON + dm + tr),
                    "0 0 %g 0 %g 1 1000 1" % (T0_ON + dp, T0_ON + dp + tr))
            out += ["* ---- L29d2 5: %s ----" % n]
            out += corsa(n, amp=0, tf=tf, ti=-100, tr=t_rel, tijk=-10, trjk=t_rel, rail=rail, **kw)
            out += [riga(n, n, "accensione_" + geo, 1000, 0, 10, rl, T0_ON, t_rel, tf, 10e-6, "evento",
                         nome("g10", "sempre", None), nome("g10", "mai", None), 0.0, 5, "A_ins;A_rel")]
            for rr in RIT_RELE:
                n = "off_r%g%s_d%g%s" % (tr * 1e3, sk, rr * 1e3, sx)
                tf = T_OFF + 2.5
                rail = ("0 15 %g 15 %g 1m 1000 1m" % (T_OFF + dp, T_OFF + dp + tr),
                        "0 -15 %g -15 %g -1m 1000 -1m" % (T_OFF + dm, T_OFF + dm + tr),
                        "0 1 %g 1 %g 0 1000 0" % (T_OFF + dp, T_OFF + dp + tr))
                out += corsa(n, amp=0, tf=tf, tijk=T_OFF + rr, trjk=1000, rail=rail, **kw)
                out += [riga(n, n, "spegnimento_" + geo, 1000, 0, 10, rl, T_OFF, 1000, tf, 10e-6, "evento",
                             nome("g10", "sempre", None), "-", 0.0, 5, "A_ins")]
    return out


# ======== L29e: il deck versionato dal sorgente (ADR-044)
NET = ARG.netlist
# il rele' di mute -> l'uscita del blocco CANALE: preamp_audio.py fa K2..K4 = MUTE1..MUTE3 su
# mute_lists[0..2] = fissa 1, fissa 2, principale
USCITA_DI = {"1": "1", "2": "2", "3": "m"}


def dal_sorgente():
    """L29e: legge circuits/preamp/preamp_audio.net e ne RICAVA la configurazione del mute al
    jack. Rifiuta se la netlist non e' la geometria iii (lo decide lo stesso controllo del 2e,
    importato: una sola definizione) o se il bleed del jack non e' quello del blocco CANALE.
    Restituisce i bleed lato condensatore, {m, 1, 2}, uguali sui due canali (T3)."""
    import sys
    from pathlib import Path
    sys.path.insert(0, os.path.join(REPO, "scripts"))
    import check_relay_safe_state as crs
    comps, pin_net = crs.parse_netlist(Path(NET))
    findings, relays, _ = crs.check(comps, pin_net)
    if findings:
        raise SystemExit("la netlist non passa il 2e, niente deck dal sorgente:\n  "
                         + "\n  ".join(findings))
    res = crs.resistors_between(comps, pin_net)
    canale = {r.split()[0].upper(): r.split()[3] for r in CANALE
              if r[:3] in ("RBL",) and len(r.split()) == 4}
    rbc = {}
    for ref, c in relays.items():
        if crs.role_of(c["value"]) != "MUTE":
            continue
        u = USCITA_DI[crs.index_of(c["value"])]
        pm = crs.KNOWN_RELAYS[(c["lib"], c["part"])]
        for pole in pm["poles"]:
            lato_c = pin_net[(ref, pole["COM"])]
            jack = pin_net[(ref, pole["NO"])]
            vc = sorted({comps[r]["value"] for r in res[frozenset((lato_c, "GND"))]})
            vj = sorted({comps[r]["value"] for r in res[frozenset((jack, "GND"))]})
            if len(vc) != 1 or len(vj) != 1:
                raise SystemExit("%s %s: attesi un bleed lato C e uno al jack, trovati %s e %s"
                                 % (ref, pole["name"], vc, vj))
            if rbc.setdefault(u, vc[0]) != vc[0]:
                raise SystemExit("uscita %s: bleed lato C diversi fra i canali (%s, %s): T3"
                                 % (u, rbc[u], vc[0]))
            atteso = canale["RBL" + u.upper()]
            if vj[0] != atteso:
                raise SystemExit("uscita %s: bleed del jack %s nella netlist, %s nel blocco CANALE "
                                 "(RBL%s): il banco non e' il sorgente" % (u, vj[0], atteso, u.upper()))
    if set(rbc) != {"m", "1", "2"}:
        raise SystemExit("uscite di mute trovate: %s, attese m, 1, 2" % sorted(rbc))
    return rbc


def matrice_sorgente():
    """L29e: la matrice di L29d2, variante di progetto (0 pF di cavo, 100 k), coi bleed lato
    condensatore letti dalla netlist. Nomi e righe sono quelli di L29d2 (suffisso _iii): il
    confronto col banco e' cella per cella."""
    return blocco_l29d2("", {})


def matrice_l29d2():
    out = []
    for vs, vkw in VARIANTI:
        out += blocco_l29d2(vs, vkw)
    # il controfattuale: N coi nomi della sonda L29d, con le aggiunte di L29d2 in posizione neutra
    out += matrice_sonda(("N",), dict(ck=CK_DS, cavo="1e-18"))
    return out


# ======== L30: lo spegnimento e il failsafe dell'alimentatore (ADR-043, ADR-045, ADR-046)
# Sul sorgente (geometria iii, bleed dalla netlist), senza segnale, +10 dB, 100 k, 0 pF di cavo.
# I tempi del relè al jack sono quelli del contatto: il comando cade a t_cmd, il contatto in
# serie si apre al rilascio MASSIMO del G6K, 3 ms dopo (en-g6k.pdf p. 3), la derivazione 1 ms
# dopo ancora (TT). L'alimentatore e' comportamentale: rampe lineari dei rail.
I_RAIL = 0.265        # A per rail: otto blocchi a riposo (ADR-042, tb_op: ~33 mA per rail)
V_TRIP = 13.5         # V: la soglia del sorvegliante sui rail (ADR-046)
# T_RIL (3 ms, il rilascio massimo dei relè del jack) sta con i tempi del mute, in testa
DELTA_MIN = 10e-3     # s: Δ garantito di ADR-045 (nominale 20 ms)
C_TENUTA = (470e-6, 1000e-6, 2200e-6)
TF_L30 = T_OFF + 2.5


def rail_lineare(t0, s, v=15.0):
    """PWL di un rail che scende da v a 1 mV con pendenza s (V/s) a partire da t0."""
    return "0 %g %.9f %g %.9f %g 1000 %g" % (v, t0, v, t0 + abs(v) / s, 1e-3 * v / 15, 1e-3 * v / 15)


def matrice_l30():
    out = []
    kw = dict(geo="iii", rl="100k", ck=CK_DS, cavo="1e-18")
    SEMPRE = dict(ti=-10, tr=1000, tijk=-10, trjk=1000)
    rif_mai, rif_sempre = "g10mai_lz_l30", "g10sempre_lz_l30"
    out += ["* ---- L30: riferimenti senza segnale, +10 dB ----"]
    out += corsa(rif_mai, amp=0, tf=TF_L30, g1=10, **kw)
    out += [riga(rif_mai, rif_mai, "rif", 1000, 0, 10, "100k", T_OFF, 1000, TF_L30, 10e-6, "rif_mai")]
    out += corsa(rif_sempre, amp=0, tf=TF_L30, g1=10, **dict(kw, **SEMPRE))
    out += [riga(rif_sempre, rif_sempre, "rif", 1000, 0, 10, "100k", T_OFF, 1000, TF_L30, 10e-6,
                 "rif_sempre")]

    # ---- N: lo spegnimento morbido (ADR-046). Il mute e' completo da secondi (jack isolati, lato
    # condensatore a massa); poi il relè di rete stacca: i rail scendono come in L29c,
    # e K1 / K5 cadono a 0 dB quando cade VRELAY: all'inizio della discesa (gi) o a meta' di quella
    # del rail piu' lento (gm), mentre il blocco perde la regolazione. Non alla fine: a rail spenti
    # non ha senso fisico, e il JFET si ferma su 'Timestep too small' (prima prova di L30).
    for tr in RAMPE:
        for sk, (dp, dm) in SFASI.items():
            for gk in ("gi", "gm"):
                n = "n_r%g%s_%s_l30" % (tr * 1e3, sk, gk)
                tg = T_OFF if gk == "gi" else T_OFF + max(dp, dm) + tr / 2
                rail = ("0 15 %g 15 %g 1m 1000 1m" % (T_OFF + dp, T_OFF + dp + tr),
                        "0 -15 %g -15 %g -1m 1000 -1m" % (T_OFF + dm, T_OFF + dm + tr),
                        "0 1 %g 1 %g 0 1000 0" % (T_OFF + dp, T_OFF + dp + tr))
                out += ["* ---- L30 N: %s ----" % n]
                out += corsa(n, amp=0, tf=TF_L30, g1=10, g2=0, tg=tg, rail=rail, **dict(kw, **SEMPRE))
                out += [riga(n, n, "spegnimento_morbido", 1000, 0, "10a0", "100k", T_OFF, 1000, TF_L30,
                             10e-6, "evento", rif_sempre, "-", 0.0, 6, "A_ins")]

    # ---- F / G: il guasto (ADR-043 §2, ADR-046). Un rail (p, m) o entrambi (s) scendono con la
    # pendenza I_RAIL / C della tenuta dopo il regolatore; il sorvegliante scatta quando il rail
    # passa V_TRIP (t = T_OFF). F: VRELAY sana, il guadagno resta +10. G: VRELAY persa, K1 / K5
    # tenuti dall'alimentazione con tenuta e caduti DELTA_MIN dopo il comando (ADR-045).
    for c in C_TENUTA:
        s = I_RAIL / c
        t0 = T_OFF - (15 - V_TRIP) / s
        for sk in ("s", "p", "m"):
            for gk in (("f", "g") if sk == "s" else ("f",)):
                n = "%s_c%d%s_l30" % (gk, round(c * 1e6), sk)
                vp = rail_lineare(t0, s) if sk in "sp" else "0 15 1000 15"
                vm = rail_lineare(t0, s, -15.0) if sk in "sm" else "0 -15 1000 -15"
                pw = ("0 1 %.9f 1 %.9f 0 1000 0" % (t0, t0 + 15 / s)) if sk in "sp" else "0 1 1000 1"
                g = dict(g2=0, tg=T_OFF + DELTA_MIN) if gk == "g" else {}
                out += ["* ---- L30 %s: %s ----" % (gk.upper(), n)]
                out += corsa(n, amp=0, tf=TF_L30, g1=10, tijk=T_OFF + T_RIL, trjk=1000,
                             rail=(vp, vm, pw), **dict(kw, **g))
                out += [riga(n, n, "guasto_" + gk, 1000, 0, "10a0" if g else 10, "100k", "%.9f" % t0,
                             1000, TF_L30, 10e-6, "evento", rif_mai, "-", 0.0, 6, "A_ins")]

    # ---- i controfattuali: devono andare MALE, e dicono perche' serve ciascun pezzo
    s = I_RAIL / 1000e-6
    t0 = T_OFF - (15 - V_TRIP) / s
    both = (rail_lineare(t0, s), rail_lineare(t0, s, -15.0), "0 1 %.9f 1 %.9f 0 1000 0" % (t0, t0 + 15 / s))
    cfs = [
        # senza Δ: K1 / K5 cadono col comando, prima che il contatto del jack si apra (ADR-045)
        ("cf_nodelta_l30", dict(g2=0, tg=T_OFF, tijk=T_OFF + T_RIL), both, t0),
        # senza sorvegliante: il relè cade solo quando il rail e' gia' a 10 V
        ("cf_tardi_l30", dict(tijk=T_OFF + (V_TRIP - 10) / s), both, t0),
        # il corto franco istantaneo del rail + (il caso accettato da ADR-046): 100 us, istantaneo
        # contro i 3 ms del relè (a 10 us il JFET si ferma su 'Timestep too small')
        ("cf_corto_p_l30", dict(tijk=T_OFF + T_RIL),
         ("0 15 %g 15 %g 1m 1000 1m" % (T_OFF, T_OFF + 100e-6), "0 -15 1000 -15", "0 1 1000 1"), T_OFF),
    ]
    for n, extra, rail, tev in cfs:
        out += ["* ---- L30 controfattuale: %s ----" % n]
        out += corsa(n, amp=0, tf=TF_L30, g1=10, trjk=1000, rail=rail, **dict(kw, **extra))
        out += [riga(n, n, "controfattuale", 1000, 0, "10a0" if "g2" in extra else 10, "100k",
                     "%.9f" % tev, 1000, TF_L30, 10e-6, "evento", rif_mai, "-", 0.0, 6, "A_ins")]
    return out


# ======== L41c: il banco di L30 col circuito vero dell'alimentatore (NC-036)
# Le forme d'onda disegnate a mano di L30 (rail, VPWL, istante del contatto, Δmin) sono sostituite
# da quelle del circuito di psu.py col firmware, al punto fisso (data/2026-09-26/L41c/seq/), portate
# qui da ponte/estrai_ponte.py: rail e istanti dei contatti (le correnti delle stringhe LED che
# il ponte portava fino a L47c2a non servono piu': niente fotoresistenze, ADR-062)
# all'angolo peggiore del G6K (jack il piu' tardi, guadagno il piu' presto; l'intestazione del
# ponte dice come). Il resto e' L30: sorgente, geometria iii, gemello di K1/K5, senza segnale,
# +10 dB, 100 k, 0 pF. Ogni caso ha il SUO riferimento: gli stessi punti fino a t_ins, poi fermi, e
# i contatti fermi - A_ins legge solo quello che succede dopo t_ins.
L41C_CASI = ("spegnimento_l", "perdita", "perdita_min", "guasto", "guasto_u501", "guasto_u503",
             "guasto_u503_min", "cf_nodelta", "corto_u503")


def pwl_json(p, fmt):
    return " ".join(("%.9f " + fmt) % (t, v) for t, v in p["punti"])


def matrice_l41c():
    import json
    if not ARG.ponte:
        raise SystemExit("--matrice l41c vuole --ponte <cartella dei JSON>")
    out = []
    kw = dict(geo="iii", rl="100k", ck=CK_DS, cavo="1e-18", amp=0, g1=10)
    for caso in L41C_CASI:
        j = json.load(open(os.path.join(ARG.ponte, caso + ".json")))
        n_ev, n_rif = "%s_l41c" % caso, "rif_%s_l41c" % caso
        tf, ti = j["t_fine"], j["t_ins"]
        for n, suf in ((n_rif, "_rif"), (n_ev, "")):
            rail = (pwl_json(j["vpp" + suf], "%.6f"), pwl_json(j["vmm" + suf], "%.6f"))
            ev = {}
            if not suf:
                if j["t_jack"] is not None:
                    ev["tijk"] = j["t_jack"]
                if j["t_gain"] is not None:
                    ev.update(g2=0, tg=j["t_gain"])
            out += ["* ---- L41c: %s (dal ponte: %s, giro %d) ----" % (n, caso, j["giro"])]
            out += corsa(n, tf=tf, trjk=1000, rail=rail, **dict(kw, **ev))
            if suf:
                out += [riga(n, n, "rif", 1000, 0, 10, "100k", "%.9f" % ti, 1000, tf, 10e-6, "rif_mai")]
            else:
                out += [riga(n, n, "l41c_" + caso, 1000, 0, "10a0" if "g2" in ev else 10, "100k",
                             "%.9f" % ti, 1000, tf, 10e-6, "evento", n_rif, "-", 0.0, 6, "A_ins")]
    return out


if ARG.matrice in ("sorgente", "l30", "l41c"):
    RBC = dal_sorgente()
    print("dal sorgente (%s): bleed lato C %s" % (NET, RBC))
if ARG.matrice in ("sonda_l29d", "l29d2", "sorgente", "l30", "l41c"):
    C = [("save v(mainjack) v(fixjack1) v(fixjack2) v(ina) v(vplus) v(vminus)"
          " v(main_a) v(mainc) v(fixc1) v(fixc2)") if r.startswith("save ") else r for r in C]
    C += {"sonda_l29d": matrice_sonda, "l29d2": matrice_l29d2, "sorgente": matrice_sorgente,
          "l30": matrice_l30, "l41c": matrice_l41c}[ARG.matrice]()
elif ARG.matrice == "controfattuale":
    C += controfattuale()
else:
    C += matrice_caldo()
C += [".endc", "", ".end"]
os.makedirs(os.path.dirname(os.path.abspath(ARG.uscita)), exist_ok=True)
open(ARG.uscita, "w").write("\n".join(H + C) + "\n")
n = sum(1 for r in C if r.startswith("tran "))
print("scritto %s: matrice %s, %d corse" % (ARG.uscita, ARG.matrice, n))
