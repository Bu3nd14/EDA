"""genera_cf.py - L47b2b1: il controfattuale del click con la dispersione degli offset (A, gruppo 3).

Nel banco V2 VOSA sta fra il nodo delle celle (INA) e l'ingresso del blocco A (INAX), e R113
(1 Mohm, R_IN) sta DENTRO il blocco, fra INAX e massa. Con VOSA = 20 mV il banco fa scorrere
20 mV / 1 Mohm = 20 nA nella rete delle celle: a meta' sfumatura, con le due celle a ~100 kohm, la
continua su INA si sposta di millivolt e il gradino arriva al jack (A 211 uV, v2/sorgente).

Nel circuito R_IN sta sul gate, e un offset del differenziale d'ingresso non manda corrente nella
rete d'ingresso (il gate assorbe pA). Il controfattuale lo rimette cosi': IOSA fra INAX e massa,
uguale a VOSA / 1 Mohm, fornisce a R113 la corrente dell'offset, e nella rete delle celle non ne
passa. L'offset al gate (e quindi il gradino d'offset all'uscita del blocco, lo scopo del gruppo 3)
resta quello di prima.

    /usr/bin/python3 genera_cf.py <deck versionato> <uscita.cir>
"""
import re
import sys

src, out = sys.argv[1], sys.argv[2]
righe = open(src).read().splitlines()
nuove, n_alter = [], 0
for r in righe:
    nuove.append(r)
    if r.startswith("VOSA INA INAX"):
        nuove.append("* L47b2b1, controfattuale: la corrente di R113 dovuta a VOSA non passa nelle celle")
        nuove.append("IOSA INAX 0 DC 0")
    m = re.match(r"^alter vosa dc = (\S+)$", r)
    if m:
        v = m.group(1)
        val = float(v[:-1]) * 1e-3 if v.endswith("m") else float(v)
        nuove.append("alter iosa dc = %.6g" % (val / 1e6))
        n_alter += 1
nuove[0] = nuove[0] + " [L47b2b1: controfattuale IOSA]"
open(out, "w").write("\n".join(nuove) + "\n")
print("scritto %s: IOSA aggiunta, %d alter vosa accoppiati" % (out, n_alter))
