#!/usr/bin/env python3
"""L55, ESPLORAZIONE - nessun valore del sorgente cambia (NC-056).

Copia di L46a/script/varianti.py ridotta a quello che serve qui: scrive in
../inc/<variante>.inc una copia di spice/preamp/gain_block_flat.inc (il blocco
generato di oggi: MJE15032/33, C124 470p, R128 1,58k, ADR-054/067/068/095/099)
con le modifiche della variante:
  ("set", "Q132", "Q132 VPLUS NBN NEN <modello>")  sostituisce la riga
  ("add", ".include ...")                            aggiunge una riga in coda

La prima riga di ogni .inc dice da dove viene e cosa cambia (#29).

Varianti:
  mje                     il blocco di oggi, nessuna modifica: il CONTROLLO, deve
                          ridare la regressione di L56 / L45d2b3b2b2
  <cand>_r<R>             il candidato, R128 spazzata sulla corrente di riposo
  <cand>                  il candidato con la R128 tarata
  <cand>_cm<C>            il candidato col Miller C124 piu' basso

Uso: /usr/bin/python3 -I varianti.py [variante...]   (nessun argomento: tutte)
"""
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L55 = os.path.dirname(QUI)
ROOT = os.path.abspath(os.path.join(L55, *[".."] * 5))
SRC = os.path.join(ROOT, "spice", "preamp", "gain_block_flat.inc")

# I candidati: (lib NPN, lib PNP, modello NPN, modello PNP, R128 tarata).
# L'include sta nel .inc con un percorso relativo alla cartella inc/
# (run_simulation.sh risolve @REPO@ solo nel deck), come i ZXT di L46a.
CANDIDATI = {}


def miller(c):
    return [("set", "C124", "C124 NX NHI %s" % c)]


def finale(npn_lib, pnp_lib, npn_mod, pnp_mod, rbb):
    """I finali Q132/Q133 sostituiti; R128 (rbb) si ritara sulla corrente di
    riposo (~20,5 mA, ADR-042 / ADR-054): la Vbe del candidato non e' quella
    dei MJE. Base stopper, 22 Ohm, diodi di ADR-095 restano."""
    return [("add", ".include ../../../../../../models/bjt_npn/%s" % npn_lib),
            ("add", ".include ../../../../../../models/bjt_pnp/%s" % pnp_lib),
            ("set", "Q132", "Q132 VPLUS NBN NEN %s" % npn_mod),
            ("set", "Q133", "Q133 VMINUS NBP NEP %s" % pnp_mod),
            ("set", "R128", "R128 NX NBB %s" % rbb)]


VARIANTI = {"mje": [],
             # spiegazione del controllo: V1 di oggi contro L56 senza i diodi di ADR-095
             "mje_senza_d158d159": [("del", "D158"), ("del", "D159")]}
for nome, (nl, pl, nm, pm, rbb, sweep, cms) in CANDIDATI.items():
    for r in sweep:
        VARIANTI["%s_r%s" % (nome, r)] = finale(nl, pl, nm, pm, r)
    VARIANTI[nome] = finale(nl, pl, nm, pm, rbb)
    for cm in cms:
        VARIANTI["%s_cm%s" % (nome, cm)] = finale(nl, pl, nm, pm, rbb) + miller(cm)


def applica(nome, mods):
    righe = open(SRC).read().rstrip("\n").split("\n")
    for op, *arg in mods:
        if op == "add":
            righe.append(arg[0])
            continue
        dev = arg[0]
        idx = [i for i, r in enumerate(righe) if r.split()[:1] == [dev]]
        if len(idx) != 1:
            sys.exit("%s: %s %s trovato %d volte" % (nome, op, dev, len(idx)))
        if op == "set":
            righe[idx[0]] = arg[1]
        else:
            del righe[idx[0]]
    desc = "; ".join("%s %s" % (op, " | ".join(a)) for op, *a in mods) or "nessuna modifica"
    testa = ["* L55 ESPLORAZIONE, variante %s, da spice/preamp/gain_block_flat.inc: %s"
             % (nome, desc)]
    d = os.path.join(L55, "inc")
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, nome + ".inc")
    open(p, "w").write("\n".join(testa + righe) + "\n")
    return p


nomi = sys.argv[1:] or sorted(VARIANTI)
for n in nomi:
    print(applica(n, VARIANTI[n]))
