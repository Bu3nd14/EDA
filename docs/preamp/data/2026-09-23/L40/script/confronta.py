#!/usr/bin/env python3
# L40: copiato da L39/script senza modifiche al codice. Qui prima/ e' il main di
# L39 (C124 470 p, modelli del costruttore), dopo/ e' L40 (C124 1 nF, ADR-042).
"""L39: il confronto grezzo, cifra per cifra, fra prima/ (segnaposto) e dopo/
(modelli del costruttore). Per ogni deck legge dal log di run_simulation.sh ogni
riga `nome = valore` (print, meas) e dalle tabelle echo .csv ogni cella numerica,
e scrive confronto_grezzo.csv: deck, sorgente, chiave, prima, dopo, delta,
delta relativo. Una chiave ripetuta nello stesso file prende un indice (#2, #3...)
nell'ordine in cui compare, cosi' due corse dello stesso deck restano distinte.

Non giudica: le soglie e i verdetti stanno nella tabella del report, che cita
queste righe. Una chiave presente da una parte sola si scrive con la cella vuota
dall'altra, e si conta: e' il sintomo di un deck che ha smesso di misurare (#26).

Uso: /usr/bin/python3 confronta.py
"""
import csv
import glob
import os
import re

QUI = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(QUI)
NUM = r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?"
RIGA = re.compile(r"^\s*([A-Za-z@_][\w@\[\]().:,#/-]*)\s*=\s*(" + NUM + r")\b")


def dal_log(path):
    out, visti = {}, {}
    for ln in open(path, errors="replace"):
        m = RIGA.match(ln)
        if not m:
            continue
        k = m.group(1).lower()
        visti[k] = visti.get(k, 0) + 1
        if visti[k] > 1:
            k = "%s#%d" % (k, visti[k])
        out[k] = float(m.group(2))
    return out


def dai_csv(path):
    out = {}
    try:
        righe = list(csv.reader(open(path, errors="replace")))
    except csv.Error:
        return out
    if len(righe) < 2:
        return out
    testa = [h.strip() for h in righe[0]]
    # Una forma d'onda (wrdata convertito) ha per prima colonna un numero: non e'
    # una tabella di cifre, e le sue righe non si abbinano fra due corse.
    if any(r and re.fullmatch(NUM, r[0].strip()) for r in righe[1:]) \
            or re.fullmatch(NUM, testa[0] or "0"):
        return out
    for i, r in enumerate(righe[1:], 1):
        chiave_riga = r[0].strip() if r else str(i)
        for h, v in zip(testa[1:], r[1:]):
            v = v.strip()
            if re.fullmatch(NUM, v):
                out["%s|%s" % (chiave_riga, h)] = float(v)
    return out


def raccogli(fase, deck):
    d = os.path.join(BASE, fase, deck)
    tab = {}
    for f in sorted(glob.glob(os.path.join(d, "*.log"))):
        tab.update({("log", k): v for k, v in dal_log(f).items()})
    for f in sorted(glob.glob(os.path.join(d, "*.csv"))):
        b = os.path.basename(f)
        if b == deck + ".csv":          # il wrdata convertito: forme d'onda, non cifre
            continue
        tab.update({(b, k): v for k, v in dai_csv(f).items()})
    return tab


def main():
    decks = sorted(os.path.basename(p) for p in glob.glob(os.path.join(BASE, "prima", "tb_*"))
                   if os.path.isdir(p))
    righe, orfane = [], 0
    for deck in decks:
        a, b = raccogli("prima", deck), raccogli("dopo", deck)
        for key in sorted(set(a) | set(b)):
            pa, pb = a.get(key), b.get(key)
            if pa is None or pb is None:
                orfane += 1
            delta = (pb - pa) if (pa is not None and pb is not None) else None
            rel = (delta / abs(pa)) if (delta is not None and pa) else None
            righe.append([deck, key[0], key[1],
                          "" if pa is None else "%.7g" % pa,
                          "" if pb is None else "%.7g" % pb,
                          "" if delta is None else "%.4g" % delta,
                          "" if rel is None else "%.4g" % rel])
    with open(os.path.join(BASE, "confronto_grezzo.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["deck", "sorgente", "chiave", "prima", "dopo", "delta", "delta_rel"])
        w.writerows(righe)
    print("%d deck, %d cifre, %d presenti da una parte sola -> confronto_grezzo.csv"
          % (len(decks), len(righe), orfane))


if __name__ == "__main__":
    main()
