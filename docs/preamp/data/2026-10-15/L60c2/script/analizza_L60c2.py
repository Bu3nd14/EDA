#!/usr/bin/env python3
"""L60c2: l'analisi delle corse di genera_L60c2.py (V2 A, il caldo, E9). Solo stdlib, /usr/bin/python3 -I.

Uso: analizza_L60c2.py        scrive v2.csv, caldo.csv, e9.csv (P10: analizza_p10.py di L45b, a parte)

Lo stesso metodo di analizza_L60c1.py, sulla sola G0 (il circuito di L60c2), con le corse nei gruppi
di genera_L60c2.py: g0 (V2, caldo, E9 nominale e -5 %) ed e9 (+5 %).
"""
import csv
import glob
import math
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L60C2 = os.path.dirname(QUI)
ROOT = os.path.abspath(os.path.join(L60C2, "..", "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import v2_metodo as vm  # noqa: E402

T_EV = 0.5
T_FINE = 3.0
DTMIN = 1e-9
RUN = os.path.join(L60C2, "run")


def leggi(nome):
    cols, _ = vm.leggi_wrdata(os.path.join(RUN, "g0", nome, nome + ".dat"), DTMIN, T_FINE)
    return cols


def spl(v):
    return 101 + 20 * math.log10(1000 * v / 100) if v > 0 else float("-inf")


def v2():
    righe = []
    for vos in ("+0", "+20", "-20"):
        for ev, rif in (("ins", "rif_mute"), ("rel", "rif_su")):
            e = leggi("G0_%s_vos%s" % (ev, vos))
            r = leggi("G0_%s_vos%s" % (rif, vos))
            a, i, durata = vm.a_picco(e[0], r[0], T_EV, T_FINE)
            n = min(len(e[0]), len(r[0]))
            i0 = int(round(T_EV * vm.FS))
            grezzo = max(abs(e[0][k] - r[0][k]) for k in range(i0, n))
            su = leggi("G0_rif_su_vos%s" % vos)
            dc_f2 = su[1][int(round(0.45 * vm.FS))]
            righe.append({"geometria": "G0", "vosf2_mV": vos, "evento": ev,
                          "A_uV": "%.4f" % (a * 1e6), "A_t_ms": "%.1f" % ((i / vm.FS - T_EV) * 1e3),
                          "grezzo_uV": "%.4f" % (grezzo * 1e6),
                          "stax_dB_SPL": "%.1f" % spl(a), "verdetto": "entro" if a <= 100e-6 else "FUORI",
                          "dc_outf2_mV": "%.3f" % (dc_f2 * 1e3), "finestra_s": "%.2f" % durata})
    scrivi("v2.csv", righe)


def caldo():
    x = leggi("G0_caldo")[0]
    i0 = int(round(T_EV * vm.FS))
    prima = x[i0 - 1]
    d = [v - prima for v in x]
    a, i = vm.picco(vm.filtra(d, i0), i0, len(d))
    scrivi("caldo.csv", [{"geometria": "G0", "jack_prima_uV": "%.3f" % (prima * 1e6),
                          "A_uV": "%.3f" % (a * 1e6),
                          "grezzo_uV": "%.3f" % (max(abs(v) for v in d[i0:]) * 1e6),
                          "verdetto": "entro" if a <= 100e-6 else "FUORI"}])


def e9():
    righe = []
    for p in sorted(glob.glob(os.path.join(RUN, "*", "*", "*_e9.csv"))):
        _, g, k, d = open(p).read().strip().split(",")
        righe.append({"geometria": g, "k_C": k, "dB_20Hz_su_1kHz": "%.3f" % float(d),
                      "verdetto": "entro" if abs(float(d)) <= 0.2 else "FUORI"})
    scrivi("e9.csv", sorted(righe, key=lambda r: float(r["k_C"])))


def scrivi(nome, righe):
    with open(os.path.join(L60C2, nome), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(righe[0].keys()))
        w.writeheader()
        w.writerows(righe)
    print("%s: %d righe" % (nome, len(righe)))


if __name__ == "__main__":
    v2()
    caldo()
    e9()
