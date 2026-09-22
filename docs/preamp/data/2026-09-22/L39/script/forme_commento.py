#!/usr/bin/env python3
"""L39: per ogni deck di spice/preamp/tb/, le righe di commento '*' che citano i
modelli (segnaposto, vendor, costruttore, KF, LSK489X, NC-017, NC-031), con il numero
di riga. Serve a riscrivere le intestazioni sapendo cosa dicono oggi (blocco 2h)."""
import glob
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."] * 6))
PAT = re.compile(r"segnaposto|placeholder|vendor|costruttore|real device|KF|LSK489X|"
                 r"NC-017|NC-031|NSS2N5551|PSS2N5401|NMJE|PMJE|D1N4148|PTHAT|"
                 r"2N5551|2N5401|hand-written|scritt[oi] a mano|Fase 4|1/f", re.I)
for f in sorted(glob.glob(os.path.join(ROOT, "spice/preamp/tb/*.cir"))):
    rows = [(i + 1, l.rstrip()) for i, l in enumerate(open(f))
            if (l.startswith("*") or l.startswith(".include") or i == 0) and PAT.search(l)]
    print("=== %s (%d)" % (os.path.basename(f), len(rows)))
    if "-v" in sys.argv:
        for n, l in rows:
            print("%4d %s" % (n, l[:150]))
