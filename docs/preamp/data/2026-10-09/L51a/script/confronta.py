#!/usr/bin/env python3
"""L51a: la ricorsa di oggi (L51a/dopo) contro le corse dello stesso circuito, file per file.

    /usr/bin/python3 confronta.py

Da L48b (c098be70) circuito, deck e modelli non sono cambiati, quindi ogni CSV deve essere
UGUALE byte per byte a quello della seconda strada:
  - i 21 deck veloci        contro L48b/regressione/dopo/<deck>/
  - tb_f1_selettore         contro L48a/misure/tb_f1_selettore/ (L48b non l'ha ricorso;
                            L48b ha toccato trim e volume, non la rete d'ingresso: se cambia
                            si scrive, non si assume)
  - le copie col bilanciamento contro L48b/{e5,v1}_bilanciamento/out/
Per ogni CSV diverso, le colonne che cambiano col loro scarto relativo massimo. Scrive
../confronto.txt. Anche l'rc di ogni deck da esiti.tsv.
"""
import csv
from pathlib import Path

QUI = Path(__file__).resolve().parent
L = QUI.parent
DATA = L.parent.parent
DOPO = L / "dopo"
L48B = DATA / "2026-10-07" / "L48b"
L48A = DATA / "2026-10-06" / "L48a"

COPPIE = [(DOPO / d.name, d) for d in sorted((L48B / "regressione" / "dopo").iterdir())
          if d.is_dir()]
COPPIE += [(DOPO / "tb_f1_selettore", L48A / "misure" / "tb_f1_selettore"),
           (DOPO / "bilanciamento" / "tb_e5_bilanciamento", L48B / "e5_bilanciamento" / "out"),
           (DOPO / "bilanciamento" / "tb_loop_bilanciamento", L48B / "v1_bilanciamento" / "out")]


def num(x):
    try:
        return float(x)
    except ValueError:
        return None


righe, n_file, n_uguali = [], 0, 0
for oggi, prima in COPPIE:
    for f in sorted(prima.glob("*.csv")):
        g = oggi / f.name
        etichetta = f"{oggi.relative_to(DOPO)}/{f.name}"
        n_file += 1
        if not g.exists():
            righe.append(f"MANCA  {etichetta}")
            continue
        if f.read_bytes() == g.read_bytes():
            n_uguali += 1
            continue
        a = list(csv.reader(f.open()))
        b = list(csv.reader(g.open()))
        if len(a) != len(b) or a[0] != b[0]:
            righe.append(f"FORMA  {etichetta}: righe {len(a)} -> {len(b)}")
            continue
        diff = {}
        for ra, rb in zip(a[1:], b[1:]):
            for h, x, y in zip(a[0], ra, rb):
                if x == y:
                    continue
                fx, fy = num(x), num(y)
                d = (float("inf") if fx is None or fy is None
                     else abs(fy - fx) / max(abs(fx), 1e-30))
                diff[h] = max(diff.get(h, 0), d)
        righe.append(f"CAMBIA {etichetta}: " + ", ".join(
            f"{h} {d:.3g}" for h, d in sorted(diff.items())))
    nuovi = sorted({p.name for p in oggi.glob("*.csv")} - {p.name for p in prima.glob("*.csv")})
    for n in nuovi:
        righe.append(f"NUOVO  {oggi.relative_to(DOPO)}/{n}")
esiti = (DOPO / "esiti.tsv").read_text().split("\n")
rc = [e for e in esiti if e and e.split("\t")[1] != "0"]
righe.append("")
righe.append(f"{n_uguali} file su {n_file} uguali alla seconda strada; "
             f"{len([e for e in esiti if e])} deck corsi; deck con rc != 0: {rc or 'nessuno'}")
(L / "confronto.txt").write_text("\n".join(righe) + "\n")
print("\n".join(righe))
