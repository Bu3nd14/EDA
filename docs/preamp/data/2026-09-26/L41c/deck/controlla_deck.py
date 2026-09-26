#!/usr/bin/env python3
"""L41c: the guard on the generated audio deck, before any run.

Solo stdlib. /usr/bin/python3 controlla_deck.py <tb_v2_l41c.cir>

ngspice 47 drops an `alter @v[pwl] = [ ... ]` of 1000 numbers or more with only
"alter: too many args." and exit 0 (L41c: 400 points pass, 500 do not). This
refuses a deck with any PWL alter of more than 800 numbers, and checks that
the bridged LED sources replaced BILS / BILP (and only in this matrix).
"""
import re
import sys

testo = open(sys.argv[1]).read().splitlines()
mx, rc = 0, 0
for r in testo:
    m = re.match(r"alter @(\w+)\[pwl\] = \[ (.*) \]$", r)
    if m:
        n = len(m.group(2).split())
        mx = max(mx, n)
        if n > 800 or n % 2:
            print("RIFIUTO: %s con %d numeri" % (m.group(1), n))
            rc = 1
bils = [r for r in testo if r.startswith(("BILS ", "BILP "))]
if bils != ["BILS 0 ALS I = V(NIS)", "BILP 0 ALP I = V(NIP)"]:
    print("RIFIUTO: BILS/BILP non sono quelli del ponte: %s" % bils)
    rc = 1
print("alter pwl: al massimo %d numeri; BILS/BILP dal ponte; %s" % (mx, "ok" if rc == 0 else "RIFIUTATO"))
sys.exit(rc)
