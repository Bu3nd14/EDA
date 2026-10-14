#!/usr/bin/env python3
"""L45d2b1: due netlist KiCad a confronto per contenuto, non per testo (i tstamp cambiano a ogni
generazione). Solo stdlib. Uso: confronta.py PRIMA.net DOPO.net

Stampa le parti aggiunte, tolte o cambiate (valore, footprint) e le reti il cui insieme di pin e'
cambiato, togliendo dal confronto i pin delle parti aggiunte: cio' che resta e' cio' che il lotto
ha toccato di quel che c'era gia'. Esce con 0.
"""
import re
import sys


def leggi(path):
    """Il parser di scripts/check_relay_safe_state.py e check_psu_harness.py, piu' il footprint."""
    t = open(path).read()
    parti = {}
    for m in re.finditer(r'\(comp\b.*?\(ref "([^"]+)"\).*?\(value "([^"]*)"\).*?\(footprint "([^"]*)"\)',
                         t.split("(nets", 1)[0], re.S):
        parti[m.group(1)] = (m.group(2), m.group(3))
    reti = {}
    for chunk in re.split(r"\(net\s*\(code", t.split("(nets", 1)[-1])[1:]:
        m = re.search(r'\(name "([^"]*)"\)', chunk)
        if m:
            reti[m.group(1)] = frozenset(re.findall(r'\(ref "([^"]+)"\)\s*\(pin "([^"]+)"\)', chunk))
    return parti, reti


def main(a, b):
    pa, ra = leggi(a)
    pb, rb = leggi(b)
    agg = sorted(set(pb) - set(pa))
    tol = sorted(set(pa) - set(pb))
    camb = sorted(r for r in set(pa) & set(pb) if pa[r] != pb[r])
    print("parti: prima %d, dopo %d" % (len(pa), len(pb)))
    print("aggiunte (%d): %s" % (len(agg), " ".join(agg)))
    print("tolte (%d): %s" % (len(tol), " ".join(tol)))
    for r in camb:
        print("cambiata %s: %s -> %s" % (r, pa[r], pb[r]))
    nuove = set(agg)
    # per pin: la rete di ogni (ref, pin) delle parti che c'erano
    def per_pin(reti):
        d = {}
        for n, nodi in reti.items():
            for ref, pin in nodi:
                if ref not in nuove:
                    d[(ref, pin)] = n
        return d
    da, db = per_pin(ra), per_pin(rb)
    # le reti si confrontano per insieme di pin vecchi, non per nome (SKiDL rinomina)
    ga = {}
    for k, n in da.items():
        ga.setdefault(n, set()).add(k)
    gb = {}
    for k, n in db.items():
        gb.setdefault(n, set()).add(k)
    sa = {frozenset(v) for v in ga.values()}
    sb = {frozenset(v) for v in gb.values()}
    diverse = [v for v in sb if v not in sa]
    print("reti dei pin che c'erano: %d prima, %d dopo, %d diverse" % (len(sa), len(sb), len(diverse)))
    for v in diverse:
        nome = db[next(iter(v))]
        print("  diversa: %s (%d pin)" % (nome, len(v)))
    rinominate = sorted({(n, db[next(iter(v))]) for n, v in ga.items()
                         if frozenset(v) in sb and db[next(iter(v))] != n})
    for x, y in rinominate:
        print("  rinominata: %s -> %s" % (x, y))
    # dove si attaccano le parti nuove
    for n, nodi in sorted(rb.items()):
        nn = sorted(r + "." + p for r, p in nodi if r in nuove)
        vecchi = [x for x in nodi if x[0] not in nuove]
        if nn and vecchi:
            print("  la rete %s (%d pin di prima) riceve %s" % (n, len(vecchi), " ".join(nn[:6]) + (" ..." if len(nn) > 6 else "")))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
