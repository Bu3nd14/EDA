#!/usr/bin/env python3
"""L29b2: C2 in numpy, per la ricerca del profilo. Deve ridare scripts/v2_metodo.py
(verifica: /Users/roberto/EDA/env/venv/bin/python3 c2np.py). Scratch, non il verdetto.

- residuo: lo stesso fit a + b su finestra centrata di CAMPIONI_C, con somme cumulative;
- filtro: gli stessi due biquad di v2_metodo (HP 20 Hz e LP 20 kHz, 2o ordine, Q = 0,707),
  applicati come convoluzione con la loro risposta all'impulso (1,5 s: la coda oltre e'
  sotto 1e-9 della risposta), stato nullo da i0 come filtra().
"""
import math
import os
import sys

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, *[".."] * 6, "scripts"))
import v2_metodo as vm  # noqa: E402

FS = vm.FS
NW = vm.CAMPIONI_C


def _impulso(n):
    x = [0.0] * n
    x[0] = 1.0
    return np.array(vm.filtra(x, 0))


H = _impulso(int(1.5 * FS))


def residuo(x, f):
    x = np.asarray(x, dtype=float)
    n = len(x)
    h = NW // 2
    k = np.arange(n)
    w = 2 * math.pi * f / FS
    s, c = np.sin(w * k), np.cos(w * k)

    def cs(v):
        return np.concatenate(([0.0], np.cumsum(v)))
    pss, psc, pcc, pxs, pxc = cs(s * s), cs(s * c), cs(c * c), cs(x * s), cs(x * c)
    i = np.arange(h, n - (NW - h))
    lo, hi = i - h, i - h + NW
    Sss, Ssc, Scc = pss[hi] - pss[lo], psc[hi] - psc[lo], pcc[hi] - pcc[lo]
    Sxs, Sxc = pxs[hi] - pxs[lo], pxc[hi] - pxc[lo]
    det = Sss * Scc - Ssc * Ssc
    a = (Sxs * Scc - Sxc * Ssc) / det
    b = (Sxc * Sss - Sxs * Ssc) / det
    r = np.zeros(n)
    r[i] = x[i] - (a * s[i] + b * c[i])
    return r, h, n - (NW - h)


def filtra(r, i0):
    seg = r[i0:]
    m = len(seg) + len(H) - 1
    nfft = 1 << (m - 1).bit_length()
    y = np.fft.irfft(np.fft.rfft(seg, nfft) * np.fft.rfft(H, nfft), nfft)[:len(seg)]
    out = np.zeros(len(r))
    out[i0:] = y
    return out


def c2(g, t_ev, finestra, f, amp, rif=0.0, t0=0.0):
    """C2 picco (V) di amp*g*sin contro amp*rif*sin; g campionato a FS da t0."""
    g = np.asarray(g, dtype=float)
    k = np.arange(len(g)) + int(round(t0 * FS))
    w = 2 * math.pi * f / FS
    s = np.sin(w * k + math.pi / 2)
    re_, i0, i1 = residuo(amp * g * s, f)
    if rif:
        rr, _, _ = residuo(amp * rif * s, f)
        re_ = re_ - rr
    y = filtra(re_, i0)
    a = max(int(round((t_ev - t0 - 0.020) * FS)), i0)
    b = min(int(round((t_ev - t0 + finestra + 0.200) * FS)), i1)
    j = a + int(np.argmax(np.abs(y[a:b])))
    return abs(y[j]), (j / FS) + t0


if __name__ == "__main__":
    # verifica contro v2_metodo (via sur.c2, pura stdlib) sugli stessi inviluppi
    sys.path.insert(0, QUI)
    import sur
    for f, T in ((1000.0, 2.0), (20.0, 2.0)):
        n = int((0.5 + T + 0.5) * FS)
        u = np.clip((np.arange(n) / FS - 0.5) / T, 0, 1)
        for nome, g in (("coseno", 0.5 + 0.5 * np.cos(np.pi * u)), ("lineare", 1 - u)):
            a = c2(g, 0.5, T, f, sur.A_MAIN)[0]
            b = sur.c2(list(g), 0.5, T, f=f, rif=0.0)[0]
            print("f %5g %-8s numpy %.6f mV   v2_metodo %.6f mV   scarto %.2e" % (
                f, nome, a * 1e3, b * 1e3, abs(a - b) / b))
