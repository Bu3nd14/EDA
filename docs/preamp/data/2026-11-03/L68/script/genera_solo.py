#!/usr/bin/env python3
"""L68: every distinct fault case of the lists generated once (no ngspice), into a folder outside the
repo: a primitive the bench refuses shows here, before the long list. One event per case (the first).
    /usr/bin/python3 -I script/genera_solo.py <cartella>
"""
import os
import subprocess
import sys

L = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(L, "psu"))
import modi  # noqa: E402

OUT = os.path.abspath(sys.argv[1])
BASE = ("--timer sorgente --n2n7002 ds --tss 3.0 --comparatore tarato --ritenuta costruttore "
        "--bat54 costruttore --sonde-piu").split()
casi = ["%s_accs" % b for b, *_ in modi.RIGHE_L68] + ["%s_muss" % b for b, *_ in modi.RIGHE_L68C] + \
       ["%s_muss" % b for b, *_ in modi.RIGHE_L68T]
male = 0
for c in casi:
    d = os.path.join(OUT, c)
    os.makedirs(d, exist_ok=True)
    r = subprocess.run(["/usr/bin/python3", os.path.join(L, "psu", "genera_tb_psu.py"), "--uscita", d,
                        "--nome", "seq", "--caso", c, "--giro", "1", "--angolo", "nom"] + BASE,
                       capture_output=True, text=True)
    if r.returncode:
        male += 1
        print(c, "RIFIUTATO:", (r.stderr.strip().splitlines() or ["?"])[-1])
print(len(casi), "casi,", male, "rifiutati")
sys.exit(1 if male else 0)
