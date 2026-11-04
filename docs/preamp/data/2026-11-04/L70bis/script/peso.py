#!/usr/bin/env python3
"""L70: the size of the files a status listing would add (?? lines), the biggest first, by kind.
    /usr/bin/python3 -I script/peso.py <status.txt> <radice del repo>
"""
import collections
import os
import sys

righe = [ln[3:].strip() for ln in open(sys.argv[1]) if ln.startswith("?? ")]
tot, per = 0, collections.Counter()
grandi = []
for p in righe:
    s = os.path.getsize(os.path.join(sys.argv[2], p))
    tot += s
    per[os.path.splitext(p)[1] or os.path.basename(p)] += s
    grandi.append((s, p))
print("%d file, %.1f MB" % (len(righe), tot / 1e6))
for k, s in per.most_common(10):
    print("  %-14s %.1f MB" % (k, s / 1e6))
for s, p in sorted(grandi, reverse=True)[:8]:
    print("  %.1f MB %s" % (s / 1e6, p))
