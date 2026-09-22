#!/usr/bin/env python3
"""L29b2: il banco di L29b (ldr_catena/build.py) con il tempo scritto a 16 cifre.

Uso:  /usr/bin/python3 build_nd.py OUTDIR [TD=6] [PROFILO=v3]  ->  OUTDIR/ldr1k.cir

Unica differenza dal banco di L29b: "set numdgt=15" in testa al blocco .control, prima di
ogni wrdata. Il blocco CANALE, le LDR, il comando, le corse e il manifesto sono quelli di
build.py, byte per byte. Piu' due corse di pavimento lungo TUTTA la sequenza: l'evento
("ev") e il suo gemello senza rele' ("norele") rifatti a TMAX 7 us, letti come C2 contro
se stessi a 10 us (tipo pav_num, come la corsa mai7u di L29b).

PERCHE' (L29b2, docs/preamp/data/2026-09-22/L29b2/pavimento/): col default wrdata scrive il
tempo con 9 cifre significative, 10 ns fino a 10 s e 100 ns oltre. Fra due corse con griglie
di passo diverse l'arrotondamento vale fino a 2 A w dt: 7 mV sulla principale a 1 kHz dopo
10 s, e ~0,7 mV prima. Era il pavimento «con le LDR attive» di L29b.
"""
import os
import subprocess
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(QUI, "..", "..", "..", "2026-09-21", "L29b", "ldr_catena", "build.py")
OUT = os.path.abspath(sys.argv[1])
TD = sys.argv[2] if len(sys.argv) > 2 else "6"
PROFILO = sys.argv[3] if len(sys.argv) > 3 else "v3"
V4 = PROFILO == "v4"
subprocess.run(["/usr/bin/python3", BUILD, OUT, TD, "v3" if V4 else PROFILO], check=True)
cir = os.path.join(OUT, "ldr1k.cir")
L = open(cir).read().splitlines()
if V4:
    # v4: PROPOSTA MIA di L29b2, scratch, NON adottata (il profilo e' dell'utente, ADR-038).
    # Come v3 fino a 4,5 uA a d = 0,45; poi 4,5 uA -> 0,19 uA (ginocchio del buio della
    # curva B) log-lineare fino a d = 0,75, e 10 nA a d = 0,8. Perche': al rilascio v3 porta
    # la serie da 10 nA a 4,5 uA in 0,3 s, e la cella SI ACCENDE alla velocita' del LED
    # (R_s da 10^8,6 a 10^6,8 in 150 ms, livello da -62 a -26 dB: C2 3,41 mV). La
    # sovrapposizione con la derivazione (d 0,5-0,75) avviene con R_s >= 2 M: la sorgente
    # non vede un carico basso (ADR-038 punto 3).
    import math
    lg = [math.log10(i) for i in (20e-3, 0.2e-3, 4.5e-6, 0.19e-6, 10e-9, 10e-9)]
    k = next(n for n, r in enumerate(L) if r.startswith("BILS "))
    L[k] = ("BILS 0 ALS I = pow(10, pwl(V(DEP), 0,%.4f, 0.1,%.4f, 0.45,%.4f, 0.75,%.4f, "
            "0.8,%.4f, 1,%.4f))" % tuple(lg))
    L = [r.replace("ldr_v3_td", "ldr_v4_td") for r in L]
i = L.index(".control")
L.insert(i + 1, "set numdgt=15")

# le due corse di pavimento lungo la sequenza, prima di .endc
td = float(TD)
TI, T_RELE = 1.0, 1.0 + td + 0.5
TR = T_RELE + 1.0
TF = TR + td + 3.0
MAN = os.path.join(OUT, "manifest.csv")
extra = []
for nome, rele in (("ev7u", (T_RELE, TR)), ("norele7u", (1000, 2000))):
    extra += [
        "alter vamp dc = 3.818",
        "alter vti dc = %s" % TI, "alter vtr dc = %s" % TR,
        "alter vtijk dc = %s" % rele[0], "alter vtrjk dc = %s" % rele[1],
        "tran 7e-06 %s 0 7e-06" % TF,
        "wrdata %s/%s$d v(mainjack) v(fixjack1) v(fixjack2)" % (OUT, nome),
        "destroy all",
    ]
    base = nome[:-2]
    for k, t in enumerate((TI, T_RELE, TR)):
        extra.append('echo "pav_%s%d,%s.dat,pavimento,1000,3.818,10,100k,%s,1000,%s,7e-06,'
                     'pav_num,%s,-,0.0" >> %s' % (base, k, nome, t, TF, base, MAN))
j = L.index(".endc")
L[j:j] = extra
open(cir, "w").write("\n".join(L) + "\n")
print("scritto", cir, "(numdgt=15, + ev7u/norele7u)")
