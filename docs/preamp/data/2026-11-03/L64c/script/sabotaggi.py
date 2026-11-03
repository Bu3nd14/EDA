#!/usr/bin/env python3
"""sabotaggi.py : ogni controllo di build_dossier.py fatto fallire, con la pagina completa (L64c).

    /usr/bin/python3 docs/preamp/data/2026-11-03/L64c/script/sabotaggi.py

Come L64a/script/sabotaggi.py e L64b/script/sabotaggi.py, di cui riprende le liste (importate, non
copiate: i loro sabotaggi.txt restano come sono), piu' quelli dei controlli nuovi di L64c: gli schemi
completi, la FMEA di oggi, i conti delle schede di prova. Per ogni sabotaggio una sostituzione di testo
(la prima occorrenza) in UN file versionato, il generatore lanciato, il file rimesso com'era byte per
byte. Il sabotaggio e' «caduto» se il generatore esce != 0 e la sua uscita contiene il motivo atteso.
Prima e dopo, il generatore sui file veri deve uscire 0. Con la pagina completa il generatore scrive
accanto a se' solo quando passa: un sabotaggio che cade non scrive niente, e il giro finale riscrive
la pagina vera. A priorita' bassa.
"""
import importlib.util
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "..", ".."))
D = "docs/preamp/data/"
BUILD = os.path.join(REPO, "docs", "preamp", "dossier", "build_dossier.py")
L = D + "2026-11-03/L64c/"
S = "docs/preamp/schematic/"


def lista(path):
    s = importlib.util.spec_from_file_location("sab_" + os.path.basename(os.path.dirname(os.path.dirname(path))), path)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m.SAB


# (nome, file, vecchio, nuovo, frammento atteso nel rifiuto)
NUOVI = [
    # 19. gli schemi completi
    ("schema_audio_contro_la_netlist", S + "audio.manifest.json", '"1": "VLIM_P"', '"1": "VLIM_X"',
     "check_schematic.py rc"),
    ("schema_psu_ridisegnato_diverso", S + "psu.svg", "stroke-width: 0.7", "stroke-width: 0.8",
     "gli schemi ridisegnati"),
    # 20. la FMEA di oggi
    ("fmea_priorita_contro_la_matrice", L + "fmea_l64c.csv", ",1,2.4,2,3,bassa,", ",1,2.4,2,3,media,",
     "la matrice di ADR-070"),
    ("fmea_oggi_riscritta", L + "fmea_oggi.csv", "il canale + cieco:", "il canale + cieco, ",
     "non e' quella ricomposta"),
    ("fmea_riga_ancora_alla_diagnosi", L + "fmea_l64c.csv", "misurata: la riserva e' il temporizzatore",
     "alla diagnosi, la riserva e' il temporizzatore", "ancora alla diagnosi"),
    ("fmea_micro_nell_effetto", L + "fmea_l64c.csv", "il canale + cieco:", "il micro cieco:",
     "il micro non c'e'"),
    ("fmea_stato_su_decisione_superata", L + "fmea_l64c.csv", "misurata: la riserva e' il temporizzatore",
     "misurata (ADR-073): la riserva e' il temporizzatore", "lo stato cita ADR-073"),
    ("fmea_parte_che_non_esiste", D + "2026-10-24/L45d2b3b3/fmea_dopo.csv", ",R550,", ",R950,",
     "R950 non sta in nessuna netlist"),
    ("fmea_non_conformita_che_non_esiste", L + "fmea_l64c.csv", "accettata (ADR-114, come C536",
     "accettata (ADR-114, NC-999, come C536", "NC-999 non e' nel registro"),
    ("fmea_riga_nuova_di_L64c", L + "fmea_l64c.csv", ",R517,", ",R917,", "non sostituisce una riga"),
    ("copertura_riscritta", L + "copertura.csv", "alimentatore,C545", "alimentatore,C945",
     "copertura.csv ne dice"),
    # 21. le schede di prova contro le netlist di oggi
    ("parti_delle_schede_riscritte", L + "parti_schede.csv", "audio,_totale,458 / 653", "audio,_totale,459 / 653",
     "parti_schede.py rieseguito"),
]
SAB = ([("L64a/" + x[0],) + tuple(x[1:]) for x in lista(os.path.join(REPO, D, "2026-11-02/L64a/script/sabotaggi.py"))]
       + [("L64b/" + x[0],) + tuple(x[1:]) for x in lista(os.path.join(REPO, D, "2026-11-03/L64b/script/sabotaggi.py"))]
       + [("L64c/" + x[0],) + tuple(x[1:]) for x in NUOVI])


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
