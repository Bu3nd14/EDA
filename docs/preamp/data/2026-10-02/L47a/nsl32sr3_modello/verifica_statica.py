#!/usr/bin/env python3
"""verifica_statica.py - il modello NSL-32SR3 restituisce i punti da cui e' generato? (L47a)

Un processo ngspice per punto, come in L29b (verifica_statica.py della VTL5C4): in sequenza
alter + op il punto di lavoro parte dal precedente e, col log10 della corrente del LED, puo'
stampare cifre sbagliate senza errore.

Controlla, ognuno entro TOL:
- ogni nodo di ogni curva A..E (CURVE di genera_modello.py);
- il buio dichiarato, 25 Mohm, a 10 nA (il riposo del comando, ADR-039) e a 1 nA;
- il massimo del costruttore, 60 ohm a 20 mA, sulle curve alte C ed E (B, la tipica del grafico,
  ne da' 62,4: e' il grafico del costruttore, si stampa e non si giudica);
- l'inviluppo copre i 61 pezzi di Maillet: minimo e massimo fra le curve a 2 mA (103 / 289 ohm)
  e a 10 uA (16 / 89 kohm).
Uso: verifica_statica.py [lib]   (default il .lib di models/). Esce col numero di controlli falliti.
"""
import os, re, subprocess, sys, tempfile

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
import genera_modello as G

LIB = sys.argv[1] if len(sys.argv) > 1 else G.OUT
NGSPICE = "/opt/homebrew/bin/ngspice"
TOL = 0.005


def R(curva, i_led):
    # Le opzioni dei banchi veri (tb_v2_casopeggiore.cir); 1 V sulla cella, che e' lineare:
    # 40 nA a 25 Mohm, sopra abstol. Con abstol=1e-15 e 1 mV (le opzioni di L29b) l'op di
    # questo modello dipendeva dal percorso di Newton: al buio falliva a 25 Mohm e non a 25,1,
    # e il «transient op» finiva «successfully» con l'anodo a 0,2 V (L47a).
    cir = ("nsl32sr3 op\n.include %s\n.options reltol=1e-6 vntol=1e-6 abstol=1e-12\n"
           "IA 0 AA DC %g\nXA AA 0 CA 0 NSL32SR3_%s\nVCA CA 0 DC 1\n"
           ".control\nop\necho \"RIS $&i(vca)\"\n.endc\n.end\n") % (LIB, i_led, curva)
    with tempfile.NamedTemporaryFile("w", suffix=".cir", delete=False) as f:
        f.write(cir)
    try:
        p = subprocess.run([NGSPICE, "-b", f.name], capture_output=True, text=True, timeout=60)
        out = p.stdout + p.stderr          # le Note di ngspice (gmin, «Transient op») vanno su stderr
    except subprocess.TimeoutExpired:
        out = "failed"
    os.unlink(f.name)
    m = re.search(r"RIS (\S+)", out)
    # un op che ripiega sul «transient op» puo' finire «successfully» in uno stato sbagliato
    # (limitations #33): nella prima versione del modello il buio usciva negativo, senza errore.
    # Il gmin stepping che finisce «completed» e' un op valido: non basta cercare «failed»,
    # che compare anche nell'avviso del dynamic gmin stepping che lo precede.
    if "Transient op" in out or not m:
        return None
    return -1.0 / float(m.group(1))


fuori = 0


def giudica(etichetta, r, rif, ok):
    global fuori
    fuori += not ok
    print("%-34s %12s  %12s  %s" % (etichetta, "NON CONV." if r is None else "%.5g" % r,
                                    "%.5g" % rif, "" if ok else "<-- FUORI"))


print("%-34s %12s  %12s" % ("punto", "R modello", "riferimento"))
for k, pts in G.CURVE.items():
    for i_ma, r_rif in pts:
        r = R(k, i_ma * 1e-3)
        giudica("%s  %.4g mA" % (k, i_ma), r, r_rif, r is not None and abs(r / r_rif - 1) <= TOL)

print("\nbuio dichiarato (%g ohm):" % G.RDARK)
for k in G.CURVE:
    for i_led in (1e-8, 1e-9):
        r = R(k, i_led)
        giudica("%s  %g A" % (k, i_led), r, G.RDARK, r is not None and abs(r / G.RDARK - 1) <= TOL)

print("\nmassimo del costruttore a 20 mA (%g ohm), curve alte:" % G.RON_MAX_20MA)
for k in ("C", "E"):
    r = R(k, 20e-3)
    giudica("%s  20 mA <= max" % k, r, G.RON_MAX_20MA, r is not None and r <= G.RON_MAX_20MA * (1 + TOL))
r = R("B", 20e-3)
print("%-34s %12.5g  (grafico tipico Silonex: non giudicato)" % ("B  20 mA", r if r else float("nan")))

print("\nl'inviluppo copre i 61 pezzi di Maillet:")
for i_ma, lo, hi in (G.POP_ACCESA, G.POP_BUIO):
    rs = [R(k, i_ma * 1e-3) for k in G.CURVE]
    ok = None not in rs
    giudica("min fra le curve a %g mA" % i_ma, min(rs) if ok else None, lo, ok and abs(min(rs) / lo - 1) <= TOL)
    giudica("max fra le curve a %g mA" % i_ma, max(rs) if ok else None, hi, ok and abs(max(rs) / hi - 1) <= TOL)

print("\ncontrolli falliti:", fuori)
sys.exit(fuori)
