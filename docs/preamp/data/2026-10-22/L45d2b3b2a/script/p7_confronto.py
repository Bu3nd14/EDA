#!/usr/bin/env python3
"""L45d2b3b2a: P7 (tb_mute_corto, ADR-021: Tj <= 125 C a 60 C d'aria) per variante, contro la base
di oggi. Solo stdlib, /usr/bin/python3 -I.

Uso: p7_confronto.py <variante> [...]     scrive p7_<v>.csv e stampa

Legge regressione/<v>/tb_mute_corto/tb_mute_corto_regime.csv (le colonne del deck) e
tb_mute_corto_parti.csv (prepara_regressione.py: Q146, Q148, R123, R126 e le parti nuove). Per ogni
colonna di potenza media, il massimo su tutti i casi e i quattro blocchi; per i transistor la Tj a
60 C d'aria con le R_thJA del banco del calore (analizza_tr.py di L45a, analizza_L62b.py; le due
meta' di Q121 insieme a 233 K/W, i due JFET insieme a 250 K/W). Le resistenze 0207 contro 0,25 W,
le 22 ohm contro 0,34 W. Il log dei deck non si usa: il contatore delle righe ripetute si sfasa.
"""
import csv
import os
import sys

L = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RTH = {"q106": 417, "q117": 417, "q118": 417, "q125": 125, "q127": 125, "q122": 125, "q146": 403,
       "q148": 403, "q132": 62.5, "q133": 62.5, "q168": 403}
TA = 60.0


def leggi(v, f):
    p = os.path.join(L, "regressione", v, "tb_mute_corto", f)
    return list(csv.DictReader(open(p))) if os.path.isfile(p) else []


def massimi(v):
    out = {}
    for f in ("tb_mute_corto_regime.csv", "tb_mute_corto_parti.csv"):
        for r in leggi(v, f):
            for k, x in r.items():
                if k.startswith("p_") and k not in ("p_rail", "p_rsep", "p_rsep2"):
                    try:
                        y = abs(float(x))
                    except ValueError:
                        continue
                    if y > out.get(k, (0, ""))[0]:
                        out[k] = (y, "%s %s dB %s Hz caso %s" % (r["blk"], r["modo_db"], r["f_hz"], r["caso"]))
    q121 = max((abs(float(a["p_q121a"])) + abs(float(a["p_q121b"])), a["blk"])
               for a in leggi(v, "tb_mute_corto_regime.csv"))
    jf = max((abs(float(a["p_jq110a"])) + abs(float(a["p_jq110b"])), a["blk"])
             for a in leggi(v, "tb_mute_corto_regime.csv"))
    out["p_q121"] = (q121[0], q121[1])
    out["p_jq110"] = (jf[0], jf[1])
    return out


def giudica(k, p):
    n = k[2:]
    if n in RTH:
        return "Tj %.0f C" % (TA + p * RTH[n]), TA + p * RTH[n] > 125
    if n == "q121":
        return "Tj %.0f C" % (TA + p * 233), TA + p * 233 > 125
    if n == "jq110":
        return "Tj %.0f C" % (TA + p * 250), TA + p * 250 > 125
    if n[0] == "r":
        lim = 0.34 if n in ("r134", "r135") else 0.25
        return "%.3f W / %.2f" % (p, lim), p > lim
    return "", False


if __name__ == "__main__":
    base = massimi("oggi")
    for v in sys.argv[1:]:
        m = massimi(v)
        righe = []
        print("== P7 %s (contro oggi)" % v)
        for k in sorted(m):
            p, dove = m[k]
            g, fuori = giudica(k, p)
            b = base.get(k, (float("nan"), ""))[0]
            righe.append({"variante": v, "colonna": k, "max_W": "%.5g" % p, "oggi_max_W": "%.5g" % b,
                          "giudizio": g, "fuori": "FUORI" if fuori else "", "dove": dove})
            print("  %-10s %10.5g  oggi %10.5g  %-18s %s %s" % (k, p, b, g, "FUORI" if fuori else "", dove))
        with open(os.path.join(L, "p7_%s.csv" % v), "w", newline="") as fo:
            w = csv.DictWriter(fo, fieldnames=list(righe[0]))
            w.writeheader()
            w.writerows(righe)
