#!/usr/bin/env python3
"""L60d1, ADR-086: il valore della resistenza in parallelo alla resistenza di gate del lato di
retroazione (R150 sul blocco del file, in parallelo a R109), sui tre deck d'anello di V1 (blocco
B, blocco A, buffer fisso). Varianti del sottocircuito e dell'include piatto GENERATI dal
sorgente, toccati in una riga:

  r<val>_nom    R150 = <val>, R109 al suo posto; i deck come sono. Il loro metodo resta esatto:
                rompono l'anello al posto di R109 (RBRK 100 + VINJ verso il gate) e misurano
                T = V(FB)/V(G2) su un gate che non assorbe corrente; R150 scavalca RBRK + VINJ e
                toglie solo un po' d'efficienza all'iniezione.
  r<val>_r109a  il guasto: R109 aperta, l'anello si chiude solo per R150. I deck aprono gia' R109
                (alter r109 = 1G); R150 si toglie dal blocco e RBRK prende il suo valore. Con 10k
                la resistenza di gate e la capacita' della JFET (~6 pF) fanno un polo dentro
                l'anello, quindi l'iniezione va dal lato di FB, che e' a bassa impedenza:
                VINJ FB NBRK, RBRK NBRK G2 <val>, T = V(FB)/V(NBRK).
  r100_r109a    controllo del metodo spostato: RBRK = 100, deve ridare i margini dei deck.

Solo stdlib, /usr/bin/python3 -I.

Uso: prepara_shunt.py   -> shunt/<variante>/{gain_block.subckt,gain_block_flat.inc,deck/*.cir},
                           shunt/lista.txt (una riga: <variante> <deck>)
"""
import os
import shutil

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
R = os.path.abspath(os.path.join(L, "..", "..", "..", "..", ".."))
SP = os.path.join(R, "spice", "preamp")
DECK = ("tb_loop", "tb_loop_blockA", "tb_loop_bufferfissa")
VARIANTI = [("r4p7k_nom", "4.7k", False), ("r22k_nom", "22k", False),
            ("r4p7k_r109a", "4.7k", True), ("r10k_r109a", "10k", True),
            ("r22k_r109a", "22k", True), ("r100_r109a", "100", True)]


def blocco(txt, val, aperta):
    # la riga di R150 col valore del sorgente (10k quando la scansione e' stata corsa)
    a = [r for r in txt.split("\n") if r.startswith("R150 FB G2 ")]
    assert len(a) == 1
    a = a[0] + "\n"
    if aperta:
        return txt.replace(a, "* R150 tolta: il deck la rifa' come RBRK (L60d1)\n")
    return txt.replace(a, "R150 FB G2 %s\n" % val)


def deck(c, val, aperta):
    if not aperta:
        return c
    a = "RBRK FB NBRK 100\nVINJ NBRK G2 DC 0 AC 1\n"
    assert c.count(a) == 1
    c = c.replace(a, "VINJ FB NBRK DC 0 AC 1\nRBRK NBRK G2 %s\n" % val)
    n = c.count("let T = v(fb)/v(g2)")
    assert n >= 1
    return c.replace("let T = v(fb)/v(g2)", "let T = v(fb)/v(nbrk)")


sub = open(os.path.join(SP, "gain_block.subckt")).read()
flat = open(os.path.join(SP, "gain_block_flat.inc")).read()
base = os.path.join(L, "shunt")
for d in os.listdir(base) if os.path.isdir(base) else []:
    if os.path.isdir(os.path.join(base, d)):
        shutil.rmtree(os.path.join(base, d))
lista = []
for nome, val, aperta in VARIANTI:
    d = os.path.join(base, nome)
    os.makedirs(os.path.join(d, "deck"), exist_ok=True)
    ps = os.path.join(d, "gain_block.subckt")
    pf = os.path.join(d, "gain_block_flat.inc")
    open(ps, "w").write(blocco(sub, val, aperta))
    open(pf, "w").write(blocco(flat, val, aperta))
    for k in DECK:
        c = open(os.path.join(SP, "tb", k + ".cir")).read()
        n = 0
        for vecchio, nuovo in (("@REPO@/spice/preamp/gain_block.subckt", ps),
                               ("@REPO@/spice/preamp/gain_block_flat.inc", pf)):
            n += c.count(vecchio)
            c = c.replace(vecchio, nuovo)
        assert n >= 1, k
        open(os.path.join(d, "deck", k + ".cir"), "w").write(deck(c, val, aperta))
        lista.append("%s %s" % (nome, k))
open(os.path.join(base, "lista.txt"), "w").write("\n".join(lista) + "\n")
print(len(lista), "corse")
