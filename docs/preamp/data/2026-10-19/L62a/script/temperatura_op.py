#!/usr/bin/env python3
"""L62a: il riposo dei finali a temperatura uniforme 27 / 60 / 90 C, per ogni variante e per i guasti
delle parti nuove che restano a blocco acceso (non si vedono al jack). La domanda: la guardia o i
diodi rubano corrente al moltiplicatore quando scaldano? E un diodo in corto lascia tre diodi che
a caldo conducono? Il banco e' tb_op (blocco B, inseguitore, 47 ohm + 4,7 uF + 100 k) con un'istanza
X del subckt della variante; il guasto e' una riga cambiata. Temperatura uniforme: un limite
grossolano (i diodi e la guardia non sono accoppiati ai finali; i finali sono a ~79 C con 60 C
d'aria), dichiarato.

Uso: temperatura_op.py   -> deck/temperatura/<caso>.cir, deck/lista_temperatura.txt
     temperatura_op.py leggi -> temperatura.csv
"""
import csv
import os
import re
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L62A = os.path.dirname(QUI)
sys.path.insert(0, QUI)
import genera_L62a as g  # noqa: E402

TEMP = (27, 60, 90)
CASI = {
    "base": ("base", None),
    "guardia": ("guardia", None),
    "diodi": ("diodi", None),
    "limite": ("limite", None),
    "diodi_D163_cc": ("diodi", ("D163 NDC3 NY D1N914", "D163 NDC3 NY D1N914\nRFLT NDC3 NY 1m")),
    "guardia_R162_ap": ("guardia", ("R162 NBG NY 1k\n", "")),
    "guardia_R161_cc": ("guardia", ("R161 NX NBG 2.7k", "R161 NX NBG 1m")),
    "guardia_Q160_ce": ("guardia", ("Q160 NX NBG NY MMBT5551", "Q160 NX NBG NY MMBT5551\nRFLT NX NY 1m")),
}
BANCO = """VPP VPLUS 0 DC 15
VMM VMINUS 0 DC -15
XB 0 OUT FB RG RG10 VPLUS VMINUS GB
CS RG 0 15p
RL RG 0 1G
CS2 RG10 0 15p
RL2 RG10 0 1G
RISO OUT OUTA 47
COUT OUTA JACK 4.7u
RB JACK 0 220k
RLD JACK 0 100k
.control
option itl1=1000
"""


def deck(caso):
    v, mod = CASI[caso]
    t = open(os.path.join(L62A, "varianti", v, "gain_block.subckt")).read()
    if mod:
        if t.count(mod[0]) != 1:
            sys.exit("RIFIUTATO: %s non trova %r" % (caso, mod[0]))
        t = t.replace(mod[0], mod[1])
    t = t.replace(".subckt GAINBLOCK ", ".subckt GB ").replace(".ends GAINBLOCK", ".ends GB")
    c = "L62a temperatura %s\n" % caso + "".join(r for r in g.gc.MODELLI.splitlines(True) if "gain_block" not in r)
    c += t + BANCO
    for T in TEMP:
        c += ("option temp=%d\nop\necho \"L62A_T %d\"\nprint i(vpp) @q.xb.q132[ic] @q.xb.q133[ic] v(xb.nx)-v(xb.ny) "
              "@q.xb.q127[ic] v(out)\n") % (T, T)
    return c + "quit\n.endc\n.end\n"


def leggi():
    out = []
    for caso in CASI:
        log = os.path.join(L62A, "run", "temperatura", caso, caso + ".log")
        t = open(log).read()
        bad = "source stepping failed" in t
        for blocco in t.split("L62A_T ")[1:]:
            T = int(blocco.split()[0])
            v = dict(re.findall(r"^(\S+) = (\S+)", blocco, re.M))
            out.append({"caso": caso, "T_C": T, "stato": "NON CONVERGE" if bad else "ok",
                        "I_rail_piu_mA": "%.2f" % (-float(v["i(vpp)"]) * 1e3),
                        "Iq_npn_mA": "%.2f" % (float(v["@q.xb.q132[ic]"]) * 1e3),
                        "Iq_pnp_mA": "%.2f" % (-float(v["@q.xb.q133[ic]"]) * 1e3),
                        "spread_V": "%.4f" % float(v["v(xb.nx)-v(xb.ny)"]),
                        "Ic_Q127_mA": "%.2f" % (float(v["@q.xb.q127[ic]"]) * 1e3),
                        "out_mV": "%.2f" % (float(v["v(out)"]) * 1e3)})
    with open(os.path.join(L62A, "temperatura.csv"), "w", newline="") as fo:
        w = csv.DictWriter(fo, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    for r in out:
        print("  ".join("%s=%s" % kv for kv in r.items()))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "leggi":
        leggi()
    else:
        lista = [g.scrivi(os.path.join(L62A, "deck", "temperatura", c + ".cir"), deck(c)) for c in CASI]
        g.scrivi(os.path.join(L62A, "deck", "lista_temperatura.txt"), "\n".join(lista) + "\n")
        print("temperatura: %d deck" % len(lista))
