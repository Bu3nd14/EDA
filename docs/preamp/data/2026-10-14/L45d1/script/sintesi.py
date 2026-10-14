#!/usr/bin/env python3
"""L45d1: the four FMEA tables of NC-042 in one, in the form of ADR-070, ordered by priority - the
input of L45d2 (the user's choices on the remedies). Solo stdlib.

    sintesi.py <data/2026-10-14/L45d1> <data/2026-10-14/L45c2>

Reads fmea_blocco_adr070.csv (L45a), fmea_controlli_adr070.csv (L45b), fmea_rail_adr070.csv
(L45c1) and L45c2's fmea_comando.csv as published. Writes fmea_sintesi.csv (every classified row,
the common columns) and fmea_sintesi.md: the count by priority and lot, the rows grouped by
candidate remedy (how many, which priorities, which lots), then the high and medium rows. Rows with
no priority (references, cross-references to another lot) are left out and counted.
"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import motore  # noqa: E402

D, C2 = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
num = motore.num


def leggi(p):
    return list(csv.DictReader(open(p)))


def mx(*xs):
    v = [num(x) for x in xs if num(x) is not None]
    return max(v) if v else None


FONTI = [
    ("L45a", os.path.join(D, "fmea_blocco_adr070.csv"),
     lambda r: (num(r["picco_V"]), num(r["sopra_max_ms"]))),
    ("L45b", os.path.join(D, "fmea_controlli_adr070.csv"),
     lambda r: (num(r["picco_V"]), num(r["sopra_max_ms"]))),
    ("L45c1", os.path.join(D, "fmea_rail_adr070.csv"),
     lambda r: (mx(r["A_main_V"], r["A_fisse_V"]), mx(r["sopra_main_ms"], r["sopra_fisse_ms"]))),
    ("L45c2", os.path.join(C2, "fmea_comando.csv"),
     lambda r: (mx(r["A_main_V"], r["A_fisse_V"]), num(r["sopra_ms"]))),
]
righe, fuori_classe = [], {}
for lotto, p, eff in FONTI:
    for r in leggi(p):
        if not r.get("priorita"):
            fuori_classe[lotto] = fuori_classe.get(lotto, 0) + 1
            continue
        v, t = eff(r)
        righe.append(dict(
            lotto=lotto, ref=r["ref"], funzione=r.get("funzione", ""), modo=r["modo"],
            verdetto=r.get("verdetto", ""), G=int(r["G"]), fit_modo=r["fit_modo"], P=int(r["P"]),
            R=int(r["R"]), priorita=r["priorita"], picco_V="" if v is None else "%.3g" % v,
            picco_dB="" if not v else "%.1f" % motore.db(v), sopra_ms="" if t is None else "%g" % t,
            rimedi=r["rimedi"], nota=r.get("nota", "")))
righe.sort(key=motore.chiave_ordine)

CAMPI = ["lotto", "ref", "funzione", "modo", "verdetto", "G", "fit_modo", "P", "R", "priorita",
         "picco_V", "picco_dB", "sopra_ms", "rimedi", "nota"]
with open(os.path.join(D, "fmea_sintesi.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=CAMPI)
    w.writeheader()
    for r in righe:
        w.writerow(r)

LOTTI = [x[0] for x in FONTI]
PR = ["alta", "media", "bassa"]
conto = {(l, p): 0 for l in LOTTI for p in PR}
for r in righe:
    conto[(r["lotto"], r["priorita"])] += 1
gruppi = {}
for r in righe:
    g = gruppi.setdefault(r["rimedi"], {"alta": 0, "media": 0, "bassa": 0, "lotti": set(), "G": 0})
    g[r["priorita"]] += 1
    g["lotti"].add(r["lotto"])
    g["G"] = max(g["G"], r["G"])


def cella(s):
    return str(s).replace("|", "/").replace("\n", " ")


with open(os.path.join(D, "fmea_sintesi.md"), "w") as f:
    f.write("# NC-042 — le quattro tabelle dei guasti nella forma di ADR-070, in una (L45d1)\n\n")
    f.write("Generata da `script/sintesi.py` da `fmea_blocco_adr070.csv` (L45a), "
            "`fmea_controlli_adr070.csv` (L45b), `fmea_rail_adr070.csv` (L45c1) e "
            "`data/2026-10-14/L45c2/fmea_comando.csv`. Tutte le righe classificate sono in "
            "`fmea_sintesi.csv`; qui il conteggio, i rimedi candidati e le righe ad alta e media "
            "priorita'. Il picco e' il filtrato al jack peggiore (V e dB SPL di picco a 1 m); «sopra» "
            "e' il tempo sopra 0,87 V a vuoto, il criterio di P10.\n\n")
    f.write("## Quante righe, per priorita' e per lotto\n\n")
    f.write("| Lotto | alta | media | bassa | senza classe (riferimenti, rimandi) |\n|---|---|---|---|---|\n")
    for l in LOTTI:
        f.write("| %s | %d | %d | %d | %d |\n" % (l, conto[(l, "alta")], conto[(l, "media")],
                                                 conto[(l, "bassa")], fuori_classe.get(l, 0)))
    f.write("| **tutte** | **%d** | **%d** | **%d** | %d |\n\n" % tuple(
        [sum(conto[(l, p)] for l in LOTTI) for p in PR] + [sum(fuori_classe.values())]))
    f.write("## Le righe raggruppate per rimedio candidato\n\n")
    f.write("Ordinate per righe ad alta priorita', poi media. Un rimedio scritto in due lotti con parole "
            "diverse resta in due gruppi.\n\n")
    f.write("| Rimedio candidato | alta | media | bassa | gravita' massima | lotti |\n|---|---|---|---|---|---|\n")
    for testo, g in sorted(gruppi.items(), key=lambda x: (-x[1]["alta"], -x[1]["media"], -x[1]["bassa"])):
        f.write("| %s | %d | %d | %d | %d | %s |\n" % (cella(testo), g["alta"], g["media"], g["bassa"],
                                                       g["G"], ", ".join(l for l in LOTTI if l in g["lotti"])))
    MD = ["lotto", "ref", "funzione", "modo", "verdetto", "G", "fit_modo", "P", "R", "picco_V",
          "picco_dB", "sopra_ms", "nota"]
    T = dict(motore.TITOLI, picco_V="picco (V)", picco_dB="dB SPL", sopra_ms="sopra 0,87 V (ms)")
    for p in ("alta", "media"):
        f.write("\n## Priorita' %s\n\n" % p)
        f.write("| " + " | ".join(T.get(k, k) for k in MD) + " |\n|" + "---|" * len(MD) + "\n")
        for r in righe:
            if r["priorita"] == p:
                f.write("| " + " | ".join(cella(r[k]) for k in MD) + " |\n")

print("fmea_sintesi.csv / .md: %d righe classificate (%s), %d senza classe" % (
    len(righe), ", ".join("%s %d" % (p, sum(conto[(l, p)] for l in LOTTI)) for p in PR),
    sum(fuori_classe.values())))
for l in LOTTI:
    print("  %-6s alta %3d  media %3d  bassa %3d  senza classe %d" % (
        l, conto[(l, "alta")], conto[(l, "media")], conto[(l, "bassa")], fuori_classe.get(l, 0)))
