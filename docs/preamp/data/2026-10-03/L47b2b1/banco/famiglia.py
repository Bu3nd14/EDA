"""famiglia.py - L47b2b1: una famiglia di profili a quattro parametri, sulla griglia, con rapido.py.

Il profilo e' una tabella (d, log10 I) per stringa, simmetrica nei due versi (come v4):
  serie:        log-lineare da ION (d = 0) a IRIP (d = a), poi IRIP;
  derivazione:  IRIP fino a d = b; da I0 a d = b a ION a d = 1 con forma
                log10 I = log10 I0 + (log10 ION - log10 I0) * ((d - b)/(1 - b))^g.
Tabelle campionate a passo 0,025 in d (pochi punti in piu' non cambiano niente: interpolazione
in log come BILS del banco V2).

Per ogni profilo, sulle curve A-E: S peggiore (due versi), il mute meno profondo, E3 a 20 kHz al
connettore (rapido.zin_e3) e il carico del solo ramo della cella (criterio di L29b, post.py).

    /usr/bin/python3 famiglia.py <uscita.csv> [td_s]
"""
import csv
import itertools
import math
import sys
from multiprocessing import Pool

import rapido as R

ION, IRIP = 7e-3, 10e-9
# il tempo della sfumatura: 3 s (ADR-059), o quello dato come secondo argomento (L47b2b1: E3 al rilascio)
TD = float(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[0].endswith("famiglia.py") else 3.0
LMAX, LMIN = math.log10(ION), math.log10(IRIP)
GRIGLIA = {
    "a": [0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6],
    "b": [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
    "i0": [1e-7, 1e-6, 3e-6],
    "g": [0.5, 0.7, 1.0, 1.4],
}
PASSO_D = 0.025


def tabelle(a, b, i0, g):
    nodi = sorted(set([round(k * PASSO_D, 6) for k in range(int(round(1 / PASSO_D)) + 1)] + [a, b]))
    serie = [(d, LMAX + (LMIN - LMAX) * min(d / a, 1.0)) for d in nodi]
    deriv = []
    for d in nodi:
        if d < b:
            deriv.append((d, LMIN))
        else:
            u = (d - b) / (1 - b)
            deriv.append((d, math.log10(i0) + (LMAX - math.log10(i0)) * u ** g))
    # il gradino a d = b (da IRIP a I0) in un passo di 1e-4 in d
    k = next(j for j, (d, _) in enumerate(deriv) if d >= b)
    deriv.insert(k, (b - 1e-4, LMIN))
    return serie, deriv


def funzioni(serie, deriv):
    def f(t):
        def g(d):
            d = min(max(d, 0.0), 1.0)
            return 10 ** R.pwl(d, t)
        return g
    return f(serie), f(deriv)


def valuta(p):
    a, b, i0, g = p
    fs, fp = funzioni(*tabelle(a, b, i0, g))
    out = {"a": a, "b": b, "i0": i0, "g": g}
    S, prof, e3, car = 0.0, -999.0, 1e12, 1e12
    v = {"Si": 0.0, "Sr": 0.0, "Ei": 1e12, "Er": 1e12, "Ci": 1e12, "Cr": 1e12}
    for c in "ABCDE":
        r = R.sfumatura(fs, fp, TD, (c, c))
        out["S_" + c] = round(max(r["S_ins_dB"], r["S_rel_dB"]), 2)
        S = max(S, r["S_ins_dB"], r["S_rel_dB"])
        prof = max(prof, r["liv_mute_dB"])
        e3 = min(e3, r["e3_min"])
        car = min(car, r["carico_min"])
        v["Si"], v["Sr"] = max(v["Si"], r["S_ins_dB"]), max(v["Sr"], r["S_rel_dB"])
        v["Ei"], v["Er"] = min(v["Ei"], r["e3_ins"]), min(v["Er"], r["e3_rel"])
        v["Ci"], v["Cr"] = min(v["Ci"], r["carico_ins"]), min(v["Cr"], r["carico_rel"])
    out.update({"S_max": round(S, 2), "mute_max_dB": round(prof, 1),
                "E3_min_k": round(e3 / 1e3, 1), "carico_min_k": round(car / 1e3, 1),
                # per verso, peggiore sulle curve: l'inserimento e il rilascio
                "S_ins": round(v["Si"], 2), "S_rel": round(v["Sr"], 2),
                "E3_ins_k": round(v["Ei"] / 1e3, 1), "E3_rel_k": round(v["Er"] / 1e3, 1),
                "carico_ins_k": round(v["Ci"] / 1e3, 1), "carico_rel_k": round(v["Cr"] / 1e3, 1)})
    return out


def main():
    punti = list(itertools.product(*GRIGLIA.values()))
    with Pool(10) as pool:
        righe = pool.map(valuta, punti, chunksize=4)
    with open(sys.argv[1], "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(righe[0]))
        w.writeheader()
        w.writerows(righe)
    for nome, chiave in (("E3 a 20 kHz al connettore", "E3_min_k"), ("ramo della cella (L29b)", "carico_min_k")):
        ok = [r for r in righe if r[chiave] >= 102 and r["mute_max_dB"] <= -70]
        ok.sort(key=lambda r: r["S_max"])
        print("== %s >= 102 k, mute <= -70 dB: %d profili su %d" % (nome, len(ok), len(righe)))
        for r in ok[:6]:
            print("   ", r)


if __name__ == "__main__":
    main()
