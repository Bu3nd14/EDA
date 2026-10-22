#!/usr/bin/env python3
"""L45d2b3b2b1: spice/preamp/tb/tb_mute_corto.cir (P7, ADR-021) per il blocco di ADR-099, ricavato dal
deck che prepara_regressione.py di L45d2b3b2a ha scritto per la variante rv2. Solo stdlib,
/usr/bin/python3 -I.

Uso: p7_deck.py        riscrive spice/preamp/tb/tb_mute_corto.cir e stampa le righe cambiate

Che cosa cambia rispetto al deck di main:
- la potenza di R123 e' i^2 * 33 (era * 56: R123 e' 33 ohm, ADR-099);
- la tabella tb_mute_corto_parti.csv: potenza media e massima di Q146, Q148, R123, R126 e delle parti
  nuove R190, R191, R192, Q193, R194, lette da @<dev>[p].
Le sigle del banco diventano quelle del sorgente: R161 -> R190, R162 -> R191, R167 -> R192,
Q168 -> Q193, R169 -> R194. RIFIUTA se il risultato include un blocco diverso da spice/preamp o nomina
ancora una sigla del banco.
"""
import os
import re
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(QUI, "..", "..", "..", "..", "..", ".."))
SRC = os.path.join(REPO, "docs", "preamp", "data", "2026-10-22", "L45d2b3b2a", "regressione",
                   "deck_rv2", "tb_mute_corto.cir")
DST = os.path.join(REPO, "spice", "preamp", "tb", "tb_mute_corto.cir")
MAPPA = {"r161": "r190", "r162": "r191", "r167": "r192", "q168": "q193", "r169": "r194"}

t = open(SRC).read()
t = t.replace("@REPO@/docs/preamp/data/2026-10-22/L45d2b3b2a/varianti/rv2/gain_block.subckt",
              "@REPO@/spice/preamp/gain_block.subckt")
for a, b in MAPPA.items():
    t = re.sub(r"\b%s\b" % a, b, t)
    t = re.sub(r"_%s\b" % a, "_" + b, t)
vecchio = "*   R123/R126 56 ohm di VAS e carico VAS (91 fino a ADR-054; le potenze col 56 da L60d2)"
nuovo = ("*   R123 33 ohm (ADR-099; 56 fino a L45d2b3b2b1, 91 fino a ADR-054) e R126 56 ohm, di VAS e\n"
         "*   carico VAS. tb_mute_corto_parti.csv (L45d2b3b2b1): Q146, Q148, R123, R126 e le parti di\n"
         "*   ADR-099 R190 R191 R192 Q193 R194, potenza media e massima da @<dev>[p]")
if t.count(vecchio) != 1:
    sys.exit("RIFIUTATO: la riga di commento di R123 non c'e' una volta sola")
t = t.replace(vecchio, nuovo)
if "L45d2b3b2a/varianti" in t or re.search(r"\b(r161|r162|r167|q168|r169)\b", t, re.I):
    sys.exit("RIFIUTATO: resta un riferimento al banco")
if t.count("@REPO@/spice/preamp/gain_block.subckt") != 1:
    sys.exit("RIFIUTATO: l'include del blocco non e' uno")
prima = open(DST).read().splitlines()
open(DST, "w").write(t)
dopo = t.splitlines()
print("tb_mute_corto.cir: %d -> %d righe" % (len(prima), len(dopo)))
