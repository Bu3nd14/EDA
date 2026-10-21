#!/usr/bin/env python3
"""L45d2b2b2: the normal sequences with and without ADR-075's options - ADR-075's «Da riaprire se»
(the limit must not slow the jack's release nor Delta, P9 (b)). Solo stdlib.

    confronta_norm.py <seq/base> <seq/opzione> <out.csv>

Per case (lista_norm.txt): t_jack_ms, t_guadagno_ms (analizza_psu.py of L45c1, the jack the latest,
the gain the earliest), anticipo_guadagno_ms (analizza_rele.py of L45c2: > 0 = Delta lost), the first
MUSICA of the core (accensione, rilascio), V5 at the end, and the differences.
"""
import csv
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
from analizza_075 import A74, REL, A  # noqa: E402

CASI = ["perdita", "f_base_niente_ins", "accensione", "spegnimento", "rilascio"]


def musica(d):
    g = int(open(os.path.join(d, "punto_fisso.txt")).read())
    for r in open(os.path.join(d, "core_g%d.csv" % g)).read().split("\n")[1:]:
        p = r.split(",")
        if len(p) == 6 and p[5] == "MUSICA" and float(p[0]) > 0:
            return 1e3 * (float(p[0]) - A.TE)
    return ""


def misura(seq, nome):
    r = A74.caso(seq, nome)
    rr = REL.caso(seq, nome)
    d = os.path.join(seq, nome)
    g = int(open(os.path.join(d, "punto_fisso.txt")).read())
    S = A.leggi(os.path.join(d, "tb_psu_seq_%s_g%d_out.txt" % (nome, g)))
    v5 = S.get("v(v5)")
    return {"t_jack_ms": r["t_jack_ms"], "t_guadagno_ms": r["t_guadagno_ms"],
            "anticipo_guadagno_ms": rr["anticipo_guadagno_ms"], "musica_ms": musica(d),
            "vrelay_reg_fine": S["v(vrelay_reg)"][-1]}


def main():
    base, opz, out = sys.argv[1:4]
    righe = []
    for c in CASI:
        b, o = misura(base, c), misura(opz, c)
        x = {"caso": c}
        for k in b:
            x[k + "_base"], x[k + "_opz"] = b[k], o[k]
            try:
                x[k + "_diff"] = float(o[k]) - float(b[k])
            except (TypeError, ValueError):
                x[k + "_diff"] = ""
        righe.append(x)
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(righe[0]))
        w.writeheader()
        for x in righe:
            w.writerow({a: ("%.4g" % v if isinstance(v, float) else v) for a, v in x.items()})
    for x in righe:
        print(x["caso"], {k: x[k] for k in x if k.endswith("_diff")})


main()
