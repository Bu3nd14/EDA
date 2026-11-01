#!/usr/bin/env python3
"""L58b (ADR-071, ADR-100: il degrado silenzioso del blocco, alla diagnosi): i 28 guasti del blocco
dentro P10 sul blocco del SORGENTE, per leggere che cosa ne vede un tester ai test point d'uscita
(ADR-107) - la continua all'uscita del blocco - e la corrente dei rail del blocco (il riposo).
Solo stdlib, /usr/bin/python3 -I.

Uso: genera.py sorg -> varianti/sorg/, inc/sorg/, deck/sorg_<pos>/*.cir, deck/lista_sorg.txt

Il banco e' quello di L45d2b3b2b2 (il suo genera.py caricato per percorso, e attraverso lui
L45d2b3b2a, L45d2b3b1, L62b e il canale di L45a), coi percorsi puntati a QUESTA cartella. La variante
«sorg» e' il blocco di spice/preamp/ byte per byte (rifiutato altrimenti). I modi: rif, i 28 di
ADR-071 (fmea_dopo.csv di L45d2b3b3, stato «alla diagnosi, L58 (ADR-071)»), e due dei quindici di
L45d2b3b2b2 come CASO NOTO (Q132_ce, R126_cc: le loro righe di calore_sorg.csv e analisi_jack_sorg.csv
si ridanno alla cifra prima di leggere i 28).
"""
import importlib.util
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
DATA = os.path.abspath(os.path.join(L, "..", ".."))
_spec = importlib.util.spec_from_file_location(
    "genera_l45d2b3b2b2", os.path.join(DATA, "2026-10-23", "L45d2b3b2b2", "script", "genera.py"))
gs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gs)
g2a, g62, gc = gs.g2a, gs.g62, gs.gc
# the paths to THIS folder (gs set them to L45d2b3b2b2's at import)
g2a.L = L
g62.L62A = L
g62.REL = os.path.relpath(L, g62.ROOT)
NUOVE = gs.NUOVE

VENTOTTO = ("C104_cc Q132_be Q133_be Q132_ae Q133_ae Q125_be Q117_ce Q118_ce Q127_ce Q148_be C105_cc "
            "C137_cc R115_ap R130_ap R131_ap R134_ap R147_ap D102_cc D103_cc R143_ap R111_cc R112_cc "
            "R123_cc R128_cc R134_cc R135_cc R136_cc R144_cc").split()
NOTI = ("Q132_ce", "R126_cc")


def sorg():
    v = "sorg"
    g2a.prepara(v, None, (), NUOVE)
    for f in ("gain_block.subckt", "gain_block_flat.inc"):
        if open(os.path.join(L, "varianti", v, f)).read() != open(os.path.join(g2a.SP, f)).read():
            sys.exit("RIFIUTATO: varianti/%s/%s non e' il blocco del sorgente" % (v, f))
    corpo = {r.split()[0] for r in gc.righe_subckt() if r.split()}
    modi = list(NOTI) + VENTOTTO
    if any(m.rsplit("_", 1)[0] not in corpo for m in modi):
        sys.exit("RIFIUTATO: un modo su una parte che il blocco non ha")
    g2a.esistono(modi)
    lista = []
    for pos, gain in g62.POSIZIONI:
        for m in ["rif"] + modi:
            if m == "rif" or (pos, gain) in g2a.posizioni_di(m):
                lista.append(g2a.un_deck(v, pos, gain, m, NUOVE))
    gc.SUBCKT = os.path.join(g2a.SP, "gain_block.subckt")
    g2a.scrivi(os.path.join(L, "deck", "lista_sorg.txt"), "\n".join(lista) + "\n")
    print("sorg: %d deck" % len(lista))


if __name__ == "__main__":
    if sys.argv[1:] != ["sorg"]:
        sys.exit(__doc__)
    sorg()
