#!/usr/bin/env python3
"""L57a (NC-059): l'RCA inserito a caldo sull'ingresso selezionato, sul circuito di oggi e coi rimedi.

Il banco e' quello di L53 (data/2026-10-12/L53/rca/genera.py, gate.py): la catena di un canale
(selettore di ADR-064, A, la fissa del Singxer col suo buffer, trim 0 dB, C_T, bilanciamento al
centro, volume, B) e davanti la sorgente col suo cavo:

  VMAINS (meta' rete di picco, 50 Hz) --CY-- SG --SWG-- massa del preamp   (la massa della sorgente)
  SG -- VOFF -- RS 1,5 Ohm -- SO --SWT-- JIN (R_J 10 M a massa)

SWT (il polo caldo) chiude a 50 ms, SWG (la massa) a 60 ms. Le ipotesi sono quelle di L53, dichiarate
nel suo genera.py: sorgente a terra 10 mV / 0,65 V (ADR-066); in classe II CY 1 nF (tipico) e
3,46 nF (0,25 mA di corrente di contatto a 230 V); la mano 10 ms; il contatto ron 0,1 Ohm.

Due modi:
  l53  - il testo di L53/rca/rca.cir o L53/rca/gate.cir, con il blocco da --blocco al posto di
         spice/preamp/gain_block.subckt. Serve al caso noto (verifica_noto.py lo confronta col
         testo di L53 riga per riga e le corse coi CSV di L53).
  oggi - la catena di oggi: in piu' di L53 R_G 1 MOhm sul gate di B (R165, ADR-065) e le due
         resistenze di scarica lato condensatore (fissa 470 k, R167; principale 220 k, ADR-044),
         che col mute rilasciato stanno in parallelo a quelle del jack. Le misure di L53 e quelle
         di gate.py in una corsa sola, piu' la corrente nei diodi di protezione, quando ci sono.

La protezione (--prot, solo modo oggi), fra il contatto del relè del selettore e l'ingresso del blocco:
  SEL -- RKSEL (contatto) -- NK -- RP -- AIN (= IN del blocco, R113 1 M e R108 100 Ohm dentro)
  diodi: AIN -> VPLUS e VMINUS -> AIN (D1N914 come stand-in; la parte vera e' di L57b), oppure
  verso due sorgenti a +/-VCL (il limitatore a una soglia sotto i rail).
  --prot nessuna | R=<ohm> | R=<ohm>,D=rail | R=<ohm>,D=<volt>

La rete: --rete 0.9 / 1.0 / 1.1 scala VMAINS (meta' rete di picco: 230 V x sqrt2 / 2 = 162,6 V).

Uso: /usr/bin/python3 genera.py <modo> <deck.cir> [--blocco P] [--prot P] [--rete X] [--casi C]
     [--tstop T]    (P relativo alla radice del repo; C: tutti | classeII | l53gate)
"""
import argparse
import os

p = argparse.ArgumentParser()
p.add_argument("modo", choices=("l53", "l53gate", "oggi"))
p.add_argument("deck")
p.add_argument("--blocco", default="spice/preamp/gain_block.subckt")
p.add_argument("--prot", default="nessuna")
p.add_argument("--rete", type=float, default=1.0)
p.add_argument("--casi", default="tutti")
p.add_argument("--tstop", default="0.4")
p.add_argument("--forma", action="store_true",
               help="solo volume in cima e 0 dB, e la forma d'onda in forma_<caso>.txt")
a = p.parse_args()

VOL = {"cima": ("1m", "10k"), "k11": ("9645", "355")}       # -29 dB: 355 / 10 k = 0,0355
MODI = {0: ("1G", "1G"), 10: ("0.1", "0.1")}
CASI = [("terra_10mV", "1e-18", "0.01"), ("terra_650mV", "1e-18", "0.65"),
        ("classeII_1n", "1n", "0.01"), ("classeII_3n46", "3.46n", "0.01")]

# ---------------------------------------------------------------- il testo di L53, verbatim
TESTA_L53 = """rca - L53: l'RCA inserito a caldo sull'ingresso selezionato (NC-059)
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
"""
CTRL_RCA = """
.control
option itl1=1000
set numdgt=6
echo "caso,vol,modo,main_pk_v,main_pk_prima_massa_v,fix_pk_v,ain_pk_v" > rca.csv
"""
CASO_L53 = """alter cy = {cy}
alter voff = {voff}
alter rattH = {rh}
alter rattL = {rl}
alter rrgb = {rrg}
alter rrg10b = {rrg10}
tran 10u 0.4 0 10u
let abs_main = abs(v(main))
let abs_fix = abs(v(fixjack1))
let abs_ain = abs(v(ain))
meas tran mpk max abs_main from=50.0m to=0.4
meas tran mpre max abs_main from=50.0m to=60m
meas tran fpk max abs_fix from=50.0m to=0.4
meas tran apk max abs_ain from=50.0m to=0.4
echo "L53_RCA caso={caso} vol={vol} modo={modo}"
echo "{caso},{vol},{modo},$&mpk,$&mpre,$&fpk,$&apk" >> rca.csv
destroy all
"""
CTRL_GATE = """.control
option itl1=1000
set numdgt=6
echo "cy,modo,gg_max_v,gg_min_v,gs_max_v,gs_min_v,ig_max_ma,ig_min_ma" > gate.csv
"""
CASO_GATE = """alter cy = {cy}
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
"""
INC_L53 = ".include @REPO@/spice/preamp/gain_block.subckt"
INC = ".include @REPO@/" + a.blocco


def l53():
    s = TESTA_L53.replace(INC_L53, INC) + CTRL_RCA.lstrip("\n")
    s = s.replace(".options reltol=1e-4 abstol=1e-12 vntol=1e-7\n",
                  ".options reltol=1e-4 abstol=1e-12 vntol=1e-7\n\n")
    for caso, cy, voff in CASI:
        for vol, (rh, rl) in VOL.items():
            for m, (rrg, rrg10) in MODI.items():
                s += CASO_L53.format(cy=cy, voff=voff, rh=rh, rl=rl, rrg=rrg, rrg10=rrg10,
                                     caso=caso, vol=vol, modo=m)
    return s + ".endc\n.end\n"


def l53gate():
    testa = TESTA_L53.replace(INC_L53, INC)
    testa = testa.replace(testa.split("\n")[0],
                          "gate - L53: i gate del blocco A durante l'RCA a caldo in classe II (NC-059)", 1)
    s = testa + "\n" + CTRL_GATE
    for cy in ("1n", "3.46n"):
        for modo, (rrg, rrg10) in ((0, ("1G", "1G")), (10, ("0.1", "0.1"))):
            s += CASO_GATE.format(cy=cy, modo=modo, rrg=rrg, rrg10=rrg10)
    return s + ".endc\n.end\n"


# ---------------------------------------------------------------- il circuito di oggi
def prot_righe(prot):
    """Le righe fra il contatto del selettore (NK) e l'ingresso del blocco (AIN)."""
    if prot == "nessuna":
        return "RKSEL SEL AIN 0.1\n", False
    d = dict(x.split("=") for x in prot.split(","))
    s = "RKSEL SEL NK 0.1\n* la protezione dell'ingresso (L57a, --prot %s)\nRP NK AIN %s\n" % (prot, d["R"])
    if "D" not in d:
        return s, False
    if d["D"] == "rail":
        alto, basso = "VPLUS", "VMINUS"
    else:
        alto, basso = "VCLP", "VCLN"
        s += "VCLP VCLP 0 DC %s\nVCLN VCLN 0 DC -%s\n" % (d["D"], d["D"])
    # gli amperometri da 0 V danno la corrente in ciascun diodo
    s += ("VIDP AIN DPA DC 0\nDP DPA %s D1N914\n" % alto +
          "VIDN DNK AIN DC 0\nDN %s DNK D1N914\n" % basso)
    return s, True


def oggi():
    testa = TESTA_L53.replace(INC_L53, INC)
    testa = testa.replace(testa.split("\n")[0],
                          "rca - L57a: l'RCA a caldo sul circuito di oggi (NC-059), prot=%s rete=%.2f"
                          % (a.prot, a.rete), 1)
    testa = testa.replace("* generato da L53/rca/genera.py",
                          "* generato da L57a/script/genera.py (dal banco di L53)")
    testa = testa.replace("SIN(0 162.6 50)", "SIN(0 %.4g 50)" % (162.6 * a.rete))
    righe, diodi = prot_righe(a.prot)
    testa = testa.replace("RKSEL SEL AIN 0.1\n", righe)
    # le tre resistenze che il banco di L53 non aveva (preamp_audio.py di oggi)
    testa = testa.replace("RLD1  FIXJACK1 0 50k\n",
                          "RLD1  FIXJACK1 0 50k\nRBC1  FIXJACK1 0 470k\n")
    testa = testa.replace("RATTL BIN 0 10k\n", "RATTL BIN 0 10k\nRGB   BIN 0 1MEG\n")
    testa = testa.replace("RLOAD  MAIN 0 100k\n", "RLOAD  MAIN 0 100k\nRBCM   MAIN 0 220k\n")
    t = a.tstop
    s = testa + """
.control
option itl1=1000
set numdgt=6
echo "caso,vol,modo,rete,main_pk_v,main_pk_prima_massa_v,fix_pk_v,ain_pk_v,gg_max_v,gg_min_v,gs_max_v,gs_min_v,ig_max_ma,ig_min_ma,ig_dopo_ma,id_max_ma,vin_rail_v,gd_max_v,gd_min_v,veb117_max_v" > rca.csv
"""
    casi = CASI if a.casi == "tutti" else [c for c in CASI if c[0].startswith("classeII")]
    for caso, cy, voff in casi:
        for vol, (rh, rl) in VOL.items():
            for m, (rrg, rrg10) in MODI.items():
                if a.forma and (vol, m) != ("cima", 0):
                    continue
                s += """alter cy = {cy}
alter voff = {voff}
alter rattH = {rh}
alter rattL = {rl}
alter rrgb = {rrg}
alter rrg10b = {rrg10}
tran 10u {t} 0 10u
let abs_main = abs(v(main))
let abs_fix = abs(v(fixjack1))
let abs_ain = abs(v(ain))
let gg = v(xa.g1) - v(xa.g2)
let gs = v(xa.g1) - v(xa.s1)
let ig = (v(ain) - v(xa.g1)) / 100 * 1000
let abs_ig = abs(ig)
meas tran mpk max abs_main from=50.0m to={t}
meas tran mpre max abs_main from=50.0m to=60m
meas tran fpk max abs_fix from=50.0m to={t}
meas tran apk max abs_ain from=50.0m to={t}
meas tran ggmax max gg from=50m to={t}
meas tran ggmin min gg from=50m to={t}
meas tran gsmax max gs from=50m to={t}
meas tran gsmin min gs from=50m to={t}
meas tran igmax max ig from=50m to={t}
meas tran igmin min ig from=50m to={t}
meas tran igdopo max abs_ig from=50.2m to={t}
let gd = v(xa.g1) - v(xa.d1n)
let veb = v(xa.d1n) - v(xa.ncasc)
meas tran gdmax max gd from=50m to={t}
meas tran gdmin min gd from=50m to={t}
meas tran vebmax max veb from=50m to={t}
""".format(cy=cy, voff=voff, rh=rh, rl=rl, rrg=rrg, rrg10=rrg10, t=t)
                if a.forma:
                    s += ("wrdata forma_%s.txt v(jin) v(ain) v(xa.g1) v(xa.g2) v(xa.s1) v(xa.d1n) "
                          "v(xa.ncasc) v(aout) v(main) ig\n" % caso)
                if diodi:
                    s += """let id = max(abs(i(vidp)), abs(i(vidn))) * 1000
meas tran idmax max id from=50m to={t}
let vr = max(v(ain) - v(vplus), v(vminus) - v(ain))
meas tran vrmax max vr from=50m to={t}
""".format(t=t)
                else:
                    s += "let idmax = 0\nlet vr = max(v(ain) - v(vplus), v(vminus) - v(ain))\nmeas tran vrmax max vr from=50m to={t}\n".format(t=t)
                s += """echo "L57A_RCA caso={caso} vol={vol} modo={modo}"
echo "{caso},{vol},{modo},{rete},$&mpk,$&mpre,$&fpk,$&apk,$&ggmax,$&ggmin,$&gsmax,$&gsmin,$&igmax,$&igmin,$&igdopo,$&idmax,$&vrmax,$&gdmax,$&gdmin,$&vebmax" >> rca.csv
destroy all
""".format(caso=caso, vol=vol, modo=m, rete=a.rete)
    return s + ".endc\n.end\n"


testo = {"l53": l53, "l53gate": l53gate, "oggi": oggi}[a.modo]()
open(a.deck, "w").write(testo)
print("%s: %s" % (a.modo, a.deck))
