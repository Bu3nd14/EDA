#!/usr/bin/env python3
"""L53 (NC-058): la THD del blocco con ogni giunzione alla sua temperatura, non a quella dell'aria.

SPICE non scalda i dispositivi: `.temp` mette tutto alla temperatura dell'aria. Ma il VAS (Q122,
MMBT5401) e il suo carico (Q125, MMBT5551) dissipano ~0,14 W in SOT-23 (gain_block.py, P7), cioe'
+50-57 gradi sopra l'aria coi R_thJA dei datasheet; e coda.py/sonda.py dicono che la THD dipende
dalla tensione che il VAS lascia allo specchio d'ingresso (Q121B, LS350, RC 231 Ohm), che scende
quando la Vbe del VAS scende col calore.

Qui, per ogni temperatura dell'aria Ta (27 e 57 gradi), la potenza di ogni dispositivo dal punto
di lavoro a Ta (op_cliff.log per i nodi e le correnti, op_temp.log per i finali) e
  Tj = Ta + P * R_thJA
con R_thJA dai datasheet in vendor/ (still air):
  MMBT5401  403 C/W piazzola minima, 357 C/W con 15x15 mm di rame (Diodes, note 5 e 6)
  MMBT5551  417 C/W piazzola minima, 2 oz (Diodes, nota 5)
  LS350     doppio sullo stesso die: 4,3 mW/C con due lati -> 233 C/W sulla somma delle due P
  LSK489    doppio: 4 mW/C sul totale -> 250 C/W sulla somma (datasheet, nota 5)
  MJE15032/33  TO-220 senza dissipatore: 0,016 W/C -> 62,5 C/W (onsemi)
Due varianti: «minima» (piazzola minima) e «rame» (MMBT5401 a 357; per gli altri il datasheet non
da' una cifra col rame, restano uguali). Un passo solo, senza iterare: la potenza cambia di poco
col calore (op_temp: VAS 10,7 -> 10,4 mA). Q127 (moltiplicatore di Vbe) col suo solo calore: ADR-034
lo vuole accoppiato al finale col rame, che sta nel layout di G2 (dichiarato).

Poi i deck: il circuito a Ta (.temp: resistenze e diodi), ogni BJT e JFET a temp=Tj; thd_20k a
0 / +3 / +10 dB con sorgente 2,5 e 5,6 kOhm, 0,2 e 2 V.

Uso: /usr/bin/python3 autoriscaldamento.py -> tj.csv, inc/aut_*.inc, deck/aut/*.cir, deck/lista_aut.txt
"""
import csv
import os
import re

QUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(QUI, *[".."] * 6))
BLOCCO = os.path.join(REPO, "spice", "preamp", "gain_block_flat.inc")
DECK = os.path.join(QUI, "deck", "aut")
INC = os.path.join(QUI, "inc")

# piedini dal netlist (C B E / D G S)
pin = {}
for r in open(BLOCCO):
    p = r.split()
    if p and p[0][0] in "QJ":
        pin[p[0]] = p[1:4]


def leggi_op(log, marca):
    t = open(log, errors="replace").read()
    b = t.split(marca, 1)[1]
    b = re.split(r"L53_(COND|OP) ", b)[0]
    v = {"0": 0.0}
    for m in re.finditer(r"^(\S+) = ([-+0-9.eE]+)", b, re.M):
        k = re.sub(r"^v\((.*)\)$", r"\1", m.group(1).lower())
        v[k] = float(m.group(2))
    return v


def potenze(ta):
    nodi = leggi_op(os.path.join(QUI, "run_cliff", "op_cliff.log"), "L53_COND t=%d r107=137" % ta)
    fin = leggi_op(os.path.join(QUI, "run_op", "op_temp.log"), "L53_OP temp=%d" % ta)
    corr = {"Q106": nodi["@q106[ic]"], "Q117": nodi["@q117[ic]"], "Q118": nodi["@q118[ic]"],
            "Q121A": nodi["@q121a[ic]"], "Q121B": nodi["@q121b[ic]"], "Q122": nodi["@q122[ic]"],
            "Q125": nodi["@q125[ic]"], "Q127": nodi["@q127[ic]"],
            "JQ110A": nodi["@jq110a[id]"], "JQ110B": nodi["@jq110b[id]"],
            "Q132": fin["@q132[ic]"], "Q133": fin["@q133[ic]"]}
    p = {}
    for d, i in corr.items():
        a, _, e = pin[d]
        va = 15.0 if a == "VPLUS" else -15.0 if a == "VMINUS" else nodi[a.lower()]
        ve = nodi[e.lower()] if e not in ("VPLUS", "VMINUS") else (15.0 if e == "VPLUS" else -15.0)
        p[d] = abs(i * (va - ve))
    return p


def tj(ta, p, variante):
    t = {}
    r5401 = 357 if variante == "rame" else 403
    for d in ("Q122",):
        t[d] = ta + p[d] * r5401
    for d in ("Q106", "Q117", "Q118", "Q125", "Q127"):
        t[d] = ta + p[d] * 417
    t["Q121A"] = t["Q121B"] = ta + (p["Q121A"] + p["Q121B"]) * 233
    t["JQ110A"] = t["JQ110B"] = ta + (p["JQ110A"] + p["JQ110B"]) * 250
    for d in ("Q132", "Q133"):
        t[d] = ta + p[d] * 62.5
    return t


TESTA = """{nome} - L53: THD a 20 kHz, ogni giunzione alla sua temperatura (aria {ta} gradi, {var})
* generato da L53/temp/autoriscaldamento.py
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
.temp {ta}
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
alter @vs[sin] = [ 0 {a} 20000 ]
tran 2e-08 0.0021 0 2e-08
echo "L46A_CASO modo={modo} livello={liv} freq=20000 ampin={a} rs={rs}"
fourier 20000 v(vsn) v(out)
destroy all
"""
MODI = {0: ("1G", "1G", 1.0), 3: ("0.1", "1G", 1.4202), 10: ("0.1", "0.1", 3.1523)}

os.makedirs(DECK, exist_ok=True)
lista, tab = [], []
for ta in (27, 57):
    p = potenze(ta)
    for var in ("minima", "rame"):
        t = tj(ta, p, var)
        nome = "aut_t%d_%s" % (ta, var)
        for d in sorted(t):
            tab.append({"aria": ta, "variante": var, "disp": d, "P_mW": "%.1f" % (p[d] * 1e3),
                        "Tj": "%.1f" % t[d]})
        righe = []
        for r in open(BLOCCO):
            q = r.split()
            if q and q[0] in t:
                r = r.rstrip("\n") + " temp=%.1f\n" % t[q[0]]
            righe.append(r)
        open(os.path.join(INC, nome + ".inc"), "w").write(
            "* L53: %s, ogni giunzione alla sua Tj (autoriscaldamento.py)\n" % nome + "".join(righe))
        s = TESTA.format(nome=nome, ta=ta, var=var, inc=nome)
        for m in (0, 3, 10):
            rrg, rrg10, g = MODI[m]
            for rs in (2500, 5600):
                for liv, a in (("lo", 0.282843), ("hi", 2.82843)):
                    s += CASO.format(rs=rs, rrg=rrg, rrg10=rrg10, a="%.6g" % (a / g), liv=liv, modo=m)
        s += ".endc\n.end\n"
        f = os.path.join(DECK, nome + ".cir")
        open(f, "w").write(s)
        lista.append(f)
open(os.path.join(QUI, "deck", "lista_aut.txt"), "w").write("\n".join(lista) + "\n")
with open(os.path.join(QUI, "tj.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, list(tab[0]))
    w.writeheader()
    w.writerows(tab)
for r in tab:
    print("aria %(aria)s %(variante)-6s %(disp)-7s P=%(P_mW)7s mW  Tj=%(Tj)6s" % r)
