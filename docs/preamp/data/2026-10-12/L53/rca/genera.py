#!/usr/bin/env python3
"""L53 (NC-059): l'RCA inserito a caldo sull'ingresso selezionato.

Inserendo un cavo RCA, il polo caldo tocca prima della massa. Il deck ha la catena di un canale
(selettore di ADR-064, A, una fissa col suo buffer, trim 0 dB, C_T, bilanciamento al centro,
volume, B) come L53/catena, e davanti la sorgente col suo cavo:

  VMAINS (115 V RMS 50 Hz) --CY-- SG --SWG-- massa del preamp     (la massa della sorgente)
  SG -- VOFF (continua d'uscita della sorgente) -- RS 1,5 Ohm -- SO --SWT-- JIN (R_J 10 M a massa)

SWT (il polo caldo) chiude a 50 ms, SWG (la massa) a 50 ms + DT. Ipotesi dichiarate:
  - sorgente a terra (CY ~ 0): conta solo la continua d'uscita VOFF, 10 mV (tipica) e 0,65 V (il
    limite di ADR-066);
  - sorgente in classe II (spina a due poli): la massa galleggia a meta' rete attraverso i
    condensatori Y dell'alimentatore, CY 1 nF (tipico) e 3,46 nF (la corrente di contatto di
    0,25 mA a 230 V, il limite delle norme per la classe II, come capacita' equivalente);
  - DT 10 ms (la mano); il contatto: switch ron 0,1 Ohm, roff 1 GOhm (tb_f1_selettore.cir).
Volume in cima e alla posizione d'ascolto del K11 (-29 dB, ADR-001); modo 0 e +10 dB.

Misure: il picco di v(main) e v(fixjack1) da 50 ms a fine corsa, e il picco nel solo intervallo
prima della massa. In dB SPL a 1 m con la catena di NC-028 (finale x21,1, Heresy 96 dB/1 W/1 m):
SPL = 96 + 20 log10(Vpk x 21,1 / (2,83 x sqrt 2)), limitato dal clip del finale (30 W su 8 Ohm,
21,9 V di picco: ~114 dB SPL).

Uso: /usr/bin/python3 genera.py -> rca.cir
"""
import os

QUI = os.path.dirname(os.path.abspath(__file__))
VOL = {"cima": ("1m", "10k"), "k11": ("9645", "355")}       # -29 dB: 355 / 10 k = 0,0355
MODI = {0: ("1G", "1G"), 10: ("0.1", "0.1")}
CASI = [("terra_10mV", "1e-18", "0.01"), ("terra_650mV", "1e-18", "0.65"),
        ("classeII_1n", "1n", "0.01"), ("classeII_3n46", "3.46n", "0.01")]

TESTA = """rca - L53: l'RCA inserito a caldo sull'ingresso selezionato (NC-059)
* generato da L53/rca/genera.py
.include @REPO@/models/jfet/lsk489.lib
.include @REPO@/models/bjt_npn/mmbt5551.lib
.include @REPO@/models/bjt_pnp/mmbt5401.lib
.include @REPO@/models/bjt_npn/mje15032.lib
.include @REPO@/models/bjt_pnp/mje15033.lib
.include @REPO@/models/diodes/1n4148.lib
.include @REPO@/models/bjt_pnp/ls350.lib
.include @REPO@/spice/preamp/gain_block.subckt

VPP VPLUS 0 DC 15
VMM VMINUS 0 DC -15
.model swk sw vt=0.5 vh=0.1 ron=0.1 roff=1e9

* la sorgente e il suo cavo
VMAINS VMN 0 SIN(0 162.6 50)
CY  VMN SG 1n
RSG SG 0 1e12
VCG CG 0 PULSE(0 1 60m 1u 1u 1 2)
SWG SG 0 CG 0 swk
VOFF SG SOI DC 0.01
RS  SOI SO 1.5
VCT CT 0 PULSE(0 1 50m 1u 1u 1 2)
SWT SO JIN CT 0 swk
* il selettore (ADR-064)
RJ    JIN 0 10Meg
CIN   JIN SEL 1u
RSEL  SEL 0 470k
RKSEL SEL AIN 0.1
CSEL  AIN 0 68p
XA AIN AOUT AFB ARG ARG10 VPLUS VMINUS GAINBLOCK
RARG   ARG   0 1G
RARG10 ARG10 0 1G
* una fissa (ADR-023), col carico della Stax
XF1 AOUT F1OUT F1FB F1RG F1RG10 VPLUS VMINUS GAINBLOCK
RF1RG   F1RG   0 1G
RF1RG10 F1RG10 0 1G
RSEP1 F1OUT FIX1 47
CFIX1 FIX1 FIXJACK1 4.7u
RBL1  FIXJACK1 0 470k
RLD1  FIXJACK1 0 50k
* trim 0 dB, C_T, bilanciamento al centro, volume (come L53/catena)
RT1R AOUT ATOP 0.1
RL1 AOUT 0 1773
CT    ATOP ATT 10u
CWIRE ATT 0 100p
RBAL  ATT 0 50k
RATTH ATT BIN 1m
RATTL BIN 0 10k
XB BIN BOUT BFB BRG BRG10 VPLUS VMINUS GAINBLOCK
CSTB    BRG   0 15p
RRGB    BRG   0 1G
CSTB10  BRG10 0 15p
RRG10B  BRG10 0 1G
RISO   BOUT BOUTA 47
COUT   BOUTA MAIN 4.7u
RBLEED MAIN 0 220k
RLOAD  MAIN 0 100k
.options reltol=1e-4 abstol=1e-12 vntol=1e-7

.control
option itl1=1000
set numdgt=6
echo "caso,vol,modo,main_pk_v,main_pk_prima_massa_v,fix_pk_v,ain_pk_v" > rca.csv
"""
CASO = """alter cy = {cy}
alter voff = {voff}
alter rattH = {rh}
alter rattL = {rl}
alter rrgb = {rrg}
alter rrg10b = {rrg10}
tran 10u 0.4 0 10u
meas tran mpk max abs_main from=50.0m to=0.4
meas tran mpre max abs_main from=50.0m to=60m
meas tran fpk max abs_fix from=50.0m to=0.4
meas tran apk max abs_ain from=50.0m to=0.4
echo "L53_RCA caso={caso} vol={vol} modo={modo}"
echo "{caso},{vol},{modo},$&mpk,$&mpre,$&fpk,$&apk" >> rca.csv
destroy all
"""
s = TESTA
for caso, cy, voff in CASI:
    for vol, (rh, rl) in VOL.items():
        for m, (rrg, rrg10) in MODI.items():
            s += CASO.format(cy=cy, voff=voff, rh=rh, rl=rl, rrg=rrg, rrg10=rrg10, caso=caso,
                             vol=vol, modo=m)
s += ".endc\n.end\n"
# le misure col modulo: vettori derivati prima di meas
s = s.replace("tran 10u 0.4 0 10u\n",
              "tran 10u 0.4 0 10u\nlet abs_main = abs(v(main))\nlet abs_fix = abs(v(fixjack1))\nlet abs_ain = abs(v(ain))\n")
open(os.path.join(QUI, "rca.cir"), "w").write(s)
print("rca.cir: %d casi" % (len(CASI) * len(VOL) * len(MODI)))
