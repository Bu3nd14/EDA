#!/usr/bin/env python3
"""L58b (ADR-110): the FMEA rows of the diagnosis, in ADR-070's form, after this lot.

In:   the 46 rows of data/2026-10-24/L45d2b3b3/fmea_dopo.csv with the state «alla diagnosi» (ADR-071,
      ADR-076, ADR-078; ADR-100), the five rows of data/2026-10-29/L58a/fmea_alimentatore.csv the
      prompt names (R585 shorted, D536 open / shorted, D534 / D541 open), and the rows of the parts
      ADR-110 adds (Q509, R586, R587, and Q501's own modes inside the pair).
Out:  fmea_l58b.csv (this folder's parent), the columns of fmea_dopo.csv. G / P / R / priority after
      this lot with ADR-070's matrix (priorita(), copied from L58a's fmea_l58a.py), the effect
      as measured here, the state, the source.
The evidence, per group (this folder):
  standby   censimento_psu.csv (VRELAY at the audio board, K501 and the rails in standby)
  mute      censimento_psu.csv, v2/analisi.csv (the bump at the power-up), an_s1m.csv /
            an_s1m_rete.csv / cens_s1m.csv (the pair), an_sorg.csv (the pair on the source)
  block     censimento_blocco.csv (the DC at the output test point, the finals' quiescent)
Solo stdlib. /usr/bin/python3 -I fmea_l58b.py
"""
import csv
import os

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
DATA = os.path.abspath(os.path.join(L, "..", ".."))


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


def classe(fit):
    return 1 if fit < 1 else 2 if fit <= 10 else 3 if fit <= 100 else 4


ADR = "ADR-110"
FB = "censimento_blocco.csv"
# ---- the block (ADR-071): what a tester sees, block A (the same in the other positions, the file)
DC = {"Q117_ce": "+14,9 mV", "Q118_ce": "-15,1 mV", "Q148_be": "+44 mV", "R111_cc": "+226 mV",
      "R112_cc": "-225 mV", "R115_ap": "-74 mV"}
RIPOSO = {"C104_cc": "0 mA", "C105_cc": "0 mA", "D102_cc": "0 mA", "D103_cc": "0 mA", "Q125_be": "0 mA",
          "Q127_ce": "0 mA", "Q132_ae": "0 mA", "Q133_ae": "0 mA", "Q133_be": "9,5 mA",
          "R128_cc": "0 mA", "R130_ap": "0 mA", "R131_ap": "0 mA", "R134_ap": "0 mA",
          "R134_cc": "0 / 39,3 mA", "R135_cc": "39,3 / 0 mA"}
FUNZIONE = ("C137_cc", "R136_cc", "R143_ap")
NASCOSTI = {"R123_cc": "la resistenza del VAS: il blocco lavora, al tester niente (continua +1,3 mV, "
                       "riposo -0,3 mA)",
            "R144_cc": "meta' della cella RC: si perde rifiuto del rail +, al tester niente",
            "R147_ap": "l'inseguitore davanti al VAS spento: distorsione ad alta frequenza, al tester "
                       "+2,9 mV e -1,1 mA"}


def blocco(x):
    c = x["caso"]
    if c == "Q132_be":
        return dict(G=x["G_dopo"], R=2, stato="a L66 (NC-076): sul blocco di oggi l'uscita va al rail",
                    eff="sul blocco del sorgente l'uscita al rail (-13,6 V): non e' un degrado "
                        "silenzioso, il blocco non suona; la riga di L45 (0,053 V) e' del blocco di "
                        "prima: la rifa' L66 col VAS a 126 C (NC-076)")
    if c in DC:
        return dict(G=3, R=3, stato="accettata, con la procedura (DIAGNOSI.md, ADR-110)",
                    eff="la continua al test point d'uscita del blocco si sposta di %s (riposo dei "
                        "finali invariato): la vede il tester contro il valore annotato da nuovo"
                        % DC[c])
    if c in RIPOSO:
        return dict(G=3, R=3, stato="accettata, con la procedura (DIAGNOSI.md, ADR-110)",
                    eff="il riposo dei finali (sulle due 22 ohm) da 20,2 mA a %s: lo vede il tester "
                        "contro il valore annotato da nuovo" % RIPOSO[c])
    if c in FUNZIONE:
        return dict(G=3, R=2, stato="accettata, si sente (ADR-110)",
                    eff="la gamba del +10 dB del blocco B: col +10 dB il livello non sale (si sente); "
                        "nelle altre posizioni nessun effetto")
    if c in NASCOSTI:
        return dict(G=3, R=3, stato="accettata, dichiarata: non si vede (ADR-110)",
                    eff=NASCOSTI[c])
    raise SystemExit("blocco: %s senza decisione" % c)


def mute(x):
    m = x["modo"]
    if x["ref"] == "Q501":
        return dict(G=1, R=3, stato="rimediata, ADR-110 (Q501 in serie a Q509)",
                    eff="con la coppia in serie il guasto di Q501 lascia Q509 a staccare le bobine: "
                        "nei sette eventi e all'inserimento come la coppia sana, anche a rete "
                        "-10 / +10 %; per il colpo servono due guasti (an_s1m.csv, an_s1m_rete.csv)")
    if x["ref"] == "K2-K4":
        return dict(G=4, R=3, stato="accettata, dichiarata (l'utente, 2026-11-01: «si», coi dB; ADR-110)",
                    eff="come prima su quell'uscita; il segno: il mute non zittisce quell'uscita, e a "
                        "ogni accensione il jack prende la salita dei rail, principale 70 mV (~90 dB "
                        "SPL), fisse 0,64 / 0,66 V (~110 dB SPL), uguale a rete -10 / +10 % "
                        "(v2/analisi.csv, 100 kOhm sul jack)")
    raise SystemExit("mute: %s %s" % (x["ref"], m))


LED = ("Q505", "Q506", "R540", "R536", "R537", "U508")


def standby(x):
    if x["ref"] in LED:
        piu = (", e il toroidale acceso" if x["ref"] in ("R536", "R537", "U508") else "")
        quando = " dal primo spegnimento" if x["ref"] == "R536" else ""
        return dict(G=2, R=2, stato="si vede: i LED del frontale accesi in standby (ADR-110)",
                    eff="VRELAY a 12,0 V alla scheda audio in standby%s%s: i LED del frontale (mute, "
                        "guadagno, trim, ~2 mA ciascuno da VRELAY) restano accesi a frontale spento"
                        % (quando, piu))
    if x["ref"] in ("Q503", "K501"):
        return dict(G=2, R=3, stato="accettata, dichiarata (ADR-110)",
                    eff="il toroidale acceso in standby (i rail a +-15 V), VRELAY spento: LED spenti; "
                        "il solo segno, all'accensione dal frontale la musica a 17,4 ms invece di "
                        "1209 ms (K501 saldato = Q503 in corto, L45c2)")
    raise SystemExit("standby: %s" % x["ref"])


righe = []
for x in csv.DictReader(open(os.path.join(DATA, "2026-10-24", "L45d2b3b3", "fmea_dopo.csv"))):
    if "diagnosi" not in x["stato"]:
        continue
    adr = x["stato"]
    d = blocco(x) if "ADR-071" in adr else mute(x) if "ADR-076" in adr else standby(x)
    g, p, r = int(d["G"]), int(x["P_dopo"]), d["R"]
    y = dict(x)
    y.update(lotto="L58b", G_dopo=g, P_dopo=p, R_dopo=r, priorita_dopo=priorita(g, p, r),
             stato=d["stato"], effetto_dopo=d["eff"], adr=(x["adr"] + " / " + ADR).strip(" /"),
             decisione=y.get("decisione", ""),
             fonte_dopo="data/2026-11-01/L58b/ (%s)" % ("censimento_blocco.csv" if "ADR-071" in adr
                                                         else "censimento_psu.csv, v2/, an_s1m*.csv"))
    righe.append(y)
assert len(righe) == 46, len(righe)
campi = list(righe[0].keys())

# ---- L58a2's rows the prompt names
VUOTA = {k: "" for k in campi}
for x in csv.DictReader(open(os.path.join(DATA, "2026-10-29", "L58a", "fmea_alimentatore.csv"))):
    chiave = (x["ref"], x["modo"])
    if chiave == ("R585", "corto"):
        st, eff = ("accettata in P9 (e), ADR-109, NC-077 (invariata: l'utente, 2026-11-01, «R585 resta "
                   "com'era»)", "in funzionamento AT_F sta a ~0 V (0,007 V in standby e in musica, "
                   "l58b_sorg/accensione): il tester non lo vede; a scheda spenta R585 si misura con "
                   "l'ohmmetro (DIAGNOSI.md; la lettura in circuito da verificare sul prototipo)")
    elif chiave in (("D536", "aperto"), ("D536", "corto"), ("D534", "aperto"), ("D541", "aperto")):
        st, eff = x["stato"] + " (L58b: nessun segno, priorita' bassa)", x["effetto_dopo"]
    else:
        continue
    y = dict(VUOTA)
    y.update({k: x.get(k, "") for k in campi if k in x})
    y.update(lotto="L58b (da L58a2)", stato=st, effetto_dopo=eff)
    righe.append(y)

# ---- the parts of ADR-110 (FIT: L45c2's 2N7002, 3 FIT, and film resistor, 0,5 FIT, with FMD-2016's
# fractions as in fmea_comando.csv)
NUOVE = [
    ("Q501 (in serie)", "corto D-S", 1.89, 1, 3, "come la coppia sana (Q509 stacca), sette eventi + "
     "inserimento, rete -10 / +10 %", "f_q501a_corto_*"),
    ("Q501 (in serie)", "corto G-D", 0.15, 1, 3, "come la coppia sana: con 1 MOhm la corrente delle "
     "bobine che rientra in MUTE_G e' ~12 uA (con 10 kOhm il jack a 50 ms, dopo il guadagno: "
     "an_serie.csv)", "f_q501a_gd_*"),
    ("Q509", "corto D-S", 1.89, 1, 3, "come la coppia sana (Q501 stacca)", "f_q509_corto_*"),
    ("Q509", "corto G-D", 0.15, 2, 2, "la musica non arriva mai: l'apparecchio resta muto, nessun "
     "colpo", "f_q509_gd_*"),
    ("Q509", "aperto (D-S) / gate aperto", 0.3, 2, 2, "le bobine del mute non si eccitano: niente "
     "musica (= Q501 aperto, L45c2)", "calcolo"),
    ("R586", "aperto", 0.295, 1, 3, "come la coppia sana (il gate di Q501 resta dov'era; Q509 stacca)",
     "f_rq501g_aperto_*"),
    ("R586", "corto", 0.025, 1, 3, "il gate di Q501 su MUTE_G come oggi: conta solo con Q501 anche in "
     "corto G-D (due guasti)", "calcolo"),
    ("R587", "aperto", 0.295, 1, 3, "come la coppia sana", "f_rq509g_aperto_*"),
    ("R587", "corto", 0.025, 1, 3, "il gate di Q509 su MUTE_G: nessun effetto da solo", "calcolo"),
]
for ref, modo, fit, g, r, eff, caso in NUOVE:
    p = classe(fit)
    y = dict(VUOTA)
    y.update(gruppo="la coppia in serie (L58b)", lotto="L58b", ref=ref,
             funzione="il comando del jack (MUTE_CMD), ADR-110", modo=modo, caso=caso, adr=ADR,
             effetto_dopo=eff, G_dopo=g, fit_modo=fit, P_dopo=p, R_dopo=r,
             priorita_dopo=priorita(g, p, r), stato="misurata" if caso != "calcolo" else "calcolo",
             fonte_dopo="data/2026-11-01/L58b/ (an_s1m.csv, an_s1m_rete.csv, cens_s1m.csv)")
    righe.append(y)

with open(os.path.join(L, "fmea_l58b.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, campi)
    w.writeheader()
    w.writerows(righe)
conta = {}
for y in righe:
    conta[(y["lotto"].split()[0], y["priorita_dopo"])] = conta.get((y["lotto"].split()[0], y["priorita_dopo"]), 0) + 1
print("righe: %d" % len(righe))
for k in sorted(conta):
    print("  %s %s: %d" % (k[0], k[1], conta[k]))
for y in righe:
    print("%-16s %-34s G%s P%s R%s %-6s %s" % (y["ref"], y["modo"][:34], y["G_dopo"], y["P_dopo"],
                                             y["R_dopo"], y["priorita_dopo"], y["stato"][:60]))
