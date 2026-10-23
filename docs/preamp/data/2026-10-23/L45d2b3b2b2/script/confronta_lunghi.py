#!/usr/bin/env python3
"""L45d2b3b2b2: i guasti piu' lunghi sulla Stax, il blocco del sorgente (p10_stax_lunghi.csv, QUI) contro
il blocco dopo ADR-097 (p10_stax_lunghi.csv di L45d2b3b1, con la corsa rifatta in gear di
p10_stax_lunghi_gear.csv). Le regole di confronta_lunghi.py di L45d2b3b1: FUORI oltre 150 ms o se la
Stax e' ancora sopra a fine corsa. Solo stdlib, /usr/bin/python3 -I. Scrive stax_lunghi.csv.
"""
import csv
import os

L = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B1 = os.path.join(os.path.dirname(os.path.dirname(L)), "2026-10-22", "L45d2b3b1")
T_F = 0.3


def carica(d):
    out = {r["modo"]: r for r in csv.DictReader(open(os.path.join(d, "p10_stax_lunghi.csv")))}
    g = os.path.join(d, "p10_stax_lunghi_gear.csv")
    if os.path.exists(g):
        for r in csv.DictReader(open(g)):
            out[r["modo"]] = r
    return out


prima, dopo = carica(B1), carica(L)
assert set(prima) == set(dopo), sorted(set(prima) ^ set(dopo))[:5]
out = []
for nome, r in dopo.items():
    s, u, tf = float(r["fix2_sopra_ms"]), float(r["fix2_ultimo_ms"] or 0), float(r["t_fine"])
    ancora = s > 0 and u >= (tf - T_F) * 1e3 - 1.0
    p = float(prima[nome]["fix2_sopra_ms"])
    out.append({"caso": nome, "adr097_ms": "%.1f" % p, "sorgente_ms": "%.1f" % s, "scarto_ms": "%.1f" % (s - p),
                "verdetto": "FUORI" if s > 150 or ancora else "entro", "stato": r["stato"]})
out.sort(key=lambda x: -float(x["sorgente_ms"]))
with open(os.path.join(L, "stax_lunghi.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0]))
    w.writeheader()
    w.writerows(out)
sc = sorted(out, key=lambda x: -abs(float(x["scarto_ms"])))
print("%d casi; fuori da 150 ms: %d; oltre 125 ms: %d; scarto al piu' %s ms (%s); stati %s"
      % (len(out), sum(x["verdetto"] == "FUORI" for x in out), sum(float(x["sorgente_ms"]) > 125 for x in out),
         sc[0]["scarto_ms"], sc[0]["caso"], sorted({x["stato"] for x in out})))
for x in out[:8]:
    print("  %-26s %7s ms (ADR-097 %7s) %s" % (x["caso"], x["sorgente_ms"], x["adr097_ms"], x["verdetto"]))
su = [x for x in out if float(x["scarto_ms"]) > 1.0]
giu = [x for x in out if float(x["scarto_ms"]) < -1.0]
print("spostati di piu' di 1 ms: %d piu' lunghi, %d piu' corti; gli altri %d entro 1 ms; il piu' lungo che "
      "si allunga: %s" % (len(su), len(giu), len(out) - len(su) - len(giu),
                         max((float(x["scarto_ms"]), x["caso"]) for x in out)))
for x in sorted(giu, key=lambda x: float(x["scarto_ms"])):
    print("  piu' corto: %-26s %7s -> %7s ms" % (x["caso"], x["adr097_ms"], x["sorgente_ms"]))
print("i cinque scarti piu' grandi:")
for x in sc[:5]:
    print("  %-26s %7s ms (ADR-097 %7s) scarto %s" % (x["caso"], x["sorgente_ms"], x["adr097_ms"], x["scarto_ms"]))
