#!/usr/bin/env python3
"""L69: the lists of the options of NC-079 on the bench (--l69ra / --l69rd / --serie2 R576).

  /usr/bin/python3 -I psu/lista_l69.py vaglio  > lista_vaglio.txt     the screening
  /usr/bin/python3 -I psu/lista_l69.py piena OPZ[,OPZ...] > lista_piena.txt   the full set

The label of a run is <option>[_m10|_p10|_t22]: seq/<label>/<case>. The options:
  a220 a470 a1k a2k2   a resistor between AT_ON and the latch's anode (Q514's emitter)
  b                    R576 as two halves in series (a short leaves one) + 1k in series with D537
The healthy events are L64b's sequences (an_l64b.csv: oggi/<seq>, oggi_m10/<seq>, oggi_p10/<seq>).
"""
import sys

BASE = "sorgente --n2n7002 ds --tss 3.0 --comparatore tarato --ritenuta costruttore --bat54 costruttore --sonde-piu"
SONDE = ("--sonde Q501:3,Q502:3,Q503:3,Q505:3,D507:2,D509:2,U507:1,Q504:3,Q504:1,U503:1,U504:3,U512:3,"
         "Q513:1,Q513:2,Q513:3,Q514:2,Q514:3")
OPZ = {"a220": "--l69ra 220", "a470": "--l69ra 470", "a1k": "--l69ra 1k", "a2k2": "--l69ra 2.2k",
       "b": "--serie2 R576 --l69rd 1k"}
SANI = ("accensione", "fredda", "guasto", "buco20", "perdita", "spegnimento_l", "accensione_u501",
        "inserimento")
RETE_B = ("accensione", "perdita", "buco20", "spegnimento_l", "inserimento")   # bases in L64b at +-10 %
GUASTI = ("f_r572_corto_guas", "f_r576_corto_guas")


def riga(caso, etich, opz, extra=""):
    return " ".join(x for x in (caso, etich, BASE, opz, extra) if x)


def main(argv):
    out = []
    if argv[1] == "vaglio":
        for o, opz in OPZ.items():
            out += [riga(g, o, opz, SONDE) for g in GUASTI]
            out += [riga(s, o, opz) for s in ("guasto", "accensione_u501", "inserimento")]
    elif argv[1] == "piena":
        for o in argv[2].split(","):
            opz = OPZ[o]
            out += [riga(s, o, opz) for s in SANI if s not in ("guasto", "accensione_u501", "inserimento")]
            # argparse keeps the last --comparatore: tarato22 over BASE's tarato
            out += [riga(s, o + "_t22", opz, "--comparatore tarato22") for s in ("accensione", "fredda")]
            for r, f in (("m10", "0.9"), ("p10", "1.1")):
                out += [riga(s, "%s_%s" % (o, r), opz, "--rete " + f) for s in RETE_B + ("guasto",)]
                out += [riga(g, "%s_%s" % (o, r), opz, SONDE + " --rete " + f) for g in GUASTI]
    else:
        raise SystemExit(__doc__)
    print("\n".join(out))


main(sys.argv)
