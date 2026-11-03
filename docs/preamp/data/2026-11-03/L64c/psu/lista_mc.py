#!/usr/bin/env python3
"""L54b3b: the run list of a set of --toll files (corri_lista_an.sh), one line per file and case.

/usr/bin/python3 -I lista_mc.py <prefisso etichetta> <casi,...> "<opzioni comuni>" <toll.json>...
Each line: <caso> <prefisso><nome del file senza toll_ e .json> sorgente <opzioni> --toll <file>.
"""
import os
import sys

pre, casi, opz = sys.argv[1], sys.argv[2].split(","), sys.argv[3]
for f in sys.argv[4:]:
    nome = os.path.basename(f)[len("toll_"):-len(".json")]
    for c in casi:
        print("%s %s%s sorgente %s --toll %s" % (c, pre, nome, opz, os.path.abspath(f)))
