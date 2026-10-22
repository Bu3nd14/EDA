#!/usr/bin/env python3
"""L45d2b3b1: P10 sulla Stax (fissa 2, 1 uF prima di K3, carico 50 k) coi guasti del blocco di oggi.
Solo stdlib, /usr/bin/python3 -I.

Uso:
  genera_stax.py [modi_in_piu.txt]   scrive deck/stax_g0/, deck/stax_guasti/, deck/stax_l60d2/,
                                     inc_stax/<v>/, deck/lista_stax.txt, deck/lista_stax_controllo.txt

IL BANCO e' quello di L60d2 (genera_L60d2.py, importato come g60, e con lui L60c2 / L60c1 / L45a):
la geometria G0 (47 ohm, 1 uF, K3 IM06), i 107 modi di L60c2 con la loro corsa buona, i 20 delle
parti di ADR-086 / ADR-087, A e F2, condensatore nominale e +5 %. Qui:
  - si aggiungono i modi dei diodi D154..D159 (ADR-090, ADR-095), aperti e in corto, e i modi di
    modi_in_piu.txt (uno per riga, «pos modo»: quelli che il banco del calore trova sopra il tetto
    sulla fissa 2 e che non sono fra questi);
  - le copie guaste si riscrivono dal blocco di oggi e si rifiutano senza R150..R153 e D154..D159
    (limitations #62);
  - IL CASO NOTO: la variante l60d2 (il blocco del commit 4fde9e40, quello di L60d2) su sei casi di
    L60d2, che deve ridare p10.csv di L60d2 (confronta_l60d2.py).
"""
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
DATA = os.path.abspath(os.path.join(L, "..", ".."))
sys.path.insert(0, os.path.join(DATA, "2026-10-19", "L60d2", "script"))
import genera_L60d2 as g60   # noqa: E402

g2, g1, gc = g60.g2, g60.g1, g60.gc
SP = os.path.join(gc.ROOT, "spice", "preamp")
SANO = "@REPO@/spice/preamp/gain_block.subckt"
DIODI = ("D154", "D155", "D156", "D157", "D158", "D159")
OGGI = ("R150", "R151", "R152", "R153") + DIODI
SUBCKT = {"oggi": os.path.join(SP, "gain_block.subckt"),
          "l60d2": os.path.join(L, "varianti", "l60d2", "gain_block.subckt")}
# i casi noti: brevi, sulle due posizioni, una corsa gear, il controllo e uno al +5 %
CONTROLLO = ("G0_CTRL_A", "G0_A_D102_ap_k105", "G0_A_JQ110B_as_k105", "G0_A_R109_ap",
             "G0_F2_R144_ap", "G0_F2_Q133_ce")


def imposta(v):
    gc.SUBCKT = SUBCKT[v]
    g60.INC = os.path.join(L, "inc_stax", v)
    g60.INC_REL = "@REPO@/%s/" % os.path.relpath(g60.INC, gc.ROOT)
    g60.OGGI = OGGI if v == "oggi" else ("R150", "R151", "R152", "R153")


def modi(in_piu, diodi=True):
    out = list(g60.modi())
    gia = {(p, m) for p, m, _, _ in out}
    nomi = {m for m, _, _, _, _ in gc.modi()}
    agg = [(pos, "%s_%s" % (d, s)) for d in DIODI for s in ("ap", "cc") for pos in ("A", "F2")]
    agg = (agg if diodi else []) + in_piu
    for pos, m in agg:
        if m not in nomi:
            sys.exit("RIFIUTATO: %s non e' un modo del blocco di oggi" % m)
        if (pos, m) not in gia:
            out.append((pos, m, False, g2.T_FINE))
            gia.add((pos, m))
    return sorted(out)


def casi(in_piu, diodi=True):
    c = [("stax_g0", n, t) for g, n, t in g2.casi() if g == "g0"]
    for pos, modo, gear, tfine in modi(in_piu, diodi):
        for k in (1.0, 1.05):
            sk = "" if k == 1.0 else "_k105"
            t = gc.deck_tr(pos, 0, modo, False, False, tfine=tfine, gear=gear)
            c.append(("stax_guasti", "G0_%s_%s%s" % (pos, modo, sk), g1.applica(t, "G0", k)))
    return c


def scrivi_deck(gruppo, nome, testo, v):
    testo = g60.reindirizza(g1.rinomina(testo, nome), nome)
    if gruppo != "stax_g0" and g60.INC_REL not in testo:
        sys.exit("RIFIUTATO: %s non include una copia guasta" % nome)
    if testo.count(SANO) != 1:
        sys.exit("RIFIUTATO: %s include il blocco sano %d volte" % (nome, testo.count(SANO)))
    if v != "oggi":
        testo = testo.replace(SANO, "@REPO@/%s" % os.path.relpath(SUBCKT[v], gc.ROOT))
    p = os.path.join(L, "deck", gruppo, nome + ".cir")
    if testo.startswith("L60c1 "):
        testo = "L45d2b3b1 %s" % v + testo[len("L60c1"):]
    else:
        testo = "L45d2b3b1 %s %s %s - " % (v, gruppo, nome) + testo
    gc.scrivi(p, testo)
    return p


def main(argv):
    in_piu = []
    if len(argv) > 1:
        for r in open(argv[1]):
            if r.strip() and not r.startswith("#"):
                pos, m = r.split()
                in_piu.append((pos, m))
    print(g2.verifica_netlist())
    # IL CASO NOTO, prima: il blocco di L60d2
    imposta("l60d2")
    if "D154" in open(SUBCKT["l60d2"]).read():
        sys.exit("RIFIUTATO: varianti/l60d2 ha D154: non e' il blocco di L60d2")
    controllo = []
    for gruppo, nome, testo in casi([], diodi=False):
        if nome in CONTROLLO:
            controllo.append(scrivi_deck("stax_l60d2", nome, testo, "l60d2"))
    if len(controllo) != len(CONTROLLO):
        sys.exit("RIFIUTATO: %d casi noti su %d" % (len(controllo), len(CONTROLLO)))
    # il banco di oggi
    imposta("oggi")
    lista = []
    for gruppo, nome, testo in casi(in_piu):
        p = scrivi_deck(gruppo, nome, testo, "oggi")
        if p not in lista:
            lista.append(p)
    gc.SUBCKT = SUBCKT["oggi"]
    gc.scrivi(os.path.join(L, "deck", "lista_stax.txt"), "\n".join(lista) + "\n")
    gc.scrivi(os.path.join(L, "deck", "lista_stax_controllo.txt"), "\n".join(controllo) + "\n")
    print("stax: %d deck (%d modi), controllo: %d deck"
          % (len(lista), len(modi(in_piu)), len(controllo)))


if __name__ == "__main__":
    main(sys.argv)
