#!/usr/bin/env python3
"""sabotaggi.py : ogni controllo nuovo di build_dossier.py (L51c) fatto fallire, e quelli di
L51a e L51b rieseguiti.

    /usr/bin/python3 docs/preamp/data/2026-10-10/L51c/script/sabotaggi.py

Come L51b/script/sabotaggi.py: per ogni sabotaggio una sostituzione di testo in UN file
versionato, il generatore lanciato, il file rimesso com'era byte per byte. Il sabotaggio e'
"caduto" se il generatore esce != 0 e la sua uscita contiene il motivo atteso.

Una differenza da L51a e L51b: da L51c la pagina e' completa e il generatore, quando passa,
SCRIVE accanto a se' (index.html, figure, schemi, immagini, summary). Un sabotaggio che non
cadesse lascerebbe la pagina sbagliata nel repo: per questo la cartella del dossier si
fotografa prima e si rimette com'era dopo ogni caso, file nuovi compresi. Alla fine il
generatore corre sui file veri e deve ridare la stessa cartella byte per byte.

Le liste di L51a e L51b si importano dai loro script e si rieseguono tali e quali. Un
sabotaggio che non si applica piu' (il testo da sostituire non c'e') si dichiara NON
APPLICABILE con la ragione, non si toglie. L'ultimo caso non tocca file: --standalone dentro
il repo dev'essere rifiutato anche con la pagina completa.

Un sabotaggio che non cade vuol dire un controllo che non controlla: esce 1.
"""
import importlib.util
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 6))
BUILD = os.path.join(REPO, "docs", "preamp", "dossier", "build_dossier.py")
DOSSIER = os.path.dirname(BUILD)
G = "docs/preamp/dossier/build_dossier.py"
C = "docs/preamp/data/2026-10-10/L51c/"
A9 = "docs/preamp/data/2026-10-09/L49a/"
B9 = "docs/preamp/data/2026-10-09/L49b/"
R = "docs/preamp/REQUIREMENTS.md"
RB = "docs/preamp/reports/2026-10-09-L49b-alimentatore-assieme.md"

# (nome, file, vecchio, nuovo, frammento atteso nel rifiuto)
SAB = [
    # la guardia del giorno delle schede
    ("schede_da_prima", G, 'L49A = os.path.join(DATAROOT, "2026-10-09", "L49a")',
     'L49A = os.path.join(DATAROOT, "2026-10-06", "L48a")', "il giorno delle schede di prova"),
    # la DRC di oggi contro il 9 ottobre
    ("drc_oggi_violazione", C + "drc/drc_audio_routed.json", '"violations": []',
     '"violations": [{}]', "DRC audio: oggi"),
    ("drc_altro_kicad", C + "drc/drc_psu_routed.json", '"kicad_version": "10.0.6"',
     '"kicad_version": "10.0.7"', "non sono la stessa prova"),
    # le misure incrociate
    ("placement_non_measure", A9 + "placement.json", "399.0", "398.0",
     "non danno la stessa scheda"),
    ("assieme_A0_ci_sta", B9 + "assembly/assembly.json", '"fits": false', '"fits": true',
     "le varianti che ci stanno"),
    ("vincoli_numerati", RB, "2. **I regolatori VQFN**", "3. **I regolatori VQFN**",
     "i vincoli non sono numerati"),
    ("immagine_non_png", B9 + "assembly/assembly_A_tutto_sul_fondo.png", "PNG", "PNX",
     "non e' un PNG"),
    ("immagine_mancante", G, '(L49B, "assembly", "assembly_A_tutto_sul_fondo.png")',
     '(L49B, "assembly", "assembly_Z.png")', "manca"),
    # la distorsione
    ("thd_csv_non_log", C + "distorsione/run/oggi/distorsione.csv", "0.0005962", "0.0005972",
     "la THD del log"),
    ("imd_non_l46b", C + "distorsione/run/oggi/distorsione.csv", "-130.8,-146.5", "-130.8,-146.6",
     "in L46b"),
    ("blocco_non_oggi", C + "distorsione/inc/oggi.inc", "C104 NREF VMINUS 100u",
     "C104 NREF VMINUS 101u", "non e' spice/preamp/gain_block_flat.inc"),
    ("deck_non_l46b", C + "distorsione/deck/oggi/thd_1k.cir", ".options reltol=1e-6",
     ".options reltol=1e-5", "distorsione, thd_1k"),
    ("corsa_rc", C + "distorsione/run/esiti.tsv", "oggi\tthd_10k\t0", "oggi\tthd_10k\t1", "rc 1"),
    ("log_distorsione", C + "distorsione/run/oggi/thd_20k/thd_20k.log", "L46A_CASO modo=0 livello=lo",
     "Error: sabotaggio\nL46A_CASO modo=0 livello=lo", "il log ha"),
    ("tetti_v4", R, "non cresce verso gli acuti", "non sale verso gli acuti", "tabella di V4"),
]


def carica(path, nome):
    spec = importlib.util.spec_from_file_location(nome, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def build(args=()):
    p = subprocess.run([sys.executable, BUILD, *args], capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def foto():
    out = {}
    for n in sorted(os.listdir(DOSSIER)):
        p = os.path.join(DOSSIER, n)
        if os.path.isfile(p):
            with open(p, "rb") as f:
                out[n] = f.read()
    return out


def rimetti(snap):
    for n in os.listdir(DOSSIER):
        p = os.path.join(DOSSIER, n)
        if os.path.isfile(p) and n not in snap:
            os.remove(p)
    for n, b in snap.items():
        with open(os.path.join(DOSSIER, n), "wb") as f:
            f.write(b)


def main():
    rc, out = build()
    if rc != 0:
        print("il generatore non passa sui file veri:\n" + out)
        return 1
    snap = foto()
    liste = [("L51a", carica(os.path.join(REPO, "docs/preamp/data/2026-10-09/L51a/script/sabotaggi.py"),
                             "sab_l51a").SAB),
             ("L51b", carica(os.path.join(REPO, "docs/preamp/data/2026-10-09/L51b/script/sabotaggi.py"),
                             "sab_l51b").SAB),
             ("L51c", SAB)]
    bad, n = 0, 0
    righe = []
    for lotto, sab in liste:
        righe.append(f"== {lotto}: {len(sab)} sabotaggi")
        for nome, rel, old, new, atteso in sab:
            n += 1
            path = os.path.join(REPO, rel)
            with open(path, "rb") as f:
                orig = f.read()
            txt = orig.decode("utf-8", errors="surrogateescape")
            if txt.count(old) < 1:
                righe.append(f"NON APPLICABILE {lotto} {nome}: «{old[:60]}» non c'e' in {rel}")
                bad += 1
                continue
            with open(path, "wb") as f:
                f.write(txt.replace(old, new, 1).encode("utf-8", errors="surrogateescape"))
            try:
                rc, out = build()
            finally:
                with open(path, "wb") as f:
                    f.write(orig)
                rimetti(snap)
            caduto = rc != 0 and atteso in out
            if not caduto:
                bad += 1
            motivo = next((ln.strip() for ln in out.splitlines() if atteso in ln), out.strip()[-120:])
            righe.append(f"{'CADE   ' if caduto else 'PASSA! '} {lotto} {nome}: rc={rc} | {motivo[:150]}")
    # l'ultimo: la pagina autoconsistente dentro il repo, anche con la pagina completa
    n += 1
    prova = os.path.join(DOSSIER, "prova.html")
    rc, out = build(["--standalone", prova])
    rimetti(snap)
    caduto = rc != 0 and "sta dentro il repository" in out
    if not caduto:
        bad += 1
    righe.append(f"{'CADE   ' if caduto else 'PASSA! '} pagina_autoconsistente_nel_repo: rc={rc}")
    if os.path.exists(prova):
        righe.append("ERRORE: prova.html e' stato scritto nel repo")
        bad += 1
    rc, out = build()
    righe.append(f"generatore sui file veri dopo i sabotaggi: rc={rc}")
    if rc != 0:
        bad += 1
    if foto() != snap:
        righe.append("ERRORE: la cartella del dossier non e' tornata quella di prima byte per byte")
        bad += 1
    else:
        righe.append("la cartella del dossier e' quella di prima, byte per byte")
    righe.append(f"{n - bad} sabotaggi su {n} cadono come devono")
    with open(os.path.join(HERE, "..", "sabotaggi.txt"), "w") as f:
        f.write("\n".join(righe) + "\n")
    print("\n".join(righe))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
