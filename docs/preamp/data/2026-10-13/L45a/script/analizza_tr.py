#!/usr/bin/env python3
"""L45a: analisi dei transitori del guasto (NC-042). Solo stdlib, /usr/bin/python3.

Uso: analizza_tr.py OUT.csv RUNDIR... [--rif RUNDIR_RIF]

Per ogni corsa run/<variante>/<modo>/ (deck di genera_canale.py tr) legge <modo>.dat (wrdata:
mainjack fix1jack fix2jack outa outf1 outf2 outb i(vpp) i(vmm)) e <modo>_fine.csv, e scrive una
riga con:

- per ogni jack (principale, fissa 1 Singxer, fissa 2 Stax):
    grezzo_V   il picco di |v - v(t_guasto-)| da t_guasto alla fine, SENZA filtro: il gradino vero
    A_V        il metodo di V2 / PR-23 (scripts/v2_metodo.py, lo stesso dei guasti dell'alimentatore
               di L41c/L47c2b2/L56): d = evento - riferimento, filtro 20 Hz - 20 kHz da t_guasto con
               stato nullo, picco. Senza musica il riferimento e' il valore costante prima del
               guasto; con la musica e' la corsa rif della stessa variante (--rif)
    fine_V     il jack alla fine della corsa (la continua che resta)
- dB SPL di picco a 1 m al jack principale, formula del PRB (NC-028): 96 + 20 log10(21,1 V / 2,83);
  0,87 V = 112,2 dB, il tetto di PR-23. Il finale da 30 W clippa a ~21,9 V di picco (~114 dB): la
  cifra si da' senza tetto del finale e lo si dice nel report.
- Stax: dB SPL all'orecchio con la catena di NC-046 (SRM-T1 a 60 dB, volume al massimo; SR-L300
  101 dB con 100 V): 101 + 20 log10(1000 V / 100), stessa convenzione «volt di picco come RMS»
  del PRB. La SRM-T1 esce al piu' con 300 V RMS (110,5 dB in questa convenzione).
- lo stato finale del blocco guasto (media, max, min dell'uscita negli ultimi 10 ms), la corrente
  dei rail, e le potenze dei dispositivi dal file _fine.csv; Tj = 27 + P * R_thJA (caldo.py di L56,
  SOT-223 per Q122/Q125 da ADR-068), e il dispositivo piu' caldo.
"""
import csv
import math
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(QUI, "..", "..", "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import v2_metodo as vm  # noqa: E402

T_GUASTO = 0.3
# Come v2_metodo (analizza): i punti piu' vicini di un quinto del passo massimo del deck si
# scartano. Con 1e-7 l'interpolazione cubica esplodeva dove ngspice infittisce: 47,8 V di
# «evento - riferimento» su un jack che sta fra -6 e +4,4 V (tr_musica_B/Q133_ce).
DTMIN = 50e-6 / 5
DTMIN_MUSICA = 10e-6 / 5
COL = ["mainjack", "fix1jack", "fix2jack", "outa", "outf1", "outf2", "outb", "ipp", "imm"]
JACK = (("main", 0), ("fix1", 1), ("fix2", 2))
# R_thJA in C/W, still air, come caldo.py di L56 (datasheet in vendor/); VAS e carico in SOT-223
# (ADR-068, 125 C/W piazzola minima); LS350 e LSK489 sulla somma delle due meta'.
RTH = {"q106": 417, "q117": 417, "q118": 417, "q125": 125, "q127": 417, "q122": 125,
       "q146": 403, "q148": 403, "q132": 62.5, "q133": 62.5}
TJMAX = {"q132": 150, "q133": 150, "q122": 150, "q125": 150}
TA = 27.0


def db_main(v):
    return 96 + 20 * math.log10(max(v, 1e-12) * 21.1 / 2.83)


def db_stax(v):
    return 101 + 20 * math.log10(max(v, 1e-12) * 1000 / 100)


def leggi_fine(path):
    d = {}
    if not os.path.exists(path):
        return d
    for r in csv.DictReader(open(path)):
        try:
            d[r["grandezza"]] = float(r["valore"])
        except ValueError:
            d[r["grandezza"]] = float("nan")
    return d


def termico(f):
    tj = {}
    for k, r in RTH.items():
        p = f.get("p_" + k)
        if p is not None:
            tj[k] = TA + abs(p) * r
    if "p_q121a" in f:
        tj["q121"] = TA + (abs(f["p_q121a"]) + abs(f["p_q121b"])) * 233
    if "p_jq110a" in f:
        tj["jq110"] = TA + (abs(f["p_jq110a"]) + abs(f["p_jq110b"])) * 250
    return tj


def main(argv):
    out = argv[1]
    dirs, rif = [], None
    a = argv[2:]
    while a:
        x = a.pop(0)
        if x == "--rif":
            rif = a.pop(0)
        else:
            dirs.append(x)
    serie_rif = None
    if rif:
        m = os.path.basename(rif.rstrip("/"))
        serie_rif, _ = vm.leggi_wrdata(os.path.join(rif, m + ".dat"), DTMIN_MUSICA, 10.0)
    righe = []
    for d in dirs:
        m = os.path.basename(d.rstrip("/"))
        dat = os.path.join(d, m + ".dat")
        log = os.path.join(d, m + ".log")
        stato = "ok"
        testo = open(log, errors="replace").read() if os.path.exists(log) else ""
        for frase in ("imestep too small", "aborted", "source stepping failed", "rror", "ransient op"):
            if frase in testo:
                stato = "LOG: " + frase
        if not os.path.exists(dat):
            righe.append({"variante": os.path.basename(os.path.dirname(d.rstrip("/"))), "modo": m,
                          "stato": "MANCA .dat"})
            continue
        serie, t_fine = vm.leggi_wrdata(dat, DTMIN_MUSICA if rif else DTMIN, 10.0)
        r = {"variante": os.path.basename(os.path.dirname(d.rstrip("/"))), "modo": m,
             "t_fine": "%.4f" % t_fine}
        if t_fine < 2.2:
            stato = "CORSA CORTA (%.3f s)" % t_fine
        i0 = int(round(T_GUASTO * vm.FS))
        for nome, k in JACK:
            x = serie[k]
            pre = x[i0 - 10]
            if serie_rif is not None:
                ref = serie_rif[k]
            else:
                ref = [pre] * len(x)
            a_v, a_i, _ = vm.a_picco(x, ref, T_GUASTO, t_fine)
            n = min(len(x), len(ref))
            grezzo = max(abs(x[i] - ref[i]) for i in range(i0, n))
            r[nome + "_grezzo_V"] = "%.4g" % grezzo
            r[nome + "_A_V"] = "%.4g" % a_v
            r[nome + "_A_t_ms"] = "%.1f" % ((a_i - i0) / vm.FS * 1e3)
            r[nome + "_fine_V"] = "%.4g" % x[-1]
        r["main_dB_SPL"] = "%.1f" % db_main(float(r["main_A_V"]))
        r["main_dB_SPL_grezzo"] = "%.1f" % db_main(float(r["main_grezzo_V"]))
        r["stax_dB_SPL"] = "%.1f" % db_stax(float(r["fix2_A_V"]))
        r["sopra_tetto_main"] = "SI" if float(r["main_A_V"]) > 0.87 else "no"
        f = leggi_fine(os.path.join(d, m + "_fine.csv"))
        for k in ("out_avg", "out_max", "out_min", "ipp_avg", "imm_avg"):
            if k in f:
                r[k] = "%.4g" % f[k]
        tj = termico(f)
        if tj:
            caldo = max(tj, key=tj.get)
            r["tj_max_C"] = "%.0f" % tj[caldo]
            r["tj_max_disp"] = caldo
        for k in ("r134", "r135", "r123", "r126", "r144", "r130", "r131", "r107", "r101"):
            if "p_" + k in f:
                r["p_" + k + "_W"] = "%.3g" % f["p_" + k]
        for k in ("q132", "q133", "q122", "q125", "q146", "q148", "q127", "q106"):
            if "p_" + k in f:
                r["p_" + k + "_W"] = "%.3g" % f["p_" + k]
        r["stato"] = stato
        righe.append(r)
    campi = []
    for r in righe:
        for k in r:
            if k not in campi:
                campi.append(k)
    with open(out, "w", newline="") as fo:
        w = csv.DictWriter(fo, fieldnames=campi)
        w.writeheader()
        for r in righe:
            w.writerow(r)
    print("righe: %d -> %s" % (len(righe), out))


if __name__ == "__main__":
    main(sys.argv)
