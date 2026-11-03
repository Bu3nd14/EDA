#!/usr/bin/env python3
"""L41c: the guard on the generated audio deck, before any run.

L47c2b2: COPIED from L41c's (data/2026-09-26/L41c/deck/), which stays as it was,
WITHOUT the check that BILS / BILP were the bridge's: the LED strings and their
sources are gone (ADR-062, L47c2b1), and L41c's copy refuses today's deck for
that alone (tried in L47c2b1 on L41c's JSON). Instead it refuses a deck where
BILS / BILP, or the bridge's LED sources, come back. The check on the PWL
alters (limitations #36) is L41c's, unchanged.

Solo stdlib. /usr/bin/python3 controlla_deck.py <tb_v2_l41c.cir>

ngspice 47 drops an `alter @v[pwl] = [ ... ]` of 1000 numbers or more with only
"alter: too many args." and exit 0 (L41c: 400 points pass, 500 do not). This
refuses a deck with any PWL alter of more than 800 numbers.
"""
import re
import sys

testo = open(sys.argv[1]).read().splitlines()
mx, n_alter, rc = 0, 0, 0
for r in testo:
    m = re.match(r"alter @(\w+)\[pwl\] = \[ (.*) \]$", r)
    if m:
        n_alter += 1
        n = len(m.group(2).split())
        mx = max(mx, n)
        if n > 800 or n % 2:
            print("RIFIUTO: %s con %d numeri" % (m.group(1), n))
            rc = 1
led = [r for r in testo if r.startswith(("BILS ", "BILP ")) or "V(NIS)" in r or "V(NIP)" in r]
if led:
    print("RIFIUTO: le sorgenti delle stringhe LED sono tornate: %s" % led)
    rc = 1
if n_alter == 0:
    print("RIFIUTO: nessun alter pwl: il deck non porta il ponte")
    rc = 1
print("alter pwl: %d, al massimo %d numeri; %s; %s"
      % (n_alter, mx, "stringhe LED PRESENTI" if led else "niente stringhe LED",
         "ok" if rc == 0 else "RIFIUTATO"))
sys.exit(rc)
