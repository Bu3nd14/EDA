#!/usr/bin/env python3
"""L29c: prima di correre una matrice, controlla DA DOVE parte ogni corsa (limitations #33).
Per ogni corsa_*.cir della directory, la stessa corsa con la tran accorciata a 1 ms: il log non
deve avere 'Transient op' ne' righe 'Error', e a t = 0 OUTA deve stare entro 0,5 V (e' l'offset
del blocco A, decine di mV) e il jack principale entro 1 mV (dietro il condensatore, a
regime). Le corse coi rail in rampa partono da 0 V per costruzione: per loro basta il log.

Uso: controlla_op.py DIR [NPAR=10]   -> DIR/_op/esito.csv, e stampa le corse che non vanno
"""
import csv
import glob
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

D = sys.argv[1]
NPAR = int(sys.argv[2]) if len(sys.argv) > 2 else 10
W = os.path.join(D, "_op")
os.makedirs(W, exist_ok=True)


def uno(path):
    nome = os.path.basename(path)[6:-4]
    L = open(path).read().splitlines()
    it = next(i for i, r in enumerate(L) if r.startswith("tran "))
    rampa = any("@vpp[pwl]" in r for r in L)
    out = L[:it] + ["save all", "tran 1e-05 1e-3 0 1e-05",
                    "print v(outa)[0] v(main_a)[0] v(mainjack)[0]", ".endc", ".end"]
    p = os.path.join(W, nome + ".cir")
    open(p, "w").write("\n".join(out) + "\n")
    r = subprocess.run(["/opt/homebrew/bin/ngspice", "-b", p], capture_output=True, text=True,
                       timeout=1800)
    txt = r.stdout + r.stderr
    open(p[:-4] + ".log", "w").write(txt)
    v = {}
    for l in txt.splitlines():
        l = l.strip()
        for k in ("outa", "main_a", "mainjack"):
            if l.startswith("v(%s)[0] = " % k):
                v[k] = float(l.split("=")[1])
    topt = "Transient op started" in txt
    err = sum(1 for l in txt.splitlines() if l.startswith("Error"))
    ok = (not topt and err == 0 and len(v) == 3
          and (rampa or (abs(v["outa"]) < 0.5 and abs(v["mainjack"]) < 1e-3)))
    return [nome, r.returncode, "si" if topt else "no", err, v.get("outa"), v.get("main_a"),
            v.get("mainjack"), "rampa" if rampa else "", "ok" if ok else "NON VA"]


corse = sorted(glob.glob(os.path.join(D, "corsa_*.cir")))
with ThreadPoolExecutor(NPAR) as ex:
    res = list(ex.map(uno, corse))
with open(os.path.join(W, "esito.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["corsa", "rc", "transient_op", "errori", "outa0", "main_a0", "mainjack0", "nota", "esito"])
    w.writerows(res)
male = [r for r in res if r[-1] != "ok"]
print("%d corse controllate, %d non vanno" % (len(res), len(male)))
for r in male:
    print("   ", r)
