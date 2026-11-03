#!/usr/bin/env python3
"""sabotaggi.py : ogni controllo di build_dossier.py fatto fallire, con la pagina completa (L68).

    /usr/bin/python3 docs/preamp/data/2026-11-03/L68/script/sabotaggi.py

Come L64c/script/sabotaggi.py, di cui riprende la lista (importata: il suo sabotaggi.txt resta com'e'),
con due cambi e cinque sabotaggi nuovi:
  - la FMEA di oggi e la copertura il generatore le legge ora da L68: i due sabotaggi di L64c su
    L64c/fmea_oggi.csv e L64c/copertura.csv passerebbero, e qui toccano i file di L68 (la copertura di
    L68 non ha piu' parti dell'alimentatore: il sabotaggio ne aggiunge una);
  - le righe di L68 (fmea_l68.csv, la sesta fonte): una priorita' contro la matrice, una non conformita'
    che non c'e', una parte che non esiste, la FMEA di oggi riscritta su una riga di L68, uno stato
    senza la sua decisione.
Per ogni sabotaggio una sostituzione di testo (la prima occorrenza) in UN file versionato, il generatore
lanciato, il file rimesso com'era byte per byte. Il sabotaggio e' «caduto» se il generatore esce != 0 e
la sua uscita contiene il motivo atteso. Prima e dopo, il generatore sui file veri deve uscire 0. A
priorita' bassa.
"""
import importlib.util
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "..", ".."))
D = "docs/preamp/data/"
BUILD = os.path.join(REPO, "docs", "preamp", "dossier", "build_dossier.py")
L = D + "2026-11-03/L68/"


def modulo(path):
    s = importlib.util.spec_from_file_location("sab_l64c", path)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


L64C = modulo(os.path.join(REPO, D, "2026-11-03/L64c/script/sabotaggi.py"))
RIPORTATI = {
    "L64c/fmea_oggi_riscritta": ("L64c/fmea_oggi_riscritta (su L68)", L + "fmea_oggi.csv"),
    "L64c/copertura_riscritta": None,
}
SAB = []
for x in L64C.SAB:
    if x[0] in RIPORTATI:
        if RIPORTATI[x[0]] is None:
            continue
        nome, f = RIPORTATI[x[0]]
        SAB.append((nome, f) + tuple(x[2:]))
    else:
        SAB.append(tuple(x))
# (nome, file, vecchio, nuovo, frammento atteso nel rifiuto)
SAB += [
    ("L68/copertura_riscritta", L + "copertura.csv", "scheda,parte_senza_riga\n",
     "scheda,parte_senza_riga\nalimentatore,C545\n", "copertura.csv ne dice"),
    ("L68/fmea_priorita_contro_la_matrice", L + "fmea_l68.csv", ',alta,"NC-079 (maggiore, prima di G1)"',
     ',media,"NC-079 (maggiore, prima di G1)"', "la matrice di ADR-070"),
    ("L68/fmea_non_conformita_che_non_esiste", L + "fmea_l68.csv", "NC-079 (maggiore, prima di G1)",
     "NC-998 (maggiore, prima di G1)", "NC-998 non e' nel registro"),
    ("L68/fmea_parte_che_non_esiste", L + "fmea_l68.csv", "\ntemporizzatore (L68),L68,Q513,",
     "\ntemporizzatore (L68),L68,Q913,", "Q913 non sta in nessuna netlist"),
    ("L68/fmea_oggi_riscritta_su_L68", L + "fmea_oggi.csv", "(la sonda che scivola)", "(la sonda scivola)",
     "non e' quella ricomposta"),
    ("L68/fmea_riga_alla_diagnosi", L + "fmea_l68.csv", "misurata, nessun rimedio",
     "alla diagnosi, nessun rimedio", "ancora alla diagnosi"),
]


def build(args=()):
    p = subprocess.run(["nice", "-n", "15", sys.executable, BUILD, *args],
                       capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def main():
    rc, out = build()
    if rc != 0:
        print("il generatore sui file veri non esce 0: niente da sabotare\n" + out[-2000:])
        return 1
    bad, righe = 0, []
    for nome, rel_, old, new, atteso in SAB:
        path = os.path.join(REPO, rel_)
        with open(path, "rb") as f:
            orig = f.read()
        txt = orig.decode("utf-8")
        if old not in txt:
            righe.append(f"MANCA  {nome}: il testo da sabotare non c'e' in {rel_}")
            bad += 1
            print(righe[-1], flush=True)
            continue
        try:
            with open(path, "wb") as f:
                f.write(txt.replace(old, new, 1).encode("utf-8"))
            rc, out = build()
        finally:
            with open(path, "wb") as f:
                f.write(orig)
        caduto = rc != 0 and atteso in out
        bad += not caduto
        righe.append(f"{'CADE   ' if caduto else 'PASSA! '} {nome}: rc={rc}"
                     + ("" if caduto else f" ({out.strip()[-300:]!r})"))
        print(righe[-1], flush=True)
    rc, out = build()
    righe.append(f"generatore sui file veri dopo i sabotaggi: rc={rc}")
    bad += rc != 0
    n = len(SAB)
    righe.append(f"{n - bad + (rc != 0)} sabotaggi su {n} cadono come devono")
    with open(os.path.join(HERE, "..", "sabotaggi.txt"), "w") as f:
        f.write("\n".join(righe) + "\n")
    print("\n".join(righe[-2:]))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
