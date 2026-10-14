#!/usr/bin/env python3
"""L45d1: the ADR-070 classes of L45c1's table (the faults of the audio rails), read by
riporto_l45c1.py. Data only (solo stdlib). The rates are tipi.py's; the measured peaks and the
verdicts are L45c1's (fmea_rail.csv), untouched.

Severity 5 (a part beyond its limits) where L45c1's report found one: a short on the raw NEGATIVE
side (C502, the bridge's two diodes towards -, C510, U502's input to ground) leaves U502's output
0,78-1,76 V above its input, against the -0,3 V of its absolute maximum (SBVS169D p. 5; D511 is the
bench's generic diode, the true figure to be verified). The positive side: U501's datasheet states
no such limit (L45a / L41a), so those rows keep the measured 4.
The over-voltages (a rail to +-20,3 V): <= 0,4 mV at the jack, so the measured severity stands; the
block parts' maximum voltages were NOT read in L45c1 (its report), and the class-A output stage
dissipates more with the rail (NC-062, L55): the remedy says it.
"""
from tipi import TIPI  # noqa: F401  (motore reads K.TIPI)

ELETTROLITICI = {"C501", "C502", "C505", "C506", "C141", "C142", "C139-C142"}
# the parts there are 8 of: one per gain block (A, F1, F2, B on each channel); C139-C142 aperto
# stands for the 16 electrolytics (the 16 ceramics add ~2 FIT, not counted: the row is severity 1)
MOLT = {"C139": 8, "C140": 8, "C141": 8, "C142": 8, "C139-C142": 16, "U501, U502": 2}


def tipo_di(ref):
    if ref in ("J513", "J1"):
        return "CONN"
    if ref in ("D501", "D510", "D511"):
        return "D_rett"
    if ref.startswith("C"):
        return "C_el" if ref in ELETTROLITICI else "C_cer"
    if ref.startswith("R"):
        return "R"
    if ref in ("U501", "U502", "U501, U502"):
        return "LDO_P"
    if ref == "Q501":
        return "FET"
    if ref == "K2-K4":
        return "RELE_S"
    return None


# U501's set point: the rows that move its output (pins 4, 5, 6, 8, 9, 10, 11, 12, SENSE, EN) share
# the LDO's "out of specification" 45 %, as L45c2 did for U503 (IPOTESI, evenly)
N_FUORI = {"U501": 10, "U502": 10, "U501, U502": 10}

FRAZIONE = {
    ("U501", "uscita a massa (interno)"): ("pin", 1),
    ("U502", "uscita a massa (interno)"): ("pin", 1),
    ("U501", "IN a massa (interno)"): ("pin", 1),
    ("U502", "IN a massa (interno)"): ("pin", 1),
    # a welded NO: half of "a pole welded" (the other half is the NC), x 3 relays (IPOTESI)
    ("K2-K4", "NO saldato, poi lo spegnimento"): ("un_polo_saldato/2", 3),
    ("K2-K4", "NO saldato, poi la perdita di rete"): ("un_polo_saldato/2", 3),
    ("K2-K4", "NO saldato, poi U502 spento"): ("un_polo_saldato/2", 3),
    ("K2-K4", "NO saldato, poi U501 spento"): ("un_polo_saldato/2", 3),
}

_GREZZO_P = "il sorvegliante muta entro 1 ms, ma il rail passa 10,6 V prima del jack (D510 / D511 " \
            "scaricano la tenuta nel corto); nel telaio il fusibile del modulo IEC apre dopo qualche semionda"
_GREZZO_M = _GREZZO_P + "; U502 con l'uscita sopra l'ingresso oltre i -0,3 V del massimo assoluto (SBVS169D)"
_SOVRA = "il rail fuori tolleranza, nessuno lo vede"
_MUTE = "il mute non si inserisce: latente fino all'evento"

# per SIMULATED case: (detection, minimum severity, note, remedy)
SIM = {
    "f_j513a_aperto_mus": (3, 1, "i rail a mezz'onda: niente interviene", "nessuno"),
    "f_j513b_aperto_mus": (3, 1, "i rail a mezz'onda: niente interviene", "nessuno"),
    "f_j513ct_aperto_mus": (3, 1, "il rail - in caduta a vita dopo ~3,5 s (valli a -14,38 V): "
                            "nessun mute, nessun avviso", "presa_centrale"),
    "f_j513ct_aperto_mus6": (3, 1, "", "presa_centrale"),
    "f_d501a_corto_mus": (1, 1, _GREZZO_P, "grezzo"),
    "f_d501b_corto_mus": (1, 1, _GREZZO_P, "grezzo"),
    "f_d501c_corto_mus": (1, 5, _GREZZO_M + " (0,78-0,88 V)", "grezzo"),
    "f_d501d_corto_mus": (1, 5, _GREZZO_M + " (0,78-0,88 V)", "grezzo"),
    "f_d501a_aperto_mus": (3, 1, "", "nessuno"),
    "f_d501b_aperto_mus": (3, 1, "", "nessuno"),
    "f_d501c_aperto_mus": (3, 1, "", "nessuno"),
    "f_d501d_aperto_mus": (3, 1, "", "nessuno"),
    "f_c501_corto_mus": (1, 1, _GREZZO_P, "grezzo"),
    "f_c502_corto_mus": (1, 5, _GREZZO_M + " (1,76 V)", "grezzo"),
    "f_c501_aperto_mus": (3, 1, "0,81 V pp a 100 Hz sul rail, valli a 14,19 V: nessuno lo vede", "ondulazione"),
    "f_c502_aperto_mus": (3, 1, "0,84 V pp sul rail: nessuno lo vede", "ondulazione"),
    "f_u501_cortoio_mus": (3, 1, _SOVRA + " (+20,3 V)", "sovratensione_rail"),
    "f_u501_vset86_mus": (1, 2, "il sorvegliante muta: la musica si ferma", "nessuno"),
    "f_u501_vset142_mus": (3, 1, "", "nessuno"),
    "f_u501_vset182_mus": (3, 1, _SOVRA + " (18,2 V chiesti)", "sovratensione_rail"),
    "f_u501_vset166_mus": (3, 1, _SOVRA + " (16,6 V)", "sovratensione_rail"),
    "f_u501_vset154_mus": (3, 1, "", "nessuno"),
    "f_u501_vset152_mus": (3, 1, "", "nessuno"),
    "f_u501_vset151_mus": (3, 1, "", "nessuno"),
    "f_u501_sense_mus": (3, 1, _SOVRA + " (+20,1 V)", "sovratensione_rail"),
    "f_u502_cortoio_mus": (3, 1, _SOVRA + " (-20,3 V)", "sovratensione_rail"),
    "f_r501_aperto_mus": (3, 1, _SOVRA + " (-20,1 V)", "sovratensione_rail"),
    "f_r502_aperto_mus": (1, 2, "il sorvegliante muta: la musica si ferma", "nessuno"),
    "f_c505_aperto_perd": (3, 1, "", "nessuno"),
    "f_c506_aperto_perd": (3, 1, "", "nessuno"),
    "f_d510_aperto_perd": (3, 1, "", "nessuno"),
    "f_d511_aperto_perd": (3, 1, "", "nessuno"),
    "f_vplus_massa_mus": (1, 1, "P9 (c), accettato: picchi di 13,8 V per 0,35 ms dai rimbalzi del "
                          "contatto che si apre", "accettato"),
    "f_vminus_massa_mus": (1, 1, "P9 (c), accettato", "accettato"),
    "f_j1vp_aperto_mus": (2, 1, "il sorvegliante legge il rail dal lato dell'alimentatore: nessun "
                          "mute, 13,3 V al jack", "filo_rail"),
    "f_j1vm_aperto_mus": (2, 1, "il sorvegliante legge il rail dal lato dell'alimentatore: nessun mute",
                          "filo_rail"),
    "f_q501_corto_spegn": (3, 1, _MUTE, "mute_mancato"),
    "f_q501_corto_perd": (3, 1, _MUTE, "mute_mancato"),
    "f_q501_corto_gu502": (3, 1, _MUTE, "mute_mancato"),
    "f_q501_corto_gu501": (3, 1, _MUTE, "mute_mancato"),
    "nosald_spegnimento_l": (3, 1, _MUTE + "; il LED rosso non lo vede (ADR-028)", "no_saldato"),
    "nosald_perdita": (3, 1, _MUTE + "; il LED rosso non lo vede (ADR-028)", "no_saldato"),
    "nosald_guasto": (3, 1, _MUTE + "; il LED rosso non lo vede (ADR-028)", "no_saldato"),
    "nosald_guasto_u501": (3, 1, _MUTE + "; il LED rosso non lo vede (ADR-028)", "no_saldato"),
}

# the base cases a row may point at: (detection, minimum severity, remedy). A regulator off: the
# supervisor mutes and the music stops (L41c)
BASI_CLASSI = {"guasto": (1, 2, "nessuno"), "guasto_u501": (1, 2, "nessuno")}

# per CALCULATED row: (severity, detection, remedy)
CALC = {
    ("C507", "aperto"): (1, 3, "verifica"),
    ("C508", "aperto"): (1, 3, "nessuno"),
    ("C509", "aperto"): (1, 3, "nessuno"),
    ("C510", "aperto"): (1, 3, "nessuno"),
    ("C511", "aperto"): (1, 3, "verifica"),
    ("C512", "aperto"): (1, 3, "verifica"),
    ("C513", "aperto"): (1, 3, "nessuno"),
    ("C139-C142", "aperto"): (1, 3, "nessuno"),
    # not simulable on the two-step bench: IPOTESI prudente, severity 4 and the listener, until
    # G2's wiring says otherwise
    ("J1", "pin 2 (GND) aperto"): (4, 2, "massa"),
    # rows equal to a raw-side short on the NEGATIVE side: U502 beyond its absolute maximum
    ("C510", "corto"): (5, 1, "grezzo"),
    ("U502", "IN a massa (interno)"): (5, 1, "grezzo"),
}

RIMEDI = {
    "nessuno": "nessuno: il guasto non ha effetto, o il circuito lo mette gia' in sicurezza",
    "grezzo": "accettarlo (al jack <= 9,0 mV) o rivedere D510 / D511 (che trasformano il corto del "
              "grezzo in un corto del rail) e la protezione di U502 dall'uscita sopra l'ingresso; "
              "il fusibile del modulo IEC dimensionato a G2",
    "ondulazione": "accettarlo (al jack <= 79 uV) o un sorvegliante dell'ondulazione del grezzo",
    "presa_centrale": "accettarlo (al jack <= 0,5 uV) o far vedere al sorvegliante il punto di mezzo "
                      "dei serbatoi (una finestra sulla somma dei due rail)",
    "sovratensione_rail": "un sorvegliante della sovratensione dei rail (oggi vede solo il rail che "
                          "scende), o un limitatore; prima, leggere le tensioni massime delle parti "
                          "del blocco e la dissipazione dei finali col rail alto (NC-062, L55)",
    "accettato": "nessuno: P9 (c), il corto di un rail, accettato",
    "filo_rail": "far leggere al sorvegliante il rail dal lato della scheda audio (un filo di ritorno "
                 "del sensore), o un rivelatore di continua sulle uscite che apra il mute",
    "mute_mancato": "rivelare il mute che non si inserisce (il firmware legge MUTE_CMD) e staccare "
                    "VRELAY alla scheda audio (Q505); o due interruttori in serie sul comando del "
                    "jack - lo stesso rimedio di Q501 gate-drain (L45c2)",
    "no_saldato": "un contatto in serie che il guasto non salda (i rele' di mute doppi), o leggere il "
                  "jack invece del comando (ADR-028: il LED rosso non lo vede)",
    "verifica": "da verificare: la stabilita' del regolatore senza il condensatore (datasheet), al banco di G2",
    "massa": "da verificare col cablaggio di G2 (la massa della scheda audio, NC-044)",
}

FUNZIONE = [
    (("J513", "D501", "C501", "C502", "C509", "C510"), "il secondario, il ponte e i serbatoi"),
    (("U501", "U502", "U501, U502", "R501", "R502", "C507", "C508", "C513"), "i regolatori dei rail"),
    (("C505", "C506", "C511", "C512", "D510", "D511"), "la tenuta e la protezione dei regolatori"),
    (("C139", "C140", "C141", "C142", "C139-C142"), "il disaccoppiamento dei blocchi"),
    (("J1",), "il cablaggio dei rail fra le due schede"),
    (("Q501", "K2-K4"), "il mute che non si inserisce"),
]


def funzione(ref, modo):
    for refs, f in FUNZIONE:
        if ref in refs:
            return f
    return ""
