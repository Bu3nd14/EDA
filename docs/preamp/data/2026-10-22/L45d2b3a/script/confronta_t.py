#!/usr/bin/python3
"""L45d2b3a: |T| and phase of two loop-gain files (wrdata f, mag, ph in radians) side by side.

usage: confronta_t.py <a.dat> <b.dat> f1 f2 ...
"""
import math
import sys


def leggi(path):
    f, m, p = [], [], []
    for riga in open(path):
        v = riga.split()
        try:
            f.append(float(v[0])); m.append(float(v[1])); p.append(float(v[2]) * 180 / math.pi)
        except (ValueError, IndexError):
            continue
    for k in range(1, len(p)):
        while p[k] - p[k - 1] > 180:
            p[k] -= 360
        while p[k] - p[k - 1] < -180:
            p[k] += 360
    return f, m, p


def a(fs, ys, x):
    for k in range(1, len(fs)):
        if fs[k] >= x:
            t = math.log(x / fs[k - 1]) / math.log(fs[k] / fs[k - 1])
            return ys[k - 1] + t * (ys[k] - ys[k - 1])
    return float("nan")


A, B = leggi(sys.argv[1]), leggi(sys.argv[2])
print("f_Hz\t|T|a\tfase_a\t|T|b\tfase_b")
for x in map(float, sys.argv[3:]):
    print("%g\t%.4g\t%.1f\t%.4g\t%.1f" % (x, a(A[0], A[1], x), a(A[0], A[2], x),
                                         a(B[0], B[1], x), a(B[0], B[2], x)))
