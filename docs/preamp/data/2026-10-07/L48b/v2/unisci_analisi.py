#!/usr/bin/env python3
"""L48b: unisce analisi CSV con la stessa intestazione (la parziale delle 152 corse e quella delle
righe a 20 kHz, corse dopo). Uso: unisci_analisi.py <uscita.csv> <a.csv> <b.csv> ..."""
import sys

uscita, *ingressi = sys.argv[1:]
testa, righe = None, []
for p in ingressi:
    r = open(p).read().splitlines()
    assert testa in (None, r[0]), p
    testa = r[0]
    righe += r[1:]
open(uscita, "w").write("\n".join([testa] + righe) + "\n")
print("%d righe da %d file -> %s" % (len(righe), len(ingressi), uscita))
