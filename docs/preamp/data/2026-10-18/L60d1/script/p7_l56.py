#!/usr/bin/env python3
"""L60d1: P7 (tb_mute_corto, ogni caso di corto e di carico) non ha mai misurato i due transistor
di L56, l'inseguitore davanti al VAS (Q146) e l'aiuto sullo specchio (Q148): il deck salva e
misura Q122, Q125, Q127 e il resto, non loro. Il commento del sorgente («~33 mW, SOT-23 is
fine») e' il riposo. Qui il deck risolto di regressione/<fase>/tb_mute_corto, con in piu', per
ognuno dei quattro blocchi: potenza media e massima di Q146 e Q148, corrente di collettore
massima di Q146, in tb_mute_corto_l56.csv (una riga per cella e blocco).

Uso: p7_l56.py <fase> <cartella> [r153]   -> <cartella>/tb_mute_corto.cir
"""
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
BLK = ("a", "f1", "f2", "b")


def aggiungi(t, r153=False):
    """Il deck risolto di tb_mute_corto con le misure di Q146 e Q148 (varianti_follower.py);
    con r153 anche la potenza della resistenza di collettore di Q146 (ADR-087), media e di picco."""
    save = "\n".join("save @q.x%s.q146[p] @q.x%s.q146[ic] @q.x%s.q148[p] @q.x%s.q148[ic]"
                     % (b, b, b, b) + (" @r.x%s.r153[i]" % b if r153 else "") for b in BLK)
    testa = ('echo "blk,modo_db,f_hz,vin_pk,k_att,caso,p_q146,pmax_q146,icmin_q146,'
             'p_q148,pmax_q148%s" > tb_mute_corto_l56.csv' % (",p_r153,pmax_r153" if r153 else ""))
    mis = []
    for b in BLK:
        if r153:
            mis += ["  let l56r153 = @r.x%s.r153[i] * @r.x%s.r153[i] * 4700" % (b, b),
                    "  meas tran l56pr AVG l56r153 from=4m to=8m",
                    "  meas tran l56xr MAX l56r153 from=4m to=8m"]
        mis += ["  meas tran l56p146 AVG @q.x%s.q146[p] from=4m to=8m" % b,
                "  meas tran l56x146 MAX @q.x%s.q146[p] from=4m to=8m" % b,
                "  meas tran l56i146 MIN @q.x%s.q146[ic] from=4m to=8m" % b,
                "  meas tran l56p148 AVG @q.x%s.q148[p] from=4m to=8m" % b,
                "  meas tran l56x148 MAX @q.x%s.q148[p] from=4m to=8m" % b,
                '  echo "%s,$gm,$f,$a,$k,$c,$&l56p146,$&l56x146,$&l56i146,$&l56p148,'
                '$&l56x148%s" >> tb_mute_corto_l56.csv' % (b.upper(), ",$&l56pr,$&l56xr" if r153 else "")]
    ancora = "  * --- blocco A ---"
    assert t.count(ancora) == 1
    t = t.replace(ancora, "\n".join(mis) + "\n" + ancora)
    a2 = "\nforeach sweep 1 2 3\n"
    assert t.count(a2) == 1
    return t.replace(a2, "\n" + save + "\n" + testa + "\n" + a2.lstrip("\n"))


if __name__ == "__main__":
    fase, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    t = open(os.path.join(L, "regressione", fase, "tb_mute_corto",
                          "tb_mute_corto_resolved.cir")).read()
    r153 = len(sys.argv) > 3 and sys.argv[3] == "r153"
    open(os.path.join(out, "tb_mute_corto.cir"), "w").write(aggiungi(t, r153))
    print("->", out)
