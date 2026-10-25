#!/usr/bin/env python3
"""Dopo L57b: la corrente nei due riferimenti durante l'RCA a caldo, col modello del costruttore.

Col modello di Diodes Inc. (TT 4,32 us) il picco nel diodo e' 5,6 mA contro 1,07 della stima di L57b:
la carica immagazzinata. Qui si misura quanto ne arriva all'LM4040 (la corrente in VU1 / VU2 di
INREF_EQ, cioe' nella ZR) e quanto al suo 100 nF, il picco e la media sull'evento, contro i 15 mA
raccomandati (SNOS633N p. 6) e i 20 mA assoluti (p. 5).

Prende il deck generato da genera.py per lim_rete11 (classe II, rete +10 %), aggiunge le misure dopo
ogni caso e lo scrive in rca/rif/. Uso: /usr/bin/python3 rif_corrente.py  (poi run_simulation.sh)
"""
import os
import subprocess

QUI = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(os.path.dirname(QUI), "rca", "rif")
os.makedirs(D, exist_ok=True)
deck = os.path.join(D, "rif_lim_rete11.cir")
subprocess.run(["/usr/bin/python3", os.path.join(QUI, "genera.py"), "oggi", deck, "--prot", "S,rif=eq",
                "--rete", "1.1", "--casi", "classeII"], check=True)
t = open(deck).read()
anc = "meas tran vlmmin min v(vlim_m) from=50m to=0.4\n"
n = t.count(anc)
assert n == 8, n
add = anc + """let iu1 = abs(i(vu1)) * 1000
let iu2 = abs(i(vu2)) * 1000
let ic1 = abs(i(vu1) - (v(vplus) - v(vlim_p)) / 10k) * 1000
meas tran iu1max max iu1 from=50m to=0.4
meas tran iu2max max iu2 from=50m to=0.4
meas tran iu1avg avg iu1 from=60m to=0.4
meas tran iu2avg avg iu2 from=60m to=0.4
echo "RIF_CORRENTE iu1_max_ma=$&iu1max iu2_max_ma=$&iu2max iu1_media_ma=$&iu1avg iu2_media_ma=$&iu2avg"
"""
t = t.replace(anc, add)
t = t.replace("rca - L57b: ", "rif - dopo L57b: la corrente nei riferimenti, ", 1)
open(deck, "w").write(t)
print(deck)
