#!/usr/bin/env python3
"""L53 (NC-058): quale gruppo di dispositivi fa crescere la THD a 57 °C.

A 57 °C la THD a 20 kHz del blocco cresce 4-10 volte (L53/rs, sintesi.csv) mentre il punto di
lavoro cambia poco (op_temp.cir). Qui il circuito sta a 57 °C (`.temp 57`) e UN gruppo di
dispositivi alla volta resta a 27 °C col parametro d'istanza `temp=27` (BJT, JFET e diodi di
ngspice lo accettano). Il gruppo che, tenuto a 27 °C, riporta la THD alla cifra di 27 °C e' quello
che la fa crescere. In piu' i due estremi: tutto a 27 °C e tutto a 57 °C.

Il caso: thd_20k a 0 dB, sorgente 2,5 kOhm, 0,2 V e 2 V (il banco di V4).

Uso: /usr/bin/python3 sonda.py  -> deck/sonda/*.cir, inc/*.inc, deck/lista_sonda.txt
"""
import os
import re

QUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(QUI, *[".."] * 6))
BLOCCO = os.path.join(REPO, "spice", "preamp", "gain_block_flat.inc")
DECK = os.path.join(QUI, "deck", "sonda")
INC = os.path.join(QUI, "inc")

GRUPPI = {
    "jfet": ["JQ110A", "JQ110B"],
    "specchio": ["Q121A", "Q121B"],
    "coda_cascode": ["Q106", "Q117", "Q118"],
    "vas": ["Q122", "Q125"],
    "vbe": ["Q127"],
    "finali": ["Q132", "Q133"],
    "diodi": ["D102", "D103"],
    # seconda tornata: coda_cascode riporta la THD a 27 °C; quale dei tre
    "coda": ["Q106"],
    "cascode": ["Q117", "Q118"],
}
# terza strada: il modello MMBT5551 senza la quasi-saturazione (QUASIMOD=0), una copia locale
MODELLO = os.path.join(REPO, "models", "bjt_npn", "mmbt5551.lib")

TESTA = """{nome} - L53: THD a 20 kHz a 57 gradi, il gruppo {gruppo} tenuto a 27 (NC-058)
* generato da L53/temp/sonda.py
.include @REPO@/models/jfet/lsk489.lib
.include @REPO@/models/bjt_npn/mmbt5551.lib
.include @REPO@/models/bjt_pnp/mmbt5401.lib
.include @REPO@/models/bjt_npn/mje15032.lib
.include @REPO@/models/bjt_pnp/mje15033.lib
.include @REPO@/models/diodes/1n4148.lib
.include @REPO@/models/bjt_pnp/ls350.lib
.include @REPO@/docs/preamp/data/2026-10-12/L53/temp/inc/{inc}.inc

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
.temp {temp}
.options reltol=1e-6 abstol=1e-15 vntol=1e-9

.control
option itl1=1000
set numdgt=10
set fourgridsize=8192
set nfreqs=10
save out vsn
"""
CASO = """alter @vs[sin] = [ 0 {a} 20000 ]
tran 2e-08 0.0021 0 2e-08
echo "L46A_CASO modo=0 livello={liv} freq=20000 ampin={a} rs=2500 gruppo={gruppo}"
fourier 20000 v(vsn) v(out)
destroy all
"""


def inc(nome, tenuti):
    righe = open(BLOCCO).read().split("\n")
    out, trovati = ["* L53 sonda: %s tenuti a 27 gradi col parametro d'istanza temp" % nome], set()
    for r in righe:
        p = r.split()
        if p and p[0] in tenuti:
            r = r + " temp=27"
            trovati.add(p[0])
        out.append(r)
    if trovati != set(tenuti):
        raise SystemExit("istanze non trovate: %s" % (set(tenuti) - trovati))
    with open(os.path.join(INC, nome + ".inc"), "w") as fh:
        fh.write("\n".join(out))


os.makedirs(DECK, exist_ok=True)
os.makedirs(INC, exist_ok=True)
lista = []
casi = [("tutto57", "nessuno", [], 57), ("tutto27", "nessuno", [], 27)]
casi += [("tieni_" + g, g, ist, 57) for g, ist in GRUPPI.items()]
casi += [("noquasi57", "nessuno", [], 57), ("noquasi27", "nessuno", [], 27)]
mod = open(MODELLO).read()
if "QUASIMOD=1" not in mod:
    raise SystemExit("QUASIMOD=1 non trovato nel modello")
open(os.path.join(INC, "mmbt5551_noquasi.lib"), "w").write(
    "* L53 sonda: copia di models/bjt_npn/mmbt5551.lib con QUASIMOD=0, solo per la prova\n"
    + mod.replace("QUASIMOD=1", "QUASIMOD=0"))
for nome, gruppo, ist, temp in casi:
    inc(nome, ist)
    t = TESTA.format(nome=nome, gruppo=gruppo, inc=nome, temp=temp)
    if nome.startswith("noquasi"):
        t = t.replace("@REPO@/models/bjt_npn/mmbt5551.lib",
                      "@REPO@/docs/preamp/data/2026-10-12/L53/temp/inc/mmbt5551_noquasi.lib")
    for liv, a in (("lo", 0.282843), ("hi", 2.82843)):
        t += CASO.format(a=a, liv=liv, gruppo=gruppo)
    t += ".endc\n.end\n"
    p = os.path.join(DECK, nome + ".cir")
    open(p, "w").write(t)
    lista.append(p)
open(os.path.join(QUI, "deck", "lista_sonda.txt"), "w").write("\n".join(lista) + "\n")
print("%d deck" % len(lista))
