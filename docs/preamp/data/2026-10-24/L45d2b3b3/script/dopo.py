#!/usr/bin/env python3
"""L45d2b3b3: the FMEA of NC-042 AFTER the remedies, row by row, in the form of ADR-070. Solo stdlib,
/usr/bin/python3 -I. No new run: every figure is read from a published CSV, named in 'fonte'.

    dopo.py     -> ../fmea_dopo.csv  (and prints the counts; sintesi_dopo.py writes the .md)

THE ROWS
  A. the 469 classified rows of L45d1/fmea_sintesi.csv (the four tables), with L45d2a's decision
     (decisioni.csv, 173 rows) and, where L45d2b3b1 redid them, righe_b1.csv (97 rows);
  B. NEW rows: the modes of the parts added after L45 that the benches have run - the block's
     D154-D159, R150-R153, R160 (ADR-086/087/090/095/097, L45d2b3b1), the five of ADR-099 (heat of
     L45d2b3b2b2, Stax of this lot: p10_stax_nuove.csv), the supply's parts of ADR-093 / ADR-094
     (L45d2b2b2, L45d2b3b1) -; and, marked 'calcolo', the supply modes no bench has run.

THE COLUMNS AFTER THE REMEDY (regole.py; verifica.py proves the rules on the published columns)
  - Block rows (L45a and the new block parts): heat and jack from the latest bench that ran the mode
    - the source block (L45d2b3b2b2, ADR-099: sintesi_sorg, the VAS also sintesi_sorgt60, the
    output pair's shorts dissipatore.csv), else the block of ADR-097 (sintesi_calore_dopo097), else
    L45d2b3b1's block (sintesi_calore); the Stax from the latest run of the case (this lot's
    p10_stax_nuove, then L45d2b3b2b2/stax_lunghi, then L45d2b3b1 stax_lunghi / p10_stax_dopo097 /
    p10_stax). G from regole.g_blocco; C145 shorted is NC-075's impulse (ADR-097, 3): 5.
  - P: unchanged for an existing row (the part and its instances are the same: a remedy that splits
    a resistor adds a part, with its own row); for a new row from tipi.TIPI.
  - R: unchanged for an existing row (the mechanism of detection did not change), except where a
    remedy changed it (J1's single pin, ADR-083: now latent). New block rows: regole.r_proxy; new
    supply rows: from what the bench shows (the rail lost and the board muted: 1; the board off or
    mute without sound: 2; nothing visible: 3).
  - The rows nobody redid (a decision accepted, sent to L58 or to G2, or a low row of L45b / L45c
    not touched by any remedy): the columns as before, with the reason in 'stato'.
Refuses if a count does not come back: 469, 173, 97, 112, 15 + 11, 121, 44.
"""
import csv
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
import regole  # noqa: E402

L = os.path.dirname(QUI)
DATA = os.path.abspath(os.path.join(L, "..", ".."))
D1 = os.path.join(DATA, "2026-10-14", "L45d1")
D2A = os.path.join(DATA, "2026-10-14", "L45d2a")
B1 = os.path.join(DATA, "2026-10-22", "L45d2b3b1")
B2B2 = os.path.join(DATA, "2026-10-23", "L45d2b3b2b2")
S1 = os.path.join(DATA, "2026-10-20", "L45d2b2b1")
S2 = os.path.join(DATA, "2026-10-20", "L45d2b2b2")
num = regole.num


def rd(p):
    return list(csv.DictReader(open(p)))


def rifiuta(msg):
    sys.exit("RIFIUTATO: " + msg)


# ---------------------------------------------------------------- the block: heat, jack, Stax
CAL = {}                                   # mode -> (row, source)
for r in rd(os.path.join(B1, "sintesi_calore.csv")):
    CAL[r["modo"]] = (r, "L45d2b3b1/sintesi_calore.csv (blocco prima di ADR-097)")
for r in rd(os.path.join(B1, "sintesi_calore_dopo097.csv")):
    CAL[r["modo"]] = (r, "L45d2b3b1/sintesi_calore_dopo097.csv (blocco di ADR-097)")
SORG = {r["modo"]: r for r in rd(os.path.join(B2B2, "sintesi_sorg.csv")) if r["modo"] != "rif"}
T60 = {r["modo"]: r for r in rd(os.path.join(B2B2, "sintesi_sorgt60.csv")) if r["modo"] != "rif"}
if len(SORG) != 26:
    rifiuta("sintesi_sorg.csv: %d modi, attesi 15 + 11" % len(SORG))
for m, r in SORG.items():
    CAL[m] = (r, "L45d2b3b2b2/sintesi_sorg.csv (sorgente, ADR-099)")
DISS = {r["caso"]: r for r in rd(os.path.join(B2B2, "dissipatore.csv"))}
# the short of one output device heats the OTHER: Q133 shorted -> Q132, Q132 shorted -> Q133
DISS_MODO = {"Q133_ce": ("NPN Q132 col PNP Q133 in corto", "NPN Q132 col PNP Q133 in corto, dispositivi a 60 C"),
             "Q132_ce": ("PNP Q133 con l'NPN Q132 in corto",)}
for m in [k for k, (r, _) in CAL.items() if r.get("stato", "ok") != "ok" and "CORSA CORTA" not in r["stato"]]:
    rifiuta("il calore di %s senza corse finite (%s)" % (m, CAL[m][0]["stato"]))


def calore(m):
    """(Tj max at 60 C air, the part beyond its limits or '', main V, fixed 1 V, source)."""
    if m not in CAL:
        return None
    r, fonte = CAL[m]
    tj = num(r["Tj_max_60_C"])
    oltre = (r.get("oltre_i_limiti_60C") or "").strip() or (r.get("diodi_oltre_60C") or "").strip()
    if m in T60:                                        # the VAS: the devices at 60 C too
        tj = max(tj, num(T60[m]["Tj_max_60_C"]))
        fonte += " + sintesi_sorgt60.csv"
        if m in DISS_MODO:
            oltre = oltre                               # the pair: handled below
        elif (T60[m]["oltre_i_limiti_60C"] or "").strip():
            oltre = T60[m]["oltre_i_limiti_60C"]
    if m in DISS_MODO and m in SORG:                     # the heatsink of ADR-099
        tjd = max(num(DISS[c]["Tj_con_C"]) for c in DISS_MODO[m])
        lim = num(DISS[DISS_MODO[m][0]]["limite_P7_C"])
        tj, oltre = tjd, ("" if tjd <= lim else "%s %g C col dissipatore" % (DISS_MODO[m][0], tjd))
        fonte += " + dissipatore.csv (WA-T220-101E)"
    return tj, oltre, num(r["main_A_V"]), num(r["fix1_A_V"]), fonte


STAX = {}                                  # (pos, mode, k) -> (ms, source)


def stax_metti(pos, m, k, ms, fonte):
    if ms is not None:
        STAX[(pos, m, k)] = (ms, fonte)


for r in rd(os.path.join(B1, "p10_stax.csv")):
    # R120 shorted ran 0,6 s (limitations #75): the fault at 0,3 s, 22 ms on the Stax, as L60d2's 22,0
    if r["posizione"] in ("A", "F2") and (r["stato"] == "ok" or r["stato"].startswith("CORSA CORTA")):
        stax_metti(r["posizione"], r["modo"], r["k_C"], num(r["stax_sopra_ms"]),
                   "L45d2b3b1/p10_stax.csv" + (" (corsa corta, 0,6 s)" if r["stato"] != "ok" else ""))
for r in rd(os.path.join(B1, "p10_stax_dopo097.csv")):
    pass                                              # read below, by case name
for r in rd(os.path.join(B1, "stax_lunghi.csv")):
    stax_metti(r["posizione"], r["modo"], r["k_C"], num(r["dopo_ms"]), "L45d2b3b1/stax_lunghi.csv (ADR-097)")


def da_caso(nome):
    k = "1.05" if nome.endswith("_k105") else "1"
    base = nome[:-5] if nome.endswith("_k105") else nome
    _, pos, m = base.split("_", 2)
    return pos, m, k


for r in rd(os.path.join(B1, "p10_stax_dopo097.csv")):
    if r["modo"].startswith("G0_"):
        p, m, k = da_caso(r["modo"])
        stax_metti(p, m, k, num(r["fix2_sopra_ms"]), "L45d2b3b1/p10_stax_dopo097.csv (ADR-097)")
lunghi = rd(os.path.join(B2B2, "stax_lunghi.csv"))
if len(lunghi) != 121:
    rifiuta("L45d2b3b2b2/stax_lunghi.csv: %d casi, attesi 121" % len(lunghi))
for r in lunghi:
    p, m, k = da_caso(r["caso"])
    stax_metti(p, m, k, num(r["sorgente_ms"]), "L45d2b3b2b2/stax_lunghi.csv (sorgente)")
nuove = rd(os.path.join(L, "p10_stax_nuove.csv"))
if len(nuove) != 44 or any(r["stato"] != "ok" for r in nuove):
    rifiuta("p10_stax_nuove.csv: %d casi (attesi 44), tutti ok" % len(nuove))
for r in nuove:
    p, m, k = da_caso(r["modo"])
    stax_metti(p, m, k, num(r["fix2_sopra_ms"]), "L45d2b3b3/p10_stax_nuove.csv (sorgente)")


def stax(m):
    v = [(ms, f) for (p, mm, k), (ms, f) in STAX.items() if mm == m]
    if not v:
        return None, ""
    ms = max(x[0] for x in v)
    return ms, "; ".join(sorted({x[1] for x in v}))


# L45b's unloaded P10 on the fixed 2: the modes the Stax bench never ran (L60c2 took the 107 with
# time above the ceiling somewhere)
P10B = {}
for r in rd(os.path.join(DATA, "2026-10-13", "L45b", "p10_blocco.csv")):
    P10B[r["modo"]] = max(P10B.get(r["modo"], 0.0), num(r["fix2_sopra_ms"]) or 0.0)


def riga_blocco(m, pezzo_nuovo=False):
    c = calore(m)
    if c is None:
        rifiuta("%s: nessun banco del calore l'ha corso" % m)
    tj, oltre, vm, vf, fonte = c
    s, fs = stax(m)
    nota_stax = ""
    if s is None:
        if P10B.get(m, 0.0) > 0:
            rifiuta("%s: mai corso sulla Stax, ma a vuoto in L45b %.1f ms sopra 0,87 V" % (m, P10B[m]))
        nota_stax = "Stax non corsa: 0 ms anche a vuoto col 4,7 uF (L45b/p10_blocco.csv)" if m in P10B \
            else "Stax non corsa"
        s_g = 0.0
    else:
        s_g = s
    picco = max(vm or 0.0, vf or 0.0)
    if m == "C145_cc":                    # ADR-097, 3: on the real supply the rail collapses; the impulse
        G = 5
        oltre = "R144 / R152 ~1,3 J in ~0,25 s (NC-075, alla scelta della parte)"
    else:
        G = regole.g_blocco(oltre, s_g, picco)
    eff = "Tj max a 60 C %s C; principale %.3g V (%.1f dB SPL), fissa 1 %.3g V; Stax %s" % (
        "%g" % tj if tj is not None else "-", vm or 0.0, regole.db(vm or 1e-12), vf or 0.0,
        ("%.1f ms sopra 0,87 V" % s) if s is not None else nota_stax)
    if oltre:
        eff += "; oltre: " + oltre
    if picco > 0.87:
        eff += "; principale e fissa 1 contano sulla protezione a valle (ADR-081)"
    return dict(G_dopo=G, effetto_dopo=eff, picco_dopo_V="%.4g" % picco, picco_dopo_dB="%.1f" % regole.db(picco or 1e-12),
                stax_ms="" if s is None else "%.1f" % s, Tj_max_C="" if tj is None else "%g" % tj,
                fonte_dopo=fonte + ("; " + fs if fs else ""), R_proxy=regole.r_proxy(picco))


# ---------------------------------------------------------------- the published rows
sintesi = rd(os.path.join(D1, "fmea_sintesi.csv"))
if len(sintesi) != 469:
    rifiuta("fmea_sintesi.csv: %d righe, attese 469" % len(sintesi))
blocco = {(r["ref"], r["modo"]): r for r in rd(os.path.join(D1, "fmea_blocco_adr070.csv"))}
if len(blocco) != 112:
    rifiuta("fmea_blocco_adr070.csv: %d chiavi, attese 112" % len(blocco))
dec = {}
for r in rd(os.path.join(D2A, "decisioni.csv")):
    k = (r["lotto"], r["ref"], r["modo"])
    if k in dec:
        rifiuta("decisioni.csv: %s due volte" % (k,))
    dec[k] = r
if len(dec) != 173:
    rifiuta("decisioni.csv: %d righe, attese 173" % len(dec))
b1 = {(r["lotto"], r["ref"], r["modo"]): r for r in rd(os.path.join(B1, "righe_b1.csv"))}
if len(b1) != 97:
    rifiuta("righe_b1.csv: %d righe, attese 97" % len(b1))
chiavi = [(r["lotto"], r["ref"], r["modo"]) for r in sintesi]
if len(set(chiavi)) != len(chiavi):
    rifiuta("fmea_sintesi.csv: chiavi doppie")
if not set(dec) <= set(chiavi) or not set(b1) <= set(dec):
    rifiuta("decisioni.csv o righe_b1.csv con righe che la sintesi non ha")

# the supply: L45d2b2b2 on the source after ADR-094 (scelta 3 rerun there, analisi_s074; scelta 4)
S074 = {}
for r in rd(os.path.join(S2, "analisi_s074.csv")):
    S074.setdefault(r["caso"].rsplit("_", 1)[0], []).append(r)
RIAS = {}
for f in (os.path.join(S2, "riassunto_sorgente.csv"), os.path.join(B1, "riassunto_nuove.csv")):
    for r in rd(f):
        RIAS.setdefault(r["caso"].rsplit("_", 1)[0], []).append(r)
AN = {}
for f in (os.path.join(S2, "analisi_sorgente.csv"), os.path.join(B1, "analisi_nuove.csv")):
    for r in rd(f):
        AN.setdefault(r["caso"].rsplit("_", 1)[0], []).append(r)
SCELTA3 = {("C501", "corto"): ["f_c501_corto"], ("U501", "IN a massa (interno)"): ["f_c501_corto"],
           ("C502", "corto"): ["f_c502_corto"], ("U502", "IN a massa (interno)"): ["f_c502_corto"],
           ("C509", "corto"): ["f_c509_corto"], ("C510", "corto"): ["f_c510_corto"]}
D501 = ["f_d501a_corto", "f_d501b_corto", "f_d501c_corto", "f_d501d_corto"]
SCELTA4 = {("U504", "IN-OUT in corto"): "f_u504_cortoio", ("K501", "bobina in corto"): "f_k501_bobina",
           ("D506", "corto"): "f_d506_corto", ("D505", "corto"): "f_d505_corto", ("D508", "corto"): "f_d508_corto",
           ("R503", "corto"): "f_r503_corto", ("R510", "corto"): "f_r510_corto", ("R512", "corto"): "f_r512_corto"}
E_IMPULSO_J = 1.0          # NC-073: R550 / R551 at 4,7-8,8 J; the healthy cases stay at ~0,1 J


def riga_scelta3(ref, modo):
    casi = D501 if ref == "D501" else SCELTA3[(ref, modo)]
    rr = [x for c in casi for x in S074[c]]
    e = max(max(num(x["er550_J"]), num(x["er551_J"])) for x in rr)
    p = max(max(num(x["pr550_pk_W"]), num(x["pr551_pk_W"])) for x in rr)
    jp = all(x["jack_prima"] == "si" for x in rr)
    if not jp:
        rifiuta("%s %s: il jack non e' sempre prima del crollo" % (ref, modo))
    eff = "il sorvegliante muta, il jack prima del crollo (~32 dB SPL, ADR-093); R550 / R551 al piu' %.3g W, %.3g J" % (p, e)
    if e > E_IMPULSO_J:
        return dict(G_dopo=5, effetto_dopo=eff + ": l'impulso di NC-073", stato="NC-073 (alla scelta della parte)",
                    fonte_dopo="L45d2b2b2/analisi_s074.csv (%s)" % ", ".join(casi))
    return dict(G_dopo=2, effetto_dopo=eff, stato="nel circuito (ADR-093)",
                fonte_dopo="L45d2b2b2/analisi_s074.csv (%s)" % ", ".join(casi))


def riga_scelta4(ref, modo):
    c = SCELTA4[(ref, modo)]
    rr = RIAS[c]
    fuori = sorted({x["parte"] for x in rr if x["esito"] != "dentro"})
    tj = max(num(x["tj100_C"]) for x in rr if num(x["tj100_C"]) is not None)
    an = AN[c]
    ant = max((num(x["anticipo_guadagno_ms"]) or 0.0) for x in an)
    eff = "le parti del comando e dei 5 V al piu' %g C a 100 ms" % tj
    if ant > 0:
        eff += "; il guadagno cade %.1f ms prima del jack (Delta perso, ~70 dB SPL)" % ant
    G = 3 if ant > 0 else 2
    if fuori:
        eff += "; oltre: %s (%g C): NC-073" % (", ".join(fuori), tj)
        return dict(G_dopo=5, effetto_dopo=eff, stato="NC-073 (alla scelta della parte)",
                    fonte_dopo="L45d2b2b2/riassunto_sorgente.csv, analisi_sorgente.csv (%s)" % c)
    return dict(G_dopo=G, effetto_dopo=eff, stato="nel circuito (ADR-094)",
                fonte_dopo="L45d2b2b2/riassunto_sorgente.csv, analisi_sorgente.csv (%s)" % c)


STATO_DEC = {"accettata": "accettata (%s)", "L58": "alla diagnosi, L58 (%s)", "G2": "a G2 (%s)"}
RIMEDIO = {"1": "ADR-081 (la Stax col suo 1 uF; principale e fissa 1 sulla protezione a valle), ADR-086 / ADR-089 / ADR-098",
           "10": "ADR-081, ADR-099 (il calore)", "12": "ADR-090 (i quattro diodi di riserva, L62b)",
           "13": "ADR-071 (alla diagnosi)", "3": "ADR-093", "4": "ADR-094", "6": "ADR-082 / ADR-085",
           "8": "ADR-083 (due pin per rail)", "9": "ADR-082 (doppio guasto accettato)",
           "bassa": "ADR-095 (i massimi col rail alto, L45d2b2c)"}

out = []
for s in sintesi:
    k = (s["lotto"], s["ref"], s["modo"])
    d = dec.get(k)
    b = b1.get(k)
    r = dict(gruppo="tabelle di L45", lotto=s["lotto"], ref=s["ref"], funzione=s["funzione"], modo=s["modo"],
             scelta=d["scelta"] if d else "", G_prima=s["G"], P_prima=s["P"], R_prima=s["R"],
             priorita_prima=d["priorita_adr071"] if d else s["priorita"], fit_modo=s["fit_modo"],
             decisione=(d["decisione"] if d else ""), adr=(d["adr"] if d else ""),
             G_dopo=s["G"], P_dopo=s["P"], R_dopo=s["R"], effetto_dopo="", picco_dopo_V="", picco_dopo_dB="",
             stax_ms="", Tj_max_C="", stato="", rimedio="", fonte_dopo="")
    sc = r["scelta"]
    r["rimedio"] = RIMEDIO.get(sc, d["adr"] if d else "")
    if s["lotto"] == "L45a":
        m = blocco[(s["ref"], s["modo"])]["caso"]
        x = riga_blocco(m)
        x.pop("R_proxy")
        r.update(x)
        r["caso"] = m
        if m == "C145_cc":
            r["stato"] = "NC-075 (alla scelta della parte)"
        elif d and d["dove"] == "L58":
            r["stato"] = STATO_DEC["L58"] % d["adr"]
        elif m in SORG:
            r["stato"] = "nel circuito (ADR-099), rimisurata sul sorgente"
            r["rimedio"] = (r["rimedio"] + "; " if r["rimedio"] else "") + "ADR-099"
        elif d:
            r["stato"] = "nel circuito, rimisurata"
        else:
            r["stato"] = "rimisurata, nessun rimedio chiesto"
    elif sc == "6":
        k3 = s["ref"].startswith("K3")
        r.update(effetto_dopo=b["effetto_oggi"], fonte_dopo=b["fonte"])
        if k3:
            r.update(G_dopo="", P_dopo="", R_dopo="", stato="escluso: K3 a isolamento rinforzato (ADR-085)")
        else:
            r.update(G_dopo=3, stato="nel circuito; principale e fissa 1 sulla protezione a valle (ADR-081)")
    elif sc == "3":
        r.update(riga_scelta3(s["ref"], s["modo"]))
    elif sc == "4":
        r.update(riga_scelta4(s["ref"], s["modo"]))
    elif sc == "8":
        r.update(G_dopo=1, R_dopo=3, effetto_dopo=b["effetto_oggi"], fonte_dopo=b["fonte"],
                 stato="nel circuito (ADR-083): latente, il secondo pin regge")
    elif sc == "9":
        v = abs(num(b["effetto_oggi"].split()[2]))
        r.update(G_dopo=regole.g_picco(v), effetto_dopo=b["effetto_oggi"] + " (%.1f dB SPL)" % regole.db(v),
                 picco_dopo_V="%.4g" % v, picco_dopo_dB="%.1f" % regole.db(v), fonte_dopo=b["fonte"],
                 stato="accettata (ADR-082): col blocco al rail dopo e' un doppio guasto")
    elif sc == "bassa" and s["lotto"] == "L45c1":
        r.update(effetto_dopo=b["effetto_oggi"], fonte_dopo=b["fonte"], stato="nel circuito (ADR-095), verificata")
    elif d:
        r["stato"] = STATO_DEC[d["dove"]] % (d["adr"] or "L45d2a") if d["dove"] in STATO_DEC else d["dove"]
        if d["dove"] == "accettata" and not d["adr"]:
            r["stato"] = "accettata (L45d2a: invariato)"
        r["effetto_dopo"] = "come prima: il rimedio non e' nel circuito" if d["dove"] in ("L58", "G2") else \
            "come prima: accettato"
    else:
        r["stato"] = "invariata: riga di %s, nessun rimedio la tocca" % s["lotto"]
    if r["P_dopo"] != "":
        r["priorita_dopo"] = regole.priorita_dopo(r["G_dopo"], r["P_dopo"], r["R_dopo"],
                                                  sc == "6" and s["ref"].startswith("K2"))
    else:
        r["priorita_dopo"] = "esclusa"
    out.append(r)

# ---------------------------------------------------------------- new rows: the block
FUNZ = {"D154": "diodo di riserva del moltiplicatore di Vbe (ADR-090)", "D155": "diodo di riserva del moltiplicatore di Vbe (ADR-090)",
        "D156": "diodo di riserva del moltiplicatore di Vbe (ADR-090)", "D157": "diodo di riserva del moltiplicatore di Vbe (ADR-090)",
        "D158": "diodo base-emettitore del finale NPN (ADR-095)", "D159": "diodo base-emettitore del finale PNP (ADR-095)",
        "R150": "in parallelo all'arresto del gate di retroazione (ADR-086)", "R151": "gemella della degenerazione di retroazione (ADR-086)",
        "R152": "gemella della resistenza della cella RC (ADR-086)", "R153": "prima meta' del limite dell'inseguitore (ADR-087, ADR-097)",
        "R160": "seconda meta' del limite dell'inseguitore (ADR-097)",
        "R190": "10 kOhm sul collettore dell'aiuto dello specchio (ADR-099)", "R191": "gemella di R101, il riferimento (ADR-099)",
        "R192": "22 Ohm, seconda parte della degenerazione del VAS (ADR-099)", "Q193": "il limite di corrente del VAS, MMBT5401 (ADR-099)",
        "R194": "1 kOhm sul collettore della sorgente di coda (ADR-099)"}
CH = {"ap": "aperto", "cc": "corto", "ce": "ce", "be": "be", "ae": "ae"}
MODO = {"ap": "aperto", "cc": "corto", "ce": "corto C-E", "be": "corto B-E", "ae": "aperto"}
nuovi_blocco = sorted({m for m in CAL if m.rsplit("_", 1)[0] in FUNZ})
n_adr099 = sum(1 for m in nuovi_blocco if m in SORG)
if n_adr099 != 11:
    rifiuta("%d modi delle parti di ADR-099, attesi 11" % n_adr099)
for m in nuovi_blocco:
    ref, suf = m.rsplit("_", 1)
    tipo = "BJT_S" if ref.startswith("Q") else "D_seg" if ref.startswith("D") else "R"
    fm, P, fonte_t, _ = regole.p_modo(tipo, CH[suf], 8)
    x = riga_blocco(m, True)
    Rr = x.pop("R_proxy")
    adr = FUNZ[ref].split("(")[-1].rstrip(")")
    r = dict(gruppo="parti nuove", lotto="blocco", ref=ref, funzione=FUNZ[ref], modo=MODO[suf], caso=m, scelta="",
             G_prima="", P_prima="", R_prima="", priorita_prima="", fit_modo="%.3g" % fm, decisione="", adr=adr,
             P_dopo=P, R_dopo=Rr, rimedio=adr, stato="nel circuito, misurata", **x)
    r["priorita_dopo"] = regole.priorita_dopo(r["G_dopo"], P, Rr)
    out.append(r)

# ---------------------------------------------------------------- new rows: the supply
PSU = [
    # ref, mode, case, type, key, function, ADR
    ("D513", "corto", "f_d513_corto", "D_rett", "corto", "il secondo SB340 sul piedino del regolatore + (ADR-093)", "ADR-093"),
    ("D514", "corto", "f_d514_corto", "D_rett", "corto", "il secondo SB340 sul piedino del regolatore - (ADR-093)", "ADR-093"),
    ("D515", "aperto", "f_d515_aperto", "D_rett", "aperto", "lo Schottky in serie dopo il regolatore + (ADR-093)", "ADR-093"),
    ("D515", "corto", "f_d515_corto", "D_rett", "corto", "lo Schottky in serie dopo il regolatore + (ADR-093)", "ADR-093"),
    ("D516", "aperto", "f_d516_aperto", "D_rett", "aperto", "lo Schottky in serie dopo il regolatore - (ADR-093)", "ADR-093"),
    ("D516", "corto", "f_d516_corto", "D_rett", "corto", "lo Schottky in serie dopo il regolatore - (ADR-093)", "ADR-093"),
    ("D530", "aperto", "f_d530_aperto", "D_seg", "aperto", "il diodo doppio del bloccaggio del mute (ADR-094)", "ADR-094"),
    ("D530", "corto", "f_d530_corto", "D_seg", "corto", "il diodo doppio del bloccaggio del mute (ADR-094)", "ADR-094"),
    ("D531", "aperto", "f_d531_aperto", "D_seg", "aperto", "il diodo doppio del bloccaggio del permesso (ADR-094)", "ADR-094"),
    ("D531", "corto", "f_d531_corto", "D_seg", "corto", "il diodo doppio del bloccaggio del permesso (ADR-094)", "ADR-094"),
    ("D532", "aperto", "f_d532_aperto", "D_seg", "aperto", "il diodo doppio del bloccaggio di K501 (ADR-094)", "ADR-094"),
    ("D532", "corto", "f_d532_corto", "D_seg", "corto", "il diodo doppio del bloccaggio di K501 (ADR-094)", "ADR-094"),
    ("R552", "aperto", "f_r552_aperto", "R", "aperto", "47 Ohm davanti a Q503 (ADR-094)", "ADR-094"),
    ("R553", "aperto", "f_r553_aperto", "R", "aperto", "gemella di R503, il riferimento (ADR-094)", "ADR-094"),
    ("R553", "corto", "f_r553_corto", "R", "corto", "gemella di R503, il riferimento (ADR-094)", "ADR-094"),
    ("R554", "aperto", "f_r554_aperto", "R", "aperto", "gemella di R510, la presa della rete (ADR-094)", "ADR-094"),
    ("R554", "corto", "f_r554_corto", "R", "corto", "gemella di R510, la presa della rete (ADR-094)", "ADR-094"),
    ("R555", "aperto", "f_r555_aperto", "R", "aperto", "gemella di R512 (ADR-094)", "ADR-094"),
    ("R555", "corto", "f_r555_corto", "R", "corto", "gemella di R512 (ADR-094)", "ADR-094"),
    ("U512", "spento", "f_u512_spento", "LDO", "spento", "il secondo regolatore dei 5 V, in serie (ADR-094)", "ADR-094"),
    ("U512", "IN-OUT in corto", "f_u512_cortoio", "LDO", "segue", "il secondo regolatore dei 5 V, in serie (ADR-094)", "ADR-094"),
    ("C536", "corto", "f_c536_corto", "C_cer", "corto", "fra i due regolatori dei 5 V (ADR-094)", "ADR-094"),
]
# existing parts whose open mode the bench redid after ADR-094 split them (the old row stays: this
# is the same mode on today's circuit, as a new row with its source)
PSU += [("R503", "aperto", "f_r503_aperto", "R", "aperto", "il riferimento, sdoppiata con R553 (ADR-094)", "ADR-094"),
        ("R510", "aperto", "f_r510_aperto", "R", "aperto", "la presa della rete, sdoppiata con R554 (ADR-094)", "ADR-094"),
        ("R512", "aperto", "f_r512_aperto", "R", "aperto", "sdoppiata con R555 (ADR-094)", "ADR-094")]


def psu_effetto(c):
    rr, an = RIAS[c], AN[c]
    fuori = sorted({x["parte"] for x in rr if x["esito"] != "dentro"})
    tj = max((num(x["tj100_C"]) for x in rr if num(x["tj100_C"]) is not None), default=None)
    v5min = min(num(x["v5_min"]) for x in an)
    tjack = [num(x["t_jack_ms"]) for x in an if num(x["t_jack_ms"]) is not None]
    vp = [num(x["vp_fine"]) for x in an if num(x["vp_fine"]) is not None]
    vm = [num(x["vm_fine"]) for x in an if num(x["vm_fine"]) is not None]
    jp = {x["jack_prima"] for x in an}
    parti = []
    if v5min < 4.5:
        parti.append("i 5 V persi (V5 al piu' basso %.3g V%s): il micro si spegne, i rele' cadono" % (
            v5min, ", l'artefatto del banco di limitations #73" if v5min < -1 else ""))
    if tjack:
        parti.append("il mute al jack a %.1f-%.1f ms (%s)" % (min(tjack), max(tjack),
                                                              "prima del crollo del rail" if jp == {"si"} else "jack_prima %s" % "/".join(sorted(jp))))
    if vp and (max(vp) > 15.1 or min(vp) < 14.0 or max(vm) > -14.0 or min(vm) < -15.1):
        parti.append("rail a fine corsa + %.2f...%.2f V, - %.2f...%.2f V (rete -10...+10 %%)" % (min(vp), max(vp), min(vm), max(vm)))
    if not parti:
        parti.append("niente al jack, i rail e i 5 V come a riposo")
    if tj is not None:
        parti.append("le parti al piu' %.0f C a 100 ms" % tj)
    if fuori:
        parti.append("oltre: " + ", ".join(fuori))
    return "; ".join(parti), fuori, v5min, tjack, vp, jp


for ref, modo, c, tipo, chiave, funz, adr in PSU:
    eff, fuori, v5min, tjack, vp, jp = psu_effetto(c)
    fm, P, _, _ = regole.p_modo(tipo, chiave, 1)
    rail_perso = vp and min(vp) < 10.0
    if fuori:
        G, R = 5, 2
        stato = "accettata (ADR-097, 2): lo spegnimento termico del regolatore" if ref == "C536" else "NC-073"
    elif v5min < 4.5:
        G, R, stato = 2, 2, "nel circuito: il guasto mette in sicuro (i 5 V persi)"
    elif rail_perso:
        G, R, stato = 2, 1, "nel circuito: il sorvegliante muta prima del crollo"
    elif tjack:
        G, R, stato = 2, 2, "nel circuito: il mute, senza suono"
    else:
        G, R, stato = 1, 3, "nel circuito: latente, la protezione di %s si perde senza effetto" % adr
    if vp and max(vp) > 15.5 and not fuori:
        eff += "; il caso del rail alto di L45d2b2c, dentro (ADR-095)"
    r = dict(gruppo="parti nuove", lotto="alimentatore", ref=ref, funzione=funz, modo=modo, caso=c, scelta="",
             G_prima="", P_prima="", R_prima="", priorita_prima="", fit_modo="%.3g" % fm, decisione="", adr=adr,
             G_dopo=G, P_dopo=P, R_dopo=R, effetto_dopo=eff, picco_dopo_V="", picco_dopo_dB="", stax_ms="",
             Tj_max_C="", stato=stato, rimedio=adr,
             fonte_dopo="%s (%s)" % ("L45d2b3b1/riassunto_nuove.csv, analisi_nuove.csv" if c in
                                     {x["caso"].rsplit("_", 1)[0] for x in rd(os.path.join(B1, "riassunto_nuove.csv"))}
                                     else "L45d2b2b2/riassunto_sorgente.csv, analisi_sorgente.csv", c))
    r["priorita_dopo"] = regole.priorita_dopo(G, P, R)
    out.append(r)

# ---------------------------------------------------------------- new supply modes no bench has run
CALCOLO = [
    ("R550", "aperto", "R", "aperto", "4,7 Ohm davanti al regolatore + (ADR-092)", "ADR-092", 2, 1,
     "il regolatore + senza ingresso: il rail + cade, il sorvegliante muta (come D515 aperto, misurato)"),
    ("R551", "aperto", "R", "aperto", "4,7 Ohm davanti al regolatore - (ADR-092)", "ADR-092", 2, 1,
     "il regolatore - senza ingresso: il rail - cade, il sorvegliante muta (come D516 aperto, misurato)"),
    ("R550", "corto", "R", "corto", "4,7 Ohm davanti al regolatore + (ADR-092)", "ADR-092", 5, 3,
     "torna il caso prima di ADR-092: il regolatore + a 91,6 / 113,7 / 135,9 C a rete -10 / 0 / +10 %, 60 C d'aria "
     "(L45d2b2a/rpre.csv, 0 ohm), senza un segno"),
    ("R551", "corto", "R", "corto", "4,7 Ohm davanti al regolatore - (ADR-092)", "ADR-092", 5, 3,
     "torna il caso prima di ADR-092: il regolatore - a 91,6 / 114,4 / 137,2 C a rete -10 / 0 / +10 %, 60 C d'aria "
     "(L45d2b2a/rpre.csv, 0 ohm), senza un segno"),
    ("C507", "corto", "C_cer", "corto", "la partenza morbida del regolatore + (ADR-091)", "ADR-091", 2, 1,
     "NR/SS a massa: il riferimento del regolatore a zero, il rail + non sale, il sorvegliante muta"),
    ("C508", "corto", "C_cer", "corto", "la partenza morbida del regolatore - (ADR-091)", "ADR-091", 2, 1,
     "NR/SS a massa: il rail - non sale, il sorvegliante muta"),
    ("C507", "aperto", "C_cer", "aperto", "la partenza morbida del regolatore + (ADR-091)", "ADR-091", 1, 3,
     "il rail + parte veloce (la partenza interna del regolatore): il caso prima di ADR-091, ma piu' veloce "
     "invece che piu' lento; i rail non piu' insieme all'accensione, il mute ancora inserito (MUSICA a 0,72 s)"),
    ("C508", "aperto", "C_cer", "aperto", "la partenza morbida del regolatore - (ADR-091)", "ADR-091", 1, 3,
     "come C507 aperto, sul rail -"),
    ("R552", "corto", "R", "corto", "47 Ohm davanti a Q503 (ADR-094)", "ADR-094", 1, 3,
     "latente: toglie il limite di ADR-094; con un secondo guasto torna il caso di L45d2b2b2 (2N7002 fino a 3,1 A)"),
    ("C536", "aperto", "C_cer", "aperto", "fra i due regolatori dei 5 V (ADR-094)", "ADR-094", 1, 3,
     "da verificare: la stabilita' di U504 / U512 senza il condensatore (MCP1703A: >= 1 uF), al banco di G2"),
    ("D513", "aperto", "D_rett", "aperto", "il secondo SB340 sul piedino del regolatore + (ADR-093)", "ADR-093", 1, 3,
     "latente: resta D510; con un secondo guasto sul piedino torna il caso prima di ADR-093"),
    ("D514", "aperto", "D_rett", "aperto", "il secondo SB340 sul piedino del regolatore - (ADR-093)", "ADR-093", 1, 3,
     "latente: resta D511; con un secondo guasto sul piedino torna il caso prima di ADR-093"),
]
for ref, modo, tipo, chiave, funz, adr, G, R, eff in CALCOLO:
    fm, P, _, _ = regole.p_modo(tipo, chiave, 1)
    # ADR-100, 1 («Nel rame del layout»): NC-072 holds the regulator <= 125 C without the 4,7 ohm
    # (with NC-072's <= 27 C/W: 60 + 27 x 2,38 = 124 C, ADR-100)
    stato = "NC-072 (il rame al layout anche senza la resistenza, ADR-100)" if G == 5 else "a G2 (il banco)" if eff.startswith("da verificare") else \
        "nel circuito (calcolo, non simulato)"
    r = dict(gruppo="parti nuove", lotto="alimentatore", ref=ref, funzione=funz, modo=modo, caso="calcolo", scelta="",
             G_prima="", P_prima="", R_prima="", priorita_prima="", fit_modo="%.3g" % fm, decisione="", adr=adr,
             G_dopo=G, P_dopo=P, R_dopo=R, effetto_dopo="CALCOLO, non simulato: " + eff, picco_dopo_V="",
             picco_dopo_dB="", stax_ms="", Tj_max_C="", stato=stato, rimedio=adr, fonte_dopo="calcolo (questo lotto)")
    r["priorita_dopo"] = regole.priorita_dopo(G, P, R)
    out.append(r)

CAMPI = ["gruppo", "lotto", "ref", "funzione", "modo", "caso", "scelta", "G_prima", "P_prima", "R_prima",
         "priorita_prima", "decisione", "adr", "rimedio", "effetto_dopo", "picco_dopo_V", "picco_dopo_dB",
         "stax_ms", "Tj_max_C", "G_dopo", "fit_modo", "P_dopo", "R_dopo", "priorita_dopo", "stato", "fonte_dopo"]
with open(os.path.join(L, "fmea_dopo.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=CAMPI, extrasaction="ignore")
    w.writeheader()
    for r in out:
        w.writerow(r)

from collections import Counter  # noqa: E402
tab = [r for r in out if r["gruppo"] == "tabelle di L45"]
nuo = [r for r in out if r["gruppo"] == "parti nuove"]
print("righe: %d (tabelle di L45 %d, parti nuove %d)" % (len(out), len(tab), len(nuo)))
print("prima (tabelle):", dict(Counter(r["priorita_prima"] for r in tab)))
print("dopo  (tabelle):", dict(Counter(r["priorita_dopo"] for r in tab)))
print("dopo  (nuove)  :", dict(Counter(r["priorita_dopo"] for r in nuo)))
print("stato:", dict(Counter(r["stato"].split(":")[0].split(" (")[0] for r in out)))
