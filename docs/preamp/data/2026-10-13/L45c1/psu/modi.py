#!/usr/bin/env python3
"""L45c1: the single faults of the supply's AUDIO RAILS, one row per mode.

The user's choice at the start of L45c (2026-10-13, «Due parti»): L45c1 the rails (T1's
secondary, the bridge D501, the reservoirs, U501 / U502 and their parts, the hold-up, the
Schottkys D510 / D511, the rails' decoupling on the audio board C139-C142, the harness J1 for
the rails) and the mute that does not engage (Q501 shorted D-S, a welded NO of K2-K4) at the
soft power-down, the mains loss and a regulator's failure. L45c2: the relay line, the
supervisors, the timer, the sinks, K501.

Every row is a mode. A SIMULATED mode has a case name f_<ref>_<modo>_<evento> (no other
underscore), run by psu/corri_seq.sh on the supply bench to its fixed point with the firmware,
then on the audio board through the bridge (ponte/). A mode the bench would only repeat has
`uguale` = the case it equals, and the reason; a mode settled without a run has `calcolo`.

The primitives (genera_tb_psu.py, applica_guasto):
  ("corto", a, b)              10 S (0.1 ohm) between nodes a and b from the fault's instant
  ("aperto", [(line, k), ...]) token k of the deck line whose first token is `line` moved to a
                               new node, joined to the old one by 1 kS before the fault, 1 nS after
  ("vset", reg, v)             a twin of the behavioural regulator `reg` with VSET = v takes over
                               at the fault's instant (the original's enable to 0, the twin's to
                               1): the set point the faulty pin or divider gives. v = 100 means
                               "to the raw": the model takes min(VSET, Vin - VDO)
  ("j1", rail, c)              the harness wire of `rail` opens: every supply line on that node is
                               moved to <rail>_psu (the supervisor, the regulator, the hold-up);
                               the audio board keeps the node, its load and c of its own decoupling
Events: mus (the fault at TE during music, nothing else), perd (the mains lost at TE), spegn
(the front switched off at TE), gu502 / gu501 (U502 / U501 off at TE). With an event other than
mus the fault is LATENT: present from t = 0, and the event is what shows it.
"""

# the audio board's own decoupling on each rail (preamp_audio.net, L45c1): VPLUS 8 x 100 uF +
# 8 x 100 nF, VMINUS 16 x 100 uF + 16 x 100 nF; the electrolytics derated -20 % as the bench
# derates every C_Polarized (ADR-046)
C_AUDIO = {"vplus": 8 * 100e-6 * 0.8 + 8 * 100e-9, "vminus": 16 * 100e-6 * 0.8 + 16 * 100e-9}

EVENTI = {"mus": dict(front=1, sw3=1, tf=1.0),
          # the centre tap open: the raw midpoint drifts with the rails' load imbalance (1.28 V/s
          # in f_j513ct_aperto_mus), and U502 reaches its dropout only seconds later
          "mus6": dict(front=1, sw3=1, tf=6.0),
          "perd": dict(front=1, sw3=1, buco=1000.0, tf=1.0),
          "spegn": dict(front="giu", sw3=1, tf=1.1),
          "gu502": dict(front=1, sw3=1, u502=True, tf=1.0),
          "gu501": dict(front=1, sw3=1, spento="U501", tf=1.0)}

# (case, ref, mode, primitive, what it is)
SIMULATI = [
    # ---- T1's secondary (J513) and the bridge D501
    ("f_j513a_aperto_mus", "J513", "pin 1 aperto (meta' A del secondario)",
     ("aperto", [("LT1_SEC_Aa", 2)]), "una meta' del secondario staccata: i due rail a mezz'onda"),
    ("f_j513b_aperto_mus", "J513", "pin 3 aperto (meta' B del secondario)",
     ("aperto", [("LT1_SEC_Ab", 2)]), "l'altra meta'"),
    ("f_j513ct_aperto_mus", "J513", "pin 2 aperto (presa centrale)",
     ("aperto", [("BT1_SEC_Aa", 2), ("BT1_SEC_Ab", 1)]),
     "la presa centrale staccata: GND non tocca piu' il trasformatore"),
    ("f_j513ct_aperto_mus6", "J513", "pin 2 aperto (presa centrale), 6 s",
     ("aperto", [("BT1_SEC_Aa", 2), ("BT1_SEC_Ab", 1)]),
     "lo stesso, fino a TE + 6 s: la deriva del punto di mezzo fino al sorvegliante"),
    ("f_d501a_corto_mus", "D501", "diodo A->+ in corto", ("corto", "t1_sec_a", "raw_p"), ""),
    ("f_d501b_corto_mus", "D501", "diodo B->+ in corto", ("corto", "t1_sec_b", "raw_p"), ""),
    ("f_d501c_corto_mus", "D501", "diodo -->A in corto", ("corto", "raw_m", "t1_sec_a"), ""),
    ("f_d501d_corto_mus", "D501", "diodo -->B in corto", ("corto", "raw_m", "t1_sec_b"), ""),
    ("f_d501a_aperto_mus", "D501", "diodo A->+ aperto", ("aperto", [("DD501a", 1)]), ""),
    ("f_d501b_aperto_mus", "D501", "diodo B->+ aperto", ("aperto", [("DD501b", 1)]), ""),
    ("f_d501c_aperto_mus", "D501", "diodo -->A aperto", ("aperto", [("DD501c", 1)]), ""),
    ("f_d501d_aperto_mus", "D501", "diodo -->B aperto", ("aperto", [("DD501d", 1)]), ""),
    # ---- the raw reservoirs
    ("f_c501_corto_mus", "C501", "corto", ("corto", "raw_p", "0"), "il grezzo + a massa"),
    ("f_c502_corto_mus", "C502", "corto", ("corto", "0", "raw_m"), "il grezzo - a massa"),
    ("f_c501_aperto_mus", "C501", "aperto", ("aperto", [("CC501", 1)]), "restano i 10 uF di C509"),
    ("f_c502_aperto_mus", "C502", "aperto", ("aperto", [("CC502", 1)]), "restano i 10 uF di C510"),
    # ---- U501, the + rail (TPS7A4701 ANY-OUT: 1.4 V + the grounded weights, SBVS204G Table 6-1)
    ("f_u501_cortoio_mus", "U501", "IN-OUT in corto", ("corto", "raw_p", "vplus"),
     "il rail + al grezzo"),
    ("f_u501_vset86_mus", "U501", "pin 4 (6,4 V) aperto", ("vset", "U501", 8.6), "il rail a 8,6 V"),
    ("f_u501_vset142_mus", "U501", "pin 9 (0,8 V) aperto", ("vset", "U501", 14.2), "14,2 V"),
    ("f_u501_vset182_mus", "U501", "pin 6 (3,2 V) a massa", ("vset", "U501", 18.2),
     "18,2 V chiesti, il grezzo meno la caduta"),
    ("f_u501_vset166_mus", "U501", "pin 8 (1,6 V) a massa", ("vset", "U501", 16.6), "16,6 V"),
    ("f_u501_vset154_mus", "U501", "pin 10 (0,4 V) a massa", ("vset", "U501", 15.4), "15,4 V"),
    ("f_u501_vset152_mus", "U501", "pin 11 (0,2 V) a massa", ("vset", "U501", 15.2), "15,2 V"),
    ("f_u501_vset151_mus", "U501", "pin 12 (0,1 V) a massa", ("vset", "U501", 15.1), "15,1 V"),
    ("f_u501_sense_mus", "U501", "SENSE (pin 3) aperto", ("vset", "U501", 100.0),
     "IPOTESI: senza retroazione l'uscita va al grezzo"),
    # ---- U502, the - rail (TPS7A3301: VOUT = VREF (1 + R501 / R502), SBVS169D Eq. 2)
    ("f_u502_cortoio_mus", "U502", "IN-OUT in corto", ("corto", "raw_m", "vminus"),
     "il rail - al grezzo"),
    ("f_r501_aperto_mus", "R501", "aperto", ("vset", "U502", 100.0),
     "FB a massa da R502: il rail - al grezzo"),
    ("f_r502_aperto_mus", "R502", "aperto", ("vset", "U502", 1.176),
     "FB sull'uscita: il rail a VREF, -1,18 V"),
    # ---- the hold-up and the Schottkys: latent, shown by the mains loss
    ("f_c505_aperto_perd", "C505", "aperto, poi la perdita di rete", ("aperto", [("CC505", 1)]),
     "la tenuta del + persa: restano i 10 uF di C511"),
    ("f_c506_aperto_perd", "C506", "aperto, poi la perdita di rete", ("aperto", [("CC506", 1)]),
     "la tenuta del -"),
    ("f_d510_aperto_perd", "D510", "aperto, poi la perdita di rete", ("aperto", [("DD510", 1)]),
     "OUT sopra IN senza il diodo?"),
    ("f_d511_aperto_perd", "D511", "aperto, poi la perdita di rete", ("aperto", [("DD511", 1)]),
     "IN sopra OUT senza il diodo? (Abs Max -0,3 V)"),
    # ---- a rail to ground (C139-C142 on the audio board, C505 / C506, C511 / C512)
    ("f_vplus_massa_mus", "C139", "corto (rail + a massa)", ("corto", "vplus", "0"),
     "U501 nel limite di corrente"),
    ("f_vminus_massa_mus", "C140", "corto (rail - a massa)", ("corto", "0", "vminus"),
     "U502 nel limite di corrente"),
    # ---- the harness J1: a rail wire open (the supervisor reads the supply's side)
    ("f_j1vp_aperto_mus", "J1", "pin 1 (VPLUS) aperto", ("j1", "vplus", C_AUDIO["vplus"]),
     "la scheda audio perde il +, il sorvegliante no"),
    ("f_j1vm_aperto_mus", "J1", "pin 3 (VMINUS) aperto", ("j1", "vminus", C_AUDIO["vminus"]),
     "la scheda audio perde il -"),
    # ---- the mute that does not engage: Q501 shorted D-S (L45b), latent
    ("f_q501_corto_spegn", "Q501", "corto D-S, poi lo spegnimento", ("corto", "mute_cmd", "rly_ret"), ""),
    ("f_q501_corto_perd", "Q501", "corto D-S, poi la perdita di rete", ("corto", "mute_cmd", "rly_ret"), ""),
    ("f_q501_corto_gu502", "Q501", "corto D-S, poi U502 spento", ("corto", "mute_cmd", "rly_ret"), ""),
    ("f_q501_corto_gu501", "Q501", "corto D-S, poi U501 spento", ("corto", "mute_cmd", "rly_ret"), ""),
]

# the welded NO of K2-K4 (on the audio board): the supply does exactly what it does without
# it, so the bridge of the base case is used with the jack contact never opening (ponte/)
SALDATI = [("nosald_spegnimento_l", "spegnimento_l", "K2-K4", "NO saldato, poi lo spegnimento"),
           ("nosald_perdita", "perdita", "K2-K4", "NO saldato, poi la perdita di rete"),
           ("nosald_guasto", "guasto", "K2-K4", "NO saldato, poi U502 spento"),
           ("nosald_guasto_u501", "guasto_u501", "K2-K4", "NO saldato, poi U501 spento")]

# modes settled without a run: (ref, mode, the effect, the source). The behavioural regulators
# of the bench (REGP / REGM) have no loop dynamics and no noise: what is about stability or
# noise is read from the datasheets in vendor/ldo_regulator/ti/ (SBVS204G, SBVS169D)
CALCOLO = [
    ("C507", "corto", "NR a massa: il riferimento di U501 a 0 V, il rail + scende come con U501 "
     "spento (IPOTESI: l'uscita segue il riferimento filtrato su NR/SS, SBVS204G 6.3.3)", "= guasto_u501"),
    ("C507", "aperto", "stabilita' non garantita: SBVS204G Tabella 4-1, NR >= 10 nF \"to assure "
     "stability\"; il banco comportamentale non puo' mostrare un'oscillazione", "datasheet"),
    ("C508", "corto", "NR/SS a massa: il riferimento di U502 a 0 V, il rail - come con U502 spento "
     "(IPOTESI, come C507)", "= guasto"),
    ("C508", "aperto", "nessun effetto in continua: SBVS169D caratterizza con CNR/SS = 0 nF; piu' "
     "rumore e niente avvio morbido", "datasheet"),
    ("C509", "aperto", "nessuno: C501 (4700 uF) resta sull'ingresso di U501", "calcolo"),
    ("C510", "aperto", "nessuno: C502 resta sull'ingresso di U502", "calcolo"),
    ("C511", "aperto", "stabilita' non garantita: SBVS204G Tabella 4-1, OUT >= 10 uF ceramico; "
     "resta C505 (elettrolitico)", "datasheet"),
    ("C512", "aperto", "stabilita' non garantita: SBVS169D, OUT >= 10 uF ceramico; resta C506",
     "datasheet"),
    ("C513", "aperto", "nessun effetto in continua: e' il condensatore di anticipo (rumore, "
     "risposta ai transitori)", "calcolo"),
    ("C505", "aperto (durante la musica)", "al guasto niente (restano i 10 uF di C511): e' "
     "latente, lo mostra la perdita di rete (f_c505_aperto_perd) o un guasto di U501, che "
     "sarebbe un secondo guasto", "= f_c505_aperto_perd"),
    ("C506", "aperto (durante la musica)", "idem per il rail -", "= f_c506_aperto_perd"),
    ("C139-C142", "aperto", "un blocco perde il suo disaccoppiamento locale: niente in continua; "
     "L45a l'ha simulato (C139_ap ... C142_ap)", "L45a"),
    ("J1", "pin 2 (GND) aperto", "la massa della scheda audio non torna piu' alla presa "
     "centrale: i rail della scheda audio si riferiscono a una massa che galleggia; il banco a due "
     "passi non lo rappresenta (la scheda audio e' un carico verso 0 V). Da riprendere in L45d "
     "col cablaggio di G2", "non simulato"),
    ("U501, U502", "EN aperto", "EN e' legato a IN; aperto, lo stato del pin non e' definito dal "
     "datasheet: il caso peggiore noto e' il regolatore spento", "= guasto_u501 / guasto"),
]

# modes the bench would only repeat: (ref, mode, the case it equals, why)
UGUALI = [
    ("U501", "spento (uscita aperta, EN)", "guasto_u501", "il caso di L41c / L56"),
    ("U502", "spento (uscita aperta, EN)", "guasto", "il caso di L41c / L56"),
    ("U501", "uscita a massa (interno)", "f_vplus_massa_mus", "lo stesso nodo"),
    ("U502", "uscita a massa (interno)", "f_vminus_massa_mus", "lo stesso nodo"),
    ("U501", "IN a massa (interno)", "f_c501_corto_mus", "lo stesso nodo"),
    ("U502", "IN a massa (interno)", "f_c502_corto_mus", "lo stesso nodo"),
    ("U501", "pin 5 (6,4 V) aperto", "f_u501_vset86_mus", "lo stesso peso del pin 4"),
    ("C509", "corto", "f_c501_corto_mus", "in parallelo a C501"),
    ("C510", "corto", "f_c502_corto_mus", "in parallelo a C502"),
    ("C505", "corto", "f_vplus_massa_mus", "sul rail +"),
    ("C511", "corto", "f_vplus_massa_mus", "sul rail +"),
    ("C141", "corto", "f_vplus_massa_mus", "sul rail + (100 uF del blocco)"),
    ("C506", "corto", "f_vminus_massa_mus", "sul rail -"),
    ("C512", "corto", "f_vminus_massa_mus", "sul rail -"),
    ("C142", "corto", "f_vminus_massa_mus", "sul rail - (100 uF del blocco)"),
    ("D510", "corto", "f_u501_cortoio_mus", "OUT-IN di U501 in corto"),
    ("D511", "corto", "f_u502_cortoio_mus", "OUT-IN di U502 in corto"),
    ("R501", "corto", "f_r502_aperto_mus", "FB sull'uscita: -1,18 V"),
    ("C513", "corto", "f_r502_aperto_mus", "FB sull'uscita: -1,18 V"),
    ("R502", "corto", "f_r501_aperto_mus", "FB a massa: il rail - al grezzo"),
]
