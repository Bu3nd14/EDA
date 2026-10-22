#!/usr/bin/env python3
"""L45d2b3b1: P7 con R153 in corto (run/p7_<v>/tb_mute_corto/, genera_p7.py). Solo stdlib,
/usr/bin/python3 -I. Casi di tb_mute_corto: 0 normale, 1 mute, 2 / 3 corto sulla fissa 1 / 2, 4 corto
sulla principale, 5 / 6 carico 10 / 100 ohm sulla fissa 1.

Prima i due casi noti:
  1. p7_oggi (il blocco di oggi, sano) contro p7/tb_cbe_nom_regime.csv e tb_cbe_nom_vbe.csv di
     L45d2b2c (la variante coi diodi di ADR-095 a +-15 V): cella per cella sulle colonne comuni;
  2. p7_l60d2_r153cc (il blocco di L60d2 con R153 a 1 ohm) contro p7_r153cc.txt di L60d2: Q146
     0,4112 W medi, 2,006 W di picco, entro 1e-3 relativo.
Poi il guasto, p7_r153cc: Q146 e Q148 (SOT-23: MMBT5401 / 5551, 403 C/W, P_D 0,31 W, Tj 150 C),
la Tj a 60 C d'aria, le giunzioni dei finali, i diodi, e ogni potenza media di P7 contro il
blocco sano.

Uso: sintesi_p7.py      stampa, e scrive p7_r153cc.txt
"""
import csv
import os
import sys

L = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.abspath(os.path.join(L, "..", ".."))
B2C = os.path.join(DATA, "2026-10-21", "L45d2b2c", "p7")
RTH = 403.0


def leggi(v, t):
    return list(csv.DictReader(open(os.path.join(L, "run", "p7_" + v, "tb_mute_corto", "tb_mute_corto_%s.csv" % t))))


def cella(r):
    return "%s/%sdB/%sHz/caso %s" % (r["blk"], r["modo_db"], r["f_hz"], r["caso"])


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


out = []
ok = True
# caso noto 1
for t in ("regime", "vbe"):
    a = leggi("oggi", t)
    b = list(csv.DictReader(open(os.path.join(B2C, "tb_cbe_nom_%s.csv" % t))))
    comuni = [c for c in a[0] if c in b[0]]
    celle = div = 0
    peggio = 0.0
    for ra, rb in zip(a, b):
        for c in comuni:
            x, y = num(ra[c]), num(rb[c])
            celle += 1
            if x is None or y is None:
                div += ra[c] != rb[c]
                continue
            d = abs(x - y) / max(abs(y), 1e-9)
            if d > 1e-3 and abs(x - y) > 1e-9:
                div += 1
                peggio = max(peggio, d)
    out.append("caso noto 1, %s: %d righe contro %d di L45d2b2c, %d celle, %d oltre 1e-3 (peggiore %.2g)"
               % (t, len(a), len(b), celle, div, peggio))
    ok = ok and div == 0 and len(a) == len(b)
# caso noto 2
r = leggi("l60d2_r153cc", "l56")
p = max(float(x["p_q146"]) for x in r)
x = max(float(x["pmax_q146"]) for x in r)
d2 = abs(p - 0.4112) / 0.4112 < 1e-3 and abs(x - 2.006) / 2.006 < 1e-3
out.append("caso noto 2, blocco di L60d2 con R153 a 1 ohm: Q146 %.4f W medi, %.4g W di picco (L60d2: 0,4112 / 2,006) %s"
           % (p, x, "uguale" if d2 else "DIVERSO"))
ok = ok and d2
# il guasto
VARIANTI = ("oggi", "r153cc") + (("r153_meta",) if os.path.isdir(os.path.join(L, "run", "p7_r153_meta")) else ())
for v in VARIANTI:
    rr = leggi(v, "l56")
    out.append("%s: %d righe di Q146 / Q148" % (v, len(rr)))
    for col, segno in (("p_q146", 1), ("pmax_q146", 1), ("icmin_q146", -1), ("p_q148", 1), ("pmax_q148", 1)):
        m = max(rr, key=lambda q: segno * float(q[col]))
        extra = ""
        if col in ("p_q146", "p_q148"):
            extra = "  Tj a 60 C %.0f C" % (60 + float(m[col]) * RTH)
        out.append("  %-11s %10.4g   %s%s" % (col, float(m[col]), cella(m), extra))
    vb = leggi(v, "vbe")
    for col in ("veb_q132_max", "vbe_q133_max", "id_d158_max", "id_d159_max", "p_d158", "p_d159"):
        m = max(vb, key=lambda q: float(q[col]))
        out.append("  %-13s %10.4g   %s" % (col, float(m[col]), cella(m)))
sano = leggi("oggi", "regime")
gu = leggi("r153cc", "regime")
out.append("P7, massimo di ogni potenza media: blocco sano / R153 in corto")
for c in sorted(k for k in sano[0] if k.startswith("p_")):
    a = max(float(q[c] or 0) for q in sano)
    rb = max(gu, key=lambda q: float(q[c] or 0))
    out.append("  %-10s %10.4g W  %10.4g W   %s" % (c, a, float(rb[c] or 0), cella(rb)))
print("\n".join(out))
open(os.path.join(L, "p7_r153cc.txt"), "w").write("\n".join(out) + "\n")
sys.exit(0 if ok else 1)
