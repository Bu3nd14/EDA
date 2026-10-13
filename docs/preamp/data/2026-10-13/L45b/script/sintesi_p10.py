#!/usr/bin/env python3
"""L45b: i guasti del blocco di L45a contro P10 (ADR-069), a vuoto. Solo stdlib.

Legge analisi_vuoto_<pos>.csv (e le corse rifatte: accorciate, gear, R120) e la sintesi di L45a
(sintesi_<pos>.csv: la classe, il verdetto contro il tetto filtrato coi carichi), e scrive:
  p10_blocco.csv   un modo per riga e posizione: classe, verdetto di L45a, a vuoto il gradino
                   grezzo, il picco filtrato e il tempo sopra 0,87 V di ogni jack, il verdetto P10
  p10_blocco.md    il riassunto per posizione e i casi in cui i due criteri non sono d'accordo
"""
import csv
import os
import statistics

QUI = os.path.dirname(os.path.abspath(__file__))
L45B = os.path.dirname(QUI)
L45A = os.path.join(os.path.dirname(L45B), "L45a")
POS = ("A", "F1", "F2", "B", "B_g10")
JACK = (("main", "principale"), ("fix1", "Singxer"), ("fix2", "Stax"))


def leggi(p):
    return list(csv.DictReader(open(p))) if os.path.exists(p) else []


def pos_di(variante):
    v = variante.replace("vuoto_tr_", "")
    for pre in ("corta_", "gear_", "r120_"):
        if v.startswith(pre):
            return v[len(pre):]
    return v


def main():
    dati = {p: {r["modo"]: r for r in leggi(os.path.join(L45B, "analisi_vuoto_%s.csv" % p))} for p in POS}
    rifatte = leggi(os.path.join(L45B, "analisi_vuoto_rifatte.csv"))
    for r in rifatte:
        p = pos_di(r["variante"])
        # r120_B (fino a 0,32 s) solo se la corsa accorciata (0,6 s) non c'e'
        if r["variante"].startswith("vuoto_tr_r120") and r["modo"] in dati[p] and \
                dati[p][r["modo"]]["variante"].startswith("vuoto_tr_corta"):
            continue
        dati[p][r["modo"]] = r
    righe, md = [], []
    md.append("# L45b — i guasti del blocco di L45a contro P10, a vuoto\n")
    md.append("Generato da `script/sintesi_p10.py`. **P10** (ADR-069): tempo sopra 0,87 V sul jack "
              "senza filtro, a vuoto, dal guasto; ≤ 100 ms su ogni uscita. Le corse finiscono a 2,3 s "
              "(0,6 s le accorciate): un jack ancora sopra alla fine dà una durata «≥». Le fisse a vuoto "
              "decadono con τ 1,1 s: il blocco al rail le tiene sopra 0,87 V **3,15 s** "
              "(`analisi_lunghe.csv`, fino a 6 s), il principale **1,47 s**.\n")
    md.append("| Posizione | Modi | P10 fuori | di cui ancora sopra alla fine | L45a sopra il tetto | "
              "P10 fuori e L45a no | L45a sopra e P10 no | Principale: tempo sopra (mediana / max) |")
    md.append("|---|---|---|---|---|---|---|---|")
    disaccordi = []
    for p in POS:
        sint = {r["modo"]: r for r in leggi(os.path.join(L45A, "sintesi_%s.csv" % p))}
        n = fuori = ancora = l45a_sopra = solo_p10 = solo_l45a = 0
        t_main = []
        for modo in sorted(dati[p]):
            if modo == "rif":
                continue
            r = dati[p][modo]
            s = sint.get(modo, {})
            n += 1
            p10 = r.get("p10", "?")
            f = p10.startswith("FUORI")
            a = s.get("verdetto", "") == "SOPRA IL TETTO"
            fuori += f
            ancora += "ancora" in p10
            l45a_sopra += a
            if f and not a:
                solo_p10 += 1
                disaccordi.append((p, modo, "P10 fuori, L45a no", r, s))
            if a and not f:
                solo_l45a += 1
                disaccordi.append((p, modo, "L45a sopra, P10 no", r, s))
            if float(r.get("main_sopra_ms") or 0) > 0:
                t_main.append(float(r["main_sopra_ms"]))
            riga = {"posizione": p, "modo": modo, "classe_L45a": s.get("classe", ""),
                    "verdetto_L45a": s.get("verdetto", ""), "variante": r["variante"],
                    "t_fine": r.get("t_fine", "")}
            for j, _ in JACK:
                riga[j + "_grezzo_V"] = r.get(j + "_grezzo_V", "")
                riga[j + "_A_V"] = r.get(j + "_A_V", "")
                riga[j + "_sopra_ms"] = r.get(j + "_sopra_ms", "")
            riga["p10"] = p10
            riga["stato"] = r.get("stato", "")
            righe.append(riga)
        tm = ("%.0f / %.0f ms" % (statistics.median(t_main), max(t_main))) if t_main else "—"
        md.append("| %s | %d | **%d** | %d | %d | %d | %d | %s |" % (
            p, n, fuori, ancora, l45a_sopra, solo_p10, solo_l45a, tm))
    md.append("\n## I casi in cui i due criteri non sono d'accordo\n")
    md.append("| Posizione | Modo | Classe (L45a) | Disaccordo | Principale grezzo / sopra | Singxer | "
              "Stax | Stato |")
    md.append("|---|---|---|---|---|---|---|---|")
    for p, modo, cosa, r, s in disaccordi:
        md.append("| %s | %s | %s | %s | %s V / %s ms | %s V / %s ms | %s V / %s ms | %s |" % (
            p, modo, s.get("classe", ""), cosa, r.get("main_grezzo_V"), r.get("main_sopra_ms"),
            r.get("fix1_grezzo_V"), r.get("fix1_sopra_ms"), r.get("fix2_grezzo_V"),
            r.get("fix2_sopra_ms"), r.get("stato")))
    with open(os.path.join(L45B, "p10_blocco.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(righe[0]))
        w.writeheader()
        w.writerows(righe)
    with open(os.path.join(L45B, "p10_blocco.md"), "w") as f:
        f.write("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
