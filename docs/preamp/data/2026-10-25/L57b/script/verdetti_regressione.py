#!/usr/bin/env python3
"""L57b: le cifre di verdetto dei quattro deck dell'ingresso, prima e dopo il limitatore.

  V1  tb_loop_blockA.csv e _trim.csv: il margine di fase minimo del blocco A con CWIRE <= 1 nF
      (ADR-024), in tutto e per carico 1 (il carico di ADR-023), contro 45 gradi
  E3  tb_e3_e5_e3.csv / tb_trim_e3.csv: |Zin| minima al jack, contro 100 kOhm (CSEL 68 pF il caso
      peggiore)
  E5  tb_e3_e5_e5.csv / tb_trim_e5.csv: il rumore massimo, contro 9,90 uV (E5 meno le quote di
      ADR-020 / ADR-022, come nei deck)
  F1  f1_selettore.csv: il gradino massimo al jack principale nei modi 0 / 3 / 10 dB (non 99, il
      controfattuale), in uV

Uso: /usr/bin/python3 verdetti_regressione.py   -> regressione/verdetti.csv
"""
import csv
import os

QUI = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(os.path.dirname(QUI), "regressione")
NF = {"1f": 1e-15, "47p": 47e-12, "100p": 1e-10, "220p": 2.2e-10, "470p": 4.7e-10, "1n": 1e-9,
      "2.2n": 2.2e-9, "4.7n": 4.7e-9}


def rows(fase, deck, f):
    return list(csv.DictReader(open(os.path.join(R, fase, deck, f))))


def v1(fase):
    x = [r for r in rows(fase, "tb_loop_blockA", "tb_loop_blockA.csv") if NF[r["cwire"]] <= 1e-9]
    y = [r for r in rows(fase, "tb_loop_blockA", "tb_loop_blockA_trim.csv") if NF[r["cwire"]] <= 1e-9]
    return min(float(r["pm_deg"]) for r in x + y), \
        min(float(r["pm_deg"]) for r in x if r["carico"] == "1")


out = []
for fase in ("prima", "dopo"):
    pm, pm1 = v1(fase)
    e3 = min(float(r["zmin_ohm"]) for r in rows(fase, "tb_e3_e5", "tb_e3_e5_e3.csv")
             + rows(fase, "tb_trim", "tb_trim_e3.csv"))
    e5 = max(float(r["onoise_uv"]) for r in rows(fase, "tb_e3_e5", "tb_e3_e5_e5.csv")
             + rows(fase, "tb_trim", "tb_trim_e5.csv"))
    f1 = rows(fase, "tb_f1_selettore", "f1_selettore.csv")
    f1m = max(abs(float(r[k])) for r in f1 if r["modo"] != "99"
              for k in ("jf_su_uv", "jf_giu_uv", "jm_su_uv", "jm_giu_uv") if r[k])
    out.append({"fase": fase, "v1_pm_min_deg": "%.2f" % pm, "v1_pm_min_carico1_deg": "%.2f" % pm1,
                "e3_zmin_kohm": "%.1f" % (e3 / 1e3), "e5_max_uv": "%.3f" % e5,
                "f1_gradino_max_uv": "%.4g" % f1m})
with open(os.path.join(R, "verdetti.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, list(out[0]))
    w.writeheader()
    w.writerows(out)
for r in out:
    print(r)
