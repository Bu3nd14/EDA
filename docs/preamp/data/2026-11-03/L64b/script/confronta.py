#!/usr/bin/env python3
"""L64b: the second road of the sequences - every run of today against the rows of the lots it stands
for (mappa.csv), column by column.

  - L58b ran on the psu.py of today (no commit to psu.py after 6a8e626); its load differs from today's
    by the block of L66 (303,373 / 311,539 mA against 303,3288 / 311,5182): the decks must be the same
    but for those two numbers and the paths (deck_uguale), the rows the same at the printed figure or
    within one unit of it (TOLL).
  - L54b3b ran before Q509 (ADR-110) and before the test points (ADR-107, not in SPICE): its rows must
    be within TOLL_L54 (the 0,1 ms / 0,1 mV of L58b's own check of the new source against the variant,
    plus one unit of the figure); every difference is written.
The four f_q501_*_accs at mains -10 / +10 % of L58b have no row in a CSV (L58b analysed them by eye
from the log): their log's .meas are compared instead.

    /usr/bin/python3 -I script/confronta.py    # after psu/analizza_mc.py has written an_l64b.csv
writes confronto_seq.csv (one line per lot row and column that is not identical) and prints the summary.
Exit 1 if anything is beyond its tolerance or a deck differs beyond the load.
"""
import csv
import os
import re
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
DATA = os.path.dirname(os.path.dirname(L))
L58B = os.path.join(DATA, "2026-11-01", "L58b")
L54B3B = os.path.join(DATA, "2026-10-28", "L54b3b")


def rows(path):
    with open(path) as f:
        return list(csv.DictReader(f))


oggi = {r["caso"]: r for r in rows(os.path.join(L, "an_l64b.csv"))}
mappa = rows(os.path.join(L, "mappa.csv"))

# the rows of the lots, by their label/case
lotto = {}
for f in ("an_l58b.csv", "an_sorg.csv", "an_s1m.csv", "an_s1m_rete.csv"):
    for r in rows(os.path.join(L58B, f)):
        lotto.setdefault(("L58b", r["caso"]), r)
# L54b3b: the case name alone. The sequences (an_v_seq.csv) are in the order of lista_v25.txt (the
# same case at three mains); the FMEA (an_v_fmea.csv) in the order of its folder, names unique
v25 = [ln.split()[:2] for ln in open(os.path.join(L54B3B, "lista_v25.txt")) if ln.strip()]
vseq = [x for x in v25 if x[1] != "v_fmea_sorgente"]
vfm = [x for x in v25 if x[1] == "v_fmea_sorgente"]
r54 = rows(os.path.join(L54B3B, "an_v_seq.csv"))
if len(vseq) != len(r54) or any(a[0] != b["caso"] for a, b in zip(vseq, r54)):
    sys.exit("RIFIUTATO: le righe di an_v_seq.csv non sono nell'ordine di lista_v25.txt")
for (caso, etich), r in zip(vseq, r54):
    lotto[("L54b3b", "%s/%s" % (etich, caso))] = r
f54 = {r["caso"]: r for r in rows(os.path.join(L54B3B, "an_v_fmea.csv"))}
if sorted(f54) != sorted(c for c, _ in vfm):
    sys.exit("RIFIUTATO: an_v_fmea.csv non ha i casi di lista_v25.txt")
for caso, etich in vfm:
    lotto[("L54b3b", "%s/%s" % (etich, caso))] = f54[caso]


def toll(col, lot):
    """One unit of the printed figure (0,1 ms; 0,01 V; 0,1 mV; 1e-4 for the .meas), and for the runs
    on the source of before the pair (L54b3b, L58b «prima») L58b's 0,1 ms / 0,1 mV of the variant on
    top."""
    extra = 1.0 if lot in ("L54b3b", "prima") else 0.0
    if col.endswith("_ms"):
        return 0.1 + 0.1 * extra + 1e-9
    if col.endswith("_mv"):
        return 0.1 + 0.1 * extra + 1e-9
    # the latch's base, near its threshold: to the fourth decimal
    if col in ("bn_max0", "bn_max"):
        return 1e-4 + 1e-4 * extra + 1e-12
    # on_min, VRELAY_EN's minimum after TE (a logic level, ~4,45 V) read by .meas on the transient's
    # own points, takes two values with the step: the healthy buco20 gives 4,4533 at the nominal mains
    # and 4,4564 at -10 / +10 % (an_l64b.csv); 0,01 V as every other voltage (first run: 1e-4, two
    # cells out at 3,1 mV, written in the README)
    if col.startswith(("vplus", "raw", "v5", "x_", "on_min")):
        return 0.01 + 1e-9
    return 0.0          # flags and counts: identical


# L58b's psu/sorgente_uguale.py: the pair of the source of today against the pair of the variant
# (--q501serie 1e6:10000) after renaming; the pair of before is the single MQ501
COPPIA = ("MQ501", "MQ509", "RR586", "RR587", "RQ501G", "RQ509G")
MAPPA_COPPIA = {"q501_g": "g501a", "q501_mid": "n501m", "q509_g": "g501b", "RR586": "RQ501G",
                "RR587": "RQ509G", "1MEG": "1e+06", "10k": "10000"}
NODI_COPPIA = ("q501_g", "q501_mid", "q509_g", "RR586", "RR587")
CARICO = ("IPLUS", "IMINUS", "RLOADP", "RLOADM")


def modo_l58b(etich):
    """How an L58b run relates to the circuit of today: «stesso» (l58b_sorg, the new source),
    «variante» (l58b_s1m*, the source before + --q501serie 1e6:10000), «prima» (l58b, l58b_base*:
    the source before, the single Q501)."""
    if etich == "l58b_sorg":
        return "stesso"
    if etich.startswith("l58b_s1m"):
        return "variante"
    return "prima"


def decks_uguali(caso, etich_oggi, etich_l58b):
    """Today's deck against L58b's: the same lines but the load (the two currents of the audio board)
    and the paths; the pair compared as in sorgente_uguale.py (variante) or left out (prima)."""
    nome = "tb_psu_seq_%s_g1.cir" % caso
    a = os.path.join(L, "seq", etich_oggi, caso, nome)
    b = os.path.join(L58B, "seq", etich_l58b, caso, nome)
    if not (os.path.exists(a) and os.path.exists(b)):
        return "manca un deck"
    modo = modo_l58b(etich_l58b)
    pat = re.compile(r"/Users/\S*?/(?=(?:circuits|models|docs|spice)/)", re.I)
    lot = (os.path.join("2026-11-03", "L64b"), os.path.join("2026-11-01", "L58b"))

    def leggi(p, oggi):
        r = [pat.sub("", x) for x in open(p).read().splitlines()[1:]]
        if oggi:
            r = [x.replace(lot[0], lot[1]) for x in r]
        if oggi and modo == "variante":
            # the nodes and the resistors of the pair under the variant's names on EVERY line (the
            # faults of modi.py name them: BF_c q501_g ...), the values only on the pair's own lines
            r = [re.sub(r"\b(%s)\b" % "|".join(NODI_COPPIA), lambda m: MAPPA_COPPIA[m.group(1)], x)
                 for x in r]
        coppia = [x for x in r if x.split() and x.split()[0] in COPPIA]
        resto = [x for x in r if not (x.split() and x.split()[0] in COPPIA)]
        if oggi and modo == "variante":
            coppia = [" ".join(MAPPA_COPPIA.get(t, t) for t in x.split()) for x in coppia]
        return sorted(coppia), resto

    ca, la = leggi(a, True)
    cb, lb = leggi(b, False)
    if modo != "prima" and ca != cb:
        return "la coppia diversa: %s / %s" % (ca, cb)
    if len(la) != len(lb):
        return "%d righe contro %d" % (len(la), len(lb))
    for x, y in zip(la, lb):
        if x != y and not (x.split()[:1] == y.split()[:1] and x.split()[0] in CARICO
                           and x.split()[:3] == y.split()[:3]):
            return "riga diversa: %r / %r" % (x[:70], y[:70])
    return None


def meas_log(path):
    out = {}
    for ln in open(path, errors="replace"):
        m = re.match(r"^(\w+)\s+=\s+(\S+)", ln)
        if m:
            out[m.group(1)] = float(m.group(2))
    return out


righe, fuori, n_conf, n_uguali = [], [], 0, 0
deck_fuori = []
for m in mappa:
    mia = "%s/%s" % (m["oggi"], m["caso"])
    r = oggi.get(mia)
    if r is None:
        fuori.append((mia, "manca nella corsa di oggi"))
        continue
    key = (m["lotto"], "%s/%s" % (m["etichetta"], m["caso"]))
    tl = m["lotto"] if m["lotto"] == "L54b3b" else (
        "prima" if modo_l58b(m["etichetta"]) == "prima" else "L58b")
    if m["lotto"] == "L58b":
        d = decks_uguali(m["caso"], m["oggi"], m["etichetta"])
        if d:
            deck_fuori.append((key[1], d))
    if key not in lotto:
        # L58b's rows without a CSV row: the log's .meas
        lg = os.path.join(L58B, "seq", m["etichetta"], m["caso"], "tb_psu_seq_%s_g1.log" % m["caso"])
        lo = os.path.join(L, "seq", m["oggi"], m["caso"], "tb_psu_seq_%s_g1.log" % m["caso"])
        if m["lotto"] != "L58b" or not os.path.exists(lg):
            fuori.append((key[1], "nessuna riga e nessun log nel lotto"))
            continue
        a, b = meas_log(lo), meas_log(lg)
        if sorted(a) != sorted(b):
            fuori.append((key[1], "misure del log %s contro %s" % (sorted(a), sorted(b))))
        for k in sorted(set(a) & set(b)):
            n_conf += 1
            dv = abs(a[k] - b[k])
            if a[k] == b[k]:
                n_uguali += 1
                continue
            righe.append({"riga": key[1], "lotto": m["lotto"], "colonna": k + " (log)",
                          "oggi": a[k], "lotto_valore": b[k], "scarto": dv, "toll": toll(k, tl)})
            if dv > toll(k, tl):
                fuori.append((key[1], "%s: %g contro %g" % (k, a[k], b[k])))
        continue
    lr = lotto[key]
    for c in lr:
        if c in ("caso", "esito") or c not in r:
            continue
        n_conf += 1
        x, y = r[c], lr[c]
        if x == y:
            n_uguali += 1
            continue
        try:
            dv = abs(float(x) - float(y))
        except ValueError:
            dv = float("inf")
        t = toll(c, tl)
        righe.append({"riga": key[1], "lotto": m["lotto"], "colonna": c, "oggi": x,
                      "lotto_valore": y, "scarto": "" if dv == float("inf") else round(dv, 6),
                      "toll": t})
        if dv > t:
            fuori.append((key[1], "%s: oggi %r, %s %r" % (c, x, m["lotto"], y)))

with open(os.path.join(L, "confronto_seq.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["riga", "lotto", "colonna", "oggi", "lotto_valore", "scarto", "toll"])
    w.writeheader()
    w.writerows(righe)
print("%d righe dei lotti, %d celle confrontate: %d identiche, %d entro la tolleranza, %d fuori"
      % (len(mappa), n_conf, n_uguali, n_conf - n_uguali - len([x for x in fuori if ":" in x[1]]),
         len(fuori)))
print("deck di oggi contro L58b: %d righe di L58b, %d diversi oltre il carico"
      % (sum(m["lotto"] == "L58b" for m in mappa), len(deck_fuori)))
for x in deck_fuori + fuori:
    print("  FUORI", *x)
sys.exit(1 if fuori or deck_fuori else 0)
