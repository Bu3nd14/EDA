#!/usr/bin/env python3
"""L57a: la sintesi delle strade - per variante e rete, il caso peggiore in classe II contro i limiti.

Legge i rca_spl.csv di rca/oggi (senza rimedio, rete nominale), rca/strade (le protezioni, rete
nominale) e rca/reti (le stesse a rete -10 % e +10 %); con costo/costo.csv accanto.

Limiti: LSK489 gate-gate +/-30 V, gate-drain e gate-source 60 V, IG(F) 10 mA (datasheet p. 2);
il 1N4148 (stand-in dei diodi) 200 mA continui; il tetto di 112,2 dB SPL (0,87 V, PR-23).
Al jack principale: «cima» = volume in cima, «k11» = la posizione d'ascolto del K11 (-29 dB);
0 e +10 dB. Le fisse in dB sopra il picco del K11 a piena scala (3,8 V).

Uso: /usr/bin/python3 sintesi.py  -> sintesi.csv (e la stampa)
"""
import csv
import os
import re

QUI = os.path.dirname(os.path.abspath(__file__))
L57A = os.path.dirname(QUI)
RCA = os.path.join(L57A, "rca")
cartelle = [("senza", "1.0", os.path.join(RCA, "oggi", "out_senza"))]
for d in sorted(os.listdir(os.path.join(RCA, "strade"))):
    if d.startswith("out_"):
        cartelle.append((d[4:], "1.0", os.path.join(RCA, "strade", d)))
for d in sorted(os.listdir(os.path.join(RCA, "reti"))):
    m = re.match(r"out_(.+)_rete(09|11)$", d)
    if m:
        cartelle.append((m.group(1), "0.9" if m.group(2) == "09" else "1.1", os.path.join(RCA, "reti", d)))
# il mute inserito durante il gesto (genera.py --mute) e la variante di AN-015, alle tre reti
for sotto in ("mute", "an015"):
    for d in sorted(os.listdir(os.path.join(RCA, sotto))):
        m = re.match(r"out_(.+)_rete(09|10|11)$", d)
        if m:
            cartelle.append((m.group(1), {"09": "0.9", "10": "1.0", "11": "1.1"}[m.group(2)],
                             os.path.join(RCA, sotto, d)))

costo = {}
p = os.path.join(L57A, "costo", "costo.csv")
if os.path.exists(p):
    for r in csv.DictReader(open(p)):
        c = costo.setdefault(r["variante"], {})
        c["%s_%s" % (r["freq"], r["livello"])] = r["thd_pct"]
        c["e5"] = r["e5_stima_uv"]

out = []
for var, rete, d in cartelle:
    f = os.path.join(d, "rca_spl.csv")
    if not os.path.exists(f):
        continue
    righe = [r for r in csv.DictReader(open(f)) if r["caso"].startswith("classeII")]
    def jack(vol, modo):
        x = [r for r in righe if r["vol"] == vol and r["modo"] == modo]
        return max(float(r["main_dbspl"]) for r in x), any(r["clip_finale"] == "si" for r in x)
    k0, k0c = jack("k11", "0")
    k10, k10c = jack("k11", "10")
    c0, c0c = jack("cima", "0")
    gg = max(float(r["gg_v"]) for r in righe)
    gd = min(float(r["gd_min_v"]) for r in righe)
    ig = max(float(r["ig_max_ma"]) for r in righe)
    idm = max(float(r["id_max_ma"]) for r in righe)
    ain = max(float(r["ain_pk_v"]) for r in righe)
    fisse = max(float(r["fisse_vs_k11_db"]) for r in righe)
    c = costo.get(var, {})
    out.append({"variante": var, "rete": rete, "ain_pk_v": "%.1f" % ain,
                "gg_v": "%.2f" % gg, "gg_margine_v": "%.2f" % (30 - gg),
                "gd_v": "%.1f" % gd, "gd_margine_v": "%.1f" % (60 + gd),
                "ig_ma": "%.3g" % ig, "id_ma": "%.3g" % idm,
                "k11_0db_dbspl": "%.1f%s" % (k0, " clip" if k0c else ""),
                "k11_10db_dbspl": "%.1f%s" % (k10, " clip" if k10c else ""),
                "cima_0db_dbspl": "%.1f%s" % (c0, " clip" if c0c else ""),
                "fisse_sul_k11_db": "%+.1f" % fisse,
                "thd20k_02v_pct": c.get("20000_lo", ""), "thd20k_2v_pct": c.get("20000_hi", ""),
                "thd20k_e6_pct": c.get("20000_e6", ""), "e5_stima_uv": c.get("e5", "")})
ordine = {"senza": 0}
out.sort(key=lambda r: (ordine.get(r["variante"], 1), r["variante"], r["rete"]))
with open(os.path.join(L57A, "sintesi.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, list(out[0]))
    w.writeheader()
    w.writerows(out)
for r in out:
    print("%(variante)-10s rete %(rete)s ain %(ain_pk_v)5s gg %(gg_v)6s (marg %(gg_margine_v)6s) gd %(gd_v)6s (marg %(gd_margine_v)5s)"
          " ig %(ig_ma)6s id %(id_ma)6s | k11 %(k11_0db_dbspl)-11s +10 %(k11_10db_dbspl)-11s cima %(cima_0db_dbspl)-11s fisse %(fisse_sul_k11_db)s"
          " | thd %(thd20k_02v_pct)s/%(thd20k_2v_pct)s/%(thd20k_e6_pct)s E5 %(e5_stima_uv)s" % r)
