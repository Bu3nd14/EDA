#!/usr/bin/env python3
"""L55, diagnosi: i deck a caldo del candidato (MJE243 / MJE253) falliscono la `tran` al punto
iniziale («Timestep too small; initial timepoint: trouble with lsk489a-instance jq110a»), mentre
gli stessi deck del MJE no, e lo stesso candidato a 27 C uniformi (genera.py) passa.

Scrive in ../prova/ due copie di deck/mje24x--sot223--diss/thd20k_t27_rame.cir col suo include:
  senza_temp  la stessa, ma Q132 / Q133 senza `temp=` (alla temperatura del deck)
  gear        la stessa, con `option method=gear` nel blocco .control
e la lista prova/lista.txt per esegui.sh. Solo stdlib, /usr/bin/python3 -I.
"""
import os
import re

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
NOME = "mje24x--sot223--diss"
DECK = os.path.join(L, "deck", NOME, "thd20k_t27_rame.cir")
INC = os.path.join(L, "inc", NOME + "__t27_rame.inc")
REL_INC = "docs/preamp/data/2026-10-29/L55/inc/%s__t27_rame.inc" % NOME

deck = open(DECK).read()
inc = open(INC).read()
lista = []

# senza_temp: l'include copiato senza temp= su Q132 / Q133
inc2 = re.sub(r"^(Q13[23] .*?) temp=\S+$", r"\1", inc, flags=re.M)
if inc2.count("temp=") != inc.count("temp=") - 2:
    raise SystemExit("senza_temp: temp= tolto da %d righe" % (inc.count("temp=") - inc2.count("temp=")))
p_inc = os.path.join(L, "inc", "prova_senza_temp.inc")
open(p_inc, "w").write(inc2)
d = os.path.join(L, "deck", "prova")
os.makedirs(d, exist_ok=True)
t = deck.replace(REL_INC, "docs/preamp/data/2026-10-29/L55/inc/prova_senza_temp.inc")
if t == deck:
    raise SystemExit("senza_temp: include non trovato")
p = os.path.join(d, "senza_temp.cir")
open(p, "w").write(t)
lista.append(p)

# gear: il deck con method=gear
t = deck.replace("option itl1=1000", "option itl1=1000\noption method=gear", 1)
if t == deck:
    raise SystemExit("gear: option itl1 non trovata")
p = os.path.join(d, "gear.cir")
open(p, "w").write(t)
lista.append(p)

# dtemp: Q132 / Q133 con dtemp = Tj - Ta (aria 27 qui) al posto di temp=. Esito delle due prove
# sopra: senza_temp passa, gear fallisce come il deck: e' il temp= di istanza sul modello onsemi
inc3 = re.sub(r"^(Q13[23] .*?) temp=(\S+)$", lambda m: "%s dtemp=%.1f" % (m.group(1), float(m.group(2)) - 27),
              inc, flags=re.M)
p_inc = os.path.join(L, "inc", "prova_dtemp.inc")
open(p_inc, "w").write(inc3)
t = deck.replace(REL_INC, "docs/preamp/data/2026-10-29/L55/inc/prova_dtemp.inc")
p = os.path.join(d, "dtemp.cir")
open(p, "w").write(t)
lista.append(p)

open(os.path.join(L, "deck", "lista_prova.txt"), "w").write("\n".join(lista) + "\n")
print("\n".join(lista))
