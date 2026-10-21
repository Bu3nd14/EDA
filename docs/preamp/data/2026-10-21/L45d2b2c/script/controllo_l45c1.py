#!/usr/bin/env python3
"""L45d2b2c: the known case of rail_alto.py. L45c1's decks of the two shorts IN-OUT
(data/2026-10-13/L45c1/seq/f_u50[12]_cortoio_mus/, giro 1 = the fixed point) are copied to
controllo/l45c1/<caso>/ with their .include paths moved from L45c1's worktree (gone) to this
repository's root; nothing else changes (asserted: only the .include lines and the first comment
line differ). controllo_l45c1.sh runs them; rail_alto.py must read +20.3253 / -20.2980 V
(L45c1's analisi_psu.csv, vp_max / vm_min).

Solo stdlib. /usr/bin/python3 -I controllo_l45c1.py
"""
import os

QUI = os.path.dirname(os.path.abspath(__file__))
LOTTO = os.path.dirname(QUI)
REPO = os.path.abspath(os.path.join(LOTTO, "..", "..", "..", "..", ".."))
VECCHIO = "/Users/roberto/EDA/.claude/worktrees/l45c1/"
SORG = os.path.join(REPO, "docs", "preamp", "data", "2026-10-13", "L45c1", "seq")

for caso in ("f_u501_cortoio_mus", "f_u502_cortoio_mus"):
    nome = "tb_psu_seq_%s_g1.cir" % caso
    with open(os.path.join(SORG, caso, nome)) as f:
        righe = f.read().split("\n")
    nuove = [r.replace(VECCHIO, REPO + "/") for r in righe]
    diverse = [i for i, (a, b) in enumerate(zip(righe, nuove)) if a != b]
    assert all(i == 0 or righe[i].startswith(".include ") for i in diverse), diverse
    assert len([i for i in diverse if i > 0]) == 5, diverse
    for i in diverse[1:]:
        assert os.path.isfile(nuove[i].split()[1]), nuove[i]
    dest = os.path.join(LOTTO, "controllo", "l45c1", caso)
    os.makedirs(dest, exist_ok=True)
    with open(os.path.join(dest, nome), "w") as f:
        f.write("\n".join(nuove))
    with open(os.path.join(dest, "punto_fisso.txt"), "w") as f:
        f.write("1\n")
    print("%s: %d righe cambiate" % (caso, len(diverse)))
