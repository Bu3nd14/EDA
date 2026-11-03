#!/usr/bin/env python3
"""L58a2: every fault / leakage / drift case of lista_l58a.py against the base of its own event, with
the criteria of L54b3b (README, «I criteri, scritti prima delle corse»):

  verdicts   musica_TE, mus_end, k501_end, ritenuta, n_giu, n_su, n_k501, C2, C3, r41, s41 must be
             the base's (the mute, the music, K501, the latch: "ogni verdetto come nel caso nominale")
  times      d_perm_ms >= 16.9 (ADR-045), dmus_ms >= 500 (buco20, ADR-104), k_perm_ms >= 50
             (ADR-046), arm_pg_ms > 0 at accensione / fredda, bn_max0 and bn_max <= 0.45 V where the
             base does not trip (ADR-103)
  shifts     t_mus_ms, t_jack_ms, t_gain_ms, t_k501_ms: printed when they move by more than 5 ms

Prints one block per case: "ok" or the list of what differs. Also writes <out.csv> with
caso,evento,difetti (one line per case), read by fmea_l58a.py.

Solo stdlib. /usr/bin/python3 -I confronta_l58a.py <an_l58a.csv> <out.csv>
"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modi  # noqa: E402

EV = modi.EVENTI_TIMER                       # key -> sequence name
SEQ_EV = {s: e for e, s in EV.items()}
VERD = ["musica_TE", "mus_end", "k501_end", "ritenuta", "n_giu", "n_su", "n_k501", "C2", "C3", "r41",
        "s41"]
TEMPI = ["t_mus_ms", "t_jack_ms", "t_gain_ms", "t_k501_ms"]


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
    righe = list(csv.DictReader(open(sys.argv[1])))
    base = {}
    for r in righe:
        et, caso = r["caso"].split("/")
        if et == "l58a_base":
            base[caso] = r
    out = []
    for r in righe:
        et, caso = r["caso"].split("/")
        if et == "l58a_base":
            continue
        if et == "l58a":
            seq = EV[caso.rsplit("_", 1)[1]]
        else:
            seq = caso
        d = difetti(r, base[seq], seq)
        print("%-34s %-16s %s" % (r["caso"], seq, "ok" if not d else "; ".join(d)))
        out.append(dict(caso=r["caso"], evento=seq, difetti="; ".join(d)))
    with open(sys.argv[2], "w", newline="") as f:
        w = csv.DictWriter(f, ["caso", "evento", "difetti"])
        w.writeheader()
        w.writerows(out)


main()
