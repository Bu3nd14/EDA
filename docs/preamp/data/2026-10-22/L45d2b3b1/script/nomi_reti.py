#!/usr/bin/env python3
"""L45d2b3b1: le reti di due netlist KiCad confrontate per insieme di piedini, non per nome. Una rete
con gli stessi piedini (a meno delle parti nuove) e un nome diverso e' un cambio di nome: SKiDL tiene
uno solo dei nomi di due reti unite, e quale dipende dall'ordine. Solo stdlib, /usr/bin/python3 -I.

Uso: nomi_reti.py <prima.net> <dopo.net> [parti nuove, separate da virgole]
"""
import re
import sys


def reti(p):
    t = open(p).read().split("(nets", 1)[1]
    out = {}
    for blocco in re.split(r"\(net\s", t)[1:]:
        nome = re.search(r'\(name\s+"([^"]*)"\)', blocco).group(1)
        out[nome] = frozenset(re.findall(r'\(node\s+\(ref\s+"([^"]+)"\)\s+\(pin\s+"([^"]+)"\)', blocco))
    return out


a, b = reti(sys.argv[1]), reti(sys.argv[2])
nuove = set(sys.argv[3].split(",")) if len(sys.argv) > 3 else set()
pulisci = lambda s: frozenset(x for x in s if x[0] not in nuove)
per_pin_b = {pulisci(v): k for k, v in b.items()}
cambiati, spariti = [], []
for k, v in sorted(a.items()):
    kb = per_pin_b.get(pulisci(v))
    if kb is None:
        spariti.append(k)
    elif kb != k:
        cambiati.append((k, kb))
print("reti prima %d, dopo %d; nome cambiato %d, piedini cambiati %d" % (len(a), len(b), len(cambiati), len(spariti)))
for k, kb in cambiati:
    print("  NOME   %s -> %s" % (k, kb))
for k in spariti:
    print("  PIEDINI %s" % k)
