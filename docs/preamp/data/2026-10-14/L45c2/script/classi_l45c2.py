#!/usr/bin/env python3
"""L45c2: the classification data of ADR-070 for the relay line's FMEA, read by tabella_l45c2.py.
Data only (solo stdlib).

THE RATES (the user's choice, 2026-10-14, «Stima dichiarata»): SN 29500 parts 3-4 and FMD-2016 are
not public. So:
  - integrated circuits: the SN 29500-2 reference rate that the maker's functional-safety report
    gives for the part or its nearest sibling (tassi/fonti.md);
  - passive and discrete parts: an ORDER OF MAGNITUDE, declared as an estimate (STIMA), at the
    hot chassis (60 C air, ADR-021). The classes of ADR-070 are decades: a factor 2-3 seldom moves
    a row, and L45d replaces these with table values if the standard is bought;
  - the split among the modes: MIL-HDBK-338B Table 7.8-1 (from FMD-91, FMD-2016's predecessor;
    tassi/mil_hdbk_338b_tab_7_8_1.txt), or the maker's own distribution where it gives one.
"""

# tipo: (FIT of the part, source, {mode key: fraction})
TIPI = {
    "R":      (0.5, "STIMA (resistenza a film SMD)",
               {"aperto": 0.59, "deriva": 0.36, "corto": 0.05}),
    "C_cer":  (1.0, "STIMA (ceramico SMD)",
               {"corto": 0.49, "valore": 0.29, "aperto": 0.22}),
    "C_el":   (10.0, "STIMA (elettrolitico in alluminio, 60 C d'aria)",
               {"corto": 0.53, "aperto": 0.35, "perdita": 0.10, "capacita": 0.02}),
    "D_seg":  (1.0, "STIMA (diodo di segnale)",
               {"deriva": 0.58, "aperto": 0.24, "corto": 0.18}),
    "D_rett": (2.0, "STIMA (raddrizzatore / Schottky, per diodo)",
               {"corto": 0.51, "aperto": 0.29, "deriva": 0.20}),
    "D_zen":  (2.0, "STIMA (zener di bloccaggio)",
               {"aperto": 0.45, "deriva": 0.35, "corto": 0.20}),
    # Transistor, FET (338B): short .51, output low .22, parameter change .17, open .05, output
    # high .05. For a switch: stuck ON = short D-S (.51 less the gate's .10) + output low (.22);
    # stuck OFF = open (.05) + output high (.05); the gate's shorts G-S / G-D .05 each (ASSUMED
    # split of the .51)
    "FET":    (3.0, "STIMA (MOSFET di segnale)",
               {"on": 0.41 + 0.22, "off": 0.05 + 0.05, "gs": 0.05, "gd": 0.05, "deriva": 0.17}),
    "BJT":    (2.0, "STIMA (bipolare di segnale)", {"corto": 0.73, "aperto": 0.27}),
    # TI SFFS612 (TPS748A-Q1): SN 29500-2 table 4, "power amplifier and regulator > 1 W (LDO)",
    # 100 FIT at 90 C virtual junction; halved for U503 / U504 (< 1 W, cooler): STIMA. Die FMD of
    # the same report: no output 35 %, output follows input 10 %, out of specification 45 %,
    # PG 5 % (no PG here), any two pins shorted 5 %
    "LDO":    (50.0, "TI SFFS612 (SN 29500-2 tab. 4: 100 FIT a 90 C), dimezzato: STIMA",
               {"spento": 0.35, "segue": 0.10, "fuori": 0.45, "pin": 0.05}),
    # TI SFFS282 (TLV1812/1822-Q1): SN 29500-2 table 4, 12 FIT at 55 C, the dual part; FMD: out
    # open 15 %, saturate high 25 %, saturate low 25 %, out of specification 30 %, short any two
    # pins 5 %. For an open-drain output, high = released: blind = 15 + 25 %. Per channel: half
    "CMP":    (12.0, "TI SFFS282 (SN 29500-2 tab. 4: 12 FIT a 55 C, il doppio; parente del TLV1702)",
               {"cieco": 0.40 / 2, "basso": 0.25 / 2, "fuori": 0.30 / 2, "pin": 0.05}),
    # TI SNOAA48A (LM4040-N-Q1): SN 29500-2 table 5, 20 FIT at 55 C; open / short split from 338B
    # "Diode, Zener, Voltage Reference" (the die FMD of the report is parametric only)
    "REF":    (20.0, "TI SNOAA48A (SN 29500-2 tab. 5: 20 FIT a 55 C)",
               {"deriva": 0.69, "aperto": 0.18, "corto": 0.13}),
    # Relay (338B): fails to trip .55, spurious trip .26, short .19. ASSUMED split of "fails to
    # trip": the coil open .25, a pole welded .27, both poles welded .03
    "RELE":   (20.0, "STIMA (rele' di potenza, poche manovre)",
               {"bobina_aperta": 0.25, "un_polo_saldato": 0.27, "due_poli_saldati": 0.03,
                "polo_aperto": 0.26, "bobina_corto": 0.19}),
    "TRAFO":  (10.0, "STIMA (piccolo toroidale)", {"aperto": 0.42, "corto": 0.42, "deriva": 0.16}),
    "FUSE":   (5.0, "STIMA (fusibile ritardato)",
               {"non_apre": 0.49, "lento": 0.43, "apre": 0.08}),
    "CONN":   (0.5, "STIMA (per contatto o filo del cablaggio)",
               {"aperto": 0.61, "intermittente": 0.23, "corto": 0.16}),
    "RAME":   (0.05, "STIMA (rame del circuito stampato)", {"aperto": 0.76, "corto": 0.24}),
}

ELETTROLITICI = {"C520", "C523"}


def tipo_di(ref):
    if ref.startswith("R"):
        return "R"
    if ref.startswith("C"):
        return "C_el" if ref in ELETTROLITICI else "C_cer"
    if ref in ("D503", "D504", "D510", "D511", "D512"):
        return "D_rett"
    if ref in ("D507", "D509"):
        return "D_zen"
    if ref.startswith("D"):
        return "D_seg"
    if ref in ("Q501", "Q502", "Q503", "Q505", "Q506"):
        return "FET"
    if ref == "Q504":
        return "BJT"
    if ref in ("U503", "U504"):
        return "LDO"
    if ref in ("U505", "U506", "U508"):
        return "CMP"
    return {"U507": "REF", "K501": "RELE", "T2": "TRAFO", "F501": "FUSE", "J514": "CONN",
            "J2": "CONN", "J1": "CONN", "NT501": "RAME"}.get(ref)


# the fraction of the part's rate in each mode, by (ref, mode) as modi.py writes it; a missing
# row falls to the rules of frazione() in tabella_l45c2.py
FRAZIONE = {
    ("T2", "secondario aperto (o F501, J514, primario)"): ("aperto", 1),
    ("T2", "spire in corto / secondario in corto"): ("corto", 1),
    ("D503", "un diodo in corto"): ("corto", 1),
    ("D503", "un diodo aperto"): ("aperto", 1),
    ("D503", "gli altri tre diodi in corto"): ("corto", 3),
    ("D503", "gli altri tre diodi aperti"): ("aperto", 3),
    ("U503", "IN-OUT in corto"): ("segue", 1),
    ("U503", "spento (uscita aperta, EN)"): ("spento", 1),
    ("U503", "uscita a massa (interno)"): ("pin", 1),
    ("U503", "IN a massa (interno)"): ("pin", 1),
    ("U504", "spento (V5 persa)"): ("spento", 1),
    ("U504", "IN-OUT in corto"): ("segue", 1),
    ("U504", "uscita a massa / EN"): ("pin", 1),
    ("F501", "in corto (o sovradimensionato)"): ("non_apre", 1),
    ("F501", "aperto"): ("apre", 1),
    ("J514", "un filo aperto"): ("aperto", 2),
    ("K501", "bobina aperta"): ("bobina_aperta", 1),
    ("K501", "bobina in corto"): ("bobina_corto", 1),
    ("K501", "un polo saldato"): ("un_polo_saldato", 1),
    ("K501", "i due poli saldati"): ("due_poli_saldati", 1),
    ("K501", "un polo aperto"): ("polo_aperto", 1),
    ("U505", "un'uscita bloccata bassa"): ("basso", 2),
    ("U505", "alimentazione (pin 8) aperta"): ("pin", 1),
    ("U506", "canale A bloccato basso / B bloccato basso"): ("basso", 2),
    ("U506", "alimentazione aperta"): ("pin", 1),
    ("U508", "canale B cieco / alimentazione aperta"): ("cieco", 1),
    ("R544-R547", "aperto"): ("aperto", 4),
    ("R544-R547", "corto"): ("corto", 4),
}
# U503's set point: SBVS204G's pins - ANY-OUT pins, SENSE, EN - share the LDO's "out of
# specification" 45 % (ASSUMED: evenly over the 8 rows that are a set point)
N_FUORI_U503 = 8

# ---- per SIMULATED case: (detection, minimum severity, note, remedy). Detection (ADR-070): 1 the
# circuit sees it and makes it safe, 2 the listener sees it at once, 3 latent. The minimum severity
# is what the measured peak cannot show: 2 when a function is lost (the music stops, a command
# fails), 5 when a part goes beyond its limits (PR-22)
SIM = {
    "f_base_niente_ins": (None, None, "", ""),
    "f_t2_aperto_mus": (1, 2, "il rivelatore di rete muta; la musica si ferma", "nessuno"),
    "f_d503a_corto_mus": (1, 2, "niente al jack nella corsa; T2 in corto a ogni altra semionda "
                          "finche' F501 apre, poi = T2 aperto: il rivelatore muta", "fusibile"),
    "f_d503a_aperto_mus": (3, 1, "mezz'onda: il rivelatore non scatta, niente al jack", "nessuno"),
    "f_d504_aperto_mus": (1, 2, "VRELAY_REG cala in 128 ms, il sorvegliante di VRELAY muta", "nessuno"),
    "f_d504_corto_perd": (3, 1, "il rivelatore cieco: alla perdita di rete muta il sorvegliante "
                          "dei rail a 89 ms, il jack prima di 10,6 V", "cieco"),
    "f_c520_aperto_mus": (3, 1, "valle di VRELAY_REG a 11,65 V, sopra la soglia di 11,0 V: a rete "
                          "-10 % da verificare (un mute che va e viene?)", "verifica"),
    "f_c520_aperto_perd": (3, 1, "", "nessuno"),
    "f_c520_corto_mus": (1, 2, "VRELAY_REG scaricata in 0,2 ms attraverso D512: Delta perso; T2 "
                         "in corto finche' F501 apre", "delta"),
    "f_u503_cortoio_mus": (3, 1, "VRELAY a 14,7 V a rete nominale (bobine, U504 entro i limiti); "
                           "a rete +10 % e in standby di piu': U504 verso i suoi 16 V", "sovratensione"),
    "f_u503_vset56_mus": (1, 2, "", "nessuno"),
    "f_u503_vset88_mus": (1, 2, "", "nessuno"),
    "f_u503_vset112_mus": (3, 1, "VRELAY a 11,2 V: 0,2 V sopra la soglia, bobine a 11,2 V", "nessuno"),
    "f_u503_vset136_mus": (3, 1, "VRELAY a 13,6 V", "nessuno"),
    "f_c523_aperto_gu503": (3, 1, "la tenuta dopo U503 persa: a U503 spento tutte le bobine "
                            "insieme, Delta perso", "delta"),
    "f_c523_aperto_perd": (3, 1, "", "nessuno"),
    "f_d512_aperto_perd": (3, 1, "", "nessuno"),
    "f_u504_spento_mus": (1, 2, "V5 persa: MUTE_G e PERMIT_G cadono insieme, Delta perso", "delta"),
    "f_q505_aperto_mus": (1, 2, "la scheda audio perde VRELAY: tutte le bobine insieme, Delta "
                          "perso", "delta"),
    "f_q505_corto_spegn": (3, 2, "VRELAY resta alla scheda audio in standby: ~1 W da T2 contro "
                           "0,5 W di P9 (a) (stima dal carico del banco, 88 mA a 12 V)", "standby"),
    "f_q505_gd_mus": (3, 1, "VRELAY a 10,76 V, sopra i 9,6 V di eccitazione", "nessuno"),
    "f_q506_aperto_mus": (1, 2, "Q505 si spegne col fronte di C531: tutte le bobine insieme, il "
                          "guadagno 4,3 ms prima del jack", "delta"),
    "f_r506_aperto_mus": (1, 2, "il mute falso: la musica si ferma, in sicurezza", "mute_falso"),
    "f_u505a_cieco_gu501": (3, 1, "il firmware fa da riserva (legge il rail dall'ADC) e muta 2,2 ms "
                            "dopo la soglia: fuori per la sola clausola di 1 ms; jack prima di "
                            "10,6 V, 38 dB SPL", "cieco"),
    "f_u505b_cieco_gu502": (3, 1, "come il canale A, sul rail -", "cieco"),
    "f_u507_aperto_mus": (1, 2, "VREF a ~4,5 V: il mute falso, e il permesso cade 0,5 ms prima "
                          "del jack (Delta perso)", "delta"),
    "f_u507_corto_mus": (1, 2, "VREF a 0: il rivelatore di rete muta (il mute falso); il permesso "
                         "resta", "mute_falso"),
    "f_q504_corto_perd": (3, 1, "il rivelatore cieco: muta il sorvegliante dei rail", "cieco"),
    "f_c518_aperto_mus": (1, 2, "il mute falso (MD sale a ogni semionda)", "mute_falso"),
    "f_u506b_cieco_gu503": (3, 1, "a U503 spento muta il firmware (16 ms), Delta resta", "cieco"),
    "f_c528_aperto_gu503": (3, 1, "Delta perso: lo mostra un mute in hardware", "delta_latente"),
    "f_c528_corto_mus": (1, 2, "il permesso cade, D522 tira giu' MUTE_G: Delta perso", "delta"),
    "f_r534_aperto_spegn": (3, 2, "il permesso non si rilascia col mute: guadagno e trim non si "
                            "cambiano in mute (funzione)", "funzione"),
    "f_c529_aperto_perd": (3, 1, "", "nessuno"),
    "f_d520_corto_ins": (3, 1, "Delta perso a OGNI mute: PERMIT_T si scarica in MUTE_REQ", "delta_latente"),
    "f_d520_corto_spegn": (3, 1, "Delta perso anche allo spegnimento", "delta_latente"),
    "f_d524_corto_spegn": (3, 1, "", "nessuno"),
    "f_r524_aperto_mus": (3, 1, "niente: PERMIT_G resta tenuto da MUTE_G attraverso D522", "delta_latente"),
    "f_r524_aperto_ins": (3, 1, "Delta perso a ogni mute: il permesso cade con MUTE_G", "delta_latente"),
    "f_q501_gd_perd": (3, 1, "il mute non si inserisce: il jack si apre solo quando cade VRELAY, "
                       "685 ms dopo la perdita di rete (come Q501 in corto, L45c1)", "mute_mancato"),
    "f_q501_gd_spegn": (3, 1, "il jack si apre 213 ms dopo lo spegnimento, il guadagno 145 ms "
                        "prima", "mute_mancato"),
    "f_d506_corto_mus": (1, 5, "VRELAY in corto attraverso lo zener D507 in diretta e Q501: U503 al "
                         "limite (~1 A) per ~20 ms finche' il sorvegliante di VRELAY muta; Q501 "
                         "(2N7002, 115 mA continui) oltre i suoi limiti", "sovraccarico"),
    "f_q502_aperto_mus": (2, 2, "K6 cade col jack chiuso: il guadagno torna a 0 dB durante la "
                          "musica (6,4 mV)", "delta"),
    "f_q502_gd_mus": (1, 2, "MUTE_G limitato da D522 a ~1,5 V: il jack si apre (il mute falso)", "mute_falso"),
    "f_q503_aperto_mus": (1, 2, "il toroidale si stacca: i rail calano, muta il sorvegliante", "nessuno"),
    "f_d505_corto_mus": (1, 5, "VRELAY_REG a massa attraverso Q503 (~1 A al limite di U503) finche' "
                         "il firmware abbassa MAINS_REQ: Q503 oltre i suoi limiti; Delta perso", "sovraccarico"),
    "f_r513_corto_perd": (3, 1, "", "nessuno"),
    "f_r513_corto_gu501": (3, 1, "", "nessuno"),
    "f_d522_corto_perd": (3, 1, "Delta perso: MUTE_G e PERMIT_G legati (il ruolo di D522 e' di L54)",
                          "delta_latente"),
    "f_d522_corto_ins": (3, 1, "Delta perso a ogni mute, e il jack si apre a 71 ms invece di 31", "delta_latente"),
}

# ---- per CALCULATED row (no run, no case of reference): (severity, detection, remedy)
CALC = {
    ("F501", "in corto (o sovradimensionato)"): (5, 3, "fusibile"),
    ("C521", "aperto"): (1, 3, "verifica"),
    ("C522", "aperto"): (1, 3, "nessuno"),
    ("U503", "pin 11 (0,2 V) aperto"): (1, 3, "nessuno"),
    ("U503", "pin 10 (0,4 V) / 12 (0,1 V) a massa"): (1, 3, "nessuno"),
    ("C524", "aperto"): (1, 3, "nessuno"),
    ("C525", "aperto"): (1, 3, "verifica"),
    ("U504", "IN-OUT in corto"): (5, 2, "sovratensione"),
    ("J2", "il filo RLY_RET aperto"): (2, 2, "funzione"),
    ("NT501", "corto"): (1, 3, "nessuno"),
    ("NT501", "aperto (la stella)"): (2, 1, "mute_falso"),
    ("R539", "corto"): (1, 3, "verifica"),
    ("C531", "aperto"): (1, 3, "nessuno"),
    ("C515", "aperto"): (1, 3, "nessuno"),
    ("C516", "aperto"): (1, 3, "nessuno"),
    ("C514", "aperto"): (1, 3, "nessuno"),
    ("R511", "aperto"): (1, 3, "nessuno"),
    ("C526", "aperto"): (1, 3, "nessuno"),
    ("C517", "aperto"): (1, 3, "nessuno"),
    ("C519", "aperto"): (1, 3, "nessuno"),
    ("C530", "aperto"): (1, 3, "nessuno"),
    ("D520", "aperto"): (1, 3, "nessuno"),
    ("D521", "aperto"): (1, 3, "nessuno"),
    ("D521", "corto"): (1, 3, "delta_latente"),
    ("R532", "aperto"): (1, 3, "nessuno"),
    ("R533", "aperto"): (1, 3, "nessuno"),
    ("R532", "corto"): (1, 3, "nessuno"),
    ("R533", "corto"): (1, 3, "nessuno"),
    ("D523", "aperto"): (1, 3, "nessuno"),
    ("D523", "corto"): (1, 3, "nessuno"),
    ("D524", "aperto"): (2, 2, "funzione"),
    ("R535", "aperto"): (2, 2, "funzione"),
    ("R535", "corto"): (1, 3, "nessuno"),
    ("R524", "corto"): (2, 2, "funzione"),
    ("R516", "aperto"): (1, 3, "nessuno"),
    ("R538", "aperto"): (1, 3, "nessuno"),
    ("D506", "aperto"): (1, 3, "sovraccarico"),
    ("D507", "aperto"): (1, 3, "sovraccarico"),
    ("D507", "corto"): (1, 3, "verifica"),
    ("D508", "aperto"): (1, 3, "sovraccarico"),
    ("D509", "aperto"): (1, 3, "sovraccarico"),
    ("D509", "corto"): (1, 3, "nessuno"),
    ("Q502", "corto D-S"): (2, 2, "funzione"),
    ("Q503", "corto D-S"): (2, 2, "standby"),
    ("D505", "aperto"): (1, 3, "sovraccarico"),
    ("R514", "aperto"): (1, 3, "nessuno"),
    ("C527", "aperto"): (1, 3, "nessuno"),
    ("D522", "aperto"): (1, 3, "L54"),
    ("R520", "corto"): (1, 3, "nessuno"),
    ("R521", "aperto"): (1, 3, "nessuno"),
    ("K501", "un polo saldato"): (1, 3, "nessuno"),
    ("R525", "aperto"): (1, 3, "nessuno"),
    ("R526", "aperto"): (1, 3, "nessuno"),
    ("R526", "corto"): (1, 3, "L54"),
    ("R527", "aperto"): (1, 3, "nessuno"),
    ("R527", "corto"): (2, 2, "L54"),
    ("R528", "aperto"): (1, 3, "nessuno"),
    ("R541", "aperto"): (2, 2, "funzione"),
    ("R541", "corto"): (1, 3, "nessuno"),
    ("C532", "corto"): (2, 2, "funzione"),
    ("C532", "aperto"): (1, 3, "nessuno"),
    ("R542", "aperto"): (2, 2, "funzione"),
    ("R542", "corto"): (1, 3, "nessuno"),
    ("C533", "corto"): (2, 2, "funzione"),
    ("C533", "aperto"): (1, 3, "nessuno"),
    ("R517", "aperto"): (2, 2, "funzione"),
    ("R518", "aperto"): (2, 2, "funzione"),
    ("R543", "aperto"): (1, 3, "nessuno"),
    ("R543", "corto"): (1, 3, "L54"),
    ("R544-R547", "aperto"): (1, 3, "nessuno"),
    ("R544-R547", "corto"): (1, 3, "L54"),
    # rows that point at another calculated row
    ("U508", "canale A cieco"): (2, 2, "funzione"),
    ("K501", "i due poli saldati"): (2, 2, "standby"),
    # rows that point at a case but change what it does
    ("R503", "corto"): (5, 1, "sovraccarico"),
    ("R510", "corto"): (5, 1, "sovraccarico"),
    ("R512", "corto"): (5, 1, "sovraccarico"),
    ("T2", "spire in corto / secondario in corto"): (2, 1, "fusibile"),
    ("C528", "aperto (durante la musica)"): (3, 3, "delta_latente"),
}

RIMEDI = {
    "nessuno": "nessuno: il guasto non ha effetto, o il circuito lo mette gia' in sicurezza",
    "mute_falso": "nessuno: il guasto mette in sicurezza (il mute); al piu' una diagnostica",
    "funzione": "nessuno nel circuito: si vede e si ripara",
    "cieco": "un autotest all'accensione (il firmware forza e legge il sorvegliante); oggi il "
             "firmware fa da riserva leggendo i rail dall'ADC",
    "delta": "accettarlo come il corto della linea a 12 V (ADR-051, 6,4 mV); o un permesso che non "
             "dipenda da VRELAY ne' da MUTE_G (una tenuta locale per K6 e i rele' di guadagno)",
    "delta_latente": "un controllo di Delta a ogni mute (il firmware legge PERMIT_G e il jack); o "
                     "rendere ridondante la parte che lo porta",
    "mute_mancato": "rivelare il mute che non si inserisce (il firmware legge MUTE_CMD) e staccare "
                    "VRELAY alla scheda audio (Q505); o due interruttori in serie sul comando del "
                    "jack - lo stesso rimedio di Q501 in corto (L45c1)",
    "sovraccarico": "limitare la corrente sul comando (una resistenza o un fusibile ripristinabile "
                    "nel ramo del clamp, o su VRELAY); scegliere un MOSFET che regga il limite di U503",
    "sovratensione": "un limitatore sulla V5 (zener o TVS con un fusibile ripristinabile), o un "
                     "sorvegliante della sovratensione di VRELAY_REG",
    "standby": "accettarlo (e' consumo, non colpo) o far leggere al firmware VRELAY e il "
               "toroidale in standby",
    "fusibile": "il fusibile dimensionato e provato dal datasheet di T2 (G2): niente nel circuito",
    "verifica": "da verificare: a rete -10 % / dal datasheet (stabilita' o tensione massima)",
    "L54": "del riesame del micro e dello standby (L54)",
}
