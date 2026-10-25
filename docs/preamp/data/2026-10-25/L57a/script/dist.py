#!/usr/bin/env python3
"""L57a: che cosa costa la protezione dell'ingresso al segnale - distorsione (V4) e rumore (E5).

Il banco: la sorgente (2,5 kOhm, quella di V4) sul jack, il selettore di ADR-064 (C_IN 1 u, R_SEL 470 k,
R_J 10 M, il contatto 0,1 Ohm, CSEL 68 p), la protezione di genera.py (--prot), il blocco A di oggi
(spice/preamp/gain_block.subckt, R_IN 1 M dentro), il trim a 0 dB (1773 Ohm a massa), e la fissa del
Singxer col suo buffer e il carico di V4 (47 Ohm + 4,7 uF + 10 kOhm).

  thd   - THD a 1 e 20 kHz a 0,2 V RMS (il livello di V4) e 2 V RMS (lo stress), il metodo di L46a
          (data/2026-10-01/L46a/script/genera.py, thd): passo 1/(2500 f), 2 ms di assestamento + due
          periodi, fourgridsize 8192, nfreqs 10, reltol 1e-6; `fourier` su v(vsn) (il pavimento) e
          v(fix1)
  rumore - l'ingresso in corto sul jack, `noise` su v(aout) 20 Hz - 20 kHz, onoise_total

Uso: /usr/bin/python3 dist.py <thd|rumore> <deck.cir> [--prot P]
"""
import argparse

p = argparse.ArgumentParser()
p.add_argument("famiglia", choices=("thd", "rumore", "op"))
p.add_argument("deck")
p.add_argument("--prot", default="nessuna")
p.add_argument("--nodeset", default="docs/preamp/data/2026-10-25/L57a/costo/nodeset.inc",
               help="il punto di lavoro vivo (nodeset.py), relativo alla radice del repo")
a = p.parse_args()

TESTA = """{fam} - L57a: il costo della protezione dell'ingresso, prot={prot}
* generato da L57a/script/dist.py
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
{sorgente}
RJ    JIN 0 10Meg
CIN   JIN SEL 1u
RSEL  SEL 0 470k
CSEL  AIN 0 68p
XA AIN AOUT AFB ARG ARG10 VPLUS VMINUS GAINBLOCK
RARG   ARG   0 1G
RARG10 ARG10 0 1G
RL1 AOUT 0 1773
XF1 AOUT F1OUT F1FB F1RG F1RG10 VPLUS VMINUS GAINBLOCK
RF1RG   F1RG   0 1G
RF1RG10 F1RG10 0 1G
RSEP1 F1OUT FIX1 47
CFIX1 FIX1 FIXJACK1 4.7u
RBL1  FIXJACK1 0 470k
RLD1  FIXJACK1 0 10k
* rshunt 1 TOhm su ogni nodo: senza, alcuni punti di lavoro coi diodi ripiegavano su un blocco
* spento (vedi NODESET); su questi nodi pesa meno di una parte su un milione
.options reltol=1e-6 abstol=1e-15 vntol=1e-9 rshunt=1e12
"""


def prot_righe(prot):
    if prot == "nessuna":
        return "RKSEL SEL AIN 0.1\n"
    d = dict(x.split("=") for x in prot.split(","))
    s = "RKSEL SEL NK 0.1\nRP NK AIN %s\n" % d["R"]
    if "D" in d:
        if d["D"] == "rail":
            alto, basso = "VPLUS", "VMINUS"
        else:
            alto, basso = "VCLP", "VCLN"
            s += "VCLP VCLP 0 DC %s\nVCLN VCLN 0 DC -%s\n" % (d["D"], d["D"])
        s += "DP AIN %s D1N914\nDN %s AIN D1N914\n" % (alto, basso)
    return s


# Il punto di lavoro coi diodi: in diverse varianti ngspice non convergeva e ripiegava sul
# «transient op» (L46a #33), e nel banco del rumore il ripiego dava un blocco SPENTO (sorgenti a
# -0,36 V, guadagno 0,00079), con una cifra di rumore plausibile e falsa. Un nodeset sui soli nodi
# d'ingresso e rshunt aiutavano a caso. Il rimedio deterministico: nodeset.py ricava il punto di
# lavoro vivo dal deck senza protezione (famiglia op) e lo scrive in costo/nodeset.inc, che tutti i
# deck includono; il nodeset dice solo dove partire, il punto finale lo trova ngspice.
# leggi_costo.py rifiuta comunque un caso col guadagno del blocco lontano da 1.


INC_NODESET = ".include @REPO@/%s\n" % a.nodeset
if a.famiglia == "op":
    # il punto di lavoro del blocco senza protezione, da cui nodeset.py ricava il nodeset per tutti
    s = TESTA.format(fam="op", prot=a.prot, sorgente="VIN VSN 0 DC 0\nRSRC VSN JIN 2500")
    s = s.replace("RSEL  SEL 0 470k\n", "RSEL  SEL 0 470k\n" + prot_righe(a.prot))
    s += "\n".join([".control", "option itl1=1000", "set numdgt=8", "op", "print all",
                    ".endc", ".end", ""])
elif a.famiglia == "thd":
    # La sorgente pilota SEL, oltre C_IN: con C_IN il polo a 0,5 Hz partiva con un transitorio che
    # nella finestra di 4 ms e' una rampa e metteva un pavimento di ~-101 dB su tutte le armoniche a
    # 1 kHz (prima corsa di L57a, identico nelle otto varianti). La protezione sta dopo C_IN: il suo
    # costo non cambia.
    s = TESTA.format(fam="thd", prot=a.prot,
                     sorgente="VS VSN 0 SIN(0 0.282843 1000)\nRSRC VSN SEL 2500")
    s = s.replace("RJ    JIN 0 10Meg\nCIN   JIN SEL 1u\n", "")
    s = s.replace("RSEL  SEL 0 470k\n", "RSEL  SEL 0 470k\n" + prot_righe(a.prot) + INC_NODESET)
    # La fourier si legge su FIX1 (dopo i 47 Ohm, prima del 4,7 uF): sul jack il polo a 3,4 Hz del
    # 4,7 uF sui 10 k partiva con lo stesso transitorio a rampa e metteva un pavimento di -102,7 dB
    # a 1 kHz, uguale nelle otto varianti (seconda corsa). Il condensatore e' lineare nel modello.
    c = [".control", "option itl1=1000", "set numdgt=10", "set fourgridsize=8192", "set nfreqs=10",
         "save fix1 vsn aout"]
    # e6: il pieno livello d'ingresso di E6 (2,7 V RMS, 3,82 V di picco) a 20 kHz, dove il
    # limitatore a +/-5,6 V e' piu' vicino al segnale; V4 non ha un tetto a questo livello: e' un
    # confronto fra le varianti
    for f in (1000, 20000):
        livelli = [("lo", 0.2 * 2 ** 0.5), ("hi", 2.0 * 2 ** 0.5)]
        if f == 20000:
            livelli.append(("e6", 2.7 * 2 ** 0.5))
        for liv, vpk in livelli:
            tmax = 1.0 / (f * 2500)
            c += ["alter @vs[sin] = [ 0 %.6g %d ]" % (vpk, f),
                  "tran %.4g %.6g 0 %.4g" % (tmax, 2e-3 + 2.0 / f, tmax),
                  'echo "L57A_CASO livello=%s freq=%d ampin=%.6g"' % (liv, f, vpk),
                  "fourier %d v(vsn) v(fix1)" % f, "destroy all"]
    s += "\n".join(c + [".endc", ".end", ""])
else:
    s = TESTA.format(fam="rumore", prot=a.prot, sorgente="VIN VSN 0 DC 0 AC 1\nRSRC VSN JIN 2500")
    s = s.replace("RSEL  SEL 0 470k\n", "RSEL  SEL 0 470k\n" + prot_righe(a.prot) + INC_NODESET)
    s += "\n".join([".control", "option itl1=1000", "set numdgt=6",
                    "ac lin 1 1k 1k", "let g = vm(aout)[0]", 'echo "L57A_GUADAGNO g=$&g"',
                    "noise v(aout) vin dec 100 20 20k", "setplot noise2",
                    "let n_uv = onoise_total * 1e6",
                    'echo "L57A_RUMORE prot=%s onoise_aout_uv=$&n_uv"' % a.prot,
                    ".endc", ".end", ""])
open(a.deck, "w").write(s)
print("%s: %s" % (a.famiglia, a.deck))
