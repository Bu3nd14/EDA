#!/usr/bin/env python3
"""L46b: il verbo di ADR-020 su uno spettro dei rail LIMITATO PER ECCESSO, per variante.

  sqrt( sum_rail sum_k [V_rail,k * 10^(-PSRR_rail(f_k)/20)]^2 ) <= 1 uV, 20 Hz-20 kHz

Il modello TI del TPS7A4701 (SBVM364) non modella il rumore d'uscita (lo dice la sua
intestazione) e in ngspice da' un punto di lavoro sbagliato (L41a); nel banco di psu.py i
regolatori sono comportamentali, senza PSRR ne' rumore. Quindi qui NON c'e' una
simulazione dei rail: c'e' un limite per eccesso, ogni ipotesi dichiarata e scelta dal
lato sfavorevole.

RUMORE DEI REGOLATORI (densita' letta a occhio dai grafici dei datasheet in vendor/):
  + TPS7A4701, SBVS204G fig. 5-1, curva VOUT = 15 V (C_NR 1 uF, COUT 50 uF, 500 mA).
    Il progetto ha C_NR 10 uF (psu.py, C507): in bassa frequenza la curva da 1 uF sta
    sopra. I punti letti sono RISCALATI IN SU, se serve, finche' l'integrale 10 Hz-100 kHz
    fa i 12,28 uVrms stampati sul grafico (mai in giu').
  - TPS7A3301, SBVS169D fig. 22, curva VOUT = -5 V (37 uVrms), la piu' alta disegnata;
    riscalata come sopra a 37 uVrms e poi MOLTIPLICATA PER 3 (15 V / 5 V: il guadagno di
    rumore del partitore, senza il credito del condensatore di feed-forward C513 che il
    progetto ha).
RIPPLE (dal serbatoio grezzo, attraverso il regolatore):
  dente di sega da Vpp = I * 10 ms / C, I = 0,30 A (265 mA del carico di L41a + 33 mA di
  ADR-054), C = 4700 uF - 20 % = 3760 uF: 0,80 Vpp, scarica sull'intero semiperiodo
  (sfavorevole: la vera e' piu' corta). Armoniche di 100 Hz: Vpp / (pi n sqrt 2) RMS.
  Piu' un tono a 50 Hz al 10 % della fondamentale (sbilanciamento del ponte, dichiarato).
  PSRR del regolatore +: 66 dB piatto fino a 10 kHz (il minimo della curva 15 V di fig.
  5-17 sotto 10 kHz, il buco a ~130 Hz; dropout 1 V, il progetto ne ha >= 3), 64 dB a
  20 kHz. Regolatore -: 50 dB piatto (fig. 18 di SBVS169D da' ~60 dB a -5 V in banda).
PSRR DEL BLOCCO: dai CSV della variante, minimo fra i tre modi, interpolato in log f.
Il rumore si integra (trapezi in f, griglia log fitta) su 20 Hz-20 kHz.

Uso: /usr/bin/python3 quota_adr020.py <variante>...   -> quota_adr020.csv
"""
import csv
import math
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
LOTTO = os.path.dirname(QUI)
MODI = ("0db", "3db", "10db")

# (f, uV/rtHz) letti dai grafici
N_POS = [(10, 2.4), (20, 2.0), (50, 1.27), (100, 0.67), (200, 0.40), (500, 0.17),
         (1e3, 0.091), (2e3, 0.055), (5e3, 0.034), (1e4, 0.025), (2e4, 0.019),
         (5e4, 0.014), (1e5, 0.012)]
N_POS_RMS = 12.28          # uVrms 10 Hz-100 kHz, stampato su fig. 5-1
N_NEG = [(10, 3.0), (20, 2.6), (50, 2.0), (100, 1.6), (200, 1.3), (500, 0.9),
         (1e3, 0.65), (2e3, 0.5), (5e3, 0.3), (1e4, 0.2), (2e4, 0.13), (5e4, 0.08),
         (1e5, 0.05)]
N_NEG_RMS = 37.0           # uVrms 10 Hz-100 kHz, fig. 22, -5 V
N_NEG_SCALA = 3.0          # 15 V / 5 V, senza credito del feed-forward

VPP = 0.30 * 10e-3 / (4700e-6 * 0.8)
PSRR_REG_POS = [(10, 66), (1e4, 66), (2e4, 64)]
PSRR_REG_NEG = [(10, 50), (2e4, 50)]


def interp_log(pts, x, logy=False):
    lx = math.log10(x)
    for (f0, y0), (f1, y1) in zip(pts, pts[1:]):
        a, b = math.log10(f0), math.log10(f1)
        if a <= lx <= b:
            t = (lx - a) / (b - a)
            if logy:
                return 10 ** (math.log10(y0) + t * (math.log10(y1) - math.log10(y0)))
            return y0 + t * (y1 - y0)
    raise ValueError(x)


def griglia(f0, f1, n=2000):
    return [f0 * (f1 / f0) ** (i / n) for i in range(n + 1)]


def integra(fun, f0, f1):
    g = griglia(f0, f1)
    return sum(0.5 * (fun(a) + fun(b)) * (b - a) for a, b in zip(g, g[1:]))


def scala(pts, rms):
    letto = math.sqrt(integra(lambda f: interp_log(pts, f, True) ** 2, 10, 1e5))
    return max(1.0, rms / letto), letto


K_POS, LETTO_POS = scala(N_POS, N_POS_RMS)
K_NEG, LETTO_NEG = scala(N_NEG, N_NEG_RMS)


def rumore(rail, f):
    if rail == "p":
        return K_POS * interp_log(N_POS, f, True) * 1e-6
    return N_NEG_SCALA * K_NEG * interp_log(N_NEG, f, True) * 1e-6


def ripple_rail(rail):
    """[(f, V RMS al nodo del blocco)] fra 50 Hz e 20 kHz."""
    reg = PSRR_REG_POS if rail == "p" else PSRR_REG_NEG
    v1 = VPP / (math.pi * math.sqrt(2))
    toni = [(50.0, 0.1 * v1)] + [(100.0 * n, v1 / n) for n in range(1, 201)]
    return [(f, v * 10 ** (-interp_log(reg, f) / 20)) for f, v in toni]


def curva(v, rail, modo):
    p = os.path.join(LOTTO, "run", v, "tb_zout_psrr_noise",
                     "tb_zout_psrr_noise_psrr%s_%s.csv" % (rail, modo))
    return [(float(a), float(b)) for a, b in list(csv.reader(open(p)))[1:]]


def psrr_blocco(v, rail):
    cc = [curva(v, rail, m) for m in MODI]
    return lambda f: min(interp_log(c, f) for c in cc)


def spl(u):
    """Nota su E5: 10 uV in uscita ~ +13 dB SPL a 1 m sulle Heresy."""
    return 13 + 20 * math.log10(u / 10e-6)


righe = []
for v in sys.argv[1:]:
    r = {"variante": v}
    tot2 = 0.0
    for rail in ("p", "m"):
        ps = psrr_blocco(v, rail)
        rip2 = sum((x * 10 ** (-ps(f) / 20)) ** 2 for f, x in ripple_rail(rail))
        nn2 = integra(lambda f: (rumore(rail, f) * 10 ** (-ps(f) / 20)) ** 2, 20, 2e4)
        r["ripple_%s_uV" % rail] = "%.4f" % (math.sqrt(rip2) * 1e6)
        r["rumore_%s_uV" % rail] = "%.4f" % (math.sqrt(nn2) * 1e6)
        tot2 += rip2 + nn2
    r["totale_uV"] = "%.4f" % (math.sqrt(tot2) * 1e6)
    r["dB_SPL_1m"] = "%.1f" % spl(math.sqrt(tot2))
    r["margine_dB"] = "%.1f" % (-20 * math.log10(math.sqrt(tot2) / 1e-6))
    righe.append(r)

print("ripple %.3f Vpp; rumore +: letto %.2f uVrms, scala %.2f; rumore -: letto %.2f uVrms,"
      " scala %.2f x %.0f" % (VPP, LETTO_POS, K_POS, LETTO_NEG, K_NEG, N_NEG_SCALA))
print("rail al nodo del blocco, 20 Hz-20 kHz: rumore + %.2f uVrms, rumore - %.2f uVrms" % (
    math.sqrt(integra(lambda f: rumore("p", f) ** 2, 20, 2e4)) * 1e6,
    math.sqrt(integra(lambda f: rumore("m", f) ** 2, 20, 2e4)) * 1e6))
campi = list(righe[0])
with open(os.path.join(LOTTO, "quota_adr020.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, campi)
    w.writeheader()
    w.writerows(righe)
print("  ".join("%14s" % c for c in campi))
for r in righe:
    print("  ".join("%14s" % r[c] for c in campi))
