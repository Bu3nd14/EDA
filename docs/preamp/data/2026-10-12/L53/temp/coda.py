#!/usr/bin/env python3
"""L53 (NC-058): la THD a 20 kHz del blocco contro la corrente di coda, a 27 e 57 °C.

La sonda (sonda.py) dice che la crescita a 57 °C viene da Q106, il generatore di coda: tenuto a
27 °C la THD torna quella di 27 °C. op_temp.cir dice che la coda passa solo da 4,51 a 4,39 mA.
Qui la coda si muove a mano, con R107 (137 Ohm), a temperatura fissa: se pochi punti percentuali
di coda valgono un fattore 4 di THD, la cifra di 27 °C sta su un annullamento stretto.

R107: -10 % ... +10 % in sette punti; per ogni punto la corrente di coda letta da un `op`.
Il caso: thd_20k a 0 dB, sorgente 2,5 kOhm, 0,2 V e 2 V (il banco di V4).

Uso: /usr/bin/python3 coda.py  -> deck/coda/coda_t27.cir, coda_t57.cir, deck/lista_coda.txt
"""
import os

QUI = os.path.dirname(os.path.abspath(__file__))
DECK = os.path.join(QUI, "deck", "coda")
R107 = [123.3, 130.2, 133.6, 137, 140.5, 144, 150.7]

TESTA = """coda_t{t} - L53: THD a 20 kHz contro R107 (la corrente di coda) a {t} gradi (NC-058)
* generato da L53/temp/coda.py
.include @REPO@/models/jfet/lsk489.lib
.include @REPO@/models/bjt_npn/mmbt5551.lib
.include @REPO@/models/bjt_pnp/mmbt5401.lib
.include @REPO@/models/bjt_npn/mje15032.lib
.include @REPO@/models/bjt_pnp/mje15033.lib
.include @REPO@/models/diodes/1n4148.lib
.include @REPO@/models/bjt_pnp/ls350.lib
.include @REPO@/spice/preamp/gain_block_flat.inc

VPP VPLUS 0 DC 15
VMM VMINUS 0 DC -15
VS VSN 0 SIN(0 0.282843 20000)
RSRC VSN IN 2500
CSTRAY RG 0 15p
CSTRAY10 RG10 0 15p
RRG RG 0 1G
RRG10 RG10 0 1G
RISO OUT OUTA 47
COUT OUTA JACK 4.7u
RBLEED JACK 0 220k
RLOAD JACK 0 10k
.temp {t}
.options reltol=1e-6 abstol=1e-15 vntol=1e-9

.control
option itl1=1000
set numdgt=10
set fourgridsize=8192
set nfreqs=10
"""
CASO = """alter r107 = {r}
op
echo "L53_CODA r107={r}"
print @q106[ic] @jq110a[id] @jq110b[id] v(out)
destroy all
alter @vs[sin] = [ 0 {a} 20000 ]
save out vsn
tran 2e-08 0.0021 0 2e-08
echo "L46A_CASO modo=0 livello={liv} freq=20000 ampin={a} rs=2500 r107={r}"
fourier 20000 v(vsn) v(out)
destroy all
"""

os.makedirs(DECK, exist_ok=True)
lista = []
for t in (27, 57):
    s = TESTA.format(t=t)
    for r in R107:
        for liv, a in (("lo", 0.282843), ("hi", 2.82843)):
            s += CASO.format(r=r, a=a, liv=liv)
    s += ".endc\n.end\n"
    p = os.path.join(DECK, "coda_t%d.cir" % t)
    open(p, "w").write(s)
    lista.append(p)
open(os.path.join(QUI, "deck", "lista_coda.txt"), "w").write("\n".join(lista) + "\n")
print("%d deck" % len(lista))
