#!/usr/bin/env python3
"""L46a, ESPLORAZIONE - nessun valore del sorgente cambia.

Scrive in ../inc/<variante>.inc una copia di spice/preamp/gain_block_flat.inc
(il blocco generato, C124 1n, ADR-042) con le modifiche della variante:
  ("set", "C124", "C124 NX NHI 680p")  sostituisce la riga del dispositivo
  ("del", "R130")                      toglie la riga
  ("add", "QD1 VPLUS NX ND1 MMBT5551") aggiunge una riga in coda
I nomi nuovi non collidono con quelli del blocco (#24): QD*, RD*, CT*, RT*, N*D*.

La prima riga di ogni .inc dice da dove viene e cosa cambia, cosi' un log che lo
include lo dichiara (#29).

Uso: /usr/bin/python3 varianti.py [variante...]   (nessun argomento: tutte)
"""
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L46A = os.path.dirname(QUI)
ROOT = os.path.abspath(os.path.join(L46A, *[".."] * 5))
SRC = os.path.join(ROOT, "spice", "preamp", "gain_block_flat.inc")


def miller(c):
    return [("set", "C124", "C124 NX NHI %s" % c)]


def driver(rbb, rdd="330"):
    """Inseguitore complementare fra il VAS e i MJE (la strada b del piano).

    QD1/QD2 isolano il nodo del VAS (NX/NY) dalla CJE dei MJE (3,06 nF, ADR-042):
    i MJE vedono l'emettitore di un MMBT, non il collettore del VAS. RD12 fra gli
    emettitori dei driver fissa la loro corrente (~2,0 V / 330 = ~6 mA). Il
    moltiplicatore di Vbe deve ora coprire 4 Vbe: R128 (rbb) si spazza per
    riportare la corrente di riposo d'uscita a ~20,3 mA (ADR-042)."""
    return [
        ("del", "R130"), ("del", "R131"),
        ("set", "R128", "R128 NX NBB %s" % rbb),
        ("add", "QD1 VPLUS NX ND1 MMBT5551"),
        ("add", "QD2 VMINUS NY ND2 MMBT5401"),
        ("add", "RD12 ND1 ND2 %s" % rdd),
        ("add", "R130 ND1 NBN 10"),
        ("add", "R131 ND2 NBP 10"),
    ]


def vas(r):
    """Corrente del VAS: la degenerazione R123 e il pozzo R126 restano uguali
    (clipping simmetrico, commento del VAS in gain_block.py): 0,55 V / r."""
    return [("set", "R123", "R123 VPLUS NVE %s" % r),
            ("set", "R126", "R126 NVLE VMINUS %s" % r)]


def tpc(c1, c2, rt):
    """Compensazione a due poli: C124 diviso in due in serie, RT dal punto
    centrale a massa (massa AC; i condensatori bloccano la continua)."""
    return [("set", "C124", "C124 NX NTPC %s" % c1),
            ("add", "CT2 NTPC NHI %s" % c2),
            ("add", "RT1 NTPC 0 %s" % rt)]


VARIANTI = {
    # a. solo Miller (la griglia di L40, ora misurata anche in distorsione)
    "cm1n": miller("1n"),          # controllo: il blocco di oggi, invariato
    "cm470p": miller("470p"),      # controfattuale: L39
    "cm680p": miller("680p"),
    "cm820p": miller("820p"),
}

# b. il driver: prima la taratura della corrente di riposo, poi il Miller
for rbb in ("3.4k", "3.48k", "3.6k", "3.9k", "4.22k", "4.53k", "4.87k"):
    VARIANTI["drv_r%s_cm1n" % rbb] = driver(rbb) + miller("1n")
# R128 3,48k: ~20,3 mA d'uscita come oggi (taratura sopra, run/drv_r*/tb_op)
for cm in ("680p", "470p", "330p", "220p"):
    VARIANTI["drv_cm%s" % cm] = driver("3.48k") + miller(cm)

# c. il VAS a ~10 mA (56 Ohm: 0,55 V / 56 = 9,8 mA), da solo e col driver
# Col VAS a 10,7 mA la corrente d'uscita sale (22,4 mA a R128 1,69k; 24,2 col driver
# e 3,48k): R128 riportato a ~20,3 mA, 1,58k da solo e 3,24k col driver
R128_VAS = [("set", "R128", "R128 NX NBB 1.58k")]
for cm in ("1n", "680p", "470p", "390p", "330p"):
    VARIANTI["vas56_cm%s" % cm] = vas("56") + R128_VAS + miller(cm)
for cm in ("470p", "330p", "220p"):
    VARIANTI["drv_vas56_cm%s" % cm] = driver("3.24k") + vas("56") + miller(cm)


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
    desc = "; ".join("%s %s" % (op, " | ".join(a)) for op, *a in mods)
    testa = ["* L46a ESPLORAZIONE, variante %s, da spice/preamp/gain_block_flat.inc: %s"
             % (nome, desc)]
    d = os.path.join(L46A, "inc")
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, nome + ".inc")
    open(p, "w").write("\n".join(testa + righe) + "\n")
    return p


nomi = sys.argv[1:] or sorted(VARIANTI)
for n in nomi:
    print(applica(n, VARIANTI[n]))
