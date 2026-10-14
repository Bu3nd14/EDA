#!/usr/bin/env python3
"""L45c1: the table of the rails' faults, one mode per row (fmea_rail.csv and .md). Solo stdlib.

    tabella_l45c1.py <L45c1>

Reads psu/modi.py (the modes), analisi_psu.csv (the supply side), corse_100k/analisi.csv (V2's
A_ins, the filtered peak of PR-23 / P9 (b), the load of L41c / L56) and corse_vuoto/p10.csv (the
raw peak and the time above 0,87 V, unloaded: P10, ADR-069). The criteria, written before
reading the audio runs:

  - a rail inside |13,5 V| after the fault (the supply's own figure, t_fuori_ms): P9 (b) /
    PR-23 - the supervisor within 1 ms, the jack open before a rail reaches 10,6 V (L41c's s),
    the filtered peak at the main jack <= 0,87 V (the ceiling) with 2 mV the target;
  - the dead short of a rail (C139-C142, C505 / C506, C511 / C512, the regulators' outputs):
    P9 (c), «caso accettato»: the numbers, no verdict;
  - the rails stay outside |13,5 V| (over-voltage, ripple, nothing): P10 as NEXT-SESSION asks,
    every jack <= 100 ms above 0,87 V, raw and unloaded;
  - a latent fault (an event other than mus, the welded NO): the criterion of its event, P9 (b).
dB SPL at 1 m: 33,45 dB at 100 uV, then 20 log10 of the ratio (NC-028; L56's tabella.py).
"""
import csv
import math
import os
import sys

L = os.path.abspath(sys.argv[1])
sys.path.insert(0, os.path.join(L, "psu"))
import modi  # noqa: E402

TETTO, OBIETTIVO = 0.87, 2e-3
ACCETTATI = ("f_vplus_massa_mus", "f_vminus_massa_mus")
BASI = {"spegnimento_l": "lo spegnimento", "perdita": "la perdita di rete",
        "guasto": "U502 spento (L41c)", "guasto_u501": "U501 spento (L41c)"}


def db(v):
    return 33.45 + 20 * math.log10(max(v, 1e-12) / 100e-6)


def leggi(p):
    return list(csv.DictReader(open(p))) if os.path.exists(p) else []


psu = {r["caso"]: r for r in leggi(os.path.join(L, "analisi_psu.csv"))}
ains = {}
for r in leggi(os.path.join(L, "corse_100k", "analisi.csv")):
    if r["grandezza"] == "A_ins":
        c = r["cella"][:-len("_l41c")]
        ains.setdefault(c, {})[r["uscita"]] = float(r["picco_V"])
p10 = {r["cella"][:-len("_l41c")]: r for r in leggi(os.path.join(L, "corse_vuoto", "p10.csv"))}
# the runs that abort with both methods, read up to the abort (fino_all_aborto.py): the RAW peak
# stands in for the filtered one (marked), and the unloaded raw figures for p10.csv's
ABORTO = {}
for car in ("100k", "vuoto"):
    for r in leggi(os.path.join(L, "corse_" + car, "aborto.csv")):
        c = r["cella"][:-len("_l41c")]
        ABORTO.setdefault(c, {})[car] = r
        if car == "100k" and "MAINJACK" not in ains.get(c, {}):
            ains[c] = {"MAINJACK": float(r["main_picco_V"]),
                       "FIXJACK1": float(r["fix1_picco_V"]), "FIXJACK2": float(r["fix2_picco_V"])}
        if car == "vuoto" and c not in p10:
            p10[c] = dict(r, main_alla_fine="no", fix1_alla_fine="no", fix2_alla_fine="no")

righe = []


def verdetto(caso, base):
    s = psu.get(base)
    a = ains.get(caso, {})
    q = p10.get(caso)
    r = {}
    if s is None:
        return {"verdetto": "manca la corsa dell'alimentatore"}
    r.update(vp="%.2f / %.2f" % (float(s["vp_min"]), float(s["vp_max"])),
             vm="%.2f / %.2f" % (float(s["vm_min"]), float(s["vm_max"])),
             t_fuori=s["t_fuori_ms"], t_mute=s["t_mute_g_ms"],
             t_jack="mai" if caso.startswith("nosald_") else (s["t_jack_ms"] or "mai"),
             t_10_6=s["t_10_6_ms"])
    pm = a.get("MAINJACK")
    pf = max([a[k] for k in ("FIXJACK1", "FIXJACK2") if k in a] or [float("nan")])
    r["A_main_V"] = "" if pm is None else "%.3g" % pm
    r["A_main_dB"] = "" if pm is None else "%.1f" % db(pm)
    r["A_fisse_V"] = "" if pf != pf else "%.3g" % pf
    if q:
        r["grezzo_main_V"] = "%.3g" % float(q["main_picco_V"])
        r["grezzo_fisse_V"] = "%.3g" % max(float(q["fix1_picco_V"]), float(q["fix2_picco_V"]))
        r["sopra_main_ms"] = "%.1f" % float(q["main_sopra_ms"])
        r["sopra_fisse_ms"] = "%.1f" % max(float(q["fix1_sopra_ms"]), float(q["fix2_sopra_ms"]))
        fine = "si" in (q["main_alla_fine"], q["fix1_alla_fine"], q["fix2_alla_fine"])
        r["sopra_alla_fine"] = "si" if fine else "no"
    fuori = bool(s["t_fuori_ms"])
    if caso in ACCETTATI:
        r["criterio"], r["verdetto"] = "P9 (c)", "caso accettato"
    elif fuori:
        r["criterio"] = "P9 (b)"
        ko = []
        if s["sorvegliante_1ms"] != "si":
            ko.append("sorvegliante oltre 1 ms" if s["t_mute_g_ms"] else "nessun mute")
        jack_mai = caso.startswith("nosald_") or not s["t_jack_ms"]
        if jack_mai:
            ko.append("il jack non si apre")
        elif s["jack_prima"] == "no":
            ko.append("jack dopo 10,6 V")
        if pm is None:
            ko.append("manca la corsa audio")
        elif pm > TETTO:
            ko.append("picco oltre il tetto")
        if ko:
            r["verdetto"] = "FUORI: " + ", ".join(ko)
        else:
            r["verdetto"] = "entro" + ("" if pm <= OBIETTIVO else ", sopra l'obiettivo di 2 mV")
    else:
        r["criterio"] = "P10"
        if not q:
            r["verdetto"] = "manca la corsa a vuoto"
        else:
            m = max(float(q[j + "_sopra_ms"]) for j in ("main", "fix1", "fix2"))
            r["verdetto"] = "entro" if m <= 100 else ("FUORI" + (", ancora sopra alla fine" if r.get("sopra_alla_fine") == "si" else ""))
    return r


for caso, ref, modo, prim, cosa in modi.SIMULATI:
    r = dict(ref=ref, modo=modo, caso=caso, come="simulato", nota=cosa)
    if caso in ABORTO:
        r["come"] = "simulato, letto fino all'aborto (picco grezzo al posto del filtrato)"
    r.update(verdetto(caso, caso))
    righe.append(r)
for nome, base, ref, cosa in modi.SALDATI:
    r = dict(ref=ref, modo=cosa, caso=nome, come="simulato (ponte di %s, jack chiuso)" % base, nota="")
    r.update(verdetto(nome, base))
    righe.append(r)
for b, cosa in BASI.items():
    r = dict(ref="-", modo="senza guasto: " + cosa, caso=b, come="riferimento (L56)", nota="")
    r.update(verdetto(b, b))
    righe.append(r)
for ref, modo, uguale, perche in modi.UGUALI:
    righe.append(dict(ref=ref, modo=modo, caso=uguale, come="uguale a", nota=perche, verdetto="come " + uguale))
for ref, modo, effetto, fonte in modi.CALCOLO:
    righe.append(dict(ref=ref, modo=modo, caso="", come=fonte, nota=effetto, verdetto="calcolo"))

CAMPI = ["ref", "modo", "caso", "come", "criterio", "verdetto", "vp", "vm", "t_fuori", "t_mute",
         "t_jack", "t_10_6", "A_main_V", "A_main_dB", "A_fisse_V", "grezzo_main_V", "grezzo_fisse_V",
         "sopra_main_ms", "sopra_fisse_ms", "sopra_alla_fine", "nota"]
with open(os.path.join(L, "fmea_rail.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=CAMPI)
    w.writeheader()
    for r in righe:
        w.writerow({k: r.get(k, "") for k in CAMPI})

TIT = {"ref": "Parte", "modo": "Modo", "caso": "Caso", "come": "Come", "criterio": "Criterio",
       "verdetto": "Verdetto", "vp": "V+ min / max", "vm": "V- min / max", "t_fuori": "|rail| < 13,5 V (ms)",
       "t_mute": "mute (ms)", "t_jack": "jack aperto (ms)", "t_10_6": "|rail| < 10,6 V (ms)",
       "A_main_V": "picco filtrato al principale, 100 k (V)", "A_main_dB": "dB SPL a 1 m",
       "A_fisse_V": "fisse, filtrato (V)", "grezzo_main_V": "grezzo al principale, a vuoto (V)",
       "grezzo_fisse_V": "fisse, grezzo (V)", "sopra_main_ms": "sopra 0,87 V, principale (ms)",
       "sopra_fisse_ms": "sopra 0,87 V, fisse (ms)", "sopra_alla_fine": "ancora sopra alla fine",
       "nota": "Nota"}
with open(os.path.join(L, "fmea_rail.md"), "w") as f:
    f.write("# L45c1 — i guasti dei rail audio, un modo per riga\n\n")
    f.write("Generata da `script/tabella_l45c1.py` (i criteri sono nella sua intestazione). Tempi in "
            "ms dal guasto (o dall'evento, per i latenti), col jack all'angolo peggiore del G6K.\n\n")
    f.write("| " + " | ".join(TIT[k] for k in CAMPI) + " |\n")
    f.write("|" + "---|" * len(CAMPI) + "\n")
    for r in righe:
        f.write("| " + " | ".join(str(r.get(k, "")).replace("|", "/") for k in CAMPI) + " |\n")
print("scritto fmea_rail.csv / .md: %d righe" % len(righe))
