#!/usr/bin/env python3
"""L48b: la sintesi del banco degli scatti (deck/scatti_v*.csv) in uV e in dB SPL.

dB SPL di picco a 1 m con la catena di NC-028 (finale x21,1, Heresy 96 dB/2,83 V): 100 uV ~ 33,5
dB SPL, la soglia di V2 (PR-20). Per ogni variante, evento e guadagno: la continua nominale e il
peggiore delle tre (-6,6 / -30 / +30 mV), col cursore cortocircuitante (m1) e non (m0).

LA CORRENTE DI GATE COL CURSORE APERTO (m0). Il modello dell'LSK489 non ne ha (Isr ignorato,
Is 3 fA); il banco corre con gmin 1e-15 per non inventarla. Il limite si aggiunge qui dal
datasheet (vendor/jfet/linear_systems/LSK489/LSK489DSRevA38.pdf, IG a VDG 15 V, ID 200 uA):
-2 pA tipica, -25 pA massima a 25 C; 10 nA massima a 125 C. A 55 C (il telaio di P5) si legge
per raddoppio ogni 10 C dalla massima a 25 C: 25 * 2^3 = 200 pA. Il gate deriva di
IG * t_aperto / C_cursore, e al jack per il guadagno del blocco B. C_cursore = 100 pF del cavo
(ipotesi del banco) + ~4 pF del gate.
"""
import csv
import glob
import math
import os

QUI = os.path.dirname(os.path.abspath(__file__))
DECK = os.path.join(QUI, "deck")

EVENTI = {1: "volume 0 -> -2 dB", 2: "volume -29 -> -27 dB", 3: "trim 0 -> -6 dB",
          4: "trim -6 -> -12 dB"}
GB = {0: 1.0, 3: 10 ** (3 / 20), 10: 10 ** (10 / 20)}


def spl(uv):
    if uv <= 0:
        return float("-inf")
    return 96 + 20 * math.log10(uv * 1e-6 * 21.1 / 2.83)


def main():
    righe = []
    for f in sorted(glob.glob(os.path.join(DECK, "scatti_v*.csv"))):
        righe += list(csv.DictReader(open(f)))
    # controllo: la continua misurata dev'essere quella imposta
    for r in righe:
        assert abs(float(r["va_misurata_mv"]) - float(r["va_mv"])) < 0.05, r
    out = []
    caps = []
    for r in righe:
        k = (r["var"], r["cap"])
        if k not in caps:
            caps.append(k)
    sint = os.path.join(QUI, "sintesi.csv")
    with open(sint, "w", newline="") as fo:
        w = csv.writer(fo)
        w.writerow(["var", "cap", "evento", "guad_db", "modo", "nominale_uv", "peggiore_uv",
                    "peggiore_va_mv", "nominale_dbspl", "peggiore_dbspl"])
        for var, cap in caps:
            out.append("\n== v%s %s ==" % (var, cap))
            out.append("%-22s %4s %3s %12s %8s %12s %8s" % ("evento", "G", "m", "nom_uV", "dBSPL",
                                                           "pegg_uV", "dBSPL"))
            for ev in (1, 2, 3, 4):
                for g in ("0", "3", "10"):
                    for m in ("1", "0"):
                        sel = [r for r in righe if r["var"] == var and r["cap"] == cap and
                               r["evento"] == str(ev) and r["guad_db"] == g and r["modo"] == m]
                        if not sel:
                            continue
                        nom = [float(r["pk_uv"]) for r in sel if r["va_mv"] == "-6.6"][0]
                        pg = max(sel, key=lambda r: float(r["pk_uv"]))
                        pv = float(pg["pk_uv"])
                        out.append("%-22s %4s %3s %12.3f %8.1f %12.3f %8.1f" % (
                            EVENTI[ev], g, m, nom, spl(nom), pv, spl(pv)))
                        w.writerow([var, cap, ev, g, m, "%.4g" % nom, "%.4g" % pv, pg["va_mv"],
                                    "%.1f" % spl(nom), "%.1f" % spl(pv)])
    out.append("\n== il limite della corrente di gate col cursore aperto (m0), al jack ==")
    out.append("%-28s %8s %8s %12s %8s" % ("caso", "t_ms", "G_dB", "uV", "dBSPL"))
    c = 104e-12
    for nome, ig in (("tipica 25 C, 2 pA", 2e-12), ("massima 25 C, 25 pA", 25e-12),
                     ("massima 55 C (stima), 200 pA", 200e-12)):
        for t in (1e-3, 5e-3):
            for g in (0, 10):
                uv = ig * t / c * GB[g] * 1e6
                out.append("%-28s %8.0f %8d %12.2f %8.1f" % (nome, t * 1e3, g, uv, spl(uv)))
    # Con R_G 1M (ADR-065) il gate non deriva senza limite: si ferma a IG * R_G con
    # tau = R_G * C_cursore ~ 104 us, gia' raggiunto in 1 ms. Il limite non dipende dal tempo.
    out.append("\n== lo stesso, con R_G 1M sul gate (ADR-065): IG * R_G, raggiunto in ~5 tau = 0,5 ms ==")
    out.append("%-28s %8s %12s %8s" % ("caso", "G_dB", "uV", "dBSPL"))
    for nome, ig in (("tipica 25 C, 2 pA", 2e-12), ("massima 25 C, 25 pA", 25e-12),
                     ("massima 55 C (stima), 200 pA", 200e-12)):
        for g in (0, 10):
            uv = ig * 1e6 * GB[g] * 1e6
            out.append("%-28s %8d %12.2f %8.1f" % (nome, g, uv, spl(uv)))
    testo = "\n".join(out)
    print(testo)
    with open(os.path.join(QUI, "sintesi.txt"), "w") as f:
        f.write(testo + "\n")


if __name__ == "__main__":
    main()
