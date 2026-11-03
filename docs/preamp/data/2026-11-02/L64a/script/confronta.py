#!/usr/bin/env python3
"""L64a: la ricorsa di oggi (L64a/dopo) contro la seconda strada.

    /usr/bin/python3 -I confronta.py

1. I 21 deck veloci contro la regressione di L66 sulla variante lim365, che e' il sorgente di
   oggi (ADR-111 l'ha portata in gain_block.py; L67 non ha cambiato il circuito). L66 non ha
   versionato le corse grezze, ma le MISURE: regressione/misure_lim365.csv, colonna lim365, le
   righe `nome = valore` dei .log lette da misure() di L45d2b3b1/script/misure_regressione.py
   e stampate a 6 cifre. Qui la stessa misure() sui log di oggi, alla stessa cifra.
   Prima: i deck di L66 (regressione/deck_lim365/) uguali a quelli di oggi a meno del percorso
   del blocco della variante, dei commenti e delle righe `save` in piu'; il blocco della
   variante (varianti/lim365/) uguale a spice/preamp/gain_block_flat.inc e gain_block.subckt di
   oggi a meno dei commenti.
2. Il selettore contro dopo-L57b/regressione/dopo/tb_f1_selettore (l'ultima corsa, col modello
   del BAV199 di oggi); dopo, il blocco e' cambiato (L58a1, L66): ogni scarto si scrive.
3. Le copie col bilanciamento contro L48b/{e5,v1}_bilanciamento/out (il circuito di L48b, prima
   del limitatore d'ingresso e dei cambi del blocco): ogni scarto si scrive.
Scrive ../confronto.txt e ../misure_confronto.csv.
"""
import csv
import os
import re
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
DATA = os.path.dirname(os.path.dirname(L))
REPO = os.path.abspath(os.path.join(DATA, "..", "..", ".."))
DOPO = os.path.join(L, "dopo")
L66 = os.path.join(DATA, "2026-11-02", "L66")
sys.path.insert(0, os.path.join(DATA, "2026-10-22", "L45d2b3b1", "script"))
import misure_regressione as mr   # noqa: E402

TB = os.path.join(REPO, "spice", "preamp", "tb")
VAR = "@REPO@/docs/preamp/data/2026-11-02/L66/varianti/lim365/"
out, problemi = [], []


def senza_commenti(path, swap=None):
    righe = []
    for l in open(path, encoding="utf-8", errors="replace"):
        s = l.rstrip("\n")
        if swap:
            s = s.replace(swap, "@REPO@/spice/preamp/")
        if s.lstrip().startswith("*") or not s.strip():
            continue
        righe.append(re.sub(r"\s+;.*$", "", s))
    return righe


# 1a. i deck
decks = sorted(os.listdir(os.path.join(L66, "regressione", "deck_lim365")))
for d in decks:
    a = senza_commenti(os.path.join(TB, d))
    b = senza_commenti(os.path.join(L66, "regressione", "deck_lim365", d), swap=VAR)
    extra = [x for x in b if x not in a]
    manca = [x for x in a if x not in b]
    if d == "tb_mute_corto.cir" and not manca:
        # L66 ha aggiunto a questo deck save, .meas e un echo su tb_mute_corto_parti.csv con
        # gli stessi nomi di misura: la seconda strada di questo deck e' confronta_mute.py
        out.append(f"deck {d}: le righe di oggi tutte nel deck di L66, che ne ha {len(extra)} in "
                   f"piu' (save, .meas ed echo delle potenze); confronto in confronta_mute.py")
    elif manca or any(not x.startswith("save ") for x in extra):
        problemi.append(f"DECK {d}: diverso da quello di L66 oltre i save ({len(manca)} righe "
                        f"solo oggi, {len(extra)} solo in L66)")
    elif extra:
        out.append(f"deck {d}: uguale a L66 a meno di {len(extra)} righe save in piu' in L66")
for f in ("gain_block_flat.inc", "gain_block.subckt"):
    a = senza_commenti(os.path.join(REPO, "spice", "preamp", f))
    b = senza_commenti(os.path.join(L66, "varianti", "lim365", f))
    if a != b:
        problemi.append(f"BLOCCO {f}: la variante lim365 di L66 non e' quello di oggi")
    else:
        out.append(f"blocco {f}: la variante lim365 di L66 uguale a quello di oggi "
                   f"({len(a)} righe, a meno dei commenti)")

# 1b. le misure
ref = {}
with open(os.path.join(L66, "regressione", "misure_lim365.csv")) as f:
    for r in csv.DictReader(f):
        ref[(r["deck"], r["misura"])] = r["lim365"]
righe, n_ug, n_tot, n_solo66, n_solooggi, peggio = [], 0, 0, 0, 0, []
deck_names = sorted({k[0] for k in ref})
for deck in deck_names:
    if deck == "tb_mute_corto":       # misure() chiave per occorrenza: confronta_mute.py
        continue
    log = os.path.join(DOPO, deck, deck + ".log")
    oggi = mr.misure(log) if os.path.isfile(log) else {}
    chiavi = {k[1] for k in ref if k[0] == deck}
    for k in sorted(chiavi | set(oggi)):
        r66 = ref.get((deck, k), "")
        o = "%.6g" % oggi[k] if k in oggi else ""
        if r66 == "" and o == "":
            continue
        if r66 == "":
            n_solooggi += 1
            righe.append([deck, k, o, "", "solo oggi"])
            continue
        if o == "":
            n_solo66 += 1
            righe.append([deck, k, "", r66, "solo L66"])
            continue
        n_tot += 1
        if o == r66:
            n_ug += 1
            continue
        x, y = float(r66), float(o)
        rel = abs(y - x) / max(abs(x), abs(y), 1e-30)
        peggio.append((rel, deck, k, r66, o))
        righe.append([deck, k, o, r66, "%.3e" % rel])
with open(os.path.join(L, "misure_confronto.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["deck", "misura", "oggi", "L66_lim365", "relativa"])
    w.writerows(righe)
out.append(f"misure dei 20 deck (tutti tranne tb_mute_corto): {n_ug} su {n_tot} uguali a 6 cifre alla corsa di L66 (lim365); "
           f"{n_solo66} solo in L66, {n_solooggi} solo oggi")
for rel, deck, k, a, b in sorted(peggio, reverse=True)[:15]:
    out.append(f"   diversa {deck} {k}: L66 {a} oggi {b} (relativa {rel:.3e})")


# 2-3. CSV per CSV
def csv_contro(oggi, prima, etichetta):
    n, ug, note = 0, 0, []
    for f in sorted(os.listdir(prima)):
        if not f.endswith(".csv"):
            continue
        n += 1
        g = os.path.join(oggi, f)
        if not os.path.isfile(g):
            note.append(f"   MANCA {f}")
            continue
        pa, pb = os.path.join(prima, f), g
        if open(pa, "rb").read() == open(pb, "rb").read():
            ug += 1
            continue
        a, b = list(csv.reader(open(pa))), list(csv.reader(open(pb)))
        if len(a) != len(b) or a[0] != b[0]:
            note.append(f"   FORMA {f}: righe {len(a)} -> {len(b)}")
            continue
        diff = {}
        for ra, rb in zip(a[1:], b[1:]):
            for h, x, y in zip(a[0], ra, rb):
                if x != y:
                    try:
                        dd = abs(float(y) - float(x)) / max(abs(float(x)), 1e-30)
                    except ValueError:
                        dd = float("inf")
                    diff[h] = max(diff.get(h, 0), dd)
        note.append(f"   CAMBIA {f}: " + ", ".join(f"{h} {d:.3g}" for h, d in sorted(diff.items())))
    out.append(f"{etichetta}: {ug} file su {n} uguali byte per byte")
    out.extend(note)


csv_contro(os.path.join(DOPO, "tb_f1_selettore"),
           os.path.join(DATA, "2026-10-25", "dopo-L57b", "regressione", "dopo", "tb_f1_selettore"),
           "selettore contro dopo-L57b")
L48B = os.path.join(DATA, "2026-10-07", "L48b")
csv_contro(os.path.join(DOPO, "bilanciamento", "tb_e5_bilanciamento"),
           os.path.join(L48B, "e5_bilanciamento", "out"), "E5 col bilanciamento contro L48b")
csv_contro(os.path.join(DOPO, "bilanciamento", "tb_loop_bilanciamento"),
           os.path.join(L48B, "v1_bilanciamento", "out"), "V1 col bilanciamento contro L48b")

# 4. la seconda strada di oggi per i tre deck senza corsa precedente sul circuito di oggi:
#    gli stessi deck col blocco della variante lim365 di L66 (genera_seconda.py, seconda.sh)
SEC = os.path.join(L, "seconda")
csv_contro(os.path.join(DOPO, "tb_f1_selettore"), os.path.join(SEC, "tb_f1_selettore"),
           "selettore contro lo stesso deck col blocco di L66")
csv_contro(os.path.join(DOPO, "bilanciamento", "tb_e5_bilanciamento"),
           os.path.join(SEC, "tb_e5_bilanciamento"), "E5 col bilanciamento contro il blocco di L66")
csv_contro(os.path.join(DOPO, "bilanciamento", "tb_loop_bilanciamento"),
           os.path.join(SEC, "tb_loop_bilanciamento"), "V1 col bilanciamento contro il blocco di L66")

esiti = [e for e in open(os.path.join(DOPO, "esiti.tsv")).read().split("\n") if e]
rc = [e for e in esiti if e.split("\t")[1] != "0"]
out.append(f"{len(esiti)} deck corsi; deck con rc != 0: {rc or 'nessuno'}")
if problemi:
    out = ["PROBLEMI:"] + ["  " + p for p in problemi] + [""] + out
open(os.path.join(L, "confronto.txt"), "w").write("\n".join(out) + "\n")
print("\n".join(out))
