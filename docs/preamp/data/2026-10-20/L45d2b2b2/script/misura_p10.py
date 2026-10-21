#!/usr/bin/env python3
"""L45c1: the P10 duration (ADR-069) and the raw peak on the audio runs of the bridge chain
(deck/genera_tb_v2_casopeggiore.py --matrice l41c: <cella>.dat = wrdata of v(mainjack)
v(fixjack1) v(fixjack2)). Solo stdlib, /usr/bin/python3.

    misura_p10.py --prova                       the tool on known cases (L45b's two, plus the
                                                exponential written as a wrdata file and read
                                                back through v2_metodo's reader)
    misura_p10.py <corse> <manifest_ok.csv> <out.csv>

Per event row of the manifest (tipo evento), per jack, from t_ins (10 ms before the event):
    picco_V     max |v| (the jack rests at 0: an output capacitor and its bleeds)
    sopra_ms    P10: total time with |v| > 0,87 V, raw (no filter), resampled at v2_metodo.FS
    ultimo_ms   the last instant above 0,87 V; at the run's end the duration is a lower bound
    fine_V      the jack at the run's end
The duration rule is L45b's analizza_p10.durata, copied (that script reads L45a's channel files).
"""
import csv
import math
import os
import sys
import tempfile

QUI = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(QUI, "..", "..", "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import v2_metodo as vm  # noqa: E402

SOGLIA = 0.87
DTMIN = 10e-6 / 5       # the bridge decks' tmax is 10 us; v2_metodo drops points closer than a fifth
JACK = ("main", "fix1", "fix2")


def durata(x, i0, fs, soglia=SOGLIA):
    """(ms above, last instant above in ms, above at the last sample) from i0 on (L45b)."""
    n, ultimo = 0, None
    for i in range(i0, len(x)):
        if abs(x[i]) > soglia:
            n += 1
            ultimo = i
    return n / fs * 1e3, ((ultimo - i0) / fs * 1e3 if ultimo is not None else 0.0), \
        ultimo is not None and ultimo == len(x) - 1


def leggi(path, t_fine):
    cols, t_last = vm.leggi_wrdata(path, DTMIN, t_fine)
    return cols, t_last


def prova():
    fs = vm.FS
    tau = 4.7e-6 * 110e3
    x = [0.0] * 1000 + [14.9 * math.exp(-i / fs / tau) for i in range(int(3.0 * fs))]
    s, _, fine = durata(x, 1000, fs)
    att = tau * math.log(14.9 / 0.87) * 1e3
    ok1 = abs(s - att) < 0.05 and not fine
    y = [math.sin(2 * math.pi * 997.0 * i / fs) for i in range(int(fs))]
    s2, _, _ = durata(y, 0, fs)
    att2 = 1e3 * 2 * math.acos(0.87) / math.pi
    ok2 = abs(s2 - att2) < 1.0
    # the same exponential as ngspice writes it: t v t v t v, an uneven step, a breakpoint
    # repeated; the event at 1 s, read back from t_ins = 0.99 s
    d = tempfile.mkdtemp()
    p = os.path.join(d, "prova.dat")
    with open(p, "w") as f:
        t = 0.0
        while t <= 4.0:
            v = 0.0 if t < 1.0 else 14.9 * math.exp(-(t - 1.0) / tau)
            f.write(" %.9e %.9e %.9e %.9e %.9e %.9e\n" % (t, v, t, v / 2, t, 0.0))
            if abs(t - 1.0) < 1e-12:
                f.write(" %.9e %.9e %.9e %.9e %.9e %.9e\n" % (t, v, t, v / 2, t, 0.0))
            t += 7e-6 if 1.0 <= t < 1.01 else 37e-6
            if 0.99999 < t < 1.0:
                t = 1.0
    cols, _ = leggi(p, 4.0)
    i0 = int(round(0.99 * fs))
    s3, _, f3 = durata(cols[0], i0, fs)
    s4, _, _ = durata(cols[1], i0, fs)
    att4 = tau * math.log(14.9 / 2 / 0.87) * 1e3
    ok3 = abs(s3 - att) < 0.5 and abs(s4 - att4) < 0.5 and not f3
    print("esponenziale: %.2f ms, atteso %.2f -> %s" % (s, att, "OK" if ok1 else "SBAGLIATO"))
    print("seno 1 V 997 Hz per 1 s: %.1f ms, atteso %.1f -> %s" % (s2, att2, "OK" if ok2 else "SBAGLIATO"))
    print("esponenziale da un file wrdata: %.2f ms (atteso %.2f), meta' %.2f ms (atteso %.2f) -> %s"
          % (s3, att, s4, att4, "OK" if ok3 else "SBAGLIATO"))
    return 0 if ok1 and ok2 and ok3 else 1


def main(corse, man, out):
    fs = vm.FS
    rows = list(csv.DictReader(open(man)))
    k = list(rows[0].keys())
    righe = []
    for r in rows:
        if r["tipo"] != "evento":
            continue
        t_ins = float(r[k[7]])
        t_fine = float(r[k[9]])
        cols, t_last = leggi(os.path.join(corse, r["file"]), t_fine)
        i0 = int(round(t_ins * fs))
        riga = {"cella": r["cella"], "t_ins": t_ins, "t_fine": t_fine, "t_ultimo_dato": t_last}
        for j, x in zip(JACK, cols):
            s, u, alla_fine = durata(x, i0, fs)
            riga[j + "_picco_V"] = max(abs(v) for v in x[i0:])
            riga[j + "_sopra_ms"] = s
            riga[j + "_ultimo_ms"] = u
            riga[j + "_alla_fine"] = "si" if alla_fine else "no"
            riga[j + "_fine_V"] = x[-1]
        sopra = max(riga[j + "_sopra_ms"] for j in JACK)
        fine = any(riga[j + "_alla_fine"] == "si" for j in JACK)
        riga["p10"] = "entro" if sopra <= 100 else ("FUORI, ancora sopra alla fine" if fine else "FUORI")
        righe.append(riga)
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(righe[0].keys()))
        w.writeheader()
        for r in righe:
            w.writerow({a: ("%.6g" % b if isinstance(b, float) else b) for a, b in r.items()})
    print("scritto %s: %d corse" % (out, len(righe)))


if __name__ == "__main__":
    if sys.argv[1] == "--prova":
        sys.exit(prova())
    main(*sys.argv[1:4])
