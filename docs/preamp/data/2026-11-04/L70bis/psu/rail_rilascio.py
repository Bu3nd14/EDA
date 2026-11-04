#!/usr/bin/env python3
"""L58a2: the rails at each release of the mute after TE (VRELAY - MUTE_CMD crossing 6 V upwards),
against their final value and their extremes after TE: is the music released into settled rails?

Solo stdlib. /usr/bin/python3 -I rail_rilascio.py <seq_dir>/<caso> [...]
"""
import os
import sys

TE = 3.0


def leggi(path):
    with open(path) as f:
        nomi = f.readline().split()
        righe = [list(map(float, r.split())) for r in f if r.strip()]
    return {n: [r[k] for r in righe] for k, n in enumerate(nomi)}


for d in sys.argv[1:]:
    fs = [f for f in os.listdir(d) if f.endswith("_g1_out.txt")]
    w = leggi(os.path.join(d, fs[0]))
    t, vp, vm, vr, mc = w["time"], w["v(vplus)"], w["v(vminus)"], w["v(vrelay)"], w["v(mute_cmd)"]
    on = [vr[k] - mc[k] > 6 for k in range(len(t))]
    nome = os.path.basename(os.path.dirname(d.rstrip("/"))) + "/" + os.path.basename(d.rstrip("/"))
    kte = min(range(len(t)), key=lambda k: abs(t[k] - TE))
    print("%-34s dopo TE: V+ %.3f..%.3f, V- %.3f..%.3f V; finali %.3f / %.3f" % (
        nome, min(vp[kte:]), max(vp[kte:]), min(vm[kte:]), max(vm[kte:]), vp[-1], vm[-1]))
    for k in range(max(1, kte), len(t)):
        if on[k] and not on[k - 1]:
            # the rails over the 50 ms after the release
            k50 = [j for j in range(k, len(t)) if t[j] <= t[k] + 0.05]
            print("   rilascio a %.1f ms: V+ %.4f, V- %.4f; nei 50 ms dopo V+ %.4f..%.4f, V- %.4f..%.4f"
                  % ((t[k] - TE) * 1e3, vp[k], vm[k], min(vp[j] for j in k50), max(vp[j] for j in k50),
                     min(vm[j] for j in k50), max(vm[j] for j in k50)))
