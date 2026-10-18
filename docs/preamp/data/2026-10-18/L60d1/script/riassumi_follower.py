#!/usr/bin/env python3
"""L60d1: il riassunto delle varianti di varianti_follower.py, una riga per variante, in
follower/riassunto.csv:
  P7      Q146 potenza media / di picco massime e corrente massima; Q148 potenza media massima
          (tb_mute_corto_l56.csv, ogni blocco e ogni caso)
  sonda   |jack principale| massimo dopo 0,2 s nella corsa «sempre in mute», |Ic Q146| massima
  V1      margine minimo sulle posizioni che contano: blocco B pos 1, blocco A cavo <= 1 nF,
          buffer fisso pos 1 (criteri di margini.py, ADR-024)
  V3      clip + / -, recupero col guadagno E la continua stimati (come v3_con_continua.py di
          L46b), e la THD del .four di tb_v3_overload (cifra di modello, non V4)
Col venv (numpy): env/venv/bin/python3 riassumi_follower.py
"""
import csv
import os
import re

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
F = os.path.join(L, "follower")


def p7(v):
    rr = list(csv.DictReader(open(os.path.join(F, v, "p7", "tb_mute_corto_l56.csv"))))
    return (max(float(r["p_q146"]) for r in rr), max(float(r["pmax_q146"]) for r in rr),
            -min(float(r["icmin_q146"]) for r in rr), max(float(r["p_q148"]) for r in rr))


def sonda(v):
    d = np.loadtxt(os.path.join(F, v, "sonda", "sonda.dat"))
    t = d[:, 0]
    k = t > 0.2
    return float(np.max(np.abs(d[k, 1]))), float(np.max(np.abs(d[:, 3])))


def margini(v):
    run = os.path.join(F, v, "run")
    m = []
    for deck, f, filtro in (
            ("tb_loop", "tb_loop_margini.csv", lambda r: r["pos"] == "1"),
            ("tb_loop_blockA", "tb_loop_blockA.csv",
             lambda r: r["cwire"] in ("1f", "47p", "100p", "220p", "470p", "1n")),
            ("tb_loop_bufferfissa", "tb_loop_bufferfissa.csv", lambda r: r["pos"] == "1")):
        rr = [r for r in csv.DictReader(open(os.path.join(run, deck, f))) if filtro(r)]
        # un pm vuoto: il deck non ha trovato |T| = 1 (si conta come nan, e si guarda a mano)
        m.append(min(float(r["pm_deg"]) if r["pm_deg"] else float("nan") for r in rr))
    return m


def v3(v):
    d = os.path.join(F, v, "run", "tb_v3_overload")
    a = np.loadtxt(os.path.join(d, "tb_v3_overload.csv"), delimiter=",", skiprows=1)
    t, src, out = a[:, 0], a[:, 1], a[:, 3]
    ov = (t >= 1e-3) & (t <= 6e-3)
    lin = (t >= 12e-3) & (t <= 20e-3)
    A = np.vstack([src[lin], np.ones(lin.sum())]).T
    g, dc = np.linalg.lstsq(A, out[lin], rcond=None)[0]
    err = np.abs(out - (g * src + dc))
    dopo6 = np.where(t > 6e-3)[0]
    fuori = dopo6[err[dopo6] >= 0.05 * g * 0.5]
    rec = (t[fuori[-1]] - 6e-3) * 1e6 if len(fuori) else 0.0
    log = open(os.path.join(d, "tb_v3_overload.log"), errors="replace").read()
    thd = re.findall(r"THD:\s*([0-9.eE+-]+)\s*%", log)
    return float(out[ov].max()), float(out[ov].min()), rec, (thd[-1] if thd else "")


righe = []
for v in sorted(d for d in os.listdir(F) if os.path.isdir(os.path.join(F, d))):
    a, b, c, e = p7(v)
    j, i = sonda(v)
    m = margini(v)
    cp, cn, rec, thd = v3(v)
    righe.append([v, "%.4f" % a, "%.3f" % b, "%.4f" % c, "%.4f" % e, "%.4g" % j, "%.4f" % i,
                  "%.2f" % m[0], "%.2f" % m[1], "%.2f" % m[2], "%+.3f" % cp, "%+.3f" % cn,
                  "%.2f" % rec, thd])
testa = ["variante", "p7_q146_W", "p7_q146_picco_W", "p7_q146_ic_A", "p7_q148_W",
         "jack_mute_V", "sonda_q146_ic_A", "v1_B_deg", "v1_A_deg", "v1_buffer_deg",
         "clip_pos_V", "clip_neg_V", "recupero_us", "thd_modello_pct"]
with open(os.path.join(F, "riassunto.csv"), "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(testa)
    w.writerows(righe)
for k, n in enumerate(testa):
    print("%-17s" % n + "".join("%12s" % r[k] for r in righe))
