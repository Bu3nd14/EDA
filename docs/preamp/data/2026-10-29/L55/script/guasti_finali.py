#!/usr/bin/env python3
"""L55 (NC-056): i guasti della FMEA che toccano i finali, e P7, sul blocco col candidato.

Il banco e' quello del calore di L45d2b3b2b2 (il blocco del sorgente, variante «sorg»), cioe'
genera.py di L45d2b3b2a importato come g2a (e attraverso lui L45d2b3b1, L62b e il canale di L45a:
rail ideali a +-15 V, le cinque posizioni, il guasto a 0,3 s, le potenze medie degli ultimi 10 ms),
coi percorsi puntati a QUESTA cartella e le parti di ADR-099 richieste in ogni copia. Non si importa
genera.py di L45d2b3b2b2: importa a sua volta un modulo «genera» (quello di L45d2b3b2a), e i due
nomi collidono; le sue righe di sorg() sono rifatte qui.

Le varianti (senza «_»: analizza_calore.py divide la cartella al primo):
  fmje     il blocco del sorgente byte per byte (rifiutato altrimenti): il CASO NOTO, deve ridare
           le righe di Q132 / Q133 di calore_sorg.csv di L45d2b3b2b2
  c243     MJE243G / MJE253G, R128 1,78k (script/varianti.py, «mje24x»)
  c243m    lo stesso col Miller C124 330p («mje24x_cm330p»)
I modi: rif + Q132 / Q133 in corto collettore-emettitore, base-emettitore, emettitore aperto.
I modelli del candidato entrano in MODELLI del canale (gc.MODELLI, letto a ogni deck).

P7 (il corto all'uscita col mute e i transitori, il banco di L56 / L45d2b3b2b1): tb_mute_corto.cir
di spice/preamp/tb con il subckt della variante e i modelli del candidato, in deck/p7/<v>.cir.

Il banco gira a 27 C: con i dispositivi a 60 C la potenza del finale superstite nel corto e' piu'
bassa (L45d2b3b2b2, dissipatore.csv: 1,543 contro 1,607 W). Solo stdlib, /usr/bin/python3 -I.

Uso: guasti_finali.py   -> varianti/<v>/, inc/<v>/, deck/<v>_<pos>/*.cir, deck/p7/<v>.cir,
                           deck/lista_finali.txt, deck/lista_p7.txt
"""
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
DATA = os.path.abspath(os.path.join(L, "..", ".."))
sys.path.insert(0, os.path.join(DATA, "2026-10-22", "L45d2b3b2a", "script"))
import genera as g2a   # noqa: E402

g62, gc = g2a.g62, g2a.gc
g2a.L = L
g62.L62A = L
g62.REL = os.path.relpath(L, g62.ROOT)
SP = g2a.SP
NUOVE = ("R190", "R191", "R192", "Q193", "R194")
g2a.richieste = lambda v: g2a.OGGI + NUOVE
MODELLI_OGGI = gc.MODELLI
CAND = (".include @REPO@/models/bjt_npn/mje243.lib\n"
        ".include @REPO@/models/bjt_pnp/mje253.lib\n")
C243 = {"Q132": ["Q132 VPLUS NBN NEN Qmje243"], "Q133": ["Q133 VMINUS NBP NEP Qmje253"],
        "R128": ["R128 NX NBB 1.78k"]}
# «fmje», non «mje»: analizza_calore.py raccoglie run/<v>_*, e run/mje_* prende anche le cartelle
# degli altri banchi di questo lotto (mje_fz, mje_senza_d158d159, ...)
VARIANTI = {"fmje": None, "c243": C243, "c243m": dict(C243, C124=["C124 NX NHI 330p"])}
MODI = ("Q132_ce", "Q133_ce", "Q132_be", "Q133_be", "Q132_ae", "Q133_ae")
TB = os.path.join(g62.ROOT, "spice", "preamp", "tb", "tb_mute_corto.cir")
SANO = "@REPO@/spice/preamp/gain_block.subckt"


def main():
    lista, lista_p7 = [], []
    for v, cambi in VARIANTI.items():
        gc.MODELLI = MODELLI_OGGI if cambi is None else MODELLI_OGGI + CAND
        g2a.prepara(v, cambi, (), NUOVE)
        if cambi is None:
            for f in ("gain_block.subckt", "gain_block_flat.inc"):
                if open(os.path.join(L, "varianti", v, f)).read() != open(os.path.join(SP, f)).read():
                    sys.exit("RIFIUTATO: varianti/%s/%s non e' il blocco del sorgente" % (v, f))
        g2a.esistono(MODI)
        for pos, gain in g62.POSIZIONI:
            for m in ("rif",) + MODI:
                if m == "rif" or (pos, gain) in g2a.posizioni_di(m):
                    lista.append(g2a.un_deck(v, pos, gain, m, NUOVE))
        # P7: tb_mute_corto col subckt della variante
        t = open(TB).read()
        if t.count(SANO) != 1:
            sys.exit("RIFIUTATO: tb_mute_corto include il blocco %d volte" % t.count(SANO))
        nuovo = ".include @REPO@/%s/varianti/%s/gain_block.subckt" % (g62.REL, v)
        t = t.replace(".include " + SANO, (CAND if cambi else "") + nuovo)
        t = "tb_mute_corto - L55 (NC-056), variante %s\n" % v + t.split("\n", 1)[1]
        lista_p7.append(g2a.scrivi(os.path.join(L, "deck", "p7", v + ".cir"), t))
    gc.MODELLI = MODELLI_OGGI
    gc.SUBCKT = os.path.join(SP, "gain_block.subckt")
    g2a.scrivi(os.path.join(L, "deck", "lista_finali.txt"), "\n".join(lista) + "\n")
    g2a.scrivi(os.path.join(L, "deck", "lista_p7.txt"), "\n".join(lista_p7) + "\n")
    print("finali: %d deck; p7: %d deck" % (len(lista), len(lista_p7)))


if __name__ == "__main__":
    main()
