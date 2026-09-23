#!/usr/bin/env python3
"""L29c: il verdetto di V2 da analisi.csv (v2_metodo.py analizza) e dal manifesto generato, che
dice per ogni riga quali grandezze sono VERDETTO (colonna conta) e a che punto del mandato
appartiene (colonna gruppo). Soglie: A e B2 <= 100 uV di picco, S <= 20 dB in 100 ms (ADR-032,
ADR-040). Una A con finestra corta non accetta (v2_metodo). Tutto il resto e' diagnostica.

Scrive verdetto.csv (una riga per cella x grandezza di verdetto, il peggiore sulle tre uscite)
e stampa il peggiore per gruppo e grandezza.

Uso: verdetto.py manifest.csv analisi.csv verdetto.csv
"""
import csv
import sys

man, ana, out = sys.argv[1:4]
SOGLIA = {"A_ins": 100e-6, "A_rel": 100e-6, "B2": 100e-6, "S_ins": 20.0, "S_rel": 20.0}
with open(man) as f:
    M = {r["cella"]: r for r in csv.DictReader(f)}
with open(ana) as f:
    AN = list(csv.DictReader(f))
peg = {}
mancanti = []
for c, r in M.items():
    for g in [x for x in r.get("conta", "").split(";") if x]:
        vals = [a for a in AN if a["cella"] == c and a["grandezza"] == g]
        if len(vals) != 3:
            mancanti.append("%s %s (%d uscite)" % (c, g, len(vals)))
            continue
        w = max(vals, key=lambda a: float(a["picco_V"]) if a["picco_V"] else float("inf"))
        esiti = {a["esito"] for a in vals}
        v = float(w["picco_V"]) if w["picco_V"] else None
        ok = (v is not None and v <= SOGLIA[g] and not any("non accetta" in e for e in esiti))
        peg[(c, g)] = dict(cella=c, gruppo=r["gruppo"], variante=r["variante"], gm=r["gm"],
                           f_hz=r["f_hz"], amp=r["amp"], rl=r["rl"], grandezza=g, uscita=w["uscita"],
                           picco=w["picco_V"], t_picco=w["t_picco_s"], soglia=SOGLIA[g],
                           esito="regge" if ok else "NON REGGE", esiti="|".join(sorted(esiti)))
with open(out, "w", newline="") as f:
    campi = ["cella", "gruppo", "variante", "gm", "f_hz", "amp", "rl", "grandezza", "uscita",
             "picco", "t_picco", "soglia", "esito", "esiti"]
    w = csv.DictWriter(f, campi)
    w.writeheader()
    w.writerows(peg.values())
print("%d verdetti -> %s" % (len(peg), out))
if mancanti:
    print("MANCANTI (%d): %s" % (len(mancanti), "; ".join(mancanti)))
per = {}
for p in peg.values():
    k = (p["gruppo"], p["grandezza"], "musica" if float(p["amp"]) > 0 else "senza segnale")
    if k not in per or float(p["picco"] or "inf") > float(per[k]["picco"] or "inf"):
        per[k] = p
for k in sorted(per):
    p = per[k]
    unita = "dB" if p["grandezza"].startswith("S") else "uV"
    v = float(p["picco"]) * (1 if unita == "dB" else 1e6)
    print("gruppo %s %-5s %-13s peggiore %8.3f %s  %-9s %s (%s, %s Hz, %s)" % (
        k[0], k[1], k[2], v, unita, p["esito"], p["cella"], p["uscita"], p["f_hz"], p["gm"]))
nr = [p for p in peg.values() if p["esito"] != "regge"]
print("NON REGGE: %d su %d" % (len(nr), len(peg)))
for p in nr:
    print("   %s %s %s %s %s" % (p["cella"], p["grandezza"], p["uscita"], p["picco"], p["esiti"]))
