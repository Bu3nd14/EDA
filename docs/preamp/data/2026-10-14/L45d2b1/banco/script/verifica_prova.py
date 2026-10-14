#!/usr/bin/env python3
"""L45d2b1: la prova dello strumento - il rivelatore da solo contro il calcolo a mano. /usr/bin/python3.

Uso: verifica_prova.py RUNDIR OUT.csv

Per ogni caso di genera_rivelatore.py prova: se doveva scattare, il tempo dal gradino (0,1 s) a
DC_FLT sotto 2,5 V contro il ritardo del filtro piu' T_HOLD di ../../scelte/dimensiona.py, alla VDP
misurata nel deck, con V_SAT 0,3 V (il modello CMPOC) e VF 0,45 V; tolleranza 3 ms (la corrente
che TMAX toglie al temporizzatore e il VF vero non sono nella formula). Se non doveva, DC_FLT non
deve mai scendere. Esce con il numero di casi sbagliati.
"""
import csv
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, "..", "..", "scelte"))
sys.path.insert(0, QUI)
import dimensiona as dm            # noqa: E402
import genera_rivelatore as gr     # noqa: E402

T0 = 0.1
TOL = 3e-3


def leggi(path):
    d = {}
    for r in csv.DictReader(open(path)):
        try:
            d[r["grandezza"]] = float(r["valore"])
        except ValueError:
            d[r["grandezza"]] = None
    return d


def ampiezza(sorg):
    # PWL(0 0 0.1 0 0.10001 V): l'ultimo numero; PULSE(V1 V2 ...): V2, il livello dal ritardo in poi
    p = sorg.rstrip(")").split("(")[1].split()
    return float(p[1]) if sorg.startswith("PULSE") else float(p[-1])


def main(rundir, out):
    righe, male = [], 0
    for nome, (presa, sorg, vp, atteso) in gr.PROVA_CASI.items():
        f = os.path.join(rundir, nome, nome + "_riv.csv")
        if not os.path.exists(f):
            righe.append((nome, atteso, "", "", "MANCA"))
            male += 1
            continue
        d = leggi(f)
        t = d.get("t_flt")
        if atteso == "no":
            esito = "OK" if t is None else "SBAGLIATO"
            righe.append((nome, atteso, "" if t is None else "%.2f" % ((t - T0) * 1e3), "", esito))
        elif atteso == "dopo_por":
            # l'inibizione (99 ms +- 6 % da quando VDP c'e', piu' la rampa di 20 ms) e poi il
            # temporizzatore da ~0,9 V (tenuto basso dai diodi su TMAX): ~68 ms. Finestra larga:
            # deve scattare, e non prima che l'inibizione finisca.
            mis = None if t is None else t - T0
            esito = "OK" if mis is not None and 0.150 <= mis <= 0.210 else "SBAGLIATO"
            righe.append((nome, atteso, "" if mis is None else "%.2f" % (mis * 1e3), "150-210", esito))
        else:
            vdp = d["vdp"]
            vx = abs(ampiezza(sorg))
            vt, _ = dm.vt(vdp)
            att = dm.t_filtro(vx, vt, vdp) + dm.t_hold(dm.R_T, dm.C_T, 0.3, 0.45, vdp)
            mis = None if t is None else t - T0
            esito = "OK" if mis is not None and abs(mis - att) <= TOL else "SBAGLIATO"
            righe.append((nome, atteso, "" if mis is None else "%.2f" % (mis * 1e3), "%.2f" % (att * 1e3), esito))
        if righe[-1][-1] != "OK":
            male += 1
    with open(out, "w", newline="") as fo:
        w = csv.writer(fo)
        w.writerow(["caso", "atteso", "misurato_ms", "calcolato_ms", "esito"])
        w.writerows(righe)
    for r in righe:
        print("%-20s %-7s misurato %8s ms  calcolato %8s ms  %s" % r)
    print("sbagliati: %d" % male)
    return male


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
