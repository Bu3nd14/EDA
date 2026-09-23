#!/usr/bin/env python3
"""L40: i limiti per tono della «Nota su E5 — la quota del ripple» (ADR-020),
ricalcolati sul PSRR vigente. ADR-020, «Da riaprire se»: quando la Fase 4 abbassa
il PSRR+ minimo la quota (1 uV) resta e i limiti per tono si ricalcolano.

Metodo di L18 (reports/2026-09-13-L18-vincolo-psrr.md §4): PSRR minimo fra le
modalita' di guadagno, interpolato in log f; limite di un tono solo =
1 uV x 10^(PSRR/20); rumore bianco sul solo rail + = 1 uV / sqrt(integrale
20 Hz-20 kHz di 10^(-PSRR+/10) df).

Uso: /usr/bin/python3 limiti_psrr.py <dir> <prefisso> <modi...>
  es. (controllo, deve ridare la tabella di L18 in REQUIREMENTS.md):
      limiti_psrr.py docs/preamp/data/2026-09-13 tb_zout_psrr_noise 0db 10db
  es. (L40): limiti_psrr.py <...>/dopo/tb_zout_psrr_noise tb_zout_psrr_noise 0db 3db 10db
"""
import csv
import math
import os
import sys

d, pref = sys.argv[1], sys.argv[2]
modi = sys.argv[3:]


def curva(rail, modo):
    p = os.path.join(d, "%s_psrr%s_%s.csv" % (pref, rail, modo))
    r = list(csv.reader(open(p)))[1:]
    return [(float(a[0]), float(a[1])) for a in r]


def minimo(rail):
    cc = [curva(rail, m) for m in modi]
    f = [x[0] for x in cc[0]]
    for c in cc:
        assert [x[0] for x in c] == f, "griglie diverse"
    return f, [min(c[i][1] for c in cc) for i in range(len(f))], \
        [modi[min(range(len(cc)), key=lambda j: cc[j][i][1])] for i in range(len(f))]


def interp(f, y, x):
    lx = math.log10(x)
    for i in range(len(f) - 1):
        a, b = math.log10(f[i]), math.log10(f[i + 1])
        if a <= lx <= b:
            return y[i] + (y[i + 1] - y[i]) * (lx - a) / (b - a)
    raise ValueError(x)


fp, pp, mp = minimo("p")
fm, pm, mm = minimo("m")
print("modo peggiore, rail +: %s; rail -: %s" % (sorted(set(mp)), sorted(set(mm))))
print("| f | PSRR rail + | V+ massimo | PSRR rail − | V− massimo |")
print("|---|---|---|---|---|")
for x in (50, 100, 1000, 10000, 20000):
    a, b = interp(fp, pp, x), interp(fm, pm, x)
    va, vb = 1e-6 * 10 ** (a / 20), 1e-6 * 10 ** (b / 20)

    def fmt(v):
        return "%.3g mV RMS" % (v * 1e3) if v >= 1e-4 else "%.3g µV RMS" % (v * 1e6)
    print("| %s | %.2f dB | %s | %.2f dB | %s |" % (
        "%g Hz" % x if x < 1000 else "%g kHz" % (x / 1000), a, fmt(va), b, fmt(vb)))
# rumore bianco sul rail +: integrale trapezoidale in f sulla griglia, 20 Hz-20 kHz
acc = 0.0
for i in range(len(fp) - 1):
    if fp[i] >= 20 and fp[i + 1] <= 20000 * 1.0001:
        g0, g1 = 10 ** (-pp[i] / 10), 10 ** (-pp[i + 1] / 10)
        acc += 0.5 * (g0 + g1) * (fp[i + 1] - fp[i])
print("rumore bianco sul solo rail +: <= %.0f nV/rtHz" % (1e-6 / math.sqrt(acc) * 1e9))
