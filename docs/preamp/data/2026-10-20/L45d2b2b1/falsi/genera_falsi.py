#!/usr/bin/env python3
"""L45d2b2b1: the fakes of ADR-093's checks, from today's psu.net. Stdlib.

    genera_falsi.py <psu.net> <cartella>

  psu_d515_rovescio.net   D515 the wrong way round (its pins 1 and 2 swapped): VPLUS would be dead.
                          check_psu_harness.py must refuse it.
"""
import re
import sys

src, out = sys.argv[1], sys.argv[2]
t = open(src).read()
n = 0


def scambia(m):
    global n
    n += 1
    return '(ref "D515") (pin "%s")' % {"1": "2", "2": "1"}[m.group(1)]


t2 = re.sub(r'\(ref "D515"\)\s*\(pin "([12])"\)', scambia, t)
assert n == 2, n
open(out.rstrip("/") + "/psu_d515_rovescio.net", "w").write(t2)
print("scritto psu_d515_rovescio.net (%d piedini scambiati)" % n)
