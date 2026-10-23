#!/usr/bin/env python3
"""L45d2b3b2b2: il banco del calore sul blocco del sorgente (variante sorg, QUI) contro la variante rv2
di L45d2b3b2a, con la mappa delle sigle (limitations #22):

    banco rv2   R161  R162  R167  Q168  R169
    sorgente    R190  R191  R192  Q193  R194

- IL CALORE (calore_*.csv: potenze, Tj, correnti dei rail, oltre i limiti; sintesi_*.csv: Tj e
  verdetti) cella per cella, tolleranza 1e-3 relativa. Le colonne P_r161_W / P_r162_W sono una lista
  fissa di analizza_calore.py (le parti del limitatore di L62b): su rv2 sono le due parti nuove del
  banco, sul sorgente non esistono e restano vuote; si mettono da parte (le potenze delle parti nuove
  sono in nuove_max.py). «diodo_max» fra D102 e D103 alla stessa potenza (sono in serie) non conta.
- IL JACK (analisi_jack_*.csv, sintesi main_*): l'ordine delle righe del subckt cambia l'arrotondamento
  del transitorio (L45d2b3b2b1, P7), e sotto il nV il residuo del primo passo cambia di ordini di
  grandezza. Si confronta ciascuna grandezza dove ha un senso: i livelli in dB SPL sopra 0 dB SPL,
  le ampiezze sopra 1 uV, i tempi del massimo dove il massimo e' sopra 1 mV. Il resto si conta e si
  dichiara. Solo stdlib, /usr/bin/python3 -I.

Uso: confronta_rv2.py [variante=sorg] [base=rv2]   esce 1 se il calore diverge
"""
import csv
import os
import sys

L = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(os.path.dirname(os.path.dirname(L)), "2026-10-22", "L45d2b3b2a")
V = sys.argv[1] if len(sys.argv) > 1 else "sorg"
B = sys.argv[2] if len(sys.argv) > 2 else "rv2"
MAPPA = {"R161": "R190", "R162": "R191", "R167": "R192", "Q168": "Q193", "R169": "R194"}
MAPPA.update({k.lower(): v.lower() for k, v in MAPPA.items()})
A_PARTE = ("P_r161_W", "P_r162_W")
REL, ASS = 1e-3, 1e-6
JACK_SPL = {"main_dB_SPL": "main", "main_dB_SPL_grezzo": "main", "stax_dB_SPL": "fix2"}


def rimappa(s):
    for k, n in MAPPA.items():
        s = s.replace(k, n)
    return s


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def uguali(a, b):
    x, y = num(a), num(b)
    if x is None or y is None:
        return a == b
    return abs(x - y) <= max(ASS, REL * max(abs(x), abs(y)))


def carica(nome, chiave):
    qui = {chiave(r): r for r in csv.DictReader(open(os.path.join(L, nome % V)))}
    banco = {}
    for r in csv.DictReader(open(os.path.join(A, nome % B))):
        r = {c: rimappa(x) for c, x in r.items()}
        banco[chiave(r)] = r
    if set(qui) != set(banco):
        sys.exit("RIFIUTATO: %s righe diverse: %s" % (nome % "", sorted(set(qui) ^ set(banco))[:6]))
    return qui, banco


# il calore
celle = diverse = 0
for nome, chiave in (("calore_%s.csv", lambda r: (r["posizione"], r["modo"])),
                     ("sintesi_%s.csv", lambda r: (r["modo"],))):
    qui, banco = carica(nome, chiave)
    for k in sorted(qui):
        for c, x in qui[k].items():
            if c == "variante" or c in A_PARTE or c not in banco[k] or c.startswith("main_") or c.startswith("fix1_"):
                continue
            if c == "diodo_max" and uguali(qui[k]["P_diodo_max_W"], banco[k]["P_diodo_max_W"]):
                continue
            celle += 1
            if not uguali(x, banco[k][c]):
                diverse += 1
                print("CALORE DIVERSA %s %s %s: %s %r, %s %r" % (nome % "", k, c, B, banco[k][c], V, x))
print("il calore: %d celle, %d diverse oltre %g relativa (messe da parte: %s)" % (celle, diverse, REL, ", ".join(A_PARTE)))

# il jack
qui, banco = carica("analisi_jack_%s.csv", lambda r: (r["variante"].split("_", 1)[1], r["modo"]))
conf = {"dB SPL sopra 0": [0, 0.0, ""], "ampiezza sopra 1 uV": [0, 0.0, ""], "tempo, massimo sopra 1 mV": [0, 0.0, ""]}
fuori = 0
for k in sorted(qui):
    q, b = qui[k], banco[k]
    for c in q:
        x, y = num(q[c]), num(b.get(c))
        if x is None or y is None or c == "t_fine":
            continue
        if c in JACK_SPL:
            if min(x, y) < 0:
                fuori += 1
                continue
            g, d = "dB SPL sopra 0", abs(x - y)
        elif c.endswith("_A_t_ms"):
            a = c[:-len("_t_ms")] + "_V"
            if min(abs(num(q[a]) or 0), abs(num(b[a]) or 0)) < 1e-3:
                fuori += 1
                continue
            g, d = "tempo, massimo sopra 1 mV", abs(x - y)
        elif c.endswith("_V"):
            if min(abs(x), abs(y)) < 1e-6:
                fuori += 1
                continue
            g, d = "ampiezza sopra 1 uV", abs(x - y) / max(abs(x), abs(y))
        else:
            continue
        conf[g][0] += 1
        if d > conf[g][1]:
            conf[g][1], conf[g][2] = d, "%s %s %s (%s %s, %s %s)" % (k[0], k[1], c, B, b[c], V, q[c])
for g, (n, d, dove) in conf.items():
    print("il jack, %s: %d celle, scarto massimo %s: %s" % (
        g, n, ("%.2g relativo" % d) if g.startswith("ampiezza") else ("%.1f" % d), dove))
print("il jack, sotto le soglie (residuo numerico, non confrontato): %d celle" % fuori)
sys.exit(1 if diverse else 0)
