#!/usr/bin/env python3
"""L45b: la lista unica delle corse di L45a a vuoto, deck/lista_giro2.txt.

Dalle famiglie complete (tr_A, tr_F1, tr_F2, tr_B, tr_B_g10) si tolgono i modi che in L45a si
erano bloccati (30 min senza finire) o interrotti: corrono nelle loro varianti accorciate o col
metodo gear (vuoto_tr_corta_*, vuoto_tr_gear_*, vuoto_tr_r120_B), come in L45a. Poi le corse del
rivelatore ideale (vuoto_tr_taglio*).
"""
import os

QUI = os.path.dirname(os.path.abspath(__file__))
DECK = os.path.join(os.path.dirname(QUI), "deck")

ESCLUSI = {
    "tr_A": {"Q133_ae", "R120_cc", "R135_ap", "C124_cc", "R109_ap", "R131_ap"},
    "tr_F1": {"R120_cc"},
    "tr_F2": {"R120_cc", "Q146_ce"},
    "tr_B": {"R120_cc"},
    "tr_B_g10": {"R120_cc"},
}
ALTRE = ["tr_corta_A", "tr_corta_B", "tr_corta_B_g10", "tr_corta_F1", "tr_corta_F2", "tr_gear_A",
         "tr_gear_F2", "tr_r120_B", "tr_taglio0p1_B", "tr_taglio1_B", "tr_taglio3_B", "tr_taglio10_B",
         "tr_taglio3_A"]

righe = []
# prima le corse lunghe (le accorciate durano minuti), poi le famiglie
for fam in ALTRE:
    righe += open(os.path.join(DECK, "lista_vuoto_%s.txt" % fam)).read().split()
for fam, via in ESCLUSI.items():
    for p in open(os.path.join(DECK, "lista_vuoto_%s.txt" % fam)).read().split():
        if os.path.basename(p)[:-4] not in via:
            righe.append(p)
with open(os.path.join(DECK, "lista_giro2.txt"), "w") as f:
    f.write("\n".join(righe) + "\n")
print("giro2: %d deck" % len(righe))
