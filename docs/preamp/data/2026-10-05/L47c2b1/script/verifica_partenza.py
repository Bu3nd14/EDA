#!/usr/bin/env python3
"""L47c2b1: copiato da data/2026-09-23/L29c/script/verifica_partenza.py, con le COLONNE NUOVE degli
stati. Da L47c2b1 la wrdata degli stati non ha piu' le tre colonne delle celle (v(xls.xs),
v(xlp.xs), v(dep)): e' v(ina) v(vplus) v(vminus) v(main_a) [...]. Lo script di L29c leggerebbe
le colonne 9, 11, 13 per posizione, cioe' altre grandezze, senza errore: per questo qui ci sono
gli indici nuovi, e un controllo che la riga abbia la forma attesa.

Verifica A POSTERIORI da dove e' partita ogni corsa (limitations #33). Per ogni X.dat con il suo
X_stati.dat: a t = 0 MAIN_A entro 0,5 V e i tre jack entro 1 mV. Le corse coi rail in rampa
(on_*) partono da 0 V per costruzione: per loro basta che i rail a t = 0 valgano 0.

Uso: verifica_partenza.py DIR [DIR ...]   -> una riga di sintesi per directory"""
import glob
import os
import sys

tot_male = 0
for d in sys.argv[1:]:
    n = 0
    male = []
    for s in sorted(glob.glob(os.path.join(d, "*_stati.dat"))):
        c = os.path.basename(s)[:-len("_stati.dat")]
        j = os.path.join(d, c + ".dat")
        if not os.path.exists(j):
            continue
        with open(s) as f:
            xs = f.readline().split()
        with open(j) as f:
            xj = f.readline().split()
        if len(xs) not in (8, 14):
            raise SystemExit("%s: %d colonne negli stati, attese 8 (o 14 con i lati del condensatore):"
                             " la wrdata non e' quella di L47c2b1" % (s, len(xs)))
        vplus, vminus, main_a = float(xs[3]), float(xs[5]), float(xs[7])
        jack = [float(xj[1]), float(xj[3]), float(xj[5])]
        n += 1
        if c.startswith("on_"):
            ok = abs(vplus) < 1e-6 and abs(vminus) < 1e-6
        else:
            ok = abs(main_a) < 0.5 and max(abs(v) for v in jack) < 1e-3 and abs(vplus - 15) < 1e-6
        if not ok:
            male.append("%s main_a %.4g jack %s rail %.3g/%.3g" % (c, main_a, jack, vplus, vminus))
    tot_male += len(male)
    print("%s: %d corse, %d non partono dal punto giusto" % (d, n, len(male)))
    for m in male:
        print("   " + m)
sys.exit(1 if tot_male else 0)
