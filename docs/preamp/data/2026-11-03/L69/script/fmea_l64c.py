#!/usr/bin/env python3
"""L64c: le righe della FMEA che dicevano il micro, riscritte dalle corse del circuito di oggi (le colonne
di fmea_dopo.csv di L45d2b3b3, ADR-070). L'utente, 2026-11-03: «Riscriverle ora»; ADR-114.

Uso: /usr/bin/python3 -I fmea_l64c.py   -> fmea_l64c.csv qui accanto (L64c/), e stampa le righe

Le righe, ognuna al posto di quella con la stessa chiave (ref, modo, caso) in fmea_dopo.csv:
  - le dieci del sorvegliante dei rail accettate con ADR-073 (la riserva del firmware, superata da
    ADR-102): ognuna uguale a uno dei due canali ciechi per la tabella delle equivalenze del banco
    (psu/modi.py, «the supervisors»); le sequenze f_u505a_cieco_gu501 / f_u505b_cieco_gu502
    (an_l64c.csv, uguali a L64b) e il loro picco al jack (catena/tabella_l64c_ciechi.csv);
  - le sedici «letture del micro» di L45c2: R517, R518, R541, R542, C532, C533 (aperto, corto) contro
    l'accensione, lo spegnimento dal frontale e il mute dal frontale (an_l64c.csv, contro le corse
    sane di L64b: accensione, spegnimento_l, inserimento); R543 e R544-R547, uscite col micro;
  - C536 in corto e U512 spento (i 5 V persi), alle tre reti: an_l64c.csv, il picco al jack
    (catena/tabella_l64c.csv), il calore dei regolatori (calore_5v.csv).
La gravita' dal picco al jack con le soglie di ADR-070 (<= 100 uV: 1; <= 2 mV: 2; <= 0,87 V: 3), o 5 se
una parte supera la sua Tj max; la probabilita' resta quella della riga (il tasso del modo non
cambia); la rilevabilita' dal meccanismo (ADR-070); la priorita' dalla matrice.
Solo stdlib.
"""
import csv
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
DATA = os.path.abspath(os.path.join(L, "..", ".."))
FMEA = os.path.join(DATA, "2026-10-24", "L45d2b3b3", "fmea_dopo.csv")
AN_B = os.path.join(DATA, "2026-11-03", "L64b", "an_l64b.csv")
DB0, V0 = 33.45, 100e-6


def priorita(g, p, r):
    """La matrice di ADR-070 (come fmea_oggi.py)."""
    if g == 5:
        return "alta"
    if r == 3:
        return {4: "alta", 3: "media"}.get(g, "bassa")
    if g == 4:
        return "media" if p == 1 else "alta"
    if g == 3:
        return "media" if p >= 3 else "bassa"
    return "bassa"


def gravita_jack(v):
    return 1 if v <= 100e-6 else 2 if v <= 2e-3 else 3 if v <= 0.87 else 4


def db(v):
    import math
    return DB0 + 20 * math.log10(v / V0)


def it(x, nd=1):
    return ("%.*f" % (nd, x)).replace(".", ",")


def leggi(path, chiave="caso"):
    with open(path, newline="", encoding="utf-8") as f:
        return {r[chiave]: r for r in csv.DictReader(f)}


def ms(r, k):
    return float(r[k]) if r[k] not in ("", None) else None


def main():
    base = {(r["ref"], r["modo"], r["caso"]): r for r in csv.DictReader(open(FMEA, newline="", encoding="utf-8"))}
    an = leggi(os.path.join(L, "an_l64c.csv"))
    sano = leggi(AN_B)
    jack = {}
    for t in ("tabella_l64c.csv", "tabella_l64c_ciechi.csv"):
        for c, r in leggi(os.path.join(L, "catena", t)).items():
            jack[c] = float(r["picco_V"])
    if abs(jack["corto_u503"] - 0.006492) > 1e-6:
        raise SystemExit("la catena non ridà corto_u503 di L64b (6,492 mV): %g" % jack["corto_u503"])
    calore = {}
    for r in csv.DictReader(open(os.path.join(L, "calore_5v.csv"), newline="", encoding="utf-8")):
        k = r["caso"]
        if k not in calore or float(r["tj100_C"]) > float(calore[k]["tj100_C"]):
            calore[k] = r
    out = []

    def riga(key, **cambi):
        if key not in base:
            raise SystemExit("la chiave %r non e' in fmea_dopo.csv" % (key,))
        r = dict(base[key])
        r.update(cambi)
        g, p, rr = int(r["G_dopo"]), int(r["P_dopo"]), int(r["R_dopo"])
        r["priorita_dopo"] = priorita(g, p, rr)
        r["lotto"] = "L64c"
        out.append(r)

    # ---- 1. il sorvegliante dei rail: i due canali ciechi, e chi il banco dichiara uguale a loro
    cieco = {}
    for lato, caso, rail, ev in (("a", "f_u505a_cieco_gu501", "+", "U501"), ("b", "f_u505b_cieco_gu502", "-", "U502")):
        a = an["oggi/" + caso]
        if a["C2"] != "1" or a["C3"] != "1" or a["r41"] != "1" or a["s41"] != "1":
            raise SystemExit("%s: un criterio del temporizzatore non tiene" % caso)
        v = jack[caso]
        cieco[lato] = (v, "il canale %s cieco: col regolatore %s spento il temporizzatore stacca il jack a %s ms, "
                       "il guadagno a %s, K501 a %s ms; al jack %s µV (%s dB SPL di picco a 1 m)"
                       % ("+" if lato == "a" else "−", ev, it(ms(a, "t_jack_ms")), it(ms(a, "t_gain_ms")),
                          it(ms(a, "t_k501_ms")), it(v * 1e6, 1), it(db(v))))
    UGUALI = {("U505", "canale A cieco (uscita aperta), poi U501 spento"): "a",
              ("U505", "canale B cieco (uscita aperta), poi U502 spento"): "b",
              ("U505", "alimentazione (pin 8) aperta"): "ab",
              ("R506", "corto"): "a", ("R507", "aperto"): "a",
              ("C516", "corto"): "b", ("R508", "aperto"): "b", ("R505", "aperto"): "b",
              ("R509", "corto"): "b", ("R504", "corto"): "b"}
    for (ref, modo), lati in UGUALI.items():
        v = max(cieco[x][0] for x in lati)
        eff = "; ".join(cieco[x][1] for x in lati)
        riga((ref, modo, ""), G_dopo=str(gravita_jack(v)), effetto_dopo=eff,
             picco_dopo_V="%.4g" % v, picco_dopo_dB=it(db(v)).replace(",", "."),
             adr="ADR-073 / ADR-102", stato="misurata: la riserva e' il temporizzatore a comparatori (ADR-102), "
                                            "al jack sotto la soglia di V2",
             fonte_dopo="data/2026-11-03/L64c/ (an_l64c.csv %s; catena/tabella_l64c_ciechi.csv)"
                        % " / ".join({"a": "f_u505a_cieco_gu501", "b": "f_u505b_cieco_gu502"}[x] for x in lati))

    # ---- 2. gli ingressi del temporizzatore
    SANO = {"accs": "oggi/accensione", "spls": "oggi/spegnimento_l", "inss": "oggi/inserimento"}
    NOMI = {"accs": "l'accensione", "spls": "lo spegnimento dal frontale", "inss": "il mute dal frontale"}
    FUNZ = {"R517": "il pull-up di MUTE_SW, il tasto del mute (ingresso del temporizzatore, 100 kOhm)",
            "R518": "il pull-up di FRONT_SW, l'interruttore frontale (ingresso del temporizzatore, 100 kOhm)",
            "R541": "il polo d'ingresso del comparatore del frontale (1 kOhm)",
            "R542": "il polo d'ingresso del comparatore del tasto del mute (1 kOhm)",
            "C532": "il polo d'ingresso del comparatore del frontale (100 nF)",
            "C533": "il polo d'ingresso del comparatore del tasto del mute (100 nF)"}
    COL = ("musica_TE", "t_jack_ms", "t_gain_ms", "t_k501_ms", "t_mus_ms", "mus_end", "k501_end")
    for ref in FUNZ:
        for modo in ("aperto", "corto"):
            caso = "f_%s_%s" % (ref.lower(), modo)
            ev = {e: an["oggi/%s_%s" % (caso, e)] for e in SANO}
            s = {e: sano[SANO[e]] for e in SANO}
            diversi = {e: [k for k in COL if (ms(ev[e], k) is None) != (ms(s[e], k) is None)
                           or (ms(ev[e], k) is not None and abs(ms(ev[e], k) - ms(s[e], k)) > 0.15)]
                       for e in SANO}
            v5 = min(float(ev[e]["v5_min"]) for e in SANO)
            cal = max((calore["%s_%s" % (caso, e)] for e in SANO), key=lambda r: float(r["tj100_C"]))
            tj = float(cal["tj100_C"])
            if v5 < 1.0:
                g, r_ = (5 if tj > 125 else 2), 2
                eff = ("i 5 V a %s V attraverso l'interruttore chiuso: il temporizzatore non si alimenta, niente "
                       "musica, K501 aperto, nessun colpo; %s %s W, %s °C a calcolo (lo spegnimento termico "
                       "del regolatore a 150 °C)" % (it(v5, 3), cal["parte"].split()[0],
                                                       it(float(cal["p100_W"]), 2), it(tj, 0)))
                stato = ("accettata (ADR-114, come C536 in corto, ADR-097 punto 2): lo spegnimento termico "
                         "del regolatore" if g == 5 else "misurata")
            elif not any(diversi.values()):
                g, r_ = 1, int(base[(ref, modo, "")]["R_dopo"])
                eff = "come la corsa sana nei tre eventi (%s)" % ", ".join(NOMI.values())
                stato = "misurata, nessun rimedio"
            elif ev["inss"]["mus_end"] == "1" and s["inss"]["mus_end"] == "0" and not diversi["spls"]:
                g, r_ = 2, 2
                eff = ("il tasto del mute non inserisce il mute: la musica resta; l'accensione e lo spegnimento "
                       "dal frontale come la corsa sana")
                stato = "misurata: si vede (il tasto non risponde)"
            elif ev["spls"]["mus_end"] == "1" and s["spls"]["mus_end"] == "0":
                g, r_ = 2, 2
                eff = ("l'interruttore frontale non spegne: la musica resta e K501 resta chiuso; si accende con la "
                       "rete senza aspettare il frontale (l'ingresso letto chiuso da t = 0), con la sequenza "
                       "dell'accensione a freddo")
                stato = "misurata: si vede (il frontale non spegne)"
            else:
                g, r_ = 1, int(base[(ref, modo, "")]["R_dopo"])
                parti = []
                for e in SANO:
                    if diversi[e]:
                        parti.append("%s stacca il jack a %s ms invece di %s, il guadagno a %s invece di %s"
                                     % (NOMI[e], it(ms(ev[e], "t_jack_ms")), it(ms(s[e], "t_jack_ms")),
                                        it(ms(ev[e], "t_gain_ms")), it(ms(s[e], "t_gain_ms"))))
                eff = ("senza il polo il comando arriva prima: " + "; ".join(parti) + "; il resto come la corsa "
                       "sana; i rimbalzi dell'interruttore arrivano al comparatore senza il primo polo (non "
                       "corsi qui)")
                stato = "misurata, nessun rimedio"
            riga((ref, modo, ""), funzione=FUNZ[ref], G_dopo=str(g), R_dopo=str(r_), effetto_dopo=eff,
                 Tj_max_C="%.0f" % tj if tj > 61 else "", adr="ADR-102" + (" / ADR-114" if g == 5 else ""),
                 stato=stato, fonte_dopo="data/2026-11-03/L64c/ (an_l64c.csv %s_accs / _spls / _inss; "
                                         "calore_5v.csv)" % caso)
    for ref in ("R543", "R544-R547"):
        for modo in ("aperto", "corto"):
            riga((ref, modo, ""), G_dopo="1", P_dopo="1", R_dopo="1",
                 effetto_dopo="la parte non c'e' piu': e' uscita col microcontrollore (ADR-102)",
                 stato="esclusa: la parte non c'e' piu' (ADR-102)", adr="ADR-102",
                 fonte_dopo="circuits/preamp/psu.net (L64c: script/copertura.py)")
            out[-1]["priorita_dopo"] = "esclusa"
            for k in ("G_dopo", "P_dopo", "R_dopo"):
                out[-1][k] = ""

    # ---- 3. i 5 V persi
    for ref, modo, caso in (("C536", "corto", "f_c536_corto"), ("U512", "spento", "f_u512_spento")):
        casi = ["%s_%s" % (caso, e) for e in ("musm10s", "muss", "musp10s")]
        a = [an["oggi/" + c] for c in casi]
        v = max(jack[c] for c in casi)
        cal = max((calore[c] for c in casi), key=lambda r: float(r["tj100_C"]))
        tj = float(cal["tj100_C"])
        k = (ref, modo, caso)       # in fmea_dopo.csv queste due righe hanno il caso
        g_j = gravita_jack(v)
        g = max(g_j, 5 if tj > 125 else 0, int(base[k]["G_dopo"]) if tj > 125 else 0)
        eff = ("i 5 V persi (V5 al piu' basso %s V): il temporizzatore si spegne e i rele' cadono insieme, il "
               "guadagno a %s ms e il jack a %s (%s ms col jack collegato), K501 a %s ms; al jack %s mV (%s dB "
               "SPL di picco a 1 m), uguale alle tre reti, come U503 in corto; %s %s W, al piu' %s °C a calcolo"
               % (it(min(float(x["v5_min"]) for x in a), 3), it(ms(a[1], "t_gain_ms")), it(ms(a[1], "t_jack_ms")),
                  it(ms(a[1], "t_jack_ms") - ms(a[1], "t_gain_ms")), it(ms(a[1], "t_k501_ms")), it(v * 1e3, 2),
                  it(db(v)), cal["parte"].split()[0], it(float(cal["p100_W"]), 2), it(tj, 0)))
        stato = ("accettata (ADR-097, 2; ADR-114): lo spegnimento termico del regolatore; il colpo come U503 "
                 "in corto (ADR-051)" if tj > 125 else
                 "accettata (ADR-114): il colpo dei 5 V persi come U503 in corto (ADR-051)")
        riga(k, G_dopo=str(g), effetto_dopo=eff, picco_dopo_V="%.4g" % v, picco_dopo_dB="%.1f" % db(v),
             Tj_max_C="%.0f" % tj, adr="ADR-097 / ADR-114", stato=stato,
             fonte_dopo="data/2026-11-03/L64c/ (an_l64c.csv %s_*; catena/tabella_l64c.csv; calore_5v.csv)" % caso)

    with open(os.path.join(L, "fmea_l64c.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(next(iter(base.values()))), lineterminator="\n")
        w.writeheader()
        w.writerows(out)
    for r in out:
        print("%-10s %-48s %s -> %s  G%s P%s R%s  %s" % (r["ref"], r["modo"][:48], r["priorita_prima"] or "-",
                                                        r["priorita_dopo"], r["G_dopo"], r["P_dopo"], r["R_dopo"],
                                                        r["stato"][:50]))
    print(len(out), "righe")
    return 0


if __name__ == "__main__":
    sys.exit(main())
