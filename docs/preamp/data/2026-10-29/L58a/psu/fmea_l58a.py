#!/usr/bin/env python3
"""L58a2: the FMEA rows of the timer's new parts (R585, the four BAS416) in ADR-070's form, with the
columns of data/2026-10-24/L45d2b3b3/fmea_dopo.csv. Stdlib.

  G   from the effect measured on the seven events (confronto_l58a.csv, an_l58a.csv), and for D536
      from V2 at the power-up (v2/verdetto.csv); the worst event of the row
  P   from data/2026-10-14/L45c2/script/classi_l45c2.py: R 0.5 FIT (open 0.59, drift 0.36, short
      0.05), D_seg 1.0 FIT (drift 0.58, open 0.24, short 0.18). The leakage row of a BAS416 takes the
      drift share: no table gives a leakage mode (ADR-070, «Da riaprire se»: the assumption declared)
  R   from the mechanism (ADR-070: 1 the circuit sees it, 2 the listener sees it, 3 latent)
  priority from ADR-070's matrix

The jack in dB SPL from L54b2's anchor (3.52 uV = +4.4 dB SPL at 1 m, the chain of today).

Uso: fmea_l58a.py <out.csv>
"""
import csv
import math
import sys

FIT = {"R": (0.5, {"aperto": 0.59, "deriva": 0.36, "corto": 0.05}),
       "D_seg": (1.0, {"deriva": 0.58, "aperto": 0.24, "corto": 0.18})}


def dbspl(v):
    return round(4.4 + 20 * math.log10(v / 3.52e-6), 1)


def classe_p(fit):
    return 1 if fit < 1 else 2 if fit <= 10 else 3 if fit <= 100 else 4


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


FUNZ = {"R585": "la tenuta di AT_F verso il ritorno: l'innesco della ritenuta (ADR-103, 33 kOhm)",
        "D534": "BAS416: svuota AT_F verso AT_MD quando la rete manca (ADR-104)",
        "D535": "BAS416: disarma AT_T2S verso AT_MD quando la rete manca (ADR-104)",
        "D536": "BAS416: scarica C548 (AT_PGT) quando l'alimentazione buona cade (ADR-104)",
        "D541": "BAS416: disarma AT_T2S quando il frontale si spegne, verso AT_ON (ADR-104)"}
NON_SI_ACCENDE = ("nessun colpo: il mute resta inserito e i rail spenti o la musica non parte")
V_D536 = {"aperto": 2.631e-6, "corto": 2.748e-6}

# ref, mode key (FIT share), mode as written, caso, G, R, effect, source
RIGHE = [
    ("R585", "aperto", "aperto", "f_r585_aperto_*", 2, 2,
     "dalla rete col frontale acceso la ritenuta scatta all'accensione (base di Q513 0,898 V, ADR-103): "
     "non si accende; dallo standby si accende (musica a 1209,3 ms, come la base). "
     + NON_SI_ACCENDE, "an_l58a.csv, confronto_l58a.csv"),
    ("R585", "corto", "corto", "f_r585_corto_*", 4, 3,
     "AT_F a massa: nei sette eventi nessuna differenza finche' un rail non cade. Col rail - che cade in "
     "musica il mute si inserisce come oggi (jack 15,6 ms, dopo il guadagno e prima del rail) ma la "
     "ritenuta non scatta e K501 resta chiuso (oggi si apre a 129,1 ms e resta aperto fino al "
     "frontale); con un rail morto all'accensione lo stesso; col VRELAY_REG perso K501 si apre a 50 ms "
     "comunque. P9 (b) non rispettato (il toroidale resta acceso dopo un guasto con la rete presente). "
     "E' il «Da riaprire se» di ADR-102: il firmware lo copriva. In serie 2 x 16,5k o 3 x 11k il pezzo "
     "rimasto (16,5k / 22k) non fa scattare la ritenuta",
     "an_l58a.csv, an_r585_serie.csv"),
    ("R585", "deriva", "deriva a 2 x (66 kOhm)", "l58a_r585x2/*", 2, 2,
     "sui sette eventi nessun verdetto diverso; nell'angolo del comparatore a 2,2 V a 60 C la base di "
     "Q513 va a 1,06 V e la ritenuta scatta all'accensione a freddo: non si accende da freddo. "
     + NON_SI_ACCENDE, "an_l58a.csv, an_r585_66k.csv"),
    ("D534", "aperto", "aperto", "f_d534_aperto_*", 1, 3,
     "nessun verdetto diverso nei sette eventi", "an_l58a.csv"),
    ("D534", "corto", "corto", "f_d534_corto_*", 2, 2,
     "AT_F e AT_MD uniti (base di Q513 0,99 V): dallo standby non suona mai, dalla rete col frontale "
     "acceso la ritenuta scatta. " + NON_SI_ACCENDE, "an_l58a.csv"),
    ("D534", "deriva", "perdita 1 uA (IPOTESI)", "l58a_perdita_d534/*", 1, 3,
     "nessun verdetto diverso nei sette eventi", "an_l58a.csv"),
    ("D535", "aperto", "aperto", "f_d535_aperto_*", 1, 3,
     "nessun verdetto diverso nei sette eventi", "an_l58a.csv"),
    ("D535", "corto", "corto", "f_d535_corto_*", 2, 2,
     "AT_T2S e AT_MD uniti: la ritenuta scatta a ogni accensione (base 1,52-1,55 V), K501 aperto: non "
     "si accende. " + NON_SI_ACCENDE, "an_l58a.csv"),
    ("D535", "deriva", "perdita 1 uA (IPOTESI)", "l58a_perdita_d535/*", 2, 2,
     "dalla rete col frontale acceso la ritenuta si arma 70,7 ms prima dell'alimentazione buona e "
     "scatta: non si accende da freddo; dallo standby normale. " + NON_SI_ACCENDE,
     "an_l58a.csv, psu/armo.py"),
    ("D536", "aperto", "aperto", "f_d536_aperto_*", 2, 3,
     "C548 non si scarica: la musica all'alimentazione buona (537 ms dalla partenza dei rail, il + a "
     "13,57 V, invece di 1198 ms); dopo un buco di 20 ms 21,2 ms dopo la rete (criterio >= 500, ADR-104) "
     "su rail fermi; alla perdita di rete il guadagno cade a 263,8 ms invece di 54,9, dopo K501, ma il "
     "jack e' a 17,4 ms come oggi. Al jack (V2, rampe vere): %.2f uV, ~%.0f dB SPL a 1 m"
     % (V_D536["aperto"] * 1e6, dbspl(V_D536["aperto"])), "an_l58a.csv, v2/verdetto.csv"),
    ("D536", "corto", "corto", "f_d536_corto_*", 2, 3,
     "AT_PGT e AT_PG uniti: la musica a 616 ms dalla partenza dei rail (il + a 14,56 V); dopo un buco di "
     "20 ms 78,5 ms dopo la rete (criterio >= 500, ADR-104) su rail fermi. Al jack (V2): %.2f uV, ~%.0f "
     "dB SPL" % (V_D536["corto"] * 1e6, dbspl(V_D536["corto"])), "an_l58a.csv, v2/verdetto.csv"),
    ("D536", "deriva", "perdita 1 uA (IPOTESI)", "l58a_perdita_d536/*", 2, 3,
     "la musica dopo un buco di 20 ms a 462,2 ms dalla rete (criterio >= 500, ADR-104), su rail fermi; "
     "all'accensione 160 ms prima della base", "an_l58a.csv, psu/rail_rilascio.py"),
    ("D541", "aperto", "aperto", "f_d541_aperto_*", 1, 3,
     "nessun verdetto diverso; allo spegnimento dal frontale la base di Q513 sale a 0,540 V (0,471 V a "
     "60 C), la ritenuta non scatta: solo margine", "an_l58a.csv, an_t60_d541.csv"),
    ("D541", "corto", "corto", "f_d541_corto_*", 2, 2,
     "AT_T2S e AT_ON uniti: la ritenuta scatta a ogni accensione (base 2,5-2,8 V): non si accende. "
     + NON_SI_ACCENDE, "an_l58a.csv"),
    ("D541", "deriva", "perdita 1 uA (IPOTESI)", "l58a_perdita_d541/*", 2, 2,
     "come la perdita di D535: la ritenuta si arma 69,4 ms prima dell'alimentazione buona e scatta da "
     "freddo; dallo standby normale. " + NON_SI_ACCENDE, "an_l58a.csv, psu/armo.py"),
]

# the user's decision on a row, when there is one: (ref, mode) -> dict of the "dopo" columns
DECISIONI = {
    ("R585", "corto"): dict(
        decisione="accettato, dichiarato (l'utente, 2026-11-01: «Accettarlo, dichiarato»; NC-077 «Minore»)",
        adr="ADR-102 / ADR-103 / ADR-109", rimedio="nessuno: 4 x 10 kOhm in serie misurato agli angoli e "
        "non scelto (ADR-109)", stato="accettata in P9 (e), ADR-109; NC-077 minore",
        fonte_dopo="an_l58a.csv, an_r585_serie.csv, an_r585_66k.csv, an_r585_serie2.csv, "
        "an_r585_t0.csv, an_r585_rete.csv"),
}

CAMPI = ["gruppo", "lotto", "ref", "funzione", "modo", "caso", "scelta", "G_prima", "P_prima", "R_prima",
         "priorita_prima", "decisione", "adr", "rimedio", "effetto_dopo", "picco_dopo_V",
         "picco_dopo_dB", "stax_ms", "Tj_max_C", "G_dopo", "fit_modo", "P_dopo", "R_dopo",
         "priorita_dopo", "stato", "fonte_dopo"]

out = []
for ref, chiave, modo, caso, g, r, eff, fonte in RIGHE:
    fit_parte, quote = FIT["R" if ref == "R585" else "D_seg"]
    fit = round(fit_parte * quote[chiave], 3)
    p = classe_p(fit)
    pr = priorita(g, p, r)
    v = V_D536.get(chiave) if ref == "D536" else None
    riga = dict(gruppo="temporizzatore (L58a)", lotto="L58a2", ref=ref, funzione=FUNZ[ref], modo=modo,
                caso=caso, scelta="", G_prima=g, P_prima=p, R_prima=r, priorita_prima=pr,
                decisione="", adr="ADR-102 / ADR-103 / ADR-104 / ADR-105", rimedio="",
                effetto_dopo=eff, picco_dopo_V="" if v is None else "%.3g" % v,
                picco_dopo_dB="" if v is None else dbspl(v), stax_ms="", Tj_max_C="",
                G_dopo=g, fit_modo=fit, P_dopo=p, R_dopo=r, priorita_dopo=pr,
                stato="misurata, nessun rimedio" if pr == "bassa" else "aperta", fonte_dopo=fonte)
    riga.update(DECISIONI.get((ref, chiave), {}))
    out.append(riga)
with open(sys.argv[1], "w", newline="") as f:
    w = csv.DictWriter(f, CAMPI)
    w.writeheader()
    w.writerows(out)
for x in out:
    print("%-5s %-24s G%s P%s R%s %-6s fit %-6s %s" % (x["ref"], x["modo"], x["G_dopo"], x["P_dopo"],
                                                      x["R_dopo"], x["priorita_dopo"], x["fit_modo"],
                                                      x["stato"]))
