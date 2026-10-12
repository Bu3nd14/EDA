#!/usr/bin/env python3
"""L53 (NC-059): durante l'RCA a caldo da una sorgente in classe II, che cosa vedono i gate del
blocco A. Dal deck rca.cir (genera.py), i soli casi in classe II al volume in cima, con le
misure dentro il blocco: v(xa.g1) - v(xa.g2) (il gate-gate del LSK489: rottura ±30 V minimo,
±45 tipico, datasheet p. 2), v(xa.g1) - v(xa.s1) (gate-source: -60 V minimo), e la corrente nel
gate d'ingresso (R108, 100 Ohm; IG(F) massimo 10 mA).

Uso: /usr/bin/python3 gate.py -> gate.cir
"""
import os

QUI = os.path.dirname(os.path.abspath(__file__))
testo = open(os.path.join(QUI, "rca.cir")).read()
testa, corpo = testo.split(".control", 1)
testa = testa.replace(testa.split("\n")[0], "gate - L53: i gate del blocco A durante l'RCA a caldo in classe II (NC-059)", 1)
s = testa + """.control
option itl1=1000
set numdgt=6
echo "cy,modo,gg_max_v,gg_min_v,gs_max_v,gs_min_v,ig_max_ma,ig_min_ma" > gate.csv
"""
for cy in ("1n", "3.46n"):
    for modo, (rrg, rrg10) in ((0, ("1G", "1G")), (10, ("0.1", "0.1"))):
        s += """alter cy = {cy}
alter voff = 0.01
alter rattH = 1m
alter rattL = 10k
alter rrgb = {rrg}
alter rrg10b = {rrg10}
tran 10u 0.12 0 10u
let gg = v(xa.g1) - v(xa.g2)
let gs = v(xa.g1) - v(xa.s1)
let ig = (v(ain) - v(xa.g1)) / 100 * 1000
meas tran ggmax max gg from=50m to=0.12
meas tran ggmin min gg from=50m to=0.12
meas tran gsmax max gs from=50m to=0.12
meas tran gsmin min gs from=50m to=0.12
meas tran igmax max ig from=50m to=0.12
meas tran igmin min ig from=50m to=0.12
echo "L53_GATE cy={cy} modo={modo}"
echo "{cy},{modo},$&ggmax,$&ggmin,$&gsmax,$&gsmin,$&igmax,$&igmin" >> gate.csv
destroy all
""".format(cy=cy, modo=modo, rrg=rrg, rrg10=rrg10)
s += ".endc\n.end\n"
open(os.path.join(QUI, "gate.cir"), "w").write(s)
print("gate.cir")
