#!/usr/bin/env python3
"""L67, caso noto 4: il blocco caldo regge dentro un subckt (temp= per istanza e la massa).

I quattro deck di THD a 20 kHz di L66 per lim365--sot223--diss (deck/lim365--sot223--diss/
thd20k_<cond>.cir, il banco di V4 a caldo di v4caldo.py) in due copie:
  piatto   il deck di L66 com'e' (deve ridare L66/sintesi_caldo.csv: 0,000695 / 0,00705 % a t27,
           0,000725 / 0,00734 % a t57)
  avvolto  lo stesso deck con il blocco piatto sostituito da inc/caldo_<cond>.subckt (avvolgi.py)
           e una riga di istanza sugli stessi nodi: le 12 THD devono essere uguali a `piatto`.

Uso: /usr/bin/python3 -I genera.py -> ../deck/{piatto,avvolto}/*.cir e ../deck/lista.txt
"""
import os

QUI = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(QUI)
ROOT = os.path.abspath(os.path.join(BASE, "..", "..", "..", "..", "..", ".."))
L66 = os.path.join(ROOT, "docs/preamp/data/2026-11-02/L66/deck/lim365--sot223--diss")
INC66 = ".include @REPO@/docs/preamp/data/2026-11-02/L66/inc/lim365--sot223--diss__%s.inc"
INC67 = (".include @REPO@/docs/preamp/data/2026-11-02/L67/inc/caldo_%s.subckt\n"
         "XG IN OUT FB RG RG10 VPLUS VMINUS GAINBLOCK")
lista = []
for cond in ("t27_rame", "t27_minima", "t57_rame", "t57_minima"):
    testo = open(os.path.join(L66, "thd20k_%s.cir" % cond)).read()
    if testo.count(INC66 % cond) != 1:
        raise SystemExit("thd20k_%s.cir: l'include del blocco non e' quello atteso" % cond)
    for copia, t in (("piatto", testo), ("avvolto", testo.replace(INC66 % cond, INC67 % cond))):
        d = os.path.join(BASE, "deck", copia)
        os.makedirs(d, exist_ok=True)
        p = os.path.join(d, "thd20k_%s.cir" % cond)
        open(p, "w").write(t)
        lista.append(p)
open(os.path.join(BASE, "deck", "lista.txt"), "w").write("\n".join(lista) + "\n")
print("%d deck" % len(lista))
