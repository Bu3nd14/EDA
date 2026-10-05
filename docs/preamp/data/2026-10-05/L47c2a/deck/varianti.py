#!/usr/bin/env python3
"""L47c2a: the VRELAY hold-up with a smaller reservoir (C520), for the user's choice.

Solo stdlib. /usr/bin/python3 varianti.py
For each value, L47c2a's rete deck (rete/tb_psu_rete.cir, generated from
today's psu.net) copied into varianti/c<value>/ with only two changes: C520's
value (derated -20 % and with its ESR, as genera_tb_psu.py writes every
polarised capacitor) and the wrdata paths. Run ngspice in each folder, then
analizza.py on it, as for rete/.
"""
import os

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
SRC = os.path.join(L, "rete", "tb_psu_rete.cir")
testo = open(SRC).read()
VECCHIA = "CC520 raw_v c520_esr {0.8*4700u}"
assert testo.count(VECCHIA) == 1, "C520 non e' quello atteso nel deck rete"
assert testo.count(os.path.join(L, "rete") + "/") == 6, "i percorsi di wrdata non sono sei"
for c in ("3300u", "2200u"):
    d = os.path.join(L, "varianti", "c" + c)
    os.makedirs(d, exist_ok=True)
    t = testo.replace(VECCHIA, "CC520 raw_v c520_esr {0.8*%s}" % c)
    t = t.replace(os.path.join(L, "rete") + "/", d + "/")
    t = t.replace("* L47c2a tb_psu rete", "* L47c2a tb_psu rete, VARIANT C520 = %s," % c, 1)
    open(os.path.join(d, "tb_psu_rete_c%s.cir" % c), "w").write(t)
    print("scritto", os.path.join(d, "tb_psu_rete_c%s.cir" % c))
