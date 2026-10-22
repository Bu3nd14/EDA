#!/usr/bin/env python3
"""L45d2b3b1: i guasti piu' lunghi sulla Stax, il blocco dopo ADR-097 (p10_stax_lunghi.csv) contro
quello di prima (p10_stax.csv, con le tre corse rifatte in gear di p10_stax_gear.csv). Il «Da riaprire
se» di ADR-089: nessuno oltre 150 ms. Solo stdlib, /usr/bin/python3 -I. Scrive stax_lunghi.csv.
"""
import csv
import os

L = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T_F = 0.3


def chiave(nome):
    k = "1.05" if nome.endswith("_k105") else "1"
    base = nome[:-5] if nome.endswith("_k105") else nome
    _, pos, modo = base.split("_", 2)
    return pos, modo, k


prima = {(r["posizione"], r["modo"], r["k_C"]): float(r["stax_sopra_ms"])
         for r in csv.DictReader(open(os.path.join(L, "p10_stax.csv")))}
for r in csv.DictReader(open(os.path.join(L, "p10_stax_gear.csv"))):
    prima[chiave(r["modo"])] = float(r["fix2_sopra_ms"])
out = []
dopo = {r["modo"]: r for r in csv.DictReader(open(os.path.join(L, "p10_stax_lunghi.csv")))}
# una corsa fermata subito dopo il guasto e rifatta in gear (rifai_gear.py --da stax_lunghi) prende il
# posto della prima
gl = os.path.join(L, "p10_stax_lunghi_gear.csv")
if os.path.exists(gl):
    for r in csv.DictReader(open(gl)):
        dopo[r["modo"]] = r
for r in dopo.values():
    c = chiave(r["modo"])
    s, u, tf = float(r["fix2_sopra_ms"]), float(r["fix2_ultimo_ms"] or 0), float(r["t_fine"])
    ancora = s > 0 and u >= (tf - T_F) * 1e3 - 1.0
    out.append({"posizione": c[0], "modo": c[1], "k_C": c[2], "prima_ms": "%.1f" % prima[c],
                "dopo_ms": "%.1f" % s, "scarto_ms": "%.1f" % (s - prima[c]),
                "verdetto": "FUORI" if s > 150 or ancora else "entro", "stato": r["stato"]})
out.sort(key=lambda x: -float(x["dopo_ms"]))
with open(os.path.join(L, "stax_lunghi.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0]))
    w.writeheader()
    w.writerows(out)
sc = [abs(float(x["scarto_ms"])) for x in out]
print("%d casi; fuori da 150 ms: %d; oltre 125 ms: %d; scarto |dopo - prima| al piu' %.1f ms; stati %s"
      % (len(out), sum(x["verdetto"] == "FUORI" for x in out),
         sum(float(x["dopo_ms"]) > 125 for x in out), max(sc), sorted({x["stato"] for x in out})))
for x in out[:8]:
    print("  %-3s %-12s C x%-4s %7s ms (prima %7s) %s" % (x["posizione"], x["modo"], x["k_C"],
                                                         x["dopo_ms"], x["prima_ms"], x["verdetto"]))
