#!/usr/bin/env python3
"""L67 (NC-055): V4 sulla catena di un canale, col blocco come argomento.

Copiato da L56/catena/script/genera.py (a sua volta L53). Il circuito del deck e la griglia di L56
sono INVARIATI riga per riga; cambiano solo:
  1. il blocco incluso, per nome (BLOCCHI qui sotto), invece di spice/preamp/gain_block.subckt fisso;
  2. due posizioni del volume in piu', `m10` e `m20` (-10 / -20 dB, partitore lineare equivalente
     sul potenziometro da 10 kOhm, con la sua impedenza verso il blocco B). Col volume basso la
     principale a 0,2 V porta la distorsione del blocco A a un livello piu' alto (0,63 / 2 V): V4
     letto alla lettera la giudica contro 0,001 %. leggi_catena.py le mette in righe a parte
     (griglia = volbasso), fuori dal confronto con L56.

La catena (da L56):
  VS -> RSRC -> R_J/C_IN/R_SEL (selettore, ADR-064) -> A -+-> F1 -> 47 R -> 4,7 u -> FIX1 (470 k; 10 k)
                                                          +-> F2 -> 47 R -> 4,7 u -> FIX2 (470 k; 10 k)
                                                          +-> trim 0 dB -> C_T 10 u -> RBAL 50 k ->
                                                              volume 10 k -> B -> 47 R -> 4,7 u -> MAIN (220 k; 10 k)
Carico di V4 su ogni jack; fourier sulle uscite dei blocchi (BOUT, F1OUT, F2OUT), come il banco di
V4 misura v(out) (L56: il transitorio del 4,7 uF al jack dava armoniche finte). Sorgente 1,5 Ohm
(il K11) e 2,5 kOhm (il banco di V4, solo a 20 kHz); modi 0 / +3 / +10; 0,2 / 2 V RMS al jack
principale; saltati i casi che chiedono al blocco A piu' di 2,7 V RMS.

I blocchi:
  l56        prima/gain_block_l56.subckt (git 369f2aad2, il blocco di L56): il CASO NOTO
  oggi       spice/preamp/gain_block.subckt, 27 gradi uniformi
  oggi_avv   inc/oggi_avv.subckt (avvolgi.py: il piatto di oggi avvolto), deve dare `oggi`
  caldo_*    inc/caldo_<t>_<p>.subckt (avvolgi.py: i blocchi caldi di L66, ogni giunzione alla sua
             Tj). IPOTESI: le quattro istanze alla stessa Tj, perche' il punto di lavoro in continua
             e' lo stesso (i carichi sono disaccoppiati in alternata; a 0,2-2 V su >= 10 kOhm la
             potenza di segnale e' trascurabile davanti ai mW di riposo)

Uso: /usr/bin/python3 -I genera.py <blocco>... -> ../deck/<blocco>/*.cir e ../deck/lista_<blocchi>.txt
"""
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(QUI)
LREL = "docs/preamp/data/2026-11-02/L67"
BLOCCHI = {"l56": LREL + "/prima/gain_block_l56.subckt", "oggi": "spice/preamp/gain_block.subckt"}
for n in ("oggi_avv", "caldo_t27_rame", "caldo_t27_minima", "caldo_t57_rame", "caldo_t57_minima"):
    BLOCCHI[n] = LREL + "/inc/%s.subckt" % n
FREQ = {1000: ("4e-07", "0.004"), 10000: ("4e-08", "0.0022"), 20000: ("2e-08", "0.0021")}
MODI = {0: ("1G", "1G", 1.0), 3: ("0.1", "1G", 1.4202), 10: ("0.1", "0.1", 3.1523)}
# L56: cima e meta. L67: m10 e m20, partitore lineare equivalente (att = 10^(-dB/20) su 10 kOhm)
VOL = {"cima": ("1m", "10k", 1.0), "meta": ("5k", "5k", 0.5),
       "m10": ("6837.72", "3162.28", 0.316228), "m20": ("9000", "1000", 0.1)}
LIV = {"lo": 0.282843, "hi": 2.82843}

TESTA = """{nome} - L67: V4 sulla catena, tre uscite, {f} Hz, blocco {blocco} (NC-055)
* generato da L67/catena/script/genera.py (L56/L53), da tb_e3_e5.cir e tb_e4_uscite.cir
.include @REPO@/models/jfet/lsk489.lib
.include @REPO@/models/bjt_npn/mmbt5551.lib
.include @REPO@/models/bjt_pnp/mmbt5401.lib
.include @REPO@/models/bjt_npn/mje15032.lib
.include @REPO@/models/bjt_pnp/mje15033.lib
.include @REPO@/models/diodes/1n4148.lib
.include @REPO@/models/bjt_pnp/ls350.lib
.include @REPO@/{inc}

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
{temp}.options reltol=1e-6 abstol=1e-15 vntol=1e-9

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

blocchi = sys.argv[1:]
if not blocchi or any(b not in BLOCCHI for b in blocchi):
    raise SystemExit("uso: genera.py <blocco>... con blocco fra %s" % ", ".join(BLOCCHI))
ROOT = os.path.abspath(os.path.join(BASE, "..", "..", "..", "..", "..", ".."))
lista = []
for blocco in blocchi:
    inc = BLOCCHI[blocco]
    if not os.path.exists(os.path.join(ROOT, inc)):
        raise SystemExit("manca %s (avvolgi.py?)" % inc)
    deck = os.path.join(BASE, "deck", blocco)
    os.makedirs(deck, exist_ok=True)
    # i casi del volume basso in deck a parte (_vb): dentro un deck i casi corrono in sequenza, e
    # mescolarli alla griglia di L56 ne cambierebbe l'ordine (e i punti di partenza dell'op). I deck
    # della griglia di L56 restano uguali a quelli di L56 salvo il titolo e l'include del blocco.
    for (f, (passo, fine)), liv, vb in [(fp, l, v) for v in (False, True) for fp in FREQ.items() for l in LIV]:
        if True:
            nome = "catena_%dk_%s%s" % (f // 1000, liv, "_vb" if vb else "")
            # i blocchi caldi a 57: l'aria a 57 per cio' che non ha temp= (i diodi, come il deck di
            # v4caldo.py di L66, che porta `.temp 57`); a 27 niente, come L56
            temp = ".temp 57\n" if blocco.startswith("caldo_t57") else ""
            s = TESTA.format(nome=nome, f=f, blocco=blocco, inc=inc, temp=temp)
            for rs in ("1.5", "2500"):
                for vol, (rh, rl, att) in VOL.items():
                    if (vol in ("m10", "m20")) != vb:
                        continue
                    for m, (rrg, rrg10, g) in MODI.items():
                        if f != 20000 and rs != "1.5":
                            continue    # la sorgente da 2,5 k solo a 20 kHz, dove V4 ha il tetto di THD
                        a = LIV[liv] / (g * att)
                        if a > 2.7 * 2 ** 0.5:
                            continue    # il blocco A oltre i 2,7 V RMS del K11: nessuna sorgente di PR-2
                        s += CASO.format(rs=rs, rrg=rrg, rrg10=rrg10, rh=rh, rl=rl, a="%.6g" % a, f=f,
                                         passo=passo, fine=fine, modo=m, vol=vol, liv=liv,
                                         atteso="%.6g" % LIV[liv])
            if s.count("L53_CATENA") == 0:
                continue        # nessun caso (il volume basso a 2 V chiede troppo al blocco A)
            s += ".endc\n.end\n"
            p = os.path.join(deck, nome + ".cir")
            open(p, "w").write(s)
            lista.append(p)
pl = os.path.join(BASE, "deck", "lista_%s.txt" % "_".join(blocchi))
open(pl, "w").write("\n".join(lista) + "\n")
print("%d deck -> %s" % (len(lista), pl))
