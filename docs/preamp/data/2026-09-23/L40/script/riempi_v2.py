#!/usr/bin/env python3
"""L40: scrive le cifre della cella V2 (v2_riassunto.py) nei documenti che le
aspettavano, al posto dei segnaposto @...@ lasciati durante la corsa.
Uso: /usr/bin/python3 riempi_v2.py
"""
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 6))
R = {
    "docs/preamp/reports/2026-09-23-L40-v1-costruttore.md": [
        ("@V2PRIMA@", "7,163 / 5,32 dB; A ≤ 3,75 µV, B2 0,327 µV, C_pav 0,267 mV"),
        ("@V2DOPO@", "7,163 / 5,32 dB; A ≤ 3,75 µV, B2 0,330 µV, C_pav 0,341 mV"),
        ("@V2ESITO@", "regge (C_pav è diagnostica)")],
    "circuits/preamp/gain_block.py": [
        ("@V2MUTE@", "Mute (tb_v2_mute_ldr.cir, 1 kHz, 100 k, main): S 7.16 / 5.32 dB, A <=\n"
                     "#     3.75 uV, B2 0.33 uV; chain distortion floor of C (C_pav) 0.27 -> 0.34 mV.")],
    "docs/preamp/NEXT-SESSION.md": [
        ("@V2CELLA@", "S 7,163 / 5,32 dB (invariato), A senza segnale ≤ 3,75 µV, B2 0,33 µV; "
                      "il fondo di distorsione della catena C_pav sale da 0,27 a **0,34 mV** "
                      "(diagnostica). Rimisurare questa cella prima della matrice resta il "
                      "primo controllo.")],
    "docs/preamp/STATE.md": [
        ("@V2STATE@", "S 7,163 / 5,32 dB, A ≤ 3,75 µV, come prima; C_pav 0,27 → 0,34 mV."),
        ("@SUITE@", "**10 passed / 0 failed**")],
}
for p, lista in R.items():
    f = os.path.join(ROOT, p)
    s = open(f).read()
    for a, b in lista:
        assert s.count(a) == 1, (p, a)
        s = s.replace(a, b)
    open(f, "w").write(s)
    print("ok", p)
