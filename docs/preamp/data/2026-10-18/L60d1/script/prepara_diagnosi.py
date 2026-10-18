#!/usr/bin/env python3
"""L60d1, NC-070: il riferimento «sempre in mute» di V2 (g10sempre_1k_iii) dal deck versionato
spice/preamp/tb/tb_v2_casopeggiore.cir, fermato a 2 s (il jack principale sale a 0,58 mV entro
~0,2 s, L60c2), in varianti che differiscono per una riga sola:

  oggi   il deck com'e' (il blocco di L56, spice/preamp/gain_block.subckt)
  l46b   il sottocircuito del blocco di prima di L56 (5dc5c8b1, base/gain_block_L46b.subckt)

Se l46b riporta il jack ai ~1 uV di L48b, la causa e' il blocco di L56; se no e' il banco.
Solo stdlib, /usr/bin/python3 -I.

Uso: prepara_diagnosi.py [VARIANTE=FILE.subckt ...]   -> run/diagnosi/<variante>/corsa.cir
"""
import os
import re
import subprocess
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
R = os.path.abspath(os.path.join(L, "..", "..", "..", "..", ".."))
CORSA = "g10sempre_1k_iii"
T_STOP = "2"

varianti = {
    "oggi": None,
    "l46b": os.path.join(L, "base", "gain_block_L46b.subckt"),
}
for a in sys.argv[1:]:
    k, v = a.split("=", 1)
    varianti[k] = os.path.abspath(v)

base = os.path.join(L, "run", "diagnosi", "deck")
os.makedirs(base, exist_ok=True)
src = open(os.path.join(R, "spice", "preamp", "tb", "tb_v2_casopeggiore.cir")).read()
open(os.path.join(base, "deck.cir"), "w").write(src.replace("@REPO@", R))
subprocess.run(["/usr/bin/python3",
                os.path.join(R, "docs", "preamp", "data", "2026-09-22", "L29b2", "pavimento",
                             "dividi.py"),
                os.path.join(base, "deck.cir")], check=True, stdout=subprocess.DEVNULL)
corsa = open(os.path.join(base, "corsa_%s.cir" % CORSA)).read()

righe = corsa.split("\n")
tr = [i for i, r in enumerate(righe) if r.startswith("tran ")]
assert len(tr) == 1, tr
p = righe[tr[0]].split()
p[2] = T_STOP
righe[tr[0]] = " ".join(p)
corsa = "\n".join(righe)

inc = ".include %s/spice/preamp/gain_block.subckt\n" % R
assert corsa.count(inc) == 1
for nome, sub in varianti.items():
    d = os.path.join(L, "run", "diagnosi", nome)
    os.makedirs(d, exist_ok=True)
    c = corsa if sub is None else corsa.replace(inc, ".include %s\n" % sub)
    open(os.path.join(d, "corsa.cir"), "w").write(c)
    print(nome, "->", d)
