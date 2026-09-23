#!/usr/bin/env python3
"""L29c: dal manifesto di dividi.py tiene le righe la cui colonna FILE (senza .dat) soddisfa il
regex, e scrive l'elenco delle corse da lanciare. Una riga si estrae dalla colonna file, non
dalla colonna cella (L39: rele_* rilegge ev_*, pav_* legge evp_*/invp_*).
Controlla che ogni riferimento nominato dalle righe tenute sia anch'esso tenuto: un
riferimento mancante farebbe fallire analizza a meta'.

Uso: seleziona.py manifest.csv REGEX manifest_sel.csv corse_sel.txt
"""
import csv
import re
import sys

man, rx, out_man, out_corse = sys.argv[1:5]
R = re.compile(rx)
with open(man) as f:
    rows = list(csv.DictReader(f))
    campi = list(rows[0].keys())
tenute = [r for r in rows if R.search(r["file"][:-4])]
celle = {r["cella"] for r in tenute}
mancano = sorted({r[k] for r in tenute for k in ("rif_ins", "rif_rel")
                  if r[k] not in ("", "-") and r[k] not in celle})
if mancano:
    sys.exit("riferimenti non selezionati: %s" % " ".join(mancano))
with open(out_man, "w", newline="") as f:
    w = csv.DictWriter(f, campi)
    w.writeheader()
    w.writerows(tenute)
corse = []
for r in tenute:
    c = r["file"][:-4]
    if c not in corse:
        corse.append(c)
open(out_corse, "w").write("\n".join(corse) + "\n")
print("%d righe, %d corse" % (len(tenute), len(corse)))
