#!/usr/bin/env python3
"""L54b3b: every run folder seq/<etichetta>/<caso> without ok.txt (a run refused, interrupted or never
finished), and the count of the folders. Solo stdlib. /usr/bin/python3 -I senza_ok.py <cartella seq>
"""
import os
import sys

s = sys.argv[1]
n = 0
for et in sorted(os.listdir(s)):
    d = os.path.join(s, et)
    if not os.path.isdir(d):
        continue
    for c in sorted(os.listdir(d)):
        p = os.path.join(d, c)
        if os.path.isdir(p):
            n += 1
            if not os.path.exists(os.path.join(p, "ok.txt")):
                print("senza ok.txt: %s/%s" % (et, c))
print("cartelle di corsa: %d" % n)
