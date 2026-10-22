#!/usr/bin/env python3
"""L45d2b3b1: la sintesi di P10 sulla Stax, dal p10_stax_grezzo.csv (analizza_p10.py di L45b sulle corse
di run/stax_g0 e run/stax_guasti). Solo stdlib, /usr/bin/python3 -I. Le regole sono quelle di
sintesi_p10.py di L60d2, riga per riga: il jack della Stax col suo carico, il tetto di ADR-086
(150 ms, colonna verdetto) e quello di ADR-081 (125 ms, colonna fuori_125); una corsa che finisce
con la Stax ancora sopra e' FUORI. Accanto, la stessa corsa di L60d2 (L60d2_sopra_ms, il blocco
prima di ADR-090 e ADR-095) e peggio_di_L60d2 se sale di piu' di 1 ms; vuota per i modi dei diodi.

Uso: sintesi_stax.py     scrive p10_stax.csv e stampa la sintesi
"""
import csv
import os

L = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.abspath(os.path.join(L, "..", ".."))
TETTO = 150.0
T_F = 0.3

l45b = {(r["posizione"], r["modo"]): r for r in
        csv.DictReader(open(os.path.join(DATA, "2026-10-13", "L45b", "p10_blocco.csv")))}
l60d2 = {(r["posizione"], r["modo"], r["k_C"]): r for r in
         csv.DictReader(open(os.path.join(DATA, "2026-10-19", "L60d2", "p10_stax.csv")))}
righe = []
for r in csv.DictReader(open(os.path.join(L, "p10_stax_grezzo.csv"))):
    nome = r["modo"]
    k = "1.05" if nome.endswith("_k105") else "1"
    base = nome[:-5] if nome.endswith("_k105") else nome
    parti = base.split("_", 2)
    if parti[1] in ("A", "F2"):
        pos, modo = parti[1], parti[2]
    else:
        pos, modo = "-", base[3:]
    sopra = float(r["fix2_sopra_ms"])
    ultimo = float(r["fix2_ultimo_ms"]) if r["fix2_ultimo_ms"] else 0.0
    t_fine = float(r["t_fine"])
    ancora = sopra > 0 and ultimo >= (t_fine - T_F) * 1e3 - 1.0
    v = l45b.get((pos, modo))
    d = l60d2.get((pos, modo, k))
    righe.append({"posizione": pos, "modo": modo, "k_C": k, "t_fine_s": "%.3f" % t_fine,
                  "stax_grezzo_V": r["fix2_grezzo_V"], "stax_sopra_ms": "%.1f" % sopra,
                  "stax_ultimo_ms": "%.1f" % ultimo,
                  "ancora_sopra_alla_fine": "si" if ancora else "",
                  "verdetto": "FUORI" if (sopra > TETTO or ancora) else "entro",
                  "fuori_125": "si" if (sopra > 125.0 or ancora) else "",
                  "L45b_vuoto_4u7_sopra_ms": v["fix2_sopra_ms"] if v else "",
                  "L60d2_sopra_ms": d["stax_sopra_ms"] if d else "",
                  "peggio_di_L60d2": "si" if d and d["stato"] == "ok"
                  and sopra > float(d["stax_sopra_ms"]) + 1.0 else "",
                  "stato": r["stato"]})
righe.sort(key=lambda x: -float(x["stax_sopra_ms"]))
with open(os.path.join(L, "p10_stax.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(righe[0].keys()))
    w.writeheader()
    w.writerows(righe)

for k in ("1", "1.05"):
    sub = [x for x in righe if x["k_C"] == k]
    fuori = [x for x in sub if x["verdetto"] == "FUORI"]
    f125 = [x for x in sub if x["fuori_125"]]
    sopra0 = [x for x in sub if float(x["stax_sopra_ms"]) > 0]
    print("C x%s: %d corse, %d con la Stax sopra 0,87 V, %d oltre 125 ms, %d fuori da %g ms; il peggiore %s %s %s ms"
          % (k, len(sub), len(sopra0), len(f125), len(fuori), TETTO, sub[0]["posizione"],
             sub[0]["modo"], sub[0]["stax_sopra_ms"]))
print("stati:", sorted({x["stato"] for x in righe}))
print("i dieci peggiori:")
for x in righe[:10]:
    print("  %-3s %-14s C x%-4s %8s ms (ultimo %8s, fine %s s) %s  [L60d2: %s ms]"
          % (x["posizione"], x["modo"], x["k_C"], x["stax_sopra_ms"], x["stax_ultimo_ms"],
             x["t_fine_s"], x["verdetto"], x["L60d2_sopra_ms"]))
print("peggio di L60d2 (> 1 ms):")
for x in righe:
    if x["peggio_di_L60d2"]:
        print("  %-3s %-14s C x%-4s %8s ms, era %s" % (x["posizione"], x["modo"], x["k_C"],
                                                     x["stax_sopra_ms"], x["L60d2_sopra_ms"]))
print("i modi dei diodi:")
for x in righe:
    if x["modo"][:4] in ("D154", "D155", "D156", "D157", "D158", "D159"):
        print("  %-3s %-8s C x%-4s %8s ms %s" % (x["posizione"], x["modo"], x["k_C"],
                                              x["stax_sopra_ms"], x["verdetto"]))
