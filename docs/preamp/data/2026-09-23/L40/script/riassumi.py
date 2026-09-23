#!/usr/bin/env python3
"""L40: riassuntore generico delle tabelle d'anello d'esplorazione.

Uso: /usr/bin/python3 riassumi.py <tabella.csv> <colonne-gruppo> [filtro]
  colonne-gruppo: nomi separati da virgola (es. variante  oppure  cm,mode)
  filtro: espressione python su r (dict della riga), es. "r['cprobe'] in ('1f','1n')"
Per ogni gruppo: margine minimo con la cella che lo da', crossover e guadagno a
10 Hz della cella a vuoto (prima riga del gruppo con rsrc 1m / 1 e sonda 1f,
se c'e').
"""
import csv
import sys

p, chiavi = sys.argv[1], sys.argv[2].split(",")
filtro = sys.argv[3] if len(sys.argv) > 3 else None
righe = list(csv.DictReader(open(p)))
g, ordine, vuoto = {}, [], {}
for r in righe:
    if filtro and not eval(filtro, {}, {"r": r}):
        continue
    k = tuple(r[c] for c in chiavi)
    if k not in g:
        ordine.append(k)
    pm = float(r["pm_deg"])
    if k not in g or pm < g[k][0]:
        g[k] = (pm, r)
    sonda = r.get("cprobe", r.get("cwire", r.get("cab", "")))
    if k not in vuoto and r.get("rsrc", "1m") in ("1m", "1") and sonda == "1f":
        vuoto[k] = r
for k in ordine:
    pm, r = g[k]
    cella = " ".join("%s=%s" % (c, v) for c, v in r.items()
                     if c not in chiavi and c not in ("fcross_hz", "pm_deg", "tdb_10hz"))
    v = vuoto.get(k, {})
    fc = float(v["fcross_hz"]) / 1e3 if v else float("nan")
    print("%-22s pm_min %7.2f  %-34s fc_vuoto %7.1f kHz  T10 %s  %s" % (
        "/".join(k), pm, cella, fc, v.get("tdb_10hz", "-")[:6],
        "OK" if pm >= 60 else "SOTTO 60"))
