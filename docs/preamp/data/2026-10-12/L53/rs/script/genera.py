#!/usr/bin/env python3
"""L53, NC-055: la THD del blocco a guadagno unitario contro l'impedenza di sorgente.

L'ipotesi dell'architetto di L52 (R5): nelle istanze a 0 dB la C_gd non lineare dei JFET,
vista attraverso la differenza fra l'impedenza di sorgente e quella del ramo di controreazione
(R_F 1,5 kOhm + R109 100 Ohm), da' una distorsione davanti all'anello. Se e' vero, la THD segue
|R_S - R_F| e ha un minimo vicino a R_S = 1,5 kOhm; se la THD e' limitata dall'anello, non
dipende da R_S.

Il banco e' quello di L46b/L51c (`thd_*.cir`), uguale riga per riga salvo:
  - il blocco incluso e' `spice/preamp/gain_block_flat.inc` di oggi (uguale a L51c/inc/oggi.inc
    tolta la prima riga di commento, verificato con diff);
  - modo 0 soltanto (rrg = rrg10 = 1G, R_g aperta);
  - RSRC per caso: 1 mOhm (la sorgente ideale), 1500, 2500 (il banco di V4), 5600 Ohm (il
    bilanciamento girato, ADR-065);
  - in piu' una scansione fine attorno a R_F (1000, 1200, 1400, 1600, 1800, 2000) a 20 kHz alto.
Livelli: lo 0,2 V RMS (ADR-055), hi 2 V RMS, all'uscita (a guadagno unitario = all'ingresso).

NC-058: con un argomento, la temperatura (°C), gli stessi deck con `.temp <T>` (un valore solo:
`.temp` con una lista ricade a 27 °C, CLAUDE.md) in deck/t<T>/; la prova che la temperatura
arriva sta nel log (`leggi_four.py` la controlla).

Uso: /usr/bin/python3 genera.py [T]  -> ../deck/<rs|tT>/*.cir e ../deck/lista_<rs|tT>.txt
"""
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(QUI)
TEMP = sys.argv[1] if len(sys.argv) > 1 else None
VAR = "t%s" % TEMP if TEMP else "rs"
DECK = os.path.join(BASE, "deck", VAR)

FREQ = {1000: ("4e-07", "0.004"), 10000: ("4e-08", "0.0022"), 20000: ("2e-08", "0.0021")}
RS = [0.001, 1500, 2500, 5600]
RS_FINE = [1000, 1200, 1400, 1600, 1800, 2000]
LIV = {"lo": 0.282843, "hi": 2.82843}

TESTA = """{nome} - L53: THD a {f} Hz, blocco a 0 dB, impedenza di sorgente variabile (NC-055)
* generato da L53/rs/script/genera.py, dal banco di L46b/L51c
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
VS VSN 0 SIN(0 0.282843 {f})
RSRC VSN IN 2500
CSTRAY RG 0 15p
CSTRAY10 RG10 0 15p
RRG RG 0 1G
RRG10 RG10 0 1G
RISO OUT OUTA 47
COUT OUTA JACK 4.7u
RBLEED JACK 0 220k
RLOAD JACK 0 10k
.options reltol=1e-6 abstol=1e-15 vntol=1e-9

.control
option itl1=1000
set numdgt=10
set fourgridsize=8192
set nfreqs=10
save out vsn
"""

CASO = """alter rsrc = {rs}
alter rrg = {rrg}
alter rrg10 = {rrg10}
alter @vs[sin] = [ 0 {a} {f} ]
tran {passo} {fine} 0 {passo}
echo "L46A_CASO modo={modo} livello={liv} freq={f} ampin={a} rs={rs}"
fourier {f} v(vsn) v(out)
destroy all
"""

# Il guadagno di ogni modo dallo schema a blocchi (run_tests.sh 2f): 1, 1.4202, 3.1523. Le
# ampiezze d'ingresso sono quelle del banco di L46b, che danno 0,2 / 2 V RMS in uscita.
MODI = {0: ("1G", "1G", 1.0), 3: ("0.1", "1G", 1.4202), 10: ("0.1", "0.1", 3.1523)}


def deck(nome, f, casi):
    passo, fine = FREQ[f]
    t = TESTA.format(nome=nome, f=f)
    if TEMP:
        t = t.replace(".options reltol", ".temp %s\n.options reltol" % TEMP)
    for c in casi:
        rs, liv = c[0], c[1]
        modo = c[2] if len(c) > 2 else 0
        rrg, rrg10, g = MODI[modo]
        t += CASO.format(rs=rs, a="%.6g" % (LIV[liv] / g), f=f, liv=liv, passo=passo,
                         fine=fine, modo=modo, rrg=rrg, rrg10=rrg10)
    t += ".endc\n.end\n"
    p = os.path.join(DECK, nome + ".cir")
    with open(p, "w") as fh:
        fh.write(t)
    return p


os.makedirs(DECK, exist_ok=True)
lista = []
for f in FREQ:
    for liv in LIV:
        lista.append(deck("thd_%dk_%s" % (f // 1000, liv), f, [(rs, liv) for rs in RS]))
lista.append(deck("thd_20k_hi_fine", 20000, [(rs, "hi") for rs in RS_FINE]))
# Il blocco B lavora a +3 e +10 dB con la stessa sorgente del bilanciamento girato.
for f in FREQ:
    for liv in LIV:
        lista.append(deck("thd_%dk_%s_modi" % (f // 1000, liv), f,
                          [(rs, liv, m) for m in (3, 10) for rs in (0.001, 2500, 5600)]))
with open(os.path.join(BASE, "deck", "lista_%s.txt" % VAR), "w") as fh:
    fh.write("\n".join(lista) + "\n")
print("%d deck in %s" % (len(lista), DECK))
