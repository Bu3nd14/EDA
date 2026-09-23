#!/usr/bin/env python3
"""L29c: v2_metodo.py analizza in parallelo. Divide il manifesto in gruppi autosufficienti: ogni
gruppo tiene le righe di un FILE d'evento, piu' le righe dei riferimenti che nominano (e,
ricorsivamente, le celle che servono a quelle). Ogni gruppo si analizza in un processo proprio
(al piu' NPAR insieme), e i CSV si concatenano. Le righe dei riferimenti analizzate in piu'
gruppi (B1, C_pav) si tengono una volta sola.

Uso: analizza_par.py manifest.csv DATADIR analisi.csv [NPAR=4]
"""
import csv
import os
import subprocess
import sys
import time

man, datadir, out = sys.argv[1:4]
NPAR = int(sys.argv[4]) if len(sys.argv) > 4 else 4
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 6))
V2 = os.path.join(REPO, "scripts", "v2_metodo.py")
with open(man) as f:
    rows = list(csv.DictReader(f))
    campi = list(rows[0].keys())
per_cella = {r["cella"]: r for r in rows}
eventi = {}
for r in rows:
    if r["tipo"] in ("evento", "pav_num"):
        eventi.setdefault(r["file"], []).append(r)


def chiusura(sel):
    celle = {r["cella"] for r in sel}
    ag = True
    while ag:
        ag = False
        for r in list(sel):
            for k in ("rif_ins", "rif_rel"):
                n = r[k]
                if n not in ("", "-") and n not in celle:
                    sel.append(per_cella[n])
                    celle.add(n)
                    ag = True
    return sel


# i riferimenti senza nessun evento che li nomina (B1 e C_pav): un gruppo loro
nominati = {r[k] for r in rows for k in ("rif_ins", "rif_rel")}
gruppi = [chiusura(list(v)) for v in eventi.values()]
soli = [r for r in rows if r["tipo"] not in ("evento", "pav_num")]
gruppi.append(soli)
wd = os.path.join(datadir, "_analisi_par")
os.makedirs(wd, exist_ok=True)
proc = []
for k, g in enumerate(gruppi):
    mp = os.path.join(wd, "m%03d.csv" % k)
    with open(mp, "w", newline="") as f:
        w = csv.DictWriter(f, campi)
        w.writeheader()
        w.writerows(g)
    proc.append((mp, os.path.join(wd, "a%03d.csv" % k)))
attivi = []
t0 = time.time()
for mp, ap in proc:
    while len([p for p in attivi if p.poll() is None]) >= NPAR:
        time.sleep(2)
    attivi.append(subprocess.Popen(["/usr/bin/python3", V2, "analizza", mp, datadir, ap],
                                   stdout=subprocess.DEVNULL, stderr=open(ap + ".err", "w")))
rc = [p.wait() for p in attivi]
if any(rc):
    sys.exit("analizza fallita in %d gruppi su %d: vedi %s/*.err" % (sum(1 for x in rc if x), len(rc), wd))
# concatena: gli eventi dai loro gruppi, i riferimenti (B1, C_pav) dal gruppo 'soli'
tipo = {r["cella"]: r["tipo"] for r in rows}
viste = set()
tutte = []
intest = None
for k, (mp, ap) in enumerate(proc):
    with open(ap) as f:
        rr = list(csv.reader(f))
    intest = rr[0]
    mie = {r["cella"] for r in (gruppi[k] if k < len(gruppi) - 1 else [])
           if r["tipo"] in ("evento", "pav_num")} if k < len(gruppi) - 1 else None
    for x in rr[1:]:
        cella = x[0]
        if mie is not None and cella not in mie:
            continue
        key = tuple(x)
        if key in viste:
            continue
        viste.add(key)
        tutte.append(x)
with open(out, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(intest)
    w.writerows(tutte)
print("%d gruppi, %d righe -> %s in %.0f s" % (len(proc), len(tutte), out, time.time() - t0))
