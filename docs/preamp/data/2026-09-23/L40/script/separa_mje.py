#!/usr/bin/env python3
"""L40, ESPLORAZIONE - nessun file di models/ ne' del sorgente cambia.

separa_cause.py ha trovato che la caduta di V1 e' dei MJE (+6,47 gradi rimettendo
i soli MJE al segnaposto). Ma il segnaposto cambia insieme le capacita', TF, VAF
e - per la Vbe - la corrente di riposo (15,2 contro 20,3 mA). Qui, sui modelli
del costruttore, si sposta UNA cosa alla volta, nella stessa esecuzione:

  base      tutto come pubblicato                    -> deve ridare 55,55
  cap       CJE/CJC dei Qmje al valore del segnaposto (altermod)
  tf        TF dei Qmje al valore del segnaposto
  vaf       VAF dei Qmje a 100
  ritorno   i valori pubblicati rimessi              -> deve ridare base cella per cella
  r<R>      R128 (moltiplicatore, NX-NBB) a R: I_q ~15 mA a modelli pubblicati

MODELLI ALTERATI (limitations #29): i Qmje15032/Qmje15033 alterati con
`altermod` portano ancora il nome del costruttore. Ogni variante stampa `showmod`
di Q132 e Q133 e I_q; la variante `ritorno` prova che niente resta appeso.
Scrive mje/tb_loop_mje.cir. Uso: /usr/bin/python3 separa_mje.py
"""
import os

QUI = os.path.dirname(os.path.abspath(__file__))
L40 = os.path.dirname(QUI)
ROOT = os.path.abspath(os.path.join(L40, *[".."] * 5))
SRC = os.path.join(ROOT, "spice", "preamp", "tb", "tb_loop.cir")
OUT = os.path.join(L40, "mje", "tb_loop_mje.cir")

# valori pubblicati (models/bjt_npn/mje15032.lib, models/bjt_pnp/mje15033.lib)
PUB = {"qmje15032": {"cje": "3.05969e-09", "cjc": "3.00108e-10", "tf": "4.94819e-09",
                     "vaf": "31.5491"},
       "qmje15033": {"cje": "3.06005e-09", "cjc": "3.00101e-10", "tf": "4.78203e-09",
                     "vaf": "12.5778"}}
# segnaposto (spice/preamp/placeholder_devices.lib, NMJE15032 / PMJE15033)
SEG = {"qmje15032": {"cje": "300p", "cjc": "100p", "tf": "5.3n", "vaf": "100"},
       "qmje15033": {"cje": "300p", "cjc": "120p", "tf": "6.4n", "vaf": "100"}}
VAR = [("base", {}), ("cap", {"cje": SEG, "cjc": SEG}), ("tf", {"tf": SEG}),
       ("vaf", {"vaf": SEG}), ("ritorno", {"cje": PUB, "cjc": PUB, "tf": PUB, "vaf": PUB})]
RR = ["1.20k", "1.25k", "1.30k", "1.33k", "1.35k", "1.40k", "1.45k", "1.50k", "1.69k"]


def corsa(nome):
    return ["showmod q132 : cje cjc tf vaf", "showmod q133 : cje cjc tf vaf",
            "op", 'echo "IQ %s"' % nome, "print @q132[ic] @q133[ic] @r128[resistance]",
            "destroy all",
            "foreach rs 1m 2.611k", "  alter rsrcb = $rs",
            "  foreach cab 1f 470p 1n 1.5n 2.2n 2.7n 3.3n 4.7n",
            "    alter ccable = $cab",
            "    ac dec 100 1 100meg",
            "    let T = v(fb)/v(g2)", "    let Tdb = db(T)", "    let Tph = ph(T)",
            "    meas ac fcross when Tdb=0", "    meas ac pmarg find Tph when Tdb=0",
            "    meas ac tdc find Tdb at=10",
            '    echo "%s,$rs,$cab,$&fcross,$&pmarg,$&tdc" >> tb_loop_mje.csv' % nome,
            "    destroy all", "  end", "end"]


def main():
    righe = open(SRC).read().split("\n")
    testa = righe[:righe.index(".control")]
    testa[0] = ("tb_loop_mje.cir - L40 ESPLORAZIONE: V1 blocco B 0 dB, i Qmje ALTERATI "
                "con altermod una grandezza alla volta, poi R128; generato da separa_mje.py")
    testa.insert(1, "* ATTENZIONE (limitations #29): nel .control i modelli Qmje15032/"
                    "Qmje15033 sono alterati; il nome resta quello del costruttore.")
    ctl = [".control", "alter r109 = 1G", "set units = degrees", "alter rrg = 1G",
           "alter rrg10 = 1G", "alter rload = 100k", "alter cnode = 1f",
           'echo "variante,rsrc,cprobe,fcross_hz,pm_deg,tdb_10hz" > tb_loop_mje.csv']
    for nome, alt in VAR:
        # ogni variante riparte dai valori pubblicati: gli altermod restano
        # appesi da una corsa all'altra, e senza questo si accumulano
        if nome != "base":
            for mod in PUB:
                for par in PUB[mod]:
                    ctl.append("altermod %s %s = %s" % (mod, par, PUB[mod][par]))
        for par, tab in alt.items():
            for mod in tab:
                ctl.append("altermod %s %s = %s" % (mod, par, tab[mod][par]))
        ctl += corsa(nome)
    for r in RR:
        ctl.append("alter r128 = %s" % r)
        ctl += corsa("r" + r)
    ctl += [".endc", ".end", ""]
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w").write("\n".join(testa + ctl))
    print("scritto", OUT)


if __name__ == "__main__":
    main()
