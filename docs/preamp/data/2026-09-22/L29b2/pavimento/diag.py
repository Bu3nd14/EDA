#!/usr/bin/env python3
"""L29b2, diagnostica del pavimento di C2 con le LDR attive. Scratch, non un verdetto.

Uso:  /usr/bin/python3 diag.py OUTDIR CORSA [TMAX=10e-6] [METODO=trap] [TD=6] [PROFILO=v3] [LIB|-] [NUMDGT=0]
      CORSA in {ev, norele, mai}  ->  OUTDIR/<corsa>_<tag>.cir, poi  ngspice -b  su quel file

La netlist e' quella di ../../../2026-09-21/L29b/ldr_catena/build.py, fino a ".control"
esclusa (blocco CANALE intatto, LDR e comando identici). Il controllo e' questo: UNA sola
corsa per processo, cosi' le corse girano in parallelo, e con piu' nodi salvati per
localizzare il pavimento: la sorgente, l'ingresso e l'uscita del blocco A, gli stati
log10(R) delle due celle, le uscite.

METODO = gear si usa SOLO come diagnosi (decisione dell'utente del 2026-09-22): il metodo
di V2 e il deck versionato restano sul trapezio. Lo si mette con un .options DOPO il
blocco CANALE, che resta byte per byte quello dei deck di V2.
LIB, se dato (e non "-"), sostituisce il modello della LDR (varianti del generatore, scratch).
NUMDGT > 0 mette "set numdgt=NUMDGT" prima del wrdata. LA CAUSA DEL PAVIMENTO (L29b2): col
default wrdata scrive il tempo con 9 cifre significative, cioe' a 100 ns sopra t = 10 s (10 ns
sotto); fra due corse con griglie diverse l'arrotondamento vale fino a 2 A w dt di C2.
"""
import os
import subprocess
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(QUI, "..", "..", "..", "2026-09-21", "L29b", "ldr_catena", "build.py")
OUT = os.path.abspath(sys.argv[1])
CORSA = sys.argv[2]
TMAX = float(sys.argv[3]) if len(sys.argv) > 3 else 10e-6
METODO = sys.argv[4] if len(sys.argv) > 4 else "trap"
TD = float(sys.argv[5]) if len(sys.argv) > 5 else 6.0
PROFILO = sys.argv[6] if len(sys.argv) > 6 else "v3"
LIB = os.path.abspath(sys.argv[7]) if len(sys.argv) > 7 and sys.argv[7] != "-" else None
NUMDGT = int(sys.argv[8]) if len(sys.argv) > 8 else 0

os.makedirs(OUT, exist_ok=True)
base = os.path.join(OUT, "_base_%s_td%g" % (PROFILO, TD))
subprocess.run(["/usr/bin/python3", BUILD, base, str(TD), PROFILO], check=True,
               stdout=subprocess.DEVNULL)
righe = open(os.path.join(base, "ldr1k.cir")).read().splitlines()
fine = righe.index(".control")
L = righe[:fine]
if LIB:
    L = [(".include " + LIB) if r.startswith(".include") and "vtl5c4" in r else r for r in L]
if METODO != "trap":
    L.append(".options method=%s" % METODO)

TI = 1.0
T_RELE = TI + TD + 0.5
TR = T_RELE + 1.0
TF = TR + TD + 3.0
CORSE = {   # vti, vtr, vtijk, vtrjk  (come build.py)
    "ev": (TI, TR, T_RELE, TR),
    "norele": (TI, TR, 1000, 2000),
    "mai": (1000, 2000, 1000, 2000),
}
vti, vtr, vtijk, vtrjk = CORSE[CORSA]
tag = "%s_t%gu_%s%s%s" % (CORSA, TMAX * 1e6, METODO, "_lib" if LIB else "",
                          "_nd%d" % NUMDGT if NUMDGT else "")
NODI = "v(mainjack) v(fixjack1) v(ina) v(outa) v(src) v(xls.xs) v(xlp.xs) v(dep)"
L += [
    ".control",
    "save " + NODI,
    "alter rsrc = 1e12", "alter rrgb = 0.1", "alter rrg10b = 0.1",
    "alter vphs dc = 1.5707963267948966", "alter vmhjk dc = 1",
    "alter vamp dc = 3.818",
    "alter vti dc = %s" % vti, "alter vtr dc = %s" % vtr,
    "alter vtijk dc = %s" % vtijk, "alter vtrjk dc = %s" % vtrjk,
    "tran %g %g 0 %g" % (TMAX, TF, TMAX),
] + (["set numdgt=%d" % NUMDGT] if NUMDGT else []) + [
    "wrdata %s/%s.dat %s" % (OUT, tag, NODI),
    ".endc", ".end",
]
cir = os.path.join(OUT, tag + ".cir")
open(cir, "w").write("\n".join(L) + "\n")
print(cir)
