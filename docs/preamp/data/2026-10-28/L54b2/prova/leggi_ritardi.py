"""Legge prova/tb_ritardi.csv (t, v(inp), t, v(outt), t, v(outc)): il ritardo dal passaggio
dell'ingresso per la soglia (1,25 V - 0,4 mV) al passaggio dell'uscita per 2,5 V, per TI e CMPTA."""
import sys

rows = []
for line in open(sys.argv[1]):
    p = line.split()
    if len(p) >= 6:
        rows.append((float(p[0]), float(p[1]), float(p[3]), float(p[5])))
THR = 1.25 - 0.4e-3


def first(t0, f):
    for a, b in zip(rows, rows[1:]):
        if a[0] >= t0 and f(a) * f(b) <= 0 and f(a) != f(b):
            return a[0] + f(a) / (f(a) - f(b)) * (b[0] - a[0])
    return None


for nome, k in (("TLV1701 (TI)", 2), ("CMPTA (tarato)", 3)):
    out = []
    for t0, lab in ((40e-6, "tpLH"), (540e-6, "tpHL")):
        ti = first(t0, lambda r: r[1] - THR)
        to = first(t0, lambda r: r[k] - 2.5)
        out.append("%s %.0f ns" % (lab, (to - ti) * 1e9))
    print("%s: %s" % (nome, ", ".join(out)))
