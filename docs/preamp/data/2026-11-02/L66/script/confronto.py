#!/usr/bin/env python3
"""L66: i modi fuori dai quindici sul blocco del sorgente contro la riga della FMEA (fmea_dopo.csv di
L45d2b3b3, che per questi modi porta il calore del blocco di prima di ADR-097 / ADR-099). Solo stdlib,
/usr/bin/python3 -I.

Uso: confronto.py   -> confronto.csv (un modo per riga)

Per ogni modo: la Tj massima a 60 C d'aria sulle sue posizioni e la parte (calore_sorg.csv di qui), la
continua d'uscita del blocco (out_avg, la piu' lontana da 0), il picco grezzo alla principale e il dB SPL
(analisi_jack_sorg.csv); contro Tj_max_C, picco_dopo_dB, stax_ms e la fonte della riga della FMEA.
  oltre_P7   : Tj > 125 C (sul sorgente)
  cambiato   : |Tj - Tj della FMEA| > 3 C, o l'uscita del blocco oltre 1 V dove la FMEA non dava colpo
  da_stax    : uscita del blocco oltre 1 V sulla fissa 2 (F2): il tempo sulla Stax va misurato (P10)
"""
import csv
import os

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
DATA = os.path.abspath(os.path.join(L, "..", ".."))
FMEA = os.path.join(DATA, "2026-10-24", "L45d2b3b3", "fmea_dopo.csv")


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def main():
    import importlib.util
    spec = importlib.util.spec_from_file_location("genera_l66", os.path.join(QUI, "genera.py"))
    g = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(g)
    g.prepara()
    _, _, fuori = g.divisione()
    fuori = fuori + list(g.LENTI)

    cal = {}
    for r in csv.DictReader(open(os.path.join(L, "calore_sorg.csv"))):
        cal.setdefault(r["modo"], []).append(r)
    jack = {}
    for r in csv.DictReader(open(os.path.join(L, "analisi_jack_sorg.csv"))):
        jack.setdefault(r["modo"], []).append(r)
    fm = {}
    for r in csv.DictReader(open(FMEA)):
        # le righe del blocco: le tabelle di L45 e le parti nuove del blocco (R150..R153, R160, i diodi)
        if r["caso"] and (r["gruppo"] == "tabelle di L45" or
                          (r["gruppo"] == "parti nuove" and r["lotto"] == "blocco")):
            fm.setdefault(r["caso"], r)

    righe = []
    for m in fuori:
        c = cal.get(m, [])
        j = jack.get(m, [])
        tj = [(num(r["Tj_max_60"]), r["Tj_max_disp_60"], r["posizione"]) for r in c
              if num(r["Tj_max_60"]) is not None]
        tmax = max(tj) if tj else (None, "", "")
        fine = all(r["fine"] == "si" for r in c) and len(c) > 0
        outs = [(abs(num(r["out_avg"]) or 0), num(r["out_avg"]), r["variante"].split("_", 1)[1])
                for r in j if num(r["out_avg"]) is not None]
        omax = max(outs) if outs else (0, None, "")
        dbs = [num(r["main_dB_SPL"]) for r in j if num(r["main_dB_SPL"]) is not None]
        f2 = [abs(num(r["out_avg"]) or 0) for r in j if r["variante"].endswith("_F2")]
        f = fm.get(m, {})
        tj_old = num(f.get("Tj_max_C"))
        old_db = num(f.get("picco_dopo_dB"))
        cambiato = (tmax[0] is not None and tj_old is not None and abs(tmax[0] - tj_old) > 3) or \
                   (omax[0] > 1 and (old_db is None or old_db < 100))
        righe.append({
            "modo": m, "ref": f.get("ref", ""), "funzione": f.get("funzione", ""),
            "posizioni": len(c), "tutte_finite": "si" if fine else "no",
            "Tj_max_60_C": "" if tmax[0] is None else "%.0f" % tmax[0], "parte": tmax[1],
            "posizione_Tj": tmax[2],
            "out_blocco_V": "" if omax[1] is None else "%.3g" % omax[1], "posizione_out": omax[2],
            "main_dB_SPL_max": "" if not dbs else "%.1f" % max(dbs),
            "out_F2_V": "" if not f2 else "%.3g" % max(f2),
            "fmea_Tj_max_C": f.get("Tj_max_C", ""), "fmea_picco_dB": f.get("picco_dopo_dB", ""),
            "fmea_stax_ms": f.get("stax_ms", ""), "fmea_priorita": f.get("priorita_dopo", ""),
            "fmea_stato": f.get("stato", ""), "fmea_fonte": f.get("fonte_dopo", "")[:60],
            "oltre_P7": "SI" if tmax[0] is not None and tmax[0] > 125 else "",
            "cambiato": "SI" if cambiato else "",
            "da_stax": "SI" if f2 and max(f2) > 1 else "",
        })
    out = os.path.join(L, "confronto.csv")
    w = csv.DictWriter(open(out, "w", newline=""), fieldnames=list(righe[0]))
    w.writeheader()
    w.writerows(righe)
    print("%d modi -> %s" % (len(righe), out))
    print("oltre P7: %s" % [r["modo"] for r in righe if r["oltre_P7"]])
    print("cambiati: %s" % [r["modo"] for r in righe if r["cambiato"]])
    print("da Stax:  %s" % [r["modo"] for r in righe if r["da_stax"]])
    print("non finiti / mancanti: %s" % [r["modo"] for r in righe if r["tutte_finite"] != "si"])
    print("senza riga FMEA: %s" % [r["modo"] for r in righe if not r["ref"]])


if __name__ == "__main__":
    main()
