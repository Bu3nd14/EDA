#!/usr/bin/env python3
"""L60c2: la tenuta di VRELAY (P9) con la bobina di K3 da IM06TS. Solo stdlib, /usr/bin/python3 -I.

Uso: prepara_rete.py        scrive run/rete/{base,im06}/tb_psu_rete.cir

Il banco della rete di L51b (data/2026-10-09/L51b/rete/tb_psu_rete.cir, il carico di oggi col
selettore) modella le tre bobine di mute come una resistenza sola, RMUTECOIL = 438,333 ohm (tre G6K
da 1315 ohm in parallelo). Con K3 IM06TS (1029 ohm, ENG_DS_108-98001_K.pdf p. 6) diventa
1315 || 1315 || 1029 = 401,17 ohm. Due copie del deck di L51b, coi percorsi riscritti verso questa
cartella: «base» invariata (deve ridare L51b: 48,3 ms a rete -10 %) e «im06» con la sola RMUTECOIL
cambiata. La differenza fra le due e' l'effetto di K3; il resto del banco resta quello di L51b
(dichiarato: generato dalla psu.net di L51b, prima di L60b).
"""
import os

QUI = os.path.dirname(os.path.abspath(__file__))
L60C2 = os.path.dirname(QUI)
DATA = os.path.abspath(os.path.join(L60C2, "..", ".."))
ROOT = os.path.abspath(os.path.join(DATA, "..", "..", ".."))
SRC = os.path.join(DATA, "2026-10-09", "L51b", "rete", "tb_psu_rete.cir")
VECCHIO_WT = "/Users/roberto/EDA/.claude/worktrees/L51b"
VECCHIA_RETE = VECCHIO_WT + "/docs/preamp/data/2026-10-09/L51b/rete/"

R_G6K = 1315.0
R_IM06 = 1029.0                     # 12 V, 140 mW: 12^2 / 0,14 = 1028,6 ohm


def par(*r):
    return 1.0 / sum(1.0 / x for x in r)


testo = open(SRC).read()
assert testo.count("RMUTECOIL vrelay mute_cmd 438.333\n") == 1
for nome, rm in (("base", "438.333"), ("im06", "%.3f" % par(R_G6K, R_G6K, R_IM06))):
    out = os.path.join(L60C2, "run", "rete", nome)
    os.makedirs(out, exist_ok=True)
    t = testo.replace(VECCHIA_RETE, out + "/").replace(VECCHIO_WT, ROOT)
    t = t.replace("RMUTECOIL vrelay mute_cmd 438.333\n", "RMUTECOIL vrelay mute_cmd %s\n" % rm)
    assert VECCHIO_WT not in t
    open(os.path.join(out, "tb_psu_rete.cir"), "w").write(t)
    print(nome, "RMUTECOIL", rm, "->", out)
