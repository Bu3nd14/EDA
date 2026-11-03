#!/usr/bin/env python3
"""L68: the FMEA rows of the comparator timer's own parts, its connectors and its test points (NC-078), in
ADR-070's form, with the columns of data/2026-10-24/L45d2b3b3/fmea_dopo.csv. Solo stdlib.

Uso: /usr/bin/python3 -I script/fmea_l68.py   -> fmea_l68.csv in L68/, and prints the rows

  G   from the effect measured (an_l68.csv, confronto_l68.csv against the healthy run of each event):
      1 nothing, or a time moved with the jack already open (catena/tabella_l68.csv, <= 100 uV);
      2 it does not switch on / a function lost and seen / the music released early on steady rails;
      3 the jack between 2 mV and 0,87 V; 4 the latch blind (K501 closed after a rail fault with the
      mains present: P9 (b), the case of R585 shorted, ADR-109); 5 a part beyond its Tj max
  P   from the rates (script/parti_l68.py); the test points have no rate: a probe that slips is a
      service event, taken as P 1 (declared)
  R   1 the circuit sees it, 2 the listener sees it, 3 latent (ADR-070)
  priority from ADR-070's matrix
The user's choices (2026-11-03, L68): the latch blind «Accettare come R585»; R572 / R576 shorted «Non
conformita' maggiore» (NC-079); the 5 V to ground «Accettare come C536»; the hits at the jack «Accettare
tutti» (ADR-115).
"""
import csv
import math
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
sys.path.insert(0, QUI)
import parti_l68 as P  # noqa: E402

DATA = os.path.abspath(os.path.join(L, "..", ".."))
FMEA_OGGI = os.path.join(DATA, "2026-11-03", "L64c", "fmea_oggi.csv")
DB0, V0 = 33.45, 100e-6
ARTEFATTO = "arm_pg_ms -13"          # limitations #85: AT_T2S a few nV above VREF at t = 0 in the fault decks


def priorita(g, p, r):
    """The matrix of ADR-070 (as fmea_oggi.py)."""
    if g == 5:
        return "alta"
    if r == 3:
        return {4: "alta", 3: "media"}.get(g, "bassa")
    if g == 4:
        return "media" if p == 1 else "alta"
    if g == 3:
        return "media" if p >= 3 else "bassa"
    return "bassa"


def db(v):
    return DB0 + 20 * math.log10(v / V0)


def it(x, nd=1):
    return ("%.*f" % (nd, x)).replace(".", ",")


def leggi(path, k="caso"):
    with open(path, newline="", encoding="utf-8") as f:
        return {r[k]: r for r in csv.DictReader(f)}


AN = leggi(os.path.join(L, "an_l68.csv"))
CONF = {}
for r in csv.DictReader(open(os.path.join(L, "confronto_l68.csv"), newline="", encoding="utf-8")):
    CONF.setdefault(r["caso"].rsplit("_", 1)[0], []).append(r)
JACK = {c: (float(r["picco_V"]), r["uscita"]) for c, r in leggi(os.path.join(L, "catena", "tabella_l68.csv")).items()
        if r["picco_V"] not in ("", "-")}
CAL = {}
for r in csv.DictReader(open(os.path.join(L, "calore_5v.csv"), newline="", encoding="utf-8")):
    b = r["caso"].rsplit("_", 1)[0]
    if b not in CAL or float(r["tj100_C"]) > float(CAL[b]["tj100_C"]):
        CAL[b] = r
if abs(JACK["corto_u503"][0] - 0.006492) > 1e-6:
    raise SystemExit("la catena non ridà corto_u503 di L64b (6,492 mV): %g" % JACK["corto_u503"][0])


def eventi(caso):
    """The events where the case differs from the healthy run (the arming artefact of limitations #85 out)."""
    out = []
    for r in CONF.get(caso, []):
        d = [x for x in r["difetti"].split("; ") if x and not x.startswith(ARTEFATTO)]
        if d:
            out.append(r["evento"])
    return out


def t(caso, ev, col):
    return AN["oggi/%s_%s" % (caso, ev)][col]


NSA = ("non si accende: il mute resta inserito e la musica non parte, nessun colpo")
RIT = ("la ritenuta cieca: senza un guasto di rail come la corsa sana; col rail che cade (in musica o morto "
       "all'accensione) il mute si inserisce come nella corsa sana e il jack resta muto, ma K501 resta chiuso: il "
       "toroidale acceso con la rete presente finche' non si spegne il frontale (P9 (b); il caso di R585 in "
       "corto, P9 (e))")
PRESTO = ("all'accensione la musica a %s ms dal frontale invece di 1209,3: all'alimentazione buona, senza il "
          "ritardo di 1,1 s (come D536 aperto, L58a: 537 ms, al jack 2,63 uV, ~2 dB SPL); dopo un buco di rete "
          "di 20 ms la musica %s ms dopo la rete (criterio >= 500, ADR-104) su rail fermi")
NULLA = "come la corsa sana negli otto eventi"
TEMPI_PERM = ("il permesso %s ms dopo il mute invece di ~40 (criterio >= 16,9, ADR-045): il guadagno si muove "
              "~12 ms dopo che il jack si e' staccato; al jack %s col rail - che cade, %s col mute dal frontale "
              "(catena)")

# (ref, modo, chiave FIT, caso, G, R, effetto, decisione)
RIGHE = []
CH = {"U513": ("rail +", "rail -", "VRELAY_REG", "rete presente"),
      "U514": ("ritardo dopo l'alimentazione buona", "tasto del mute", "MUTE_REQ", "PERMIT_REQ"),
      "U515": ("frontale", "MAINS_REQ, K501", "ritenuta non armata", "alimentazione buona")}
C_U513D = "f_u513d_cieco"
SPECIFICI_CIECO = {
    ("U513", "a"): (4, 3, RIT, "rit"), ("U513", "b"): (4, 3, RIT, "rit"),
    ("U513", "c"): (1, 3, NULLA + "; il canale vede solo VRELAY_REG sotto 11,0 V, e con VRELAY_REG perso i rele' "
                    "cadono e K501 si apre comunque (a 50 ms, L58a): nessun effetto da solo", None),
    ("U513", "d"): (2, 2, "dopo un buco di rete di 20 ms la musica %s ms dopo la rete (criterio >= 500, ADR-104) su "
                    "rail fermi (come D536 aperto, L58a); alla perdita di rete la ritenuta scatta: al ritorno della "
                    "rete resta spenta finche' non si spegne e riaccende il frontale (si vede)"
                    % it(float(t(C_U513D, "b20s", "dmus_ms"))), None),
    ("U514", "a"): (2, 3, PRESTO % (it(float(t("f_u514a_cieco", "accs", "t_mus_ms"))),
                                    it(float(t("f_u514a_cieco", "b20s", "dmus_ms")))), None),
    ("U514", "b"): (2, 2, "il tasto del mute non inserisce il mute; il resto come la corsa sana", None),
    ("U514", "c"): (2, 2, "il temporizzatore non chiede piu' il mute: il tasto del mute e il frontale non fermano la "
                    "musica (col frontale spento K501 resta chiuso); dopo un buco di 20 ms la musica 1,1 ms dopo la "
                    "rete; il sorvegliante dei rail e la rete persa mutano come nella corsa sana", None),
    ("U514", "d"): (4, 2, "il permesso sempre presente: in standby VRELAY e il toroidale restano accesi (i rail su), "
                    "dallo standby la musica %s ms dopo il frontale su rail fermi; col rail - che cade e allo "
                    "spegnimento dal frontale K501 resta chiuso. Si vede: lo standby non spegne"
                    % it(float(t("f_u514d_cieco", "accs", "t_mus_ms"))), "rit"),
    ("U515", "a"): (2, 2, "il frontale non spegne: acceso con la rete, suona gia' in standby; il sorvegliante e la "
                    "ritenuta come la corsa sana", None),
    ("U515", "b"): (4, 2, "K501 sempre chiuso: il toroidale acceso anche in standby (dallo standby la musica %s ms "
                    "dopo il frontale, su rail fermi); dopo un guasto di rail e allo spegnimento K501 resta chiuso. "
                    "Si vede: i rail accesi in standby" % it(float(t("f_u515b_cieco", "accs", "t_mus_ms"))), "rit"),
    ("U515", "c"): (2, 2, "la ritenuta scatta a ogni accensione: " + NSA, None),
    ("U515", "d"): (2, 2, "la ritenuta scatta quando si arma, ~2,2 s dopo il frontale: suona per ~1 s, poi il mute "
                    "si inserisce con la sequenza della ritenuta su rail fermi e K501 si apre, a ogni accensione",
                    None),
}
BASSI = {"U513": {"a": "f_u513pg_basso", "b": "f_u513pg_basso", "c": "f_u513pg_basso", "d": "f_u513d_basso"},
         "U514": {"a": "f_c549_corto", "b": "f_c549_corto", "c": "f_u514c_basso", "d": "f_u514d_basso"},
         "U515": {"a": "f_u515a_basso", "b": "f_u515b_basso", "c": "R585", "d": "R585"}}
for u in ("U513", "U514", "U515"):
    for i, ch in enumerate("abcd"):
        g, r, e, dec = SPECIFICI_CIECO[(u, ch)]
        RIGHE.append((u, "canale %s (%s): uscita aperta" % (ch.upper(), CH[u][i]), "cieco", "f_%s%s_cieco" % (u.lower(), ch),
                      g, r, e, dec))
    for i, ch in enumerate("abcd"):
        c = BASSI[u][ch]
        if c == "R585":
            RIGHE.append((u, "canale %s (%s): uscita bloccata bassa" % (ch.upper(), CH[u][i]), "basso",
                          "f_r585_corto_* (L58a)", 4, 3, "AT_F a massa, come R585 in corto (L58a2, an_l58a.csv): " + RIT,
                          "rit"))
        else:
            extra = " (la ritenuta scatta all'accensione)" if c in ("f_u513pg_basso", "f_u515b_basso") else ""
            RIGHE.append((u, "canale %s (%s): uscita bloccata bassa" % (ch.upper(), CH[u][i]), "basso", c, 2, 2,
                          NSA + extra, None))
RIGHE += [
    ("U513", "alimentazione persa (pin 3): le quattro uscite aperte (IPOTESI: il datasheet non dice)", "pin",
     "f_u513_alim", 4, 3, RIT + "; in piu' " + PRESTO % ("548,6", "1,1"), "rit"),
    ("U514", "alimentazione persa (pin 3): le quattro uscite aperte (IPOTESI: il datasheet non dice)", "pin",
     "f_u514_alim", 4, 2, "il temporizzatore non chiede piu' ne' il mute ne' lo spegnimento: in standby suona, il "
     "tasto del mute e il frontale non fermano la musica; dopo un guasto di rail il sorvegliante muta ma K501 resta "
     "chiuso. Si vede", "rit"),
    ("U515", "alimentazione persa (pin 3): le quattro uscite aperte (IPOTESI: il datasheet non dice)", "pin",
     "f_u515_alim", 2, 2, "la ritenuta scatta all'accensione: " + NSA, None),
    ("Q513", "corto C-E", "ce", "f_q513_ce", 2, 2, "la ritenuta tenuta da t = 0: " + NSA, None),
    ("Q513", "corto B-E", "be", "f_q513_be", 4, 3, RIT, "rit"),
    ("Q513", "collettore aperto", "aperto", "f_q513_aperto", 4, 3, RIT, "rit"),
    ("Q514", "corto C-E", "ce", "f_q514_ce", 2, 2, "la ritenuta tenuta da t = 0: " + NSA, None),
    ("Q514", "corto B-E", "be", "f_q514_be", 4, 3, RIT, "rit"),
    ("Q514", "collettore aperto", "aperto", "f_q514_aperto", 4, 3, RIT, "rit"),
    ("D533", "aperto", "aperto", "f_d533_aperto", 2, 3, "dopo un buco di rete di 20 ms la musica %s ms dopo la rete "
     "(criterio >= 500, ADR-104) su rail fermi, come D536 aperto (L58a); alla perdita di rete il guadagno a %s ms "
     "invece di 54,9, dopo il jack (17,4 ms come la corsa sana)"
     % (it(float(t("f_d533_aperto", "b20s", "dmus_ms"))), it(float(t("f_d533_aperto", "perds", "t_gain_ms")))), None),
    ("D533", "corto", "corto", "f_d533_corto", 4, 3, RIT, "rit"),
    ("D537", "aperto", "aperto", "f_d537_aperto", 2, 2, "il frontale spento non svuota AT_MRQ: la musica resta e K501 "
     "resta chiuso (il frontale non spegne); il resto come la corsa sana", None),
    ("D537", "corto", "corto", "f_d537_corto", 2, 2, NSA, None),
    ("D538", "aperto", "aperto", "f_d538_aperto", 2, 2, NSA, None),
    ("D538", "corto", "corto", "f_d538_corto", 1, 3, "PERMD538", None),
    ("D539", "aperto", "aperto", "f_d539_aperto", 1, 3, NULLA, None),
    ("D539", "corto", "corto", "f_d539_corto", 1, 3, "K501 si apre a %s ms dallo spegnimento dal frontale e a %s ms "
     "dal rail - che cade, prima del permesso (criterio >= 50 ms dopo, ADR-046), col jack gia' staccato: al jack "
     "JACK:f_d539_corto_guas col rail che cade, JACK:f_d539_corto_spls allo spegnimento (catena)"
     % (it(float(t("f_d539_corto", "spls", "t_k501_ms"))), it(float(t("f_d539_corto", "guas", "t_k501_ms")))), None),
    ("D540", "aperto", "aperto", "f_d540_aperto", 1, 3, "K501 a %s / %s ms invece di 122,5 / 129,1 (allo spegnimento "
     "e col rail che cade: %s / %s ms dopo il permesso, criterio >= 50, ADR-046), col jack gia' staccato: al jack "
     "JACK:f_d540_aperto_spls allo spegnimento (catena)"
     % (it(float(t("f_d540_aperto", "spls", "t_k501_ms"))), it(float(t("f_d540_aperto", "guas", "t_k501_ms"))),
        it(float(t("f_d540_aperto", "spls", "k_perm_ms"))), it(float(t("f_d540_aperto", "guas", "k_perm_ms")))), None),
    ("D540", "corto", "corto", "f_d540_corto", 2, 2, NSA, None),
]
for c in ("C545", "C546", "C547"):
    RIGHE += [(c, "aperto", "aperto", "calcolo", 1, 3, "il TLV1704 senza il suo 100 nF: i 5 V hanno C536 e gli altri "
               "due 100 nF vicini; il banco comportamentale non lo mostra (come C536 aperto): dal datasheet", None),
              (c, "corto", "corto", "f_c545_corto", 5, 2, "i 5 V a massa: U504 CAL:f_c545_corto; " + NSA, "5v")]
PERM_C550 = "PERM"
RIGHE += [
    ("C548", "aperto", "aperto", "f_c548_aperto", 2, 3, PRESTO % (it(float(t("f_c548_aperto", "accs", "t_mus_ms"))),
                                                                  it(float(t("f_c548_aperto", "b20s", "dmus_ms")))), None),
    ("C548", "corto", "corto", "f_c548_corto", 2, 2, NSA, None),
    ("C549", "aperto", "aperto", "f_c549_aperto", 1, 3, "la musica %s ms dal frontale invece di 1209,3; il tasto del "
     "mute senza il suo antirimbalzo (i rimbalzi non corsi qui)" % it(float(t("f_c549_aperto", "accs", "t_mus_ms"))),
     None),
    ("C549", "corto", "corto", "f_c549_corto", 2, 2, NSA, None),
    ("C550", "aperto", "aperto", "f_c550_aperto", 1, 3, PERM_C550, None),
    ("C550", "corto", "corto", "f_c550_corto", 2, 2, NSA, None),
    ("C551", "aperto", "aperto", "f_c551_aperto", 1, 3, "K501 a %s / %s ms invece di 122,5 / 129,1 (%s / %s ms dopo "
     "il permesso, criterio >= 50, ADR-046), col jack gia' staccato: al jack JACK:f_c551_aperto_spls allo "
     "spegnimento (catena)" % (it(float(t("f_c551_aperto", "spls", "t_k501_ms"))),
                              it(float(t("f_c551_aperto", "guas", "t_k501_ms"))),
                              it(float(t("f_c551_aperto", "spls", "k_perm_ms"))),
                              it(float(t("f_c551_aperto", "guas", "k_perm_ms")))), None),
    ("C551", "corto", "corto", "f_c551_corto", 2, 2, NSA, None),
    ("C552", "aperto", "aperto", "f_c552_aperto", 2, 2, "la ritenuta scatta a ogni accensione: " + NSA, None),
    ("C552", "corto", "corto", "f_c552_corto", 4, 3, RIT, "rit"),
    ("C553", "aperto", "aperto", "f_c553_aperto", 1, 3, "solo margine: la base di Q513 a %s V dopo un buco e alla "
     "perdita di rete (criterio <= 0,45 V, ADR-103), la ritenuta non scatta (come D541 aperto, L58a)"
     % it(float(t("f_c553_aperto", "perds", "bn_max")), 3), None),
    ("C553", "corto", "corto", "f_r585_corto_* (L58a)", 4, 3, "AT_F a massa, come R585 in corto (L58a2): " + RIT, "rit"),
    ("C554", "aperto", "aperto", "f_c554_aperto", 1, 3, NULLA + "; il condensatore tiene la ritenuta contro i fronti "
     "veloci, che questi eventi non hanno (dichiarato)", None),
    ("C554", "corto", "corto", "f_q513_be", 4, 3, "base-emettitore di Q513 in corto: " + RIT, "rit"),
    ("C555", "aperto", "aperto", "f_c555_aperto", 1, 3, NULLA + "; il condensatore tiene la ritenuta contro i fronti "
     "veloci, che questi eventi non hanno (dichiarato)", None),
    ("C555", "corto", "corto", "f_q514_be", 4, 3, "base-emettitore di Q514 in corto: " + RIT, "rit"),
    ("R569", "aperto", "aperto", "f_r569_aperto", 4, 3, "AT_MD senza pull-up: all'accensione con un rail morto la "
     "ritenuta non scatta: " + RIT, "rit"),
    ("R569", "corto", "corto", "f_r569_corto", 2, 2, "AT_MD sui 5 V: la rete sempre presente per il temporizzatore. "
     + SPECIFICI_CIECO[("U513", "d")][2], None),
    ("R570", "aperto", "aperto", "f_r570_aperto", 1, 3, NULLA + " (la musica dopo un buco 8 ms dopo)", None),
    ("R570", "corto", "corto", "f_r570_corto", 4, 3, "AT_PG sui 5 V: l'alimentazione sempre buona. " + RIT + "; in "
     "piu' " + PRESTO % ("548,6", "1,1") + "; U504 CAL:f_r570_corto; i canali di U513 che tirano giu' AT_PG "
     "sui 5 V, al piu' 3 x 5 V x 20 mA (SBOS589D), 0,3 W, 98 C con 128,1 C/W: dentro i 150 C", "rit"),
    ("R571", "aperto", "aperto", "f_r571_aperto", 2, 2, NSA, None),
    ("R571", "corto", "corto", "f_r571_corto", 4, 3, "AT_PGT sui 5 V, che attraverso D536 tiene alta AT_PG: " + RIT +
     "; in piu' " + PRESTO % ("548,6", "1,1"), "rit"),
    ("R572", "aperto", "aperto", "f_r572_aperto", 2, 2, "AT_MRQ senza pull-up: da freddo non si accende; dallo "
     "standby la musica a %s ms invece di 1209,3, dopo un buco a %s ms; il guadagno ~16 ms prima, col jack gia' "
     "staccato" % (it(float(t("f_r572_aperto", "accs", "t_mus_ms"))), it(float(t("f_r572_aperto", "b20s", "t_mus_ms")))),
     None),
    ("R572", "corto", "corto", "f_r572_corto", 5, 2, "AT_MRQ sui 5 V: il tasto del mute e il frontale non fermano la "
     "musica (si vede); dopo un buco la musica 1,1 ms dopo la rete. Col rail - che cade la ritenuta scatta e, "
     "attraverso D537, tiene i 5 V a massa: 0,25 A (il limite di U504), U504 CAL:f_r572_corto; Q513 ~0,37 W, ~209 C "
     "con 403 C/W (Diodes DS11108; Tj max 150 C) e 0,25 A di emettitore contro i 200 mA di picco; la musica torna "
     "per un istante (a %s ms) e il mute si reinserisce; al jack JACK:f_r572_corto_guas (catena)"
     % it(float(t("f_r572_corto", "guas", "t_mus_ms"))), "nc079"),
    ("R573", "aperto", "aperto", "f_r573_aperto", 2, 2, NSA, None),
    ("R573", "corto", "corto", "f_r573_corto", 4, 2, "MUTE_REQ sui 5 V: il temporizzatore non chiede piu' il mute: il "
     "tasto e il frontale non fermano la musica (si vede); col rail - che cade il sorvegliante muta ma K501 resta "
     "chiuso; U504 CAL:f_r573_corto", "rit"),
    ("R574", "aperto", "aperto", "f_r574_aperto", 4, 3, "AT_PRT non si scarica: il permesso resta; dopo un guasto di "
     "rail e allo spegnimento dal frontale K501 resta chiuso (il toroidale acceso in standby)", "rit"),
    ("R574", "corto", "corto", "f_c550_corto", 2, 2, NSA, None),
    ("R575", "aperto", "aperto", "f_r575_aperto", 2, 2, NSA, None),
    ("R575", "corto", "corto", "f_r575_corto", 4, 2, "PERMIT_REQ sui 5 V: " + SPECIFICI_CIECO[("U514", "d")][2], "rit"),
    ("R576", "aperto", "aperto", "f_r576_aperto", 2, 2, "AT_ON senza pull-up: il frontale sempre spento: " + NSA, None),
    ("R576", "corto", "corto", "f_r576_corto", 5, 2, "AT_ON sui 5 V: il frontale non spegne (si vede). Col rail - che "
     "cade, o all'accensione con un rail morto, la ritenuta scatta e tiene i 5 V a massa: 0,25 A (il limite di "
     "U504), U504 CAL:f_r576_corto; Q513 ~0,37 W, ~209 C con 403 C/W (Diodes DS11108; Tj max 150 C) e 0,25 A di "
     "emettitore contro i 200 mA di picco; K501 a %s ms dal rail che cade, prima del permesso; al jack "
     "JACK:f_r576_corto_guas (catena)" % it(float(t("f_r576_corto", "guas", "t_k501_ms"))), "nc079"),
    ("R577", "aperto", "aperto", "f_r577_aperto", 1, 3, NULLA + " (K501 tenuto da D540, VR_G)", None),
    ("R577", "corto", "corto", "f_r577_corto", 1, 3, NULLA, None),
    ("R578", "aperto", "aperto", "f_r578_aperto", 4, 3, "AT_MT non si scarica: K501 resta chiuso dopo un guasto di "
     "rail, allo spegnimento dal frontale e all'accensione con un rail morto", "rit"),
    ("R578", "corto", "corto", "f_c551_corto", 2, 2, NSA, None),
    ("R579", "aperto", "aperto", "f_r579_aperto", 2, 2, "la ritenuta scatta all'accensione: " + NSA, None),
    ("R579", "corto", "corto", "f_r579_corto", 4, 2, "MAINS_REQ sui 5 V: " + SPECIFICI_CIECO[("U515", "b")][2], "rit"),
    ("R580", "aperto", "aperto", "f_r580_aperto", 4, 3, "AT_T2S mai armata: " + RIT, "rit"),
    ("R580", "corto", "corto", "f_r580_corto", 2, 2, "la ritenuta armata subito, scatta all'accensione: " + NSA, None),
    ("R581", "aperto", "aperto", "f_r581_aperto", 4, 3, "AT_F senza pull-up: " + RIT, "rit"),
    ("R581", "corto", "corto", "f_r581_corto", 2, 2, "AT_F sui 5 V, la ritenuta scatta all'accensione: " + NSA +
     "; U504 CAL:f_r581_corto", None),
    ("R582", "aperto", "aperto", "f_r582_aperto", 4, 3, "la base di Q513 staccata da AT_F: " + RIT, "rit"),
    ("R582", "corto", "corto", "f_r582_corto", 4, 3, "AT_F sulla base di Q513, tenuta a una V_BE: " + RIT, "rit"),
    ("R583", "aperto", "aperto", "f_r583_aperto", 1, 3, "solo margine: la base di Q513 a %s V prima dell'evento "
     "(criterio <= 0,45 V, ADR-103), la ritenuta non scatta" % it(float(t("f_r583_aperto", "accs", "bn_max0")), 3), None),
    ("R583", "corto", "corto", "f_q513_be", 4, 3, "base-emettitore di Q513 in corto: " + RIT, "rit"),
    ("R584", "aperto", "aperto", "f_r584_aperto", 1, 3, NULLA, None),
    ("R584", "corto", "corto", "f_q514_be", 4, 3, "base-emettitore di Q514 in corto: " + RIT, "rit"),
]
# ---- the connectors: one row per pin
RIGHE += [
    ("J4", "pin 1 (MUTE_CMD) aperto", "aperto", "f_j4mute_aperto", 2, 2, "le bobine del mute staccate: in musica il "
     "jack si stacca a 3,1 ms e resta staccato (il guadagno fermo), al jack JACK:f_j4mute_aperto_muss (catena); "
     "all'accensione non suona", None),
    ("J4", "pin 2 (PERMIT_CMD) aperto", "aperto", "f_j4permit_aperto", 3, 2, "le bobine del permesso staccate: in "
     "musica i rele' del guadagno cadono col jack collegato, al jack JACK:f_j4permit_aperto_muss (catena, come U503 "
     "in corto); la musica resta, col guadagno a riposo", "colpo"),
    ("J4", "pin 3 (MUTE_SW) aperto", "aperto", "f_j4sw_aperto", 2, 2, "il tasto del mute staccato e' letto in mute: "
     "in musica il mute si inserisce con la sequenza sana (il jack a 10,3 ms, il guadagno a 47,4), poi non suona "
     "piu'", None),
    ("J508", "pin 1 (FRONT_SW) aperto", "aperto", "f_j508_aperto", 2, 2, "il frontale staccato e' letto spento: in "
     "musica si spegne con la sequenza sana (il jack a 10,3 ms, K501 a 122,5), poi non si accende", None),
    ("J508", "pin 2 (RLY_RET) aperto", "aperto", "f_j508_aperto", 2, 2, "come il pin 1: il frontale letto spento",
     None),
]
for pin in ("L", "N"):
    RIGHE += [
        ("J510", "pin %s aperto" % pin, "aperto", "perdita (L64b)", 2, 2, "la rete persa: la sequenza sana della "
         "perdita di rete (data/2026-11-03/L64b/an_l64b.csv, perdita: il jack a 17,4 ms, il guadagno a 54,9, K501 a "
         "221,6); latente: non si accende", None),
        ("J511", "pin %s aperto" % pin, "aperto", "T2", None, None, "T2", None),
        ("J512", "pin %s aperto" % pin, "aperto", "f_tp514_corto", 1, 2, "il toroidale staccato in musica, come K501 "
         "che si apre (MAINS_G a massa, f_tp514_corto_muss): i rail cadono, il sorvegliante muta (il jack a 82,4 ms), "
         "la ritenuta scatta; al jack JACK:f_tp514_corto_muss (catena); latente: non si accende", None),
    ]
# ---- the test points (ADR-107): a probe that slips onto the reference next to it, in music
for tp, net in P.TP.items():
    if net in ("GND", "RLY_RET"):
        RIGHE.append((tp, "corto verso la massa vicina", None, "-", 1, 1, "nessun effetto: e' il riferimento stesso "
                      "(%s)" % net, None))
TPR = {
    "TP501": (3, 2, "il rail + a massa: la corsa della catena si ferma 4 ms dopo il corto («timestep too small», il "
                    "rail che crolla); per simmetria come TP502 (0,15 V all'uscita fissa 1, 97,0 dB SPL): DICHIARATO, "
                    "non misurato. Sull'alimentatore il sorvegliante muta a 3,1 ms e la ritenuta scatta; la riga "
                    "«U501 uscita a massa (interno)» ha gli stessi due nodi", "colpo"),
    "TP502": (3, 2, "il rail - a massa: il sorvegliante muta a 3,1 ms, la ritenuta scatta, K501 a 116,4 ms; al jack "
                    "JACK:f_tp502_corto_muss (catena)", "colpo"),
    "TP504": (3, 2, "VRELAY a massa: tutti i rele' cadono insieme (il guadagno a 0,1 ms, il jack a 3,1), K501 si "
                    "apre; al jack JACK:f_tp504_corto_muss (catena), come U503 in corto: il corto della linea a 12 V "
                    "dei rele' di ADR-051", "colpo"),
    "TP505": (3, 2, "VRELAY_REG a massa: come TP504; al jack JACK:f_tp505_corto_muss (catena)", "colpo"),
    "TP507": (5, 2, "i 5 V a massa in musica: i rele' cadono insieme, al jack JACK:f_tp507_corto_muss (catena); U504 "
                    "CAL:f_tp507_corto, U512 1,16 W, 132 C (come C536 in corto)", "5v"),
    "TP508": (2, 2, "MUTE_G a massa: il mute si inserisce (il jack a 3,1 ms) e resta finche' dura il corto", None),
    "TP509": (3, 2, "PERMIT_G a massa: i rele' del guadagno cadono a 0,1 ms, prima del jack (3,1 ms); al jack "
                    "JACK:f_tp509_corto_muss (catena)", "colpo"),
    "TP510": (3, 2, "PERMIT_T a massa: come TP509; al jack JACK:f_tp510_corto_muss (catena)", "colpo"),
    "TP512": (1, 1, "MUTE_CMD a massa: le bobine del mute gia' eccitate in musica; " + NULLA.replace("otto eventi",
                    "evento in musica"), None),
    "TP513": (1, 1, "PERMIT_CMD a massa: le bobine del permesso gia' eccitate in musica; come la corsa sana", None),
    "TP514": (1, 2, "MAINS_G a massa: K501 si apre in musica, i rail cadono, il sorvegliante muta (il jack a 82,4 "
                    "ms), la ritenuta scatta; al jack JACK:f_tp514_corto_muss (catena)", None),
    "TP515": (1, 1, "MAINS_COIL a massa: la bobina di K501 gia' eccitata in musica; come la corsa sana", None),
    "TP516": (3, 2, "VR_G a massa: il guadagno a 19,0 ms, prima del jack (23,3 ms); al jack JACK:f_tp516_corto_muss "
                    "(catena)", "colpo"),
}
for tp, (g, r, e, dec) in TPR.items():
    RIGHE.append((tp, "corto verso la massa vicina (la sonda che scivola)", None, "f_%s_corto" % tp.lower(), g, r, e, dec))

DECISIONI = {
    "rit": dict(decisione="accettato come R585 in corto (l'utente, 2026-11-03: «Accettare come R585»)",
                adr="ADR-102 / ADR-109 / ADR-115", stato="accettata in P9 (e), come R585 in corto (ADR-115)"),
    "5v": dict(decisione="accettato come C536 (l'utente, 2026-11-03: «Accettare come C536»)",
               adr="ADR-097 / ADR-114 / ADR-115", stato="accettata (ADR-115, come C536 in corto, ADR-114): lo "
               "spegnimento termico del regolatore"),
    "nc079": dict(decisione="non conformita' maggiore (l'utente, 2026-11-03: «Non conformità maggiore»)",
                  adr="ADR-102", stato="NC-079 (maggiore, prima di G1)"),
    "colpo": dict(decisione="accettato (l'utente, 2026-11-03: «Accettare tutti»)", adr="ADR-051 / ADR-115",
                  stato="accettata (ADR-115): sotto il tetto di 0,87 V, sopra l'obiettivo"),
}
CAMPI = ["gruppo", "lotto", "ref", "funzione", "modo", "caso", "scelta", "G_prima", "P_prima", "R_prima",
         "priorita_prima", "decisione", "adr", "rimedio", "effetto_dopo", "picco_dopo_V", "picco_dopo_dB",
         "stax_ms", "Tj_max_C", "G_dopo", "fit_modo", "P_dopo", "R_dopo", "priorita_dopo", "stato", "fonte_dopo"]


def espandi(e):
    """JACK:<caso> -> the peak at the jack in uV / mV and dB SPL; CAL:<caso> -> the regulator's W and C."""
    picchi, tj = [], []
    out = []
    for w in e.split(" "):
        tail = ""
        while w and w[-1] in ",;:)":
            tail = w[-1] + tail
            w = w[:-1]
        if w.startswith("JACK:"):
            v, usc = JACK[w[5:]]
            picchi.append(v)
            s = ("%s nV" % it(v * 1e9, 1)) if v < 1e-6 else ("%s uV" % it(v * 1e6, 1)) if v < 1e-3 else ("%s mV" % it(v * 1e3, 2)) if v < 0.1 else "%s V" % it(v, 2)
            w = "%s (%s dB SPL%s)" % (s, it(db(v)), "" if usc == "MAINJACK" else ", " + usc)
        elif w.startswith("CAL:"):
            r = CAL[w[4:]]
            tj.append(float(r["tj100_C"]))
            w = "%s W, %s C a calcolo" % (it(float(r["p100_W"]), 2), it(float(r["tj100_C"]), 0))
        out.append(w + tail)
    return " ".join(out), (max(picchi) if picchi else None), (max(tj) if tj else None)


def main():
    t2 = [r for r in csv.DictReader(open(FMEA_OGGI, newline="", encoding="utf-8"))
          if r["ref"] == "T2" and r["modo"].startswith("secondario aperto")]
    assert len(t2) == 1, t2
    t2 = t2[0]
    perm = TEMPI_PERM % ("15,4-15,9", "JACK:f_c550_aperto_guas", "JACK:f_c550_aperto_inss")
    out = []
    for ref, modo, chiave, caso, g, r, e, dec in RIGHE:
        if e == "T2":
            g, r = int(t2["G_dopo"]), int(t2["R_dopo"])
            e = "il primario di T2 aperto: come la riga di T2 «%s» (%s)" % (t2["modo"], t2["effetto_dopo"])
        if e == "PERM":
            e = perm
        if e == "PERMD538":
            # the same instants as C550 open in every event (confronto_l68.csv): its chain run stands for both
            e = perm.replace("(catena)", "(la catena di C550 aperto, che ha gli stessi istanti)")
        e, v, tjc = espandi(e)
        ev = eventi(caso) if caso.startswith("f_") else []
        if ev:
            e += " [eventi diversi dalla corsa sana: %s]" % ", ".join(ev)
        f = P.fit(ref, chiave) if chiave else None
        if f is not None and ref.startswith("U") and modo.startswith("canale") and "bloccata" in modo:
            f = P.fit(ref, "basso")
        p = P.classe_p(f) if f is not None else 1
        if g == 3 and v is not None and v > 0.87:
            raise SystemExit("%s %s: sopra il tetto" % (ref, modo))
        pr = priorita(g, p, r)
        cl = P.classe(ref)
        riga = dict(gruppo="temporizzatore (L68)", lotto="L68", ref=ref, funzione=P.FUNZ[ref], modo=modo,
                    caso=caso + ("_*" if caso.startswith("f_") and not caso.endswith("*") else ""), scelta="",
                    G_prima=g, P_prima=p, R_prima=r, priorita_prima=pr, decisione="",
                    adr="ADR-102 / ADR-105 / ADR-108", rimedio="", effetto_dopo=e,
                    picco_dopo_V="" if v is None else "%.4g" % v, picco_dopo_dB="" if v is None else "%.1f" % db(v),
                    stax_ms="", Tj_max_C="" if tjc is None else "%.0f" % tjc, G_dopo=g,
                    fit_modo="" if f is None else round(f, 3), P_dopo=p, R_dopo=r, priorita_dopo=pr,
                    stato="misurata, nessun rimedio" if pr == "bassa" else "aperta",
                    fonte_dopo="data/2026-11-03/L68/ (an_l68.csv, confronto_l68.csv%s%s; %s)"
                    % (", catena/tabella_l68.csv" if v is not None else "", ", calore_5v.csv" if tjc is not None else "",
                       P.FONTE_CLASSE[cl] if cl else "test point: nessun tasso, la sonda che scivola presa a P 1"))
        if caso == "calcolo":
            riga["fonte_dopo"] = "datasheet TLV1704 (SBOS589D); " + P.FONTE_CLASSE[cl]
        if dec:
            riga.update(DECISIONI[dec])
        out.append(riga)
    keys = [(r["ref"], r["modo"], r["caso"]) for r in out]
    assert len(set(keys)) == len(keys), "chiavi ripetute"
    with open(os.path.join(L, "fmea_l68.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, CAMPI, lineterminator="\n")
        w.writeheader()
        w.writerows(out)
    import collections
    for x in out:
        print("%-5s %-60s G%s P%s R%s %-6s %s" % (x["ref"], x["modo"][:60], x["G_dopo"], x["P_dopo"], x["R_dopo"],
                                                x["priorita_dopo"], x["stato"][:45]))
    c = collections.Counter(x["priorita_dopo"] for x in out)
    print(len(out), "righe:", dict(c), "| ritenuta cieca accettata:",
          sum(1 for x in out if x["stato"].startswith("accettata in P9 (e)")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
