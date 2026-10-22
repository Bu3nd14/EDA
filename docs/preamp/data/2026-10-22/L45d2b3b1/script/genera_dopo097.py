#!/usr/bin/env python3
"""L45d2b3b1: le corse sul blocco DOPO ADR-097 (R153 + R160, due 2,4 k in serie). Solo stdlib,
/usr/bin/python3 -I.

Uso: genera_dopo097.py    scrive varianti/dopo097/, inc/dopo097/, inc_stax/dopo097/,
                          deck/dopo097_<pos>/<modo>.cir, deck/stax_dopo097/<caso>.cir,
                          deck/lista_dopo097_r120.txt, deck/lista_dopo097.txt

Le corse di prima restano com'erano (deck/oggi_*, deck/stax_*: il blocco prima di ADR-097). Qui:
  - il banco del calore (genera_calore.py, la variante dopo097 = spice/preamp/gain_block.subckt di
    oggi): rif, R153_ap / R153_cc / R160_ap / R160_cc nelle cinque posizioni a 2,3 s; e R120_cc a
    0,6 s (limitations #75: su 2,3 s ngspice cresce a ~9 GB; L45a lo correva corto), in una lista
    a parte, da correre UNA alla volta;
  - il banco della Stax (genera_stax.py): R153 e R160 aperti e in corto, A e F2, C nominale e +5 %.
"""
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
sys.path.insert(0, QUI)
import genera_calore as gk   # noqa: E402
import genera_stax as gs     # noqa: E402

g62, gc = gk.g62, gk.gc
V = "dopo097"
SP = gk.SP
NUOVI = ("R153", "R160")
T_CORTA = 0.6


def main():
    src = open(os.path.join(SP, "gain_block.subckt")).read()
    if "R160" not in src:
        sys.exit("RIFIUTATO: spice/preamp/gain_block.subckt non ha R160: non e' il blocco di ADR-097")
    d = os.path.join(L, "varianti", V)
    g62.scrivi(os.path.join(d, "gain_block.subckt"), src)
    g62.scrivi(os.path.join(d, "gain_block_flat.inc"), open(os.path.join(SP, "gain_block_flat.inc")).read())
    g62.VARIANTI[V] = []
    g62.PROPRIE[V] = list(gk.DIODI[2:]) + ["R160"]
    gc.SUBCKT = os.path.join(d, "gain_block.subckt")
    modi = [m for m, nome in gk.modi_tutti() if nome in NUOVI]
    if len(modi) != 4:
        sys.exit("RIFIUTATO: %d modi di R153 / R160" % len(modi))
    lista, lista_r120 = [], []
    orig = gc.deck_tr
    for pos, gain in g62.POSIZIONI:
        cart = "%s_%s%s" % (V, pos, "_g10" if gain else "")
        for m in ["rif"] + modi + ["R120_cc"]:
            if m == "R120_cc":
                gc.deck_tr = lambda *a, **k: orig(*a, tfine=T_CORTA, **k)
            t = gk.con_diodi(g62.deck_guasto(V, pos, gain, m), pos, m)
            gc.deck_tr = orig
            if m != "rif":
                copia = open(os.path.join(L, "inc", V, m + ".subckt")).read()
                righe = {r.split()[0] for r in copia.splitlines() if r.split()}
                if not set(gk.OGGI + ("R160",)) <= righe:
                    sys.exit("RIFIUTATO: la copia %s non e' il blocco di ADR-097" % m)
            p = g62.scrivi(os.path.join(L, "deck", cart, m + ".cir"), t)
            (lista_r120 if m == "R120_cc" else lista).append(p)
    # la Stax: genera_stax con le sue cartelle spostate su dopo097
    gs.SUBCKT[V] = os.path.join(SP, "gain_block.subckt")
    gs.imposta("oggi")
    gs.g60.INC = os.path.join(L, "inc_stax", V)
    gs.g60.INC_REL = "@REPO@/%s/" % os.path.relpath(gs.g60.INC, gc.ROOT)
    gs.g60.OGGI = gs.OGGI + ("R160",)
    gc.SUBCKT = gs.SUBCKT[V]
    for pos in ("A", "F2"):
        for m in modi:
            for k in (1.0, 1.05):
                nome = "G0_%s_%s%s" % (pos, m, "" if k == 1.0 else "_k105")
                t = gs.g1.applica(gc.deck_tr(pos, 0, m, False, False, tfine=gs.g2.T_FINE), "G0", k)
                lista.append(gs.scrivi_deck("stax_" + V, nome, t, "oggi"))
    gc.SUBCKT = os.path.join(SP, "gain_block.subckt")
    g62.scrivi(os.path.join(L, "deck", "lista_dopo097.txt"), "\n".join(lista) + "\n")
    g62.scrivi(os.path.join(L, "deck", "lista_dopo097_r120.txt"), "\n".join(lista_r120) + "\n")
    print("dopo097: %d deck (calore e Stax), %d di R120 in corto a %g s" % (len(lista), len(lista_r120), T_CORTA))


if __name__ == "__main__":
    main()
