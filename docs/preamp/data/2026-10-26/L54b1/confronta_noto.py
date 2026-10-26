#!/usr/bin/env python3
"""L54b1: the numerical known case. analizza_an.py's CSV of the source (--timer sorgente) against
L54a's (--timer comparatori), row by row in the same order, with the criteria of the README,
written before the runs:
  - the same verdicts: C2, C3, r41, s41, musica_TE, mus_end, k501_end, esito;
  - every instant within max(0.05 ms, 0.1 %); vplus_end within 0.01 V.
Exit 0 if every row holds, 1 otherwise. Solo stdlib.

Uso: /usr/bin/python3 -I confronta_noto.py <L54a.csv> <L54b1.csv> [righe di L54a da leggere]
"""
import csv
import sys

VERDETTI = ("musica_TE", "C2", "C3", "r41", "s41", "mus_end", "k501_end", "esito")
ISTANTI = ("t_jack_ms", "t_gain_ms", "t_v106_ms", "t_k501_ms", "t_mus_ms")


def righe(p):
    with open(p) as f:
        return list(csv.DictReader(f))


def main():
    a, b = righe(sys.argv[1]), righe(sys.argv[2])
    if len(sys.argv) > 3:
        a = a[:int(sys.argv[3])]
    ok = len(a) == len(b)
    if not ok:
        print("righe: L54a %d, L54b1 %d" % (len(a), len(b)))
    peggio = 0.0
    for ra, rb in zip(a, b):
        guai = []
        if ra["caso"] != rb["caso"]:
            guai.append("caso %s / %s" % (ra["caso"], rb["caso"]))
        for k in VERDETTI:
            if ra[k] != rb[k]:
                guai.append("%s %s -> %s" % (k, ra[k], rb[k]))
        dd = []
        for k in ISTANTI:
            if (ra[k] == "") != (rb[k] == ""):
                guai.append("%s %r -> %r" % (k, ra[k], rb[k]))
                continue
            if ra[k] == "":
                continue
            x, y = float(ra[k]), float(rb[k])
            lim = max(0.05, 1e-3 * abs(x))
            d = y - x
            peggio = max(peggio, abs(d) / lim)
            dd.append("%s %+.2f" % (k[2:-3], d))
            if abs(d) > lim + 1e-9:
                guai.append("%s %.2f -> %.2f ms (limite %.2f)" % (k, x, y, lim))
        if ra["vplus_end"] and rb["vplus_end"] and abs(float(ra["vplus_end"]) - float(rb["vplus_end"])) > 0.01:
            guai.append("vplus_end %s -> %s" % (ra["vplus_end"], rb["vplus_end"]))
        print("%-22s %s  %s" % (rb["caso"], "ok " if not guai else "NO ", "; ".join(guai) or " ".join(dd)))
        ok = ok and not guai
    print("\nil caso noto %s; scarto peggiore %.2f del limite" % ("TORNA" if ok else "NON TORNA", peggio))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
