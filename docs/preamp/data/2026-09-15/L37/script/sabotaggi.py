#!/usr/bin/env python3
"""L37: i controlli di E4 in build_dossier.py, fatti fallire.

Uso: /usr/bin/python3 sabotaggi.py <repo> <cartella di lavoro>

Per ogni caso costruisce <lavoro>/<caso>/ come un repo finto:
  - spice/, models/, docs/preamp/schematic/, data/2026-09-14/ e L13/prima|esplorazione
    sono symlink al repo vero;
  - data/2026-09-15/L13/dopo/<deck>/<file> sono symlink file per file, e il caso ne
    sostituisce qualcuno con una copia alterata;
  - docs/preamp/dossier/ contiene una COPIA del builder (REPO si ricava da li') e
    di svgplot.py; un caso puo' alterare il builder copiato con sostituzioni che
    devono comparire esattamente una volta. Il builder versionato non si tocca.
Poi lancia il builder copiato e registra rc, file scritti e i messaggi. Un caso
passa solo se TUTTI i messaggi attesi ci sono e NESSUNO di quelli esclusi.

Esce 0 solo se ogni caso esce come atteso.
"""
import os
import re
import shutil
import subprocess
import sys

REPO, WORK = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
D15 = os.path.join(REPO, "docs/preamp/data/2026-09-15/L13")
PY = sys.executable

SIG = "contiene il segnale del modo"            # firma #28, measure_zout
XDECK = "non misurano la stessa impedenza"      # incrocio fra deck, measure_e4

CASES = [
    # nome, {file: alterazione}, [sostituzioni nel builder], attesi, esclusi, descrizione
    ("intatto", {}, [], [], [], "nessuna alterazione"),
    ("contaminata", {"tb_zout_psrr_noise/*": "prima"}, [], [SIG, XDECK], [],
     "dopo/tb_zout_psrr_noise sostituito da prima/: la Zout con VSRC accesa, al percorso giusto"),
    ("contaminata_senza_incrocio", {"tb_zout_psrr_noise/*": "prima"},
     [("            if bad:\n", "            if False and bad:\n")], [SIG], [XDECK],
     "come sopra, builder senza l'incrocio fra deck: deve cadere la sola firma"),
    ("contaminata_senza_firma", {"tb_zout_psrr_noise/*": "prima"},
     [('        if not r["za1k"] < ZSIG_FRAC * r["glin"]:\n', "        if False:\n")],
     [XDECK], [SIG],
     "come sopra, builder senza la firma: deve cadere il solo incrocio"),
    ("radice_L27", {},
     [('L13 = os.path.join(DATA15, "L13", "dopo")', 'L13 = os.path.join(DATA, "L27", "dopo")')],
     ["sorgente AC accesa (NC-033, #28)"], [], "la radice di E4 puntata sui dati di L27"),
    ("tab_zrmax", {"tb_e4_uscite/tb_e4_uscite_tab.csv": ("sub", "main,0,0,0db,60.0504,",
                                                         "main,0,0,0db,61.0504,")}, [],
     ["tb_e4_uscite_tab.csv [zrmax]: riga 2", "e4.py esce 1"], [],
     "tb_e4_uscite_tab.csv, zrmax della prima riga 60,0504 -> 61,0504"),
    ("tab_cella_vuota", {"tb_e4_uscite/tb_e4_uscite_tab.csv": (
        "sub", "main,0,0,0db,60.0504,60.0504,47.0313,47.0262,1693.38,57.9449,0.0386443,",
        "main,0,0,0db,60.0504,60.0504,47.0313,47.0262,1693.38,57.9449,,")}, [],
     ["celle vuote", "(#26)"], [], "tb_e4_uscite_tab.csv, zn1k della prima riga svuotata"),
    ("tab_riga_tolta", {"tb_e4_uscite/tb_e4_uscite_tab.csv": ("droplast",)}, [],
     ["attese 135 righe, trovate 134"], [], "tb_e4_uscite_tab.csv, ultima riga tolta"),
    ("log_error", {"tb_e4_uscite/tb_e4_uscite.log": ("append", "Error: riga di sabotaggio\n")},
     [], ["righe 'Error' (#26)"], [], "una riga Error aggiunta in coda al log di tb_e4_uscite"),
    ("dispersione_alterata", {},
     [('            g[c + "_disp"] = max(vs) - min(vs)\n',
       '            g[c + "_disp"] = max(vs) - min(vs) + 1e-3\n')],
     ["dispersione Re(Z)max: dossier"], [],
     "il builder calcola la dispersione 1 mΩ piu' larga: la seconda strada, e4.py, dissente"),
]


def link(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    os.symlink(src, dst)


def build_tree(case, alter, subs):
    root = os.path.join(WORK, case)
    if os.path.exists(root):
        shutil.rmtree(root)
    for p in ("spice", "models", "docs/preamp/schematic", "docs/preamp/data/2026-09-14"):
        link(os.path.join(REPO, p), os.path.join(root, p))
    for p in ("prima", "esplorazione"):
        link(os.path.join(D15, p), os.path.join(root, "docs/preamp/data/2026-09-15/L13", p))
    for deck in ("tb_zout_psrr_noise", "tb_e4_uscite"):
        sd = os.path.join(D15, "dopo", deck)
        for f in sorted(os.listdir(sd)):
            key, dst = f"{deck}/{f}", os.path.join(root, "docs/preamp/data/2026-09-15/L13/dopo", deck, f)
            how = alter.get(key) or alter.get(f"{deck}/*")
            if how is None:
                link(os.path.join(sd, f), dst)
            elif how == "prima":
                link(os.path.join(D15, "prima", deck, f), dst)
            else:
                text = open(os.path.join(sd, f)).read()
                if how[0] == "sub":
                    if text.count(how[1]) != 1:
                        raise SystemExit(f"{case}: {how[1]!r} compare {text.count(how[1])} volte in {key}")
                    text = text.replace(how[1], how[2])
                elif how[0] == "droplast":
                    text = "".join(text.splitlines(True)[:-1])
                elif how[0] == "append":
                    text += how[1]
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                open(dst, "w").write(text)
    dd = os.path.join(root, "docs/preamp/dossier")
    os.makedirs(dd)
    shutil.copy(os.path.join(REPO, "docs/preamp/dossier/svgplot.py"), dd)
    code = open(os.path.join(REPO, "docs/preamp/dossier/build_dossier.py")).read()
    for a, b in subs:
        if code.count(a) != 1:
            raise SystemExit(f"{case}: la sostituzione {a!r} compare {code.count(a)} volte nel builder")
        code = code.replace(a, b)
    open(os.path.join(dd, "build_dossier.py"), "w").write(code)
    return dd


def naive_ratio():
    """Il criterio letterale «la Zout al nodo scala col guadagno», sui dati veri."""
    def prints(path, key):
        pat = re.compile(r"^" + re.escape(key) + r" = (\S+)\s*$")
        return [float(m.group(1)) for m in (pat.match(l.rstrip("\n")) for l in open(path)) if m]
    g = prints(os.path.join(REPO, "docs/preamp/data/2026-09-14/L27/dopo/tb_ac/tb_ac.log"), "g1k")
    glin = [10 ** (g[i] / 20) for i in (0, 4, 8)]
    out = []
    for tag in ("prima", "dopo"):
        za = prints(os.path.join(D15, tag, "tb_zout_psrr_noise/tb_zout_psrr_noise.log"), "za1k")
        worst = max(abs((za[i] / za[0]) / (glin[i] / glin[0]) - 1) for i in (1, 2))
        out.append((tag, worst, worst < 0.01))
    return out


def main():
    os.makedirs(WORK, exist_ok=True)
    ok_all = True
    print(f"{'caso':<28} {'rc':>3} {'file':>4}  esito")
    for name, alter, subs, want, avoid, desc in CASES:
        dd = build_tree(name, alter, subs)
        before = set(os.listdir(dd))
        p = subprocess.run([PY, os.path.join(dd, "build_dossier.py")], capture_output=True, text=True)
        written = len(set(os.listdir(dd)) - before - {"__pycache__"})
        msgs = [l.strip()[2:] for l in p.stderr.splitlines() if l.strip().startswith("- ")]
        if p.stderr.startswith("RIFIUTATO: la Zout"):
            msgs = [p.stderr.strip()]
        err = p.stderr
        if name == "intatto":
            good = p.returncode == 0 and written > 0 and not msgs
        else:
            good = (p.returncode != 0 and written == 0 and all(w in err for w in want)
                    and not any(a in err for a in avoid))
        ok_all &= good
        print(f"{name:<28} {p.returncode:>3} {written:>4}  {'come atteso' if good else 'INATTESO'}"
              f"  — {desc}")
        for m in msgs[:6]:
            print(f"      · {m[:220]}")
        if len(msgs) > 6:
            print(f"      · ... e altri {len(msgs) - 6}")
        if not good and p.returncode != 0 and not msgs:
            print("      stderr: " + err.strip()[-400:])
    print("\nIl criterio ingenuo «rapporto fra i modi = rapporto dei guadagni, entro 1 %»:")
    for tag, worst, fires in naive_ratio():
        print(f"   L13 {tag:<6} scarto massimo {worst:.2e} -> {'SCATTA' if fires else 'non scatta'}")
    print("   (scatta su entrambi: non distingue la Zout contaminata da quella vera)")
    print("\nTUTTI I CASI COME ATTESI" if ok_all else "\nALMENO UN CASO INATTESO")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
