#!/usr/bin/env python3
"""L45c2: the FMEA of the relay line and the commands, one mode per row, in the form of ADR-070
(fmea_comando.csv and .md). Solo stdlib.

    tabella_l45c2.py <L45c2>

Reads psu/modi.py (the modes), analisi_psu.csv and analisi_rele.csv (the supply side),
corse_100k/analisi.csv (V2's A_ins, the filtered peak of PR-23 / P9 (b)), corse_vuoto/p10.csv (the
raw peak and the time above 0,87 V, unloaded: P10) and script/classi_l45c2.py (the rates, the
detection, the remedies). The criteria are L45c1's (tabella_l45c1.py), written before the runs:

  - a rail inside |13,5 V| after the fault: P9 (b) / PR-23 - the supervisor within 1 ms, the jack
    open before a rail reaches 10,6 V, the filtered peak at the main jack <= 0,87 V (2 mV target);
  - the rails stay outside |13,5 V|: P10, every jack <= 100 ms above 0,87 V, raw and unloaded;
  - a latent fault: the criterion of its event.
ADR-070's columns:
  gravita'     1 <= 100 uV; 2 a function lost, or <= 2 mV; 3 > 2 mV inside the criterion; 4 the
               criterion not met; 5 a part beyond its limits. From the filtered peak at the main
               jack and the fixed ones (100 k), raised to the row's minimum (classi_l45c2.SIM)
  probabilita' 1 < 1 FIT, 2 1-10, 3 10-100, 4 > 100, from the part's rate x the mode's fraction
  rilevabilita' 1 the circuit, 2 the listener, 3 latent
  priorita'    the matrix of ADR-070
dB SPL at 1 m: 33,45 dB at 100 uV, then 20 log10 of the ratio (NC-028)."""
import csv
import math
import os
import re
import sys

L = os.path.abspath(sys.argv[1])
sys.path.insert(0, os.path.join(L, "psu"))
sys.path.insert(0, os.path.join(L, "script"))
import modi  # noqa: E402
import classi_l45c2 as K  # noqa: E402

TETTO, OBIETTIVO = 0.87, 2e-3
BASI = {"spegnimento_l": "lo spegnimento", "perdita": "la perdita di rete",
        "guasto": "U502 spento (L41c)", "guasto_u501": "U501 spento (L41c)",
        "guasto_u503": "U503 spento (L41c)", "corto_u503": "l'uscita di U503 a massa (L41c, ADR-051)",
        "cf_nodelta": "la perdita di rete senza Delta (C528 = 10 pF, L30 / L41c)"}
# the base cases a row may point at: (detection, minimum severity, remedy)
BASI_CLASSI = {"guasto_u503": (1, 2, "nessuno"), "corto_u503": (1, 2, "delta"),
               "cf_nodelta": (3, 1, "delta_latente"), "f_base_niente_ins": (2, 2, "funzione")}


def db(v):
    return 33.45 + 20 * math.log10(max(v, 1e-12) / 100e-6)


def leggi(p):
    return list(csv.DictReader(open(p))) if os.path.exists(p) else []


psu = {r["caso"]: r for r in leggi(os.path.join(L, "analisi_psu.csv"))}
rele = {r["caso"]: r for r in leggi(os.path.join(L, "analisi_rele.csv"))}
ains = {}
for r in leggi(os.path.join(L, "corse_100k", "analisi.csv")):
    if r["grandezza"] == "A_ins":
        ains.setdefault(r["cella"][:-len("_l41c")], {})[r["uscita"]] = float(r["picco_V"])
p10 = {r["cella"][:-len("_l41c")]: r for r in leggi(os.path.join(L, "corse_vuoto", "p10.csv"))}


def misura(caso):
    """L45c1's verdetto(), the same criteria, plus the gain's lead over the jack."""
    s, a, q, e = psu.get(caso), ains.get(caso, {}), p10.get(caso), rele.get(caso, {})
    if s is None:
        raise SystemExit("%s: manca la corsa dell'alimentatore" % caso)
    r = dict(t_fuori=s["t_fuori_ms"], t_mute=s["t_mute_g_ms"], t_jack=s["t_jack_ms"] or "mai",
             t_guad=s["t_guadagno_ms"] or "mai", t_10_6=s["t_10_6_ms"],
             anticipo_guad=e.get("anticipo_guadagno_ms", ""))
    pm = a.get("MAINJACK")
    pf = max([a[k] for k in ("FIXJACK1", "FIXJACK2") if k in a] or [0.0])
    if pm is None or q is None:
        raise SystemExit("%s: manca una corsa audio" % caso)
    r.update(A_main_V="%.3g" % pm, A_main_dB="%.1f" % db(pm), A_fisse_V="%.3g" % pf,
             grezzo_main_V="%.3g" % float(q["main_picco_V"]),
             grezzo_fisse_V="%.3g" % max(float(q["fix1_picco_V"]), float(q["fix2_picco_V"])),
             sopra_ms="%.1f" % max(float(q[j + "_sopra_ms"]) for j in ("main", "fix1", "fix2")))
    if s["t_fuori_ms"]:
        r["criterio"] = "P9 (b)"
        ko = []
        if s["sorvegliante_1ms"] != "si":
            ko.append("sorvegliante oltre 1 ms" if s["t_mute_g_ms"] else "nessun mute")
        if not s["t_jack_ms"]:
            ko.append("il jack non si apre")
        elif s["jack_prima"] == "no":
            ko.append("jack dopo 10,6 V")
        if pm > TETTO:
            ko.append("picco oltre il tetto")
        r["verdetto"] = ("FUORI: " + ", ".join(ko)) if ko else (
            "entro" + ("" if pm <= OBIETTIVO else ", sopra l'obiettivo di 2 mV"))
    else:
        r["criterio"] = "P10"
        m = max(float(q[j + "_sopra_ms"]) for j in ("main", "fix1", "fix2"))
        r["verdetto"] = "entro" if m <= 100 else "FUORI"
    g = 4 if r["verdetto"].startswith("FUORI") else (
        1 if max(pm, pf) <= 100e-6 else 2 if max(pm, pf) <= OBIETTIVO else 3)
    r["_g"] = g
    return r


def frazione(ref, modo):
    """(the mode's key in TIPI, multiplicity), from classi.FRAZIONE or the rules."""
    if (ref, modo) in K.FRAZIONE:
        return K.FRAZIONE[(ref, modo)]
    t = K.tipo_di(ref)
    m = modo.split(", poi")[0]
    if t == "FET":
        if "G-D" in m:
            return ("gd", 1)
        if "aperto (D-S)" in m and "G-S" in m:
            return ("off+gs", 1)
        if "G-S" in m or "gate" in m:
            return ("gs", 1)
        if "corto D-S" in m:
            return ("on", 1)
        if "aperto" in m:
            return ("off", 1)
    if t == "CMP":
        if "cieco" in m:
            return ("cieco", 1)
        if "bloccat" in m:
            return ("basso", 1)
    if t == "LDO":
        if re.search(r"pin \d|SENSE|EN aperto", m):
            return ("fuori/%d" % K.N_FUORI_U503, 1)
        if "IN-OUT" in m:
            return ("segue", 1)
        if "spento" in m:
            return ("spento", 1)
    if m.startswith("aperto") or " aperto" in m:
        return ("aperto", 1)
    if m.startswith("corto") or "in corto" in m:
        return ("corto", 1)
    raise SystemExit("frazione: %s / %s senza regola" % (ref, modo))


def probabilita(ref, modo):
    t = K.tipo_di(ref)
    if t is None:
        return dict(tipo="", fit_parte="", fonte="", frazione="", fit_modo="", P="")
    fit, fonte, dist = K.TIPI[t]
    chiave, n = frazione(ref, modo)
    if chiave == "off+gs":
        f = dist["off"] + dist["gs"]
    elif chiave.startswith("fuori/"):
        f = dist["fuori"] / int(chiave.split("/")[1])
    else:
        f = dist[chiave]
    fm = fit * f * n
    P = 1 if fm < 1 else 2 if fm < 10 else 3 if fm < 100 else 4
    return dict(tipo=t, fit_parte="%g" % fit, fonte=fonte, frazione="%s %.3g%s" % (
        chiave, f, (" x %d" % n) if n > 1 else ""), fit_modo="%.3g" % fm, P=P)


def priorita(G, P, R):
    if G == 5:
        return "alta"
    if G == 4:
        return "media" if (P == 1 and R != 3) else "alta"
    if G == 3:
        return "media" if (P >= 3 or R == 3) else "bassa"
    return "bassa"


FUNZIONE = [
    (("T2", "F501", "J514", "D503", "D504", "C520", "C521", "C522", "U503", "C523", "D512", "C524"),
     "la linea dei rele' (VRELAY_REG)"),
    (("U504", "C525", "C517", "C519", "C530"), "la logica (V5)"),
    (("NT501", "J2"), "la stella e il ritorno dei rele'"),
    (("Q505", "Q506", "R539", "R540", "C531", "J1"), "l'interruttore dello standby (VRELAY)"),
    (("U505", "R506", "R507", "R508", "R509", "C515", "C516"), "il sorvegliante dei rail"),
    (("U507", "R503", "R504", "R505", "C514"), "il riferimento"),
    (("Q504", "R510", "R511", "R512", "C518"), "il rivelatore di rete"),
    (("R522", "R523", "C526"), "il sorvegliante di VRELAY"),
    (("U508", "C528", "R534", "C529", "R536", "D520", "D521", "D523", "D524", "R532", "R533",
      "R535", "R524", "R516", "R537", "R538"), "il ritardo Delta in hardware"),
    (("Q501", "D506", "D507", "R513", "R514", "C527"), "il comando del jack (MUTE_CMD)"),
    (("Q502", "D508", "D509", "D522"), "il permesso (PERMIT_CMD)"),
    (("Q503", "D505", "R520", "R521", "K501"), "il rele' di rete"),
    (("R525", "R526", "R527", "R528"), "i pull-down dei comandi"),
    (("R541", "R542", "R543", "R544-R547", "R517", "R518", "C532", "C533"), "le letture del micro"),
]


def funzione(ref, modo):
    if ref == "U506":
        return "il sorvegliante di VRELAY" if "canale B" in modo else "il rivelatore di rete"
    for refs, f in FUNZIONE:
        if ref in refs:
            return f
    return ""


righe, per_caso = [], {}


def classe(r, G, R, rimedio, nota=""):
    p = probabilita(r["ref"], r["modo"])
    r.update(p)
    r["G"], r["R"] = G, R
    r["priorita"] = priorita(G, p["P"], R) if p["P"] != "" else ""
    r["rimedi"] = K.RIMEDI[rimedio] if rimedio else ""
    if nota:
        r["nota"] = (r.get("nota", "") + "; " + nota).strip("; ")
    r["funzione"] = funzione(r["ref"], r["modo"])


# the base cases first (their figures are what rows point at)
for b, cosa in BASI.items():
    m = misura(b)
    R, gmin, rim = BASI_CLASSI.get(b, (None, None, ""))
    per_caso[b] = (max(m["_g"], gmin or 0), R)
    righe.append(dict(ref="-", modo="senza guasto: " + cosa, caso=b, come="riferimento", **m))
for caso, ref, modo, prim, cosa in modi.SIMULATI:
    m = misura(caso)
    R, gmin, nota, rim = K.SIM[caso]
    r = dict(ref=ref, modo=modo, caso=caso, come="simulato", nota=cosa, **m)
    if caso in getattr(modi, "TF", {}):
        r["come"] += ", fino a TE + %g s" % modi.TF[caso]
    if ref == "-":
        r["come"] = "riferimento"
        per_caso[caso] = (max(m["_g"], BASI_CLASSI[caso][1]), BASI_CLASSI[caso][0])
        righe.append(r)
        continue
    G = max(m["_g"], gmin)
    per_caso[caso] = (G, R)
    classe(r, G, R, rim, nota)
    righe.append(r)


def rimanda(fonte):
    """The cases a row points at ('= a', '= a, b', '= a o b'): the worst severity, the first's detection."""
    nomi = re.findall(r"\b(f_[a-z0-9_]+|guasto_u50\d|corto_u503|cf_nodelta|guasto)\b", fonte)
    vis = [per_caso[n] for n in nomi if n in per_caso]
    if not vis:
        return None
    return max(v[0] for v in vis), vis[0][1], nomi


for ref, modo, uguale, perche in modi.UGUALI:
    r = dict(ref=ref, modo=modo, caso=uguale, come="uguale a", nota=perche)
    x = K.CALC.get((ref, modo)) or None
    if x:
        classe(r, x[0], x[1], x[2])
    else:
        G, R, nomi = rimanda(uguale)
        base = BASI_CLASSI.get(nomi[0]) or K.SIM.get(nomi[0])
        classe(r, G, R, base[3] if len(base) == 4 else base[2])
    r["verdetto"] = "come " + uguale
    righe.append(r)
for ref, modo, effetto, fonte in modi.CALCOLO:
    r = dict(ref=ref, modo=modo, caso="", come=fonte, nota=effetto)
    x = K.CALC.get((ref, modo))
    if x:
        classe(r, x[0], x[1], x[2])
    else:
        y = rimanda(fonte)
        if y is None:
            raise SystemExit("%s / %s: niente in classi_l45c2.CALC e nessun caso a cui rimanda" % (ref, modo))
        G, R, nomi = y
        base = BASI_CLASSI.get(nomi[0]) or K.SIM.get(nomi[0])
        classe(r, G, R, base[3] if len(base) == 4 else base[2])
    r["verdetto"] = "calcolo" if fonte in ("calcolo", "datasheet", "non simulato") else "come " + fonte[2:]
    righe.append(r)

CAMPI = ["ref", "funzione", "modo", "caso", "come", "criterio", "verdetto", "G", "tipo", "fit_parte",
         "fonte", "frazione", "fit_modo", "P", "R", "priorita", "rimedi",
         "t_fuori", "t_mute", "t_jack", "t_guad", "anticipo_guad", "t_10_6", "A_main_V", "A_main_dB",
         "A_fisse_V", "grezzo_main_V", "grezzo_fisse_V", "sopra_ms", "nota"]
with open(os.path.join(L, "fmea_comando.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=CAMPI)
    w.writeheader()
    for r in righe:
        w.writerow({k: r.get(k, "") for k in CAMPI})

TIT = {"ref": "Parte", "funzione": "Funzione", "modo": "Modo", "caso": "Caso", "come": "Come",
       "criterio": "Criterio", "verdetto": "Verdetto", "G": "Gravita'", "fit_modo": "FIT del modo",
       "P": "Probabilita'", "R": "Rilevabilita'", "priorita": "Priorita'",
       "t_jack": "jack aperto (ms)", "anticipo_guad": "guadagno prima del jack (ms)",
       "A_main_V": "picco filtrato al principale (V)", "A_main_dB": "dB SPL a 1 m",
       "sopra_ms": "sopra 0,87 V (ms)", "nota": "Effetto e nota", "rimedi": "Rimedi candidati"}
MD = ["ref", "funzione", "modo", "come", "verdetto", "G", "fit_modo", "P", "R", "priorita", "t_jack",
      "anticipo_guad", "A_main_V", "A_main_dB", "sopra_ms", "nota", "rimedi"]
ordine = {"alta": 0, "media": 1, "bassa": 2, "": 3}
with open(os.path.join(L, "fmea_comando.md"), "w") as f:
    f.write("# L45c2 — i guasti della linea dei rele' e del comando, un modo per riga (ADR-070)\n\n")
    f.write("Generata da `script/tabella_l45c2.py` (i criteri nella sua intestazione, i tassi e le "
            "classi in `script/classi_l45c2.py`). Ordinata per priorita', poi per gravita'. Tempi in "
            "ms dal guasto (o dall'evento, per i latenti), col jack all'angolo peggiore del G6K. Le "
            "colonne di dettaglio sono in `fmea_comando.csv`.\n\n")
    f.write("| " + " | ".join(TIT[k] for k in MD) + " |\n")
    f.write("|" + "---|" * len(MD) + "\n")
    for r in sorted(righe, key=lambda r: (ordine[r.get("priorita", "")], -int(r.get("G") or 0))):
        f.write("| " + " | ".join(str(r.get(k, "")).replace("|", "/") for k in MD) + " |\n")
n = {}
for r in righe:
    n[r.get("priorita", "")] = n.get(r.get("priorita", ""), 0) + 1
print("scritto fmea_comando.csv / .md: %d righe; priorita' %s" % (len(righe), n))
