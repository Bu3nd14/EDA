#!/usr/bin/env python3
"""L45a: la tabella della FMEA del blocco (fmea_blocco.csv e fmea_blocco.md). Solo stdlib.

Uso: tabella_finale.py   (legge le sintesi accanto, scrive fmea_blocco.csv e fmea_blocco.md)

Una riga per modo di guasto. Per ogni posizione del canale il picco di PR-23 (filtrato, evento -
riferimento) sul jack che quella posizione raggiunge:
  B  -> jack principale         (a 0 dB; a +10 dB a parte)
  F2 -> jack della Stax         F1 -> jack del Singxer
  A  -> il peggiore dei tre (le fisse in continua, la principale attraverso C_T e il blocco B)
Le rifatture sostituiscono la corsa originale (corta_A, gear_A, gear_F2, r120_B). Il corto di R120
nelle posizioni senza transitorio (A, F1, F2, B a +10 dB) si da' dal punto di lavoro: l'uscita del
blocco a -1,47 V e' un gradino di almeno 1,47 V sul jack, ed e' scritto «dal punto di lavoro».
"""
import csv
import math
import os

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)

NOMI = {
    "C104": "condensatore del riferimento (100 uF)", "C105": "condensatore del riferimento (100 nF)",
    "C116": "condensatore del riferimento dei cascode", "C124": "condensatore di Miller",
    "C137": "condensatore di retroazione", "C139": "disaccoppiamento + (100 nF)",
    "C140": "disaccoppiamento - (100 nF)", "C141": "disaccoppiamento + (100 uF)",
    "C142": "disaccoppiamento - (100 uF)", "C145": "condensatore della cella RC (1000 uF)",
    "D102": "diodo del riferimento (alto)", "D103": "diodo del riferimento (basso)",
    "JQ110A": "JFET d'ingresso, lato segnale", "JQ110B": "JFET d'ingresso, lato retroazione",
    "Q106": "generatore di coda", "Q117": "cascode, lato segnale", "Q118": "cascode, lato retroazione",
    "Q121A": "specchio, lato a diodo", "Q121B": "specchio, lato d'uscita",
    "Q122": "VAS (DZT5401)", "Q125": "carico del VAS (DZT5551)", "Q127": "moltiplicatore di Vbe",
    "Q132": "finale NPN (MJE15032)", "Q133": "finale PNP (MJE15033)",
    "Q146": "inseguitore davanti al VAS", "Q148": "transistor di aiuto dello specchio",
    "R101": "resistenza del riferimento", "R107": "emettitore della coda",
    "R108": "stopper di gate, lato segnale", "R109": "stopper di gate, lato retroazione",
    "R111": "degenerazione, lato segnale", "R112": "degenerazione, lato retroazione",
    "R113": "resistenza d'ingresso (R_IN / R_G)", "R114": "riferimento dei cascode (alto)",
    "R115": "riferimento dei cascode (basso)", "R119": "emettitore dello specchio, lato a diodo",
    "R120": "emettitore dello specchio, lato d'uscita", "R123": "emettitore del VAS (56)",
    "R126": "emettitore del carico del VAS (56)", "R128": "moltiplicatore di Vbe (alto)",
    "R129": "moltiplicatore di Vbe (basso)", "R130": "stopper di base del finale NPN",
    "R131": "stopper di base del finale PNP", "R134": "emettitore del finale NPN (22)",
    "R135": "emettitore del finale PNP (22)", "R136": "resistenza di retroazione",
    "R138": "ramo di guadagno +3 dB", "R143": "ramo di guadagno +10 dB",
    "R144": "resistenza della cella RC (10)", "R147": "resistenza dell'inseguitore",
    "R149": "resistenza dell'aiuto",
}
MODI = {"ce": "corto C-E", "be": "corto B-E", "ae": "aperto", "ds": "corto D-S", "gs": "corto G-S",
        "as": "aperto", "cc": "corto", "ap": "aperto"}
POS = (("A", "A"), ("F1", "F1"), ("F2", "F2"), ("B", "B"), ("B_g10", "B_g10"))
SOSTITUTE = {("corta_A", "A"), ("gear_A", "A"), ("gear_F2", "F2"), ("r120_B", "B")}
JACK = {"A": None, "F1": "fix1", "F2": "fix2", "B": "main", "B_g10": "main"}


def leggi(nome):
    p = os.path.join(L, nome)
    return list(csv.DictReader(open(p))) if os.path.exists(p) else []


def db_main(v):
    return 96 + 20 * math.log10(max(v, 1e-12) * 21.1 / 2.83)


def main():
    tab = {}
    for f, pos in POS:
        for r in leggi("sintesi_%s.csv" % f):
            tab[(r["modo"], pos)] = r
    for r in leggi("sintesi_rifatte.csv"):
        for var, pos in SOSTITUTE:
            if r["posizione"] == var:
                tab[(r["modo"], pos)] = dict(r, nota="rifatta (%s)" % var)
    modi = sorted({m for m, _ in tab if m != "rif"}, key=lambda m: (m[0] != "Q" and m[0] != "J", m))
    righe = []
    for m in modi:
        parte, sig = m.rsplit("_", 1)
        riga = {"modo": m, "parte": NOMI.get(parte, parte), "guasto": MODI[sig]}
        calore, note = [], []
        for _, pos in POS:
            r = tab.get((m, pos))
            if r is None or r["verdetto"] == "?":
                if parte == "R120" and sig == "cc":
                    riga[pos + "_V"] = ">=1.47"
                    riga[pos + "_esito"] = "SOPRA IL TETTO"
                    note.append("%s dal punto di lavoro" % pos)
                else:
                    riga[pos + "_V"] = "-"
                    riga[pos + "_esito"] = "-"
                continue
            j = JACK[pos] or r["jack_peggiore"]
            riga[pos + "_V"] = r.get(j + "_A_V", "")
            riga[pos + "_esito"] = r["verdetto"]
            if pos == "B":
                riga["classe_B"] = r["classe"]
            if pos == "A":
                riga["classe_A"] = r["classe"]
            if r.get("calore"):
                calore.append(r["calore"])
            if r.get("stato") not in ("ok", None, ""):
                note.append("%s: %s" % (pos, r["stato"]))
        riga["calore"] = calore[0] if calore else ""
        riga["note"] = "; ".join(note)
        righe.append(riga)
    campi = ["modo", "parte", "guasto", "classe_A", "classe_B"] + \
        [p + s for _, p in POS for s in ("_V", "_esito")] + ["calore", "note"]
    with open(os.path.join(L, "fmea_blocco.csv"), "w", newline="") as fo:
        w = csv.DictWriter(fo, fieldnames=campi, extrasaction="ignore")
        w.writeheader()
        for r in righe:
            w.writerow(r)

    def cella(r, pos):
        v = r.get(pos + "_V", "-")
        e = r.get(pos + "_esito", "-")
        if v in ("-", ""):
            return "-"
        if v.startswith(">="):
            return "**≥ 1,47 V**"
        x = float(v)
        s = ("%.3g V" % x) if x >= 0.01 else ("%.2g mV" % (x * 1e3))
        s = s.replace(".", ",")
        return "**%s**" % s if e == "SOPRA IL TETTO" else s

    with open(os.path.join(L, "fmea_blocco.md"), "w") as fo:
        fo.write("| Parte | Guasto | Blocco A (peggiore dei tre jack) | Buffer Singxer | Buffer Stax "
                 "| Blocco B, 0 dB | Blocco B, +10 dB | Dopo (calore) |\n|---|---|---|---|---|---|---|---|\n")
        for r in righe:
            fo.write("| %s | %s | %s | %s | %s | %s | %s | %s |\n" % (
                r["parte"], r["guasto"], cella(r, "A"), cella(r, "F1"), cella(r, "F2"),
                cella(r, "B"), cella(r, "B_g10"), r["calore"].replace(".", ",")))
    conti = {}
    for r in righe:
        for _, pos in POS:
            k = (pos, r.get(pos + "_esito"))
            conti[k] = conti.get(k, 0) + 1
    for k in sorted(conti):
        print("%-6s %-18s %d" % (k[0], k[1], conti[k]))


if __name__ == "__main__":
    main()
