#!/usr/bin/env python3
"""L44 (ADR-057) - i commenti dei deck e del sorgente che dicevano «solo l'LSK489A ha
KF» / «il rumore e' un pavimento senza flicker». Da L44 tutti i bipolari portano KF al
tetto dichiarato: quelle frasi sono false. Sostituzione esatta; ogni frase vecchia deve
comparire il numero di volte atteso, se no lo script si ferma prima di scrivere.
Uso: /usr/bin/python3 commenti_kf.py
"""
import os

QUI = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(QUI, *[".."] * 6))
TB = "spice/preamp/tb/"

A_OLD = ("* Only the LSK489A carries KF: 1/f noise is on the input pair and nowhere\n"
         "* else.")
A_NEW = ("* Since L44 every bipolar model carries KF as well (ADR-057: a declared\n"
         "* upper bound).")
B_OLD = "* Solo l'LSK489A ha KF (1/f); nessun modello porta la dispersione."
B_NEW = "* Da L44 tutti i modelli hanno KF (ADR-057, un tetto); nessuno porta la dispersione."

A_DECK = ["tb_v3_overload", "tb_op", "tb_e4_uscite", "tb_noise_breakdown",
          "tb_switch_v2_counterfactual", "tb_switch_v2", "tb_dc_headroom", "tb_loop_blockA",
          "tb_loop", "tb_ac", "tb_zout_psrr_noise", "tb_bias_sweep", "tb_noise_vectors"]
B_DECK = ["tb_mute_corto", "tb_blockA_carichi", "tb_v2_mute_pavimento", "tb_v2_mute_graduale",
          "tb_v2_mute_varianti"]

SOST = [(TB + d + ".cir", A_OLD, A_NEW) for d in A_DECK] + \
       [(TB + d + ".cir", B_OLD, B_NEW) for d in B_DECK] + [
    (TB + "tb_v2_mute_ldr.cir",
     "e solo\n* l'LSK489A ha KF (1/f).",
     "e da L44\n* tutti hanno KF (1/f; ADR-057)."),
    (TB + "tb_e3_e5_ldr.cir",
     "* terminati (#27). Il rumore e' un PAVIMENTO: da L39 i modelli sono del\n"
     "* costruttore, ma solo l'LSK489A porta KF; gli altri non hanno 1/f (NC-004).",
     "* terminati (#27). Il rumore: da L39 i modelli sono del costruttore, da L44\n"
     "* i bipolari portano KF al tetto dichiarato di ADR-057: un limite per eccesso."),
    (TB + "tb_noise_breakdown.cir",
     "* REMINDER: since L39 the models are the manufacturer's, and only the\n"
     "* LSK489A carries KF. 1/f noise is on the input pair and nowhere else: for\n"
     "* every other device these are thermal + shot noise only, i.e. a FLOOR.",
     "* REMINDER: since L39 the models are the manufacturer's; since L44 every\n"
     "* bipolar model carries KF at a declared UPPER BOUND (ADR-057), so these\n"
     "* totals are a bound with flicker, not a floor without it."),
    (TB + "tb_noise_breakdown.cir",
     "* ATTENZIONE DI MERITO: da L39 i modelli sono del costruttore, ma solo\n"
     "* l'LSK489A porta KF. Fuori dalla coppia d'ingresso qui NON c'e' rumore 1/f:\n"
     "* e' un pavimento termico+shot, non una previsione (NC-004).",
     "* ATTENZIONE DI MERITO: da L39 i modelli sono del costruttore; da L44 i\n"
     "* bipolari portano KF al tetto dichiarato di ADR-057: le cifre sono un\n"
     "* limite per eccesso col flicker, non un pavimento senza (NC-004)."),
    (TB + "tb_noise_vectors.cir",
     "* ATTENZIONE: da L39 i modelli sono del costruttore, ma solo l'LSK489A porta\n"
     "* KF. Fuori dalla coppia d'ingresso e' un pavimento senza rumore 1/f\n"
     "* (NC-004), non una previsione.",
     "* ATTENZIONE: da L39 i modelli sono del costruttore; da L44 i bipolari\n"
     "* portano KF al tetto dichiarato di ADR-057: un limite per eccesso col\n"
     "* flicker (NC-004)."),
    (TB + "tb_uscite_fisse.cir",
     "* *** IL RUMORE E' UN PAVIMENTO, NON UNA PREVISIONE *** (tb_zout_psrr_noise):\n"
     "* da L39 solo l'LSK489A porta KF; fuori dalla coppia d'ingresso nessun 1/f.",
     "* IL RUMORE (tb_zout_psrr_noise): da L44 tutti i bipolari portano KF al tetto\n"
     "* dichiarato di ADR-057, quindi e' un limite per eccesso, non un pavimento."),
    (TB + "tb_trim.cir",
     "* NOISE IS A FLOOR (since L39 only the LSK489A carries KF; no other model\n"
     "* has 1/f: NC-004).",
     "* NOISE IS AN UPPER BOUND (since L44 every bipolar model carries KF at the\n"
     "* declared bound of ADR-057; NC-004)."),
    (TB + "tb_zout_psrr_noise.cir",
     "* *** THE NOISE NUMBER IS A FLOOR, NOT A PREDICTION ***\n"
     "* Since L39 the models are the manufacturer's, and only the LSK489A carries\n"
     "* KF: the input pair has its 1/f, the mirror/VAS flicker noise is missing.\n"
     "* Treat the result as a floor for everything but the input pair.",
     "* THE NOISE NUMBER IS AN UPPER BOUND, NOT A FLOOR (since L44)\n"
     "* Since L39 the models are the manufacturer's; since L44 the mirror, VAS,\n"
     "* cascode and output devices carry KF at the declared bound of ADR-057,\n"
     "* the input pair its vendor KF."),
    (TB + "tb_idss_op_noise.cir",
     "* models/bjt_pnp/ls350.lib, without KF. Since L39 (NC-017) every other device\n"
     "* is a vendor model of models/ too (MMBT5551, MMBT5401, Qmje15032, Qmje15033,\n"
     "* D1N914), none with KF; until L39 they were the hand-written models of\n"
     "* placeholder_devices.lib. So every noise figure here is a FLOOR WITHOUT\n"
     "* FLICKER for every device but the input pair.",
     "* models/bjt_pnp/ls350.lib. Since L39 (NC-017) every other device is a vendor\n"
     "* model of models/ too (MMBT5551, MMBT5401, Qmje15032, Qmje15033, D1N914);\n"
     "* until L39 they were the hand-written models of placeholder_devices.lib.\n"
     "* Since L44 every bipolar model carries KF at the declared bound of ADR-057,\n"
     "* so the noise figures here are bounds with flicker, not floors without it."),
]


def main():
    testi = {}
    for rel, old, new in SOST:
        p = os.path.join(ROOT, rel)
        t = testi.get(p) or open(p).read()
        if t.count(old) != 1:
            raise SystemExit("%s: frase trovata %d volte, nessun file scritto:\n%s"
                             % (rel, t.count(old), old))
        testi[p] = t.replace(old, new)
    for p, t in testi.items():
        open(p, "w").write(t)
        print("scritto:", os.path.relpath(p, ROOT))


if __name__ == "__main__":
    main()
