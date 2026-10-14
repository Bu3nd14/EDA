#!/usr/bin/env python3
"""L45d1: the ADR-070 classes of L45b's table (the faults of the controls), one entry per row n of
L45b/fmea_controlli.csv, read by riporto_l45b.py. Data only (solo stdlib). The rates are tipi.py's.

Each classified row: (terms, minimum severity, detection, remedy, note). The terms are the parts the
row stands for, (type, the mode's key in TIPI, how many), and the row's rate is their sum: a row of
L45b may name several parts (K13-K16, "R1, R2, LED"), and the relays serve both channels (one pole
each), so they count once. Instances (IPOTESI where the source does not say): four inputs x two
channels = 8 (C_IN, R_SEL, R_J); three outputs x two channels = 6 (C_OUT, the bleeds, the 47 Ohm),
of which 2 main and 4 fixed; C_T 2; the panel LEDs of trim and gain 6 (three each).

Where two rows of L45b share one 338B class of the same relays (an open pole and a bounce are both
"spurious trip"), each gets the whole class: the rate is an upper bound, and it moves a class at
most a factor 2. Where two rows split a class between them (a welded NO and a welded NC), each gets
half: un_polo_saldato/2.

A cross-reference (RIMANDO) has no class here: the mode is classified where it was measured on the
real bench (L45c1, L45c2), or belongs to another lot (the micro: L54), or has no part (the LDRs).
"""
from tipi import TIPI  # noqa: F401  (riporto_l45b reads K.TIPI)

R = "RELE_S"
TUTTI = "bobina_aperta+un_polo_saldato+due_poli_saldati+spurio+bobina_corto+isolamento"

RIMANDO = {
    43: "L45c1 (nosald_*): il NO saldato sul banco vero, con lo spegnimento, la perdita di rete e i "
        "regolatori spenti",
    51: "L45c1 (f_q501_corto_*): Q501 in corto sul banco vero",
    52: "L45c2: Q501 aperto (D-S) / gate aperto",
    53: "L45c2: Q502 corto D-S",
    54: "L45c2: Q502 aperto (D-S)",
    55: "L45c2: D522 in corto, con la perdita di rete e il mute dal tasto",
    56: "L45c2: R513, R514, R516, R524-R526, C527 riga per riga",
    59: "le righe 19, 27, 54: e' un effetto, non un modo",
    73: "nessuna parte: le LDR non ci sono piu' (ADR-062)",
    74: "L54: il riesame del micro (nessun tasso, come in L45c2)",
    75: "L54: il riesame del micro",
    76: "L54: il riesame del micro",
    77: "L54: il riesame del micro",
    78: "L54: il riesame del micro",
}

# n: (terms, minimum severity, detection, remedy, note)
CLASSI = {
    1: ([(R, "bobina_aperta", 4)], 2, 2, "funzione", "l'ingresso tace"),
    2: ([(R, "bobina_corto", 4)], 2, 1, "linea12", ""),
    3: ([(R, "un_polo_saldato", 4)], 1, 3, "nessuno", ""),
    4: ([(R, "spurio", 4)], 2, 2, "funzione", ""),
    5: ([(R, "spurio", 4)], 1, 3, "nessuno", ""),
    6: ([(R, "isolamento", 4)], 1, 2, "isolamento", ""),
    7: ([(R, "isolamento", 4)], 1, 2, "isolamento", "variante della riga 6 (1 kOhm): lo stesso modo"),
    8: ([("D_seg", "corto", 4)], 2, 1, "linea12", ""),
    9: ([("D_seg", "aperto", 4)], 1, 3, "nessuno", ""),
    10: ([("ROT", "uscita_errata", 1)], 2, 2, "funzione", ""),
    11: ([(R, "bobina_aperta", 4)], 2, 2, "funzione", ""),
    12: ([(R, "bobina_corto", 4)], 2, 1, "linea12", ""),
    13: ([(R, "un_polo_saldato", 2)], 2, 2, "pr18", "un canale 3 (o 10) dB sopra l'altro: si sente"),
    14: ([(R, "spurio", 2)], 2, 2, "funzione", ""),
    15: ([(R, "spurio", 2)], 1, 2, "nessuno", ""),
    16: ([(R, "isolamento", 2)], 2, 1, "linea12", ""),
    17: ([(R, "un_polo_saldato/2", 2)], 2, 2, "pr18", ""),
    18: ([(R, "un_polo_saldato/2", 2), (R, "spurio", 2)], 2, 2, "funzione", ""),
    19: ([("D_rett", "corto", 2)], 2, 2, "led_mute", "il LED rosso acceso con la musica"),
    20: ([("D_rett", "aperto", 2)], 2, 2, "funzione", ""),
    21: ([("D_seg", "corto", 2)], 2, 2, "pr18", ""),
    22: ([("D_seg", "aperto", 2)], 2, 2, "funzione", ""),
    23: ([("D_seg", "corto", 2)], 2, 1, "linea12", ""),
    24: ([("D_seg", "aperto", 2)], 1, 3, "nessuno", ""),
    25: ([("ROT", "uscita_errata", 1)], 2, 2, "funzione", ""),
    26: ([("ROT", "contatto", 1)], 2, 2, "funzione", ""),
    27: ([(R, "bobina_aperta", 1)], 2, 2, "permesso", "il LED rosso acceso con la musica"),
    28: ([(R, "bobina_corto", 1)], 2, 1, "linea12", ""),
    29: ([(R, "un_polo_saldato/2", 1)], 1, 3, "nessuno", "latente: col secondo NC, la riga 27"),
    30: ([(R, "un_polo_saldato/2", 1)], 2, 2, "funzione", ""),
    31: ([(R, "spurio", 1)], 2, 2, "funzione", ""),
    32: ([("D_seg", "corto", 1)], 2, 1, "linea12", ""),
    33: ([(R, "bobina_aperta", 2)], 2, 2, "funzione", ""),
    34: ([(R, "bobina_corto", 2), ("D_zen", "corto", 2)], 2, 1, "linea12", ""),
    35: ([(R, "un_polo_saldato", 2)], 2, 2, "funzione", "fino a 12 dB fra i canali"),
    36: ([(R, "spurio", 1)], 2, 2, "funzione", ""),
    37: ([(R, "spurio", 2)], 1, 2, "pr17", "il trim cambia fuori mute"),
    38: ([(R, "isolamento", 2)], 1, 2, "isolamento", "corsa al limite superiore (L45b)"),
    39: ([(R, TUTTI, 2)], 2, 2, "funzione", ""),
    40: ([("ROT", "uscita_errata+contatto", 1)], 2, 2, "funzione", ""),
    41: ([(R, "bobina_aperta", 3)], 2, 2, "funzione", "il polo che si apre e' la riga 45"),
    42: ([(R, "bobina_corto", 3)], 2, 1, "linea12", ""),
    44: ([(R, "un_polo_saldato/2", 3)], 2, 2, "funzione", ""),
    45: ([(R, "spurio", 3)], 2, 2, "funzione", ""),
    46: ([(R, "spurio", 3)], 1, 3, "nessuno", ""),
    # the main jack's relay and the Singxer's (IPOTESI: like the main's), the Stax's is row 50
    47: ([(R, "isolamento/2", 2)], 1, 2, "isolamento", "anche a mute inserito"),
    48: ([(R, "isolamento/2", 2)], 1, 2, "isolamento", "variante della riga 47 (1 kOhm): lo stesso modo"),
    49: ([(R, "isolamento/2", 3)], 1, 2, "isolamento", ""),
    50: ([(R, "isolamento/2", 1)], 1, 2, "isolamento", "anche a mute inserito"),
    57: ([("R", "aperto", 2), ("LED", "aperto", 6)], 2, 2, "funzione", ""),
    58: ([("R", "aperto", 1), ("LED", "aperto", 1)], 2, 2, "funzione", ""),
    60: ([("C_film", "corto", 2)], 1, 3, "uscita_continua", ""),
    61: ([("C_film", "corto", 4)], 1, 3, "uscita_continua", ""),
    62: ([("C_film", "aperto", 6)], 2, 2, "funzione", ""),
    63: ([("C_film", "corto", 2)], 1, 2, "volume", ""),
    64: ([("C_film", "aperto", 2)], 2, 2, "funzione", ""),
    65: ([("C_film", "corto", 8)], 1, 3, "nessuno", "con una sorgente sana (<= 0,65 V di continua, ADR-064)"),
    # no figure in L45b: a step up to the source's DC at the next change of input; a sound source
    # (<= 0,65 V, ADR-064) keeps it under the ceiling, not under 2 mV
    66: ([("R", "aperto", 8)], 3, 3, "nessuno", "gravita' dichiarata: il gradino fino alla continua della sorgente"),
    67: ([("R", "aperto", 8)], 1, 3, "nessuno", ""),
    68: ([("R", "aperto", 6)], 1, 3, "nessuno", ""),
    69: ([("R", "aperto", 6)], 1, 3, "nessuno", ""),
    70: ([("R", "corto", 6)], 1, 3, "p7", ""),
    71: ([("R", "aperto", 6)], 2, 2, "funzione", ""),
    72: ([("R", "aperto+corto", 6)], 2, 2, "funzione", ""),
}

RIMEDI = {
    "nessuno": "nessuno: il guasto non ha effetto, o il circuito lo mette gia' in sicurezza",
    "funzione": "nessuno nel circuito: si vede e si ripara",
    "linea12": "nessuno: e' la classe del corto della linea a 12 V, accettata da ADR-051 (<= 29,7 mV)",
    "isolamento": "un rele' con isolamento rinforzato fra bobina e contatti (dal datasheet del G6K), o "
                  "togliere VRELAY quando un'uscita ha continua (oggi nessun mute lo toglie: sul rele' "
                  "di mute la bobina rilasciata ha i due capi a 12 V)",
    "pr18": "accettarlo dichiarato (il guadagno resta sopra quello della manopola, senza colpo; PR-18) "
            "o far leggere lo stato vero dei contatti del guadagno",
    "pr17": "accettarlo dichiarato (un cambio di trim fuori mute, ~61 dB SPL; PR-17) o rileggere lo "
            "stato dei bistabili",
    "led_mute": "far leggere al LED rosso lo stato del jack invece di VTRIM (ADR-028), o accettarlo "
                "dichiarato",
    "permesso": "leggere lo stato vero di K6 (il firmware, o il LED rosso dal contatto), o accettarlo: "
                "guadagno e trim si muovono fuori mute (il «Da riaprire se» di ADR-027)",
    "uscita_continua": "un guasto doppio: da solo e' un colpo piccolo, ma l'uscita resta accoppiata in "
                       "continua e un guasto del blocco poi non decade (P10 senza fine); un rivelatore "
                       "di continua sulle uscite lo coprirebbe",
    "volume": "accettarlo: tornano i passi del volume (fino a 19,5 mV, ~79 dB SPL, L48b)",
    "p7": "la protezione dal corto senza la sua resistenza: da riguardare col dispositivo d'uscita (L55)",
}

GRUPPI = {  # the group of L45b's table, shortened for the 'funzione' column
    "Selettore": "il selettore d'ingresso", "Guadagno": "il guadagno e la sua tenuta",
    "Permesso": "il permesso e il trim", "Mute": "il mute e i suoi comandi", "LED": "i LED",
    "Condensatori": "il percorso del segnale (condensatori, bleed, resistenze)",
    "Firmware": "il firmware e il micro",
}
