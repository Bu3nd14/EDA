#!/usr/bin/env python3
"""L45d2b3b2b2: i guasti piu' lunghi sulla Stax (oltre 100 ms) rifatti sul blocco del SORGENTE, con
ADR-099 (il «Vincoli per la seconda parte» di ADR-099 e il «Da riaprire se» di ADR-098). Solo stdlib,
/usr/bin/python3 -I.

Uso: genera_stax_lunghi.py     -> deck/stax_lunghi/<caso>.cir, inc_stax/sorg/, deck/lista_stax_lunghi.txt

I casi sono ESATTAMENTE quelli di L45d2b3b1 (p10_stax_lunghi.csv di L45d2b3b1, 121), con le loro
impostazioni (genera_stax.modi(): gear e durata della corsa buona di L60d2; gear anche per quelli di
p10_stax_gear.csv). L'unico che L45d2b3b1 ha dovuto rifare in gear dopo (p10_stax_lunghi_gear.csv, Q122
in corto, fermato subito dopo il guasto) qui parte gia' in gear: e' l'impostazione con cui L45d2b3b1 ha
chiuso. Il generatore di L45d2b3b1 rifiutava un blocco senza R160; questo rifiuta anche un blocco, e
ogni copia guasta, senza le cinque parti di ADR-099 (R190, R191, R192, Q193, R194).
"""
import csv
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
DATA = os.path.abspath(os.path.join(L, "..", ".."))
B1 = os.path.join(DATA, "2026-10-22", "L45d2b3b1")
sys.path.insert(0, os.path.join(B1, "script"))
import genera_stax as gs   # noqa: E402

gc, g60 = gs.gc, gs.g60
gs.L = L
NUOVE = ("R190", "R191", "R192", "Q193", "R194")


def nomi(f):
    p = os.path.join(B1, f)
    return [r["modo"] for r in csv.DictReader(open(p))] if os.path.exists(p) else []


def chiave(nome):
    k = "1.05" if nome.endswith("_k105") else "1"
    base = nome[:-5] if nome.endswith("_k105") else nome
    _, pos, modo = base.split("_", 2)
    return pos, modo, k


def main():
    src = open(gs.SUBCKT["oggi"]).read()
    righe = {r.split()[0] for r in src.splitlines() if r.split()}
    manca = set(("R160",) + NUOVE) - righe
    if manca:
        sys.exit("RIFIUTATO: spice/preamp/gain_block.subckt senza %s: non e' il blocco di ADR-099" % sorted(manca))
    casi = nomi("p10_stax_lunghi.csv")
    if len(casi) != 121 or len(set(casi)) != 121:
        sys.exit("RIFIUTATO: %d casi in p10_stax_lunghi.csv di L45d2b3b1, attesi 121" % len(casi))
    in_gear = set(nomi("p10_stax_gear.csv")) | set(nomi("p10_stax_lunghi_gear.csv"))
    impost = {(p, m): (g, tf) for p, m, g, tf in gs.modi([])}
    gs.imposta("oggi")
    g60.INC = os.path.join(L, "inc_stax", "sorg")
    g60.INC_REL = "@REPO@/%s/" % os.path.relpath(g60.INC, gc.ROOT)
    g60.OGGI = gs.OGGI + ("R160",) + NUOVE
    lista = []
    for nome in casi:
        pos, modo, k = chiave(nome)
        gear, tf = impost[(pos, modo)]
        gear = gear or nome in in_gear
        t = gs.g1.applica(gc.deck_tr(pos, 0, modo, False, False, tfine=tf, gear=gear), "G0", float(k))
        p = gs.scrivi_deck("stax_lunghi", nome, t, "oggi")
        inc = [r.split()[1] for r in open(p) if r.startswith(".include") and "/inc_stax/sorg/" in r]
        for i in inc:
            copia = open(i.replace("@REPO@", gc.ROOT)).read()
            nella = {r.split()[0] for r in copia.splitlines() if r.split()}
            if not set(g60.OGGI) <= nella:
                sys.exit("RIFIUTATO: la copia %s non ha %s" % (i, sorted(set(g60.OGGI) - nella)))
        if len(inc) != 1:
            sys.exit("RIFIUTATO: %s include %d copie guaste" % (nome, len(inc)))
        lista.append(p)
    gc.scrivi(os.path.join(L, "deck", "lista_stax_lunghi.txt"), "\n".join(lista) + "\n")
    print("stax_lunghi: %d deck, %d in gear" % (len(lista), sum(1 for n in casi if n in in_gear or impost[chiave(n)[:2]][0])))


if __name__ == "__main__":
    main()
