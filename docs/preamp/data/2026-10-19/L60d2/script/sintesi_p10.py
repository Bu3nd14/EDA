#!/usr/bin/env python3
"""L60d2: la sintesi di P10 sulla Stax, da p10.csv (analizza_p10.py di L45b). Solo stdlib.
Copia di L60c2/script/sintesi_p10.py con i percorsi di L60d2 e, in piu', la colonna
L60c2_sopra_ms: la stessa corsa sul blocco senza la ridondanza (L60c2/p10_stax.csv); vuota per i
modi nuovi (R150..R153, R112 / R144 in corto). La colonna peggio_di_L60c2 segna chi sale di piu'
di 1 ms.

Uso: sintesi_p10.py        scrive p10_stax.csv e stampa la sintesi

Solo il jack della Stax (fix2): la colonna p10 di analizza_p10.py giudica i tre jack a 100 ms (P10 di
ADR-069 a vuoto), mentre qui conta la Stax col suo carico e il tetto di ADR-086, 150 ms (ADR-081 diceva 125: colonna fuori_125). Per ogni
guasto: il tempo sopra 0,87 V (sopra_ms), l'ultimo istante sopra (ultimo_ms) e se la corsa finisce
con la Stax ancora sopra (allora la durata e' un limite inferiore). Accanto, la durata a vuoto di
L45b (p10_blocco.csv, fix2_sopra_ms), col condensatore da 4,7 uF e senza carico.
"""
import csv
import os

QUI = os.path.dirname(os.path.abspath(__file__))
L60D2 = os.path.dirname(QUI)
DATA = os.path.abspath(os.path.join(L60D2, "..", ".."))
TETTO = 150.0      # ADR-086 (L60c2); era 125 ms (ADR-081): la colonna fuori_125 lo tiene
T_F = 0.3

l45b = {(r["posizione"], r["modo"]): r for r in
        csv.DictReader(open(os.path.join(DATA, "2026-10-13", "L45b", "p10_blocco.csv")))}
righe = []
l60c2 = {(r["posizione"], r["modo"], r["k_C"]): r for r in
         csv.DictReader(open(os.path.join(DATA, "2026-10-15", "L60c2", "p10_stax.csv")))}
for r in csv.DictReader(open(os.path.join(L60D2, "p10.csv"))):
    nome = r["modo"]
    k = "1.05" if nome.endswith("_k105") else "1"
    base = nome[:-5] if nome.endswith("_k105") else nome
    parti = base.split("_", 2)            # G0, A/F2/CTRL/pin, resto
    if parti[1] in ("A", "F2"):
        pos, modo = parti[1], parti[2]
    else:
        pos, modo = "-", base[3:]
    sopra = float(r["fix2_sopra_ms"])
    ultimo = float(r["fix2_ultimo_ms"]) if r["fix2_ultimo_ms"] else 0.0
    t_fine = float(r["t_fine"])
    ancora = sopra > 0 and ultimo >= (t_fine - T_F) * 1e3 - 1.0
    v = l45b.get((pos, modo))
    righe.append({"posizione": pos, "modo": modo, "k_C": k, "t_fine_s": "%.3f" % t_fine,
                  "stax_grezzo_V": r["fix2_grezzo_V"], "stax_sopra_ms": "%.1f" % sopra,
                  "stax_ultimo_ms": "%.1f" % ultimo,
                  "ancora_sopra_alla_fine": "si" if ancora else "",
                  "verdetto": "FUORI" if (sopra > TETTO or ancora) else "entro",
                  "fuori_125": "si" if (sopra > 125.0 or ancora) else "",
                  "L45b_vuoto_4u7_sopra_ms": v["fix2_sopra_ms"] if v else "",
                  "L60c2_sopra_ms": l60c2[(pos, modo, k)]["stax_sopra_ms"]
                  if (pos, modo, k) in l60c2 else "",
                  # una corsa di L60c2 ferma presto (CORSA CORTA) non e' un riferimento
                  "peggio_di_L60c2": "si" if (pos, modo, k) in l60c2
                  and l60c2[(pos, modo, k)]["stato"] == "ok" and sopra >
                  float(l60c2[(pos, modo, k)]["stax_sopra_ms"]) + 1.0 else "",
                  "stato": r["stato"]})
righe.sort(key=lambda x: -float(x["stax_sopra_ms"]))
with open(os.path.join(L60D2, "p10_stax.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(righe[0].keys()))
    w.writeheader()
    w.writerows(righe)

for k in ("1", "1.05"):
    sub = [x for x in righe if x["k_C"] == k]
    fuori = [x for x in sub if x["verdetto"] == "FUORI"]
    sopra0 = [x for x in sub if float(x["stax_sopra_ms"]) > 0]
    print("C x%s: %d corse, %d con la Stax sopra 0,87 V, %d fuori da %g ms; il peggiore %s %s %s ms"
          % (k, len(sub), len(sopra0), len(fuori), TETTO, sub[0]["posizione"], sub[0]["modo"],
             sub[0]["stax_sopra_ms"]))
print("stati:", sorted({x["stato"] for x in righe}))
print("i dieci peggiori:")
for x in righe[:10]:
    print("  %-3s %-14s C x%-4s %8s ms (ultimo %8s, fine %s s) %s  [L45b a vuoto: %s ms]"
          % (x["posizione"], x["modo"], x["k_C"], x["stax_sopra_ms"], x["stax_ultimo_ms"],
             x["t_fine_s"], x["verdetto"], x["L45b_vuoto_4u7_sopra_ms"]))
print("peggio di L60c2 (> 1 ms):")
for x in righe:
    if x["peggio_di_L60c2"]:
        print("  %-3s %-14s C x%-4s %8s ms, era %s" % (x["posizione"], x["modo"], x["k_C"],
                                                     x["stax_sopra_ms"], x["L60c2_sopra_ms"]))
