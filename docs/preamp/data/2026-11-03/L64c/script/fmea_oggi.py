#!/usr/bin/env python3
"""L64c: la FMEA del progetto di oggi, con le misure adottate, composta dai quattro CSV versionati
(le colonne di ADR-070, quelle di fmea_dopo.csv di L45d2b3b3).

Uso: /usr/bin/python3 -I fmea_oggi.py   -> fmea_oggi.csv e fmea_oggi_conti.csv qui accanto (L64c/)

Le fonti, dalla piu' vecchia; una riga di un lotto piu' recente prende il posto di quella con la
stessa chiave (ref, modo, caso):
  L45d2b3b3  data/2026-10-24/L45d2b3b3/fmea_dopo.csv     539 righe, la FMEA dopo i rimedi
  L58a2      data/2026-10-29/L58a/fmea_alimentatore.csv   R585 e i BAS416 (righe nuove)
  L58b       data/2026-11-01/L58b/fmea_l58b.csv           l'autodiagnosi, ADR-110 (46 al posto di
                                                          righe di L45d2b3b3, 5 di L58a2, 9 nuove)
  L66        data/2026-11-02/L66/fmea_l66.csv             il blocco dopo ADR-111 (tutte al posto
                                                          di righe che c'erano)
Rifiuta (exit 1) se: una chiave si ripete dentro un file; L66 porta una riga nuova (L66 rifa' righe,
non ne aggiunge); una riga non ha fonte o stato; la priorita' dopo non e' quella della matrice di
ADR-070 dai G / P / R dopo della riga (priorita() di L58b/script/fmea_l58b.py, scritta di nuovo qui).
Aggiunge la colonna `da`, il lotto della riga che vale oggi.
Solo stdlib.
"""
import collections
import csv
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
DATA = os.path.abspath(os.path.join(L, "..", ".."))
FONTI = (("L45d2b3b3", os.path.join(DATA, "2026-10-24", "L45d2b3b3", "fmea_dopo.csv")),
         ("L58a2", os.path.join(DATA, "2026-10-29", "L58a", "fmea_alimentatore.csv")),
         ("L58b", os.path.join(DATA, "2026-11-01", "L58b", "fmea_l58b.csv")),
         ("L66", os.path.join(DATA, "2026-11-02", "L66", "fmea_l66.csv")))


def priorita(g, p, r):
    """La matrice di ADR-070."""
    if g == 5:
        return "alta"
    if r == 3:
        return {4: "alta", 3: "media"}.get(g, "bassa")
    if g == 4:
        return "media" if p == 1 else "alta"
    if g == 3:
        return "media" if p >= 3 else "bassa"
    return "bassa"


def main():
    errori = []
    oggi = {}
    ordine = []
    colonne = None
    for lotto, path in FONTI:
        with open(path, newline="", encoding="utf-8") as f:
            rd = csv.DictReader(f)
            if colonne is None:
                colonne = rd.fieldnames
            elif rd.fieldnames != colonne:
                errori.append(f"{lotto}: le colonne non sono quelle di L45d2b3b3")
            righe = list(rd)
        visti = set()
        for r in righe:
            k = (r["ref"], r["modo"], r["caso"])
            if k in visti:
                errori.append(f"{lotto}: la chiave {k} si ripete")
            visti.add(k)
            if lotto == "L66" and k not in oggi:
                errori.append(f"L66: {k} e' una riga nuova")
            if k not in oggi:
                ordine.append(k)
            oggi[k] = dict(r, da=lotto)
    conti = collections.Counter()
    for k in ordine:
        r = oggi[k]
        # lo stato sempre; la fonte vuota vuol dire che il «dopo» e' la riga di L45 (colonna lotto),
        # e si puo' solo in L45d2b3b3. Nessuna riga e' ancora «alla diagnosi»: L58 e' chiuso.
        if not r["stato"].strip():
            errori.append(f"{k} ({r['da']}): senza stato")
        if not r["fonte_dopo"].strip() and r["da"] != "L45d2b3b3":
            errori.append(f"{k} ({r['da']}): senza fonte")
        if r["stato"].startswith("alla diagnosi"):
            errori.append(f"{k} ({r['da']}): ancora «{r['stato']}», ma la diagnosi (L58) e' chiusa")
        if r["priorita_dopo"] != "esclusa":
            try:
                g, p, rr = int(r["G_dopo"]), int(r["P_dopo"]), int(r["R_dopo"])
            except ValueError:
                errori.append(f"{k} ({r['da']}): G / P / R dopo non numerici "
                              f"({r['G_dopo']!r}, {r['P_dopo']!r}, {r['R_dopo']!r})")
            else:
                if priorita(g, p, rr) != r["priorita_dopo"]:
                    errori.append(f"{k} ({r['da']}): priorita' {r['priorita_dopo']}, la matrice "
                                  f"di ADR-070 da' {priorita(g, p, rr)} (G {g}, P {p}, R {rr})")
        conti[(r["da"], r["priorita_dopo"])] += 1
    if errori:
        for e in errori:
            print("RIFIUTO:", e)
        return 1
    with open(os.path.join(L, "fmea_oggi.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=colonne + ["da"], lineterminator="\n")
        w.writeheader()
        for k in ordine:
            w.writerow(oggi[k])
    with open(os.path.join(L, "fmea_oggi_conti.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(("da", "priorita_dopo", "righe"))
        for (da, pr), n in sorted(conti.items()):
            w.writerow((da, pr, n))
    tot = collections.Counter(oggi[k]["priorita_dopo"] for k in ordine)
    print(f"righe {len(ordine)}: " + ", ".join(f"{p} {tot[p]}" for p in ("alta", "media", "bassa", "esclusa")))
    print("per lotto:", dict(collections.Counter(oggi[k]["da"] for k in ordine)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
