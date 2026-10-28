#!/usr/bin/env python3
"""L54b3b: the linear regression of a Monte Carlo margin on the normalised parameters, and the
worst corner it predicts.

  /usr/bin/python3 -I regressione.py <campioni.csv> <intervalli.json> <an.csv> <caso> <colonna>
                     <min|max> <toll_angolo.json> [<testo.txt>]

<an.csv> is analizza_mc.py's output; its rows "<prefisso>mcNNN/<caso>" are matched to the rows of
campioni.csv by mcNNN. The model: y = b0 + sum b_i u_i, u_i in [-1, 1] (least squares, normal
equations, stdlib). The corner: every u_i at -sign(b_i) for min (the margin's worst is its lowest),
+sign(b_i) for max; its predicted y = b0 - sum |b_i| (min) or b0 + sum |b_i| (max), written with the
MC's own extreme and the fit's residual. The corner's absolute values go to <toll_angolo.json>, a
--toll file; it must then be RUN (the model is linear, the circuit is not).
"""
import csv
import json
import sys


def risolvi(a, b):
    n = len(b)
    m = [row[:] + [b[i]] for i, row in enumerate(a)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(m[r][c]))
        m[c], m[p] = m[p], m[c]
        if abs(m[c][c]) < 1e-15:
            raise SystemExit("matrice singolare alla colonna %d" % c)
        for r in range(n):
            if r != c:
                f = m[r][c] / m[c][c]
                m[r] = [x - f * y for x, y in zip(m[r], m[c])]
    return [m[i][n] / m[i][i] for i in range(n)]


def main():
    fc, fi, fa, caso, col, verso, fout = sys.argv[1:8]
    ftxt = sys.argv[8] if len(sys.argv) > 8 else None
    camp = {r["campione"]: r for r in csv.DictReader(open(fc))}
    nomi = [k for k in next(iter(camp.values())) if k != "campione"]
    iv = json.load(open(fi))
    X, y = [], []
    for r in csv.DictReader(open(fa)):
        et, c = r["caso"].split("/")
        if c != caso or r.get(col, "") == "" or "mc" not in et:
            continue
        mc = et[et.index("mc"):]
        if mc not in camp:
            continue
        X.append([1.0] + [float(camp[mc][k]) for k in nomi])
        y.append(float(r[col]))
    n, p = len(y), len(nomi) + 1
    assert n > p, ("campioni insufficienti", n, p)
    ata = [[sum(X[k][i] * X[k][j] for k in range(n)) for j in range(p)] for i in range(p)]
    aty = [sum(X[k][i] * y[k] for k in range(n)) for i in range(p)]
    b = risolvi(ata, aty)
    res = [y[k] - sum(b[i] * X[k][i] for i in range(p)) for k in range(n)]
    rms = (sum(e * e for e in res) / (n - p)) ** 0.5
    s = -1 if verso == "min" else 1
    ang = {nomi[i - 1]: (s if b[i] >= 0 else -s) for i in range(1, p)}
    pred = b[0] + s * sum(abs(x) for x in b[1:])
    val = {k: (iv[k][0] + iv[k][1]) / 2 + ang[k] * (iv[k][1] - iv[k][0]) / 2 for k in nomi}
    t = {"nota": "L54b3b angolo %s %s di %s (regressione su %d campioni)" % (verso, col, caso, n),
         "fattori": {}, "vos": {}}
    for k, v in val.items():
        if k == "vref":
            t["vref"] = v
        elif k == "ib":
            t["ib"] = v
        elif k.startswith("vos_"):
            t["vos"][k[4:]] = v
        else:
            t["fattori"][k] = v
    json.dump(t, open(fout, "w"), sort_keys=True, indent=0)
    righe = ["%s %s (%s): %d campioni, b0 %.4g, residuo rms %.3g; MC min %.4g max %.4g; "
             "angolo previsto %.4g" % (caso, col, verso, n, b[0], rms, min(y), max(y), pred)]
    for i in sorted(range(1, p), key=lambda i: -abs(b[i]))[:12]:
        righe.append("  %-10s %+.4g" % (nomi[i - 1], b[i]))
    print("\n".join(righe))
    if ftxt:
        open(ftxt, "a").write("\n".join(righe) + "\n")


main()
