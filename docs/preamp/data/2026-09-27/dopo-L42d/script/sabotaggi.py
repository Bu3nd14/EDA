#!/usr/bin/env python3
"""sabotaggi.py : il controllo aggiunto dopo L42d (nessun rimando dentro la propria
destinazione) fatto fallire, piu' tutti quelli di L42a, L42b e L42d rieseguiti.

    /usr/bin/python3 docs/preamp/data/2026-09-27/dopo-L42d/script/sabotaggi.py

Il difetto l'ha trovato l'utente: nella sezione 0 ogni «PR-n» in testa alla sua
voce era un link alla voce stessa. Stesso meccanismo dei lotti di prima: una
sostituzione in UN file, il generatore lanciato, il file rimesso byte per byte.
"""
import importlib.util
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "..", ".."))
CT = "docs/preamp/dossier/contratto.py"

_spec = importlib.util.spec_from_file_location(
    "sab_l42d", os.path.join(REPO, "docs", "preamp", "data", "2026-09-27", "L42d", "script",
                             "sabotaggi.py"))
L42D = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(L42D)
L42A = L42D.L42A

# (nome, file, vecchio, nuovo, frammento atteso nel rifiuto)
SAB = [
    ("voce_link_a_se_stessa", CT, '<strong class="prn">{self_id(f"PR-{n}")}</strong>',
     '<strong class="prn">PR-{n}</strong>', "link a se stesso: dentro #pr-1"),
]


def main():
    rc_prima = L42D.main()
    print("---- dopo L42d")
    bad = 0
    for nome, rel, old, new, atteso in SAB:
        path = os.path.join(REPO, rel)
        with open(path, "rb") as f:
            orig = f.read()
        txt = orig.decode("utf-8")
        if txt.count(old) < 1:
            print(f"{nome:36s} NON APPLICABILE: il testo da sabotare non c'e'")
            bad += 1
            continue
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(txt.replace(old, new, 1))
            rc, out = L42A.build()
        finally:
            with open(path, "wb") as f:
                f.write(orig)
        ok = rc != 0 and atteso in out
        bad += not ok
        riga = next((ln.strip() for ln in out.splitlines() if atteso in ln), out.strip()[-120:])
        print(f"{nome:36s} {'caduto' if ok else 'NON CADUTO'}  rc={rc}  {riga[:150]}")
    rc, out = L42A.build()
    print(f"\ndi nuovo sui file veri: generatore rc={rc}")
    print(f"dopo L42d: {len(SAB) - bad} sabotaggi su {len(SAB)} caduti; quelli di L42a, L42b e "
          f"L42d: {'tutti caduti' if rc_prima == 0 else 'NON tutti caduti'} (sopra)")
    return 1 if bad or rc or rc_prima else 0


if __name__ == "__main__":
    tee = L42D.L42B._Tee(sys.stdout)
    sys.stdout = tee
    rc = main()
    sys.stdout = tee.s
    with open(os.path.join(HERE, "sabotaggi.txt"), "w", encoding="utf-8") as f:
        f.write(re.sub(r"\x1b\[[0-9;]*m", "", "".join(tee.buf)))
    sys.exit(rc)
