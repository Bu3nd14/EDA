#!/usr/bin/env python3
"""L29b2: ricerca del profilo del comando dei LED col simulatore veloce. Scratch.

Uso (venv con numpy):  /Users/roberto/EDA/env/venv/bin/python3 cerca.py valuta NOME
                       /Users/roberto/EDA/env/venv/bin/python3 cerca.py cerca [GIRI] [TD] [ACC]

Un profilo = log10 della corrente del generatore di ciascun LED a d = 0, 0,05, ..., 1
(21 nodi, passo 0,05, log-lineare fra i nodi), piu' Td e ACC (il tempo in cui la velocita' di d passa
da +1/Td a -1/Td: d(t) ha accelerazione limitata anche all'inizio e alla fine).

Per ogni profilo:
- corse: "ev" (inserzione, 0,5 s dopo d = 1 il rele', 1 s di mute, rilascio),
  "lungo" (lo stesso con 30 s di mute: la serie si fa buia), inversioni a d = 0,3 / 0,5 / 0,75;
- C2 dell'inviluppo (c2np, identico a v2_metodo) a 1 kHz e a 20 Hz sul jack principale,
  NORMALIZZATO al coseno ideale della stessa durata (Td + ACC): 1 vuol dire "come il coseno";
- vincoli: carico sulla sorgente >= 100 kohm (E3) in ogni istante di ogni corsa, e al
  chiudersi del rele' il residuo a 1 kHz al jack <= 0,2 mV.
Il 10 M del banco sull'anodo e' nel modello del LED (R_SHUNT) come nel deck; con None e'
il comando della scheda, senza.
L'obiettivo: il peggiore fra 1 kHz e 20 Hz del rapporto col coseno, piu' le penalita'.
"""
import json
import math
import os
import random
import sys
from multiprocessing import Pool

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
import sur  # noqa: E402
import c2np  # noqa: E402

FS = c2np.FS
DT = 1e-4                 # passo delle celle: tau >= 2,7 ms
R_SHUNT = 1e7
A = sur.A_MAIN
NOD = [i / 20 for i in range(21)]
IRIP = 1e-8


def interp_log(d, knots):
    return 10 ** float(np.interp(d, NOD, knots))


def dtraj(n, t_ins, t_rel, td, acc):
    """d(t) ad accelerazione limitata: velocita' target +1/td da t_ins, -1/td da t_rel;
    all'arrivo a 0 o a 1 la velocita' si annulla (frenata anticipata: d non supera i capi)."""
    v = 1.0 / td
    a = 2 * v / acc
    d = np.zeros(n)
    x, vel = 0.0, 0.0
    for k in range(n):
        t = k * DT
        vt = 0.0 if t < t_ins else (v if t < t_rel else -v)
        # frenata: se la distanza dal capo verso cui si va e' <= vel^2/(2a), target 0
        if vel > 0 and (1 - x) <= vel * vel / (2 * a):
            vt = 0.0
        if vel < 0 and x <= vel * vel / (2 * a):
            vt = 0.0
        vel += max(min(vt - vel, a * DT), -a * DT)
        x = min(max(x + vel * DT, 0.0), 1.0)
        d[k] = x
    return d


def cella(ks, d):
    n = len(d)
    i_src = [interp_log(x, ks) for x in d]
    xs0 = sur.xt_di(sur.i_led(i_src[0], R_SHUNT))
    return np.array(sur.evolvi(lambda k: i_src[k], n, DT, xs0, R_SHUNT))


def corsa(prof, t_rel, tf):
    n = int(tf / DT)
    d = dtraj(n, 0.5, t_rel, prof["td"], prof["acc"])
    xs, xp = cella(prof["s"], d), cella(prof["p"], d)
    rs, rp = 10 ** xs, 10 ** xp
    par = rp * 1e6 / (rp + 1e6)
    g = par / (rs + 1.5 + par)
    carico = rs + par
    return d, g, carico


def a_fs(g, t0, t1):
    """g a DT -> a FS fra t0 e t1."""
    tt = np.arange(int(t0 * FS), int(t1 * FS)) / FS
    return np.interp(tt, np.arange(len(g)) * DT, g), tt[0]


_COS = {}


def ideale(f, T):
    key = (f, round(T, 4))
    if key not in _COS:
        n = int((0.5 + T + 0.5) * FS)
        u = np.clip((np.arange(n) / FS - 0.5) / T, 0, 1)
        _COS[key] = c2np.c2(0.5 + 0.5 * np.cos(np.pi * u), 0.5, T, f, A)[0]
    return _COS[key]


def valuta(prof):
    td, acc = prof["td"], prof["acc"]
    T = td + acc
    out = {"td": td, "acc": acc}
    pen = 0.0
    t_rele = 0.5 + T + 0.5
    g_full = None
    eventi = []
    for nome, t_rel, tf in (("ev", t_rele + 1.0, t_rele + 1.0 + T + 1.5),
                            ("lungo", t_rele + 30.0, t_rele + 30.0 + T + 1.5)):
        d, g, car = corsa(prof, t_rel, tf)
        g_full = g[0]
        k_rele = int(t_rele / DT)
        res = A * g[k_rele] * 1e3
        out["res_rele_mV_" + nome] = res
        if res > 0.2:
            pen += (res - 0.2) * 5
        out["carico_min_" + nome] = float(car.min())
        eventi.append(("ins_" + nome, g, 0.5, T + 0.5, 0.0))
        eventi.append(("rel_" + nome, g, t_rel, T + 0.5, g_full))
        if car.min() < 1e5:
            pen += (1e5 - car.min()) / 1e4
    for dinv in (0.3, 0.5, 0.75):
        # il rilascio parte quando d arriva a dinv (in salita)
        d, _, _ = corsa(prof, 1e9, 0.5 + T + 0.5)
        k = int(np.argmax(d >= dinv))
        t_inv = k * DT
        d, g, car = corsa(prof, t_inv, t_inv + T + 1.5)
        eventi.append(("inv%02d" % round(100 * dinv), g, t_inv, T + 0.5, g_full))
        out["carico_min_inv%02d" % round(100 * dinv)] = float(car.min())
        if car.min() < 1e5:
            pen += (1e5 - car.min()) / 1e4
    peggio = 0.0
    for nome, g, t_ev, fin, rif in eventi:
        if nome == "ins_lungo":
            continue
        gg, t0 = a_fs(g, max(t_ev - 0.8, 0.0), min(t_ev + fin + 0.5, len(g) * DT))
        for f in (1000.0, 20.0):
            v = c2np.c2(gg, t_ev, fin, f, A, rif=rif, t0=t0)[0]
            r = v / ideale(f, T)
            out["%s_%g" % (nome, f)] = v * 1e3
            peggio = max(peggio, r)
    out["peggio_su_coseno"] = peggio
    out["pen"] = pen
    out["obiettivo"] = peggio + pen
    return out


def v3():
    s = [np.interp(x, [0, 0.1, 0.45, 0.5, 1], [math.log10(v) for v in (20e-3, 0.2e-3, 4.5e-6, IRIP, IRIP)]) for x in NOD]
    p = [math.log10(IRIP * 2e6 ** min(max((x - 0.5) / 0.5, 0), 1)) for x in NOD]
    return {"s": s, "p": p}


def v4():
    s = [np.interp(x, [0, 0.1, 0.45, 0.75, 0.8, 1], [math.log10(v) for v in (20e-3, 0.2e-3, 4.5e-6, 0.19e-6, IRIP, IRIP)]) for x in NOD]
    return {"s": s, "p": v3()["p"]}


def _job(p):
    try:
        return p, valuta(p)
    except Exception as e:  # noqa: BLE001
        return p, {"obiettivo": 1e9, "errore": repr(e)}


def monotono(ks, cresce):
    ks = list(ks)
    for i in range(1, len(ks)):
        ks[i] = max(ks[i], ks[i - 1]) if cresce else min(ks[i], ks[i - 1])
    lo, hi = math.log10(IRIP), math.log10(20e-3)
    return [min(max(x, lo), hi) for x in ks]


def cerca(giri, td, acc):
    random.seed(29)
    base = dict(v4(), td=td, acc=acc)
    migliore = _job(base)[1]
    best = base
    print("partenza v4:", json.dumps(migliore), flush=True)
    passo_ = 0.6
    with Pool(10) as pool:
        for giro in range(giri):
            cand = []
            for _ in range(20):
                c = {"td": td, "acc": acc,
                     "s": monotono([x + random.gauss(0, passo_) * (random.random() < 0.4) for x in best["s"]], False),
                     "p": monotono([x + random.gauss(0, passo_) * (random.random() < 0.4) for x in best["p"]], True)}
                c["s"][0] = math.log10(20e-3)
                c["p"][-1] = math.log10(20e-3)
                cand.append(c)
            for c, r in pool.map(_job, cand):
                if r["obiettivo"] < migliore["obiettivo"]:
                    migliore, best = r, c
            if giro % 5 == 4:
                passo_ = max(passo_ * 0.8, 0.05)
            print("giro %d  obiettivo %.3f  peggio/coseno %.3f  pen %.3f" % (
                giro, migliore["obiettivo"], migliore["peggio_su_coseno"], migliore["pen"]), flush=True)
            json.dump({"profilo": best, "esito": migliore},
                      open(os.path.join(QUI, "migliore_td%g_acc%g.json" % (td, acc)), "w"), indent=1)
    return best, migliore


if __name__ == "__main__":
    if sys.argv[1] == "valuta":
        p = {"v3": v3, "v4": v4}[sys.argv[2]]()
        p.update(td=float(sys.argv[3]) if len(sys.argv) > 3 else 6.0,
                 acc=float(sys.argv[4]) if len(sys.argv) > 4 else 1e-3)
        print(json.dumps(valuta(p), indent=1))
    else:
        cerca(int(sys.argv[2]) if len(sys.argv) > 2 else 40,
              float(sys.argv[3]) if len(sys.argv) > 3 else 6.0,
              float(sys.argv[4]) if len(sys.argv) > 4 else 0.5)
