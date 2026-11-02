#!/usr/bin/env python3
"""L66 (NC-076, ADR-099, ADR-100): i modi del blocco FUORI dai quindici di ADR-099, rifatti sul blocco
del SORGENTE col banco del calore. Solo stdlib, /usr/bin/python3 -I.

Uso: genera.py elenco          -> stampa i modi del blocco e la loro divisione, non scrive deck
     genera.py noto            -> deck/lista_noto.txt   (il caso noto)
     genera.py fuori           -> deck/lista_fuori.txt  (i modi da rifare)
     genera.py <nome> <modo>.. -> deck/lista_<nome>.txt (una lista a mano, sulla variante sorg)

Il banco e' quello di L45d2b3b2b2 (il suo genera.py caricato per percorso, e attraverso lui
L45d2b3b2a, L45d2b3b1, L62b e il canale di L45a), coi percorsi puntati a QUESTA cartella, come in
L58b. La variante «sorg» e' il blocco di spice/preamp/ byte per byte (rifiutato altrimenti).

Il caso noto: rif, Q132_ce, R126_cc (calore_sorg.csv di L45d2b3b2b2 e di L58b) e Q132_be (la riga di
calore_fmje.csv di L55: 126 C), nelle cinque posizioni.
I modi da rifare: tutti quelli che il canale (gc.modi()) da' sul blocco del sorgente, tolti i quindici
di ADR-099, i modi delle cinque parti nuove (L45d2b3b2b2) e i 28 di ADR-071 (L58b): questi tre gruppi
sono gia' stati corsi sul sorgente.
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
g2a.L = L
g62.L62A = L
g62.REL = os.path.relpath(L, g62.ROOT)
NUOVE = gs.NUOVE

VENTOTTO = ("C104_cc Q132_be Q133_be Q132_ae Q133_ae Q125_be Q117_ce Q118_ce Q127_ce Q148_be C105_cc "
            "C137_cc R115_ap R130_ap R131_ap R134_ap R147_ap D102_cc D103_cc R143_ap R111_cc R112_cc "
            "R123_cc R128_cc R134_cc R135_cc R136_cc R144_cc").split()
NOTI = ("Q132_ce", "R126_cc", "Q132_be")


def prepara():
    v = "sorg"
    g2a.prepara(v, None, (), NUOVE)
    for f in ("gain_block.subckt", "gain_block_flat.inc"):
        if open(os.path.join(L, "varianti", v, f)).read() != open(os.path.join(g2a.SP, f)).read():
            sys.exit("RIFIUTATO: varianti/%s/%s non e' il blocco del sorgente" % (v, f))
    return v


def divisione():
    tutti = [m for m, _, _, _, _ in gc.modi() if m not in gc.RAIL_A_MASSA]
    nuove = [m for m, nome, _, _, _ in gc.modi() if nome in NUOVE]
    gia = set(g2a.QUINDICI) | set(nuove) | set(VENTOTTO)
    fuori = [m for m in tutti if m not in gia]
    return tutti, nuove, fuori


def lista(v, nome, modi):
    corpo = {r.split()[0] for r in gc.righe_subckt() if r.split()}
    if any(m.rsplit("_", 1)[0] not in corpo for m in modi):
        sys.exit("RIFIUTATO: un modo su una parte che il blocco non ha")
    g2a.esistono(modi)
    righe = []
    for pos, gain in g62.POSIZIONI:
        for m in ["rif"] + list(modi):
            if m == "rif" or (pos, gain) in g2a.posizioni_di(m):
                righe.append(g2a.un_deck(v, pos, gain, m, NUOVE))
    gc.SUBCKT = os.path.join(g2a.SP, "gain_block.subckt")
    g2a.scrivi(os.path.join(L, "deck", "lista_%s.txt" % nome), "\n".join(righe) + "\n")
    print("%s: %d deck" % (nome, len(righe)))


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    v = prepara()
    tutti, nuove, fuori = divisione()
    if a == ["elenco"]:
        print("tutti %d, nuove %d, quindici %d, ventotto %d, fuori %d"
              % (len(tutti), len(nuove), len(g2a.QUINDICI), len(VENTOTTO), len(fuori)))
        print(" ".join(fuori))
        assenti = [m for m in list(g2a.QUINDICI) + VENTOTTO if m not in tutti]
        print("assenti dal canale:", assenti)
    elif a == ["noto"]:
        lista(v, "noto", NOTI)
    elif a == ["fuori"]:
        lista(v, "fuori", fuori)
    else:
        lista(v, a[0], a[1:])
