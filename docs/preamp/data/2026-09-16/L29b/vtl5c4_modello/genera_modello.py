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
- lo spegnimento come funzione del solo stato log10(R): tassi letti sulla curva a 40 mA
  fino a ~80 kohm, poi un tasso di 0,40 decadi/s, il piu' lento compatibile con «400 Mohm
  minimi 10 s dopo»: e' la scelta PESSIMISTICA per il residuo del mute;
- l'accensione come primo ordine su log10(R) con tau = 3 ms (letto: 2,2 ms a 40 mA,
  3,6 ms a 10 mA);
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

# spegnimento: (log10 R, decadi/s) dai tratti della curva a 40 mA
OFF = [(1.8, 12.5), (3.3, 4.65), (3.5, 3.6), (3.68, 3.3), (3.84, 3.13), (3.99, 2.9),
       (4.13, 2.76), (4.33, 2.55), (4.57, 2.46), (4.79, 2.41), (4.95, 2.41), (5.25, 0.40), (9.0, 0.40)]


def tabella(pts):
    lx = [(math.log10(i), math.log10(r)) for i, r in pts]
    s0 = (lx[1][1] - lx[0][1]) / (lx[1][0] - lx[0][0])          # pendenza del primo tratto
    x_buio = lx[0][0] + (XDARK - lx[0][1]) / s0                  # dove raggiunge il buio
    s1 = (lx[-1][1] - lx[-2][1]) / (lx[-1][0] - lx[-2][0])
    fine = (2.5, lx[-1][1] + s1 * (2.5 - lx[-1][0]))
    return [(-9.0, XDARK), (x_buio, XDARK)] + lx + [fine]


def pwl(pts):
    return ", ".join("%.4f,%.4f" % p for p in pts)


testa = '''* vtl5c4_comportamentale.lib - Excelitas VTL5C4, modello COMPORTAMENTALE dal datasheet.
* GENERATO da docs/preamp/data/2026-09-16/L29b/vtl5c4_modello/genera_modello.py: non si edita a mano.
* L29b, ADR-038. Non e' un modello del costruttore: il costruttore non ne pubblica.
*
* DA DATI PUBBLICATI (datasheet pag. 45-46, letti a pixel):
*   R(I_LED) statica fra ~0,1-0,6 mA e 40 mA, quattro curve A..D (inviluppo delle condizioni
*   di adattamento e temperatura pubblicate); spegnimento da 40 mA fino a ~80 kohm;
*   accensione (tau ~2-4 ms); C cella 5,0 pF; C ingresso-uscita 0,5 pF; LED Vf 1,65 V a 20 mA.
* IPOTESI DICHIARATE (non pubblicate):
*   - sotto la corrente minima leggibile: pendenza del primo tratto fino a 400 Mohm;
*   - spegnimento oltre ~80 kohm a 0,40 decadi/s, il minimo compatibile con 400 Mohm a 10 s
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
        "BDX 0 xs I = min((V(xt) - V(xs))/3m, pow(10, pwl(V(xs), %s)))" % pwl([(x, math.log10(r)) for x, r in OFF]),
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
for k, pts in CURVE.items():
    print(k, "buio da log10(I_mA) = %.3f" % tabella(pts)[1][0])
