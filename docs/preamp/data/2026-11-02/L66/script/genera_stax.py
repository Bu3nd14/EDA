#!/usr/bin/env python3
"""L66: la Stax (P10) dei modi che sul blocco del sorgente portano l'uscita lontano dal riposo, con il
banco della Stax di L45d2b3b2b2 (genera_stax_lunghi.py: genera_stax.py di L45d2b3b1 puntato al blocco
del sorgente, con le cinque parti di ADR-099). Solo stdlib, /usr/bin/python3 -I.

Uso: genera_stax.py <nome_lista> <caso> [<caso> ...]
     caso = G0_<pos>_<modo>[_k105]  (come in p10_stax_lunghi.csv; _k105 = il condensatore d'uscita +5 %)
     -> deck/stax/<caso>.cir, inc_stax/sorg/, deck/lista_<nome_lista>.txt

Le impostazioni (gear, durata) sono quelle di genera_stax.modi() di L45d2b3b1; un modo che li' non c'e'
prende la corsa normale (g2.T_FINE, senza gear), come fa modi() per i modi aggiunti.
Il caso noto: G0_F2_Q132_ce e G0_F2_Q133_ce (con _k105) devono ridare le righe di
p10_stax_lunghi.csv di L45d2b3b2b2.
"""
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
DATA = os.path.abspath(os.path.join(L, "..", ".."))
sys.path.insert(0, os.path.join(DATA, "2026-10-22", "L45d2b3b1", "script"))
import genera_stax as gs   # noqa: E402

gc, g60 = gs.gc, gs.g60
gs.L = L
NUOVE = ("R190", "R191", "R192", "Q193", "R194")


def chiave(nome):
    k = "1.05" if nome.endswith("_k105") else "1"
    base = nome[:-5] if nome.endswith("_k105") else nome
    _, pos, modo = base.split("_", 2)
    return pos, modo, k


def main(lista_nome, casi):
    src = open(gs.SUBCKT["oggi"]).read()
    righe = {r.split()[0] for r in src.splitlines() if r.split()}
    if set(("R160",) + NUOVE) - righe:
        sys.exit("RIFIUTATO: spice/preamp/gain_block.subckt non e' il blocco di ADR-099")
    agg = sorted({chiave(n)[:2] for n in casi})
    impost = {(p, m): (g, tf) for p, m, g, tf in gs.modi(agg)}
    gs.imposta("oggi")
    g60.INC = os.path.join(L, "inc_stax", "sorg")
    g60.INC_REL = "@REPO@/%s/" % os.path.relpath(g60.INC, gc.ROOT)
    g60.OGGI = gs.OGGI + ("R160",) + NUOVE
    lista = []
    for nome in casi:
        pos, modo, k = chiave(nome)
        gear, tf = impost[(pos, modo)]
        t = gs.g1.applica(gc.deck_tr(pos, 0, modo, False, False, tfine=tf, gear=gear), "G0", float(k))
        p = gs.scrivi_deck("stax", nome, t, "oggi")
        inc = [r.split()[1] for r in open(p) if r.startswith(".include") and "/inc_stax/sorg/" in r]
        if len(inc) != 1:
            sys.exit("RIFIUTATO: %s include %d copie guaste" % (nome, len(inc)))
        copia = open(inc[0].replace("@REPO@", gc.ROOT)).read()
        nella = {r.split()[0] for r in copia.splitlines() if r.split()}
        if not set(g60.OGGI) <= nella:
            sys.exit("RIFIUTATO: la copia %s non ha %s" % (inc[0], sorted(set(g60.OGGI) - nella)))
        lista.append(p)
    gc.scrivi(os.path.join(L, "deck", "lista_%s.txt" % lista_nome), "\n".join(lista) + "\n")
    print("%s: %d deck" % (lista_nome, len(lista)))


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2:])
