#!/usr/bin/env python3
"""L56: da dove viene il secondo ordine delle varianti che tolgono il gradino.

A 27 gradi uniformi, il controllo ha l'intermodulazione CCIF a -130,8 / -130,7 / -125,6 dB (0 / +3
/ +10 dB) col terzo ordine alto (-104,7 dB a 2 V); ogni variante che da' tensione allo specchio
(inseguitore, R123 piu' grande, diodo) sta a ~-116 / -112 / -105 dB col secondo ordine dominante e
il terzo basso. Ipotesi da provare: la quasi-saturazione di Q121B nel controllo compensa per caso un
secondo ordine che sta altrove; e l'effetto Early dello specchio (VAF 37 V nel modello, specchio a
Vce diverse sui due lati quando l'uscita ha piu' tensione) come sorgente di quel secondo ordine.

COPIE DI PROVA del modello, NON modelli (non vanno in models/):
  rc0    L53/temp/inc/ls350_rc0.lib (RC 231 -> 0,001)
  vaf1k  inc/prove/ls350_vaf1k.lib  (VAF 37,3 -> 1000; tutto il resto come il costruttore)
Il deck di partenza e' deck/<spec>/imd_u27.cir (caldo.py), col solo include dell'LS350 cambiato.

Uso: /usr/bin/python3 prove.py <spec>...  -> deck/prove/imd_<spec>_<copia>.cir, deck/lista_prove.txt
"""
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
LOTTO = os.path.dirname(QUI)
VERO = ".include @REPO@/models/bjt_pnp/ls350.lib"
COPIE = {"rc0": ".include @REPO@/docs/preamp/data/2026-10-12/L53/temp/inc/ls350_rc0.lib",
         "vaf1k": ".include @REPO@/docs/preamp/data/2026-10-12/L56/inc/prove/ls350_vaf1k.lib"}

src = open(os.path.join(os.path.dirname(QUI), "..", "..", "..", "..", "..", "models", "bjt_pnp",
                        "ls350.lib")).read()
# VAF compare due volte: nella riga del costruttore citata nel commento e nella .model; si cambia
# solo la .model (l'ultima)
testa, sep, coda = src.rpartition(".model LS350")
if not sep or coda.count("VAF=37.2934") != 1:
    sys.exit("VAF del costruttore non trovata una volta sola nella .model")
open(os.path.join(LOTTO, "inc", "prove", "ls350_vaf1k.lib"), "w").write(
    "* L56 COPIA DI PROVA, NON UN MODELLO: models/bjt_pnp/ls350.lib con VAF 37.2934 -> 1000\n"
    + testa + sep + coda.replace("VAF=37.2934", "VAF=1000"))

lista = []
for spec in sys.argv[1:]:
    t = open(os.path.join(LOTTO, "deck", spec, "imd_u27.cir")).read()
    if t.count(VERO) != 1:
        sys.exit("%s: include dell'LS350 trovato %d volte" % (spec, t.count(VERO)))
    for c, riga in COPIE.items():
        s = t.replace(VERO, riga)
        s = "imd - L56 prova %s, %s: " % (c, spec) + s.split("\n", 1)[0] + "\n" + s.split("\n", 1)[1]
        p = os.path.join(LOTTO, "deck", "prove", "imd_%s_%s.cir" % (spec, c))
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w").write(s)
        lista.append(p)
open(os.path.join(LOTTO, "deck", "lista_prove.txt"), "w").write("\n".join(lista) + "\n")
print("%d deck" % len(lista))
