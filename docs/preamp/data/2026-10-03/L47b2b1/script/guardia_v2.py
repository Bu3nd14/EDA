"""guardia_v2.py - L47b2b1: le guardie che corri.sh di L29c non ha, su ogni corsa di una cartella
di V2 (#35, #36, #42; corri.sh guarda solo «Transient op», #33):
  - il log (stdout e stderr nello stesso file) senza «Timestep too small», «aborted», «Error»,
    «too many args», «no such device», «Transient op»;
  - l'ultima riga di ogni .dat della corsa al tempo finale chiesto (colonna t_fine del manifesto),
    entro 1 ms: una `tran` abortita scrive comunque le righe fino a tstop, ma il log lo dice (#35);
    una che si ferma prima ha l'ultima riga corta (#42).

    /usr/bin/python3 guardia_v2.py <cartella> [<cartella> ...]
Esce col numero di corse rifiutate.
"""
import csv
import os
import sys

RIFIUTI = ("Timestep too small", "aborted", "Error", "error:", "too many args", "no such device",
           "Transient op started")


def ultima_riga(p):
    with open(p, "rb") as f:
        f.seek(0, 2)
        n = f.tell()
        f.seek(max(n - 4096, 0))
        righe = [r for r in f.read().decode(errors="replace").splitlines() if r.strip()]
    return righe[-1] if righe else ""


def main():
    male = 0
    for d in sys.argv[1:]:
        man = {}
        for r in csv.DictReader(open(os.path.join(d, "manifest.csv"))):
            corsa = r["file"][:-4]
            man.setdefault(corsa, float(r["t_fine"]))
        corse = [c.strip() for c in open(os.path.join(d, "corse_sel.txt")) if c.strip()]
        n_ok = 0
        for c in corse:
            log = os.path.join(d, "corsa_%s.log" % c)
            motivi = []
            if not os.path.exists(log):
                motivi.append("senza log")
            else:
                for riga in open(log, errors="replace"):
                    for x in RIFIUTI:
                        if x in riga:
                            motivi.append(riga.strip()[:80])
                            break
            for suff in ("", "_stati"):
                p = os.path.join(d, c + suff + ".dat")
                if suff and not os.path.exists(p):
                    continue
                if not os.path.exists(p) or os.path.getsize(p) == 0:
                    motivi.append("%s.dat assente o vuoto" % (c + suff))
                    continue
                ur = ultima_riga(p).split()
                t = float(ur[0]) if ur else -1.0
                tf = man.get(c)
                if tf is not None and abs(t - tf) > 1e-3:
                    motivi.append("%s.dat finisce a %.4f s su %.4f" % (c + suff, t, tf))
            if motivi:
                male += 1
                print("RIFIUTATA %s/%s: %s" % (os.path.basename(d), c, "; ".join(motivi[:3])))
            else:
                n_ok += 1
        print("%s: %d corse su %d passano la guardia" % (d, n_ok, len(corse)))
    return male


if __name__ == "__main__":
    sys.exit(main())
