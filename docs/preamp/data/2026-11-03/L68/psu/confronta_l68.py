#!/usr/bin/env python3
"""L68: every case of lista_l68.txt against the healthy run of its own event, with the criteria of
L54b3b written before the runs (confronta_l58a.py's difetti(), copied here: that file runs on import).

  the base of an event of the timer (accs ... inss): L64b's run of its sequence, data/2026-11-03/L64b/
  an_l64b.csv (oggi/<sequence>); the two bases run here (seq/base/accensione, fredda) give it back
  column for column. The base of muss (a fault at TE in music): seq/oggi/f_base_niente_muss, run here.

  verdicts   musica_TE, mus_end, k501_end, ritenuta, n_giu, n_su, n_k501, C2, C3, r41, s41 as the base's
  times      d_perm_ms >= 16.9 (ADR-045), dmus_ms >= 500 (buco20, ADR-104), k_perm_ms >= 50 (ADR-046),
             arm_pg_ms > 0 at accensione / fredda, bn_max0 and bn_max <= 0.45 V where the base does
             not trip (ADR-103)
  shifts     t_mus_ms, t_jack_ms, t_gain_ms, t_k501_ms: listed when they move by more than 5 ms

Writes <out.csv>: caso, ref, modo, evento, difetti. Solo stdlib.
    /usr/bin/python3 -I psu/confronta_l68.py an_l68.csv confronto_l68.csv
"""
import csv
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
import modi  # noqa: E402

AN_B = os.path.join(QUI, "..", "..", "L64b", "an_l64b.csv")
VERD = ["musica_TE", "mus_end", "k501_end", "ritenuta", "n_giu", "n_su", "n_k501", "C2", "C3", "r41",
        "s41"]
TEMPI = ["t_mus_ms", "t_jack_ms", "t_gain_ms", "t_k501_ms"]
EV = dict(modi.EVENTI_L58B, muss="musica")


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def difetti(r, b, seq):
    out = []
    if r.get("esito") != "letto":
        return ["corsa non letta: %s" % r.get("esito")]
    for c in VERD:
        if r.get(c, "") != b.get(c, ""):
            out.append("%s %s -> %s" % (c, b.get(c, ""), r.get(c, "")))
    lim = [("d_perm_ms", 16.9, ">="), ("k_perm_ms", 50.0, ">=")]
    if seq == "buco20":
        lim.append(("dmus_ms", 500.0, ">="))
    for c, v, _op in lim:
        x = num(r.get(c))
        if x is not None and x < v:
            out.append("%s %.1f < %.1f (base %s)" % (c, x, v, b.get(c, "")))
    if seq in ("accensione", "fredda"):
        x = num(r.get("arm_pg_ms"))
        if x is not None and x <= 0:
            out.append("arm_pg_ms %.1f <= 0 (base %s)" % (x, b.get("arm_pg_ms", "")))
    if b.get("ritenuta") == "0":
        for c in ("bn_max0", "bn_max"):
            x = num(r.get(c))
            if x is not None and x > 0.45:
                out.append("%s %.3f V > 0,45 (base %s)" % (c, x, b.get(c, "")))
    for c in TEMPI:
        x, y = num(r.get(c)), num(b.get(c))
        if (x is None) != (y is None):
            out.append("%s %s -> %s" % (c, b.get(c, "") or "-", r.get(c, "") or "-"))
        elif x is not None and abs(x - y) > 5:
            out.append("%s %.1f -> %.1f" % (c, y, x))
    return out


def main():
    an = {r["caso"]: r for r in csv.DictReader(open(sys.argv[1], newline=""))}
    b64 = {r["caso"]: r for r in csv.DictReader(open(AN_B, newline=""))}
    base = {e: b64["oggi/" + s] for e, s in modi.EVENTI_L58B.items()}
    base["muss"] = an["oggi/f_base_niente_muss"]
    guasti = {c[0]: c for c in modi.SIMULATI}
    out = []
    for k, r in sorted(an.items()):
        caso = k.split("/")[-1]
        if not caso.startswith("f_") or caso.startswith("f_base_"):
            continue
        e = caso.rsplit("_", 1)[1]
        d = difetti(r, base[e], EV[e])
        g = guasti[caso]
        out.append(dict(caso=caso, ref=g[1], modo=g[2], evento=EV[e], difetti="; ".join(d)))
        print("%-26s %-18s %s" % (caso, EV[e], "ok" if not d else "; ".join(d)))
    with open(sys.argv[2], "w", newline="") as f:
        w = csv.DictWriter(f, ["caso", "ref", "modo", "evento", "difetti"], lineterminator="\n")
        w.writeheader()
        w.writerows(out)


main()
