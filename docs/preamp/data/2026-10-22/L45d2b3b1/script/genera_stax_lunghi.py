#!/usr/bin/env python3
"""L45d2b3b1: i guasti piu' lunghi sulla Stax rifatti sul blocco DOPO ADR-097 (il «Da riaprire se» di
ADR-089: «R153 cambia valore»). Solo stdlib, /usr/bin/python3 -I.

Uso: genera_stax_lunghi.py [soglia_ms=100]   scrive deck/stax_lunghi/<caso>.cir, inc_stax/dopo097/,
                                             deck/lista_stax_lunghi.txt

I casi: ogni (posizione, modo, condensatore) di p10_stax.csv (il blocco prima di ADR-097) con la Stax
sopra 0,87 V per piu' della soglia, con le impostazioni della corsa buona di genera_L60d2.modi()
(gear, durata); in gear anche quelli che sul blocco di prima si sono fermati subito dopo il guasto e
sono stati rifatti in gear (p10_stax_gear.csv). Il blocco e' spice/preamp/ di oggi (R153 + R160); le
copie guaste in inc_stax/dopo097/ (genera_dopo097.py le rifiuta senza R160).
"""
import csv
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
sys.path.insert(0, QUI)
import genera_stax as gs   # noqa: E402

gc, g60 = gs.gc, gs.g60
SOGLIA = float(sys.argv[1]) if len(sys.argv) > 1 else 100.0


def main():
    righe = list(csv.DictReader(open(os.path.join(L, "p10_stax.csv"))))
    gear_rifatti = {r["modo"] for r in csv.DictReader(open(os.path.join(L, "p10_stax_gear.csv")))}
    scelti = sorted({(r["posizione"], r["modo"], r["k_C"]) for r in righe
                     if r["posizione"] in ("A", "F2") and float(r["stax_sopra_ms"]) > SOGLIA})
    impost = {(p, m): (g, tf) for p, m, g, tf in gs.modi([])}
    gs.imposta("oggi")
    g60.INC = os.path.join(L, "inc_stax", "dopo097")
    g60.INC_REL = "@REPO@/%s/" % os.path.relpath(g60.INC, gc.ROOT)
    g60.OGGI = gs.OGGI + ("R160",)
    if "R160" not in open(gs.SUBCKT["oggi"]).read():
        sys.exit("RIFIUTATO: spice/preamp/gain_block.subckt non e' il blocco di ADR-097")
    lista = []
    for pos, modo, k in scelti:
        gear, tf = impost[(pos, modo)]
        nome = "G0_%s_%s%s" % (pos, modo, "" if k == "1" else "_k105")
        gear = gear or nome in gear_rifatti
        t = gs.g1.applica(gc.deck_tr(pos, 0, modo, False, False, tfine=tf, gear=gear), "G0", float(k))
        lista.append(gs.scrivi_deck("stax_lunghi", nome, t, "oggi"))
    gc.scrivi(os.path.join(L, "deck", "lista_stax_lunghi.txt"), "\n".join(lista) + "\n")
    print("stax_lunghi: %d deck (sopra %g ms sul blocco di prima)" % (len(lista), SOGLIA))


if __name__ == "__main__":
    main()
