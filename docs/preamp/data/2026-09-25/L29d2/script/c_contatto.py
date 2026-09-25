#!/usr/bin/env python3
"""L29d2: la capacita' del contatto aperto del G6K dal datasheet (decisione dell'utente del
2026-09-25: «C dal datasheet + cavo realistico»).

Fonte: vendor/relays/omron/G6K/en-g6k.pdf, pagina 5, «High-frequency Characteristics
(Isolation)», G6K-2G(F/P)(-Y), media di 10 pezzi, iniziale, sul PCB di prova Omron (nota *2:
dipende dal PCB). Letti a occhio dal grafico (render a 200 dpi con pdftoppm): la curva e' una
retta da ~86,5 dB a 1 MHz a ~46 dB a 100 MHz.

Modello: contatto aperto = una C in serie fra due porte da Z0 = 50 ohm. Per w C 2 Z0 << 1
  |S21| = 2 Z0 / |2 Z0 + 1/(j w C)| ~ w C 2 Z0     ->  C = |S21| / (2 pi f 2 Z0)
La pendenza letta (20 dB/decade) dice che la curva e' capacitiva pura.

Uso: /usr/bin/python3 c_contatto.py
"""
import math

Z0 = 50.0
LETTI = [(1e6, 86.5), (10e6, 66.5), (100e6, 46.0)]   # (Hz, isolamento in dB), letti dal grafico

cc = []
for f, iso in LETTI:
    s21 = 10 ** (-iso / 20)
    c = s21 / (2 * math.pi * f * 2 * Z0)
    cc.append(c)
    print("f = %6.0f MHz  isolamento %5.1f dB  |S21| = %.3e  C = %.3f pF" % (f / 1e6, iso, s21, c * 1e12))
print("pendenza 1-100 MHz: %.1f dB/decade" % ((LETTI[0][1] - LETTI[2][1]) / 2))
print("C massima letta: %.3f pF; valore del banco, per eccesso: 0.1 pF" % (max(cc) * 1e12))
print("lettura +-2 dB -> C x %.2f / x %.2f" % (10 ** (2 / 20), 10 ** (-2 / 20)))
