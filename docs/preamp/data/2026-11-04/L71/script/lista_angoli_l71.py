#!/usr/bin/env python3
"""L71: the shortest MUSICA on ADR-105's worst corner of Delta (L54b3b's toll_c0g_t<T>_dperm_sp.json,
copied into psu/, with the diodes' leakage at the temperature, as L54b3b's lista_angoli.py), at
mains -10 %.
  step 1 (no argument): accensione and rilascio on each corner -> lista_angoli_1.txt (where the
         music arrives on the corner: the instants of step 2 depend on it)
  step 2 (--da an_l71.csv): acc_spento_<ms> and ril_ritorno_<ms> at the corner's own music instant
         minus 7.2 ... 6.6 ms (nominal: the jack closes from 7.05 ms before it), 0.1 ms apart; the
         generator's families take any <ms> written with 'p' -> lista_angoli_2.txt
Labels l71_ang_t<T>_m10. Needs the generator to accept the instants: step 2 writes them into
psu/casi_extra.txt, which genera_tb_psu.py reads (L71).
"""
import csv
import os
import sys

L = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PERDITE = {
    0: "D538:5.5e-9,D535:2.9e-9,D536:2.9e-9,D541:2.9e-9,D533:0.4e-6,D534:2.9e-9,D537:0.4e-6",
    25: "D538:25e-9,D535:5e-9,D536:5e-9,D541:5e-9,D533:2e-6,D534:5e-9,D537:2e-6",
    60: "D538:210e-9,D535:11e-9,D536:11e-9,D541:11e-9,D533:19e-6,D534:11e-9,D537:19e-6",
}
BASE = ("sorgente --n2n7002 ds --tss 3.0 --ritenuta costruttore --bat54 costruttore --sonde-piu "
        "--comparatore tarato --rete 0.9")


def riga(caso, t):
    return "%s l71_ang_t%d_m10 %s --temp %d --perdita %s --toll %s" % (
        caso, t, BASE, t, PERDITE[t], os.path.join(L, "psu", "toll_c0g_t%d_dperm_sp.json" % t))


if "--da" not in sys.argv:
    out = [riga(c, t) for t in (0, 25, 60) for c in ("accensione", "rilascio")]
    nome = "lista_angoli_1.txt"
else:
    an = {r["caso"]: r for r in csv.DictReader(open(sys.argv[sys.argv.index("--da") + 1]))}
    out, extra = [], []
    for t in (0, 25, 60):
        for caso, fam in (("accensione", "acc_spento"), ("rilascio", "ril_ritorno")):
            tm = float(an["l71_ang_t%d_m10/%s" % (t, caso)]["t_mus_ms"])
            for k in range(7):
                ms = round(tm - 7.2 + 0.1 * k, 1)
                nome_c = "%s_%s" % (fam, ("%.1f" % ms).replace(".", "p"))
                extra.append(nome_c)
                out.append(riga(nome_c, t))
    open(os.path.join(L, "psu", "casi_extra.txt"), "w").write("\n".join(sorted(set(extra))) + "\n")
    nome = "lista_angoli_2.txt"
open(os.path.join(L, nome), "w").write("\n".join(out) + "\n")
print(nome, len(out), "corse")
