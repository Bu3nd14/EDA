#!/usr/bin/env python3
"""L60d2: perche' alcuni guasti del blocco A sulla Stax durano piu' che in L60c2 (Q122 in corto da
5,9 a 118 ms, JQ110A in corto da 78 a 124, D102 aperto da 95 a 125), pur restando sotto 150 ms.
Le stesse corse (A, condensatore nominale) con tre blocchi:
  oggi     la copia guasta del blocco di oggi (= il banco, per controllo)
  r153_1   la stessa con R153 a 1 ohm: l'inseguitore senza il limite di ADR-087
  l45a     la copia di L45a/inc: il blocco senza ridondanza e senza R153 (= L60c2)
E la corsa ferma a 0,304 s (JQ110B aperta, A, nominale) rifatta col metodo gear.
Solo stdlib, /usr/bin/python3 -I.

Uso: diagnosi_peggio.py   -> deck/diagnosi/*.cir, inc_diagnosi/, deck/lista_diagnosi.txt
"""
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
import genera_L60d2 as g  # noqa: E402

L = g.L60D2
MODI = ("Q122_ce", "JQ110A_ds", "D102_ap")
INC_D = os.path.join(L, "inc_diagnosi")
REL_D = "@REPO@/%s/" % os.path.relpath(INC_D, g.gc.ROOT)
lista = []


def deck(nome, modo, gear, inc):
    t = g.gc.deck_tr("A", 0, modo, False, False, tfine=g.g2.T_FINE, gear=gear)
    t = g.g1.rinomina(g.g1.applica(t, "G0", 1.0), nome)
    assert t.count(g.INC_L45A) == 1
    t = t.replace(g.INC_L45A, inc)
    p = os.path.join(L, "deck", "diagnosi", nome + ".cir")
    g.gc.scrivi(p, "L60d2 diagnosi %s - " % nome + t)
    lista.append(p)


for m in MODI:
    deck("A_%s_oggi" % m, m, False, g.INC_REL)
    testo = g.gc.subckt_guasto(m).splitlines()
    k = [i for i, r in enumerate(testo) if r.split()[:1] == ["R153"]]
    assert len(k) == 1
    testo[k[0]] = "* L60d2 diagnosi: R153 a 1 ohm\n" + testo[k[0]].replace(" 4.7k", " 1")
    g.gc.scrivi(os.path.join(INC_D, "r153_1", m + ".subckt"), "\n".join(testo) + "\n")
    deck("A_%s_r153_1" % m, m, False, REL_D + "r153_1/")
    deck("A_%s_l45a" % m, m, False, g.INC_L45A)
deck("A_JQ110B_as_gear", "JQ110B_as", True, g.INC_REL)
g.gc.scrivi(os.path.join(L, "deck", "lista_diagnosi.txt"), "\n".join(lista) + "\n")
print("%d deck" % len(lista))
