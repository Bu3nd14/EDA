#!/usr/bin/env python3
"""L38 - cifre CALCOLATE (non simulate) per ADR-032, la soglia di V2.

Solo stdlib. Nessun circuito: una formula e un filtro digitale su forme d'onda
ideali. Serve a due cose:

1. La stima d'udibilita' di NC-028 applicata alla soglia da 100 uV:
   dB SPL di picco a 1 m ~= 96 + 20*log10(21,1 * dV / 2,83)
   (finale x21,1, Klipsch Heresy 96 dB/1 W/1 m = 2,83 V). E' un limite
   superiore grossolano (NC-028): tratta il fronte come un tono.
   Le righe della tabella di NC-028 si riproducono come controllo.

2. Quanto l'ORDINE del passa-alto a 20 Hz pesa sul picco filtrato 20 Hz-20 kHz
   di un gradino netto e di rampe (il "rilascio lento"). Passa-basso sempre
   Butterworth 2 ordine a 20 kHz. fs 96 kHz, trasformata bilineare.

Uso:  /usr/bin/python3 calcolo_v2.py > calcolo_v2.out.txt
"""
import math

FS = 96000.0


def spl(dv):
    return 96 + 20 * math.log10(21.1 * dv / 2.83)


def biquad(kind, f0, q):
    w = 2 * math.pi * f0 / FS
    c = math.cos(w)
    a = math.sin(w) / (2 * q)
    if kind == "hp":
        b = [(1 + c) / 2, -(1 + c), (1 + c) / 2]
    else:
        b = [(1 - c) / 2, 1 - c, (1 - c) / 2]
    den = [1 + a, -2 * c, 1 - a]
    return [x / den[0] for x in b], [x / den[0] for x in den]


def hp_first(f0):
    k = math.tan(math.pi * f0 / FS)
    return [1 / (1 + k), -1 / (1 + k)], [1.0, (k - 1) / (k + 1)]


def run(x, stages):
    for b, den in stages:
        y = [0.0] * len(x)
        x1 = x2 = y1 = y2 = 0.0
        if len(b) == 2:
            for i, xi in enumerate(x):
                yi = b[0] * xi + b[1] * x1 - den[1] * y1
                x1, y1 = xi, yi
                y[i] = yi
        else:
            for i, xi in enumerate(x):
                yi = b[0] * xi + b[1] * x1 + b[2] * x2 - den[1] * y1 - den[2] * y2
                x2, x1, y2, y1 = x1, xi, y1, yi
                y[i] = yi
        x = y
    return x


LP = [biquad("lp", 20000, 1 / math.sqrt(2))]
HP = {
    1: [hp_first(20)],
    2: [biquad("hp", 20, 1 / math.sqrt(2))],
    4: [biquad("hp", 20, 0.5412), biquad("hp", 20, 1.3066)],
}
N = int(1.5 * FS)


def ramp(amp, dur):
    t0 = 0.1
    out = []
    for i in range(N):
        t = i / FS
        if dur == 0:
            out.append(amp if t >= t0 else 0.0)
        else:
            out.append(amp * min(max((t - t0) / dur, 0.0), 1.0))
    return out


def main():
    print("# 1. Stima SPL di picco a 1 m, formula di NC-028 (CALCOLATA, limite superiore)")
    for label, dv in [("soglia V2, 100 uV", 100e-6),
                      ("residuo in mute NC-028, 4 mV p-p = 2 mV di picco", 2e-3),
                      ("controllo NC-028: 1 mV (tabella: 53)", 1e-3),
                      ("controllo NC-028: 14 mV (tabella: 76)", 14e-3),
                      ("controllo NC-028: 45 mV (tabella: 86)", 45e-3),
                      ("controllo NC-028: 104 mV (tabella: 94)", 104e-3)]:
        print("%-52s %.2f dB SPL" % (label, spl(dv)))
    print()
    print("# 2. Picco filtrato 20 Hz-20 kHz (LP Butterworth 2 ord. a 20 kHz), per ordine del HP a 20 Hz")
    for label, x in [("gradino netto 104 mV", ramp(0.104, 0)),
                     ("rampa 104 mV in 100 ms", ramp(0.104, 0.1)),
                     ("rampa 104 mV in 500 ms", ramp(0.104, 0.5)),
                     ("rampa 14 mV in 100 ms", ramp(0.014, 0.1))]:
        cells = []
        for order in (1, 2, 4):
            peak = max(abs(v) for v in run(x, HP[order] + LP))
            cells.append("ord %d: %.4g V" % (order, peak))
        print("%-26s %s" % (label, " | ".join(cells)))


if __name__ == "__main__":
    main()
