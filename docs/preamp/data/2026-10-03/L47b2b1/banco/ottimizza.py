"""ottimizza.py - L47b2b1: il profilo a 3 s ricalibrato sull'inviluppo A-E della NSL-32SR3.

Due tabelle (d, log10 I) a nodi fissi di d, una per stringa, interpolate in log come il profilo
v4 (genera_tb_v2_casopeggiore.py, BILS) e come la tabella del firmware. Discesa per coordinate
sul costo
    max su curve A-E e sui due versi di S (dB)  +  penalita' se il mute a fine sfumatura e'
    meno profondo di PROF dB su una curva
con i vincoli: serie non crescente in d, derivazione non decrescente; serie a d = 0 e
derivazione a d = 1 alla cima; serie a d = 1 e derivazione a d = 0 al riposo (10 nA).

Il banco e' rapido.py (verificato contro ngspice su L47b1: entro 0,2 dB). Il profilo trovato
si riverifica con la `tran` vera (sfumatura.py) prima di ogni altra cosa.

    /usr/bin/python3 ottimizza.py <cima_A> <prof_dB> <uscita.json>
"""
import json
import math
import sys
import time

import rapido as R

ION = float(sys.argv[1])
PROF = float(sys.argv[2])
USCITA = sys.argv[3]
IRIP = 10e-9
E3_MIN = 102e3    # E3 >= 100 kohm col 2 % di margine sul modello rapido (rapido.zin_e3)
TD = 3.0
CURVE = "ABCDE"
NODI = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
LMIN, LMAX = math.log10(IRIP), math.log10(ION)


def tabelle(xs, xp):
    return ([(d, 10 ** v) for d, v in zip(NODI, xs)], [(d, 10 ** v) for d, v in zip(NODI, xp)])


def valuta(xs, xp, curve=CURVE):
    ts, tp = tabelle(xs, xp)
    fs, fp = R.tabella_log(ts), R.tabella_log(tp)
    peggiore, prof, e3, det = 0.0, -999.0, 1e12, {}
    for c in curve:
        r = R.sfumatura(fs, fp, TD, (c, c))
        peggiore = max(peggiore, r["S_ins_dB"], r["S_rel_dB"])
        prof = max(prof, r["liv_mute_dB"])
        e3 = min(e3, r["e3_min"])
        det[c] = (round(r["S_ins_dB"], 2), round(r["S_rel_dB"], 2), round(r["liv_mute_dB"], 1),
                  round(r["e3_min"] / 1e3, 1))
    costo = peggiore + 2.0 * max(0.0, prof - PROF) + 1.0 * max(0.0, E3_MIN - e3) / 1e3
    return costo, peggiore, prof, det, e3


def vincola(xs, xp):
    xs = [min(max(v, LMIN), LMAX) for v in xs]
    xp = [min(max(v, LMIN), LMAX) for v in xp]
    xs[0], xs[-1], xp[0], xp[-1] = LMAX, LMIN, LMIN, LMAX
    for k in range(1, len(xs)):
        xs[k] = min(xs[k], xs[k - 1])
        xp[k] = max(xp[k], xp[k - 1])
    return xs, xp


def main():
    # partenza: serie giu' al riposo entro d = 0,2, derivazione log-lineare su tutta la corsa
    xs = [LMAX, math.log10(0.2e-3), LMIN] + [LMIN] * 8
    xp = [LMIN + (LMAX - LMIN) * d for d in NODI]
    if "--da-v4" in sys.argv:      # oppure dal profilo v4 campionato sui nodi
        fs4, fp4 = R.profilo_v4(ION, IRIP)
        xs = [math.log10(fs4(d)) for d in NODI]
        xp = [math.log10(fp4(d)) for d in NODI]
    xs, xp = vincola(xs, xp)
    t0 = time.time()
    best = valuta(xs, xp)
    print("partenza: costo %.2f  S %.2f  prof %.1f  E3 %.1f k  (%.1f s)" % (best[0], best[1], best[2], best[4] / 1e3, time.time() - t0))
    for passo in (0.8, 0.4, 0.2, 0.1, 0.05):
        migliorato = True
        while migliorato:
            migliorato = False
            for quale in ("s", "p"):
                for k in range(1, len(NODI) - 1):
                    for seg in (+1, -1):
                        ns, npp = list(xs), list(xp)
                        (ns if quale == "s" else npp)[k] += seg * passo
                        ns, npp = vincola(ns, npp)
                        if (ns, npp) == (xs, xp):
                            continue
                        v = valuta(ns, npp)
                        if v[0] < best[0] - 1e-3:
                            xs, xp, best = ns, npp, v
                            migliorato = True
            print("passo %.2f: costo %.2f  S %.2f  prof %.1f  E3 %.1f k  (%.0f s)" % (
                passo, best[0], best[1], best[2], best[4] / 1e3, time.time() - t0), flush=True)
    ts, tp = tabelle(xs, xp)
    out = {"cima_A": ION, "riposo_A": IRIP, "td_s": TD, "prof_dB": PROF, "nodi_d": NODI,
           "serie_log10A": [round(v, 4) for v in xs], "deriv_log10A": [round(v, 4) for v in xp],
           "S_peggiore_dB": round(best[1], 3), "mute_meno_profondo_dB": round(best[2], 2),
           "E3_min_kohm": round(best[4] / 1e3, 2),
           "per_curva_Sins_Srel_mute_E3k": best[3]}
    json.dump(out, open(USCITA, "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
