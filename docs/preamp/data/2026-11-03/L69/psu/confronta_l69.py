#!/usr/bin/env python3
"""L69: every healthy run of an option (seq/<option>[_m10|_p10|_t22]/<sequence>) against L64b's healthy
run of the same sequence (data/2026-11-03/L64b/an_l64b.csv), with the criteria of L54b3b written before
the runs: difetti() of confronta_l68.py, copied (that file runs on import).

  base   <opt>/<seq> -> oggi/<seq>; <opt>_m10 -> oggi_m10; <opt>_p10 -> oggi_p10; <opt>_t22 -> oggi
         (L64b has no run with the comparator at 2.2 V: the base is the nominal one, its shifts noted).
         A sequence without its base at +-10 % (guasto) is compared with oggi/<seq>: declared.
  fault runs (f_...) are listed with ritenuta, on_min and v5_min only: their verdict is the heat
  (script/calore_ritenuta.py)

Writes <out.csv>: caso, base, difetti, on_min, ritenuta.  Solo stdlib.
    /usr/bin/python3 -I psu/confronta_l69.py an_vaglio.csv confronto_vaglio.csv
"""
import csv
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
AN_B = os.path.join(QUI, "..", "..", "L64b", "an_l64b.csv")
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
    an = list(csv.DictReader(open(sys.argv[1], newline="")))
    b64 = {r["caso"]: r for r in csv.DictReader(open(AN_B, newline=""))}
    out = []
    for r in sorted(an, key=lambda x: x["caso"]):
        etich, seq = r["caso"].split("/")[-2:]
        if seq.startswith("f_"):
            out.append(dict(caso=r["caso"], base="-", difetti="(guasto: vedi il calore)",
                            on_min=r.get("on_min", ""), ritenuta=r.get("ritenuta", "")))
            continue
        suf = etich.rsplit("_", 1)[1] if "_" in etich else ""
        bl = {"m10": "oggi_m10", "p10": "oggi_p10"}.get(suf, "oggi")
        nota = []
        if bl + "/" + seq not in b64:
            nota.append("base %s/%s assente: oggi/%s" % (bl, seq, seq))
            bl = "oggi"
        if suf == "t22":
            nota.append("comparatore a 2,2 V contro la base a 2,0 V")
        b = b64[bl + "/" + seq]
        d = difetti(r, b, seq)
        out.append(dict(caso=r["caso"], base="%s/%s" % (bl, seq),
                        difetti="; ".join(d + ["(%s)" % n for n in nota]) if d or nota else "",
                        on_min=r.get("on_min", ""), ritenuta=r.get("ritenuta", "")))
    with open(sys.argv[2], "w", newline="") as f:
        w = csv.DictWriter(f, ["caso", "base", "difetti", "on_min", "ritenuta"], lineterminator="\n")
        w.writeheader()
        w.writerows(out)
    for x in out:
        print("%-32s on_min %-7s rit %-2s %s" % (x["caso"], x["on_min"], x["ritenuta"], x["difetti"] or "ok"))


main()
