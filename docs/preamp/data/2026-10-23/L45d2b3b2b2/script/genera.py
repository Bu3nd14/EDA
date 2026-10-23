#!/usr/bin/env python3
"""L45d2b3b2b2 (NC-042, ADR-099): il calore dei quindici guasti e dei modi delle parti nuove sul blocco
del SORGENTE (spice/preamp/, generato da circuits/preamp/gain_block.py con ADR-099). Solo stdlib,
/usr/bin/python3 -I.

Uso: genera.py sorg     -> varianti/sorg/, inc/sorg/, deck/sorg_<pos>/*.cir, deck/lista_sorg.txt

Il banco e' quello di L45d2b3b2a (genera.py importato come g2a, e attraverso lui genera_calore.py di
L45d2b3b1, L62b e il canale di L45a), coi percorsi puntati a QUESTA cartella. La variante «sorg» (senza
«_»: analizza_calore.py divide la cartella al primo) e' il blocco di spice/preamp/ byte per byte, senza
cambi testuali: e' cio' che rv2 era sul banco, con le sigle del sorgente (limitations #22):

    banco rv2   R161  R162  R167  Q168  R169
    sorgente    R190  R191  R192  Q193  R194

Le copie guaste si riscrivono dal subckt del sorgente (limitations #62) e si rifiutano senza R150..R153,
R160 e le cinque parti nuove.
"""
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
DATA = os.path.abspath(os.path.join(L, "..", ".."))
sys.path.insert(0, os.path.join(DATA, "2026-10-22", "L45d2b3b2a", "script"))
import genera as g2a   # noqa: E402

g62, gc, gk = g2a.g62, g2a.gc, g2a.gk
g2a.L = L
g62.L62A = L
g62.REL = os.path.relpath(L, g62.ROOT)
SP = g2a.SP
NUOVE = ("R190", "R191", "R192", "Q193", "R194")
MAPPA = {"R161": "R190", "R162": "R191", "R167": "R192", "Q168": "Q193", "R169": "R194"}

g2a.richieste = lambda v: g2a.OGGI + NUOVE


def sorg():
    v = "sorg"
    g2a.prepara(v, None, (), NUOVE)
    for f in ("gain_block.subckt", "gain_block_flat.inc"):
        if open(os.path.join(L, "varianti", v, f)).read() != open(os.path.join(SP, f)).read():
            sys.exit("RIFIUTATO: varianti/%s/%s non e' il blocco del sorgente" % (v, f))
    corpo = {r.split()[0] for r in gc.righe_subckt() if r.split()}
    propri = [m for m, nome, _, _, _ in gc.modi() if nome in NUOVE and m not in gc.RAIL_A_MASSA]
    if len(propri) < 2 * len(NUOVE):
        sys.exit("RIFIUTATO: %d modi per %d parti nuove" % (len(propri), len(NUOVE)))
    modi = [m for m in g2a.QUINDICI if m.rsplit("_", 1)[0] in corpo]
    if len(modi) != len(g2a.QUINDICI):
        sys.exit("RIFIUTATO: dei quindici il blocco ne ha %d" % len(modi))
    g2a.esistono(modi + propri)
    lista = []
    for pos, gain in g62.POSIZIONI:
        for m in ["rif"] + modi + propri:
            if m == "rif" or (pos, gain) in g2a.posizioni_di(m):
                lista.append(g2a.un_deck(v, pos, gain, m, NUOVE))
    gc.SUBCKT = os.path.join(SP, "gain_block.subckt")
    g2a.scrivi(os.path.join(L, "deck", "lista_sorg.txt"), "\n".join(lista) + "\n")
    print("sorg: %d deck; modi delle parti nuove: %s" % (len(lista), " ".join(propri)))


if __name__ == "__main__":
    if sys.argv[1:] != ["sorg"]:
        sys.exit(__doc__)
    sorg()
