#!/usr/bin/env python3
"""L33 - i sabotaggi del guardiano check_deck_provenance.py.

    /usr/bin/python3 genera_e_verifica.py <radice-del-repo>

Parte dai deck GIA' corretti di spice/preamp/tb/, scrive accanto a questo file
una copia sabotata per ogni caso (sostituzione esatta, che deve comparire una
volta sola), lancia il guardiano su ciascuna e confronta l'exit code con quello
atteso. Esce 1 se anche un solo caso non va come atteso.
"""

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

L22_FIXED = ("* LS352 (ADR-018) and this is its VENDOR model - the only one in this\n")

CASES = [
    # nome, deck di partenza, vecchio, nuovo, rc atteso, perche'
    ("c00_controllo_intatto", "tb_op", None, None, 0,
     "il deck corretto, senza modifiche"),
    ("c01_forma_besides", "tb_op",
     "* LS352 (ADR-018) and this is its VENDOR model - the only one in this\n"
     "* deck. L33 (NC-031): the LSK489 is not a vendor model here.",
     "* LS352 (ADR-018) and this is its VENDOR model - the only real device\n"
     "* model in this deck besides the LSK489.", 1,
     "la frase di L22 rimessa"),
    ("c02_forma_tranne", "tb_mute_corto",
     "tutto tranne LS352 e' segnaposto, LSK489 compreso",
     "tutto tranne LS352 e LSK489 e' segnaposto, compreso", 1,
     "l'LSK489 rimesso fra le eccezioni"),
    ("c03_forma_kf_but", "tb_trim",
     "* NOISE IS A FLOOR (KF = 0 on every model, the LSK489's LSK489X placeholder\n",
     "* NOISE IS A FLOOR (placeholder models, KF = 0 but on the LSK489, sic\n", 1,
     "«KF = 0 but on the LSK489» rimesso"),
    ("c04_forma_diretta_vendor", "tb_ac",
     "* OTHER device here is a hand-written placeholder too, and none has 1/f.\n",
     "* OTHER device here is a hand-written placeholder too, and none has 1/f.\n"
     "* The LSK489 is a vendor model.\n", 1,
     "«The LSK489 is a vendor model»"),
    ("c05_forma_solo", "tb_ac",
     "* OTHER device here is a hand-written placeholder too, and none has 1/f.\n",
     "* OTHER device here is a hand-written placeholder too, and none has 1/f.\n"
     "*\n* Nota: solo LS352 e LSK489 hanno un modello del costruttore.\n", 1,
     "«solo LS352 e LSK489 hanno un modello del costruttore»"),
    ("c06_ls352_segnaposto", "tb_op",
     L22_FIXED,
     "* LS352 (ADR-018) and this is still a placeholder - the only one in this\n", 1,
     "il verso opposto: LS352, del costruttore, detto segnaposto"),
    ("c07_include_del_costruttore_tolto", "tb_op",
     ".include @REPO@/models/bjt_pnp/ls350.lib\n", "", 2,
     "LS350 non definito da nessun include: la provenienza non si legge"),
    ("c08_negazione_non_scatta", "tb_ac",
     "* OTHER device here is a hand-written placeholder too, and none has 1/f.\n",
     "* OTHER device here is a hand-written placeholder too, and none has 1/f.\n"
     "* The LSK489 is not a vendor model, and no deck calls it real.\n", 0,
     "una frase negata non e' un'affermazione: nessun falso allarme"),
    ("c09_parte_segnaposto_corretta", "tb_ac",
     "* OTHER device here is a hand-written placeholder too, and none has 1/f.\n",
     "* OTHER device here is a hand-written placeholder too, and none has 1/f.\n"
     "* The 2N5551 is a placeholder.\n", 0,
     "una frase vera in forma diretta: nessun falso allarme"),
    ("c10_2n5551_vendor", "tb_ac",
     "* OTHER device here is a hand-written placeholder too, and none has 1/f.\n",
     "* OTHER device here is a hand-written placeholder too, and none has 1/f.\n"
     "* The 2N5551 is a vendor model.\n", 1,
     "un altro dispositivo detto del costruttore"),
]


def main():
    repo = os.path.abspath(sys.argv[1])
    tb = os.path.join(repo, "spice", "preamp", "tb")
    guard = os.path.join(repo, "scripts", "check_deck_provenance.py")
    wrong = 0
    for name, deck, old, new, expected, why in CASES:
        with open(os.path.join(tb, deck + ".cir")) as fh:
            text = fh.read()
        if old is not None:
            n = text.count(old)
            if n != 1:
                print(f"{name}: testo da sabotare trovato {n} volte in {deck}.cir - caso non valido")
                wrong += 1
                continue
            text = text.replace(old, new)
        out = os.path.join(HERE, f"{name}.cir")
        with open(out, "w") as fh:
            fh.write(text)
        r = subprocess.run(["/usr/bin/python3", guard, repo, out],
                           capture_output=True, text=True)
        ok = r.returncode == expected
        wrong += not ok
        print(f"{'OK  ' if ok else 'ERR '} {name}: rc {r.returncode}, atteso {expected} - {why}")
        for ln in r.stdout.splitlines():
            if "CONTRADICTED" in ln or ln.startswith("UNREADABLE") or ": calls" in ln or ": says" in ln:
                print(f"       {ln.strip()}")
    print(f"{len(CASES) - wrong} casi su {len(CASES)} come attesi")
    return 1 if wrong else 0


if __name__ == "__main__":
    sys.exit(main())
