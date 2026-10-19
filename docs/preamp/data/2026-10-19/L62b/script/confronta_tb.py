#!/usr/bin/env python3
"""L62b (copiato da L62a): il blocco del sorgente coi diodi (run/tb_base/); lo scarto di V1 riga per
riga contro lo stesso deck della regressione PRIMA (regressione/prima/, il blocco senza diodi di main
5036d8e3), che e' la base di L62a. Da confrontare con la riga `diodi` di L62a/blocco_sano.csv.

L62a: le varianti a blocco sano contro la base (run/tb_<v>/), scrive blocco_sano.csv e stampa.

  riposo   tb_op: corrente dei rail del blocco B e dei due finali
  V1       il margine di fase minimo di tb_loop, tb_loop_blockA, tb_loop_bufferfissa, tb_idss_loop
           (ADR-024: >= 45 gradi), e lo scarto massimo riga per riga contro la base
  P7       tb_mute_corto (mute e corto, ogni blocco, ogni modo e frequenza): il massimo della potenza
           dei finali, delle 22 ohm, del VAS e del suo carico, del moltiplicatore; la Tj del finale a
           60 C d'aria (62,5 C/W); la corrente di picco dei finali e l'uscita di picco (un limite che
           taglia in classe B si vede qui); Q146 da tb_mute_corto_l56.csv (L60d1)
"""
import csv
import os
import re

L62A = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V = ("base",)
LOOP = (("tb_loop", "tb_loop_margini.csv"), ("tb_loop_blockA", "tb_loop_blockA.csv"),
        ("tb_loop_bufferfissa", "tb_loop_bufferfissa.csv"), ("tb_idss_loop", "tb_idss_loop_margini.csv"))
P7 = ("p_q132", "p_q133", "p_r134", "p_r135", "p_q122", "p_q125", "p_q127")


def leggi(v, deck, f):
    if v == "prima":
        return list(csv.DictReader(open(os.path.join(L62A, "regressione", "prima", deck, f))))
    return list(csv.DictReader(open(os.path.join(L62A, "run", "tb_" + v, deck, f))))


def op(v):
    t = open(os.path.join(L62A, "run", "tb_" + v, "tb_op", "tb_op.log")).read()
    g = lambda k: float(re.search(r"^%s = (\S+)" % re.escape(k), t, re.M).group(1))
    if "source stepping failed" in t:
        return None
    return -g("i(vpp)") * 1e3, g("@q132[ic]") * 1e3, -g("@q133[ic]") * 1e3


righe = []
for v in V:
    r = {"variante": v}
    o = op(v)
    r["I_rail_piu_mA"], r["Iq_npn_mA"], r["Iq_pnp_mA"] = ("%.2f" % x for x in o)
    for deck, f in LOOP:
        a, b = leggi(v, deck, f), leggi("prima", deck, f)
        if len(a) != len(b):
            raise SystemExit("%s: righe %d contro %d" % (deck, len(a), len(b)))
        pm = [float(x["pm_deg"]) for x in a]
        r["V1_min_%s" % deck] = "%.2f" % min(pm)
        r["V1_scarto_max_%s" % deck] = "%.2f" % max(abs(float(x["pm_deg"]) - float(y["pm_deg"])) for x, y in zip(a, b))
    p7 = leggi(v, "tb_mute_corto", "tb_mute_corto_regime.csv")
    for k in P7:
        r["P7_%s_W" % k[2:]] = "%.3f" % max(abs(float(x[k])) for x in p7)
    r["P7_Tj_finale_60C"] = "%.0f" % (60 + 62.5 * max(float(r["P7_q132_W"]), float(r["P7_q133_W"])))
    r["P7_icmax_finale_mA"] = "%.0f" % (1e3 * max(max(float(x["icmax_q132"]), -float(x["icmin_q133"])) for x in p7))
    r["P7_voutpk_max_V"] = "%.3f" % max(abs(float(x["voutpk"])) for x in p7)
    l56 = leggi(v, "tb_mute_corto", "tb_mute_corto_l56.csv")
    r["P7_q146_W"] = "%.3f" % max(float(x["p_q146"]) for x in l56)
    righe.append(r)

with open(os.path.join(L62A, "blocco_sano.csv"), "w", newline="") as fo:
    w = csv.DictWriter(fo, fieldnames=list(righe[0]))
    w.writeheader()
    w.writerows(righe)
for k in righe[0]:
    print("%-34s" % k + "".join("%12s" % r[k] for r in righe))
