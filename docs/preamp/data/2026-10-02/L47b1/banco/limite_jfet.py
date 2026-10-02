"""limite_jfet.py - L47b1: il limite fisico della sfumatura a JFET, col correttivo IDEALE.

La domanda: la distorsione della sfumatura a JFET dipende dalla geometria del prompt (serie +
derivazione, correttivo resistivo parziale), o da qualunque sfumatura a JFET con 2,7 V RMS?

Il caso piu' favorevole: un partitore a L, una resistenza fissa RSER in serie e il JFET verso
massa che sfuma (il source a massa, quindi il comando e' riferito a massa); il gate comandato da
una sorgente comportamentale IDEALE, Vg = Vd/2 + Vc: meta' esatta della tensione drain-source,
nessun carico, nessun limite del comando. Nessun circuito reale fa meglio di cosi' (il correttivo
resistivo e' una sua approssimazione). Se a una profondita' di qualche dB la THD resta alta, il
limite e' del JFET col segnale di questo progetto, non della geometria.

Per RSER 1 k, 10 k, 33 k, l'angolo TIP e i due estremi; Vc spazzato finemente; per ogni punto il
livello della fondamentale su AIN, la THD a 1 kHz e la tensione di picco ai capi del JFET.

    /usr/bin/python3 limite_jfet.py
Scrive run/limite/*.cir|.log e tabelle/limite_jfet.csv; stampa la THD alle profondita' -1, -3,
-6, -10, -20, -40 dB (interpolata sul punto piu' vicino).
"""
import csv
import os
import sys
from concurrent.futures import ThreadPoolExecutor

from comune import A_PIENO, ANGOLI, QUI, corri, db, guardia, testa
from statico import leggi

RSER = ["1k", "10k", "33k"]


def griglia(vto):
    # Vc da VTO - 0,5 V a 0: fitta vicino al pinch-off, dove avviene la sfumatura
    pts = [vto - 0.5 + 0.5 * k / 10 for k in range(10)]
    pts += [vto + (abs(vto)) * (10 ** (e / 8.0) - 1e-3) for e in range(-32, 1)]
    return sorted(set(round(p, 6) for p in pts if p <= 0))


def deck(ang, rser):
    vto = ANGOLI[ang][0]
    r = testa("limite jfet %s rser %s" % (ang, rser)) + [
        "RSER SRCX AIN %s" % rser,
        "JP AIN GP 0 MMBFJ112_%s" % ang,
        "VC NC 0 DC 0",
        "* il correttivo ideale: meta' esatta di Vds sul gate, piu' il comando",
        "BG GP 0 V = V(AIN)/2 + V(NC)",
        ".control", "option itl1=1000", "set numdgt=10", "set fourgridsize=8192", "set nfreqs=10"]
    vcs = griglia(vto)
    for vc in vcs:
        r += ["echo L47B1_CASO d=%.6f" % (vc - vto + 10),
              "alter vc dc = %.6f" % vc,
              "tran 0.5u 4m 2m 0.5u", "fourier 1000 v(vsn) v(ain)",
              "let vdsmax = vecmax(abs(v(ain)))", "print vdsmax", "destroy all",
              "* il secondo passaggio: la stessa riga di 20 kHz che leggi() si aspetta",
              "alter @vsrc[sin] = [ 0 %g 20000 ]" % A_PIENO,
              "tran 25n 0.4m 0.3m 25n", "fourier 20000 v(vsn) v(ain)", "destroy all",
              "alter @vsrc[sin] = [ 0 %g 1000 ]" % A_PIENO]
    return r + [".endc", ".end"], vcs


def main():
    cartella = os.path.join(QUI, "run", "limite")
    os.makedirs(cartella, exist_ok=True)
    lavori = []
    for ang in ANGOLI:
        for rser in RSER:
            nome = "%s_%s" % (ang, rser)
            r, vcs = deck(ang, rser)
            open(os.path.join(cartella, nome + ".cir"), "w").write("\n".join(r) + "\n")
            lavori.append((nome, ang, rser, vcs))
    with ThreadPoolExecutor(8) as ex:
        esiti = list(ex.map(lambda l: (l, corri(os.path.join(cartella, l[0] + ".cir"))), lavori))
    righe, ok = [], True
    for (nome, ang, rser, vcs), (rc, log) in esiti:
        cattive = guardia(log)
        if rc != 0 or cattive:
            print("RIFIUTATA %s rc=%d %s" % (nome, rc, cattive[:3]))
            ok = False
            continue
        casi = leggi(log)
        if len(casi) != len(vcs):
            print("RIFIUTATA %s: %d casi su %d" % (nome, len(casi), len(vcs)))
            ok = False
            continue
        for vc, c in zip(vcs, casi):
            a = c["four"][("v(ain)", 1000)]
            a20 = c["four"][("v(ain)", 20000)]
            righe.append({"angolo": ang, "rser": rser, "vc": vc,
                          "liv1k_db": db(a["h"][1] / A_PIENO), "thd1k_pct": a["thd"],
                          "thd20k_pct": a20["thd"], "vds_picco": c.get("vdsmax"),
                          "pav1k_pct": c["four"][("v(vsn)", 1000)]["thd"]})
    os.makedirs(os.path.join(QUI, "tabelle"), exist_ok=True)
    with open(os.path.join(QUI, "tabelle", "limite_jfet.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(righe[0]))
        w.writeheader()
        for r in righe:
            w.writerow({k: ("%.6g" % v if isinstance(v, float) else v) for k, v in r.items()})
    print("THD a 1 kHz (%%) alla profondita' piu' vicina; [livello reale]. Correttivo IDEALE.")
    obiettivi = [-1, -3, -6, -10, -20, -40]
    print("%-10s" % "" + "".join("%16s" % ("%d dB" % o) for o in obiettivi))
    for ang in ANGOLI:
        for rser in RSER:
            sel = [r for r in righe if r["angolo"] == ang and r["rser"] == rser]
            if not sel:
                continue
            cel = []
            for o in obiettivi:
                r = min(sel, key=lambda r: abs(r["liv1k_db"] - o))
                cel.append("%7.3g [%5.1f]" % (r["thd1k_pct"], r["liv1k_db"]))
            print("%-10s" % ("%s %s" % (ang, rser)) + "".join("%16s" % c for c in cel))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
