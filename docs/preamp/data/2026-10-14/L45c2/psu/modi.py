#!/usr/bin/env python3
"""L45c2: the single faults of the supply's RELAY LINE AND COMMANDS, one row per mode.

The second half of L45c (the user's choice, 2026-10-13, «Due parti»): T2 and its rectifier, the
VRELAY regulator U503 and its hold, the logic supply U504, the star NT501 and J2; the standby
switch Q505 / Q506; the supervisors U505 / U506, the reference U507, the mains detector; the
hardware delay D (U508 and its RC); the sinks Q501-Q503 with their clamps; the mains relay K501
and F501; the micro's pull-downs and its reads. L45c1 did the audio rails.

Every row is a mode. A SIMULATED mode has a case name f_<ref>_<modo>_<evento> (no other
underscore), run by psu/corri_seq.sh on the supply bench to its fixed point with the firmware,
then on the audio board through the bridge (ponte/). A mode the bench would only repeat has
`uguale` = the case it equals, and the reason; a mode settled without a run has `calcolo`.

The primitives (genera_tb_psu.py, applica_guasto), L45c1's four plus two:
  ("corto", a, b)              10 S (0.1 ohm) between nodes a and b from the fault's instant
  ("aperto", [(line, k), ...]) token k of the deck line whose first token is `line` moved to a
                               new node, joined to the old one by 1 kS before the fault, 1 nS after
  ("vset", reg, v)             a twin of the behavioural regulator `reg` with VSET = v takes over
  ("j1", rail, c)              (L45c1, not used here)
  ("spento", reg)              L45c2: the regulator's enable to 0 at the fault's instant
  ("niente",)                  L45c2: no fault, the base case of an event L45c1 had not
Events: mus (the fault at TE during music), perd (mains lost at TE), spegn (the front switched
off at TE), ins (L45c2: SW3 to mute at TE, the mute inserted from the front), gu501 / gu502 /
gu503 (U501 / U502 / U503 off at TE). With an event other than mus the fault is LATENT: present
from t = 0, and the event is what shows it.
"""

EVENTI = {"mus": dict(front=1, sw3=1, tf=1.0),
          "perd": dict(front=1, sw3=1, buco=1000.0, tf=1.0),
          "spegn": dict(front="giu", sw3=1, tf=1.1),
          "ins": dict(front=1, sw3="giu", tf=1.0),
          "gu502": dict(front=1, sw3=1, u502=True, tf=1.0),
          "gu501": dict(front=1, sw3=1, spento="U501", tf=1.0),
          "gu503": dict(front=1, sw3=1, spento="U503", tf=1.0)}

# the end of a case, s after TE, where ngspice stops ("Timestep too small") with BOTH methods
# once everything is already off; analizza_psu.py shows, for each, the jack and the gain moved
# and the rails settled before this end (README, «Le corse accorciate»)
TF = {"f_c520_aperto_perd": 0.6,       # stopped at TE + 0.72 s (b.xu503.bi), VRELAY_REG gone
      "f_u505a_cieco_gu501": 0.9,      # stopped at TE + 0.95 s, rails at +0.0004 / -0.73 V
      "f_u507_aperto_mus": 0.9}        # stopped at TE + 0.96 s (rly_ret)

# (case, ref, mode, primitive, what it is)
SIMULATI = [
    # ---- the base case of the new event (no fault): the mute inserted from the front
    ("f_base_niente_ins", "-", "senza guasto: il mute inserito dal tasto", ("niente",),
     "il riferimento dell'evento ins"),
    # ---- T2, F501, J514 and the bridge D503
    ("f_t2_aperto_mus", "T2", "secondario aperto (o F501, J514, primario)",
     ("aperto", [("LT2_SEC_A", 2)]), "VRELAY_REG e V5 perdono la sorgente; il rivelatore di rete scatta"),
    ("f_d503a_corto_mus", "D503", "un diodo in corto", ("corto", "t2_sec_a", "rect_v"),
     "il secondario di T2 in corto a ogni altra semionda (prima che F501 apra)"),
    ("f_d503a_aperto_mus", "D503", "un diodo aperto", ("aperto", [("DD503a", 1)]),
     "mezz'onda su RECT_V: il rivelatore vede un buco di 10 ms a ogni periodo?"),
    ("f_d504_aperto_mus", "D504", "aperto", ("aperto", [("DD504", 1)]),
     "C520 non si ricarica, il rivelatore vede la rete: VRELAY_REG scende da sola"),
    ("f_d504_corto_perd", "D504", "in corto, poi la perdita di rete", ("corto", "rect_v", "raw_v"),
     "RECT_V tenuta da C520: il rivelatore di rete e' cieco"),
    # ---- the VRELAY reservoir and U503
    ("f_c520_aperto_mus", "C520", "aperto", ("aperto", [("CC520", 1)]),
     "restano i 10 uF di C522: U503 in caduta a ogni valle?"),
    ("f_c520_aperto_perd", "C520", "aperto, poi la perdita di rete", ("aperto", [("CC520", 1)]),
     "la tenuta di VRELAY senza il serbatoio"),
    ("f_c520_corto_mus", "C520", "corto", ("corto", "raw_v", "rly_ret"),
     "RAW_V a massa: D512 scarica C523 nel corto"),
    ("f_u503_cortoio_mus", "U503", "IN-OUT in corto", ("corto", "raw_v", "vrelay_reg"),
     "VRELAY_REG al grezzo: bobine e U504 a ~17 V"),
    ("f_u503_vset56_mus", "U503", "pin 4 (6,4 V) aperto", ("vset", "U503", 5.6), "VRELAY_REG a 5,6 V"),
    ("f_u503_vset88_mus", "U503", "pin 6 (3,2 V) aperto", ("vset", "U503", 8.8), "8,8 V"),
    ("f_u503_vset112_mus", "U503", "pin 9 (0,8 V) aperto", ("vset", "U503", 11.2),
     "11,2 V: sopra la soglia di 11,0 V del sorvegliante"),
    ("f_u503_vset136_mus", "U503", "pin 8 (1,6 V) a massa", ("vset", "U503", 13.6), "13,6 V"),
    ("f_c523_aperto_gu503", "C523", "aperto, poi U503 spento", ("aperto", [("CC523", 1)]),
     "la tenuta dopo U503 persa: Delta regge a U503 spento?"),
    ("f_c523_aperto_perd", "C523", "aperto, poi la perdita di rete", ("aperto", [("CC523", 1)]), ""),
    ("f_d512_aperto_perd", "D512", "aperto, poi la perdita di rete", ("aperto", [("DD512", 1)]),
     "OUT di U503 sopra IN senza il diodo?"),
    # ---- V5 and the star
    ("f_u504_spento_mus", "U504", "spento (V5 persa)", ("spento", "U504"),
     "comparatori e micro senza alimentazione: tutto cade insieme?"),
    # ---- the standby switch
    ("f_q505_aperto_mus", "Q505", "aperto (D-S)", ("aperto", [("MQ505", 1)]),
     "la scheda audio perde VRELAY: tutte le bobine insieme"),
    ("f_q505_corto_spegn", "Q505", "corto D-S, poi lo spegnimento", ("corto", "vrelay_reg", "vrelay"),
     "VRELAY resta alla scheda audio in standby"),
    ("f_q505_gd_mus", "Q505", "corto G-D", ("corto", "sw_g", "vrelay"),
     "Q505 a diodo: VRELAY una soglia sotto VRELAY_REG"),
    ("f_q506_aperto_mus", "Q506", "aperto (D-S)", ("aperto", [("MQ506", 1)]),
     "Q505 si spegne con C531 (~10 ms): tutte le bobine insieme"),
    # ---- the supervisors and the reference
    ("f_r506_aperto_mus", "R506", "aperto", ("aperto", [("RR506", 1)]),
     "SUP_P a massa: il sorvegliante del + scatta senza guasto dei rail (il mute falso)"),
    ("f_u505a_cieco_gu501", "U505", "canale A cieco (uscita aperta), poi U501 spento",
     ("aperto", [("XU505a", 3)]), "il rail + cade e nessun sorvegliante lo vede"),
    ("f_u505b_cieco_gu502", "U505", "canale B cieco (uscita aperta), poi U502 spento",
     ("aperto", [("XU505b", 3)]), "il rail - cade e nessun sorvegliante lo vede"),
    ("f_u507_aperto_mus", "U507", "aperto (VREF a ~4,5 V)", ("aperto", [("XU507", 1)]),
     "tutte le soglie si spostano insieme: mute e permesso nello stesso istante?"),
    ("f_u507_corto_mus", "U507", "corto (VREF a 0)", ("corto", "vref", "rly_ret"),
     "tutte le soglie a zero"),
    ("f_q504_corto_perd", "Q504", "corto C-E, poi la perdita di rete", ("corto", "md", "rly_ret"),
     "il rivelatore di rete cieco"),
    ("f_c518_aperto_mus", "C518", "aperto", ("aperto", [("CC518", 1)]),
     "MD sale a ogni passaggio per lo zero: il mute a impulsi?"),
    ("f_u506b_cieco_gu503", "U506", "canale B cieco (uscita aperta), poi U503 spento",
     ("aperto", [("XU506b", 3)]), "VRELAY cala e nessuno muta prima"),
    # ---- the hardware delay D
    ("f_c528_aperto_gu503", "C528", "aperto, poi U503 spento", ("aperto", [("CC528", 1)]),
     "Delta perso, VRELAY che cade"),
    ("f_c528_corto_mus", "C528", "corto", ("corto", "permit_t", "rly_ret"),
     "PERMIT_T a zero: il permesso cade, D522 tira giu' anche MUTE_G"),
    ("f_r534_aperto_spegn", "R534", "aperto, poi lo spegnimento", ("aperto", [("RR534", 1)]),
     "PERMIT_T non si scarica: il permesso e VRELAY restano"),
    ("f_c529_aperto_perd", "C529", "aperto, poi la perdita di rete", ("aperto", [("CC529", 1)]),
     "D2 perso: VRELAY spenta prima del permesso?"),
    ("f_d520_corto_ins", "D520", "corto, poi il mute dal tasto", ("corto", "pt_a", "permit_t"),
     "PERMIT_T scaricato in MUTE_REQ: Delta perso a ogni mute?"),
    ("f_d520_corto_spegn", "D520", "corto, poi lo spegnimento", ("corto", "pt_a", "permit_t"), ""),
    ("f_d524_corto_spegn", "D524", "corto, poi lo spegnimento", ("corto", "ve_a", "vr_t"),
     "VR_T scaricato in VRELAY_EN: D2 perso?"),
    ("f_r524_aperto_mus", "R524", "aperto", ("aperto", [("RR524", 1)]),
     "PERMIT_G senza pull-up: il permesso cade durante la musica?"),
    # the first run: nothing at once - PERMIT_G is held at ~4 V by MUTE_G through D522 (anode
    # MUTE_G), i.e. by MUTE_REQ: latent, and the next mute takes both down together
    ("f_r524_aperto_ins", "R524", "aperto, poi il mute dal tasto", ("aperto", [("RR524", 1)]),
     "PERMIT_G tenuto da MUTE_G attraverso D522: cade col mute?"),
    # ---- the sinks and their clamps
    ("f_q501_gd_perd", "Q501", "corto G-D, poi la perdita di rete", ("corto", "mute_g", "mute_cmd"),
     "il comparatore deve tenere giu' anche la corrente delle bobine"),
    ("f_q501_gd_spegn", "Q501", "corto G-D, poi lo spegnimento", ("corto", "mute_g", "mute_cmd"), ""),
    ("f_d506_corto_mus", "D506", "corto", ("corto", "mute_cmd", "clamp_mute"),
     "lo zener D507 in diretta da VRELAY a MUTE_CMD: un corto di VRELAY attraverso Q501"),
    ("f_q502_aperto_mus", "Q502", "aperto (D-S)", ("aperto", [("MQ502", 1)]),
     "K6 cade col jack chiuso: il guadagno torna a riposo durante la musica"),
    ("f_q502_gd_mus", "Q502", "corto G-D", ("corto", "permit_g", "permit_cmd"),
     "PERMIT_G a una soglia: D522 limita MUTE_G"),
    ("f_q503_aperto_mus", "Q503", "aperto (D-S)", ("aperto", [("MQ503", 1)]),
     "K501 cade: il toroidale si stacca, T2 resta"),
    ("f_d505_corto_mus", "D505", "corto", ("corto", "mains_coil", "vrelay_reg"),
     "VRELAY_REG a massa attraverso Q503"),
    ("f_r513_corto_perd", "R513", "corto, poi la perdita di rete", ("corto", "mute_req", "mute_g"),
     "il comparatore contro l'uscita del micro"),
    ("f_r513_corto_gu501", "R513", "corto, poi U501 spento", ("corto", "mute_req", "mute_g"), ""),
    ("f_d522_corto_perd", "D522", "corto, poi la perdita di rete", ("corto", "mute_g", "permit_g"),
     "MUTE_G e PERMIT_G legati"),
    ("f_d522_corto_ins", "D522", "corto, poi il mute dal tasto", ("corto", "mute_g", "permit_g"), ""),
]

# (no welded contact in this half: K501's contact is calcolo below)
SALDATI = []

# modes settled without a run: (ref, mode, the effect, the source)
CALCOLO = [
    # T2, F501
    ("T2", "spire in corto / secondario in corto", "F501 apre: = T2 aperto (f_t2_aperto_mus); "
     "prima che apra, T2 si scalda (il fusibile e' dimensionato dal datasheet di T2, G2)", "= f_t2_aperto_mus"),
    ("F501", "in corto (o sovradimensionato)", "latente: niente finche' T2 non si guasta; poi un "
     "guasto di T2 non e' interrotto (sicurezza, secondo guasto)", "calcolo"),
    ("J514", "un filo aperto", "= T2 aperto", "= f_t2_aperto_mus"),
    ("C521", "aperto", "stabilita' di U503 non garantita (SBVS204G Tab. 4-1, NR >= 10 nF); il "
     "banco comportamentale non lo mostra", "datasheet"),
    ("C522", "aperto", "nessuno: C520 sull'ingresso di U503", "calcolo"),
    ("U503", "pin 11 (0,2 V) aperto", "11,8 V: nessun effetto (G6K a 9,6 V di eccitazione)", "calcolo"),
    ("U503", "pin 10 (0,4 V) / 12 (0,1 V) a massa", "12,4 / 12,1 V: nessun effetto", "calcolo"),
    ("U503", "EN aperto", "stato non definito dal datasheet: il caso peggiore noto e' U503 spento",
     "= guasto_u503"),
    ("C524", "aperto", "U504 (MCP1703A) senza il suo 1 uF in ingresso: resta C523 a monte; "
     "nessun effetto in continua", "calcolo"),
    ("C525", "aperto", "stabilita' di U504 non garantita (MCP1703A, >= 1 uF in uscita); il banco "
     "non lo mostra", "datasheet"),
    ("U504", "IN-OUT in corto", "V5 = VRELAY_REG = 12 V: l'ATtiny3216 oltre il suo massimo "
     "assoluto (6 V, DS40002205A) - si guasta, e il suo stato dopo e' un guasto del micro (L54); "
     "comparatori (40 V) e LM4040 (4,75 mA < 15 mA) reggono", "calcolo"),
    ("J2", "il filo RLY_RET aperto", "la scheda audio perde il ritorno di SW3, del selettore, dei LED "
     "e del resto (RRESTO): SW3 letto come mute (pull-up a V5) -> il firmware muta; il selettore "
     "apre: la musica si ferma senza colpo (il selettore cambia senza mute, ADR-064: <= 19,8 uV). "
     "Le bobine del jack e di K6 tornano da MUTE_CMD / PERMIT_CMD: non toccate", "calcolo"),
    ("NT501", "corto", "e' un pezzo di rame: nessun modo", "calcolo"),
    # simulated first (f_nt501_aperto_mus, seq/ kept): it stops at the fault's instant with RLY_RET
    # on 1 nS, and with 1 nF across the opening (ASSUMED, T2's interwinding) at TE + 30 ms with both
    # methods; the first pass reads every logic level against GND, which the fault no longer ties
    # to RLY_RET. By hand: the only DC paths from the command's domain to GND are the supervisors'
    # dividers, VPLUS - 54,2k - RLY_RET and VREF - 128k - VMINUS: RLY_RET settles ~+5,3 V above GND
    # (VREF = RLY_RET + 2,5 V), SUP_P sees VPLUS - 5,3 = 9,7 V < 13,55 V and trips
    ("NT501", "aperto (la stella)", "il dominio del comando galleggia a ~+5,3 V sulla massa audio "
     "(i due partitori dei sorveglianti): il canale A vede il + a ~9,7 V e scatta, il mute falso; "
     "le correnti delle bobine non escono dal loro dominio. Simulazione rifiutata (sopra)", "calcolo"),
    # the standby switch
    ("Q505", "corto G-S", "= Q505 aperto", "= f_q505_aperto_mus"),
    ("Q506", "corto D-S", "= Q505 in corto (VRELAY sempre alla scheda audio)", "= f_q505_corto_spegn"),
    ("R539", "aperto", "= Q506 aperto", "= f_q506_aperto_mus"),
    ("R539", "corto", "Vgs di Q505 = -VRELAY_REG = -12 V (+-1 %): sul massimo assoluto dell'AO3401A "
     "(+-12 V); un secondo guasto possibile (il gate in corto). Fronti senza C531 rallentato", "calcolo"),
    ("R540", "aperto", "il gate di Q505 resta basso quando Q506 si spegne: VRELAY non si stacca "
     "in standby", "= f_q505_corto_spegn"),
    ("R540", "corto", "gate = source: Q505 non si accende mai: all'accensione niente musica; durante "
     "la musica = Q505 aperto", "= f_q505_aperto_mus"),
    ("C531", "aperto", "fronti di Q505 veloci: picco di corrente nei condensatori della scheda "
     "audio all'accensione; allo spegnimento D2 perde i ~10 ms del fronte (resta >= 17,3 ms)", "calcolo"),
    ("C531", "corto", "gate = source: = Q505 aperto", "= f_q505_aperto_mus"),
    ("J1", "pin 4 (VRELAY) aperto", "la scheda audio perde VRELAY", "= f_q505_aperto_mus"),
    # the supervisors
    ("R507", "corto", "SUP_P a massa: il mute falso", "= f_r506_aperto_mus"),
    ("C515", "corto", "SUP_P a massa: il mute falso", "= f_r506_aperto_mus"),
    ("R506", "corto", "SUP_P = VPLUS: il canale A cieco", "= f_u505a_cieco_gu501"),
    ("R507", "aperto", "SUP_P = VPLUS: il canale A cieco", "= f_u505a_cieco_gu501"),
    ("C515", "aperto", "nessuno: e' un filtro di 10 us", "calcolo"),
    ("R508", "corto", "SUP_M = VREF = 2,5 V > VREF/2: il mute falso", "= f_r506_aperto_mus"),
    ("R509", "aperto", "SUP_M = VREF: il mute falso", "= f_r506_aperto_mus"),
    ("R508", "aperto", "SUP_M = VMINUS (-15 V, sotto la massa del comparatore, ~0,13 mA nel suo "
     "diodo d'ingresso): il canale B cieco", "= f_u505b_cieco_gu502"),
    ("R509", "corto", "SUP_M = VMINUS: il canale B cieco", "= f_u505b_cieco_gu502"),
    ("C516", "corto", "SUP_M a 0 < VREF/2: il canale B cieco", "= f_u505b_cieco_gu502"),
    ("C516", "aperto", "nessuno", "calcolo"),
    ("U505", "un'uscita bloccata bassa", "il mute falso", "= f_r506_aperto_mus"),
    ("U505", "alimentazione (pin 8) aperta", "le due uscite aperte: i due rail ciechi",
     "= f_u505a_cieco_gu501, f_u505b_cieco_gu502"),
    ("R503", "aperto", "il riferimento senza corrente: VREF a 0", "= f_u507_corto_mus"),
    ("R503", "corto", "5 V sul LM4040: ~0,25 A, U504 al limite; il riferimento si distrugge "
     "(secondo guasto, di solito in corto)", "= f_u507_corto_mus"),
    ("C514", "corto", "VREF a 0", "= f_u507_corto_mus"),
    ("C514", "aperto", "nessuno in continua (rumore sul riferimento)", "calcolo"),
    ("R504", "aperto", "VREF_HALF a 0: SUP_M (1,13 V) sopra: il mute falso", "= f_r506_aperto_mus"),
    ("R505", "corto", "VREF_HALF a 0: il mute falso", "= f_r506_aperto_mus"),
    ("R504", "corto", "VREF_HALF = VREF: SUP_M (1,13 V) sotto: il canale B cieco", "= f_u505b_cieco_gu502"),
    ("R505", "aperto", "VREF_HALF = VREF: il canale B cieco", "= f_u505b_cieco_gu502"),
    # the mains detector
    ("Q504", "aperto", "MD non si scarica: il mute falso entro ~15 ms", "= f_r506_aperto_mus"),
    ("R510", "aperto", "Q504 mai acceso: il mute falso", "= f_r506_aperto_mus"),
    ("R511", "corto", "Q504 mai acceso: il mute falso", "= f_r506_aperto_mus"),
    ("R510", "corto", "RECT_V (~17 V) sulla base di Q504 senza limite: Q504 si distrugge (secondo "
     "guasto, aperto o in corto)", "= f_r506_aperto_mus o f_q504_corto_perd"),
    ("R511", "aperto", "Q504 acceso da ~0,7 V invece di ~4 V: il rivelatore funziona, piu' "
     "lento di qualche decimo di ms", "calcolo"),
    ("R512", "aperto", "MD non si carica: il rivelatore cieco", "= f_q504_corto_perd"),
    ("R512", "corto", "V5 su MD: Q504 acceso tira V5 a massa (U504 al limite, 250 mA) = V5 persa a "
     "ogni semionda; Q504 si distrugge", "= f_u504_spento_mus"),
    ("C518", "corto", "MD a 0: il rivelatore cieco", "= f_q504_corto_perd"),
    ("U506", "canale A bloccato basso / B bloccato basso", "il mute falso", "= f_r506_aperto_mus"),
    ("U506", "canale A cieco", "il rivelatore cieco", "= f_q504_corto_perd"),
    ("U506", "alimentazione aperta", "il rivelatore e il sorvegliante di VRELAY ciechi",
     "= f_q504_corto_perd, f_u506b_cieco_gu503"),
    ("R522", "aperto", "SUP_VR a 0: il mute falso", "= f_r506_aperto_mus"),
    ("R523", "corto", "il mute falso", "= f_r506_aperto_mus"),
    ("C526", "corto", "il mute falso", "= f_r506_aperto_mus"),
    ("R522", "corto", "SUP_VR = VRELAY_REG: il canale B cieco", "= f_u506b_cieco_gu503"),
    ("R523", "aperto", "il canale B cieco", "= f_u506b_cieco_gu503"),
    ("C526", "aperto", "nessuno", "calcolo"),
    ("C517", "corto", "V5 a massa", "= f_u504_spento_mus"),
    ("C519", "corto", "V5 a massa", "= f_u504_spento_mus"),
    ("C530", "corto", "V5 a massa", "= f_u504_spento_mus"),
    ("C525", "corto", "V5 a massa", "= f_u504_spento_mus"),
    ("C517", "aperto", "nessuno in continua", "calcolo"),
    ("C519", "aperto", "nessuno in continua", "calcolo"),
    ("C530", "aperto", "nessuno in continua", "calcolo"),
    # the delay
    ("C528", "aperto (durante la musica)", "latente: Delta perso; lo mostra un mute in hardware", "= cf_nodelta"),
    ("R534", "corto", "PERMIT_T a 0", "= f_c528_corto_mus"),
    ("C529", "corto", "VR_T a 0: VR_G basso, Q505 si spegne (C531)", "= f_q506_aperto_mus"),
    ("R536", "corto", "VR_T a 0", "= f_q506_aperto_mus"),
    ("R536", "aperto", "VR_T non si scarica: VRELAY resta in standby", "= f_q505_corto_spegn"),
    ("D520", "aperto", "PERMIT_T caricato solo da PERMIT_REQ: Delta si misura dall'ultima delle due "
     "richieste come oggi se il firmware le alza insieme; latente, conta solo con un firmware che "
     "abbassa PERMIT_REQ per primo (secondo guasto)", "calcolo"),
    ("D521", "aperto", "simmetrico: Delta solo da MUTE_REQ; nessun effetto col firmware di oggi", "calcolo"),
    ("D521", "corto", "PERMIT_T scaricato in PERMIT_REQ quando il firmware lo abbassa, dopo il suo "
     "Delta: perso solo il Delta di riserva in hardware; col micro in reset PERMIT_T si scarica in "
     "R526 (tau ~10 ms): Delta ~6 ms invece di ~20 (secondo evento)", "calcolo"),
    ("R532", "aperto", "= D520 aperto", "calcolo"),
    ("R533", "aperto", "= D521 aperto", "calcolo"),
    ("R532", "corto", "il pin di MUTE_REQ carica C528 senza limite (picco di decine di mA per "
     "qualche us): la funzione resta", "calcolo"),
    ("R533", "corto", "come R532", "calcolo"),
    ("D523", "aperto", "VR_T caricato solo da VRELAY_EN: D2 dal firmware; col micro in reset VR_T "
     "decade da solo (tau 100 ms), sempre dopo il permesso", "calcolo"),
    ("D523", "corto", "VR_T = PERMIT_T: le due costanti di tempo si sommano (Delta ~30 ms), VRELAY "
     "cade insieme al permesso: D2 = 0, dopo il jack", "calcolo"),
    ("D524", "aperto", "VRELAY accesa solo da PERMIT_T: all'accensione VRELAY arriva con MUTE_REQ, "
     "non 13 ms prima (ADR-027): i bistabili del trim forse non si impostano (funzione)", "calcolo"),
    ("R535", "aperto", "= D524 aperto", "calcolo"),
    ("R535", "corto", "come R532", "calcolo"),
    ("R524", "corto", "PERMIT_G = V5 sempre: U508 A in corto sull'uscita (corrente di corto); il "
     "permesso non si rilascia mai: guadagno e trim non si cambiano in mute (funzione)", "calcolo"),
    ("R516", "aperto", "nessuno (il pull-down per U508 morto)", "calcolo"),
    ("R516", "corto", "PERMIT_G a 0", "= f_r524_aperto_mus"),
    ("R537", "aperto", "VR_G a 0: Q505 si spegne", "= f_q506_aperto_mus"),
    ("R538", "corto", "VR_G a 0", "= f_q506_aperto_mus"),
    ("R537", "corto", "VR_G = V5 sempre: VRELAY in standby", "= f_q505_corto_spegn"),
    ("R538", "aperto", "nessuno", "calcolo"),
    ("U508", "canale A bloccato basso", "PERMIT_G a 0", "= f_r524_aperto_mus"),
    ("U508", "canale A cieco", "il permesso non si rilascia mai (funzione)", "= R524 corto"),
    ("U508", "canale B bloccato basso", "VR_G a 0", "= f_q506_aperto_mus"),
    ("U508", "canale B cieco / alimentazione aperta", "VRELAY in standby", "= f_q505_corto_spegn"),
    # the sinks
    ("Q501", "aperto (D-S) / gate aperto / G-S in corto", "i relè del jack non si eccitano: "
     "all'accensione niente musica; durante la musica il jack si apre come un mute normale (il "
     "permesso resta): il clic del taglio, misurato e dichiarato (ADR-062)", "= f_base_niente_ins"),
    ("D506", "aperto", "il clamp tolto: alla prossima diseccitazione la bobina scarica in valanga su "
     "Q501 (2N7002, 60 V, energia di valanga non dichiarata); se Q501 si guasta in corto il mute non "
     "si inserisce piu' (L45c1). Rilascio piu' veloce, non piu' lento", "calcolo"),
    ("D507", "aperto", "= D506 aperto", "calcolo"),
    ("D507", "corto", "il clamp e' il solo diodo: rilascio allungato oltre i 3 ms del G6K (quanto, il "
     "datasheet non lo dice; il banco ha bobine resistive). Il jack resta il primo: Delta >= 17,2 ms", "calcolo"),
    ("D508", "aperto", "come D506, su Q502", "calcolo"),
    ("D509", "aperto", "come D507 aperto, su Q502", "calcolo"),
    ("D509", "corto", "il rilascio di K6 si allunga: va nella stessa direzione di Delta", "calcolo"),
    ("D508", "corto", "come D506 corto, su PERMIT_CMD", "= f_d506_corto_mus"),
    ("Q502", "corto D-S", "K6 sempre eccitato: guadagno e trim non si cambiano mai in mute "
     "(funzione); all'accensione e' di L54", "calcolo"),
    ("Q502", "gate aperto / G-S in corto", "= Q502 aperto", "= f_q502_aperto_mus"),
    ("Q503", "corto D-S", "K501 sempre chiuso: in standby il toroidale resta acceso (P9 (a): ~W "
     "di magnetizzazione contro 0,5 W) e i rail della scheda audio restano su a jack aperti", "calcolo"),
    ("Q503", "gate aperto / G-S in corto", "= Q503 aperto", "= f_q503_aperto_mus"),
    ("D505", "aperto", "il flyback di K501 tolto: alla prossima diseccitazione (ogni spegnimento) "
     "valanga su Q503; se si guasta in corto = Q503 in corto, se aperto = K501 non si chiude piu'", "calcolo"),
    ("R513", "aperto", "MUTE_G tirato giu' da R514: il mute (funzione); durante la musica un mute "
     "normale", "= f_base_niente_ins"),
    ("R514", "aperto", "nessuno: il pull-down per un micro morto (R525 e R513 lo fanno lo stesso)", "calcolo"),
    ("R514", "corto", "MUTE_G a 0: il mute (funzione)", "= f_base_niente_ins"),
    ("C527", "aperto", "MUTE_G senza il suo ritardo di 0,22 ms: D522 tiene comunque MUTE_G sotto "
     "PERMIT_G al rilascio", "calcolo"),
    ("C527", "corto", "MUTE_G a 0: il mute (funzione)", "= f_base_niente_ins"),
    ("D522", "aperto", "latente: MUTE_G non piu' legato sotto PERMIT_G; conta solo con un firmware "
     "che alza MUTE_REQ prima di PERMIT_REQ (secondo guasto; il ruolo di D522 e' di L54)", "calcolo"),
    ("R520", "aperto", "MAINS_G a 0 (R521): K501 cade", "= f_q503_aperto_mus"),
    ("R521", "corto", "MAINS_G a 0", "= f_q503_aperto_mus"),
    ("R520", "corto", "nessuno: il pin pilota il gate", "calcolo"),
    ("R521", "aperto", "nessuno: il pull-down per un micro morto", "calcolo"),
    # K501
    ("K501", "bobina aperta", "= Q503 aperto", "= f_q503_aperto_mus"),
    ("K501", "bobina in corto", "VRELAY_REG a massa attraverso Q503", "= f_d505_corto_mus"),
    ("K501", "un polo saldato", "nessuno: l'altro polo stacca il toroidale (DPST); latente", "calcolo"),
    ("K501", "i due poli saldati", "= Q503 in corto (standby col toroidale acceso)", "= Q503 corto"),
    ("K501", "un polo aperto", "il toroidale si stacca", "= f_q503_aperto_mus"),
    # the micro's pull-downs and reads
    ("R525", "aperto", "nessuno: con il micro in reset MUTE_G scende lo stesso per R514", "calcolo"),
    ("R525", "corto", "MUTE_REQ a massa: il mute (funzione); il pin del micro in corto (L54)", "= f_base_niente_ins"),
    ("R526", "aperto", "nessuno", "calcolo"),
    ("R526", "corto", "PERMIT_REQ a massa: PERMIT_T caricato da MUTE_REQ (D520): nessun effetto "
     "visibile; il pin del micro in corto (L54)", "calcolo"),
    ("R527", "aperto", "nessuno", "calcolo"),
    ("R527", "corto", "VRELAY_EN a massa: = D524 aperto; il pin in corto (L54)", "calcolo"),
    ("R528", "aperto", "nessuno", "calcolo"),
    ("R528", "corto", "MAINS_REQ a massa: = Q503 aperto; il pin in corto (L54)", "= f_q503_aperto_mus"),
    ("R541", "aperto", "FRONT_IN flottante (resta C532): il micro non vede l'interruttore; letture "
     "a caso possibili (accensioni o spegnimenti spontanei, ciascuno con la sua sequenza)", "calcolo"),
    ("R541", "corto", "nessuno (perso il primo polo del filtro)", "calcolo"),
    ("C532", "corto", "FRONT_IN a massa = acceso sempre: dal frontale non si spegne (resta il "
     "retro, ADR-048)", "calcolo"),
    ("C532", "aperto", "nessuno (il debounce e' anche nel firmware)", "calcolo"),
    ("R542", "aperto", "SW3_IN flottante: mute o musica a caso", "calcolo"),
    ("R542", "corto", "nessuno", "calcolo"),
    ("C533", "corto", "SW3_IN a massa = musica sempre: il mute dal tasto non si inserisce piu' "
     "(funzione); il mute in hardware resta", "calcolo"),
    ("C533", "aperto", "nessuno", "calcolo"),
    ("R517", "corto", "MUTE_SW = V5: SW3 su musica mette V5 a massa", "= f_u504_spento_mus"),
    ("R518", "corto", "FRONT_SW = V5: l'interruttore acceso mette V5 a massa", "= f_u504_spento_mus"),
    ("R517", "aperto", "SW3 aperto lascia MUTE_SW flottante: = R542 aperto", "calcolo"),
    ("R518", "aperto", "= R541 aperto", "calcolo"),
    ("R543", "aperto", "il firmware non legge piu' MUTE_G: perde il verdetto dell'hardware "
     "(diagnostica; il mute in hardware resta)", "calcolo"),
    ("R543", "corto", "latente: un firmware che pilota PC2 alto solleverebbe MUTE_G (secondo guasto, L54)", "calcolo"),
    ("R544-R547", "aperto", "il firmware non sa quale sorvegliante e' scattato (ADR-048 p. 5): "
     "diagnostica; il mute in hardware resta", "calcolo"),
    ("R544-R547", "corto", "latente: un pin del micro non alimentato o in latch-up carica il nodo "
     "del sorvegliante (secondo guasto, L54)", "calcolo"),
]

# modes the bench would only repeat: (ref, mode, the case it equals, why)
UGUALI = [
    ("U503", "spento (uscita aperta, EN)", "guasto_u503", "il caso di L41c / L56"),
    ("U503", "uscita a massa (interno)", "corto_u503", "il caso di L41c, accettato da ADR-051"),
    ("C523", "corto", "corto_u503", "lo stesso nodo"),
    ("C524", "corto", "corto_u503", "lo stesso nodo"),
    ("C522", "corto", "f_c520_corto_mus", "in parallelo a C520"),
    ("C521", "corto", "guasto_u503", "NR a massa: il riferimento di U503 a 0 (IPOTESI, come C507 in L45c1)"),
    ("U503", "IN a massa (interno)", "f_c520_corto_mus", "lo stesso nodo"),
    ("U503", "pin 5 (6,4 V) a massa", "f_u503_cortoio_mus", "18,4 V chiesti: il grezzo meno la caduta"),
    ("U503", "SENSE (pin 3) aperto", "f_u503_cortoio_mus", "IPOTESI: l'uscita al grezzo, come L45c1"),
    ("D512", "corto", "f_u503_cortoio_mus", "OUT-IN di U503 in corto"),
    ("D503", "gli altri tre diodi in corto", "f_d503a_corto_mus", "simmetrici"),
    ("D503", "gli altri tre diodi aperti", "f_d503a_aperto_mus", "simmetrici"),
    ("F501", "aperto", "f_t2_aperto_mus", "T2 senza rete"),
    ("U504", "uscita a massa / EN", "f_u504_spento_mus", "V5 persa"),
    ("C528", "aperto, poi la perdita di rete", "cf_nodelta", "il controfattuale di L30 / L41c: C528 = 10 pF"),
    ("C520", "corto (la tenuta di VRELAY)", "f_c520_corto_mus", "lo stesso caso"),
    ("D504", "corto (durante la musica)", "f_d504_corto_perd", "latente: lo mostra la perdita di rete"),
    ("Q504", "corto C-E (durante la musica)", "f_q504_corto_perd", "latente"),
]
