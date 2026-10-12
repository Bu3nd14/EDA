#!/usr/bin/env python3
"""L53 (NC-055): V4 sulla catena, su ogni uscita, a 27 gradi uniformi.

V4 dice «su ogni uscita, in ogni modo»; finora si misurava il blocco da solo. Qui la catena di un
canale con quattro istanze del blocco (gain_block.subckt), come tb_e3_e5.cir (selettore, A, trim,
C_T, bilanciamento al centro, volume) e tb_e4_uscite.cir (i due buffer delle fisse):

  VS -> RSRC -> R_J/C_IN/R_SEL (selettore, ADR-064) -> A -+-> F1 -> 47 R -> 4,7 u -> FIX1 (470 k; 10 k)
                                                          +-> F2 -> 47 R -> 4,7 u -> FIX2 (470 k; 10 k)
                                                          +-> trim 0 dB -> C_T 10 u -> RBAL 50 k ->
                                                              volume 10 k -> B -> 47 R -> 4,7 u -> MAIN (220 k; 10 k)

Il carico su ogni jack e' quello di V4 (47 Ohm + 4,7 uF + 10 kOhm). Il trim a 0 dB (con -6 / -12
il blocco A lavora a un livello piu' alto per la stessa uscita: non e' un uso della catena di V4).

Casi: sorgente 1,5 Ohm (il K11) e 2,5 kOhm (il banco di V4); il volume in cima (cursore sulla cima)
e a meta' (5 k / 5 k, ~2,5 kOhm al blocco B); modo 0 / +3 / +10 dB; 0,2 e 2 V RMS **al jack
principale**: l'ampiezza della sorgente e' livello / (guadagno del modo x volume), dai guadagni
dello schema a blocchi (run_tests 2f). Le fisse escono al livello della sorgente; si giudicano nei
casi in cui la sorgente e' a 0,2 / 2 V (volume in cima, modo 0). Frequenze 1 / 10 / 20 kHz.

Seconda versione, dopo la prima corsa: la fourier sta sulle USCITE DEI BLOCCHI (BOUT, F1OUT,
F2OUT), prima dei 47 Ohm e del 4,7 uF, come il banco di V4 misura v(out). Al jack il transitorio
di carica del 4,7 uF (tau 47 ms con 10 k) cadeva dentro il periodo della fourier e a 1 kHz dava
armoniche finte a -96 dB. Restano C_IN 1 uF e C_T 10 uF a monte: col seno che parte da zero
lasciano un pavimento del metodo di ~-116 dB sulle armoniche alte, solo a 1 kHz (calcolo nel
report). E si saltano i casi che chiedono al blocco A piu' di 2,7 V RMS (volume a meta' e 2 V al
principale): nessuna sorgente di PR-2 li da'.

A 27 gradi uniformi, come ogni cifra di V4 finora: col calore vero dei dispositivi il blocco esce da
V4 da solo (temp/), e la catena non aggiunge niente a quel verdetto.

Uso: /usr/bin/python3 genera.py -> ../deck/catena/*.cir e ../deck/lista.txt
"""
import os

QUI = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(QUI)
DECK = os.path.join(BASE, "deck", "catena")
FREQ = {1000: ("4e-07", "0.004"), 10000: ("4e-08", "0.0022"), 20000: ("2e-08", "0.0021")}
MODI = {0: ("1G", "1G", 1.0), 3: ("0.1", "1G", 1.4202), 10: ("0.1", "0.1", 3.1523)}
VOL = {"cima": ("1m", "10k", 1.0), "meta": ("5k", "5k", 0.5)}
LIV = {"lo": 0.282843, "hi": 2.82843}

TESTA = """{nome} - L53: V4 sulla catena, tre uscite, {f} Hz (NC-055)
* generato da L53/catena/script/genera.py, da tb_e3_e5.cir e tb_e4_uscite.cir
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
VS VSN 0 SIN(0 0.282843 {f})
RSRC VSN JIN 1.5
* il selettore (ADR-064), come tb_e3_e5.cir
RJ    JIN 0 10Meg
CIN   JIN SEL 1u
RSEL  SEL 0 470k
RKSEL SEL AIN 0.1
CSEL  AIN 0 1f
XA AIN AOUT AFB ARG ARG10 VPLUS VMINUS GAINBLOCK
RARG   ARG   0 1G
RARG10 ARG10 0 1G
* le fisse (ADR-023), come tb_e4_uscite.cir, col carico di V4
XF1 AOUT F1OUT F1FB F1RG F1RG10 VPLUS VMINUS GAINBLOCK
RF1RG   F1RG   0 1G
RF1RG10 F1RG10 0 1G
RSEP1 F1OUT FIX1 47
CFIX1 FIX1 FIXJACK1 4.7u
RBL1  FIXJACK1 0 470k
RLD1  FIXJACK1 0 10k
XF2 AOUT F2OUT F2FB F2RG F2RG10 VPLUS VMINUS GAINBLOCK
RF2RG   F2RG   0 1G
RF2RG10 F2RG10 0 1G
RSEP2 F2OUT FIX2 47
CFIX2 FIX2 FIXJACK2 4.7u
RBL2  FIXJACK2 0 470k
RLD2  FIXJACK2 0 10k
* il trim a 0 dB (ADR-027), C_T (ADR-065), il bilanciamento al centro, il volume
RL1 AOUT TAP6 845
RL2 TAP6 TAP12 464
RL3 TAP12 0 464
RT1R AOUT ATOP 0.1
CT1R AOUT ATOP 15p
RT1S T2C ATOP 1G
CT1S T2C ATOP 15p
RT2R TAP6 T2C 0.1
CT2R TAP6 T2C 15p
RT2S TAP12 T2C 1G
CT2S TAP12 T2C 15p
CT    ATOP ATT 10u
CWIRE ATT 0 100p
RBAL  ATT 0 50k
RATTH ATT BIN 1m
RATTL BIN 0 10k
* R_G 1 MOhm sul cursore (ADR-065) e' gia' la R113 del subckt, come in tb_e3_e5.cir
XB BIN BOUT BFB BRG BRG10 VPLUS VMINUS GAINBLOCK
CSTB    BRG   0 15p
RRGB    BRG   0 1G
CSTB10  BRG10 0 15p
RRG10B  BRG10 0 1G
RISO   BOUT BOUTA 47
COUT   BOUTA MAIN 4.7u
RBLEED MAIN 0 220k
RLOAD  MAIN 0 10k
.options reltol=1e-6 abstol=1e-15 vntol=1e-9

.control
option itl1=1000
set numdgt=10
set fourgridsize=8192
set nfreqs=10
save vsn main fixjack1 fixjack2 bout f1out f2out
"""
CASO = """alter rsrc = {rs}
alter rrgb = {rrg}
alter rrg10b = {rrg10}
alter rattH = {rh}
alter rattL = {rl}
alter @vs[sin] = [ 0 {a} {f} ]
tran {passo} {fine} 0 {passo}
echo "L53_CATENA modo={modo} vol={vol} livello={liv} freq={f} ampin={a} rs={rs} main_atteso={atteso}"
fourier {f} v(vsn) v(bout) v(f1out) v(f2out)
destroy all
"""

os.makedirs(DECK, exist_ok=True)
lista = []
for f, (passo, fine) in FREQ.items():
    for liv in LIV:
        nome = "catena_%dk_%s" % (f // 1000, liv)
        s = TESTA.format(nome=nome, f=f)
        for rs in ("1.5", "2500"):
            for vol, (rh, rl, att) in VOL.items():
                for m, (rrg, rrg10, g) in MODI.items():
                    if f != 20000 and rs != "1.5":
                        continue        # la sorgente da 2,5 k solo a 20 kHz, dove V4 ha il tetto di THD
                    a = LIV[liv] / (g * att)
                    if a > 2.7 * 2 ** 0.5:
                        continue        # il blocco A oltre i 2,7 V RMS del K11: nessuna sorgente di PR-2
                    s += CASO.format(rs=rs, rrg=rrg, rrg10=rrg10, rh=rh, rl=rl, a="%.6g" % a, f=f,
                                     passo=passo, fine=fine, modo=m, vol=vol, liv=liv,
                                     atteso="%.6g" % LIV[liv])
        s += ".endc\n.end\n"
        p = os.path.join(DECK, nome + ".cir")
        open(p, "w").write(s)
        lista.append(p)
open(os.path.join(BASE, "deck", "lista.txt"), "w").write("\n".join(lista) + "\n")
print("%d deck" % len(lista))
