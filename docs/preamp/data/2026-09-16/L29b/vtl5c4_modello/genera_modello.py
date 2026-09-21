#!/usr/bin/env python3
"""genera_modello.py - scrive models/optocoupler/vtl5c4_comportamentale.lib dai punti
digitalizzati del datasheet VTL5C4 (L29b, ADR-038). Solo stdlib.

FONTE: vendor/optocoupler/excelitas/VTL5C3_VTL5C4/vtl5c3-vtl5c4-vactrol.pdf, pag. 46
(«Output Resistance vs. Input Current VTL5C4», «Response Time VTL5C4»), rasterizzata a
300 dpi con pdftoppm e letta a pixel (digit.py, tabelle.py in questa cartella). Calibrazione
dalla griglia: 176,5 px per decade di resistenza, 307,8 px per decade di corrente; tempi
159 px per decade e 123,8 px per 100 ms (spegnimento) o 1 ms (accensione).
Errore di lettura stimato: qualche pixel, cioe' ~±3 % in resistenza.

LE QUATTRO CURVE. Il datasheet le da' per quattro condizioni di adattamento alla luce e
di temperatura (25 C al buio 24 h; 25, +50, -20 C con 40 mA per 24 h) senza che la lettura
a pixel permetta di dire con certezza quale sia quale. Qui si chiamano A..D dalla piu'
bassa alla piu' alta resistenza a 1 mA, e si usano come INVILUPPO: A e D sono gli estremi.

CIO' CHE NON E' PUBBLICATO, E COSA SI IPOTIZZA (tutto dichiarato nel .lib):
- sotto la corrente piu' bassa leggibile di ogni curva: la pendenza log-log del primo
  tratto, fino alla resistenza al buio di 400 Mohm (minimo del datasheet a 10 s);
- lo spegnimento come funzione del solo stato log10(R): tasso costante fra i punti letti
  sulla curva a 40 mA fino a ~80 kohm, poi un tasso di 0,397 decadi/s, il piu' lento compatibile con «400 Mohm
  minimi 10 s dopo»: e' la scelta PESSIMISTICA per il residuo del mute;
- l'accensione: nel tratto pubblicato (da ~1,5 ms) e' un primo ordine su log10(R), tau
  2,6 ms a 40 mA e 3,6 ms a 10 mA (minimi quadrati sui punti letti, fit_accensione); tau
  interpolato fra le due correnti sul regime log10(R) e tenuto costante fuori. Estrapolato
  a t = 0 il tratto parte 1,2-1,5 decadi sopra il regime, non dal buio: il salto dal buio
  fin li' non e' pubblicato e si modella con tau_rapido = 2 us (IPOTESI; nel mute il LED
  e' comandato a rampa di secondi, e questo tratto non pesa);
- nessuna dipendenza della cella dalla tensione (distorsione) e nessun rumore;
- LED: diodo con N = 2 e IS tale che Vf = 1,65 V a 20 mA (tipico del datasheet);
- capacita' della cella 5,0 pF e d'accoppiamento ingresso-uscita 0,5 pF (datasheet pag. 45).
"""
import math, os

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", ".."))
OUT = os.path.join(REPO, "models", "optocoupler", "vtl5c4_comportamentale.lib")

# (I_mA, R_ohm) per curva, da tabelle.py; i punti «bordo» sono dove la curva esce dal
# grafico in alto (10 kohm), letti sulla colonna di pixel del bordo.
CURVE = {
    "A": [(0.1415, 7500), (0.211, 4632), (0.311, 2896), (0.520, 1579), (1.051, 722), (2.108, 357),
          (3.111, 248), (5.212, 161), (10.530, 100), (21.114, 73), (38.701, 60)],
    "B": [(0.206, 10000), (0.311, 5346), (0.520, 2575), (1.051, 1020), (2.108, 454),
          (3.111, 305), (5.212, 191), (10.530, 121), (21.114, 86), (38.701, 66)],
    "C": [(0.311, 9554), (0.520, 4145), (1.051, 1441), (2.108, 582),
          (3.111, 381), (5.212, 241), (10.530, 145), (21.114, 98), (38.701, 74)],
    "D": [(0.566, 10000), (1.051, 2260), (2.108, 786),
          (3.111, 507), (5.212, 311), (10.530, 178), (21.114, 114), (38.701, 82)],
}
XDARK = math.log10(400e6)

# spegnimento. Punti a pixel della curva a 40 mA (tabelle.py, off40): (x_px, y_px).
# Il tasso (decadi/s) e' COSTANTE fra due punti consecutivi e vale Delta log10R / Delta t:
# cosi' l'integrale ripercorre i punti per costruzione. (L29b, prima versione: tassi scelti a
# mano con log(tasso) interpolato fra nodi; ritardava di ~0,25 decadi, 567 contro 1555 ohm a
# 105 ms, e non riproduceva la fonte.) Il primo tratto parte dal regime a 40 mA della curva B
# (66 ohm, il datasheet non dice quale curva): il primo punto leggibile e' a 105 ms.
# Oltre l'ultimo punto (~80 kohm a 689 ms) il tasso costante che porta a 400 Mohm a 10,0 s:
# il piu' lento compatibile col minimo del datasheet, scelta PESSIMISTICA per il residuo.
TX0, TPX = 52.5, 123.8
OFF40_PX = [(182, 360), (240, 326), (305, 295.5), (365, 270.5), (430, 244), (490, 222),
            (553, 199.5), (677, 159), (790, 123), (905, 87.5)]
OFF_PUNTI = [(0.0, math.log10(66))] + [((x - TX0) / TPX * 0.1, 5 - (y - 72.5) / 159.0)
                                       for x, y in OFF40_PX]
OFF_PUNTI.append((10.0, math.log10(400e6)))
EPS = 1e-4                                   # larghezza del gradino fra due tassi, in decadi


def tabella_off():
    tassi = [(b[1] - a[1]) / (b[0] - a[0]) for a, b in zip(OFF_PUNTI, OFF_PUNTI[1:])]
    tab = [(1.0, tassi[0])]
    for i, r in enumerate(tassi):
        x_a, x_b = OFF_PUNTI[i][1], OFF_PUNTI[i + 1][1]
        tab += [(x_a + EPS, r), (x_b - EPS, r)]
    return tab + [(9.0, tassi[-1])]


def tabella(pts):
    lx = [(math.log10(i), math.log10(r)) for i, r in pts]
    s0 = (lx[1][1] - lx[0][1]) / (lx[1][0] - lx[0][0])          # pendenza del primo tratto
    x_buio = lx[0][0] + (XDARK - lx[0][1]) / s0                  # dove raggiunge il buio
    s1 = (lx[-1][1] - lx[-2][1]) / (lx[-1][0] - lx[-2][0])
    fine = (2.5, lx[-1][1] + s1 * (2.5 - lx[-1][0]))
    return [(-9.0, XDARK), (x_buio, XDARK)] + lx + [fine]


# accensione. Punti a pixel (tabelle.py, on40 e on10): (x_px, y_px), 123,8 px per 1 ms.
ON_PX = {40.0: [(240, 467), (305, 488.5), (365, 502.5), (430, 515.5), (490, 525.5), (553, 535.5),
                (610, 542.5)],
         10.0: [(305, 403), (365, 420), (430, 436), (490, 446.5), (610, 465.5), (677, 476.5),
                (740, 486.5), (790, 490.5), (905, 500)]}
TAU_RAPIDO = 2e-6                    # il fit mette D0 a t = 0: il salto deve finire in pochi us


def regime_B(i_ma):
    """log10(R) a regime sulla curva B, interpolata in log-log (la curva dello spegnimento).
    40 mA sta appena oltre l'ultimo punto letto (38,7 mA): si prolunga l'ultimo tratto."""
    lx = [(math.log10(i), math.log10(r)) for i, r in CURVE["B"]]
    x = math.log10(i_ma)
    for (xa, ya), (xb, yb) in zip(lx, lx[1:]):
        if xa <= x <= xb or (xb, yb) == lx[-1]:          # oltre l'ultimo: ultimo tratto, come tabella()
            return ya + (yb - ya) * (x - xa) / (xb - xa)


def fit_accensione():
    """Per ogni corrente: (regime log10R, tau s, D0 decadi) col fit ln(x - regime) = ln D0 - t/tau."""
    out = []
    for i_ma, pxs in sorted(ON_PX.items()):
        xf = regime_B(i_ma)
        pts = [((x - TX0) / TPX * 1e-3, math.log(5 - (y - 72.5) / 159.0 - xf)) for x, y in pxs]
        n = len(pts)
        mt = sum(t for t, _ in pts) / n
        my = sum(y for _, y in pts) / n
        b = sum((t - mt) * (y - my) for t, y in pts) / sum((t - mt) ** 2 for t, _ in pts)
        out.append((xf, -1 / b, math.exp(my - b * mt)))
    return sorted(out)


def pwl(pts):
    return ", ".join("%.4f,%.4f" % p for p in pts)


testa = '''* vtl5c4_comportamentale.lib - Excelitas VTL5C4, modello COMPORTAMENTALE dal datasheet.
* GENERATO da docs/preamp/data/2026-09-16/L29b/vtl5c4_modello/genera_modello.py: non si edita a mano.
* L29b, ADR-038. Non e' un modello del costruttore: il costruttore non ne pubblica.
*
* DA DATI PUBBLICATI (datasheet pag. 45-46, letti a pixel):
*   R(I_LED) statica fra ~0,1-0,6 mA e 40 mA, quattro curve A..D (inviluppo delle condizioni
*   di adattamento e temperatura pubblicate); spegnimento da 40 mA fino a ~80 kohm;
*   accensione (tau 2,6-3,6 ms nel tratto pubblicato); C cella 5,0 pF; C ingresso-uscita 0,5 pF; LED Vf 1,65 V a 20 mA.
* IPOTESI DICHIARATE (non pubblicate):
*   - sotto la corrente minima leggibile: pendenza del primo tratto fino a 400 Mohm;
*   - spegnimento oltre ~80 kohm a 0,397 decadi/s, il minimo compatibile con 400 Mohm a 10 s
*     (pessimistico per il residuo); tasso funzione del solo log10(R);
*   - nessuna distorsione della cella, nessun rumore, nessuna memoria della luce oltre la curva.
* Ogni cifra ricavata da qui porta l'etichetta «modello comportamentale dal datasheet, con
* estrapolazione dichiarata».
*
* USO:  X1 anodo catodo c1 c2 VTL5C4_B     (A = resistenza piu' bassa ... D = piu' alta)
*
* STATO: il nodo interno xs vale log10(R) in volt. Al punto di lavoro vale il regime per la
* corrente del LED a t = 0 (CXS aperto, BDX nullo per xs = xt). IC=8,6 conta solo con uic.
'''

TAU_PWL = "pwl(V(xt), %s)" % ", ".join("%.4f,%.6g" % (xf, tau) for xf, tau, _ in fit_accensione())
D0_PWL = "pwl(V(xt), %s)" % pwl([(xf, d0) for xf, _, d0 in fit_accensione()])
corpo = []
for k, pts in CURVE.items():
    tab = tabella(pts)
    corpo += [
        "",
        ".subckt VTL5C4_%s a k c1 c2" % k,
        "DLED a nl DLED_VTL5C4",
        "VSEN nl k DC 0",
        "* stato: log10(R) della cella, su 1 F",
        "BXT xt 0 V = pwl(log10(max(abs(i(VSEN))*1000, 1e-9)), %s)" % pwl(tab),
        "* accensione: tau e salto rapido oltre D0 funzione del regime; spegnimento: tasso letto.",
        "* La divisione per V(tau) e' protetta da max(.., 1e-4): nel Newton del punto di lavoro",
        "* il nodo parte da 0 V e la divisione dava NaN, con l'op che falliva a seconda del",
        "* percorso (L29b, 2026-09-21: cella in serie a 1 M). Alla soluzione tau >= 2,7 ms: nulla",
        "* cambia. (Scrivere tau e D0 dentro BDX come pwl annidati cambiava l'accensione.)",
        "BTAU tau 0 V = %s" % TAU_PWL,
        "BD0 d0 0 V = %s" % D0_PWL,
        "BDX 0 xs I = V(xt) >= V(xs) ? min((V(xt) - V(xs))/max(V(tau), 1e-4), pow(10, pwl(V(xs), %s)))"
        " : (V(xt) - V(xs))/max(V(tau), 1e-4) - max(V(xs) - V(xt) - V(d0), 0)/%g"
        % (pwl([(x, math.log10(r)) for x, r in tabella_off()]), TAU_RAPIDO),
        "CXS xs 0 1 IC=%.4f" % XDARK,
        "RXS xs 0 1e12",
        "BCELL c1 c2 I = V(c1,c2) / pow(10, V(xs))",
        "CCELL c1 c2 5p",
        "CIO a c1 0.5p",
        ".model DLED_VTL5C4 D(IS=2.8e-16 N=2)",
        ".ends",
    ]

os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "w").write(testa + "\n".join(corpo) + "\n")
print("scritto", OUT)
for xf, tau, d0 in fit_accensione():
    print("accensione: regime log10R %.4f  tau %.3f ms  D0 %.3f decadi" % (xf, tau * 1e3, d0))
for k, pts in CURVE.items():
    print(k, "buio da log10(I_mA) = %.3f" % tabella(pts)[1][0])
