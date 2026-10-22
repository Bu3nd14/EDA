#!/usr/bin/env python3
"""L45d2b3b2b1: P7 (tb_mute_corto, ADR-021: Tj <= 125 C a 60 C d'aria) sul blocco del sorgente, contro
la variante rv2 (deve coincidere) e il blocco di main (oggi) di L45d2b3b2a. Solo stdlib,
/usr/bin/python3 -I.

Uso: p7.py      scrive p7_sorgente.csv e stampa

Il metodo e le R_thJA sono quelli di p7_confronto.py di L45d2b3b2a (che si importa), con Q193 al posto
di Q168 (MMBT5401 in SOT-23, 403 K/W). I finali due volte: senza dissipatore (62,5 K/W, la cifra di
ieri) e col WA-T220-101E di ADR-099 (2,5 giunzione-case + 2 interfaccia, ipotesi + 20 dissipatore-aria
a 1 W dalla curva Ohmite = 24,5 K/W).
"""
import csv
import os
import re
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
A = os.path.join(os.path.dirname(L), "L45d2b3b2a")
sys.path.insert(0, os.path.join(A, "script"))
import p7_confronto as pc   # noqa: E402

pc.RTH["q193"] = 403
RTH_HS = 2.5 + 2.0 + 20.0
MAPPA = {"q168": "q193", "r161": "r190", "r162": "r191", "r167": "r192", "r169": "r194"}


def massimi(cartella, v):
    vecchio = pc.L
    pc.L = cartella
    try:
        m = pc.massimi(v)
    finally:
        pc.L = vecchio
    out = {}
    for k, x in m.items():
        for a, b in MAPPA.items():
            k = re.sub(r"_%s$" % a, "_" + b, k)
        out[k] = x
    return out


dopo = massimi(L, "dopo")
rv2 = massimi(A, "rv2")
oggi = massimi(A, "oggi")
righe = []
fmt = "  %-10s %10s  rv2 %10s  oggi %10s  %-18s %-5s %s"
print(fmt % ("colonna", "max_W", "", "", "giudizio", "", "dove"))
for k in sorted(dopo):
    p, dove = dopo[k]
    g, fuori = pc.giudica(k, p)
    hs = ""
    if k in ("p_q132", "p_q133"):
        hs = "col dissipatore Tj %.0f C" % (pc.TA + p * RTH_HS)
    r = {"colonna": k, "max_W": "%.5g" % p, "rv2_max_W": "%.5g" % rv2.get(k, (float("nan"),))[0],
         "oggi_max_W": "%.5g" % oggi.get(k, (float("nan"),))[0], "giudizio": g,
         "fuori": "FUORI" if fuori else "", "dissipatore": hs, "dove": dove}
    righe.append(r)
    print(fmt % (k, r["max_W"], r["rv2_max_W"], r["oggi_max_W"], g + ("  " + hs if hs else ""),
                 r["fuori"], dove))
uguali = sum(1 for r in righe if r["max_W"] == r["rv2_max_W"])
print("uguali a rv2 (5 cifre): %d su %d; fuori: %d" % (uguali, len(righe), sum(bool(r["fuori"]) for r in righe)))
with open(os.path.join(L, "p7_sorgente.csv"), "w", newline="") as fo:
    w = csv.DictWriter(fo, fieldnames=list(righe[0]))
    w.writeheader()
    w.writerows(righe)
