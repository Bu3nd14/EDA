#!/usr/bin/env python3
"""L64c: i due regolatori dei 5 V (U504, U512, MCP1703A) nelle 42 corse nuove della FMEA: la potenza e
la temperatura di giunzione, col metodo di riassunto_075.py di L45d2b3b1 (il conto e i limiti sono i
suoi, scritti di nuovo qui perche' quello script vuole il punto fisso del firmware, che non c'e' piu').

  P(t)    = |corrente d'uscita| x (V(IN) - V(OUT)): U504 da VRELAY_REG a V5_PRE (i(vsiu504_3)), U512 da
            V5_PRE a V5 (i(vsiu512_3))
  p100_W  la media piu' alta su una finestra di 100 ms, su TUTTA la corsa: i guasti degli ingressi
          sono latenti, presenti da t = 0, e lo stress comincia quando i 5 V salgono, non a TE
  pfin_W  la media degli ultimi 50 ms (quello che resta)
  tj100_C 60 + p100 x Rth(j-a), tjfin_C 60 + pfin x Rth(j-a): MCP1703A, Tj max 125 C, 62 K/W
          (LIM di riassunto_075.py, da limiti_parti.csv); l'MCP1703A ha lo spegnimento termico a 150 C
  esito   «fuori» se tj100_C o tjfin_C superano 125 C

Uso: /usr/bin/python3 -I calore_5v.py <seq/oggi> <out.csv> <caso> [...]    Solo stdlib.
"""
import csv
import os
import sys

TJ_MAX, RTH = 125.0, 62.0
PARTI = (("U504", "i(vsiu504_3)", "v(vrelay_reg)", "v(v5_pre)"),
         ("U512", "i(vsiu512_3)", "v(v5_pre)", "v(v5)"))


def leggi(path):
    with open(path) as f:
        nomi = f.readline().split()
        righe = [list(map(float, r.split())) for r in f if r.strip()]
    # wrdata ripete la colonna del tempo davanti a ogni vettore: si tiene la prima
    return {n: [r[k] for r in righe] for k, n in enumerate(nomi)}


def media_max(t, p, w):
    """La media piu' alta di p su una finestra lunga w (trapezi, finestra scorrevole sui campioni)."""
    best, j, acc = 0.0, 0, 0.0
    area = [0.0]
    for k in range(1, len(t)):
        area.append(area[-1] + 0.5 * (p[k] + p[k - 1]) * (t[k] - t[k - 1]))
    for k in range(len(t)):
        while t[k] - t[j] > w:
            j += 1
        if t[k] - t[j] >= 0.5 * w:
            best = max(best, (area[k] - area[j]) / (t[k] - t[j]))
    return best


def main(argv):
    seq, out, casi = argv[1], argv[2], argv[3:]
    righe = []
    for c in casi:
        d = os.path.join(seq, c)
        f = os.path.join(d, "tb_psu_seq_%s_g1_out.txt" % c)
        if not os.path.isfile(os.path.join(d, "ok.txt")):
            raise SystemExit("%s: manca ok.txt" % c)
        S = leggi(f)
        t = S["time"]
        for nome, i, vin, vout in PARTI:
            p = [abs(a) * max(b - c_, 0.0) for a, b, c_ in zip(S[i], S[vin], S[vout])]
            p100 = media_max(t, p, 0.1)
            kf = next(k for k in range(len(t)) if t[k] >= t[-1] - 0.05)
            pfin = (sum(0.5 * (p[k] + p[k - 1]) * (t[k] - t[k - 1]) for k in range(kf + 1, len(t)))
                    / (t[-1] - t[kf]))
            tj100, tjfin = 60 + p100 * RTH, 60 + pfin * RTH
            righe.append({"caso": c, "parte": nome + " (MCP1703A)",
                          "ipk_A": "%.4g" % max(abs(a) for a in S[i]), "p100_W": "%.4g" % p100,
                          "pfin_W": "%.4g" % pfin, "tj100_C": "%.1f" % tj100, "tjfin_C": "%.1f" % tjfin,
                          "esito": "fuori" if max(tj100, tjfin) > TJ_MAX else "dentro"})
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(righe[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(righe)
    for r in righe:
        if r["esito"] == "fuori" or float(r["p100_W"]) > 0.05:
            print(r["caso"], r["parte"], r["p100_W"], "W", r["tj100_C"], "C", r["esito"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
