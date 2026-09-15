#!/usr/bin/env python3
"""verifica.py - ogni sabotaggio di genera.py deve essere rifiutato, e per la
ragione giusta (L13).

Uso: /usr/bin/python3 verifica.py <repo-root>

Presuppone che ogni c<x>.cir sia gia' stato eseguito con
    run_simulation.sh c<x>.cir out_<x>
Per ogni sabotaggio lancia e4.py sull'output (o il blocco 2g sul deck, per f)
e confronta l'esito con quello atteso: exit != 0 e, fra le sigle dei
controlli falliti, quelle attese. Scrive esito.txt accanto a se'.
Esce 0 se tutti i sabotaggi sono rifiutati come attesi, 1 altrimenti.
"""
import os
import re
import subprocess
import sys

# sabotaggio -> (strumento, sigle che DEVONO comparire fra i controlli falliti)
ATTESI = {
    "a": ("e4", "FG"),   # sorgente accesa: MAIN non costante, fisse lontane da L17
    "b": ("e4", "D"),    # sonda su BOUT: Re(Z) < 47 ohm, niente condensatore
    "c0": ("e4", "A"),   # attenuatore scollegato: segnale zero, vdb(0) -> Error, guadagno vuoto
    "c": ("e4", "C"),    # attenuatore scavalcato: il guadagno non segue la manopola
    "d": ("e4", "DF"),   # cursore: il passivo di ADR-002, non costante
    "e": ("e4", "D"),    # FIX2 letta su FIX1: diafonia, non impedenza
    "f": ("2g", ""),     # RG10 non terminato: cade il 2g
    "g": ("e4", "C"),    # K1 che non chiude: il guadagno non segue il modo
}


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    root = sys.argv[1]
    here = os.path.dirname(os.path.abspath(__file__))
    e4 = os.path.join(here, "..", "script", "e4.py")
    righe, tutti = [], True
    for k, (tool, sigle) in ATTESI.items():
        if tool == "e4":
            cmd = ["/usr/bin/python3", e4, os.path.join(here, f"out_{k}")]
        else:
            cmd = ["/usr/bin/python3", os.path.join(root, "scripts", "check_deck_refs.py"),
                   root, os.path.join(here, f"c{k}.cir")]
        p = subprocess.run(cmd, capture_output=True, text=True)
        out = p.stdout + p.stderr
        m = re.search(r"sigle ([A-G]+)", out)
        trovate = m.group(1) if m else ""
        ok = p.returncode == 1 and all(s in trovate for s in sigle)
        tutti &= ok
        righe.append(f"--- sabotaggio {k}: {tool}, rc {p.returncode}, sigle fallite "
                     f"'{trovate}', attese '{sigle}' -> {'COME ATTESO' if ok else 'NON COME ATTESO'}")
        righe.append(out.rstrip())
    righe.append("")
    n = len(ATTESI)
    righe.append(f"ESITO: {f'{n} sabotaggi su {n} rifiutati come attesi' if tutti else 'ALMENO UN SABOTAGGIO NON RIFIUTATO COME ATTESO'}")
    txt = "\n".join(righe) + "\n"
    open(os.path.join(here, "esito.txt"), "w").write(txt)
    print(txt)
    return 0 if tutti else 1


if __name__ == "__main__":
    sys.exit(main())
