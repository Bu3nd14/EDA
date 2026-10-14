#!/usr/bin/env python3
"""L45d1: the ADR-070 columns for a FMEA table that already has its rows, its measured peaks and its
verdicts. Solo stdlib, imported by the riporto_*.py scripts.

The rules are L45c2's (tabella_l45c2.py, data/2026-10-14/L45c2/script/), lifted out UNCHANGED so
that the carry-over of L45a, L45b and L45c1 uses the same scale; verifica_l45c2.py recomputes
L45c2's columns from its own table with them, and must find every one equal. One addition, which
L45c2 does not use (its MOLT is empty): MOLT, the number of identical parts a row stands for (the
eight gain blocks, K2-K4, ...), multiplies the mode's rate, as L45c2's FRAZIONE already did for J514
and R544-R547.

ADR-070's columns:
  gravita'     1 <= 100 uV; 2 a function lost, or <= 2 mV; 3 > 2 mV inside the criterion; 4 the
               criterion not met; 5 a part beyond its limits. From the verdict and the filtered peak
               at the main jack and the fixed ones, raised to the row's minimum
  probabilita' 1 < 1 FIT, 2 1-10, 3 10-100, 4 > 100, from the part's rate x the mode's fraction
               x the multiplicity
  rilevabilita' 1 the circuit, 2 the listener, 3 latent
  priorita'    the matrix of ADR-070
"""
import math
import re

TETTO, OBIETTIVO = 0.87, 2e-3
# the case names a row may point at ('= a', '= a, b', '= a o b'): L45c2's, plus L45c1's welded NO
NOMI = re.compile(r"\b(f_[a-z0-9_]+|nosald_[a-z0-9_]+|guasto_u50\d|corto_u503|cf_nodelta|guasto)\b")


def db(v):
    """dB SPL of peak at 1 m: 33,45 dB at 100 uV, then 20 log10 of the ratio (NC-028)."""
    return 33.45 + 20 * math.log10(max(v, 1e-12) / 100e-6)


def num(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def g_misurata(verdetto, pm, pf):
    """The severity the measurement shows: 4 out of the criterion, else by the larger peak."""
    if verdetto.startswith("FUORI"):
        return 4
    m = max(pm or 0.0, pf or 0.0)
    return 1 if m <= 100e-6 else 2 if m <= OBIETTIVO else 3


def frazione(K, ref, modo):
    """(the mode's key in K.TIPI, multiplicity), from K.FRAZIONE or L45c2's rules."""
    if (ref, modo) in K.FRAZIONE:
        return K.FRAZIONE[(ref, modo)]
    t = K.tipo_di(ref)
    m = modo.split(", poi")[0]
    if t in ("FET", "JFET"):
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
    if t in ("LDO", "LDO_P"):
        if re.search(r"pin \d|SENSE|EN aperto", m):
            return ("fuori/%d" % K.N_FUORI[ref], 1)
        if "IN-OUT" in m:
            return ("segue", 1)
        if "spento" in m:
            return ("spento", 1)
    if m.startswith("aperto") or " aperto" in m:
        return ("aperto", 1)
    if m.startswith("corto") or "in corto" in m:
        return ("corto", 1)
    raise SystemExit("frazione: %s / %s senza regola" % (ref, modo))


def fr(dist, chiave):
    """The fraction of a key: 'a' one mode, 'a+b' the sum (L45c2's off+gs), 'a/N' a mode shared by N
    rows (L45c2's fuori/8)."""
    if "/" in chiave:
        k, n = chiave.split("/")
        return fr(dist, k) / int(n)
    return sum(dist[k] for k in chiave.split("+"))


def classe_p(fm):
    return 1 if fm < 1 else 2 if fm < 10 else 3 if fm < 100 else 4


def probabilita(K, ref, modo):
    t = K.tipo_di(ref)
    if t is None:
        return dict(tipo="", fit_parte="", fonte="", frazione="", fit_modo="", P="")
    fit, fonte, dist = K.TIPI[t]
    chiave, n = frazione(K, ref, modo)
    n *= getattr(K, "MOLT", {}).get(ref, 1)
    f = fr(dist, chiave)
    fm = fit * f * n
    P = classe_p(fm)
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


def classe(K, r, G, R, rimedio, nota=""):
    p = probabilita(K, r["ref"], r["modo"])
    r.update(p)
    r["G"], r["R"] = G, R
    r["priorita"] = priorita(G, p["P"], R) if p["P"] != "" else ""
    r["rimedi"] = K.RIMEDI[rimedio] if rimedio else ""
    if nota:
        r["nota"] = (r.get("nota", "") + "; " + nota).strip("; ")
    r["funzione"] = K.funzione(r["ref"], r["modo"])


def classifica(righe, K, basi_classi):
    """The ADR-070 columns for a table of the supply's kind (L45c1, L45c2): reference rows (ref '-'
    or come 'riferimento...'), simulated rows (come 'simulato...', their case in K.SIM), rows equal
    to a case (come 'uguale a', the case in 'caso') and calculated rows (the source in 'come').
    Same order of work as tabella_l45c2.py: the measured rows first, since the others point at them."""
    per_caso = {}
    for r in righe:
        rif = r["ref"] == "-" or r["come"].startswith("riferimento")
        if not (rif or r["come"].startswith("simulato")):
            continue
        g = g_misurata(r["verdetto"], num(r.get("A_main_V")), num(r.get("A_fisse_V")))
        caso = r["caso"]
        if rif:
            R, gmin, _ = basi_classi.get(caso, (None, None, ""))
            per_caso[caso] = (max(g, gmin or 0), R)
            continue
        R, gmin, nota, rim = K.SIM[caso]
        G = max(g, gmin)
        per_caso[caso] = (G, R)
        classe(K, r, G, R, rim, nota)

    def rimanda(fonte):
        nomi = NOMI.findall(fonte)
        vis = [per_caso[n] for n in nomi if n in per_caso]
        if not vis:
            return None
        return max(v[0] for v in vis), vis[0][1], nomi

    for r in righe:
        c = r["come"]
        if r["ref"] == "-" or c.startswith("riferimento") or c.startswith("simulato"):
            continue
        fonte = r["caso"] if c == "uguale a" else c
        x = K.CALC.get((r["ref"], r["modo"]))
        if x:
            classe(K, r, x[0], x[1], x[2])
            continue
        y = rimanda(fonte)
        if y is None:
            raise SystemExit("%s / %s: niente in CALC e nessun caso a cui rimanda" % (r["ref"], r["modo"]))
        G, R, nomi = y
        base = basi_classi.get(nomi[0]) or K.SIM.get(nomi[0])
        classe(K, r, G, R, base[3] if len(base) == 4 else base[2])
    return righe


ADR070 = ["funzione", "G", "tipo", "fit_parte", "fonte", "frazione", "fit_modo", "P", "R",
          "priorita", "rimedi"]
TITOLI = {"ref": "Parte", "funzione": "Funzione", "modo": "Modo", "come": "Come",
          "verdetto": "Verdetto", "G": "Gravita'", "fit_modo": "FIT del modo", "P": "Probabilita'",
          "R": "Rilevabilita'", "priorita": "Priorita'", "rimedi": "Rimedi candidati",
          "nota": "Effetto e nota", "lotto": "Lotto"}


def scrivi(base, righe, campi, md_campi, titolo, intro, titoli=None):
    """<base>.csv with every column in the table's order, <base>.md ordered by priority."""
    import csv
    t = dict(TITOLI, **(titoli or {}))
    with open(base + ".csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campi)
        w.writeheader()
        for r in righe:
            w.writerow({k: r.get(k, "") for k in campi})
    with open(base + ".md", "w") as f:
        f.write("# " + titolo + "\n\n" + intro + "\n\n")
        f.write("| " + " | ".join(t.get(k, k) for k in md_campi) + " |\n")
        f.write("|" + "---|" * len(md_campi) + "\n")
        for r in sorted(righe, key=chiave_ordine):
            f.write("| " + " | ".join(str(r.get(k, "")).replace("|", "/").replace("\n", " ")
                                      for k in md_campi) + " |\n")


def conta(righe):
    n = {}
    for r in righe:
        n[r.get("priorita", "")] = n.get(r.get("priorita", ""), 0) + 1
    return n


ORDINE = {"alta": 0, "media": 1, "bassa": 2, "": 3}


def chiave_ordine(r):
    """priority, then severity (worst first), then the mode's rate (largest first)."""
    return (ORDINE[str(r.get("priorita", ""))], -int(r.get("G") or 0), -(num(r.get("fit_modo")) or 0))
