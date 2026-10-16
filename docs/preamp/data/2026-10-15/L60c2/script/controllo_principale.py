#!/usr/bin/env python3
"""L60c2: il riferimento «sempre in mute» di V2 (g10sempre_1k_iii) con le due righe di L60c2 tolte:
CFIX2 di nuovo 4.7u e il contatto aperto di K3 di nuovo 0.1p, cioe' il deck versionato di prima di
L60c2 per questa corsa; fermato a 2 s (il salto sul jack principale e' a ~0,2 s). Se il jack
principale fa lo stesso, il salto non viene da L60c2. Solo stdlib, /usr/bin/python3 -I.

Uso: controllo_principale.py      scrive run/controllo_principale/corsa_g10sempre_1k_iii.cir
"""
import os

QUI = os.path.dirname(os.path.abspath(__file__))
L60C2 = os.path.dirname(QUI)
src = open(os.path.join(L60C2, "run", "v2", "corsa_g10sempre_1k_iii.cir")).read()
for a, b in (("CFIX2 FIX2 FIXC2 1u\n", "CFIX2 FIX2 FIXC2 4.7u\n"),
             ("alter cks2 = 1p\n", "alter cks2 = 0.1p\n")):
    assert src.count(a) == 1, a
    src = src.replace(a, b)
righe = src.split("\n")
tr = [i for i, r in enumerate(righe) if r.startswith("tran ")]
assert len(tr) == 1
p = righe[tr[0]].split()
p[2] = "2"
righe[tr[0]] = " ".join(p)
d = os.path.join(L60C2, "run", "controllo_principale")
os.makedirs(d, exist_ok=True)
open(os.path.join(d, "corsa_g10sempre_1k_iii.cir"), "w").write("\n".join(righe))
print(righe[tr[0]], "->", d)
