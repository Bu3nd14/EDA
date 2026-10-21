#!/usr/bin/env python3
"""L45d2b2b1: ADR-074's 24 rows (RIGHE_074 at three mains levels; D510 / D511 shorted left out) per
option, the worst row of each quantity. Stdlib.

    confronto_opzioni.py <out.csv> <etichetta>=<analisi.csv> ...
"""
import csv
import sys


def f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


righe = []
for arg in sys.argv[2:]:
    nome, path = arg.split("=", 1)
    rs = [r for r in csv.DictReader(open(path)) if not r["caso"].startswith(("f_d510", "f_d511"))]

    def peggio(col, fn=max, rs=rs):
        v = [(f(r.get(col)), r["caso"]) for r in rs if f(r.get(col)) is not None]
        return fn(v) if v else (None, "")

    oim, oim_c = peggio("oi_pin_m")
    oip, oip_c = peggio("oi_pin_p")
    toi, toi_c = peggio("t_oi_m_ms")
    i511, i511_c = peggio("id511_pk_A")
    i510, i510_c = peggio("id510_pk_A")
    i2t, i2t_c = peggio("i2t_511")
    i2tp, _ = peggio("i2t_510")
    vmj, vmj_c = peggio("vm_al_jack")          # the least negative - rail at the jack
    vpj, vpj_c = peggio("vp_al_jack", min)
    righe.append({
        "opzione": nome, "righe": len(rs),
        "jack_dopo_10_6": sum(r["jack_prima"] == "no" for r in rs),
        "sorvegliante_oltre_1ms": sum(r["sorvegliante_1ms"] == "no" for r in rs),
        "oi_u502_max_V": oim, "caso_oi_u502": oim_c, "t_oltre_0_3_max_ms": toi, "caso_t": toi_c,
        "oi_u501_max_V": oip, "caso_oi_u501": oip_c,
        "d511_pk_A": i511, "d510_pk_A": i510, "i2t_511_max": i2t, "i2t_510_max": i2tp,
        "vp_al_jack_min": vpj, "caso_vp": vpj_c, "vm_al_jack_max": vmj, "caso_vm": vmj_c})
with open(sys.argv[1], "w", newline="") as fo:
    w = csv.DictWriter(fo, fieldnames=list(righe[0].keys()))
    w.writeheader()
    for r in righe:
        w.writerow({k: ("%.4g" % v if isinstance(v, float) else v) for k, v in r.items()})
for r in righe:
    print(" ".join("%s=%s" % (k, ("%.4g" % v if isinstance(v, float) else v)) for k, v in r.items()))
