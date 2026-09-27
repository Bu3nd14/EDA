#!/usr/bin/env python3
"""profilo_mute.py : il livello del tono al jack principale nel tempo, per una cella
di V2 col mute graduale a LDR (profilo v4), con lo stesso strumento che da' S.

    /usr/bin/python3 profilo_mute.py MANIFEST DATDIR CELLA OUT.csv

Importa scripts/v2_metodo.py e ne usa le funzioni senza toccarle:
  - leggi_wrdata: la ricampionatura a 96 kHz del .dat;
  - ampiezza:     il fit a + b del tono su max(10 ms, un periodo), un valore ogni ms;
  - il livello pieno: il 95-esimo percentile dell'ampiezza della corsa di
    riferimento del rilascio, da 0,3 s alla fine, come in `analizza`.

Scrive OUT.csv: t_s, livello_db (dB sotto il pieno, NON tenuto al pavimento: il
pavimento di S, -70 dB, lo applica chi legge), un campione ogni ms sulla corsa
intera. Stampa il pieno e le S ricalcolate su quella curva con salto_db, nelle
stesse finestre di `analizza`: devono coincidere con analisi.csv (che le scrive a
quattro cifre).

L42a, per il grafico del profilo v4 nel dossier.
"""
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "scripts"))
import v2_metodo as vm                                  # noqa: E402


def main(argv):
    if len(argv) != 5:
        print(__doc__)
        return 2
    manifest, datadir, cella, out = argv[1:5]
    with open(manifest) as f:
        per_nome = {r["cella"]: r for r in csv.DictReader(f)}
    c = per_nome[cella]
    rif = per_nome[c["rif_rel"]]
    f = float(c["f_hz"])
    k = vm.USCITE.index("MAINJACK")

    def colonna(r):
        cols, tend = vm.leggi_wrdata(os.path.join(datadir, r["file"]), float(r["tmax"]) / 5,
                                     float(r["t_fine"]))
        return cols[k], min(float(r["t_fine"]), tend)

    xr, tfr = colonna(rif)
    _, ap = vm.ampiezza(xr, f, 0.3, tfr)
    a_pieno = sorted(ap)[int(0.95 * (len(ap) - 1))]
    x, tf = colonna(c)
    ii, aa = vm.ampiezza(x, f, 0.0, tf)
    with open(out, "w", newline="") as fo:
        w = csv.writer(fo)
        w.writerow(["t_s", "livello_db"])
        for i, a in zip(ii, aa):
            w.writerow(["%.6f" % (i / vm.FS), "%.6f" % (20 * vm.math.log10(max(a, 1e-30) / a_pieno))])
    print("cella %s, riferimento del pieno %s, pieno %.6g V" % (cella, rif["cella"], a_pieno))
    tg = float(c.get("t_grad") or 0.0)
    for nm, te in (("S_ins", float(c["t_ins"])), ("S_rel", float(c["t_rel"]))):
        i2, a2 = vm.ampiezza(x, f, te - 0.020, min(te + tg + 0.200, tf))
        vs, js = vm.salto_db(i2, a2, a_pieno)
        print("%s = %.4g dB a %.6f s (finestra %.3f .. %.3f s)"
              % (nm, vs, js / vm.FS, te - 0.020, min(te + tg + 0.200, tf)))
    print("%d campioni -> %s" % (len(ii), out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
