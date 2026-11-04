#!/usr/bin/env python3
"""L58b: the deck of the NEW source (Q501 + Q509, R586 / R587 in psu.net, ADR-110) against the deck of
the measured variant (the source before, with --q501serie 1e6:10000). The pair's four lines are compared
as a set after renaming the nodes (q501_g = g501a, q501_mid = n501m, q509_g = g501b; the part names
RR586 / RR587 = RQ501G / RQ509G, values 1MEG = 1e+06, 10k = 10000); every other line must be identical
and in the same order. Solo stdlib.
Uso: sorgente_uguale.py <deck_sorgente.cir> <deck_variante.cir>
"""
import sys

MAPPA = {"q501_g": "g501a", "q501_mid": "n501m", "q509_g": "g501b", "RR586": "RQ501G",
         "RR587": "RQ509G", "1MEG": "1e+06", "10k": "10000"}
COPPIA = ("MQ501", "MQ509", "RR586", "RR587", "RQ501G", "RQ509G")


def leggi(p, mappa):
    righe = open(p).read().splitlines()
    coppia = sorted(" ".join(mappa.get(t, t) for t in r.split()) for r in righe
                    if r.split() and r.split()[0] in COPPIA)
    resto = [r for r in righe if not (r.split() and r.split()[0] in COPPIA)]
    return coppia, resto


cs, rs = leggi(sys.argv[1], MAPPA)
cv, rv = leggi(sys.argv[2], {})
print("la coppia:", "UGUALE" if cs == cv else "DIVERSA\n  %s\n  %s" % (cs, cv))
diff = [(a, b) for a, b in zip(rs, rv) if a != b]
print("il resto: %d righe contro %d, %d diverse" % (len(rs), len(rv), len(diff)))
for a, b in diff[:10]:
    print("  < %s\n  > %s" % (a, b))
sys.exit(0 if cs == cv and len(rs) == len(rv) and not diff else 1)
