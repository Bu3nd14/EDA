#!/usr/bin/env python3
"""L30: la soglia a cui il blocco perde la regolazione allo spegnimento (ADR-043 §1: «~10 V
misurati, da rimisurare sul circuito di L30»). Solo stdlib, /usr/bin/python3.

Legge i file *_stati.dat delle corse di guasto (un rail o entrambi, discesa lineare lenta, il
guadagno fermo a +10 dB) e riporta il rail nell'istante in cui l'uscita del blocco (MAIN_A,
prima dei 47 ohm) si scosta di piu' di SCOSTA dal suo valore a regime. SIMULATA.

Uso: soglia_regolazione.py DIR CORSA...
"""
import sys

SCOSTA = (0.001, 0.01, 0.1)    # V
# wrdata: coppie (tempo, valore) per ogni vettore, nell'ordine del deck
ORDINE = ("xls.xs", "xlp.xs", "dep", "ina", "vplus", "vminus", "main_a", "mainc", "fixc1", "fixc2")


def leggi(path):
    righe = []
    for r in open(path):
        c = r.split()
        if len(c) < 2 * len(ORDINE):
            continue
        try:
            v = [float(x) for x in c]
        except ValueError:
            continue
        righe.append({"t": v[0], **{n: v[2 * i + 1] for i, n in enumerate(ORDINE)}})
    return righe


def main(argv):
    d = argv[1]
    print("corsa,scostamento_V,t_s,vplus_V,vminus_V,main_a_V")
    for corsa in argv[2:]:
        r = leggi("%s/%s_stati.dat" % (d, corsa))
        base = [x for x in r if 0.9 < x["t"] < 0.95]
        v0 = sum(x["main_a"] for x in base) / len(base)
        for s in SCOSTA:
            for x in r:
                if x["t"] > 0.95 and abs(x["main_a"] - v0) > s:
                    print("%s,%g,%.6f,%.3f,%.3f,%.5f" % (corsa, s, x["t"], x["vplus"], x["vminus"],
                                                         x["main_a"]))
                    break
            else:
                print("%s,%g,mai,,," % (corsa, s))


if __name__ == "__main__":
    main(sys.argv)
