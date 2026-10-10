#!/usr/bin/env python3
"""L51b: the second path. Every file of L51b-prima/ (today's scripts, the load
before: 265 / 265 / 42.4 mA) against the same file of the lots that ran with
that load: L47c2a (the six bench decks and the six sequences, the timer, the
counterfactual of the load) and L47c2b2 (the nine fault cases and the bridge; the
V2 deck, the runs and the table use today's audio board and are not compared here).

Equal means byte for byte after one normalisation only: an absolute path to
the repo (a worktree or the main checkout) becomes <R>/, and a path into a
lot's data folder becomes <LOTTO>/. Nothing else is forgiven.

    /usr/bin/python3 confronta_prima.py [--fase psu|seq|audio|tutto]

Writes ../confronto_prima.txt; exit 1 if any file differs or is missing.
"""
import os
import re
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
DATA = os.path.dirname(os.path.dirname(L))
PRIMA = os.path.join(DATA, "2026-10-09", "L51b-prima")
A = os.path.join(DATA, "2026-10-05", "L47c2a")
B = os.path.join(DATA, "2026-10-06", "L47c2b2")

_R = re.compile(r"/Users/roberto/EDA(?:/\.claude/worktrees/[^/\s]+)?/")
_LOT = re.compile(r"<R>/docs/preamp/data/\d{4}-\d{2}-\d{2}/[^/\s]+/")


def norm(b):
    try:
        s = b.decode()
    except UnicodeDecodeError:
        return b
    return _LOT.sub("<LOTTO>/", _R.sub("<R>/", s)).encode()


SEQ_A = ("accensione", "rilascio", "spegnimento", "buco20", "buco200")
SEQ_B = ("spegnimento_l", "perdita", "perdita_min", "guasto", "guasto_u501", "guasto_u503",
         "guasto_u503_min", "cf_nodelta", "corto_u503")


def coppie(fase):
    out = []
    if fase in ("psu", "tutto"):
        for d, f in (("timer", "tb_psu_timer_nom.cir"), ("timer", "tb_psu_timer_min.cir"),
                     ("timer", "analisi_timer.txt"),
                     ("rete", "tb_psu_rete.cir"), ("rete", "analisi.csv"),
                     ("guasti", "tb_psu_guasti.cir"), ("guasti", "analisi.csv"),
                     ("carico_l41a/rete", "tb_psu_rete_carico_l41a.cir"),
                     ("carico_l41a/rete", "analisi.csv"),
                     ("carico_l41a/guasti", "tb_psu_guasti_carico_l41a.cir"),
                     ("carico_l41a/guasti", "analisi.csv")):
            out.append((os.path.join(PRIMA, d, f), os.path.join(A, d, f)))
    if fase in ("seq", "tutto"):
        for casi, lot in ((SEQ_A, A), (SEQ_B, B)):
            for c in casi:
                src = os.path.join(lot, "seq", c)
                if not os.path.isdir(src):
                    out.append((os.path.join(PRIMA, "seq", c), src))
                    continue
                for f in sorted(os.listdir(src)):
                    if f.endswith((".cir", ".csv")) or f == "punto_fisso.txt":
                        out.append((os.path.join(PRIMA, "seq", c, f), os.path.join(src, f)))
    if fase in ("audio", "tutto"):
        # only the supply's half: the bridge. The V2 deck, the runs and the table are made
        # from TODAY's preamp_audio.net (L48a's selector, L48b's C_T), which L47c2b2 did not
        # have: they differ on purpose, and scomposizione.py sets them side by side
        for f in sorted(os.listdir(os.path.join(B, "ponte"))):
            if f.endswith(".json"):
                out.append((os.path.join(PRIMA, "ponte", f), os.path.join(B, "ponte", f)))
        out.append((os.path.join(PRIMA, "ponte", "estrai.txt"), os.path.join(B, "ponte", "estrai.txt")))
    return out


def main():
    fase = sys.argv[sys.argv.index("--fase") + 1] if "--fase" in sys.argv else "tutto"
    righe, diverse = [], 0
    for nuovo, vecchio in coppie(fase):
        if not os.path.isfile(vecchio):
            esito = "MANCA NEL LOTTO"
        elif not os.path.isfile(nuovo):
            esito = "MANCA OGGI"
        elif norm(open(nuovo, "rb").read()) == norm(open(vecchio, "rb").read()):
            esito = "uguale"
        else:
            esito = "DIVERSO"
        if esito != "uguale":
            diverse += 1
        righe.append("%-16s %s  <-  %s" % (esito, os.path.relpath(nuovo, DATA), os.path.relpath(vecchio, DATA)))
    tot = len(righe)
    righe.append("%d file su %d uguali (fase %s)" % (tot - diverse, tot, fase))
    open(os.path.join(L, "confronto_prima_%s.txt" % fase), "w").write("\n".join(righe) + "\n")
    print("\n".join(r for r in righe if not r.startswith("uguale")))
    return 1 if diverse else 0


if __name__ == "__main__":
    sys.exit(main())
