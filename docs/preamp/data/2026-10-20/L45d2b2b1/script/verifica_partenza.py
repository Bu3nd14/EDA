#!/usr/bin/env python3
"""L47c2b2: copiato da data/2026-10-05/L47c2b1/script/verifica_partenza.py (le colonne degli stati
senza celle), che resta com'era, con UNA differenza: il rail di partenza.

Lo script di L47c2b1 chiede V+ = 15 V entro 1 uV a t = 0: e' il rail disegnato a mano della
matrice V2. Nel banco dei guasti (--matrice l41c) i rail sono quelli del circuito vero portati dal
ponte (estrai_ponte.py), e a t = 0 valgono il primo punto della PWL del ponte (il TPS7A4701 a
regime: +15,0x V, -15,1 V), non 15 V tondi. Su questo banco quello script rifiuta tutte le 18 corse
per questo solo motivo (provato in L47c2b2, `partenza_l47c2b1.txt`). Qui il rail di partenza
deve coincidere entro 1 uV col primo punto del ponte del suo caso (vpp / vmm, o vpp_rif / vmm_rif
per i riferimenti). Il resto e' quello di L47c2b1: MAIN_A entro 0,5 V e i tre jack entro 1 mV.

Uso: verifica_partenza.py CORSE PONTE   -> una riga di sintesi; esce 1 se una corsa non va"""
import glob
import json
import os
import sys

d, ponte = sys.argv[1], sys.argv[2]
n, male = 0, []
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
        raise SystemExit("%s: %d colonne negli stati, attese 8 o 14: la wrdata non e' quella di L47c2b1"
                         % (s, len(xs)))
    vplus, vminus, main_a = float(xs[3]), float(xs[5]), float(xs[7])
    jack = [float(xj[1]), float(xj[3]), float(xj[5])]
    rif = c.startswith("rif_")
    caso = c[len("rif_"):] if rif else c
    caso = caso[:-len("_l41c")]
    pj = json.load(open(os.path.join(ponte, caso + ".json")))
    suf = "_rif" if rif else ""
    p0, m0 = pj["vpp" + suf]["punti"][0][1], pj["vmm" + suf]["punti"][0][1]
    n += 1
    ok = (abs(main_a) < 0.5 and max(abs(v) for v in jack) < 1e-3
          and abs(vplus - p0) < 1e-6 and abs(vminus - m0) < 1e-6)
    riga = "%s main_a %.4g jack max %.3g rail %.6f/%.6f ponte %.6f/%.6f" % (
        c, main_a, max(abs(v) for v in jack), vplus, vminus, p0, m0)
    print(("   " if ok else " X ") + riga)
    if not ok:
        male.append(c)
print("%s: %d corse, %d non partono dal punto giusto" % (d, n, len(male)))
sys.exit(1 if male else 0)
