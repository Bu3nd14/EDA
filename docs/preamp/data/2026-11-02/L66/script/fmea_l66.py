#!/usr/bin/env python3
"""L66: le righe della FMEA del blocco rifatte sul sorgente DOPO ADR-111 (ADR-070, le colonne di
fmea_dopo.csv di L45d2b3b3). Solo stdlib, /usr/bin/python3 -I.

Uso: fmea_l66.py   -> fmea_l66.csv, e stampa i controlli

Le righe: ogni riga del blocco di fmea_dopo.csv (le tabelle di L45 e le parti nuove del blocco) il cui
caso e' un modo del canale; per i modi che L58b ha riscritto (fmea_l58b.csv) si parte dalla riga di
L58b. Cambiano, dal sorgente dopo ADR-111 (calore_dopo.csv coi finali col dissipatore,
analisi_jack_dopo.csv):
  Tj_max_C      la Tj massima a 60 C d'aria sulle posizioni del modo (e la parte, in effetto_dopo)
  picco_dopo_V  il picco alla principale (main_A_V), il massimo sulle posizioni
  picco_dopo_dB il suo dB SPL (main_dB_SPL)
  stax_ms       Q132_be e D158_cc da p10_stax.csv (il condensatore a +5 %, il caso peggiore); gli
                altri restano quelli della riga (i picchi al jack sul sorgente sono quelli della FMEA
                entro 0,1 dB, confronto.csv), e la fonte lo dice
  lotto, fonte_dopo; e per Q132_be e D158_cc decisione, adr, rimedio, stato.
G, P, R e la priorita' non cambiano: il guasto al rail ha la gravita' dei guasti al rail del blocco
(Q132_ce, G 3), che la riga gia' aveva.
"""
import csv
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
DATA = os.path.abspath(os.path.join(L, "..", ".."))
FMEA = os.path.join(DATA, "2026-10-24", "L45d2b3b3", "fmea_dopo.csv")
L58B = os.path.join(DATA, "2026-11-01", "L58b", "fmea_l58b.csv")
RAIL = ("Q132_be", "D158_cc")


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def per_modo(p):
    out = {}
    for r in csv.DictReader(open(p)):
        out.setdefault(r["modo"], []).append(r)
    return out


def main():
    cal = per_modo(os.path.join(L, "calore_dopo.csv"))
    jack = per_modo(os.path.join(L, "analisi_jack_dopo.csv"))
    stax = {}
    for r in csv.DictReader(open(os.path.join(L, "p10_stax.csv"))):
        m = r["modo"].replace("G0_F2_", "").replace("_k105", "")
        stax[m] = max(stax.get(m, 0.0), num(r["fix2_sopra_ms"]))
    l58b = {r["caso"]: r for r in csv.DictReader(open(L58B)) if r["gruppo"] == "tabelle di L45"}
    campi = None
    righe, mancano = [], []
    for r in csv.DictReader(open(FMEA)):
        campi = campi or list(r)
        blocco = r["gruppo"] == "tabelle di L45" or (r["gruppo"] == "parti nuove" and r["lotto"] == "blocco")
        m = r["caso"]
        if not blocco or not m or m not in cal:
            if blocco and m and m.rsplit("_", 1)[0][0] in "RCDQJ" and m not in cal:
                mancano.append(m)
            continue
        base = dict(l58b.get(m, r))
        c, j = cal[m], jack.get(m, [])
        if any(x["fine"] != "si" for x in c):
            sys.exit("RIFIUTATO: %s non finito su tutte le posizioni" % m)
        tj, parte, pos = max((num(x["Tj_max_60"]), x["Tj_max_disp_60"], x["posizione"]) for x in c)
        mv = max((num(x["main_A_V"]) or 0.0) for x in j)
        mdb = max((num(x["main_dB_SPL"]) or -999.0) for x in j)
        f1 = max((num(x["fix1_A_V"]) or 0.0) for x in j)
        if m in RAIL:
            sx, fonte_s = stax[m], "L66/p10_stax.csv (sorgente, il condensatore a +5 %)"
        else:
            sx, fonte_s = num(base["stax_ms"]), "la Stax dalla riga di prima (%s)" % (base["fonte_dopo"][:70] or "-")
        sxt = "" if sx is None else "%.1f" % sx
        base["lotto"] = "L66"
        base["Tj_max_C"] = "%.0f" % tj
        base["picco_dopo_V"] = "%.4g" % mv
        base["picco_dopo_dB"] = "%.1f" % mdb
        base["stax_ms"] = sxt
        base["effetto_dopo"] = ("Tj max a 60 C %.0f C (%s, %s); principale %.3g V (%.1f dB SPL), fissa 1 %.3g V%s"
                                % (tj, parte, pos, mv, mdb, f1,
                                   "; Stax %s ms sopra 0,87 V" % sxt if sxt else ""))
        if m in RAIL:
            base["decisione"] = "l'uscita del blocco al rail (sorgente, ADR-099): il VAS al limite; rimedio nel circuito"
            base["adr"] = "ADR-111"
            base["rimedio"] = "ADR-111 (il limitatore del VAS a 36,5 + 18,7 ohm)"
            base["effetto_dopo"] += ("; l'uscita del blocco al rail, come i corti dei finali; principale e fissa 1 "
                                     "sulla protezione a valle (ADR-081)")
            base["stato"] = "nel circuito (ADR-111), misurata sul sorgente"
        base["fonte_dopo"] = "L66/calore_dopo.csv, analisi_jack_dopo.csv (sorgente, ADR-111); " + fonte_s
        righe.append(base)
    with open(os.path.join(L, "fmea_l66.csv"), "w", newline="") as fo:
        w = csv.DictWriter(fo, fieldnames=campi)
        w.writeheader()
        w.writerows(righe)
    oltre = [(x["caso"], x["Tj_max_C"]) for x in righe if float(x["Tj_max_C"]) > 125]
    stax_oltre = [(x["caso"], x["stax_ms"]) for x in righe if num(x["stax_ms"]) and num(x["stax_ms"]) > 150]
    print("righe: %d -> fmea_l66.csv" % len(righe))
    print("oltre P7 (Tj > 125 C): %s" % oltre)
    print("oltre P10 (Stax > 150 ms): %s" % stax_oltre)
    print("modi del blocco nella FMEA senza corsa: %s" % sorted(set(mancano)))
    print("priorita' alte: %s" % [x["caso"] for x in righe if x["priorita_dopo"] == "alta"])


if __name__ == "__main__":
    main()
