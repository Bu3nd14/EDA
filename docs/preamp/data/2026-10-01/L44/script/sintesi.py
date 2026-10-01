#!/usr/bin/env python3
"""L44 - sintesi delle corse: E5 per variante e rumore per dispositivo.

Per ogni variante in ../run/:
  e5_max_uv     il massimo di tb_e3_e5_ldr_e5.csv (la catena con le LDR, il caso
                peggiore di E5; L39-L46b: curva D, +10 dB, 430 ohm) e la sua riga
  d_uv, b_uv    tb_noise_breakdown, caso D (+10 dB, 2,5 kohm) e B (0 dB, 430 ohm)
  dB_SPL        e5_max in dB SPL a 1 m: 96 + 20 log10(21,1 V / 2,83) (NC-028,
                finale x21,1, Heresy 96 dB/1 W/1 m). E' un livello RMS non pesato
                20 Hz - 20 kHz, da confrontare con una stanza silenziosa (25-35
                dB(A)) con la riserva che A pesa via proprio le basse frequenze
  margine_dB    20 log10(9,95 / e5_max): la distanza dal tetto di E5 (ADR-020)
Scrive ../sintesi.csv e ../dispositivi.csv (densita' per dispositivo, nV/rtHz al
jack, a 20 / 100 / 1000 Hz, blocco B +10 dB, sorgente 430 ohm, da
rumore_dispositivi_r430.txt), e stampa la prima.

Uso: /usr/bin/python3 sintesi.py
"""
import csv
import math
import os
import re

QUI = os.path.dirname(os.path.abspath(__file__))
L44 = os.path.dirname(QUI)
RUN = os.path.join(L44, "run")
TETTO = 9.95
VETT = ["onoise_spectrum", "onoise_q106", "onoise_q117", "onoise_q118", "onoise_q121a",
        "onoise_q121b", "onoise_q122", "onoise_q125", "onoise_q127", "onoise_q132",
        "onoise_q133", "onoise_jq110a", "onoise_jq110b", "onoise_r119", "onoise_r120",
        "onoise_r136", "onoise_rsrc"]


def spl(v):
    return 96 + 20 * math.log10(21.1 * v / 2.83)


def totali(log):
    return [float(x) for x in re.findall(r"^onoise_total = (\S+)", open(log).read(), re.M)]


def e5(path):
    righe = list(csv.DictReader(open(path)))
    r = max(righe, key=lambda x: float(x["onoise_uv"]))
    return float(r["onoise_uv"]), "%s %s %s %s" % (r["ldr"], r["mode"], r["att"], r["rsrc"])


def spettro(path, freqs):
    """{f: {vettore: V/rtHz}} interpolando in log fra i punti di wrdata."""
    righe = [[float(x) for x in l.split()] for l in open(path) if l.strip()]
    out = {}
    for f in freqs:
        k = min(range(len(righe) - 1), key=lambda i: abs(math.log(righe[i][0] / f)))
        if righe[k][0] > f and k > 0:
            k -= 1
        a, b = righe[k], righe[k + 1]
        t = math.log(f / a[0]) / math.log(b[0] / a[0])
        out[f] = {n: math.exp((1 - t) * math.log(a[2 * i + 1]) + t * math.log(b[2 * i + 1]))
                  for i, n in enumerate(VETT)}
    return out


def main():
    sint, disp = [], []
    for v in sorted(os.listdir(RUN)):
        d = os.path.join(RUN, v)
        if not os.path.isdir(d):
            continue
        r = {"variante": v}
        try:
            t = totali(os.path.join(d, "tb_noise_breakdown", "tb_noise_breakdown.log"))
            r["b_uv"], r["d_uv"] = "%.4f" % (t[1] * 1e6), "%.4f" % (t[3] * 1e6)
            m, caso = e5(os.path.join(d, "tb_e3_e5_ldr", "tb_e3_e5_ldr_e5.csv"))
            r["e5_max_uv"], r["caso"] = "%.4f" % m, caso
            r["dB_SPL"], r["margine_dB"] = "%.1f" % spl(m * 1e-6), "%.2f" % (20 * math.log10(TETTO / m))
            sp = spettro(os.path.join(d, "rumore_dispositivi", "rumore_dispositivi_r430.txt"),
                         (20, 100, 1000))
            for f, valori in sp.items():
                riga = {"variante": v, "f_hz": f}
                riga.update({n.replace("onoise_", ""): "%.3f" % (x * 1e9) for n, x in valori.items()})
                disp.append(riga)
        except (OSError, IndexError, ValueError) as e:
            r["caso"] = "ERRORE %s" % e
        sint.append(r)
    campi = ["variante", "e5_max_uv", "dB_SPL", "margine_dB", "caso", "d_uv", "b_uv"]
    with open(os.path.join(L44, "sintesi.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, campi)
        w.writeheader()
        w.writerows(sint)
    with open(os.path.join(L44, "dispositivi.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, ["variante", "f_hz"] + [n.replace("onoise_", "") for n in VETT])
        w.writeheader()
        w.writerows(disp)
    for r in sint:
        print(",".join(str(r.get(c, "")) for c in campi))


if __name__ == "__main__":
    main()
