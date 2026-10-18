#!/usr/bin/env python3
"""L60d1: rimedi per l'inseguitore davanti al VAS (Q146, ADR-067). Col blocco B sovraccarico sui
47 ohm (mute inserito con la musica, o corto sulla principale) Q146 non ha limite di corrente:
fino a 82 mA, 0,41 W medi e 2 W di picco (P7: 0,31 W per un SOT-23), il VAS in saturazione
profonda, e all'uscita il fronte che fa i picchi sul jack in mute (NC-070). Varianti del
sottocircuito e dell'include piatto GENERATI dal sorgente:

  base    il blocco com'e'
  rc<R>   Q146 col collettore al rail negativo attraverso R (limita la corrente dell'inseguitore)
  rb<R>   R in serie alla base del VAS Q122 (limita la corrente di base del VAS)

Per ogni variante:
  p7      tb_mute_corto risolto (regressione/dopo) con le misure di p7_l56.py -> tb_mute_corto_l56.csv
  sonda   la corsa «sempre in mute» (run/diagnosi/oggi) a 0,3 s: jack principale e Q146 del blocco B
  deck    tb_loop, tb_loop_blockA, tb_loop_bufferfissa, tb_v3_overload con run_simulation.sh

Uso: varianti_follower.py   -> follower/<variante>/..., follower/lista.txt
"""
import os
import shutil
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
R = os.path.abspath(os.path.join(L, "..", "..", "..", "..", ".."))
SP = os.path.join(R, "spice", "preamp")
sys.path.insert(0, QUI)
import p7_l56  # noqa: E402

Q146 = "Q146 VMINUS NHI NVB MMBT5401\n"
Q122 = "Q122 NX NVB NVE MMBT5401\n"
VARIANTI = {"base": None}
for v in ("4.7k", "10k"):
    VARIANTI["rc" + v.replace(".", "p")] = (Q146, "Q146 NC146 NHI NVB MMBT5401\nRXC146 NC146 VMINUS %s\n" % v)
for v in ("1k", "2.2k"):
    VARIANTI["rb" + v.replace(".", "p")] = (Q122, "Q122 NX NB122 NVE MMBT5401\nRXB122 NVB NB122 %s\n" % v)
DECK = ("tb_loop", "tb_loop_blockA", "tb_loop_bufferfissa", "tb_v3_overload")
INC = (("gain_block.subckt", "@REPO@/spice/preamp/gain_block.subckt"),
       ("gain_block_flat.inc", "@REPO@/spice/preamp/gain_block_flat.inc"))


def cambia(txt, mod):
    if mod is None:
        return txt
    assert txt.count(mod[0]) == 1, mod[0]
    return txt.replace(mod[0], mod[1])


def includi(c, d):
    n = 0
    for f, segnaposto in INC:
        for vecchio in (segnaposto, segnaposto.replace("@REPO@", R)):
            n += c.count(vecchio)
            c = c.replace(vecchio, os.path.join(d, f))
    assert n >= 1
    return c


def sonda(c):
    out = []
    for r in c.split("\n"):
        if r.startswith("save "):
            r = "save v(mainjack) @q.xb.q146[ic] @q.xb.q146[p]"
        elif r.startswith("tran "):
            p = r.split()
            p[2] = "300m"
            r = " ".join(p)
        elif r.startswith("wrdata "):
            continue
        out.append(r)
        if r.startswith("tran "):
            out.append("wrdata sonda.dat v(mainjack) @q.xb.q146[ic] @q.xb.q146[p]")
    return "\n".join(out)


base = os.path.join(L, "follower")
if os.path.isdir(base):
    shutil.rmtree(base)
p7 = open(os.path.join(L, "regressione", "dopo", "tb_mute_corto",
                       "tb_mute_corto_resolved.cir")).read()
corsa = open(os.path.join(L, "run", "diagnosi", "oggi", "corsa.cir")).read()
lista = []
for nome, mod in VARIANTI.items():
    d = os.path.join(base, nome)
    for sub in ("p7", "sonda", "deck"):
        os.makedirs(os.path.join(d, sub), exist_ok=True)
    for f, _ in INC:
        open(os.path.join(d, f), "w").write(cambia(open(os.path.join(SP, f)).read(), mod))
    open(os.path.join(d, "p7", "tb_mute_corto.cir"), "w").write(p7_l56.aggiungi(includi(p7, d)))
    open(os.path.join(d, "sonda", "corsa.cir"), "w").write(sonda(includi(corsa, d)))
    lista += ["p7 %s" % nome, "sonda %s" % nome]
    for k in DECK:
        c = includi(open(os.path.join(SP, "tb", k + ".cir")).read(), d)
        open(os.path.join(d, "deck", k + ".cir"), "w").write(c)
        lista.append("deck %s %s" % (nome, k))
open(os.path.join(base, "lista.txt"), "w").write("\n".join(lista) + "\n")
print(len(VARIANTI), "varianti,", len(lista), "corse")
