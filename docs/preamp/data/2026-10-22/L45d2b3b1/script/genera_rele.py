#!/usr/bin/env python3
"""L45d2b3b1: le scelte 6, 8, 9 e 10 di L60a rifatte sul blocco di oggi. Solo stdlib, /usr/bin/python3 -I.

Uso: genera_rele.py    scrive deck/rele_<gruppo>/<caso>.cir e deck/lista_rele.txt

IL BANCO e' quello di L60a (genera_L60a.py, importato): il canale di L45a con 1 uF sulla fissa 2
prima del contatto del mute (la geometria che ADR-084 ha tenuto), il carico della Stax, i rail
ideali, i guasti dei controlli di L45b (l'isolamento bobina-contatti a 10 ohm / 1 kohm). Le corse
dei relè includono il blocco di spice/preamp/, cioe' quello di oggi. Le corse col blocco guasto
(scelte 1, 9, 10) includevano la copia di L45a (limitations #62): qui la includono riscritta dal
blocco di oggi, con reindirizza() di L60d2, e si rifiutano senza R150..R153 e D154..D159.
I file della corsa prendono il nome del deck, come in L60a.
"""
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
DATA = os.path.abspath(os.path.join(L, "..", ".."))
sys.path.insert(0, os.path.join(DATA, "2026-10-15", "L60a", "script"))
sys.path.insert(0, os.path.join(DATA, "2026-10-19", "L60d2", "script"))
import genera_L60a as ga     # noqa: E402
import genera_L60d2 as g60   # noqa: E402

gc = ga.gc
g60.INC = os.path.join(L, "inc_stax", "oggi")
g60.INC_REL = "@REPO@/%s/" % os.path.relpath(g60.INC, gc.ROOT)
g60.OGGI = ("R150", "R151", "R152", "R153", "D154", "D155", "D156", "D157", "D158", "D159")


def rinomina(testo, nome):
    righe = testo.split("\n")
    for i, r in enumerate(righe):
        if r.startswith("wrdata ") or (r.startswith("echo ") and "_fine.csv" in r):
            parti = r.split(" ")
            for k, p in enumerate(parti):
                if p.endswith(".dat"):
                    parti[k] = nome + ".dat"
                elif p.endswith("_fine.csv"):
                    parti[k] = nome + "_fine.csv"
            righe[i] = " ".join(parti)
    return "\n".join(righe)


def main():
    gc.SUBCKT = os.path.join(gc.ROOT, "spice", "preamp", "gain_block.subckt")
    lista = []
    for gruppo, nome, testo in ga.casi():
        testo = g60.reindirizza(rinomina(testo, nome), nome)
        if "L45a/inc" in testo:
            sys.exit("RIFIUTATO: %s include ancora una copia di L45a" % nome)
        p = os.path.join(L, "deck", "rele_" + gruppo, nome + ".cir")
        gc.scrivi(p, "L45d2b3b1 %s %s - " % (gruppo, nome) + testo)
        lista.append(p)
    gc.scrivi(os.path.join(L, "deck", "lista_rele.txt"), "\n".join(lista) + "\n")
    print("rele: %d deck" % len(lista))


if __name__ == "__main__":
    main()
