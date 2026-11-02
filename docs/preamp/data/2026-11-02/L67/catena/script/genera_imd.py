#!/usr/bin/env python3
"""L67 (NC-055): l'intermodulazione CCIF sulla catena, il prodotto che cade in banda.

La THD fuori dai tetti sulla catena e' seconda armonica di un tono a 20 kHz, cioe' a 40 kHz. Il
CCIF (V4, ADR-055: toni uguali a 19 + 20 kHz, picco composto di 0,2 V RMS, prodotto a 1 kHz
<= -110 dB contro un tono) mette lo stesso meccanismo a 1 kHz. Il metodo e' quello del banco del
blocco (L66/script/genera_imd.py, imd()): ciascun tono a picco/2, transitorio 3 ms a 20 ns,
fourier a 1 kHz (il tono a 20 kHz e' l'armonica 20).

Il circuito e' quello dei deck della catena gia' generati (genera.py: la testa di
deck/<blocco>/catena_20k_lo.cir fino a `.control`, con i nodeset e il .temp), salvo la sorgente:
due generatori in serie al posto di VS. Un deck per (blocco, volume, sorgente), i tre modi dentro;
saltati i casi che chiedono al blocco A piu' di 2,7 V RMS di picco composto.

Uso: /usr/bin/python3 -I genera_imd.py <blocco>... -> ../deck/imd_<blocco>/*.cir, ../deck/lista_imd.txt
"""
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(QUI)
MODI = {0: ("1G", "1G", 1.0), 3: ("0.1", "1G", 1.4202), 10: ("0.1", "0.1", 3.1523)}
VOL = {"cima": ("1m", "10k", 1.0), "meta": ("5k", "5k", 0.5),
       "m10": ("6800", "3200", 0.32), "m20": ("9000", "1000", 0.1)}   # come genera.py
PICCO = 0.2 * 2 ** 0.5      # picco composto alla principale, V (ADR-055)
CASO = """alter rsrc = {rs}
alter rrgb = {rrg}
alter rrg10b = {rrg10}
alter rattH = {rh}
alter rattL = {rl}
alter @vs1[sin] = [ 0 {a} 19000 ]
alter @vs2[sin] = [ 0 {a} 20000 ]
tran 0.02u 0.003 0 0.02u
echo "L67_IMD modo={modo} vol={vol} rs={rs} ampin={a} picco_main={p}"
fourier 1000 v(vsn) v(bout) v(f1out)
destroy all
"""

lista = []
for blocco in sys.argv[1:]:
    sorg = os.path.join(BASE, "deck", blocco, "catena_20k_lo.cir")
    testa = open(sorg).read().split(".control\n")[0]
    vs = "VS VSN 0 SIN(0 0.282843 20000)"
    if testa.count(vs) != 1:
        raise SystemExit("%s: la riga della sorgente non e' quella attesa" % sorg)
    testa = testa.replace(vs, "VS1 VSN VMIDS SIN(0 0.0707107 19000)\nVS2 VMIDS 0 SIN(0 0.0707107 20000)")
    testa = testa.replace(" - L67: V4 sulla catena", " - L67: IMD CCIF sulla catena (da)", 1)
    d = os.path.join(BASE, "deck", "imd_" + blocco)
    os.makedirs(d, exist_ok=True)
    for vol, (rh, rl, att) in VOL.items():
        for rs in ("1.5", "2500"):
            s = testa + (".control\noption itl1=1000\nset numdgt=10\nset fourgridsize=16384\n"
                         "set nfreqs=24\nsave vsn bout f1out\n")
            n = 0
            for m, (rrg, rrg10, g) in MODI.items():
                a = PICCO / 2 / (g * att)
                if 2 * a > 2.7 * 2 ** 0.5:
                    continue
                s += CASO.format(rs=rs, rrg=rrg, rrg10=rrg10, rh=rh, rl=rl, a="%.6g" % a, modo=m,
                                 vol=vol, p="%.6g" % PICCO)
                n += 1
            if not n:
                continue
            s += ".endc\n.end\n"
            p = os.path.join(d, "imd_%s_rs%s.cir" % (vol, rs.replace(".", "p")))
            open(p, "w").write(s)
            lista.append(p)
open(os.path.join(BASE, "deck", "lista_imd.txt"), "w").write("\n".join(lista) + "\n")
print("%d deck" % len(lista))
