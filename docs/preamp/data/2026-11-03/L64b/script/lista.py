#!/usr/bin/env python3
"""L64b: the power supply's sequences on the circuit of today, one list.

The cases are those of the last lots on the timer of today:
  - L54b3b lista_v25.txt: the 24 sequences of the source (as the 15 of the firmware were) and the
    7 lines of its FMEA (ADR-105);
  - L58b lista_l58b.txt (the standby, Q503: ADR-110), lista_sorg.txt (the 8 events on the new
    source), lista_rete.txt (accensione at mains -10 / +10 %);
  - L58b lista_s1m.txt, lista_s1m2.txt: the pair Q501 + Q509 of today (1 MOhm / 10 kOhm, ADR-110)
    and its single faults, at every event and at mains -10 / +10 %. L58b ran them on the source of
    before with --q501serie 1e6:10000; the source of today has the pair (L58b's
    psu/sorgente_uguale.py: the same deck but the title), so here they run WITHOUT --q501serie.
OUT: the lines of lista_l58b.txt / lista_rete.txt on Q501 (f_q501_corto_*, f_q501_gd_*). They are
the faults of the single Q501 of before the pair: on today's deck «corto» shorts MUTE_CMD to RLY_RET,
the whole pair (two faults), and «gd» joins MUTE_G to MUTE_CMD, the gate and drain of no transistor
of today. Today's single faults of the pair are those of lista_s1m.
Every line runs with the options of L58b (the comparator calibrated, the latch and the BAT54 of the
manufacturer, --sonde-piu). The same case with the same options runs ONCE: the label of the run is
`oggi` + the mains suffix; mappa.csv says which line of which lot each run stands for (the second
road compares against those rows).

    /usr/bin/python3 -I script/lista.py
writes lista_l64b.txt (every run), mappa.csv, and lista_l64b_mancanti.txt (the runs without their
seq/<etichetta>/<caso>/ok.txt yet).
"""
import csv
import os
import re

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
DATA = os.path.dirname(os.path.dirname(L))
L58 = os.path.join(DATA, "2026-11-01", "L58b")
SORGENTI = (("L54b3b", os.path.join(DATA, "2026-10-28", "L54b3b", "lista_v25.txt")),
            ("L58b", os.path.join(L58, "lista_l58b.txt")),
            ("L58b", os.path.join(L58, "lista_sorg.txt")),
            ("L58b", os.path.join(L58, "lista_rete.txt")),
            ("L58b", os.path.join(L58, "lista_s1m.txt")),
            ("L58b", os.path.join(L58, "lista_s1m2.txt")))
BASE = ["--n2n7002", "ds", "--tss", "3.0", "--comparatore", "tarato", "--ritenuta", "costruttore",
        "--bat54", "costruttore", "--sonde-piu"]
FUORI = re.compile(r"^f_q501_(corto|gd)_")


def opzioni(resto):
    """The options of a line minus those of BASE: only --rete may differ, and --q501serie 1e6:10000
    (the pair of today) is dropped."""
    o, rete = list(resto), None
    if "--rete" in o:
        i = o.index("--rete")
        rete = o[i + 1]
        del o[i:i + 2]
    if "--q501serie" in o:
        i = o.index("--q501serie")
        if o[i + 1] != "1e6:10000":
            raise SystemExit(f"RIFIUTATO: --q501serie {o[i + 1]}, la coppia di oggi e' 1e6:10000")
        del o[i:i + 2]
    if "--sonde-piu" not in o:
        o.append("--sonde-piu")
    if o != BASE:
        raise SystemExit(f"RIFIUTATO: opzioni diverse da quelle di L58b: {o}")
    return rete


righe, mappa, viste, tolte = [], [], {}, []
for lotto, path in SORGENTI:
    for ln in open(path):
        x = ln.split()
        if not x:
            continue
        caso, etich, timer = x[:3]
        if timer != "sorgente":
            raise SystemExit(f"RIFIUTATO: {path}: timer {timer}")
        if FUORI.match(caso):
            tolte.append(f"{etich}/{caso}")
            continue
        rete = opzioni(x[3:])
        suff = {None: "", "0.9": "_m10", "1.1": "_p10"}[rete]
        # an etichetta that says the mains in its name (v_sorgente_m10, l58b_s1m_p10) must agree
        m = re.search(r"_(m10|p10)$", etich)
        if (m and "_" + m.group(1) != suff) or (not m and suff and lotto == "L54b3b"):
            raise SystemExit(f"RIFIUTATO: {etich} con --rete {rete}")
        mia = "oggi" + suff
        k = (caso, mia)
        if k not in viste:
            viste[k] = True
            righe.append(" ".join([caso, mia, "sorgente"] + BASE + (["--rete", rete] if rete else [])))
        mappa.append({"caso": caso, "oggi": mia, "lotto": lotto, "etichetta": etich})

with open(os.path.join(L, "lista_l64b.txt"), "w") as f:
    f.write("\n".join(righe) + "\n")
mancanti = [r for r in righe if not os.path.exists(os.path.join(L, "seq", r.split()[1], r.split()[0], "ok.txt"))]
with open(os.path.join(L, "lista_l64b_mancanti.txt"), "w") as f:
    f.write("".join(r + "\n" for r in mancanti))
with open(os.path.join(L, "mappa.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["caso", "oggi", "lotto", "etichetta"])
    w.writeheader()
    w.writerows(mappa)
print(f"{len(righe)} corse per {len(mappa)} righe dei lotti; {len(mancanti)} da correre; "
      f"{len(tolte)} righe di Q501 di prima della coppia fuori")
