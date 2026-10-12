#!/usr/bin/env python3
"""L53 (NC-058): V1 del blocco B a caldo, dal deck di L48b (tb_loop_bilanciamento.cir) con sed.

Varianti, ciascuna in v1/<nome>/:
  t27          il deck com'e' (il controllo: deve ridare 64,42 gradi di L48b)
  t57          `.temp 57` (un valore solo)
  aut_t27_rame ogni giunzione alla sua Tj con aria a 27 gradi (temp/autoriscaldamento.py)
  aut_t57_rame idem con aria a 57
  aut_t57_minima idem, piazzola minima del VAS
L'unica modifica e' la riga del blocco incluso e la riga `.temp`.

Uso: /usr/bin/python3 genera.py -> v1/<nome>/tb_loop_<nome>.cir e lista.txt
"""
import os

QUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(QUI, *[".."] * 6))
SRC = os.path.join(REPO, "docs", "preamp", "data", "2026-10-07", "L48b", "v1_bilanciamento",
                   "tb_loop_bilanciamento.cir")
BLOCCO = ".include @REPO@/spice/preamp/gain_block_flat.inc"
AUT = ".include @REPO@/docs/preamp/data/2026-10-12/L53/temp/inc/%s.inc"
VAR = {"t27": (None, None), "t57": (None, 57), "aut_t27_rame": ("aut_t27_rame", 27),
       "aut_t57_rame": ("aut_t57_rame", 57), "aut_t57_minima": ("aut_t57_minima", 57)}

testo = open(SRC).read()
if testo.count(BLOCCO) != 1:
    raise SystemExit("la riga del blocco non c'e' una volta sola")
lista = []
for nome, (inc, temp) in VAR.items():
    t = testo
    t = t.replace(t.split("\n")[0], "tb_loop_%s - L53: V1 del blocco B a caldo (%s), dal deck di L48b" % (nome, nome), 1)
    if inc:
        t = t.replace(BLOCCO, AUT % inc)
    if temp:
        t = t.replace("VPP VPLUS 0 DC 15", ".temp %d\nVPP VPLUS 0 DC 15" % temp, 1)
    d = os.path.join(QUI, nome)
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, "tb_loop_%s.cir" % nome)
    open(p, "w").write(t)
    lista.append(p)
open(os.path.join(QUI, "lista.txt"), "w").write("\n".join(lista) + "\n")
print("\n".join(lista))
