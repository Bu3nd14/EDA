#!/usr/bin/env python3
"""L45d2b3b3: P10 sulla Stax per i modi delle cinque parti di ADR-099 (R190, R191, R192, Q193, R194),
sul blocco del SORGENTE. Solo stdlib, /usr/bin/python3 -I.

Uso: genera_stax_nuove.py   -> deck/stax_controllo/, deck/stax_nuove/, inc_stax/sorg/,
                               deck/lista_stax_controllo.txt, deck/lista_stax_nuove.txt

L45d2b3b2b2 ha corso questi modi al calore (sintesi_sorg.csv), non sulla Stax: tre portano il blocco al
rail (Q193 in corto C-E, R192 aperta, R194 aperta, 12,7-15 V alla principale). Il banco e' quello di
genera_stax_lunghi.py di L45d2b3b2b2 (e attraverso lui genera_stax.py di L45d2b3b1, L60d2, L60c2, L60c1,
L45a): la geometria G0, A e F2, condensatore nominale e +5 %, i modi nuovi con l'impostazione di
default del banco (non gear, g2.T_FINE).

IL CASO NOTO, prima: tre casi di L45d2b3b2b2/stax_lunghi.csv rigenerati qui con le loro impostazioni
devono ridare la colonna sorgente_ms (confronta_stax.py). Rifiuta un blocco, o una copia guasta, senza
R160 e le cinque parti di ADR-099, e un modo che il blocco di oggi non ha.
"""
import csv
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
DATA = os.path.abspath(os.path.join(L, "..", ".."))
B1 = os.path.join(DATA, "2026-10-22", "L45d2b3b1")
B2 = os.path.join(DATA, "2026-10-23", "L45d2b3b2b2")
sys.path.insert(0, os.path.join(B1, "script"))
import genera_stax as gs   # noqa: E402

gc, g60, g1, g2 = gs.gc, gs.g60, gs.g1, gs.g2
gs.L = L
NUOVE = ("R190", "R191", "R192", "Q193", "R194")
CONTROLLO = ("G0_A_JQ110B_as_k105", "G0_F2_Q133_ce", "G0_A_D102_ap")


def nomi(f):
    p = os.path.join(B1, f)
    return [r["modo"] for r in csv.DictReader(open(p))] if os.path.exists(p) else []


def chiave(nome):
    k = "1.05" if nome.endswith("_k105") else "1"
    base = nome[:-5] if nome.endswith("_k105") else nome
    _, pos, modo = base.split("_", 2)
    return pos, modo, k


def deck(gruppo, nome, pos, modo, k, gear, tf):
    t = g1.applica(gc.deck_tr(pos, 0, modo, False, False, tfine=tf, gear=gear), "G0", float(k))
    p = gs.scrivi_deck(gruppo, nome, t, "oggi")
    inc = [r.split()[1] for r in open(p) if r.startswith(".include") and "/inc_stax/sorg/" in r]
    if len(inc) != 1:
        sys.exit("RIFIUTATO: %s include %d copie guaste" % (nome, len(inc)))
    copia = open(inc[0].replace("@REPO@", gc.ROOT)).read()
    nella = {r.split()[0] for r in copia.splitlines() if r.split()}
    if not set(g60.OGGI) <= nella:
        sys.exit("RIFIUTATO: la copia %s non ha %s" % (inc[0], sorted(set(g60.OGGI) - nella)))
    return p


def main():
    src = open(gs.SUBCKT["oggi"]).read()
    righe = {r.split()[0] for r in src.splitlines() if r.split()}
    manca = set(("R160",) + NUOVE) - righe
    if manca:
        sys.exit("RIFIUTATO: spice/preamp/gain_block.subckt senza %s: non e' il blocco di ADR-099" % sorted(manca))
    gs.imposta("oggi")
    g60.INC = os.path.join(L, "inc_stax", "sorg")
    g60.INC_REL = "@REPO@/%s/" % os.path.relpath(g60.INC, gc.ROOT)
    g60.OGGI = gs.OGGI + ("R160",) + NUOVE
    # il caso noto: le impostazioni di L45d2b3b2b2 (genera_stax_lunghi.py)
    in_gear = set(nomi("p10_stax_gear.csv")) | set(nomi("p10_stax_lunghi_gear.csv"))
    impost = {(p, m): (g, tf) for p, m, g, tf in gs.modi([])}
    noti = {r["caso"] for r in csv.DictReader(open(os.path.join(B2, "stax_lunghi.csv")))}
    controllo = []
    for nome in CONTROLLO:
        if nome not in noti:
            sys.exit("RIFIUTATO: %s non e' in stax_lunghi.csv di L45d2b3b2b2" % nome)
        pos, modo, k = chiave(nome)
        gear, tf = impost[(pos, modo)]
        controllo.append(deck("stax_controllo", nome, pos, modo, k, gear or nome in in_gear, tf))
    # i modi nuovi
    propri = sorted(m for m, nome, _, _, _ in gc.modi() if nome in NUOVE)
    if len(propri) != 11:
        sys.exit("RIFIUTATO: %d modi delle parti nuove, attesi 11: %s" % (len(propri), propri))
    lista = []
    for modo in propri:
        for pos in ("A", "F2"):
            for k in ("1", "1.05"):
                nome = "G0_%s_%s%s" % (pos, modo, "" if k == "1" else "_k105")
                lista.append(deck("stax_nuove", nome, pos, modo, k, False, g2.T_FINE))
    gc.scrivi(os.path.join(L, "deck", "lista_stax_controllo.txt"), "\n".join(controllo) + "\n")
    gc.scrivi(os.path.join(L, "deck", "lista_stax_nuove.txt"), "\n".join(lista) + "\n")
    print("controllo: %d deck; nuove: %d deck sui modi %s" % (len(controllo), len(lista), " ".join(propri)))


if __name__ == "__main__":
    main()
