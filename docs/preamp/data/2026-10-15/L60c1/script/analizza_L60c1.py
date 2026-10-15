#!/usr/bin/env python3
"""L60c1: l'analisi delle corse di genera_L60c1.py. Solo stdlib, /usr/bin/python3 -I.

Uso: analizza_L60c1.py        scrive v2.csv, caldo.csv, e9.csv (P10: analizza_p10.py di L45b, a parte)

V2 A (ADR-032) con le funzioni di scripts/v2_metodo.py, importate: ricampionamento cubico a 96 kHz,
filtro Butterworth 2 ordine 20 Hz - 20 kHz da t_evento con stato nullo, picco di
d = evento - riferimento fino alla fine (2,5 s dopo l'evento). Il riferimento tiene lo stato finale:
l'inserimento contro «sempre in mute», il rilascio contro «sempre rilasciato».
dB SPL all'orecchio sulla Stax con la catena di NC-046 (come analizza_p10.py): 101 + 20 log10(1000 V / 100).
"""
import csv
import glob
import math
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L60C1 = os.path.dirname(QUI)
ROOT = os.path.abspath(os.path.join(L60C1, "..", "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import v2_metodo as vm  # noqa: E402

T_EV = 0.5
T_FINE = 3.0
DTMIN = 1e-9
RUN = os.path.join(L60C1, "run")


def leggi(gruppo, nome):
    cols, _ = vm.leggi_wrdata(os.path.join(RUN, gruppo, nome, nome + ".dat"), DTMIN, T_FINE)
    return cols


def spl(v):
    return 101 + 20 * math.log10(1000 * v / 100) if v > 0 else float("-inf")


def v2():
    righe = []
    for g in ("G0", "G1", "G1b", "G2", "G2b"):
        for vos in ("+0", "+20", "-20"):
            for ev, rif in (("ins", "rif_mute"), ("rel", "rif_su")):
                e = leggi("v2", "%s_%s_vos%s" % (g, ev, vos))
                r = leggi("v2", "%s_%s_vos%s" % (g, rif, vos))
                a, i, durata = vm.a_picco(e[0], r[0], T_EV, T_FINE)
                n = min(len(e[0]), len(r[0]))
                i0 = int(round(T_EV * vm.FS))
                grezzo = max(abs(e[0][k] - r[0][k]) for k in range(i0, n))
                su = leggi("v2", "%s_rif_su_vos%s" % (g, vos))
                dc_f2 = su[1][int(round(0.45 * vm.FS))]
                righe.append({"geometria": g, "vosf2_mV": vos, "evento": ev,
                              "A_uV": "%.2f" % (a * 1e6), "A_t_ms": "%.1f" % ((i / vm.FS - T_EV) * 1e3),
                              "grezzo_uV": "%.2f" % (grezzo * 1e6),
                              "stax_dB_SPL": "%.1f" % spl(a), "verdetto": "entro" if a <= 100e-6 else "FUORI",
                              "dc_outf2_mV": "%.3f" % (dc_f2 * 1e3), "finestra_s": "%.2f" % durata})
    scrivi("v2.csv", righe)


def caldo():
    righe = []
    for g in ("G0", "G1", "G1b", "G2", "G2b"):
        x = leggi("caldo", "%s_caldo" % g)[0]
        i0 = int(round(T_EV * vm.FS))
        prima = x[i0 - 1]
        d = [v - prima for v in x]
        a, i = vm.picco(vm.filtra(d, i0), i0, len(d))
        righe.append({"geometria": g, "jack_prima_uV": "%.3f" % (prima * 1e6), "A_uV": "%.3f" % (a * 1e6),
                      "grezzo_uV": "%.3f" % (max(abs(v) for v in d[i0:]) * 1e6),
                      "verdetto": "entro" if a <= 100e-6 else "FUORI"})
    scrivi("caldo.csv", righe)


def e9():
    righe = []
    for p in sorted(glob.glob(os.path.join(RUN, "e9", "*", "*_e9.csv"))):
        _, g, k, d = open(p).read().strip().split(",")
        righe.append({"geometria": g, "k_C": k, "dB_20Hz_su_1kHz": "%.3f" % float(d),
                      "verdetto": "entro" if abs(float(d)) <= 0.2 else "FUORI"})
    scrivi("e9.csv", righe)


def scrivi(nome, righe):
    with open(os.path.join(L60C1, nome), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(righe[0].keys()))
        w.writeheader()
        w.writerows(righe)
    print("%s: %d righe" % (nome, len(righe)))


if __name__ == "__main__":
    v2()
    caldo()
    e9()
