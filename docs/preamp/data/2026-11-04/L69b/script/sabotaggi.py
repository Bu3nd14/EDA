#!/usr/bin/env python3
"""sabotaggi.py : ogni controllo di build_dossier.py fatto fallire, con la pagina completa (L69b).

    /usr/bin/python3 docs/preamp/data/2026-11-04/L69b/script/sabotaggi.py

Come L68/script/sabotaggi.py, di cui riprende la lista (importata: L64a, L64b, L64c, L68; il suo
sabotaggi.txt resta com'e'), con i file spostati dove il generatore li legge oggi:
  - i sabotaggi di L64b toccano i file di L69b (la stessa evidenza rifatta sul sorgente di ADR-116,
    con gli stessi nomi), coi valori di oggi dove la corsa nuova li ha cambiati (VALORI);
  - il giorno dell'alimentatore e' il 2026-11-04: il sabotaggio lo sposta al 2026-11-05;
  - parti_schede.csv e' quello di L69b; la FMEA di oggi e la copertura sono quelle di L69;
e i sabotaggi nuovi: una meta' di un pull-up cambiata nel deck corso, la lettura delle due meta' in
confronta.py, il dossier ripuntato sui dati di L64b (devono essere rifiutati), il confronto contro L64b,
le righe di L69 nella FMEA (la settima fonte).
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
L = D + "2026-11-04/L69b/"
L64B = D + "2026-11-03/L64b/"
L69 = D + "2026-11-03/L69/"


def modulo(path):
    s = importlib.util.spec_from_file_location("sab_l68", path)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


L68 = modulo(os.path.join(REPO, D, "2026-11-03/L68/script/sabotaggi.py"))
# nome -> (file, vecchio, nuovo, atteso): None tiene quello di L68
SPOSTATI = {
    "L64b/giorno_di_oggi_spostato": ("docs/preamp/dossier/build_dossier.py", 'PSU_DA = "2026-11-04"',
                                     'PSU_DA = "2026-11-05"', "non e' del 2026-11-05"),
    "L64c/parti_delle_schede_riscritte": (L + "parti_schede.csv", None, None, None),
    "L64c/fmea_oggi_riscritta (su L68)": (L69 + "fmea_oggi.csv", None, None, None),
    "L68/fmea_oggi_riscritta_su_L68": (L69 + "fmea_oggi.csv", None, None, None),
    "L68/copertura_riscritta": (L69 + "copertura.csv", None, None, None),
}
# i testi da sabotare che la corsa di oggi ha cambiato (nome -> (vecchio, nuovo)), e i sabotaggi di L68
# sulle righe di R572 / R576 in corto (NC-079): da L69 quelle righe sono sostituite da fmea_l69.csv e non
# entrano piu' nella FMEA di oggi, quindi passerebbero; qui toccano righe di L68 ancora vive
VALORI = {
    "L64b/potenza_del_calore_riscritta": ("CALORE regime_nom pt1=13.9339 ", "CALORE regime_nom pt1=13.9839 "),
    "L64b/standby_illeggibile": ("2.500-3.000 s: T2 129.76 mW", "2.500-3.000 s: T2 = 129.76 mW"),
    "L64b/tabella_della_catena_riscritta": ("spegnimento_l,MAINJACK,3.686e-09,-55.2,",
                                            "spegnimento_l,MAINJACK,3.686e-09,-45.2,"),
    "L68/fmea_priorita_contro_la_matrice": (',alta,"accettata in P9 (e), come R585 in corto (ADR-115)"',
                                            ',media,"accettata in P9 (e), come R585 in corto (ADR-115)"'),
    "L68/fmea_non_conformita_che_non_esiste": ('"accettata in P9 (e), come R585 in corto (ADR-115)"',
                                               '"NC-998 (maggiore, prima di G1)"'),
}

SAB = []
for nome, f, old, new, atteso in L68.SAB:
    if nome in SPOSTATI:
        nf, no, nn, na = SPOSTATI[nome]
        f, old, new, atteso = nf, no or old, nn or new, na or atteso
        nome += " (L69b)"
    elif f.startswith(L64B):
        f = L + f[len(L64B):]
        nome += " (su L69b)"
    if nome.split(" (")[0] in VALORI:
        old, new = VALORI[nome.split(" (")[0]]
    SAB.append((nome, f, old, new, atteso))

# (nome, file, vecchio, nuovo, frammento atteso nel rifiuto)
SAB += [
    ("L69b/meta_del_pullup_nel_deck", L + "seq/oggi/accensione/tb_psu_seq_accensione_g1.cir",
     "RR588 at_mrq_m at_mrq 100k", "RR588 at_mrq_m at_mrq 120k", "sequenza oggi/accensione"),
    ("L69b/meta_lette_come_un_altro_pullup", L + "script/confronta.py",
     '"RR576 v5 vrelay_en 10k", "at_on_m"', '"RR576 v5 vrelay_en 12k", "at_on_m"', "confronta.py"),
    ("L69b/dossier_sui_dati_di_L64b", "docs/preamp/dossier/build_dossier.py",
     'L69B = os.path.join(DATAROOT, "2026-11-04", "L69b")', 'L69B = os.path.join(DATAROOT, "2026-11-03", "L64b")',
     "non e' del 2026-11-04"),
    ("L69b/confronto_con_L64b_riscritto", L + "confronto_l64b.csv", "\n", "\nan_l64b.csv,x,y,1,1,0\n",
     "confronta_l64b.py rieseguito"),
    # la priorita' dopo il rimedio (G, P, R di dopo -> priorita_dopo) della riga di R572 in corto
    ("L69/fmea_priorita_contro_la_matrice", L69 + "fmea_l69.csv", ',1,0.025,1,3,bassa,"misurata',
     ',1,0.025,1,3,media,"misurata', "la matrice di ADR-070"),
    ("L69/fmea_parte_che_non_esiste", L69 + "fmea_l69.csv", "\ntemporizzatore (L68),L69,R572,",
     "\ntemporizzatore (L68),L69,R972,", "R972 non sta in nessuna netlist"),
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
