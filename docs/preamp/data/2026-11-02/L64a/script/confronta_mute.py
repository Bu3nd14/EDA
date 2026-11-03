#!/usr/bin/env python3
"""L64a: tb_mute_corto, la seconda strada che le misure per occorrenza non danno.

    /bin/zsh seconda.sh          (ricorre il deck di L66 in <L>/l66_mute)
    /usr/bin/python3 -I confronta_mute.py

Il deck di L66 (lim365) misura in piu', dentro il ciclo, potenze di Q146, Q148, R123 e R126 con
gli STESSI nomi delle .meas che il deck di oggi ha gia': misure() chiave per occorrenza
(nome#k), quindi accoppia misure diverse. Qui:
  1. il deck di L66 ricorso oggi ridà le sue misure di misure_lim365.csv (colonna lim365), tutte,
     a 6 cifre: la ricorsa e' la corsa di L66;
  2. ogni CSV che il deck di oggi scrive, byte per byte contro quello della ricorsa del deck di L66
     (tb_mute_corto_parti.csv lo scrive solo il deck di L66).
Accoda il risultato a ../confronto.txt.
"""
import csv
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
DATA = os.path.dirname(os.path.dirname(L))
sys.path.insert(0, os.path.join(DATA, "2026-10-22", "L45d2b3b1", "script"))
import misure_regressione as mr   # noqa: E402

R66 = os.path.join(L, "l66_mute")
OGGI = os.path.join(L, "dopo", "tb_mute_corto")
out = []
m = mr.misure(os.path.join(R66, "tb_mute_corto.log"))
ref = {}
with open(os.path.join(DATA, "2026-11-02", "L66", "regressione", "misure_lim365.csv")) as f:
    for r in csv.DictReader(f):
        if r["deck"] == "tb_mute_corto" and r["lim365"] != "":
            ref[r["misura"]] = r["lim365"]
ug = sum(1 for k, v in ref.items() if k in m and "%.6g" % m[k] == v)
out.append(f"tb_mute_corto, il deck di L66 ricorso oggi: {ug} misure su {len(ref)} di "
           f"misure_lim365.csv uguali a 6 cifre; misure nella ricorsa {len(m)}")
n, uguali, note = 0, 0, []
for f in sorted(os.listdir(OGGI)):
    if not f.endswith(".csv"):
        continue
    n += 1
    g = os.path.join(R66, f)
    if not os.path.isfile(g):
        note.append(f"   MANCA nella ricorsa di L66: {f}")
    elif open(g, "rb").read() == open(os.path.join(OGGI, f), "rb").read():
        uguali += 1
    elif f == "tb_mute_corto_parti.csv":
        # il deck di L66 riscrive l'intestazione con 14 colonne e, per ogni caso, accoda alla
        # riga di oggi (24 colonne) una seconda riga con le stesse prime 14 misure: le righe a
        # 24 colonne, nell'ordine, devono essere quelle di oggi
        a = open(os.path.join(OGGI, f)).read().split("\n")
        b = [r for r in open(g).read().split("\n") if r.count(",") == 23]
        dup = [r for r in open(g).read().split("\n")[1:] if r and r.count(",") == 13]
        if a[1:-1] == b and len(dup) == len(b):
            uguali += 1
            note.append(f"   {f}: le {len(b)} righe di oggi uguali, nell'ordine, alle righe a 24 "
                        f"colonne della ricorsa di L66 (che ne accoda {len(dup)} a 14 colonne)")
        else:
            note.append(f"   DIVERSO {f}")
    else:
        note.append(f"   DIVERSO {f}")
out.append(f"tb_mute_corto, i CSV di oggi contro la ricorsa del deck di L66: {uguali} su {n} "
           f"uguali (byte per byte, tb_mute_corto_parti.csv riga per riga)")
out += note
with open(os.path.join(L, "confronto.txt"), "a") as f:
    f.write("\n".join(out) + "\n")
print("\n".join(out))
