#!/usr/bin/env python3
"""L33 - corregge le frasi di provenienza dell'LSK489 nei deck. Solo commenti.

    /usr/bin/python3 correggi.py <radice-del-repo>

Ogni sostituzione e' testo esatto, vecchio -> nuovo, e deve comparire
ESATTAMENTE una volta nel deck a cui e' assegnata: altrimenti lo script rifiuta
e non scrive nessun file. Che il risultato tocchi solo righe di commento lo
prova solo_commenti.py, non questo script.
"""

import os
import sys

L22_OLD = """\
* L22: the input current mirror is no longer a placeholder. It is an
* LS352 (ADR-018) and this is its VENDOR model - the only real device
* model in this deck besides the LSK489. Every OTHER device here is
* still a hand-written placeholder.
"""
L22_NEW = """\
* L22: the input current mirror is no longer a placeholder. It is an
* LS352 (ADR-018) and this is its VENDOR model - the only one in this
* deck. L33 (NC-031): the LSK489 is not a vendor model here. Its halves
* are LSK489X, a hand-written placeholder with KF=0; the vendor model
* models/jfet/lsk489.lib is included by no deck (Fase 4, NC-017). Every
* OTHER device here is a hand-written placeholder too, and none has 1/f.
"""
L22_DECKS = ["tb_ac", "tb_bias_sweep", "tb_dc_headroom", "tb_loop",
             "tb_loop_blockA", "tb_noise_breakdown", "tb_noise_vectors", "tb_op",
             "tb_switch_v2", "tb_switch_v2_counterfactual", "tb_v3_overload",
             "tb_zout_psrr_noise"]

EDITS = {d: [(L22_OLD, L22_NEW)] for d in L22_DECKS}

EDITS["tb_trim"] = [(
    "* NOISE IS A FLOOR (placeholder models, KF = 0 but on the LSK489, NC-004).\n",
    "* NOISE IS A FLOOR (KF = 0 on every model, the LSK489's LSK489X placeholder\n"
    "* too: NC-004, NC-031).\n",
)]

EDITS["tb_blockA_carichi"] = [(
    "* PROVVISORIO SUI MODELLI: tutto tranne LS352 e LSK489 e' segnaposto\n"
    "* (placeholder_devices.lib, NC-017). Nessuna cifra di distorsione va ricavata\n"
    "* da qui.\n",
    "* PROVVISORIO SUI MODELLI: tutto tranne LS352 e' segnaposto, LSK489 compreso\n"
    "* (LSK489X in placeholder_devices.lib, KF=0; NC-017, NC-031). Nessuna cifra di\n"
    "* distorsione va ricavata da qui.\n",
)]

EDITS["tb_mute_corto"] = [(
    "* PROVVISORIO SUI MODELLI: tutto tranne LS352 e LSK489 e' segnaposto\n"
    "* (placeholder_devices.lib, NC-017). Le correnti di corto le fissano il\n"
    "* carico e la corrente di pilotaggio, quindi h_FE conta (NC-024).\n",
    "* PROVVISORIO SUI MODELLI: tutto tranne LS352 e' segnaposto, LSK489 compreso\n"
    "* (LSK489X in placeholder_devices.lib, KF=0; NC-017, NC-031). Le correnti di\n"
    "* corto le fissano il carico e la corrente di pilotaggio, quindi h_FE conta\n"
    "* (NC-024).\n",
)]


def main():
    tb = os.path.join(os.path.abspath(sys.argv[1]), "spice", "preamp", "tb")
    out, errors = {}, []
    for deck, edits in sorted(EDITS.items()):
        path = os.path.join(tb, deck + ".cir")
        with open(path) as fh:
            text = fh.read()
        for old, new in edits:
            n = text.count(old)
            if n != 1:
                errors.append(f"{deck}.cir: testo vecchio trovato {n} volte, non 1")
                continue
            text = text.replace(old, new)
        out[path] = text
    if errors:
        print("RIFIUTATO, nessun file scritto:", *errors, sep="\n  ")
        return 1
    for path, text in out.items():
        with open(path, "w") as fh:
            fh.write(text)
        print(f"   corretto {os.path.basename(path)}")
    print(f"{len(out)} deck corretti")
    return 0


if __name__ == "__main__":
    sys.exit(main())
