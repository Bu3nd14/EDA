#!/usr/bin/env python3
"""L60d2: P7 con R153 in corto. R153 (4,7 kOhm fra il collettore dell'inseguitore davanti al VAS e il
rail negativo, ADR-087) e' il limite che L60d1 ha messo a Q146: in corto l'inseguitore torna senza
limite, come prima di L60d1 (0,41 W medi, 2,0 W di picco col mute inserito o col corto sulla
principale, NC-071). Il guasto e' di una parte: qui la sua conseguenza, la dissipazione di Q146.

Il deck e' il P7 di L60d2 risolto (p7/dopo/tb_mute_corto, coi 56 Ohm di R123 / R126) con le misure
di Q146 e Q148 di L60d1 (p7_l56.aggiungi), e gain_block.subckt sostituito da una copia con R153 a
1 mOhm. La copia vale per le quattro istanze insieme: i rail del banco sono ideali, quindi ogni
blocco vede solo il proprio carico, e P7 legge ogni blocco per conto suo.

Uso: p7_r153cc.py [valore=1m]   -> run/p7_r153cc[_valore]/tb_mute_corto.cir
"""
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
R = os.path.abspath(os.path.join(L, "..", "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(R, "docs", "preamp", "data", "2026-10-18", "L60d1", "script"))
import p7_l56  # noqa: E402

SUB = os.path.join(R, "spice", "preamp", "gain_block.subckt")
VAL = sys.argv[1] if len(sys.argv) > 1 else "1m"   # 1 ohm: la prova del punto di lavoro
OUT = os.path.join(L, "run", "p7_r153cc" + ("" if VAL == "1m" else "_" + VAL))
os.makedirs(OUT, exist_ok=True)
righe = open(SUB).read().splitlines()
k = [i for i, r in enumerate(righe) if r.split()[:1] == ["R153"]]
assert len(k) == 1 and righe[k[0]].split()[3] == "4.7k", righe[k[0]] if k else "R153 assente"
righe[k[0]] = "* L60d2: R153 IN CORTO\nR153 %s %s" % (" ".join(righe[k[0]].split()[1:3]), VAL)
copia = os.path.join(OUT, "gain_block_r153cc.subckt")
open(copia, "w").write("\n".join(righe) + "\n")

t = open(os.path.join(L, "p7", "dopo", "tb_mute_corto", "tb_mute_corto_resolved.cir")).read()
inc = ".include %s" % SUB
assert t.count(inc) == 1, "il deck non include %s" % SUB
t = t.replace(inc, ".include %s" % copia)
open(os.path.join(OUT, "tb_mute_corto.cir"), "w").write(p7_l56.aggiungi(t, False))
print("->", OUT)
