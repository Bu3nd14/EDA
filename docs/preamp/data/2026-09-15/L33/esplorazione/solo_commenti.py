#!/usr/bin/env python3
"""L33 - prova che la correzione dei deck tocca SOLO righe di commento.

    /usr/bin/python3 solo_commenti.py <cartella-deck-di-main> <cartella-deck-nuova>

Per ogni deck .cir presente in una delle due cartelle:
  1. ogni riga tolta o aggiunta dal diff (difflib, contesto 0) comincia con '*',
     che per ngspice e' una riga di commento;
  2. la sequenza delle righe NON di commento e' identica a quella di main.
Anche l'insieme dei file deve coincidere. Esce 0 se tutto regge, 1 altrimenti.
Un controllo mai fatto fallire non e' un controllo: va lanciato anche su una
copia sabotata (una riga non di commento cambiata) e deve uscire 1.
"""

import difflib
import os
import sys


def decks(d):
    return {f for f in os.listdir(d) if f.endswith(".cir")}


def lines(path):
    with open(path, errors="replace") as fh:
        return fh.read().splitlines()


def main():
    old_dir, new_dir = sys.argv[1], sys.argv[2]
    bad = 0
    a, b = decks(old_dir), decks(new_dir)
    if a != b:
        print(f"   INSIEMI DIVERSI: solo in main {sorted(a - b)}, solo nuovi {sorted(b - a)}")
        bad += 1
    changed = 0
    for name in sorted(a & b):
        old, new = lines(os.path.join(old_dir, name)), lines(os.path.join(new_dir, name))
        diff = [ln for ln in difflib.unified_diff(old, new, lineterm="", n=0)
                if ln[:1] in "+-" and not ln.startswith(("+++", "---"))]
        non_comment = [ln for ln in diff if not ln[1:].startswith("*")]
        same_code = ([x for x in old if not x.startswith("*")]
                     == [x for x in new if not x.startswith("*")])
        if diff:
            changed += 1
        if non_comment or not same_code:
            bad += 1
            print(f"   NON SOLO COMMENTI: {name}")
            for ln in non_comment:
                print(f"      {ln}")
            if not same_code:
                print("      le righe non di commento non coincidono con main")
        elif diff:
            plus = sum(1 for ln in diff if ln[0] == "+")
            print(f"   OK {name}: -{len(diff) - plus} +{plus} righe, tutte '*'")
    print(f"{changed} deck cambiati, {bad} con righe non di commento toccate")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
