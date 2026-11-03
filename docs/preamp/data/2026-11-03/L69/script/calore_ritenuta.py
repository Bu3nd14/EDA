#!/usr/bin/env python3
"""L69: la ritenuta (Q513 BC847, Q514 BC857) e i 5 V in una corsa con le sonde della ritenuta.

Le sonde (--sonde ...,Q513:1,Q513:2,Q513:3,Q514:2,Q514:3): la corrente ENTRANTE in ogni piedino
sondato. La base di Q514 non e' sondata: Ib514 = -(Ie514 + Ic514).

  P(t) di un transistor = somma sui piedini di V(piedino) x I(entrante): esatta, non dipende dal
       riferimento perche' le tre correnti sommano a zero.
       Q513: B at_bn, E rly_ret, C at_bp.   Q514: B at_bp, E vrelay_en (= AT_ON), C at_bn.
  p100_W la media piu' alta su 100 ms su TUTTA la corsa; pfin_W la media degli ultimi 50 ms
         (il metodo di calore_5v.py di L64c)
  tj     60 C d'aria + P x 403 K/W (Diodes DS11108, la piazzola minima, il dato di L68; per il BC857
         nello stesso SOT-23 lo stesso valore, dichiarato). Tj max 150 C.
  ie_max la corrente di emettitore di Q513 piu' alta (ICM 200 mA, impulso <= 1 ms)
  U504   la potenza e la Tj di calore_5v.py (62 K/W, Tj max 125 C)

Uso: /usr/bin/python3 -I calore_ritenuta.py <seq/etichetta> <out.csv> <caso> [...]   Solo stdlib.
"""
import csv
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
from calore_5v import leggi, media_max  # noqa: E402

RTH_Q, TJ_Q = 403.0, 150.0
RTH_U, TJ_U = 62.0, 125.0
T_AMB = 60.0


def ultimi(t, p, w=0.05):
    t0 = t[-1] - w
    k = [j for j in range(len(t)) if t[j] >= t0]
    area = sum(0.5 * (p[j] + p[j - 1]) * (t[j] - t[j - 1]) for j in k[1:])
    return area / (t[k[-1]] - t[k[0]])


def main(argv):
    seq, out, casi = argv[1], argv[2], argv[3:]
    righe = []
    for c in casi:
        d = os.path.join(seq, c)
        if not os.path.isfile(os.path.join(d, "ok.txt")):
            raise SystemExit("%s: manca ok.txt" % c)
        S = leggi(os.path.join(d, "tb_psu_seq_%s_g1_out.txt" % c))
        t = S["time"]
        bn, bp, on, ret = S["v(at_bn)"], S["v(at_bp)"], S["v(vrelay_en)"], S["v(rly_ret)"]
        ib3, ie3, ic3 = S["i(vsiq513_1)"], S["i(vsiq513_2)"], S["i(vsiq513_3)"]
        ie4, ic4 = S["i(vsiq514_2)"], S["i(vsiq514_3)"]
        ib4 = [-(a + b) for a, b in zip(ie4, ic4)]
        p3 = [bn[k] * ib3[k] + ret[k] * ie3[k] + bp[k] * ic3[k] for k in range(len(t))]
        p4 = [bp[k] * ib4[k] + on[k] * ie4[k] + bn[k] * ic4[k] for k in range(len(t))]
        pu = [abs(a) * max(b - c_, 0.0) for a, b, c_ in
              zip(S["i(vsiu504_3)"], S["v(vrelay_reg)"], S["v(v5_pre)"])]
        r = {"caso": c}
        for nome, p, rth in (("q513", p3, RTH_Q), ("q514", p4, RTH_Q), ("u504", pu, RTH_U)):
            a, b = media_max(t, p, 0.1), ultimi(t, p)
            r[nome + "_p100_W"] = "%.4f" % a
            r[nome + "_pfin_W"] = "%.4f" % b
            r[nome + "_tj_C"] = "%.1f" % (T_AMB + max(a, b) * rth)
        r["ie513_max_mA"] = "%.2f" % (1e3 * max(abs(x) for x in ie3))
        r["ie513_fin_mA"] = "%.2f" % (1e3 * abs(ie3[-1]))
        r["iu504_max_mA"] = "%.1f" % (1e3 * max(abs(x) for x in S["i(vsiu504_3)"]))
        r["v5_fin_V"] = "%.3f" % S["v(v5)"][-1] if False else "%.3f" % (S["v(v5)"][-1] - ret[-1])
        r["at_on_fin_V"] = "%.3f" % (on[-1] - ret[-1])
        r["vbe513_fin_V"] = "%.3f" % (bn[-1] - ret[-1])
        fuori = (float(r["q513_tj_C"]) > TJ_Q or float(r["q514_tj_C"]) > TJ_Q
                 or float(r["u504_tj_C"]) > TJ_U or float(r["ie513_max_mA"]) > 200.0)
        r["esito"] = "fuori" if fuori else "dentro"
        righe.append(r)
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(righe[0]))
        w.writeheader()
        w.writerows(righe)
    for r in righe:
        print(" ".join("%s=%s" % kv for kv in r.items()))


if __name__ == "__main__":
    main(sys.argv)
