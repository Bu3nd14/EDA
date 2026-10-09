#!/usr/bin/env python3
"""L48b: confronta due netlist KiCad di SKiDL per connettivita'. Le reti si identificano
dall'insieme dei loro piedini (ref, pin), non dal nome (SKiDL non sceglie il nome di una rete
fusa in modo riproducibile, limitations #23). Stampa le parti tolte/aggiunte/cambiate di
valore o d'impronta, e le reti (come insiemi di piedini) che esistono in una sola delle due.
Uso: confronta_netlist.py <prima.net> <dopo.net>"""
import re
import sys


def sexp(t):
    tok = re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+', t)
    pila = [[]]
    for x in tok:
        if x == "(":
            pila.append([])
        elif x == ")":
            e = pila.pop()
            pila[-1].append(e)
        else:
            pila[-1].append(x[1:-1] if x.startswith('"') else x)
    return pila[0][0]


def campo(e, nome):
    for x in e[1:]:
        if isinstance(x, list) and x and x[0] == nome:
            return x[1] if len(x) > 1 else ""
    return ""


def leggi(p):
    rad = sexp(open(p).read())
    parti, reti = {}, {}
    for sez in rad[1:]:
        if isinstance(sez, list) and sez[0] == "components":
            for c in sez[1:]:
                parti[campo(c, "ref")] = (campo(c, "value"), campo(c, "footprint"))
        if isinstance(sez, list) and sez[0] == "nets":
            for n in sez[1:]:
                nodi = frozenset((campo(x, "ref"), campo(x, "pin")) for x in n[1:]
                                 if isinstance(x, list) and x[0] == "node")
                reti[nodi] = campo(n, "name")
    return parti, reti


a_p, a_r = leggi(sys.argv[1])
b_p, b_r = leggi(sys.argv[2])
print("parti: prima %d, dopo %d; reti: prima %d, dopo %d" % (len(a_p), len(b_p), len(a_r), len(b_r)))
for r in sorted(set(a_p) - set(b_p)):
    print("TOLTA   %s %s" % (r, a_p[r]))
for r in sorted(set(b_p) - set(a_p)):
    print("NUOVA   %s %s" % (r, b_p[r]))
for r in sorted(set(a_p) & set(b_p)):
    if a_p[r] != b_p[r]:
        print("CAMBIA  %s %s -> %s" % (r, a_p[r], b_p[r]))
for n in sorted(set(a_r) - set(b_r), key=lambda n: a_r[n]):
    print("RETE SOLO PRIMA  %-14s %s" % (a_r[n], sorted(n)))
for n in sorted(set(b_r) - set(a_r), key=lambda n: b_r[n]):
    print("RETE SOLO DOPO   %-14s %s" % (b_r[n], sorted(n)))
