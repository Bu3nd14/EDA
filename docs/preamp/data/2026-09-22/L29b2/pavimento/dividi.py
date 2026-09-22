#!/usr/bin/env python3
"""L29b2: divide un deck di corse in sequenza (build.py / build_nd.py) in un deck per corsa,
da lanciare in parallelo. Le cifre non cambiano: ogni corsa reimposta da se' vamp, vti, vtr,
vtijk, vtrjk, e gli alter globali (rsrc, rrgb, ...) stanno nell'intestazione di tutti.
Il manifesto si scrive qui dalle righe echo, invece che da ngspice.

Uso:  /usr/bin/python3 dividi.py DECK.cir   ->  accanto: corsa_<nome>.cir, manifest.csv
"""
import os
import re
import sys

deck = os.path.abspath(sys.argv[1])
d = os.path.dirname(deck)
L = open(deck).read().splitlines()
c0 = L.index(".control")
# Il CONTESTO: ogni riga fuori da una corsa (alter globali, e gli alter dei carichi FRA
# un gruppo di corse e l'altro) vale per tutte le corse che la seguono, come nel deck in
# sequenza. Ogni corsa porta quindi il contesto accumulato fino a lei, non solo la testa:
# con la sola testa gli alter di un gruppo finivano in tutti i deck (L29b2, trovato
# prima di correre).
contesto = []
corse = []
manifest = []
cur = None
for r in L[c0 + 1:]:
    m = re.match(r'echo "(.*)" >>? (\S+)$', r)
    if m:
        manifest.append(m.group(1))
        continue
    if r.startswith("alter vamp"):
        cur = (list(contesto), [r])
        continue
    if cur is None:
        if r not in (".endc", ".end", ""):
            contesto.append(r)
        continue
    cur[1].append(r)
    if r == "destroy all":
        corse.append(cur)
        cur = None
assert corse and cur is None, "struttura inattesa"
nomi = []
for ctx, c in corse:
    w = next(x for x in c if x.startswith("wrdata"))
    nome = os.path.basename(w.split()[1]).replace("$d", "")
    nomi.append(nome)
    out = L[:c0 + 1] + ctx + c[:-1] + [".endc", ".end"]
    open(os.path.join(d, "corsa_%s.cir" % nome), "w").write("\n".join(out) + "\n")
open(os.path.join(d, "manifest.csv"), "w").write("\n".join(manifest) + "\n")
print("%d corse: %s; manifesto %d righe" % (len(corse), " ".join(nomi), len(manifest) - 1))
