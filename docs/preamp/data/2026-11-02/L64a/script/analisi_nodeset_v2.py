#!/usr/bin/env python3
"""L64a: le cifre di V2 di tre celle con e senza i .nodeset del blocco (prova_nodeset_v2.sh).

    /usr/bin/python3 -I analisi_nodeset_v2.py

Le onde coi nodeset coincidono con quelle senza fino all'evento (< 1 uV su 12 V), poi lo scatto
del contatto si sposta di un passo: un confronto delle onde non dice se il verdetto cambia. Qui
l'analisi di V2 (analizza_par.py di L29c, 2 processi) sulle tre celle, una volta coi .dat senza
nodeset e una coi .dat con, gli stessi riferimenti (corsi senza) in tutte e due; scrive
../prova_nodeset/{senza,con}/analisi.csv e ../prova_nodeset/analisi_confronto.csv (cella,
grandezza, uscita, picco senza, picco con, scarto).
"""
import csv
import os
import subprocess
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
RUN = os.path.join(L, "run", "v2")
P = os.path.join(L, "prova_nodeset")
ROOT = os.path.abspath(os.path.join(L, "..", "..", "..", "..", ".."))
AN = os.path.join(ROOT, "docs", "preamp", "data", "2026-09-23", "L29c", "script", "analizza_par.py")
CELLE = ("mh01_lz_iii", "mh01_20_iii", "g10sempre_20_r10k_iii")
RIF = ("g10sempre_20_iii", "g10mai_20_iii", "g10sempre_lz_iii", "g10mai_lz_iii")

man = list(csv.reader(open(os.path.join(RUN, "manifest.csv"))))
sel = [man[0]] + [r for r in man[1:] if r[0] in CELLE + RIF]
for caso in ("senza", "con"):
    d = os.path.join(P, caso)
    os.makedirs(d, exist_ok=True)
    for r in RIF:
        for suf in ("", "_stati"):
            dst = os.path.join(d, r + suf + ".dat")
            if not os.path.exists(dst):
                os.symlink(os.path.join(RUN, r + suf + ".dat"), dst)
    for c in CELLE:
        for suf in ("", "_stati"):
            src = (os.path.join(P, f"{c}{suf}_senza.dat") if caso == "senza"
                   else os.path.join(RUN, f"{c}{suf}_nb.dat"))
            dst = os.path.join(d, c + suf + ".dat")
            if not os.path.exists(dst):
                os.symlink(src, dst)
    with open(os.path.join(d, "manifest_sel.csv"), "w", newline="") as f:
        csv.writer(f).writerows(sel)
    rc = subprocess.run(["nice", "-n", "15", "/usr/bin/python3", AN,
                         os.path.join(d, "manifest_sel.csv"), d,
                         os.path.join(d, "analisi.csv"), "2"]).returncode
    if rc:
        sys.exit(f"analizza_par.py esce {rc} su {caso}")

def leggi(caso):
    return {(r["cella"], r["grandezza"], r["uscita"]): float(r["picco_V"])
            for r in csv.DictReader(open(os.path.join(P, caso, "analisi.csv")))}

a, b = leggi("senza"), leggi("con")
righe = []
for k in sorted(set(a) | set(b)):
    x, y = a.get(k), b.get(k)
    righe.append(list(k) + ["%.6g" % x if x is not None else "", "%.6g" % y if y is not None else "",
                            "%.3g" % abs(y - x) if None not in (x, y) else "manca"])
with open(os.path.join(P, "analisi_confronto.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["cella", "grandezza", "uscita", "picco_senza_V", "picco_con_V", "scarto_V"])
    w.writerows(righe)
for r in righe:
    print(*r)
