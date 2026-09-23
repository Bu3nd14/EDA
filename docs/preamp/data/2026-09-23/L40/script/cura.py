#!/usr/bin/env python3
"""L39: toglie da prima/ e dopo/ l'output grezzo rigenerabile, prima del commit.
docs/preamp/data/ e' versionato di proposito (.gitignore, AGENTS.md regola 8), ma
per i dati CURATI: le corse di V2 scrivono .dat da ~400 MB l'una (8,7 GB in tutto).

Si tolgono:
  - in ogni cartella di deck, le forme d'onda di wrdata: <nome>.txt e i gemelli
    <nome>.csv / <nome>.json che run_simulation.sh ne ricava. Resta la forma
    d'onda di tb_v3_overload (tb_v3_overload.csv), che v3.py rilegge;
  - in v2_1k_100k/, i .dat e i deck divisi corsa_*.cir (si rifanno con dividi.py
    da ldr.cir, che resta).
Restano: i log, le tabelle echo, i deck risolti, esiti, manifesti, analisi, tempi.
Uso: /usr/bin/python3 cura.py [--togli]      (senza: elenca e somma)
"""
import glob
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TIENI = {"tb_v3_overload.csv"}
via = []
for fase in ("prima", "dopo"):
    for d in sorted(glob.glob(os.path.join(BASE, fase, "*"))):
        if not os.path.isdir(d):
            continue
        if d.endswith("v2_1k_100k"):
            via += glob.glob(os.path.join(d, "*.dat")) + glob.glob(os.path.join(d, "corsa_*.cir"))
            continue
        for t in glob.glob(os.path.join(d, "*.txt")):
            radice = t[:-4]
            for f in (t, radice + ".csv", radice + ".json"):
                if os.path.exists(f) and os.path.basename(f) not in TIENI:
                    via.append(f)
        # <deck>.json e <deck>.csv: run_simulation.sh li ricava dal primo wrdata
        # (<deck>_wrdata.txt), quindi sono forme d'onda anche quando il .txt non
        # porta il loro nome. L'rc di ogni deck sta in <fase>/esiti.tsv. Una
        # <deck>.csv che e' una tabella echo resta: la conversione di
        # run_simulation.sh si riconosce dall'intestazione "col0,col1,...", non
        # dalla prima colonna numerica (tb_loop_blockA.csv e tb_loop_bufferfissa.csv
        # sono tabelle echo con la prima colonna numerica).
        deck = os.path.basename(d)
        j = os.path.join(d, deck + ".json")
        if os.path.exists(j):
            via.append(j)
        c = os.path.join(d, deck + ".csv")
        if os.path.exists(c) and os.path.basename(c) not in TIENI:
            with open(c) as fh:
                if fh.readline().startswith("col0,"):
                    via.append(c)
tot = sum(os.path.getsize(f) for f in via)
print("%d file, %.1f MB" % (len(via), tot / 1e6))
if "--togli" in sys.argv:
    for f in via:
        os.remove(f)
    print("tolti")
