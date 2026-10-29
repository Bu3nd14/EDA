#!/usr/bin/env python3
"""L54b3b: the verdict of each worst-corner run against its criterion (README, "I criteri").

/usr/bin/python3 -I verdetti_angoli.py <an_angoli.csv>
The label <ipotesi>_t<T>_<angolo>[_m10|_p10][_22] says which criterion; the case says where.
Besides the criterion, every run's verdicts must be the nominal case's: no latch at a power-up or
in music, the latch and K501 open in the faults, the music back at the end where it should be.
"""
import csv
import re
import sys


def num(r, k):
    return float(r[k]) if r.get(k, "") != "" else None


def giudica(ang, caso, r):
    lat, mus, k5 = r["ritenuta"], r["mus_end"], r["k501_end"]
    if ang == "dmus":
        v = num(r, "dmus_ms")
        return v, ">= 500 ms", v is not None and v >= 500 and lat == "0" and r["n_su"] == "1"
    if ang.startswith("dperm"):
        v = num(r, "d_perm_ms")
        ok = v is not None and v >= 16.9 and r["C2"] == "1" and r["C3"] == "1"
        if caso == "guasto":
            ok = ok and lat == "1" and k5 == "0"
        return v, ">= 16.9 ms", ok
    if ang.startswith("kperm"):
        v = num(r, "k_perm_ms")
        ok = v is not None and v >= 50
        if caso == "guasto":
            ok = ok and lat == "1"
        return v, ">= 50 ms", ok
    if ang in ("arm_acc", "arm_fr"):
        v = num(r, "arm_pg_ms")
        # not armed within the run = armed later still: it passes if the latch never tripped
        return v, "> 0 ms, no latch", (v is None or v > 0) and lat == "0" and mus == "1"
    if ang == "bn_fr":
        v = num(r, "bn_max")
        return v, "<= 0.45 V", v is not None and v <= 0.45 and lat == "0" and mus == "1"
    if ang == "arm_tardi":
        v = num(r, "t_arm_ms")
        if caso == "accensione_u501":
            return v, "latch, K501 open", lat == "1" and k5 == "0"
        return v, "no latch, music", lat == "0" and mus == "1"
    if ang == "jack_tardi":
        v = num(r, "dvm_mv")
        return v, "dV at the jack (mV)", r["s41"] in ("1", "") and r["C2"] == "1" and r["C3"] == "1"
    raise SystemExit("angolo sconosciuto %s" % ang)


righe = []
for r in csv.DictReader(open(sys.argv[1])):
    et, caso = r["caso"].split("/")
    m = re.match(r"(?:v_)?(c0g|x7r)_t(\d+)_([a-z_]+?)(_m10|_p10)?(_22)?$", et)
    assert m, et
    v, crit, ok = giudica(m.group(3), caso, r)
    righe.append((m.group(1), int(m.group(2)), m.group(3), caso, (m.group(4) or "") + (m.group(5) or ""),
                  v, crit, ok, r))
righe.sort(key=lambda x: (x[0], x[2], x[3], x[1], x[4]))
n_ko = 0
for ip, t, ang, caso, var, v, crit, ok, r in righe:
    n_ko += not ok
    print("%-4s %3d C %-10s %-16s %-8s %-10s %-22s %s  (rit %s mus %s k501 %s dvp %s dvm %s)"
          % (ip, t, ang, caso, var, "" if v is None else "%g" % v, crit, "ok" if ok else "FALLISCE",
             r["ritenuta"], r["mus_end"], r["k501_end"], r.get("dvp_mv", ""), r.get("dvm_mv", "")))
print("falliscono: %d su %d" % (n_ko, len(righe)))
