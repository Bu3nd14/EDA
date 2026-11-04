#!/usr/bin/env python3
"""L69: the FMEA rows of AT_MRQ's and AT_ON's pull-ups after ADR-116 (R572 + R588, R576 + R589, each two
halves in series), in ADR-070's form, with fmea_l68.py's columns. The seventh source of fmea_oggi.csv. Solo stdlib.

Uso: /usr/bin/python3 -I script/fmea_l69.py   -> fmea_l69.csv in L69/, and prints the rows

  the runs   seq/oggi on the source after ADR-116 (an_sorgente.csv, confronto_sorgente.csv: against L64b's
             healthy run of each event and against the same case in L68), calore_5v.csv (U504)
  the rows   R572 / R576 open and shorted REPLACE L68's (same key: ref, modo, caso); R588 / R589 are new.
             Every other row of the timer stays L68's: on the new source its case gives L68's verdicts and
             times in all eight events (confronto_sorgente.csv: «L68: uguale»), checked here (exit 1 if not)
  the latch's heat with a half shorted: the bench of the option (seq/c*, calore_c*.txt: ~60 C), the
             same circuit (--serie2 R572,R576), at mains -10 / 0 / +10 %
  G / P / R  as fmea_l68.py; the arming artefact of limitations #85 (arm_pg_ms -13..) out
"""
import csv
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
sys.path.insert(0, QUI)
import parti_l68 as P  # noqa: E402

ARTEFATTO = "arm_pg_ms -13"
NUOVE = ("R588", "R589")
TOCCATE = ("R572", "R576") + NUOVE
CAMPI = ["gruppo", "lotto", "ref", "funzione", "modo", "caso", "scelta", "G_prima", "P_prima", "R_prima",
         "priorita_prima", "decisione", "adr", "rimedio", "effetto_dopo", "picco_dopo_V", "picco_dopo_dB",
         "stax_ms", "Tj_max_C", "G_dopo", "fit_modo", "P_dopo", "R_dopo", "priorita_dopo", "stato", "fonte_dopo"]


def priorita(g, p, r):
    if g == 5:
        return "alta"
    if r == 3:
        return {4: "alta", 3: "media"}.get(g, "bassa")
    if g == 4:
        return "media" if p == 1 else "alta"
    if g == 3:
        return "media" if p >= 3 else "bassa"
    return "bassa"


def it(x, nd=1):
    return ("%.*f" % (nd, x)).replace(".", ",")


AN = {r["caso"]: r for r in csv.DictReader(open(os.path.join(L, "an_sorgente.csv"), newline="", encoding="utf-8"))}
CONF = list(csv.DictReader(open(os.path.join(L, "confronto_sorgente.csv"), newline="", encoding="utf-8")))
CAL = {}
for r in csv.DictReader(open(os.path.join(L, "calore_5v.csv"), newline="", encoding="utf-8")):
    b = r["caso"].rsplit("_", 1)[0]
    if r["parte"].startswith("U504") and (b not in CAL or float(r["tj100_C"]) > float(CAL[b]["tj100_C"])):
        CAL[b] = r


def t(caso, ev, col):
    return float(AN["oggi/%s_%s" % (caso, ev)][col])


def eventi(caso):
    out = []
    for r in CONF:
        if r["caso"].startswith("oggi/%s_" % caso):
            d = [x for x in r["difetti"].split("; ") if x and not x.startswith(ARTEFATTO)]
            if d:
                out.append(r["evento"])
    return out


def controlla():
    """Every case of the timer other than the pull-ups' is L68's: verdicts and times."""
    male = [r["caso"] for r in CONF if r["caso"].startswith("oggi/")
            and not any(r["caso"].startswith("oggi/f_%s_" % x.lower()) for x in TOCCATE)
            and r["vs_l68"] not in ("",)]
    sani = [r["caso"] for r in CONF if r["caso"].startswith("sano/") and r["difetti"]]
    if male or sani:
        raise SystemExit("diversi da L68: %s; sani fuori: %s" % (male, sani))
    return sum(1 for r in CONF if r["caso"].startswith("oggi/"))


NSA = "non si accende: il mute resta inserito e la musica non parte, nessun colpo"


def righe():
    out = []
    for a, b in (("R572", "R588"), ("R588", "R572")):
        out.append((a, "aperto", "f_%s_aperto" % a.lower(), 2, 2,
                    "AT_MRQ senza pull-up (la catena R572 + R588 interrotta): da freddo non si accende; dallo standby "
                    "la musica a %s ms invece di 1209,3, dopo un buco a %s ms; il guadagno ~16 ms prima, col jack gia' "
                    "staccato (come R572 aperta di L68)"
                    % (it(t("f_%s_aperto" % a.lower(), "accs", "t_mus_ms")),
                       it(t("f_%s_aperto" % a.lower(), "b20s", "t_mus_ms")))))
        c = "f_%s_corto" % a.lower()
        out.append((a, "corto", c, 1, 3,
                    "l'altra meta' (%s, 100 kOhm) tiene AT_MRQ: come la corsa sana negli otto eventi, l'antirimbalzo "
                    "dimezzato (la musica a %s ms invece di 1209,3; dopo un buco di 20 ms a %s ms, criterio >= 500); "
                    "col rail - che cade la ritenuta tiene AT_ON a %s V e K501 si apre a %s ms (%s ms dopo il "
                    "permesso, >= 50); U504 %s W, %s C a calcolo; Q513 / Q514 ~60 C (il banco dell'opzione, ADR-116). "
                    "Il guasto non si vede: latente"
                    % (b, it(t(c, "accs", "t_mus_ms")), it(t(c, "b20s", "t_mus_ms")),
                       it(t(c, "guas", "on_min"), 2), it(t(c, "guas", "t_k501_ms")), it(t(c, "guas", "k_perm_ms")),
                       it(float(CAL[c]["p100_W"]), 2), it(float(CAL[c]["tj100_C"]), 0))))
    for a, b in (("R576", "R589"), ("R589", "R576")):
        out.append((a, "aperto", "f_%s_aperto" % a.lower(), 2, 2,
                    "AT_ON senza pull-up (la catena R576 + R589 interrotta): il frontale sempre spento: " + NSA +
                    " (come R576 aperta di L68)"))
        c = "f_%s_corto" % a.lower()
        out.append((a, "corto", c, 1, 3,
                    "l'altra meta' (%s, 4,99 kOhm) tiene AT_ON: come la corsa sana negli otto eventi; col rail - che "
                    "cade la ritenuta tiene AT_ON a %s V e K501 si apre a %s ms (%s ms dopo il permesso, >= 50); U504 "
                    "%s W, %s C a calcolo; Q513 / Q514 ~60 C (il banco dell'opzione, ADR-116). Il guasto non si vede: "
                    "latente"
                    % (b, it(t(c, "guas", "on_min"), 2), it(t(c, "guas", "t_k501_ms")), it(t(c, "guas", "k_perm_ms")),
                       it(float(CAL[c]["p100_W"]), 2), it(float(CAL[c]["tj100_C"]), 0))))
    return out


def main():
    n = controlla()
    out = []
    for ref, modo, caso, g, r, e in righe():
        ev = eventi(caso)
        if g == 1 and [x for x in ev if x not in ("accensione", "buco20", "fredda")]:
            raise SystemExit("%s %s: G 1 ma fuori dai criteri in %s" % (ref, modo, ev))
        if ev:
            e += " [eventi diversi dalla corsa sana: %s]" % ", ".join(ev)
        f = P.fit(ref, modo)
        p = P.classe_p(f)
        pr = priorita(g, p, r)
        tj = CAL.get(caso, {}).get("tj100_C", "") if modo == "corto" else ""
        out.append(dict(gruppo="temporizzatore (L68)", lotto="L69", ref=ref, funzione=P.FUNZ[ref], modo=modo,
                        caso=caso + "_*", scelta="", G_prima=g, P_prima=p, R_prima=r, priorita_prima=pr,
                        decisione="due meta' per pull-up (l'utente, 2026-11-04: «Due metà per pull-up»)",
                        adr="ADR-102 / ADR-116", rimedio="ADR-116: il pull-up in due meta' in serie",
                        effetto_dopo=e, picco_dopo_V="", picco_dopo_dB="", stax_ms="",
                        Tj_max_C="" if not tj else "%.0f" % float(tj), G_dopo=g, fit_modo=round(f, 3), P_dopo=p,
                        R_dopo=r, priorita_dopo=pr,
                        stato="misurata, nessun rimedio" if pr == "bassa" else "aperta",
                        fonte_dopo="data/2026-11-03/L69/ (an_sorgente.csv, confronto_sorgente.csv, calore_5v.csv; "
                                   "calore_piena.txt, il banco dell'opzione; %s)" % P.FONTE_CLASSE["R"]))
    keys = [(r["ref"], r["modo"], r["caso"]) for r in out]
    assert len(set(keys)) == len(keys)
    with open(os.path.join(L, "fmea_l69.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, CAMPI, lineterminator="\n")
        w.writeheader()
        w.writerows(out)
    for x in out:
        print("%-5s %-7s G%s P%s R%s %-6s %s" % (x["ref"], x["modo"], x["G_dopo"], x["P_dopo"], x["R_dopo"],
                                               x["priorita_dopo"], x["effetto_dopo"][:110]))
    print(len(out), "righe; le altre %d corse del temporizzatore uguali a L68" % (n - 8 * 8))
    return 0


if __name__ == "__main__":
    sys.exit(main())
