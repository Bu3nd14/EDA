#!/usr/bin/env python3
"""L45d2b3b1: P7 con R153 in corto, sul blocco di oggi (coi diodi di ADR-090 e ADR-095). Solo stdlib,
/usr/bin/python3 -I.

Uso: genera_p7.py    scrive varianti/<v>/, deck/p7_<v>/tb_mute_corto.cir, deck/lista_p7.txt

Il deck e' spice/preamp/tb/tb_mute_corto.cir (invariato da L60d2) con le misure di Q146 / Q148 di
L60d1 (p7_l56.aggiungi) e le giunzioni base-emettitore dei finali e la corrente dei diodi di
L45d2b2c (genera_massimi.vbe_p7), coi rail a +-15 V: P7 e' una condizione d'uso, il rail di un
regolatore sano non dipende dalla rete.

LE VARIANTI (il blocco incluso al posto di spice/preamp/gain_block.subckt)
  oggi          il blocco di oggi, sano: IL CASO NOTO 1, deve ridare p7/tb_cbe_nom_* di L45d2b2c
  r153cc        il blocco di oggi con R153 a 1 ohm: IL GUASTO. 1 ohm e non 1 mOhm: con 1 mOhm il
                banco finisce in un punto di lavoro sbagliato (L60d2, limitations #59)
  l60d2_r153cc  il blocco di L60d2 (commit 4fde9e40) con R153 a 1 ohm: IL CASO NOTO 2, deve ridare
                p7_r153cc.txt di L60d2 (Q146 0,4112 W medi, 2,006 W di picco)
La misura della potenza di R153 di p7_l56 moltiplica per 4700 ohm: sulle varianti in corto non si
chiede (r153=False).
"""
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
DATA = os.path.abspath(os.path.join(L, "..", ".."))
sys.path.insert(0, os.path.join(DATA, "2026-10-21", "L45d2b2c", "script"))
import genera_massimi as gm   # noqa: E402

g62 = gm.g62
g62.L62A = L
g62.REL = os.path.relpath(L, g62.ROOT)
SP = gm.SP
SORGENTE = {"oggi": os.path.join(SP, "gain_block.subckt"),
            "r153cc": os.path.join(SP, "gain_block.subckt"),
            "l60d2_r153cc": os.path.join(L, "varianti", "l60d2", "gain_block.subckt"),
            "r153_meta": os.path.join(SP, "gain_block.subckt")}
# r153_meta: UN'OPZIONE, non il circuito. R153 sdoppiata in due da 2,4 k in serie (E24, 4,8 k in tutto)
# con una delle due in corto: resta 2,4 k fra il collettore di Q146 e il rail negativo
VALORE = {"r153cc": "1", "l60d2_r153cc": "1", "r153_meta": "2.4k"}


def r153_in_corto(t, valore):
    righe = t.split("\n")
    k = [i for i, r in enumerate(righe) if r.split()[:1] == ["R153"]]
    if len(k) != 1 or righe[k[0]].split()[3] != "4.7k":
        sys.exit("RIFIUTATO: R153 da 4,7 k non trovata una volta sola")
    p = righe[k[0]].split()
    righe[k[0]] = "* L45d2b3b1: R153 IN CORTO (resta %s)\nR153 %s %s %s" % (valore, p[1], p[2], valore)
    return "\n".join(righe)


def main():
    lista = []
    for v, src in SORGENTE.items():
        t = open(src).read()
        if v in VALORE:
            t = r153_in_corto(t, VALORE[v])
        g62.scrivi(os.path.join(L, "varianti", v, "gain_block.subckt"), t)
        diodi = "D158" in t
        tb = g62.includi(open(os.path.join(SP, "tb", "tb_mute_corto.cir")).read(), v)
        tb = gm.vbe_p7(g62.p7_l56.aggiungi(tb, r153=(v == "oggi")), diodi=diodi)
        lista.append(g62.scrivi(os.path.join(L, "deck", "p7_" + v, "tb_mute_corto.cir"),
                                "L45d2b3b1 P7 %s %s" % (v, gm.rail(tb, "nom"))))
    if open(os.path.join(L, "varianti", "oggi", "gain_block.subckt")).read() != open(SORGENTE["oggi"]).read():
        sys.exit("RIFIUTATO: varianti/oggi non e' il blocco di oggi")
    g62.scrivi(os.path.join(L, "deck", "lista_p7.txt"), "\n".join(lista) + "\n")
    print("P7: %d deck" % len(lista))


if __name__ == "__main__":
    main()
