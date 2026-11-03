#!/usr/bin/env python3
"""L58b: the series pair against the base. Two checks, printed per case:
  base   <etichetta>_base/<event> against L58a's l58a_base (an_l58a.csv) and l58b_base/inserimento
         (an_l58b.csv): the columns of K that differ
  guasti <etichetta>/<f_..._ev> against <etichetta>_base/<event>: the columns that differ, plus
         censimento.py's t_coil_ms (accensione) and mute_en_fine (inserimento)
Solo stdlib. /usr/bin/python3 -I confronta_serie.py <an.csv> <censimento.csv> <etichetta>
(run from the lot's folder: the references are read by relative path)
"""
import csv
import sys

K = "musica_TE C2 C3 r41 s41 t_jack_ms t_gain_ms t_k501_ms t_mus_ms mus_end k501_end ritenuta".split()
EV = {"accs": "accensione", "freds": "fredda", "guas": "guasto", "b20s": "buco20", "perds": "perdita",
      "spls": "spegnimento_l", "u501s": "accensione_u501", "inss": "inserimento"}
an, cens, et = sys.argv[1:4]
ref = {r["caso"].split("/")[1]: r for r in csv.DictReader(open("../../2026-10-29/L58a/an_l58a.csv"))
       if r["caso"].startswith("l58a_base/")}
ref.update({r["caso"].split("/")[1]: r for r in csv.DictReader(open("an_l58b.csv"))
            if r["caso"] == "l58b_base/inserimento"})
R = {r["caso"]: r for r in csv.DictReader(open(an))}
C = {r["caso"]: r for r in csv.DictReader(open(cens))}
for c, r in sorted(R.items()):
    n = c.split("/")[1]
    if c.startswith(et + "_base/"):
        b, tag = ref[n], "base " + n
    else:
        b, tag = R["%s_base/%s" % (et, EV[n.rsplit("_", 1)[1]])], n
    d = [(k, b[k], r[k]) for k in K if b[k] != r[k]]
    x = C.get(c, {})
    extra = ""
    if x.get("t_coil_ms") or x.get("mute_en_fine"):
        extra = "  coil %s ms, mute_fine %s" % (x.get("t_coil_ms"), x.get("mute_en_fine"))
    print("%-26s %s%s" % (tag, "uguale" if not d else d, extra))
