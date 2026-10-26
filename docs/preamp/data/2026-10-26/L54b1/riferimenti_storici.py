#!/usr/bin/env python3
"""L54b1: every reference ever used in circuits/preamp/psu.net, across its git history, so that the
timer's new parts take numbers that no older report uses for another part. Solo stdlib.

Uso: /usr/bin/python3 -I riferimenti_storici.py <repo>
"""
import re
import subprocess
import sys

repo = sys.argv[1]
revs = subprocess.run(["git", "-C", repo, "log", "--format=%H", "--", "circuits/preamp/psu.net"],
                      capture_output=True, text=True, check=True).stdout.split()
visti = {}
for h in revs:
    r = subprocess.run(["git", "-C", repo, "show", "%s:circuits/preamp/psu.net" % h],
                       capture_output=True, text=True)
    if r.returncode:
        continue
    for ref in set(re.findall(r'\(comp\s*\(ref "([A-Z]+)(\d+)"\)', r.stdout)):
        visti.setdefault(ref[0], set()).add(int(ref[1]))
print("versioni di psu.net lette: %d" % len(revs))
for k in sorted(visti):
    n = sorted(visti[k])
    print("%-3s max %d  usati: %s" % (k, n[-1], " ".join(map(str, n))))
