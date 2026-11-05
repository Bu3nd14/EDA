"""L72: il tempo sopra 0,87 V sul jack della Stax, dalle corse di stax/run/.

Il .dat di wrdata ha la colonna del tempo ripetuta davanti a ogni vettore: v(fix2jack) e' la colonna 5
(0 = tempo). Il tempo sopra soglia e' la somma degli intervalli con |v| > 0,87 V, con l'interpolazione
lineare agli attraversamenti (come i banchi di L45). Controllo: la corsa a 1,05 uF ridà la cifra
versionata (p10_stax_lunghi.csv di L45d2b3b2b2, p10_stax.csv di L66) entro 0,5 ms.

Uso: /usr/bin/python3 -I .../L72/script/analizza_stax.py  -> stax/stax_limite_alto.csv
"""
import csv
import os

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
RUN = os.path.join(L, "stax", "run")
ROOF = 0.87
P10 = 150.0
NOTI = {"G0_A_JQ110A_ds": 124.5, "G0_A_JQ110B_as": 124.4, "G0_A_Q146_ce": 124.2,
        "G0_F2_D158_cc": 120.0}   # L66 p10_stax.csv; Q132_be letto sotto


def legge_l66():
    p = os.path.join(os.path.dirname(os.path.dirname(L)), "2026-11-02", "L66", "p10_stax.csv")
    for r in csv.DictReader(open(p)):
        if r["modo"] == "G0_F2_Q132_be_k105":
            NOTI["G0_F2_Q132_be"] = float(r["fix2_sopra_ms"])


def sopra(dat):
    tot, prev = 0.0, None
    for riga in open(dat):
        c = riga.split()
        if len(c) < 6:
            continue
        t, v = float(c[0]), abs(float(c[5]))
        if prev is not None:
            t0, v0 = prev
            a0, a1 = v0 > ROOF, v > ROOF
            if a0 and a1:
                tot += t - t0
            elif a0 != a1:
                tx = t0 + (ROOF - v0) * (t - t0) / (v - v0)
                tot += (t - tx) if a1 else (tx - t0)
        prev = (t, v)
    return 1e3 * tot


legge_l66()
righe = []
for caso in sorted(NOTI):
    m = {tag: sopra(os.path.join(RUN, f"{caso}_{tag}", f"{caso}_{tag}.dat")) for tag in ("c1050", "c1265")}
    ctrl = abs(m["c1050"] - NOTI[caso]) <= 0.5
    lin = NOTI[caso] * 1.265 / 1.05
    righe.append({"caso": caso, "versionato_1u05_ms": NOTI[caso], "corsa_1u05_ms": round(m["c1050"], 1),
                  "controllo": "ok" if ctrl else "FALLITO", "corsa_1u265_ms": round(m["c1265"], 1),
                  "lineare_1u265_ms": round(lin, 1), "p10": "entro" if m["c1265"] <= P10 else "FUORI"})
    print(righe[-1])
with open(os.path.join(L, "stax", "stax_limite_alto.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(righe[0]))
    w.writeheader()
    w.writerows(righe)
