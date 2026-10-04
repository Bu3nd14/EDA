"""sfumatura.py - L47b2b1: la `tran` vera di ngspice sul banco ridotto di L47b1, cima 7 mA.

Riverifica i profili trovati con rapido.py. Il banco e' quello di L47b1 (importato, non
riscritto: ../../../2026-10-02/L47b1/banco/comune.py e la sua guardia sui log): sorgente 1,5 ohm,
NSL-32SR3 in serie e verso massa, R_IN 1 Mohm, v(AIN). Le correnti dei LED sono generatori ideali
dal profilo, una tabella in log10(I) contro d, come BILS del banco V2; con tabelle e tempi
diversi nei due versi se il profilo li ha.

S col metodo di V2 (scripts/v2_metodo.py, importato); E3 a 20 kHz dagli stati delle celle
(v(xls.xs), v(xlp.xs)) con rapido.zin_e3, per verso, e il carico della cella (criterio di L29b);
la profondita' a fine inserimento come in L47b1.

    /usr/bin/python3 sfumatura.py v4|v5                                # v4 compresso, o il v5, a 3 s
    /usr/bin/python3 sfumatura.py asim:<asimmetrico.json>:<criterio>:<td_ins>:<td_rel> [nome]
"""
import csv
import math
import os
import sys
from concurrent.futures import ThreadPoolExecutor

QUI = os.path.dirname(os.path.abspath(__file__))
L47B1 = os.path.abspath(os.path.join(QUI, "..", "..", "..", "2026-10-02", "L47b1", "banco"))
sys.path.insert(0, L47B1)
import comune as C  # noqa: E402  (il banco e la guardia di L47b1)
import rapido as R  # noqa: E402
import famiglia as F  # noqa: E402

sys.path.insert(0, os.path.join(C.REPO, "scripts"))
import v2_metodo as V2  # noqa: E402

ION, IRIP, T_INS = 7e-3, 10e-9, 0.3


def profilo(arg):
    """-> (serie_ins, deriv_ins, serie_rel, deriv_rel, td_ins, td_rel), tabelle in (d, log10 I)."""
    if arg in ("v4", "v5"):
        if arg == "v4":
            serie = [(0, ION), (0.1, 0.2e-3), (0.45, 4.5e-6), (0.75, 0.19e-6), (0.8, IRIP), (1, IRIP)]
            deriv = [(0, IRIP), (0.5, IRIP), (1, ION)]
        else:   # rapido.profilo_v5
            serie = [(0, ION), (R.SERIE_V5_D, IRIP), (1, IRIP)]
            deriv = [(0, IRIP), (R.DERIV_V5_D, IRIP), (1, ION)]
        s = [(d, math.log10(i)) for d, i in serie]
        p = [(d, math.log10(i)) for d, i in deriv]
        return s, p, s, p, 3.0, 3.0
    _, path, crit, ti, tr = arg.split(":")
    import json
    acc = json.load(open(path))[crit]
    pi, pr = acc["inserimento"], acc["rilascio"]
    si, di = F.tabelle(pi["a"], pi["b"], pi["i0"], pi["g"])
    sr, dr = F.tabelle(pr["a"], pr["b"], pr["i0"], pr["g"])
    return si, di, sr, dr, float(ti), float(tr)


def pwl_testo(t):
    return ", ".join("%.6g,%.4f" % (d, v) for d, v in t)


def tempi(td_i, td_r):
    t_rel = T_INS + td_i + 1.0
    return t_rel, t_rel + td_r + 0.5


def deck(nome, curva, prof):
    si, di, sr, dr, td_i, td_r = prof
    t_rel, t_fine = tempi(td_i, td_r)
    dep = ("BDEP DEP 0 V = time < %g ? min(max((time - %g)/%g, 0), 1)"
           " : min(max(1 - (time - %g)/%g, 0), 1)" % (t_rel, T_INS, td_i, t_rel, td_r))
    r = C.testa("sfumatura L47b2b1 %s" % nome)
    r[1] = "* GENERATO da docs/preamp/data/2026-10-03/L47b2b1/banco/sfumatura.py. Banco ridotto di L47b1."
    c = [x for x in C.cella_ldr(curva, curva) if not x.startswith(("ILS ", "ILP "))]
    # pwl() estrapola fuori dai punti (#31): d e' tenuto in [0, 1] da BDEP, e la tabella copre [0, 1]
    c += ["* il profilo: log10(I) contro d, interpolato linearmente (come BILS del banco V2);",
          "* una tabella per verso, scelta dal tempo (il comando di rilascio a t = %g s)" % t_rel,
          "BILS 0 ALS I = time < %g ? pow(10, pwl(V(DEP), %s)) : pow(10, pwl(V(DEP), %s))" % (
              t_rel, pwl_testo(si), pwl_testo(sr)),
          "BILP 0 ALP I = time < %g ? pow(10, pwl(V(DEP), %s)) : pow(10, pwl(V(DEP), %s))" % (
              t_rel, pwl_testo(di), pwl_testo(dr))]
    r += c + [dep, ".control", "option itl1=1000", "set numdgt=15",
              "tran 10u %g 0 10u" % t_fine,
              "wrdata %s.dat v(ain) v(xls.xs) v(xlp.xs)" % nome, ".endc", ".end"]
    return r


def leggi_stati(path):
    """wrdata a tre colonne (t, y ripetuto): t, xs, xp ogni ~1 ms."""
    t, xs, xp, ultimo = [], [], [], -1.0
    for riga in open(path):
        v = riga.split()
        if len(v) != 6:
            continue
        tk = float(v[0])
        if tk - ultimo >= 1e-3:
            t.append(tk)
            xs.append(float(v[3]))
            xp.append(float(v[5]))
            ultimo = tk
    return t, xs, xp


def analizza(cartella, nome, td_i, td_r):
    t_rel, t_fine = tempi(td_i, td_r)
    p = os.path.join(cartella, nome + ".dat")
    cols, tend = V2.leggi_wrdata(p, 2e-6, t_fine)
    x = cols[0]
    _, ap = V2.ampiezza(x, 1000.0, 0.05, T_INS - 0.02)
    a_pieno = sorted(ap)[int(0.95 * (len(ap) - 1))]
    out = {"corsa": nome, "td_ins_s": td_i, "td_rel_s": td_r, "a_pieno_V": a_pieno, "t_fine_letto": tend}
    for nm, te, td in (("S_ins", T_INS, td_i), ("S_rel", t_rel, td_r)):
        ii, aa = V2.ampiezza(x, 1000.0, te - 0.020, min(te + td + 0.200, t_fine))
        vs, js = V2.salto_db(ii, aa, a_pieno)
        out[nm + "_dB"] = vs
        out[nm + "_t"] = None if js is None else js / V2.FS
    ii, aa = V2.ampiezza(x, 1000.0, t_rel - 0.15, t_rel - 0.05)
    out["liv_mute_dB"] = 20 * math.log10(max(max(aa), 1e-30) / a_pieno)
    t, xs, xp = leggi_stati(p)
    z = [(R.zin_e3(10 ** a, 10 ** b), tk) for tk, a, b in zip(t, xs, xp)]
    out["E3_ins_kohm"] = min(v for v, tk in z if tk < t_rel) / 1e3
    out["E3_rel_kohm"] = min(v for v, tk in z if tk >= t_rel) / 1e3
    out["carico_min_kohm"] = min(R.carico(10 ** a, 10 ** b) for a, b in zip(xs, xp)) / 1e3
    out["E3_20Hz_kohm"] = min(R.zin_e3(10 ** a, 10 ** b, R.F_BASSI) for a, b in zip(xs, xp)) / 1e3
    out["ultimo_t_stati"] = t[-1]
    return out


def main():
    arg = sys.argv[1]
    etichetta = sys.argv[2] if len(sys.argv) > 2 else arg.replace(":", "_").replace("/", "_")[-40:]
    prof = profilo(arg)
    td_i, td_r = prof[4], prof[5]
    cartella = os.path.join(QUI, "run", etichetta)
    os.makedirs(cartella, exist_ok=True)
    corse = [("%s_%s" % (etichetta, c), c) for c in "ABCDE"]
    for nome, c in corse:
        for est in (".dat", ".log"):     # #35: un esito vecchio non sopravvive a una corsa fallita
            if os.path.exists(os.path.join(cartella, nome + est)):
                os.remove(os.path.join(cartella, nome + est))
        open(os.path.join(cartella, nome + ".cir"), "w").write("\n".join(deck(nome, c, prof)) + "\n")
    with ThreadPoolExecutor(5) as ex:
        esiti = list(ex.map(lambda k: (k, C.corri(os.path.join(cartella, k[0] + ".cir"), 7200)), corse))
    righe, ok = [], True
    _, t_fine = tempi(td_i, td_r)
    for (nome, c), (rc, log) in esiti:
        cattive = C.guardia(log)
        if rc != 0 or cattive:
            print("RIFIUTATA %s rc=%d %s" % (nome, rc, cattive[:3]))
            ok = False
            continue
        r = analizza(cartella, nome, td_i, td_r)
        if abs(r["ultimo_t_stati"] - t_fine) > 2e-3:      # #42: l'ultima riga al tempo chiesto
            print("RIFIUTATA %s: dati fino a %.4f s su %.4f" % (nome, r["ultimo_t_stati"], t_fine))
            ok = False
            continue
        righe.append(r)
        print("%-24s S ins %5.2f  S rel %5.2f dB  mute %6.1f dB  E3 20 kHz ins %6.1f k  rel %6.1f k  20 Hz %6.1f k  carico %6.1f k" % (
            nome, r["S_ins_dB"], r["S_rel_dB"], r["liv_mute_dB"], r["E3_ins_kohm"],
            r["E3_rel_kohm"], r["E3_20Hz_kohm"], r["carico_min_kohm"]))
    if righe:
        os.makedirs(os.path.join(QUI, "tabelle"), exist_ok=True)
        with open(os.path.join(QUI, "tabelle", "sfumatura_%s.csv" % etichetta), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(righe[0]))
            w.writeheader()
            for r in righe:
                w.writerow({k: ("%.6g" % v if isinstance(v, float) else v) for k, v in r.items()})
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
