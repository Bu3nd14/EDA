"""analizza_sonda.py - L47c2b1: per ogni variante della sonda, il manifesto delle sue celle (mev_*
e i loro riferimenti, presi dal manifesto della matrice), i .dat dei riferimenti collegati da
../matrice (corsi SENZA opzioni), e v2_metodo.py analizza. Poi il confronto di mev_lz_iii con la
matrice (la corsa che corre anche senza opzioni: quanto sposta ogni opzione).

    /usr/bin/python3 analizza_sonda.py
"""
import csv
import os
import subprocess
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
MATRICE = os.path.abspath(os.path.join(QUI, "..", "matrice_interruttore"))
REPO = os.path.abspath(os.path.join(QUI, *[".."] * 6))
V2 = os.path.join(REPO, "scripts", "v2_metodo.py")
CORSE = ("mev_1k_iii", "mev_20_iii", "mev_lz_iii")
VARIANTI = sys.argv[1:] or ["t1", "t1r", "gear"]

with open(os.path.join(MATRICE, "manifest_sel.csv")) as f:
    righe = list(csv.DictReader(f))
    campi = list(righe[0].keys())
per = {r["cella"]: r for r in righe}
sel = []
for c in CORSE:
    r = per[c]
    sel.append(r)
    for k in ("rif_ins", "rif_rel"):
        if r[k] not in ("", "-") and per[r[k]] not in sel:
            sel.append(per[r[k]])

for v in VARIANTI:
    d = os.path.join(QUI, v)
    fatte = {}
    for x in open(os.path.join(d, "tempi.txt")):
        p = x.split()
        fatte[p[0]] = p[1]
    ok = [c for c in CORSE if fatte.get(c) == "rc=0"]
    rows = []
    for r in sel:
        if r["cella"] in CORSE and r["cella"] not in ok:
            continue
        if r["cella"] not in CORSE:
            dst = os.path.join(d, r["file"])
            if not os.path.exists(dst):
                os.symlink(os.path.join(MATRICE, r["file"]), dst)
        rows.append(r)
    man = os.path.join(d, "manifest_sonda.csv")
    with open(man, "w", newline="") as f:
        w = csv.DictWriter(f, campi)
        w.writeheader()
        w.writerows(rows)
    print("%s: corse riuscite %s, fermate %s" % (v, ok, [c for c in CORSE if c not in ok]))
    subprocess.run([sys.executable, V2, "analizza", man, d, os.path.join(d, "analisi.csv")], check=True)

# quanto sposta ogni opzione: mev_lz_iii contro la matrice (la sua analisi, coi soli riferimenti
# che le servono, in rif_matrice/: la matrice intera non e' ancora analizzata)
RM = os.path.join(QUI, "rif_matrice")
os.makedirs(RM, exist_ok=True)
rows = [r for r in sel if r["cella"] == "mev_lz_iii"]
rows += [per[r[k]] for r in list(rows) for k in ("rif_ins", "rif_rel")]
with open(os.path.join(RM, "manifest.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, campi)
    w.writeheader()
    w.writerows(rows)
subprocess.run([sys.executable, V2, "analizza", os.path.join(RM, "manifest.csv"), MATRICE,
                os.path.join(RM, "analisi.csv")], check=True)
with open(os.path.join(RM, "analisi.csv")) as f:
    M = {(a["cella"], a["grandezza"], a["uscita"]): a for a in csv.DictReader(f) if a["cella"] == "mev_lz_iii"}
for v in VARIANTI:
    p = os.path.join(QUI, v, "analisi.csv")
    with open(p) as f:
        S = {(a["cella"], a["grandezza"], a["uscita"]): a for a in csv.DictReader(f) if a["cella"] == "mev_lz_iii"}
    for k in sorted(set(M) & set(S)):
        a, b = M[k]["picco_V"], S[k]["picco_V"]
        if a and b:
            print("%-5s %-6s %-9s matrice %.4g V, %s %.4g V, scarto %.3g V" % (
                v, k[1], k[2], float(a), v, float(b), float(b) - float(a)))
