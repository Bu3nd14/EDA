#!/usr/bin/env python3
"""genera_modello.py - scrive models/optocoupler/nsl32sr3_comportamentale.lib (L47a, NC-043).
Solo stdlib. Il .lib NON si edita a mano: si corregge qui e si rigenera.

LA PARTE. NSL-32SR3, oggi Advanced Photonix (prima Silonex, poi Luna): scelta dell'utente il
2026-10-02, l'unica sostituta della VTL5C4 acquistabile da un distributore (DigiKey, 7867 pz,
Active). Nessun costruttore pubblica un modello SPICE, e nessuno la curva sotto 0,1 mA.
L'utente non puo' misurare dei campioni: il modello si fa da dati PUBBLICATI piu' IPOTESI
DICHIARATE (sua indicazione: «cercare in rete o fare assunzioni»).

LE FONTI (in ordine di autorita'):
1. COSTRUTTORE, sopra 0,1 mA. Silonex 104058 Rev 07 (vendor/optocoupler/silonex/NSL-32SR3/),
   grafico «Photocell Resistance vs. LED Current», tipico, letto a pixel a 300 dpi (digit.py):
   cinque punti marcati, griglia 109 px per decade di R e 260 px per decade di I.
   Tabelle: 60 ohm MAX a 20 mA, 150 ohm tipici a 5 mA (il grafico ne da' ~115: incoerenza del
   costruttore, si segue il grafico), 25 Mohm MINIMI al buio 10 s dopo lo spegnimento (dopo
   1 minuto a 20 mA, nota 4 della Luna Rev 01-04-16), salita 5 ms (63 % della conduttanza
   finale a 5 mA), discesa 10 ms (fino a 100 kohm dopo lo spegnimento da 5 mA), LED 2,5 V MAX
   a 20 mA.
2. UNA CELLA MISURATA, da 2 mA a 2,5 uA. JC Maillet, «NSL32-SR3 STATIC Spice Model
   Derivation» (2008), tabella «Cell B» scritta a mano (fonti/maillet_2008_cellB/): l'unico
   dato pubblico che attraversa la regione da kohm a Mohm, dove sta la dissolvenza del mute.
   Un esemplare, temperatura e strumenti non dichiarati. Il punto a 4,7 uA ha le cifre
   sovrascritte («115?.8k»): ESCLUSO.
3. LA DISPERSIONE, a due correnti. Maillet, «Matching NSL-32SR3 opto couplers» (viva-analog.com,
   2014; fonti/maillet_2014_61pezzi/), 61 pezzi, grafico a dispersione: Ron a 2 mA fra 103 e
   289 ohm, R a 10 uA fra 16 e 89 kohm, le due non correlate. Esclusi dall'autore 5 pezzi su
   61 (guasti o fuori limite): la coda vera e' piu' larga.

COME SI COMPONE:
- la curva TIPICA (B): il grafico Silonex sopra 0,1 mA; sotto, la forma della Cell B (le sue
  pendenze log-log) scalata di K per raccordarsi al grafico a 0,131 mA, dove la Cell B sta
  1,45 volte sotto il tipico Silonex (a 2 mA 1,5 volte: e' una cella bassa ma dentro i 61);
- l'INVILUPPO: fattori in log10 rispetto alla tipica, ancorati ai due estremi dei 61 pezzi a
  2 mA e a 10 uA, lineari in log10(I) fra le due ancore e costanti fuori; i fattori ALTI
  scendono fra 2 e 20 mA fino a rispettare i 60 ohm MASSIMI del costruttore a 20 mA (IPOTESI:
  a corrente alta le celle convergono, come dice la tabella), costanti oltre;
- cinque curve: A bassa ovunque, B tipica, C alta ovunque, D bassa accesa e alta al buio (la
  piu' ripida), E alta accesa e bassa al buio (la piu' piatta). Le ultime due esistono perche'
  i 61 pezzi non mostrano correlazione fra i due estremi.

CIO' CHE NON E' PUBBLICATO, E COSA SI IPOTIZZA (tutto dichiarato nel .lib):
- sotto 2,5 uA: la pendenza dell'ultimo tratto della Cell B (circa -1,8 decadi per decade)
  fino a 25 Mohm, il MINIMO del costruttore, e poi costante: pessimistico sia per il residuo
  del mute (la cella in serie al buio) sia per il carico in gioco (la derivazione al buio).
  Maillet scrive «circa 5 Mohm a 1 uA», senza dato: la tipica ne da' ~3,6;
- l'accensione: primo ordine su log10(R) con tau costante, scelto perche' dal buio a 5 mA la
  conduttanza arrivi al 63 % in 5 ms sulla curva B;
- lo spegnimento come funzione del solo stato log10(R): dal regime a 5 mA fino a 100 kohm in
  10 ms a tasso costante (il dato), poi il tasso PIU' LENTO compatibile con 25 Mohm a 10 s,
  scelta PESSIMISTICA per il residuo, come nel modello della VTL5C4 (L29b). Lo schizzo di
  Maillet (una decade ogni ~6 ms fino a 400 kohm) non ha fonte verificata: non si usa;
- capacita' della cella 5 pF e d'accoppiamento ingresso-uscita 0,5 pF: NON PUBBLICATE,
  quelle della VTL5C4 (stessa famiglia costruttiva, CdS assiale);
- LED: il diodo della VTL5C4 (IS 2,8e-16, N = 2: 1,65 V a 20 mA) piu' una resistenza serie
  che porta la caduta a 2,5 V a 20 mA, il MASSIMO pubblicato (pessimistico per la tensione del
  pilota con due LED in serie). Non il solo diodo con IS ~2e-23: il punto di lavoro a 10 nA
  non converge, e il «transient op» finisce «successfully» con l'anodo a 0,2 V e la corrente
  del LED nella CIO (limitations #33; L47a, prima versione);
- nessuna dipendenza dalla temperatura (0,7 %/C tipici sopra 5 mA, solo dichiarato), nessuna
  memoria della luce, nessuna distorsione, nessun rumore.
"""
import math, os

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."] * 6))
OUT = os.path.join(REPO, "models", "optocoupler", "nsl32sr3_comportamentale.lib")

# 1. Silonex Rev 07: centri dei rombi in pixel (digit.py sul ritaglio, vedi README) e griglia
X01, PXD_I = 223.0, 260.0          # x della decade 0,1 mA; px per decade di corrente
Y10K, PXD_R = 439.0, 109.0         # y della decade 10 kohm; px per decade di resistenza
SILONEX_PX = [(224.0, 513.0), (480.0, 605.0), (741.0, 666.0), (819.0, 679.0), (894.5, 691.0)]
SILONEX = [(0.1 * 10 ** ((x - X01) / PXD_I), 10 ** (4 - (y - Y10K) / PXD_R)) for x, y in SILONEX_PX]

# 2. Maillet 2008, Cell B: (I_mA, R_ohm) trascritti dall'immagine; 4,7 uA escluso (cifre sovrascritte)
CELLB = [(2.05, 137), (0.29, 568), (0.131, 1150), (0.0781, 2220), (0.0382, 9250), (0.0181, 19300),
         (0.0081, 58100), (0.0033, 300e3), (0.0025, 490e3)]
I_RACCORDO = 0.131                 # mA: dove la forma della Cell B si attacca al grafico

# 3. Maillet 2014, 61 pezzi: estremi letti sul grafico a dispersione
POP_ACCESA = (2.0, 103.0, 289.0)   # I_mA, R minima, R massima
POP_BUIO = (0.010, 16e3, 89e3)
RON_MAX_20MA = 60.0                # tabella del costruttore
RDARK = 25e6                       # minimo del costruttore, 10 s dopo lo spegnimento
XDARK = math.log10(RDARK)

TR_S, TD_S, RD_TD = 5e-3, 10e-3, 100e3     # salita (63 % di G a 5 mA), discesa fino a 100 kohm
I_TEMPI = 5.0                               # mA, la corrente delle due definizioni
T_BUIO = 10.0                               # s: il minimo al buio vale a 10 s
VF_MAX, I_VF = 2.5, 20e-3
EPS = 1e-4


def ll(pts):
    return sorted((math.log10(i), math.log10(r)) for i, r in pts)


def interp(lx, x):
    """log10 R in x = log10 I, spezzata log-log; fuori dagli estremi prolunga il tratto d'estremo."""
    k = 0
    while k < len(lx) - 2 and x > lx[k + 1][0]:
        k += 1
    (xa, ya), (xb, yb) = lx[k], lx[k + 1]
    return ya + (yb - ya) * (x - xa) / (xb - xa)


SIL = ll(SILONEX)
CB = ll(CELLB)
K = interp(SIL, math.log10(I_RACCORDO)) - interp(CB, math.log10(I_RACCORDO))   # log10 del fattore
TIPICA = sorted([(x, y + K) for x, y in CB if x < math.log10(I_RACCORDO) - EPS] + SIL)

XB, XA, XC = math.log10(POP_BUIO[0]), math.log10(POP_ACCESA[0]), math.log10(20.0)
f_lo_b = math.log10(POP_BUIO[1]) - interp(TIPICA, XB)
f_hi_b = math.log10(POP_BUIO[2]) - interp(TIPICA, XB)
f_lo_a = math.log10(POP_ACCESA[1]) - interp(TIPICA, XA)
f_hi_a = math.log10(POP_ACCESA[2]) - interp(TIPICA, XA)
f_hi_c = min(f_hi_a, math.log10(RON_MAX_20MA) - interp(TIPICA, XC))


def rampa(x, x0, x1, y0, y1):
    if x <= x0:
        return y0
    if x >= x1:
        return y1
    return y0 + (y1 - y0) * (x - x0) / (x1 - x0)


def f_basso(lato_buio, lato_acceso):
    """fattore (log10) di un estremo: lato_buio/lato_acceso in {'lo', 'hi', 'tip'}."""
    fb = {"lo": f_lo_b, "hi": f_hi_b, "tip": 0.0}[lato_buio]
    fa = {"lo": f_lo_a, "hi": f_hi_a, "tip": 0.0}[lato_acceso]
    fc = {"lo": f_lo_a, "hi": f_hi_c, "tip": 0.0}[lato_acceso]
    return lambda x: rampa(x, XB, XA, fb, fa) if x <= XA else rampa(x, XA, XC, fa, fc)


ESTREMI = {"A": ("lo", "lo"), "B": ("tip", "tip"), "C": ("hi", "hi"), "D": ("hi", "lo"), "E": ("lo", "hi")}
NODI_X = sorted(set([x for x, _ in TIPICA] + [XB, XA, XC]))


def curva(nome):
    f = f_basso(*ESTREMI[nome])
    return [(x, interp(TIPICA, x) + f(x)) for x in NODI_X]


def tabella(nodi):
    (x0, y0), (x1, y1) = nodi[0], nodi[1]
    s0 = (y1 - y0) / (x1 - x0)                      # pendenza del tratto piu' basso
    x_buio = x0 + (XDARK - y0) / s0
    (xp, yp), (xu, yu) = nodi[-2], nodi[-1]
    fine = (2.5, yu + (yu - yp) / (xu - xp) * (2.5 - xu))
    return [(-9.0, XDARK), (x_buio, XDARK)] + nodi + [fine]


CURVE = {k: [(10 ** x, 10 ** y) for x, y in curva(k)] for k in ESTREMI}   # (I_mA, R) per le verifiche

# dinamica, sulla curva B
XF5 = interp(curva("B"), math.log10(I_TEMPI))
D63 = -math.log10(0.63)                                         # R = Rf / 0,63
TAU_ON = TR_S / math.log((XDARK - XF5) / D63)
R1 = (math.log10(RD_TD) - XF5) / TD_S                           # dec/s fino a 100 kohm
# Il passaggio da R1 a R2 e' una rampa di log10(tasso) larga W decadi di stato, tutta SOPRA
# 100 kohm (il punto a 10 ms resta esatto). Non un gradino: un salto di tre decadi del tasso
# in 2e-4 decadi di stato (prima versione) dava a Newton una derivata enorme a ogni passaggio
# per 100 kohm, e l'op a 10 nA e a 20 mA non convergeva (L47a). R2 si calcola col tempo speso
# nella rampa, perche' 25 Mohm restino a 10 s: t_rampa = (1/R2 - 1/R1) / (m ln10),
# m = log10(R1/R2)/W la pendenza; si risolve per punto fisso.
W = 0.02
R2 = (XDARK - math.log10(RD_TD)) / (T_BUIO - TD_S)
for _ in range(50):
    m = math.log10(R1 / R2) / W
    t_rampa = (1 / R2 - 1 / R1) / (m * math.log(10))
    R2 = (XDARK - math.log10(RD_TD) - W) / (T_BUIO - TD_S - t_rampa)
IS_LED = 2.8e-16                                               # il diodo della VTL5C4 (L29b)
RS_LED = (VF_MAX - 2 * 0.025852 * math.log(I_VF / IS_LED + 1)) / I_VF


def pwl(pts):
    return ", ".join("%.4f,%.4f" % p for p in pts)


TASSI = [(0.0, math.log10(R1)), (math.log10(RD_TD), math.log10(R1)),
         (math.log10(RD_TD) + W, math.log10(R2)), (9.0, math.log10(R2))]      # log10 dec/s

testa = '''* nsl32sr3_comportamentale.lib - NSL-32SR3 (Advanced Photonix, gia' Silonex e Luna),
* modello COMPORTAMENTALE da dati pubblicati. GENERATO da
* docs/preamp/data/2026-10-02/L47a/nsl32sr3_modello/genera_modello.py: non si edita a mano.
* L47a, NC-043, ADR-058. Il costruttore non pubblica un modello SPICE.
*
* DA DATI PUBBLICATI:
*   - sopra 0,1 mA: il grafico tipico Silonex 104058 Rev 07, letto a pixel (5 punti);
*   - da 0,1 mA a 2,5 uA: la FORMA di UNA cella misurata da JC Maillet (2008), raccordata;
*   - la dispersione: 61 pezzi di Maillet (2014), solo a 2 mA (103-289 ohm) e a 10 uA
*     (16-89 kohm); il massimo del costruttore di 60 ohm a 20 mA;
*   - 25 Mohm minimi al buio a 10 s; salita 5 ms (63 %% di G a 5 mA); discesa 10 ms a 100 kohm.
* IPOTESI DICHIARATE (non pubblicate):
*   - sotto 2,5 uA la pendenza dell'ultimo tratto fino a 25 Mohm, poi costante (il minimo);
*   - accensione a primo ordine su log10(R), tau %.3f ms costante;
*   - spegnimento oltre 100 kohm a %.3f decadi/s, il piu' lento compatibile con 25 Mohm a 10 s
*     (pessimistico per il residuo); tasso funzione del solo log10(R);
*   - fattori di dispersione lineari in log10(I) fra 10 uA e 2 mA, e fra 2 e 20 mA quelli alti;
*   - C cella 5 pF e C ingresso-uscita 0,5 pF della VTL5C4; LED: diodo VTL5C4 piu' RS, 2,5 V a 20 mA (il massimo);
*   - nessuna temperatura, memoria della luce, distorsione, rumore.
* Ogni cifra ricavata da qui porta l'etichetta «modello comportamentale da dati pubblicati,
* una sola cella misurata nella regione del mute, con estrapolazione dichiarata».
*
* USO:  X1 anodo catodo c1 c2 NSL32SR3_B
*       A bassa ovunque, B tipica, C alta ovunque, D bassa accesa e alta al buio (la piu'
*       ripida), E alta accesa e bassa al buio (la piu' piatta).
*
* STATO: il nodo interno xs vale log10(R) in volt. Al punto di lavoro vale il regime per la
* corrente del LED a t = 0 (CXS aperto, BDX nullo per xs = xt). IC=%.4f conta solo con uic.
* CONVERGENZA: provato con le opzioni dei banchi (reltol=1e-6 vntol=1e-6 abstol=1e-12). Con
* abstol=1e-15 l'op dipende dal percorso di Newton e puo' finire nel «transient op» in uno
* stato sbagliato SENZA errore (limitations #33): guardare il log.
''' % (TAU_ON * 1e3, R2, XDARK)

corpo = []
for k in ESTREMI:
    corpo += [
        "",
        ".subckt NSL32SR3_%s a k c1 c2" % k,
        "DLED a nl DLED_NSL32SR3",
        "VSEN nl k DC 0",
        "* stato: log10(R) della cella, su 1 F",
        "BXT xt 0 V = pwl(log10(max(abs(i(VSEN))*1000, 1e-9)), %s)" % pwl(tabella(curva(k))),
        "* accensione: primo ordine, tau costante; spegnimento: tasso funzione di log10(R).",
        "BDX 0 xs I = V(xt) >= V(xs) ? min((V(xt) - V(xs))/%.6g, pow(10, pwl(V(xs), %s)))"
        " : (V(xt) - V(xs))/%.6g" % (TAU_ON, pwl(TASSI), TAU_ON),
        "CXS xs 0 1 IC=%.4f" % XDARK,
        "RXS xs 0 1e12",
        "BCELL c1 c2 I = V(c1,c2) / pow(10, V(xs))",
        "CCELL c1 c2 5p",
        "CIO a c1 0.5p",
        ".model DLED_NSL32SR3 D(IS=%.4g N=2 RS=%.4g)" % (IS_LED, RS_LED),
        ".ends",
    ]

if __name__ == "__main__":
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w").write(testa + "\n".join(corpo) + "\n")
    print("scritto", OUT)
    print("Silonex letti (I_mA, R):", ", ".join("%.4g %.4g" % p for p in SILONEX))
    print("raccordo Cell B: fattore %.3f a %.3f mA" % (10 ** K, I_RACCORDO))
    print("fattori: buio lo %.3f hi %.3f; acceso lo %.3f hi %.3f; hi a 20 mA %.3f"
          % tuple(10 ** f for f in (f_lo_b, f_hi_b, f_lo_a, f_hi_a, f_hi_c)))
    print("dinamica: R(5 mA) %.1f ohm, tau_on %.3f ms, discesa %.1f dec/s poi %.4f dec/s"
          % (10 ** XF5, TAU_ON * 1e3, R1, R2))
    print("LED IS %.4g RS %.4g ohm" % (IS_LED, RS_LED))
    for k, pts in CURVE.items():
        print(k, " ".join("%.4g:%.4g" % p for p in pts), " buio da %.3g mA" % 10 ** tabella(curva(k))[1][0])
